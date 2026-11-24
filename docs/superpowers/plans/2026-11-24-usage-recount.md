# Usage Recount Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 把博客用量统计改为从本机逐条调用记录重新聚合，展示并计入缓存未命中。

**Architecture:** 重写 Python 导出器，直接流式读取 `usage.jsonl`（网关行 + `source=reported` 会话上报行），按 rid/route_id 去重、按 Asia/Shanghai 分日，输出单来源 schema v4 快照；同步脚本与计划任务改读台账文件；页面加“缓存未命中”指标与每日分项列。

**Tech Stack:** Python 标准库（json / decimal / datetime / pathlib / unittest）、Astro 5 原生组件与 scoped CSS、GitHub Contents API via `gh`、Windows 计划任务。

**Spec:** `docs/superpowers/specs/2026-11-24-usage-recount-design.md`

## Global Constraints

- 不调用 `magpie usage --csv`，不上传逐条记录、会话正文、凭据或供应商配置；只发布日期、模型与汇总数字。
- 台账路径优先级：`--ledger` > `MAGPIE_USAGE_LEDGER` > `D:/Dev/OpenCode/config-root/magpie/usage.jsonl`；找不到报错，禁止发布零值。
- 分日时区固定 `Asia/Shanghai`（UTC+8）；`totalTokens = cacheMissTokens + outputTokens + cacheReadTokens + cacheWriteTokens`。
- `schemaVersion = 4`；`inputTokens` 保留并与 `cacheMissTokens` 同值；不生成 `history` 段，`daily` 不再有 `source` 字段。
- 成本直接取逐条记录的 `cost`，不重新定价；缺字段的行不计成本。
- 修改导出/同步逻辑先跑 `python -m unittest discover -s scripts -p 'test_*.py'`；页面改动跑 `npm run build`。

## Review Focus

- 网关行没有 `rid` 也没有 `cost`：必须照常计入 token，用 `route_id` 去重，成本留空。→ Task 1 测试 `test_gateway_row_without_rid_or_cost_counts_tokens`。
- `rejected=true` 的行：必须整体排除（token、请求、成本都不计）。→ Task 1 测试 `test_rejected_row_is_ignored`。
- 跨时区日界：`2026-11-11T23:30:00-05:00` 必须落到上海日 `2026-11-12`。→ Task 1 测试 `test_shanghai_day_boundary`。
- 线上仍是 schema v3 快照：同步不得把它当历史合并，必须发布 v4。→ Task 2 测试 `test_publishes_v4_without_merging_old_history`。
- 五个摘要指标与每日五列在 320px 与 1440px 不溢出：→ Task 3 用 `npm run build` 与浏览器检查。

---

### Task 1: 从台账重新聚合的导出器

**Files:**
- Rewrite: `scripts/export_usage.py`
- Rewrite: `scripts/test_export_usage.py`

**Interfaces:**
- Consumes: `usage.jsonl` 的行字典：`t`, `agent`, `model`, `req`, `in`, `out`, `cache_read`, `cache_write`, `cost`, `source`, `rid`, `route_id`, `rejected`。
- Produces:
  - `ledger_path(override=None) -> Path`
  - `read_ledger(path=None) -> list[dict]`
  - `empty_bucket() -> dict`
  - `finish(bucket: dict) -> dict`
  - `export_usage(rows: list[dict]) -> dict`
  - `unchanged(left: dict, right: dict) -> bool`
  - `write_snapshot(data: dict, output: Path = OUTPUT) -> bool`
  - `OUTPUT`, `SHANGHAI`, `TOKEN_FIELDS`, `SCHEMA_VERSION = 4`

- [x] **Step 1: Write the failing test**

In `scripts/test_export_usage.py`, add a row factory and these tests (exact assertions):

```python
def ledger_row(t='2026-11-12T16:30:00+08:00', agent='pi', model='m', req='', inp=100,
               out=10, read=50, write=5, cost='0.25', rid='r1', route_id=None, **extra):
    row = dict(t=t, agent=agent, model=model, req=req, **{'in': inp}, out=out,
               cache_read=read, cache_write=write, status=200)
    if cost is not None: row['cost'] = cost
    if rid is not None: row['rid'] = rid
    if route_id is not None: row['route_id'] = route_id
    row.update(extra)
    return row
```

