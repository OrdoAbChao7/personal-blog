"""Read magpie usage only; never export providers, sessions or credentials.

`magpie usage --csv` is magpie's public per-call ledger: the calls its gateway
logged plus the calls the agents' own session files recorded that the gateway
did not see, already deduplicated by magpie. A row's `input_tokens` excludes
cache reads and writes (they have their own columns), `cost_usd` is the
effective price in USD and is empty for a model magpie could not price, and a
row with `handed_on` is a failed try whose request the next row of the same
route finished: it is billed, but it is not a request.

The blog published CC Switch's numbers until the migration on 2026-11-10. A
snapshot therefore keeps that period as a frozen `history` block and lets
magpie own every day from MAGPIE_SINCE on, so no day is counted twice.
"""
import argparse
import csv
import io
import json
import os
import shutil
import subprocess
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

SHANGHAI = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public' / 'data' / 'usage.json'
DEFAULT_MAGPIE = Path('E:/edge download/magpie-windows-amd64.exe')
# The old snapshot's last day is 2026-11-10, the day magpie took over; magpie
# owns the day after, so the two sources never share a day.
MAGPIE_SINCE = '2026-11-11'
SCHEMA_VERSION = 2
TOKEN_FIELDS = ('inputTokens', 'outputTokens', 'cacheReadTokens', 'cacheWriteTokens')
REQUIRED_COLUMNS = {'time', 'requested_model', 'model', 'input_tokens', 'output_tokens',
                    'cache_write_tokens', 'cache_read_tokens', 'cost_usd', 'rejected', 'handed_on'}


def magpie_executable(path=None):
    for candidate in (path, os.environ.get('MAGPIE_BIN'), shutil.which('magpie'),
                      shutil.which('magpie.exe'), DEFAULT_MAGPIE):
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise RuntimeError('magpie not found: pass --magpie <path> or set MAGPIE_BIN')


def read_ledger(executable, period='all'):
    result = subprocess.run([executable, 'usage', '--csv', period], capture_output=True,
                            text=True, encoding='utf-8', timeout=300,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    if result.returncode:
        raise RuntimeError(f'magpie usage failed: {result.stderr.strip()[-500:]}')
    reader = csv.DictReader(io.StringIO(result.stdout))
    missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
    if missing:
        raise RuntimeError(f'Unsupported magpie ledger columns: {", ".join(sorted(missing))}')
    return list(reader)


def empty_bucket():
    return dict(requests=0, inputTokens=0, outputTokens=0, cacheReadTokens=0,
                cacheWriteTokens=0, estimatedCostUsd=Decimal(0))


def bucket_of(entry):
    return dict(requests=int(entry['requests']), inputTokens=int(entry['inputTokens']),
                outputTokens=int(entry['outputTokens']), cacheReadTokens=int(entry['cacheReadTokens']),
                cacheWriteTokens=int(entry['cacheWriteTokens']),
                estimatedCostUsd=Decimal(entry['estimatedCostUsd']))


def add_bucket(bucket, other):
    for key in bucket:
        if key != 'estimatedCostUsd':
            bucket[key] += other[key]
    bucket['estimatedCostUsd'] += other['estimatedCostUsd']


def add_row(bucket, row):
    if row['handed_on'] != 'true':
        bucket['requests'] += 1
    bucket['inputTokens'] += int(row['input_tokens'] or 0)
    bucket['outputTokens'] += int(row['output_tokens'] or 0)
    bucket['cacheReadTokens'] += int(row['cache_read_tokens'] or 0)
    bucket['cacheWriteTokens'] += int(row['cache_write_tokens'] or 0)
    if row['cost_usd']:
        bucket['estimatedCostUsd'] += Decimal(row['cost_usd'])


def finish(bucket):
    result = dict(bucket)
    result['totalTokens'] = sum(result[key] for key in TOKEN_FIELDS)
    denominator = result['inputTokens'] + result['cacheReadTokens'] + result['cacheWriteTokens']
    result['cacheHitRate'] = result['cacheReadTokens'] / denominator if denominator else 0
    result['estimatedCostUsd'] = format(result['estimatedCostUsd'].quantize(Decimal('.000001')), 'f')
    return result


def frozen_history(history):
    """The pre-migration period a snapshot carries, as its own block.

    Taken from the snapshot's `history` block once it has one; the first run
    after the migration takes it from a CC Switch snapshot instead, and refuses
    one that already holds magpie days, which merging again would double count.
    """
    if not history:
        return None
    if 'history' in history:
        return history['history']
    days = history.get('daily') or []
    if not days:
        return None
    last = max(day['date'] for day in days)
    if last >= MAGPIE_SINCE:
        raise RuntimeError(f'history snapshot already covers {last}, not before {MAGPIE_SINCE}')
    return {'source': history.get('source', 'CC Switch'), 'until': last,
            'summary': history['summary'], 'models': history['models']}


def export_usage(rows, history=None, since=MAGPIE_SINCE):
    since_day = date.fromisoformat(since)
    history = history or {}
    legacy = frozen_history(history)
    carried = {day['date']: day for day in history.get('daily', []) if day['date'] < since}

    total = empty_bucket()
    models = {}
    if legacy:
        add_bucket(total, bucket_of(legacy['summary']))
        for model in legacy['models']:
            add_bucket(models.setdefault(model['model'], empty_bucket()), bucket_of(model))

    daily = defaultdict(empty_bucket)
    for row in rows:
        if row['rejected'] == 'true':
            continue
        when = datetime.fromisoformat(row['time']).astimezone(SHANGHAI)
        if when.date() < since_day:
            continue
        name = row['model'] or row['requested_model'] or 'unknown'
        for bucket in (daily[when.date().isoformat()], models.setdefault(name, empty_bucket()), total):
            add_row(bucket, row)

    merged = [dict(date=day, **finish(bucket)) for day, bucket in sorted(daily.items())]
    merged += [day for day in carried.values() if day['date'] not in daily]
    merged.sort(key=lambda day: day['date'])
    return {
        'schemaVersion': SCHEMA_VERSION,
        'generatedAt': datetime.now(SHANGHAI).isoformat(timespec='seconds'),
        'timezone': 'Asia/Shanghai',
        'source': 'magpie',
        'history': legacy,
        'summary': finish(total),
        'daily': merged,
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
    parser.add_argument('--magpie', help='magpie executable (default: MAGPIE_BIN, PATH, then the known install)')
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    history = None
    if args.output.exists():
        history = json.loads(args.output.read_text(encoding='utf-8'))
    data = export_usage(read_ledger(magpie_executable(args.magpie)), history)
    changed = write_snapshot(data, args.output)
    print(json.dumps({'changed': changed, 'summary': data['summary']}, ensure_ascii=False))
