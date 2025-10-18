@echo off
echo Setting up daily China pattern monitoring...
echo.

REM Create scheduled task to run daily at 7 AM
schtasks /create /tn "ChinaPatternMonitor" /tr "python C:\Projects\OSINT - Foresight\scripts\china_monitor.py" /sc daily /st 07:00 /f

echo.
echo Scheduled task created successfully!
echo The monitoring script will run daily at 7:00 AM
echo.
echo You can also run it manually anytime with:
echo python "C:\Projects\OSINT - Foresight\scripts\china_monitor.py"
echo.
pause