Assertions:
- `result['summary']`: `inputTokens=100`, `cacheMissTokens=100`, `outputTokens=10`, `cacheReadTokens=50`, `cacheWriteTokens=5`, `totalTokens=165`, `cacheHitRate=50/155`, `estimatedCostUsd='0.250000'`.
- `result['daily'][0]['date']=='2026-11-12'` and `result['daily'][0]['totalTokens']==165`.
- `result['models'][0]['model']=='m'`, `totalTokens==165`.
- `result['schemaVersion']==4`, `'history' not in result`, `'source' not in result['daily'][0]`.
- `test_gateway_row_without_rid_or_cost_counts_tokens`: two rows with `rid=None`, `route_id=7`, `cost=None`, `source='gateway'` → `requests==1`, `totalTokens==165`, `estimatedCostUsd=='0.000000'` (same `route_id` counts once).
- `test_rejected_row_is_ignored`: two rows, second `rejected=True`, `inp=999`, `cost='9'` → summary unchanged from one row.
- `test_shanghai_day_boundary`: `t='2026-11-11T23:30:00-05:00'` → `daily[0]['date']=='2026-11-12'`.
- `test_duplicate_rid_counts_once`: two identical `rid='r1'` rows → `requests==1`, `totalTokens` counted once.
- `test_missing_model_uses_requested_model`: `model=''`, `req='vendor/model'` → model name `vendor/model`.
- `test_empty_ledger`: empty rows → summary totals 0, `daily==[]`, `models==[]`.
- `test_unchanged_ignores_generated_at`: same data with different `generatedAt` → `unchanged(...) is True`.
- `test_read_ledger_rejects_missing_columns`: temp JSONL with a row missing `cache_read` → `RuntimeError`.
- `test_ledger_path_missing_raises`: `ledger_path('does-not-exist.jsonl')` → `RuntimeError`.

- [x] **Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s scripts -p 'test_*.py'`
Expected: FAIL with import errors / missing symbols.

- [x] **Step 3: Implement the exporter**

Rewrite `scripts/export_usage.py`:
- Constants: `SHANGHAI`, `ROOT`, `OUTPUT`, `DEFAULT_LEDGER = Path('D:/Dev/OpenCode/config-root/magpie/usage.jsonl')`, `SCHEMA_VERSION = 4`, `TOKEN_FIELDS = ('inputTokens','outputTokens','cacheReadTokens','cacheWriteTokens')` (`cacheMissTokens` mirrors `inputTokens` but is not summed separately), `REQUIRED_COLUMNS = {'t','agent','in','out','cache_read','cache_write','status'}`.
- `ledger_path`: first existing of override, `MAGPIE_USAGE_LEDGER`, `DEFAULT_LEDGER`; `resolve(strict=True)`; raise `RuntimeError('usage ledger not found: ...')`.
- `read_ledger`: open JSONL with `encoding='utf-8'`, `errors='replace'`; skip blank lines; `json.loads`; validate `REQUIRED_COLUMNS <= row.keys()`; return list.
- `empty_bucket`: `dict(requests=0, cacheMissTokens=0, inputTokens=0, outputTokens=0, cacheReadTokens=0, cacheWriteTokens=0, estimatedCostUsd=Decimal(0))`.
- add_row: skip when `row.get('rejected') is True`; `requests += 1`; map `in`→`cacheMissTokens`+`inputTokens`, `out`, `cache_read`, `cache_write`; add Decimal `cost` when present.
- dedup: key `rid` when present else `('route', route_id)` when present else `('line', index)`; skip already-seen keys before `add_row`.
- day: `datetime.fromisoformat(row['t']).astimezone(SHANGHAI).date().isoformat()`.
- `finish`: `totalTokens = sum(result[key] for key in TOKEN_FIELDS)` (inputTokens already equals cacheMissTokens, so the four categories are not double counted); `cacheHitRate = cacheRead / (cacheMiss + cacheRead + cacheWrite)`; format cost with `Decimal('.000001')`.
- `export_usage(rows)`: build `total`, `models`, `daily`; return `schemaVersion`, `generatedAt`, `timezone`, `source: '本机逐条调用记录（网关 + 会话上报）'`, `summary`, `daily`, `models` (sorted by `-totalTokens`, name).
- `unchanged` / `write_snapshot`: keep current behavior, ignoring `generatedAt`.
- CLI: `--ledger`, `--output`; print `{'changed':..., 'summary':...}`.

- [x] **Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s scripts -p 'test_*.py'`
Expected: PASS for all `test_export_usage.py` tests (other test file may still fail until Task 2).

