@echo off
REM Create scheduled task for EPO Patent Collection

schtasks /create /tn "EPO_Patent_Collection" /tr "C:\Projects\OSINT - Foresight\scripts\run_epo_collection.bat" /sc HOURLY /mo 2 /f

echo.
echo Scheduled task created: EPO_Patent_Collection
echo Will run every 2 hours
echo.
echo To view the task: schtasks /query /tn "EPO_Patent_Collection"
echo To run manually: schtasks /run /tn "EPO_Patent_Collection"
echo To delete: schtasks /delete /tn "EPO_Patent_Collection" /f
