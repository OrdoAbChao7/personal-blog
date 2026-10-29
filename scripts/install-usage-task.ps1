$ErrorActionPreference = 'Stop'
$taskName = 'JJLab-DailyUsageSync'
$pythonPath = (Get-Command pythonw.exe -ErrorAction Stop).Source
$ghPath = (Get-Command gh -ErrorAction Stop).Source
$syncScript = Join-Path $PSScriptRoot 'sync_usage.py'
# pythonw hides the scheduled task window; gh uses the existing Windows login.
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument ('"' + $syncScript + '" --gh "' + $ghPath + '"') -WorkingDirectory (Split-Path $PSScriptRoot)
$trigger = New-ScheduledTaskTrigger -Daily -At '20:00'
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Publish CC Switch daily aggregates only to the JJ Lab blog at 20:00 local time.' -Force | Select-Object TaskName,State
