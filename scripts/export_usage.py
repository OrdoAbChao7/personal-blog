"""Read CC Switch usage only; never export providers, sessions or credentials.

Normalization/dedup follows farion1231/cc-switch services/sql_helpers.rs and
services/usage_stats.rs (2026-10-29). Rollups contain already-pruned detail.
"""
import argparse
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

SHANGHAI = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = Path.home() / '.cc-switch' / 'cc-switch.db'
OUTPUT = ROOT / 'public' / 'data' / 'usage.json'
TOKEN_FIELDS = ('inputTokens', 'outputTokens', 'cacheReadTokens', 'cacheWriteTokens')
SESSION_SOURCES = {'session_log', 'codex_session', 'gemini_session', 'opencode_session'}


def fresh_input(tokens, read, write, app, semantics):
    if semantics not in (0, 1, 2):
        raise RuntimeError('Unsupported CC Switch input token semantics')
    if semantics != 2 and app in ('codex', 'gemini', 'grokbuild'):
        cached = read + write if semantics == 1 else read
        if tokens >= cached:
            return tokens - cached
    return tokens


def empty_bucket():
    return dict(requests=0, inputTokens=0, outputTokens=0, cacheReadTokens=0,
                cacheWriteTokens=0, estimatedCostUsd=Decimal(0))


def add(bucket, row, count):
    bucket['requests'] += count
    bucket['inputTokens'] += fresh_input(row['input_tokens'], row['cache_read_tokens'],
        row['cache_creation_tokens'], row['app_type'], row['input_token_semantics'])
    bucket['outputTokens'] += row['output_tokens']
    bucket['cacheReadTokens'] += row['cache_read_tokens']
    bucket['cacheWriteTokens'] += row['cache_creation_tokens']
    bucket['estimatedCostUsd'] += Decimal(row['total_cost_usd'])


def finish(bucket):
    result = dict(bucket)
    result['totalTokens'] = sum(result[key] for key in TOKEN_FIELDS)
    denominator = result['inputTokens'] + result['cacheReadTokens'] + result['cacheWriteTokens']
    result['cacheHitRate'] = result['cacheReadTokens'] / denominator if denominator else 0
    result['estimatedCostUsd'] = format(result['estimatedCostUsd'].quantize(Decimal('.000001')), 'f')
    return result


def export_usage(conn):
    conn.row_factory = sqlite3.Row
    common = {'app_type', 'model', 'pricing_model', 'input_tokens', 'output_tokens',
              'cache_read_tokens', 'cache_creation_tokens', 'input_token_semantics', 'total_cost_usd'}
    for table, required in [('proxy_request_logs', common | {'created_at','data_source','status_code'}),
                             ('usage_daily_rollups', common | {'date','request_count'})]:
        columns = {row[1] for row in conn.execute(f'PRAGMA table_info({table})')}
        if not required <= columns:
            raise RuntimeError(f'Unsupported CC Switch schema in {table}')
    own_transaction = not conn.in_transaction
    if own_transaction:
        conn.execute('BEGIN')
    try:
        fields = ','.join(sorted(common))
        detail = conn.execute(f'SELECT {fields},created_at,data_source,status_code FROM proxy_request_logs').fetchall()
        rollups = conn.execute(f'SELECT {fields},date,request_count FROM usage_daily_rollups').fetchall()
    finally:
        if own_transaction:
            conn.rollback()

    # Index successful proxy rows in memory; the source database remains read-only.
    proxies = defaultdict(list)
    def match_key(row, app=None):
        return (app or row['app_type'], row['input_tokens'], row['output_tokens'], row['cache_read_tokens'])
    for row in detail:
        if (row['data_source'] or 'proxy') == 'proxy' and 200 <= row['status_code'] < 300:
            proxies[match_key(row)].append(row)

    def duplicate(row):
        if row['data_source'] not in SESSION_SOURCES:
            return False
        apps = [row['app_type']]
        if row['app_type'] == 'claude':
            apps.append('claude-desktop')
        for app in apps:
            for proxy in proxies[match_key(row, app)]:
                writes_match = (proxy['cache_creation_tokens'] == row['cache_creation_tokens']
                    or (row['cache_creation_tokens'] == 0 and row['data_source'] != 'session_log')
                    or (proxy['cache_creation_tokens'] == 0 and proxy['input_token_semantics'] == 0
                        and row['data_source'] == 'codex_session'))
                models = (proxy['model'].lower(), row['model'].lower())
                if (abs(proxy['created_at'] - row['created_at']) <= 600 and writes_match
                        and (models[0] == models[1] or 'unknown' in models)):
                    return True
        return False

    total, daily, models = empty_bucket(), defaultdict(empty_bucket), defaultdict(empty_bucket)
    def collect(row, date, count):
        model = row['pricing_model'] or row['model']
        for bucket in (total, daily[date], models[model]):
            add(bucket, row, count)
    for row in detail:
        if not duplicate(row):
            collect(row, datetime.fromtimestamp(row['created_at'], SHANGHAI).date().isoformat(), 1)
    for row in rollups:
        collect(row, row['date'], row['request_count'])
    return {
        'schemaVersion': 1,
        'generatedAt': datetime.now(SHANGHAI).isoformat(timespec='seconds'),
        'timezone': 'Asia/Shanghai',
        'source': 'CC Switch',
        'summary': finish(total),
        'daily': [dict(date=date, **finish(bucket)) for date, bucket in sorted(daily.items())],
        'models': sorted([dict(model=model, **finish(bucket)) for model, bucket in models.items()],
                         key=lambda item: item['totalTokens'], reverse=True),
    }


def read_usage(db=DEFAULT_DB):
    db = Path(db).resolve(strict=True)
    with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True, timeout=30) as conn:
        conn.execute('PRAGMA query_only=ON')
        return export_usage(conn)


def unchanged(left, right):
    return ({key: value for key, value in left.items() if key != 'generatedAt'} ==
            {key: value for key, value in right.items() if key != 'generatedAt'})


def write_snapshot(data, output=OUTPUT):
    output = Path(output)
    if output.exists() and unchanged(data, json.loads(output.read_text(encoding='utf-8'))):
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix('.json.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(output)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    data = read_usage(args.db)
    changed = write_snapshot(data, args.output)
    print(json.dumps({'changed': changed, 'summary': data['summary']}, ensure_ascii=False))
