$ErrorActionPreference = 'Stop'
$taskName = 'JJLab-DailyUsageSync'
$pythonPath = (Get-Command pythonw.exe -ErrorAction Stop).Source
$ghPath = (Get-Command gh -ErrorAction Stop).Source
$ledgerPath = $env:MAGPIE_USAGE_LEDGER
if (-not $ledgerPath) { $ledgerPath = 'D:\Dev\OpenCode\config-root\magpie\usage.jsonl' }
if (-not (Test-Path -LiteralPath $ledgerPath)) {
  throw "usage ledger not found. Set `$env:MAGPIE_USAGE_LEDGER to usage.jsonl, then run this script again."
}
$syncScript = Join-Path $PSScriptRoot 'sync_usage.py'
# pythonw hides the scheduled task window; gh uses the existing Windows login.
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument ('"' + $syncScript + '" --ledger "' + $ledgerPath + '" --gh "' + $ghPath + '"') -WorkingDirectory (Split-Path $PSScriptRoot)
$trigger = New-ScheduledTaskTrigger -Daily -At '20:00'
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Publish recounted local usage aggregates only to the JJ Lab blog at 20:00 local time.' -Force | Select-Object TaskName,State
