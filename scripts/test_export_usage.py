import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('export_usage', Path(__file__).with_name('export_usage.py'))
usage = importlib.util.module_from_spec(spec)
if spec.loader and Path(spec.origin).exists():
    spec.loader.exec_module(usage)


def row(time='2026-11-12T10:00:00+08:00', model='test-model', inp=100, out=10, read=50,
        write=5, cost='0.100001', rejected='false', handed_on='false', requested=''):
    return {'time': time, 'requested_model': requested, 'model': model, 'input_tokens': str(inp),
            'output_tokens': str(out), 'cache_read_tokens': str(read), 'cache_write_tokens': str(write),
            'cost_usd': cost, 'rejected': rejected, 'handed_on': handed_on}


def snapshot(bucket, day='2026-11-10', model='legacy-model'):
    return {'schemaVersion': 1, 'generatedAt': f'{day}T20:00:02+08:00', 'timezone': 'Asia/Shanghai',
            'source': 'CC Switch', 'summary': usage.finish(bucket),
            'daily': [dict(date=day, **usage.finish(bucket))],
            'models': [dict(model=model, **usage.finish(bucket))]}


def legacy_bucket():
    return dict(requests=3, inputTokens=1000, outputTokens=100, cacheReadTokens=500,
                cacheWriteTokens=0, estimatedCostUsd=usage.Decimal('1.250000'))


class UsageExportTests(unittest.TestCase):
    def test_cache_columns_stay_apart_from_fresh_input(self):
        result = usage.export_usage([row()])
        summary = result['summary']
        self.assertEqual(summary['requests'], 1)
        self.assertEqual(summary['inputTokens'], 100)
        self.assertEqual(summary['cacheReadTokens'], 50)
        self.assertEqual(summary['cacheWriteTokens'], 5)
        self.assertEqual(summary['totalTokens'], 165)
        self.assertEqual(summary['estimatedCostUsd'], '0.100001')
        self.assertAlmostEqual(summary['cacheHitRate'], 50 / 155)
        self.assertEqual(result['daily'][0]['date'], '2026-11-12')
        self.assertEqual(result['models'][0]['model'], 'test-model')

    def test_handed_on_try_is_billed_but_is_not_a_request(self):
        result = usage.export_usage([row(cost='0.5'), row(handed_on='true', inp=7, out=1, read=0,
                                                           write=0, cost='0.25')])
        self.assertEqual(result['summary']['requests'], 1)
        self.assertEqual(result['summary']['totalTokens'], 165 + 8)
        self.assertEqual(result['summary']['estimatedCostUsd'], '0.750000')

    def test_rejected_call_is_left_out_of_every_total(self):
        result = usage.export_usage([row(), row(rejected='true', inp=999, cost='9')])
        self.assertEqual(result['summary']['requests'], 1)
        self.assertEqual(result['summary']['inputTokens'], 100)
        self.assertEqual(result['summary']['estimatedCostUsd'], '0.100001')

    def test_unpriced_call_adds_tokens_but_no_cost(self):
        result = usage.export_usage([row(cost='')])
        self.assertEqual(result['summary']['totalTokens'], 165)
        self.assertEqual(result['summary']['estimatedCostUsd'], '0.000000')

    def test_days_are_bucketed_in_shanghai_time(self):
        result = usage.export_usage([row(time='2026-11-12T16:30:00Z')])
        self.assertEqual(result['daily'][0]['date'], '2026-11-13')

    def test_model_falls_back_to_requested_model_or_unknown(self):
        result = usage.export_usage([row(model='', requested='vendor/model'), row(model='')])
        self.assertEqual([m['model'] for m in result['models']], ['unknown', 'vendor/model'])

    def test_pre_migration_history_is_frozen_and_merged_once(self):
        history = snapshot(legacy_bucket())
        rows = [row(), row(time='2026-11-10T23:59:00+08:00', inp=999)]
        result = usage.export_usage(rows, history)
        self.assertEqual(result['history']['source'], 'CC Switch')
        self.assertEqual(result['history']['until'], '2026-11-10')
        self.assertEqual([day['date'] for day in result['daily']], ['2026-11-10', '2026-11-12'])
        self.assertEqual(result['summary']['requests'], 4)
        self.assertEqual(result['summary']['totalTokens'], usage.finish(legacy_bucket())['totalTokens'] + 165)
        models = {model['model']: model for model in result['models']}
        self.assertEqual(models['legacy-model']['requests'], 3)
        self.assertEqual(models['test-model']['requests'], 1)

    def test_second_run_against_its_own_snapshot_does_not_double_count(self):
        history = snapshot(legacy_bucket())
        rows = [row(), row(time='2026-11-13T09:00:00+08:00', inp=1, out=1, read=0, write=0)]
        first = usage.export_usage(rows, history)
        second = usage.export_usage(rows, first)
        self.assertTrue(usage.unchanged(first, second))
        self.assertEqual(second['summary']['requests'], first['summary']['requests'])
        self.assertEqual(second['summary']['totalTokens'], first['summary']['totalTokens'])
        self.assertEqual(sum(model['totalTokens'] for model in second['models']),
                         second['summary']['totalTokens'])

    def test_snapshot_already_holding_magpie_days_without_history_block_is_refused(self):
        broken = {'source': 'magpie', 'summary': usage.finish(legacy_bucket()),
                  'daily': [{'date': '2026-11-12'}], 'models': []}
        with self.assertRaises(RuntimeError):
            usage.export_usage([], broken)

    def test_empty_ledger_is_zero_and_export_has_only_whitelisted_fields(self):
        result = usage.export_usage([])
        self.assertEqual(result['summary']['cacheHitRate'], 0)
        self.assertEqual(result['daily'], [])
        self.assertEqual(result['models'], [])
        self.assertIsNone(result['history'])
        self.assertEqual(set(result), {'schemaVersion', 'generatedAt', 'timezone', 'source',
                                       'history', 'summary', 'daily', 'models'})
        self.assertEqual(set(result['summary']), {'requests', 'inputTokens', 'outputTokens',
                                                  'cacheReadTokens', 'cacheWriteTokens',
                                                  'totalTokens', 'estimatedCostUsd', 'cacheHitRate'})

    def test_unknown_ledger_columns_fail_instead_of_publishing_zero(self):
        bad = 'time,agent,input_tokens\n2026-11-12T10:00:00+08:00,claude,1\n'
        with patch.object(usage.subprocess, 'run', return_value=type('R', (), {
                'returncode': 0, 'stdout': bad, 'stderr': ''})()):
            with self.assertRaises(RuntimeError):
                usage.read_ledger('magpie')

    def test_failed_magpie_call_raises(self):
        with patch.object(usage.subprocess, 'run', return_value=type('R', (), {
                'returncode': 1, 'stdout': '', 'stderr': 'boom'})()):
            with self.assertRaises(RuntimeError):
                usage.read_ledger('magpie')


if __name__ == '__main__':
    unittest.main()
