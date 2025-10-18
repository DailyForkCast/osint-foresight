@echo off
REM Schedule README updates every 12 hours using Windows Task Scheduler

echo Setting up README auto-update schedule...

REM Create task to run every 12 hours
schtasks /create /tn "OSINT-README-Update" /tr "python \"C:\Projects\OSINT - Foresight\scripts\update_readme.py\"" /sc DAILY /mo 1 /st 06:00 /f

REM Also create second task 12 hours later
schtasks /create /tn "OSINT-README-Update-Evening" /tr "python \"C:\Projects\OSINT - Foresight\scripts\update_readme.py\"" /sc DAILY /mo 1 /st 18:00 /f

echo ✅ README auto-update scheduled for 6:00 AM and 6:00 PM daily
echo.
echo To check scheduled tasks:
echo   schtasks /query /tn "OSINT-README-Update*"
echo.
echo To delete scheduled tasks:
echo   schtasks /delete /tn "OSINT-README-Update" /f
echo   schtasks /delete /tn "OSINT-README-Update-Evening" /f
echo.
echo To run update manually:
echo   python "C:\Projects\OSINT - Foresight\scripts\update_readme.py"

pause
