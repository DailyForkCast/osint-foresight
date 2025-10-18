# PowerShell script to set up OSINT automation
# This creates scheduled tasks for automatic intelligence collection

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OSINT AUTOMATION SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script needs to run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Close this window" -ForegroundColor Yellow
    Write-Host "2. Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "3. Navigate to: cd `"C:\Projects\OSINT - Foresight`"" -ForegroundColor Yellow
    Write-Host "4. Run: .\AUTOMATE_NOW.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "Running as Administrator - Good!" -ForegroundColor Green
Write-Host ""

# Define the action (what to run)
$scriptPath = "C:\Projects\OSINT - Foresight\scripts\scheduled_intelligence_runner.bat"

# Create action
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`""

# Create triggers
Write-Host "Creating scheduled tasks..." -ForegroundColor Yellow

# Daily at 6 AM
try {
    $dailyTrigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
    Register-ScheduledTask -TaskName "OSINT_Daily_Intelligence" `
                          -Action $action `
                          -Trigger $dailyTrigger `
                          -Description "Daily OSINT China risk intelligence collection" `
                          -Force | Out-Null
    Write-Host "[OK] Daily intelligence collection scheduled for 6:00 AM" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create daily task: $_" -ForegroundColor Red
}

# Weekly on Mondays at 8 AM
try {
    $weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8:00AM
    Register-ScheduledTask -TaskName "OSINT_Weekly_Analysis" `
                          -Action $action `
                          -Trigger $weeklyTrigger `
                          -Description "Weekly OSINT comprehensive analysis" `
                          -Force | Out-Null
    Write-Host "[OK] Weekly analysis scheduled for Mondays at 8:00 AM" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create weekly task: $_" -ForegroundColor Red
}

# Every 4 hours during business hours (more practical than every hour)
try {
    $fourHourlyTrigger = New-ScheduledTaskTrigger -Once -At 8:00AM -RepetitionInterval (New-TimeSpan -Hours 4) -RepetitionDuration (New-TimeSpan -Hours 12)
    Register-ScheduledTask -TaskName "OSINT_Regular_Updates" `
                          -Action $action `
                          -Trigger $fourHourlyTrigger `
                          -Description "Regular OSINT updates every 4 hours" `
                          -Force | Out-Null
    Write-Host "[OK] Regular updates scheduled every 4 hours (8AM-8PM)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create regular update task: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AUTOMATION SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your OSINT platform will now run automatically:" -ForegroundColor White
Write-Host "  - Daily at 6:00 AM" -ForegroundColor White
Write-Host "  - Weekly on Mondays at 8:00 AM" -ForegroundColor White
Write-Host "  - Every 4 hours during business hours" -ForegroundColor White
Write-Host ""
Write-Host "You can also run manually anytime:" -ForegroundColor Yellow
Write-Host "  - Double-click: RUN_NOW.bat" -ForegroundColor Yellow
Write-Host "  - Or run: python MASTER_CONTROL.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test automation now:" -ForegroundColor Cyan
Write-Host "  schtasks /run /tn `"OSINT_Daily_Intelligence`"" -ForegroundColor White
Write-Host ""

# Ask if user wants to run a test now
$response = Read-Host "Would you like to run a test collection now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "Running test collection..." -ForegroundColor Yellow
    Start-ScheduledTask -TaskName "OSINT_Daily_Intelligence"
    Write-Host "Test started! Check the analysis folder for reports." -ForegroundColor Green
}

Write-Host ""
Read-Host "Press Enter to exit"
