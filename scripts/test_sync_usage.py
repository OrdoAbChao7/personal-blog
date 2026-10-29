import base64
import json
import unittest
from unittest.mock import Mock

try:
    from sync_usage import publish_snapshot
except ImportError:
    publish_snapshot = None


class SyncTests(unittest.TestCase):
    def data(self, tokens=100, at='2026-10-29T12:00:00+08:00'):
        return {'schemaVersion':1, 'generatedAt':at, 'summary':{'totalTokens':tokens}}

    def remote(self, data):
        return {'sha':'existing-sha', 'content':base64.b64encode(json.dumps(data).encode()).decode()}

    def test_same_numbers_with_new_timestamp_do_not_create_a_commit(self):
        self.assertIsNotNone(publish_snapshot)
        api=Mock(return_value=self.remote(self.data(at='2026-10-28T12:00:00+08:00')))
        self.assertEqual(publish_snapshot(self.data(),api),'unchanged')
        self.assertEqual(api.call_count,1)

    def test_only_the_usage_json_is_committed_with_optimistic_lock(self):
        self.assertIsNotNone(publish_snapshot)
        api=Mock(side_effect=[self.remote(self.data(50)), {'commit':{'sha':'new'}}])
        self.assertEqual(publish_snapshot(self.data(),api),'published')
        method,path,payload=api.call_args.args
        self.assertEqual(method,'PUT')
        self.assertEqual(path,'repos/OrdoAbChao7/personal-blog/contents/public/data/usage.json')
        self.assertEqual(payload['sha'],'existing-sha')
        self.assertEqual(payload['branch'],'main')
        self.assertEqual(json.loads(base64.b64decode(payload['content'])),self.data())

    def test_dry_run_cannot_publish(self):
        self.assertIsNotNone(publish_snapshot)
        api=Mock(return_value=self.remote(self.data(50)))
        self.assertEqual(publish_snapshot(self.data(),api,dry_run=True),'would-publish')
        self.assertEqual(api.call_count,1)

    def test_malformed_remote_file_is_not_overwritten(self):
        self.assertIsNotNone(publish_snapshot)
        api=Mock(return_value={'sha':'x','content':'not-base64'})
        with self.assertRaises(Exception):
            publish_snapshot(self.data(),api)
        self.assertEqual(api.call_count,1)


if __name__=='__main__': unittest.main()