- [x] **Step 5: Commit**

```bash
git add scripts/export_usage.py scripts/test_export_usage.py
git commit -m "feat(usage): recount tokens from the local per-call ledger"
```

### Task 2: 同步脚本与每日任务改读台账

**Files:**
- Modify: `scripts/sync_usage.py`
- Modify: `scripts/install-usage-task.ps1`
- Rewrite: `scripts/test_sync_usage.py`

**Interfaces:**
- Consumes: `ledger_path`, `read_ledger`, `export_usage`, `unchanged`, `OUTPUT` from Task 1.
- Produces: `publish_snapshot(rows, api=gh_api, dry_run=False) -> str` returning `'unchanged' | 'would-publish' | 'published'`; `gh_api`; `main()` supporting `--ledger`, `--gh`, `--dry-run`.

- [x] **Step 1: Write the failing test**

In `scripts/test_sync_usage.py`, add:
- `test_publishes_v4_without_merging_old_history`: remote snapshot is a v3-shaped dict with `history` and a fake day `2026-11-10`; call `publish_snapshot([], api=Mock(return_value=remote))`; assert PUT payload content decodes to `schemaVersion == 4`, `'history' not in data`, and `daily == []`.
- `test_unchanged_when_remote_matches`: remote is `export_usage([])`; assert `publish_snapshot([], api=...) == 'unchanged'` and PUT not called.
- `test_dry_run_does_not_put`: remote different; `dry_run=True` → returns `'would-publish'`, PUT not called.
- `test_put_uses_remote_sha`: assert PUT payload `sha == remote['sha']`.

- [x] **Step 2: Run test to verify it fails**

Run: `python -m unittest discover -s scripts -p 'test_*.py'`
Expected: FAIL because `publish_snapshot` still merges `previous`.

- [x] **Step 3: Implement sync changes**

- `sync_usage.py`: import `ledger_path, read_ledger, export_usage, unchanged` (drop `magpie_executable`); `publish_snapshot` sets `data = export_usage(rows)` and compares `unchanged(previous, data)`; add `--ledger` to argparse; use `read_ledger(ledger_path(args.ledger))`.
- `install-usage-task.ps1`: replace magpie executable lookup with ledger lookup: `$env:MAGPIE_USAGE_LEDGER`, then default `D:\Dev\OpenCode\config-root\magpie\usage.jsonl`; `Test-Path -LiteralPath` else throw; action argument `"$syncScript" --ledger "$ledgerPath" --gh "$ghPath"`; update task description to mention the local ledger.

- [x] **Step 4: Run test to verify it passes**

