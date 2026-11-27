# AI 用量统计

## 数据与口径

统计来源是本机逐条调用记录 `D:/Dev/OpenCode/config-root/magpie/usage.jsonl`，由导出器**自己重新聚合**，不使用 `magpie usage --csv` 的汇总，也不把已发布的旧快照当历史合并。Astro 构建期读取 `public/data/usage.json` 生成 `/usage/` 与首页摘要；对外只发布日期、模型与汇总数字，不发布请求明细、会话正文、供应商配置或凭据。

台账每行是一次调用：`in` 是未命中缓存的输入（缓存未命中），`out` 是输出，`cache_read` 是缓存命中，`cache_write` 是缓存写入，`cost` 是记录里已有的美元成本估算，未定价调用可能没有这个字段；`source=reported` 的行是从本机各 Agent 会话文件补录的调用，`source` 为空/其他值是网关直接处理的调用。`rid` 或 `route_id` 用于去重，`rejected=true` 的行整体不计。每日按 Asia/Shanghai 分桶。

**总量 = 缓存未命中 + 输出 + 缓存命中 + 缓存写入**，四项全部计入；缓存命中率 = 命中 /（未命中 + 命中 + 写入）。快照 `schemaVersion` 为 4，单一来源、全日期一条时间线；不再有 `history` 块，也不在每天标 `source`。成本直接汇总记录里的估算值，不重新定价，未定价行可能没有成本，因此它不是实际账单。

网关直连的行可能没有 `cost`，也没有 `rid`（用 `route_id` 去重）；它们照常计入 token，只是不贡献成本。热力图用最近 53 周活动日的四分位数分档；未来日期不计入，零用量保持空格。

## 手动操作

```powershell
python scripts/export_usage.py                       # 写本地快照
python scripts/export_usage.py --ledger "D:\Dev\OpenCode\config-root\magpie\usage.jsonl"
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/sync_usage.py --dry-run
python scripts/sync_usage.py
```

台账路径按 `--ledger`、环境变量 `MAGPIE_USAGE_LEDGER`、默认安装路径的顺序解析；显式传了 `--ledger` 但文件不存在会报错，不会退回默认路径，也不会发布零值。`export_usage.py` 只更新本地快照；数据和上次相同则不改写文件。

`sync_usage.py` 先读取 GitHub 上已有的快照，仅用于乐观锁 SHA 和“数字未变就不提交”的判断，**不再把远端数字合并进新快照**。它只通过现有 `gh` 登录更新 `public/data/usage.json`，不操作工作区，不提交其他文件。失败保留线上快照并返回非零状态。

## 每日同步

执行 `scripts/install-usage-task.ps1` 注册 `JJLab-DailyUsageSync`：Windows 本地时间 20:00、当前用户登录时运行，错过后可补跑，失败每隔 5 分钟重试，最多 3 次。任务使用 `pythonw.exe` 隐藏窗口，并显式带上台账路径与 `gh` 路径。台账默认 `D:\Dev\OpenCode\config-root\magpie\usage.jsonl`，也可用 `MAGPIE_USAGE_LEDGER` 覆盖；电脑离线时网页保留上次快照。任务不内置密钥。

前提：本机有可读取的 `usage.jsonl`（其中已有当日调用）；现有 `gh` 登录有仓库写权限，且 `gh` 在用户 PATH 中。脚本只读台账，不启动或改写任何 Agent 会话文件。

检查状态：

```powershell
Get-ScheduledTask -TaskName JJLab-DailyUsageSync
Get-ScheduledTaskInfo -TaskName JJLab-DailyUsageSync
Get-Content "$env:LOCALAPPDATA/JJLab/usage-sync.log" -Tail 10
```

删除任务：`Unregister-ScheduledTask -TaskName JJLab-DailyUsageSync -Confirm:$false`。

## 发布

汇总 JSON 提交到 `main` 后沿用现有 GitHub Pages 工作流，构建通过才部署。若在其他电脑上使用同一博客，避免安装第二个同步任务，以免不同机器的台账互相覆盖（`sync_usage.py` 以远端 SHA 乐观锁阻止并发覆盖）。升级或移动台账后如字段变化，导出器会报错而不是发布零值，应先对照 `usage.jsonl` 并运行测试。
