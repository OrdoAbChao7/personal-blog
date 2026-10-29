"""Publish only the public usage snapshot using the user's existing gh login."""
import argparse
import base64
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from export_usage import DEFAULT_DB, read_usage, unchanged

ENDPOINT = 'repos/OrdoAbChao7/personal-blog/contents/public/data/usage.json'


def gh_api(method, path, payload=None, executable='gh'):
    command = [executable, 'api', '--method', method, path]
    if payload is not None:
        command += ['--input', '-']
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            capture_output=True, text=True, encoding='utf-8', timeout=90,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    if result.returncode:
        raise RuntimeError(f'GitHub API failed: {result.stderr.strip()}')
    return json.loads(result.stdout)


def publish_snapshot(data, api=gh_api, dry_run=False):
    remote = api('GET', ENDPOINT + '?ref=main')
    previous = json.loads(base64.b64decode(remote['content']).decode('utf-8'))
    if unchanged(previous, data):
        return 'unchanged'
    if dry_run:
        return 'would-publish'
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    api('PUT', ENDPOINT, {'message':'data: sync daily AI usage', 'branch':'main',
                          'sha':remote['sha'], 'content':base64.b64encode(content.encode('utf-8')).decode('ascii')})
    return 'published'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--gh', default='gh', help='Absolute gh executable path for scheduled runs')
    args = parser.parse_args()
    log_dir = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'JJLab'
    log_dir.mkdir(parents=True, exist_ok=True)
    try:
        api = lambda method, path, payload=None: gh_api(method, path, payload, executable=args.gh)
        status = publish_snapshot(read_usage(args.db), api=api, dry_run=args.dry_run)
        message = f'{datetime.now().isoformat(timespec="seconds")} {status}'
        code = 0
    except Exception as error:
        message = f'{datetime.now().isoformat(timespec="seconds")} FAILED: {error}'
        code = 1
    with (log_dir / 'usage-sync.log').open('a', encoding='utf-8') as log:
        log.write(message + '\n')
    print(message)
    return code


if __name__ == '__main__':
    sys.exit(main())
