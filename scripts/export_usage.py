"""Recount this computer's AI usage from the local per-call ledger.

The ledger (`usage.jsonl`) holds one row per call: gateway traffic plus calls
reported from the agents' own session files, already deduplicated by magpie.
A row's `in` is fresh input (cache misses); `cache_read` and `cache_write` are
separate, so the daily total is in + out + cache_read + cache_write.

Only aggregate dates, models and numbers are exported. No request bodies,
session text, credentials or provider configuration ever leave this machine.
"""
import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

SHANGHAI = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public' / 'data' / 'usage.json'
DEFAULT_LEDGER = Path('D:/Dev/OpenCode/config-root/magpie/usage.jsonl')
SCHEMA_VERSION = 4
SOURCE = '本机逐条调用记录（网关 + 会话上报）'
# cacheMissTokens mirrors inputTokens; sum only the four distinct categories.
TOKEN_FIELDS = ('inputTokens', 'outputTokens', 'cacheReadTokens', 'cacheWriteTokens')
REQUIRED_COLUMNS = {'t', 'agent', 'in', 'out', 'cache_read', 'cache_write', 'status'}


def ledger_path(path=None):
    """Resolve the ledger; an explicit --ledger is authoritative, never a fallback."""
    if path:
        try:
            resolved = Path(path).expanduser().resolve(strict=True)
        except OSError:
            raise RuntimeError(f'usage ledger not found: {path}') from None
        if not resolved.is_file():
            raise RuntimeError(f'usage ledger not found: {path}')
        return resolved
    for candidate in (os.environ.get('MAGPIE_USAGE_LEDGER'), DEFAULT_LEDGER):
        if not candidate:
            continue
        try:
            resolved = Path(candidate).expanduser().resolve(strict=True)
        except OSError:
            continue
        if resolved.is_file():
            return resolved
    raise RuntimeError(f'usage ledger not found: {os.environ.get("MAGPIE_USAGE_LEDGER") or DEFAULT_LEDGER}')


def read_ledger(path=None):
    """Stream the JSONL ledger into rows, refusing an unsupported schema."""
    target = ledger_path(path) if path is None else Path(path).expanduser()
    rows = []
    with target.open(encoding='utf-8', errors='replace') as source:
        for line in source:
            if not line.strip():
                continue
            row = json.loads(line)
            missing = REQUIRED_COLUMNS - set(row)
            if missing:
                raise RuntimeError(f'Unsupported usage ledger columns: {", ".join(sorted(missing))}')
            rows.append(row)
    return rows


def empty_bucket():
    return dict(requests=0, cacheMissTokens=0, inputTokens=0, outputTokens=0,
                cacheReadTokens=0, cacheWriteTokens=0, estimatedCostUsd=Decimal(0))


def add_row(bucket, row):
    if row.get('rejected') in (True, 'true'):
        return
    bucket['requests'] += 1
    fresh = int(row.get('in') or 0)
    bucket['cacheMissTokens'] += fresh
    bucket['inputTokens'] += fresh
    bucket['outputTokens'] += int(row.get('out') or 0)
    bucket['cacheReadTokens'] += int(row.get('cache_read') or 0)
    bucket['cacheWriteTokens'] += int(row.get('cache_write') or 0)
    if row.get('cost'):
        bucket['estimatedCostUsd'] += Decimal(str(row['cost']))


def finish(bucket):
    result = dict(bucket)
    result['totalTokens'] = sum(result[key] for key in TOKEN_FIELDS)
    denominator = result['cacheMissTokens'] + result['cacheReadTokens'] + result['cacheWriteTokens']
    result['cacheHitRate'] = result['cacheReadTokens'] / denominator if denominator else 0
    result['estimatedCostUsd'] = format(result['estimatedCostUsd'].quantize(Decimal('.000001')), 'f')
    return result


def dedup_key(row, index):
    if row.get('rid'):
        return ('rid', row['rid'])
    if row.get('route_id') is not None:
        return ('route', row['route_id'])
    return ('line', index)


def export_usage(rows):
    total = empty_bucket()
    models = defaultdict(empty_bucket)
    daily = defaultdict(empty_bucket)
    seen = set()
    for index, row in enumerate(rows):
        key = dedup_key(row, index)
        if key in seen:
            continue
        seen.add(key)
        if row.get('rejected') in (True, 'true'):
            continue
        day = datetime.fromisoformat(row['t']).astimezone(SHANGHAI).date().isoformat()
        model = row.get('model') or row.get('req') or 'unknown'
        for bucket in (total, models[model], daily[day]):
            add_row(bucket, row)
    return {
        'schemaVersion': SCHEMA_VERSION,
        'generatedAt': datetime.now(SHANGHAI).isoformat(timespec='seconds'),
        'timezone': 'Asia/Shanghai',
        'source': SOURCE,
        'summary': finish(total),
        'daily': [dict(date=day, **finish(bucket)) for day, bucket in sorted(daily.items())],
        'models': sorted(([dict(model=model, **finish(bucket)) for model, bucket in models.items()]),
                         key=lambda item: (-item['totalTokens'], item['model'])),
    }


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
    parser.add_argument('--ledger', help='usage.jsonl path (default: MAGPIE_USAGE_LEDGER, then the known install)')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    data = export_usage(read_ledger(ledger_path(args.ledger)))
    changed = write_snapshot(data, args.output)
    print(json.dumps({'changed': changed, 'summary': data['summary']}, ensure_ascii=False))
