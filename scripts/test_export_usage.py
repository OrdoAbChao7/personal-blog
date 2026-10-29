import importlib.util
import sqlite3
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('export_usage', Path(__file__).with_name('export_usage.py'))
usage = importlib.util.module_from_spec(spec)
if spec.loader and Path(spec.origin).exists():
    spec.loader.exec_module(usage)


class UsageExportTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute('''CREATE TABLE proxy_request_logs (
            request_id TEXT PRIMARY KEY, app_type TEXT, model TEXT, pricing_model TEXT,
            input_tokens INTEGER, output_tokens INTEGER, cache_read_tokens INTEGER,
            cache_creation_tokens INTEGER, input_token_semantics INTEGER,
            total_cost_usd TEXT, created_at INTEGER, data_source TEXT, status_code INTEGER)''')
        self.db.execute('''CREATE TABLE usage_daily_rollups (
            date TEXT, app_type TEXT, model TEXT, pricing_model TEXT, request_count INTEGER,
            input_tokens INTEGER, output_tokens INTEGER, cache_read_tokens INTEGER,
            cache_creation_tokens INTEGER, input_token_semantics INTEGER, total_cost_usd TEXT)''')

    def tearDown(self):
        self.db.close()

    def add(self, id='p1', app='codex', source='proxy', timestamp=1793203200,
            input=1000, output=100, read=600, write=100, semantics=0, model='test-model', status=200):
        self.db.execute('INSERT INTO proxy_request_logs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (id, app, model, None, input, output, read, write, semantics,
                         '0.100001', timestamp, source, status))

    def test_cache_semantics_are_normalized_without_double_counting(self):
        self.assertEqual(usage.fresh_input(1000,600,100,'codex',0),400)
        self.assertEqual(usage.fresh_input(1000,600,100,'codex',1),300)
        self.assertEqual(usage.fresh_input(300,600,100,'codex',2),300)
        self.assertEqual(usage.fresh_input(100,600,0,'codex',0),100)
        self.assertEqual(usage.fresh_input(300,600,100,'claude',0),300)

    def test_proxy_duplicate_session_is_removed_but_other_models_and_failed_proxy_are_kept(self):
        self.add()
        self.add(id='s1',source='codex_session',timestamp=1793203205,write=0)
        self.add(id='s2',source='codex_session',model='other-model')
        self.add(id='failed',model='failed-model',status=500)
        self.add(id='s3',source='codex_session',model='failed-model')
        result=usage.export_usage(self.db)
        self.assertEqual(result['summary']['requests'],4)
        self.assertEqual(result['summary']['totalTokens'],4800)

    def test_rollups_and_recent_detail_share_shanghai_calendar_without_losing_history(self):
        self.add(timestamp=1793203200)  # 2026-10-28 16:00 UTC -> 2026-10-29 Shanghai
        self.db.execute("INSERT INTO usage_daily_rollups VALUES ('2026-09-01','codex','old',NULL,10,300,100,600,100,2,'1.25')")
        result=usage.export_usage(self.db)
        self.assertEqual(result['summary']['requests'],11)
        self.assertEqual([x['date'] for x in result['daily']],['2026-09-01','2026-10-29'])
        self.assertEqual(result['summary']['estimatedCostUsd'], '1.350001')
        self.assertEqual(result['summary']['totalTokens'],2300)
        self.assertEqual(sum(x['totalTokens'] for x in result['models']),2300)

    def test_empty_data_is_zero_and_public_export_has_only_whitelisted_fields(self):
        result=usage.export_usage(self.db)
        self.assertEqual(result['summary']['cacheHitRate'],0)
        self.assertEqual(result['daily'],[])
        self.assertEqual(set(result),{'schemaVersion','generatedAt','timezone','source','summary','daily','models'})
        self.assertEqual(set(result['summary']),{'requests','inputTokens','outputTokens','cacheReadTokens','cacheWriteTokens','totalTokens','estimatedCostUsd','cacheHitRate'})

    def test_missing_schema_fails_instead_of_publishing_zero(self):
        self.db.execute('DROP TABLE usage_daily_rollups')
        with self.assertRaises(RuntimeError):
            usage.export_usage(self.db)


if __name__ == '__main__':
    unittest.main()
