# AI 用量统计

## 数据与口径

本机 magpie 的 `magpie usage --csv all` 只读导出至 `public/data/usage.json`，Astro 构建期生成 `/usage/` 与首页摘要。对外只发布日期、模型与汇总数字，不发布请求明细、会话正文、供应商配置或凭据。

CSV 是 magpie 的公开逐次调用台账：网关记录的调用，加上 magpie 从各 Agent 会话文件里读到、网关没见过的调用，已由 magpie 去重。每行 `input_tokens` 不含缓存读取与写入（它们各占一列），`cost_usd` 是 magpie 按生效价格估算的美元成本，未定价模型留空；`handed_on` 为 `true` 的行是失败后交给同一路由下一次尝试的尝试，它计费但不算一次请求；`rejected` 为 `true` 的行（未发出上游就被拒）整体不计入。每日按 Asia/Shanghai 分桶。

迁移前博客发布的是 CC Switch 的数字，快照因此把那段时期冻结成 `history` 块（来源、截止日期、汇总与模型分布），magpie 从 `MAGPIE_SINCE`（2026-11-11）起接管，两天不在同一份数据里重复计。历史明细（`daily` 中 2026-11-10 及更早的日期）继续随快照保留，热力图不断档。

费用直接汇总 magpie 已记录的估算成本，不重新定价。未定价模型的费用可能为零，因此它不是实际账单。热力图用最近 53 周活动日的四分位数分档；未来日期不计入，零用量保持空格。

## 手动操作

```powershell
python scripts/export_usage.py                       # 写本地快照
python scripts/export_usage.py --magpie "E:\edge download\magpie-windows-amd64.exe"
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/sync_usage.py --dry-run
python scripts/sync_usage.py
```

magpie 可执行文件按 `--magpie`、环境变量 `MAGPIE_BIN`、`PATH` 中的 `magpie.exe`、默认安装路径的顺序查找，找不到就报错而不是发布零值。`export_usage.py` 只更新本地快照；数据和上次相同则不改写文件。

`sync_usage.py` 先读取 GitHub 上已有的快照作为历史基准，再把本机台账合并进去，通过现有 `gh` 登录只更新 `public/data/usage.json`，不操作工作区，不提交其他文件。数字未改变时不产生提交；SHA 乐观锁阻止覆盖并发更新。失败保留线上快照并返回非零状态。

## 每日同步

执行 `scripts/install-usage-task.ps1` 注册 `JJLab-DailyUsageSync`：Windows 本地时间 20:00、当前用户登录时运行，错过后可补跑，失败每隔 5 分钟重试，最多 3 次。任务使用 `pythonw.exe` 隐藏窗口并显式带上 magpie 与 `gh` 路径；电脑离线时网页保留上次快照。

前提：magpie 正在（或曾经）运行并已记录用量（`magpie usage` 能列出今天的调用）；现有 `gh` 登录有仓库写权限，且 `gh` 在用户 PATH 中。脚本只读 magpie 的台账，不会启动 magpie，也不会扫描或改写会话文件。任务不内置密钥。

检查状态：

```powershell
Get-ScheduledTask -TaskName JJLab-DailyUsageSync
Get-ScheduledTaskInfo -TaskName JJLab-DailyUsageSync
Get-Content "$env:LOCALAPPDATA/JJLab/usage-sync.log" -Tail 10
```

删除任务：`Unregister-ScheduledTask -TaskName JJLab-DailyUsageSync -Confirm:$false`。

## 发布

汇总 JSON 提交到 `main` 后沿用现有 GitHub Pages 工作流，构建通过才部署。若在其他电脑上使用同一博客，避免安装第二个同步任务，以免不同机器的台账互相覆盖（`sync_usage.py` 以线上快照为历史基准，因此并发运行仍可能叠加两份用量）。升级 magpie 后如 CSV 列变化，导出器会报错而非发布零值，应先对照 `magpie usage --csv` 并运行测试。
