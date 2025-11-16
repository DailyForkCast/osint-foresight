# PowerShell script to create Windows scheduled tasks
# Run as Administrator

$projectDir = "C:\Projects\OSINT - Foresight"
$pythonPath = "python"

Write-Host "Creating OSINT Foresight Automated Tasks..." -ForegroundColor Green

# Create logs directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "$projectDir\logs" | Out-Null

# Task 1: Weekly EU/MCF Sweep
$action1 = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c cd /d `"$projectDir`" && $pythonPath scripts/automation/intake_scheduler.py --run-weekly >> logs/weekly_sweep.log 2>&1"
$trigger1 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "OSINT_Weekly_MCF_Sweep" -Action $action1 -Trigger $trigger1 -Settings $settings1 -Force
Write-Host "[OK] Created: OSINT_Weekly_MCF_Sweep (Mondays 9:00 AM)" -ForegroundColor Cyan

# Task 2: Regional Sprint Rotation
$action2 = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c cd /d `"$projectDir`" && $pythonPath scripts/automation/intake_scheduler.py --run-sprint >> logs/regional_sprint.log 2>&1"
$trigger2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 10am
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "OSINT_Regional_Sprint" -Action $action2 -Trigger $trigger2 -Settings $settings2 -Force
Write-Host "[OK] Created: OSINT_Regional_Sprint (Sundays 10:00 AM)" -ForegroundColor Cyan

# Task 3: Gap Map Refresh
$action3 = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c cd /d `"$projectDir`" && $pythonPath scripts/automation/intake_scheduler.py --refresh-gap >> logs/gap_refresh.log 2>&1"
$trigger3 = New-ScheduledTaskTrigger -Daily -At 11pm
$settings3 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "OSINT_Gap_Map_Refresh" -Action $action3 -Trigger $trigger3 -Settings $settings3 -Force
Write-Host "[OK] Created: OSINT_Gap_Map_Refresh (Daily 11:00 PM)" -ForegroundColor Cyan

Write-Host "`nScheduled tasks created successfully!" -ForegroundColor Green
Write-Host "`nTo view tasks: taskschd.msc" -ForegroundColor Yellow
Write-Host "To remove tasks: Get-ScheduledTask -TaskName 'OSINT_*' | Unregister-ScheduledTask -Confirm:`$false" -ForegroundColor Yellow
Write-Host "`nFirst run: Monday, October 14, 2025, 9:00 AM (Weekly MCF Sweep)" -ForegroundColor Cyan
Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
