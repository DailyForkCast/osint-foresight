# PowerShell script to set up scheduled tasks for China Analysis Index updates
# Creates two tasks: one at midnight and one at noon

$taskPath = "C:\Projects\OSINT - Foresight\scripts\schedule_china_index_update.bat"

# Create midnight task
$action = New-ScheduledTaskAction -Execute $taskPath
$trigger1 = New-ScheduledTaskTrigger -Daily -At 12:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "ChinaAnalysisIndexUpdate_Midnight" `
    -Action $action `
    -Trigger $trigger1 `
    -Settings $settings `
    -Description "Updates China Analysis Index at midnight daily" `
    -Force

# Create noon task
$trigger2 = New-ScheduledTaskTrigger -Daily -At 12:00PM

Register-ScheduledTask -TaskName "ChinaAnalysisIndexUpdate_Noon" `
    -Action $action `
    -Trigger $trigger2 `
    -Settings $settings `
    -Description "Updates China Analysis Index at noon daily" `
    -Force

Write-Host "[SUCCESS] China Analysis Index scheduled tasks created:"
Write-Host "  - ChinaAnalysisIndexUpdate_Midnight (00:00 daily)"
Write-Host "  - ChinaAnalysisIndexUpdate_Noon (12:00 daily)"
Write-Host ""
Write-Host "To view tasks: Get-ScheduledTask -TaskName 'ChinaAnalysisIndex*'"
Write-Host "To run manually: Start-ScheduledTask -TaskName 'ChinaAnalysisIndexUpdate_Midnight'"
