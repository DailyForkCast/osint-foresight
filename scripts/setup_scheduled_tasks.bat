@echo off
REM Setup Windows Scheduled Tasks for OSINT Platform
REM Run as Administrator for best results

echo Setting up OSINT Scheduled Tasks...

REM Daily intelligence collection at 6 AM
schtasks /create /tn "OSINT_Daily_Intelligence" /tr "C:\Projects\OSINT - Foresight\scripts\scheduled_intelligence_runner.bat" /sc DAILY /st 06:00 /f

REM Weekly comprehensive analysis (Mondays at 8 AM)
schtasks /create /tn "OSINT_Weekly_Analysis" /tr "C:\Projects\OSINT - Foresight\scripts\scheduled_intelligence_runner.bat" /sc WEEKLY /d MON /st 08:00 /f

REM Hourly RSS check (every hour from 8 AM to 6 PM)
schtasks /create /tn "OSINT_Hourly_RSS" /tr "python C:\Projects\OSINT - Foresight\scripts\rss_intelligence_simple.py" /sc HOURLY /st 08:00 /et 18:00 /f

echo.
echo Scheduled tasks created:
echo - OSINT_Daily_Intelligence (Daily at 6 AM)
echo - OSINT_Weekly_Analysis (Mondays at 8 AM)
echo - OSINT_Hourly_RSS (Every hour 8 AM - 6 PM)

echo.
echo To view tasks: schtasks /query /tn OSINT*
echo To run now: schtasks /run /tn "OSINT_Daily_Intelligence"
echo To delete: schtasks /delete /tn "OSINT_Daily_Intelligence" /f

pause
