"""Tests for publishing the recounted usage snapshot."""
import base64
import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import Mock

try:
    from sync_usage import ENDPOINT, publish_snapshot
except ImportError:
    ENDPOINT, publish_snapshot = None, None

spec = importlib.util.spec_from_file_location('export_usage', Path(__file__).with_name('export_usage.py'))
usage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage)


def remote(data, sha='existing-sha'):
    return {'sha': sha, 'content': base64.b64encode(json.dumps(data).encode()).decode()}


def old_snapshot():
    """A schema v3 snapshot with two sources; it must not be merged into v4."""
    return {'schemaVersion': 3, 'generatedAt': '2026-11-14T20:00:00+08:00',
            'source': 'magpie', 'history': {'source': 'CC Switch', 'until': '2026-11-10'},
            'summary': {'totalTokens': 999},
            'daily': [{'date': '2026-11-10', 'source': 'CC Switch', 'totalTokens': 999}],
            'models': []}


class SyncTests(unittest.TestCase):
    def test_publishes_v4_without_merging_old_history(self):
        self.assertIsNotNone(publish_snapshot)
        api = Mock(side_effect=[remote(old_snapshot()), {'commit': {'sha': 'new'}}])
        self.assertEqual(publish_snapshot([], api), 'published')
        method, path, payload = api.call_args.args
        self.assertEqual(method, 'PUT')
        self.assertEqual(path, ENDPOINT)
        published = json.loads(base64.b64decode(payload['content']))
        self.assertEqual(published['schemaVersion'], 4)
        self.assertNotIn('history', published)
        self.assertEqual(published['daily'], [])

    def test_unchanged_when_remote_matches(self):
        self.assertIsNotNone(publish_snapshot)
        api = Mock(return_value=remote(usage.export_usage([])))
        self.assertEqual(publish_snapshot([], api), 'unchanged')
        self.assertEqual(api.call_count, 1)
        self.assertEqual(api.call_args.args[0], 'GET')

    def test_dry_run_does_not_put(self):
        self.assertIsNotNone(publish_snapshot)
        api = Mock(return_value=remote(old_snapshot()))
        self.assertEqual(publish_snapshot([], api, dry_run=True), 'would-publish')
        self.assertEqual(api.call_count, 1)
        self.assertEqual(api.call_args.args[0], 'GET')

    def test_put_uses_remote_sha(self):
        self.assertIsNotNone(publish_snapshot)
        api = Mock(side_effect=[remote(old_snapshot(), sha='sha-from-remote'), {'commit': {'sha': 'new'}}])
        publish_snapshot([], api)
        self.assertEqual(api.call_args.args[2]['sha'], 'sha-from-remote')
        self.assertEqual(api.call_args.args[2]['branch'], 'main')

    def test_malformed_remote_file_is_not_overwritten(self):
        self.assertIsNotNone(publish_snapshot)
        api = Mock(return_value={'sha': 'x', 'content': 'not-base64'})
        with self.assertRaises(Exception):
            publish_snapshot([], api)
        self.assertEqual(api.call_count, 1)


if __name__ == '__main__':
    unittest.main()