Run: `python -m unittest discover -s scripts -p 'test_*.py'`
Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add scripts/sync_usage.py scripts/install-usage-task.ps1 scripts/test_sync_usage.py
git commit -m "feat(usage): sync from the local ledger instead of the magpie CLI"
```

### Task 3: 页面展示缓存未命中与分项

**Files:**
- Modify: `src/components/UsageSummary.astro`
- Modify: `src/pages/usage.astro`
- Modify: `src/lib/i18n.ts`

**Interfaces:**
- Consumes: snapshot fields `summary.cacheMissTokens`, `daily[].cacheMissTokens`, `daily[].cacheReadTokens`, `daily[].cacheWriteTokens`, `daily[].outputTokens`, `daily[].totalTokens`, `summary.totalTokens` from Task 1 snapshot.
- Produces: UI copy keys `usage.cacheMiss`, `usage.cacheHit`, `usage.cacheWrite`, `usage.output`, updated `usage.source`, `usage.method`, `usage.sourcesNote`.

- [x] **Step 1: Write the failing check**

Run `npm run build` after the edits below; before edits the new i18n keys and daily columns do not exist. Expected after Step 3: build passes and rendered HTML contains `缓存未命中`.

- [x] **Step 2: Add i18n keys and copy**

In `src/lib/i18n.ts`:
- zh: `usage.cacheMiss: '缓存未命中'`, `usage.cacheHit: '缓存命中'`, `usage.cacheWrite: '缓存写入'`, `usage.output: '输出'`; update `usage.source` to `'数据来源：本机逐条调用记录，含网关与各 Agent 会话上报'`, `usage.sourcesNote` to `'逐条记录，统一口径'`, `usage.method` to `'来源：本机逐条调用记录（含网关请求与各 Agent 会话上报），按 Asia/Shanghai 分日。缓存未命中、命中、写入与输出全部计入总量；成本取记录中已有的估算值，未定价调用可能为空，并非实际账单。电脑离线时保留上次快照。'`.
- en mirror: `'Cache miss'`, `'Cache hit'`, `'Cache write'`, `'Output'`; corresponding source/note/method sentences.

- [x] **Step 3: Update components**

- `UsageSummary.astro`: import `compact`; add a fifth stat `{ key: 'cacheMiss', label: '缓存未命中', value: compact(usage.summary.cacheMissTokens), exact: integer(usage.summary.cacheMissTokens) }`; change `.metrics` grid to `repeat(auto-fit, minmax(150px, 1fr))`.
- `usage.astro`: daily table headers become 日期 / Tokens / 缓存未命中 / 缓存命中 / 缓存写入 / 输出 / 请求；remove the 来源 column and `sourceLabel` helper; render the six numeric fields from each day; keep the existing sources panel but with one row (snapshot `source` string) and remove the “two sources” note.

- [x] **Step 4: Run build and browser check**

Run: `npm run build`
Expected: build passes; inspect `dist/usage/index.html` for `缓存未命中` and the six table headers; at 320px and 1440px no horizontal overflow.

- [x] **Step 5: Commit**

```bash
git add src/components/UsageSummary.astro src/pages/usage.astro src/lib/i18n.ts
git commit -m "feat(usage): show cache misses and per-day token breakdown"
```

### Task 4: 刷新快照、文档与验证

**Files:**
- Modify: `public/data/usage.json`
- Modify: `docs/usage-sync.md`
- Modify: `AGENT.md`

**Interfaces:**
- Consumes: Task 1 exporter and Task 3 copy.
- Produces: committed v4 snapshot and updated operating docs.

- [x] **Step 1: Regenerate the local snapshot**

Run: `python scripts/export_usage.py`
Expected: prints `{"changed": true, "summary": {...}}`; `public/data/usage.json` has `schemaVersion: 4`, `source` string, no `history`, daily rows through the latest ledger day.

- [x] **Step 2: Update docs**

- `docs/usage-sync.md`: describe the ledger file and fields (`in` = cache miss, `out`, `cache_read`, `cache_write`, `cost`, `source`, `rid`/`route_id`); remove CC Switch history / two-source sections; commands use `--ledger`; scheduled task uses `MAGPIE_USAGE_LEDGER`; note gateway rows may lack `cost`.
- `AGENT.md`: replace the AI usage section with the single-ledger recount rule and cache-miss inclusion.

- [x] **Step 3: Full verification**

Run: `python -m unittest discover -s scripts -p 'test_*.py' && npm run build`
Expected: all tests pass; build passes; report summary numbers from the regenerated snapshot.

- [x] **Step 4: Commit**

```bash
git add public/data/usage.json docs/usage-sync.md AGENT.md
git commit -m "data: recount usage from the local ledger"
```
