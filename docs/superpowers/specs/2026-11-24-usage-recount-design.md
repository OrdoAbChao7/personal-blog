# 用量重新统计：设计（待确认）

## 意图

把 `/usage/` 和首页摘要的口径从“magpie CLI 汇总”改成“本机逐条调用记录重新统计”：

- 目标是**这台电脑一天消耗的 AI token 总量**，不是只看经过网关的请求。
- **缓存未命中**（未缓存的输入 token）要单独展示，并计入总量。
- 不再把旧 CC Switch 快照当成冻结的 `history` 段；所有日期由同一份逐条记录算出，一条时间线。

## 现状（查证结果）

1. 线上快照每天 20:00 由计划任务更新；仓库内 `public/data/usage.json` 停在 11/14，本地预览会明显偏少。11/12 旧快照 15 token，而现有逐条记录中那天约 2.17 亿——早期会话记录是后来补录的。
2. 逐条记录文件：`D:/Dev/OpenCode/config-root/magpie/usage.jsonl`（约 43.8 MB，11 万余行）。每行有 `t`、`agent`、`model`、`in`、`out`、`cache_read`、`cache_write`、`cost`、`source`、`rid`。
3. 其中 `source=reported` 约 10 万行，来自本机 Claude / Codex / Gemini / Antigravity / pi 等会话文件以及迁移进来的 CC Switch 历史；`source` 为空的行才是网关直接处理的请求。所以它已经覆盖整台电脑，不只是网关流量。
4. 只解析各 Agent 原始会话文件并不足以得到“电脑总量”：例如 11/14 Antigravity 的 `transcript.jsonl` 只有 41 条，而逐条记录里有 3339 条；纯会话文件方案会把那天少算近一半。Claude / Codex / pi 的原始会话与逐条记录基本吻合。
5. CC Switch 数据库已在 11/14 停止更新；其历史已导入上面的逐条记录，因此不需要继续保留双来源结构。

## 方案

**选定：以逐条记录为原始输入，自己重新聚合（不调用 `magpie usage --csv`，也不沿用已发布的汇总数字）。**

- 逐行流式读取 `usage.jsonl`，按 `rid` 去重，按 `Asia/Shanghai` 分日。
- 每条调用记账：`cacheMissTokens = in`，`cacheReadTokens = cache_read`，`cacheWriteTokens = cache_write`，`outputTokens = out`，`estimatedCostUsd += cost`。
- `totalTokens = cacheMiss + output + cacheRead + cacheWrite`（四项都算，不扣除未命中）。
- `cacheHitRate = cacheRead / (cacheMiss + cacheRead + cacheWrite)`。
- 模型分布按 `model`（缺失时用 `req`）分组；请求数按每条有效调用计 1。
- 快照 schema 升到 v4，新增 `cacheMissTokens` 字段（`inputTokens` 保留同值以兼容旧读者）；去掉 `history` / `source` 双段，改为单来源、全日期。
- 页面：摘要卡增加“缓存未命中”；每日明细表增加“未命中 / 命中 / 写入 / 输出 / 总计”列；说明文字改成“本机逐条调用记录，含网关与各 Agent 会话上报；未命中计入总量”。中英文同步。
- 同步脚本改为直接读 `usage.jsonl`（可用 `--ledger` 覆盖路径），继续只通过现有 `gh` 登录更新远端 `public/data/usage.json`；计划任务改为传台账路径而非 magpie 可执行文件。
- 本地快照补一次与线上一致的重算，避免预览与线上不一致。

## 不做的

- 不解析 CC Switch 数据库或各 Agent 会话正文来替代台账（会漏算 Antigravity 等来源，正是“看着少”的原因）。
- 不上传逐条记录、会话内容、模型密钥或供应商配置；只发布日期、模型与汇总数字。
- 不重新定价成本：`cost` 直接取逐条记录里已有的估算值，未定价调用留空。

## 风险 / 边界

- 依赖本机 `usage.jsonl` 的路径；路径变化要显式配置，找不到就报错，不发布零值。
- 逐条记录里 `rejected` 类调用需排除；`status` 非成功的行按现有规则保留计费但可标记为尝试（沿用当前口径：失败交接不计请求数）。
- 若某天原始记录缺失（旧机器、清理过日志），那天的数字会缺，不会从旧快照补。

## 验证

- 单测：去重、上海日界、缓存未命中计入总量、未定价成本、空数据、schema v4、与旧快照不兼容时拒绝合并。
- 与现有 CSV 对账：同一天总量应接近（允许去重规则差异），逐日差异写进说明。
- `npm run build`；`/usage/` 与首页摘要在桌面和手机宽度无溢出。
