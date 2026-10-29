# AI 用量统计

## 数据与口径

本机 CC Switch 的 `~/.cc-switch/cc-switch.db` 只读导出至 `public/data/usage.json`，Astro 构建期生成 `/usage/` 与首页摘要。对外只发布日期、模型与汇总数字，不发布请求明细、会话正文、供应商配置或凭据。

归一化跟随 CC Switch 的 `services/sql_helpers.rs`：Codex/Gemini/Grok 的 legacy 输入扣除缓存读取、total 输入扣除缓存读取与写入、fresh 输入保持原值。与代理请求重复的会话按上游的 600 秒窗口、应用、模型、Token 与成功状态去重。历史日汇总已由上游事务汇总并删除原明细，与剩余明细合并。每日按 Asia/Shanghai 分桶。

费用直接汇总 CC Switch 已记录的估算成本，不重新定价。未定价模型的费用可能为零，因此它不是实际账单。热力图用最近 53 周活动日的四分位数分档；未来日期不计入，零用量保持空格。

## 手动操作

```powershell
python scripts/export_usage.py
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/sync_usage.py --dry-run
python scripts/sync_usage.py
```

`export_usage.py` 只更新本地快照；相同数据不会更新时间。
`sync_usage.py` 直接读取本机数据库，通过现有 `gh` 登录只更新 GitHub 的 `public/data/usage.json`，不操作工作区，不提交其他文件。数字未改变时不产生提交；SHA 乐观锁阻止覆盖并发更新。失败保留线上快照并返回非零状态。

## 每日同步

执行 `scripts/install-usage-task.ps1` 注册 `JJLab-DailyUsageSync`：Windows 本地时间 20:00、当前用户登录时运行，错过后可补跑，失败每隔 5 分钟重试，最多 3 次。任务使用 `pythonw.exe` 隐藏窗口；电脑离线时网页保留上次快照。

前提：CC Switch 已扫描会话日志；现有 `gh` 登录有仓库写权限，且 `gh` 在用户 PATH 中。脚本仅导出数据库现状，不会启动 CC Switch 或强制扫描历史日志。任务不内置密钥。

检查状态：

```powershell
Get-ScheduledTask -TaskName JJLab-DailyUsageSync
Get-ScheduledTaskInfo -TaskName JJLab-DailyUsageSync
Get-Content "$env:LOCALAPPDATA/JJLab/usage-sync.log" -Tail 10
```

删除任务：`Unregister-ScheduledTask -TaskName JJLab-DailyUsageSync -Confirm:$false`。

## 发布

汇总 JSON 提交到 `main` 后沿用现有 GitHub Pages 工作流，构建通过才部署。若在其他电脑上使用同一博客，避免安装第二个同步任务，以免不同数据库快照互相覆盖。升级 CC Switch 后如统计结构变化，导出器会报错而非发布零值，应先对照上游并运行测试。
