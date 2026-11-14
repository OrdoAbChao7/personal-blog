import base64
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import Mock

try:
    from sync_usage import ENDPOINT, publish_snapshot
except ImportError:
    publish_snapshot = None

spec = importlib.util.spec_from_file_location('export_usage', Path(__file__).with_name('export_usage.py'))
usage = importlib.util.module_from_spec(spec)
if spec.loader and Path(spec.origin).exists():
    spec.loader.exec_module(usage)


def row(inp=100, cost='0.5', time='2026-11-12T10:00:00+08:00'):
    return {'time': time, 'requested_model': '', 'model': 'm', 'input_tokens': str(inp),
            'output_tokens': '10', 'cache_read_tokens': '0', 'cache_write_tokens': '0',
            'cost_usd': cost, 'rejected': 'false', 'handed_on': 'false'}


class SyncTests(unittest.TestCase):
    def remote(self, data, sha='existing-sha'):
        return {'sha': sha, 'content': base64.b64encode(json.dumps(data).encode()).decode()}

    def test_same_numbers_with_new_timestamp_do_not_create_a_commit(self):
        self.assertIsNotNone(publish_snapshot)
        rows = [row()]
        published = usage.export_usage(rows)
        published['generatedAt'] = '2026-11-13T20:00:00+08:00'
        api = Mock(return_value=self.remote(published))
        self.assertEqual(publish_snapshot(rows, api), 'unchanged')
        self.assertEqual(api.call_count, 1)

    def test_only_the_usage_json_is_committed_with_optimistic_lock(self):
        self.assertIsNotNone(publish_snapshot)
        rows = [row()]
        previous = usage.export_usage([])
        api = Mock(side_effect=[self.remote(previous), {'commit': {'sha': 'new'}}])
        self.assertEqual(publish_snapshot(rows, api), 'published')
        method, path, payload = api.call_args.args
        self.assertEqual(method, 'PUT')
        self.assertEqual(path, ENDPOINT)
        self.assertEqual(payload['sha'], 'existing-sha')
        self.assertEqual(payload['branch'], 'main')
        self.assertTrue(usage.unchanged(json.loads(base64.b64decode(payload['content'])),
                                        usage.export_usage(rows, previous)))

    def test_remote_history_block_is_the_base_so_earlier_days_survive(self):
        self.assertIsNotNone(publish_snapshot)
        legacy = dict(requests=3, inputTokens=1000, outputTokens=100, cacheReadTokens=500,
                      cacheWriteTokens=0, estimatedCostUsd=usage.Decimal('1.25'))
        history = {'schemaVersion': 1, 'generatedAt': '2026-11-10T20:00:02+08:00',
                   'source': 'CC Switch', 'summary': usage.finish(legacy),
                   'daily': [dict(date='2026-11-10', **usage.finish(legacy))],
                   'models': [dict(model='legacy-model', **usage.finish(legacy))]}
        api = Mock(side_effect=[self.remote(history), {'commit': {'sha': 'new'}}])
        self.assertEqual(publish_snapshot([row(inp=5), row(inp=7, time='2026-11-13T10:00:00+08:00')],
                                          api), 'published')
        published = json.loads(base64.b64decode(api.call_args.args[2]['content']))
        self.assertEqual(published['history']['until'], '2026-11-10')
        self.assertEqual([day['date'] for day in published['daily']],
                         ['2026-11-10', '2026-11-12', '2026-11-13'])
        self.assertEqual(published['summary']['requests'], 5)
        self.assertEqual(published['summary']['inputTokens'], 1012)

    def test_dry_run_cannot_publish(self):
        self.assertIsNotNone(publish_snapshot)
        api = Mock(return_value=self.remote(usage.export_usage([])))
        self.assertEqual(publish_snapshot([row()], api, dry_run=True), 'would-publish')
        self.assertEqual(api.call_count, 1)

    def test_malformed_remote_file_is_not_overwritten(self):
        self.assertIsNotNone(publish_snapshot)
        api = Mock(return_value={'sha': 'x', 'content': 'not-base64'})
        with self.assertRaises(Exception):
            publish_snapshot([row()], api)
        self.assertEqual(api.call_count, 1)


if __name__ == '__main__':
    unittest.main()
