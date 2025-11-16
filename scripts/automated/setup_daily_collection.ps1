# Setup Windows Task Scheduler for Daily GDELT Collection
# Run this once to set up automatic 2am daily collection

$TaskName = "GDELT_Daily_Collection"
$ScriptPath = "C:\Projects\OSINT-Foresight\scripts\automated\run_daily_collection.bat"
$Time = "02:00"

Write-Host "Setting up daily GDELT collection..." -ForegroundColor Cyan
Write-Host "Task Name: $TaskName"
Write-Host "Script: $ScriptPath"
Write-Host "Schedule: Daily at $Time"
Write-Host ""

# Delete existing task if it exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create scheduled task action
$Action = New-ScheduledTaskAction -Execute $ScriptPath

# Create trigger (daily at 2am)
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time

# Create settings
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -DontStopIfGoingOnBatteries `
    -AllowStartIfOnBatteries

# Register task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily GDELT event collection - collects previous day's China-related events" `
    -RunLevel Highest

Write-Host ""
Write-Host "SUCCESS! Task created." -ForegroundColor Green
Write-Host ""
Write-Host "Next run: Tomorrow at $Time" -ForegroundColor Cyan
Write-Host ""
Write-Host "To verify:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "To run manually now:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  Get-Content C:\Projects\OSINT-Foresight\logs\daily_gdelt_*.log -Tail 50"
