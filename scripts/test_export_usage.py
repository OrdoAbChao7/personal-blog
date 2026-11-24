"""Tests for the local-ledger usage exporter."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('export_usage', Path(__file__).with_name('export_usage.py'))
usage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usage)


def ledger_row(t='2026-11-12T16:30:00+08:00', agent='pi', model='m', req='', inp=100,
               out=10, read=50, write=5, cost='0.25', rid='r1', route_id=None, **extra):
    row = dict(t=t, agent=agent, model=model, req=req, **{'in': inp}, out=out,
               cache_read=read, cache_write=write, status=200)
    if cost is not None:
        row['cost'] = cost
    if rid is not None:
        row['rid'] = rid
    if route_id is not None:
        row['route_id'] = route_id
    row.update(extra)
    return row


class UsageExportTests(unittest.TestCase):
    def test_summary_counts_cache_miss_and_other_categories(self):
        result = usage.export_usage([ledger_row()])
        summary = result['summary']
        self.assertEqual(summary['inputTokens'], 100)
        self.assertEqual(summary['cacheMissTokens'], 100)
        self.assertEqual(summary['outputTokens'], 10)
        self.assertEqual(summary['cacheReadTokens'], 50)
        self.assertEqual(summary['cacheWriteTokens'], 5)
        self.assertEqual(summary['totalTokens'], 165)
        self.assertAlmostEqual(summary['cacheHitRate'], 50 / 155)
        self.assertEqual(summary['estimatedCostUsd'], '0.250000')

    def test_daily_and_model_buckets(self):
        result = usage.export_usage([ledger_row()])
        self.assertEqual(result['daily'][0]['date'], '2026-11-12')
        self.assertEqual(result['daily'][0]['totalTokens'], 165)
        self.assertEqual(result['models'][0]['model'], 'm')
        self.assertEqual(result['models'][0]['totalTokens'], 165)

    def test_single_source_schema(self):
        result = usage.export_usage([ledger_row()])
        self.assertEqual(result['schemaVersion'], 4)
        self.assertNotIn('history', result)
        self.assertNotIn('source', result['daily'][0])

    def test_gateway_row_without_rid_or_cost_counts_tokens(self):
        rows = [ledger_row(rid=None, route_id=7, cost=None, source='gateway') for _ in range(2)]
        result = usage.export_usage(rows)
        self.assertEqual(result['summary']['requests'], 1)
        self.assertEqual(result['summary']['totalTokens'], 165)
        self.assertEqual(result['summary']['estimatedCostUsd'], '0.000000')

    def test_rejected_row_is_ignored(self):
        rows = [ledger_row(), ledger_row(rid='r2', inp=999, cost='9', rejected=True)]
        result = usage.export_usage(rows)
        self.assertEqual(result['summary']['totalTokens'], 165)
        self.assertEqual(result['summary']['estimatedCostUsd'], '0.250000')

    def test_shanghai_day_boundary(self):
        result = usage.export_usage([ledger_row(t='2026-11-11T23:30:00-05:00')])
        self.assertEqual(result['daily'][0]['date'], '2026-11-12')

    def test_duplicate_rid_counts_once(self):
        result = usage.export_usage([ledger_row(), ledger_row()])
        self.assertEqual(result['summary']['requests'], 1)
        self.assertEqual(result['summary']['totalTokens'], 165)

    def test_missing_model_uses_requested_model(self):
        result = usage.export_usage([ledger_row(model='', req='vendor/model')])
        self.assertEqual(result['models'][0]['model'], 'vendor/model')

    def test_empty_ledger(self):
        result = usage.export_usage([])
        self.assertEqual(result['summary']['totalTokens'], 0)
        self.assertEqual(result['daily'], [])
        self.assertEqual(result['models'], [])

    def test_unchanged_ignores_generated_at(self):
        first = usage.export_usage([ledger_row()])
        second = dict(first, generatedAt='2000-01-01T00:00:00+08:00')
        self.assertTrue(usage.unchanged(first, second))

    def test_read_ledger_rejects_missing_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'usage.jsonl'
            path.write_text('{"t":"2026-11-12T10:00:00+08:00","agent":"pi","in":1,"out":1,"cache_write":0,"status":200}\n', encoding='utf-8')
            with self.assertRaises(RuntimeError):
                usage.read_ledger(path)

    def test_ledger_path_missing_raises(self):
        with self.assertRaises(RuntimeError):
            usage.ledger_path('does-not-exist.jsonl')


if __name__ == '__main__':
    unittest.main()
