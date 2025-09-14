@echo off
REM Setup automated data pulls using Windows Task Scheduler
REM Run this as Administrator

echo Setting up OSINT Foresight Automated Data Pulls...
echo ================================================

REM Daily pulls (2 AM)
schtasks /create /tn "OSINT_Daily_Pulls" /tr "python C:\Projects\OSINT - Foresight\src\pulls\master_pull_orchestrator.py --mode once --priority high --base-dir F:\OSINT_Data" /sc daily /st 02:00 /f

REM Weekly pulls (Sunday 3 AM)
schtasks /create /tn "OSINT_Weekly_Pulls" /tr "python C:\Projects\OSINT - Foresight\src\pulls\master_pull_orchestrator.py --mode once --source crossref --base-dir F:\OSINT_Data" /sc weekly /d SUN /st 03:00 /f

REM Monthly pulls (1st of month, 4 AM)
schtasks /create /tn "OSINT_Monthly_Pulls" /tr "python C:\Projects\OSINT - Foresight\src\pulls\master_pull_orchestrator.py --mode once --base-dir F:\OSINT_Data" /sc monthly /d 1 /st 04:00 /f

REM Quarterly Common Crawl (Every 3 months on 15th, 1 AM)
schtasks /create /tn "OSINT_Quarterly_CommonCrawl" /tr "python C:\Projects\OSINT - Foresight\src\pulls\master_pull_orchestrator.py --mode once --source commoncrawl --base-dir F:\OSINT_Data" /sc monthly /mo 3 /d 15 /st 01:00 /f

REM Status report generation (Daily at 6 AM)
schtasks /create /tn "OSINT_Status_Report" /tr "python C:\Projects\OSINT - Foresight\src\pulls\master_pull_orchestrator.py --mode status --base-dir F:\OSINT_Data" /sc daily /st 06:00 /f

echo.
echo Scheduled tasks created successfully!
echo.
echo View tasks with: schtasks /query /tn OSINT*
echo.
pause
