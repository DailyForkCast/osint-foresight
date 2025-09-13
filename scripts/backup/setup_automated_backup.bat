@echo off
echo ========================================
echo OSINT Foresight Automated Backup Setup
echo ========================================
echo.

echo This will set up automated daily backups to F: drive
echo.

REM Import the scheduled task
echo Importing scheduled task...
schtasks /create /xml "scheduled_backup_task.xml" /tn "OSINT Foresight Backup"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Task created successfully!
    echo.
    echo Backup schedule:
    echo - Daily at 9:00 PM
    echo - On system logon (after 5 min delay)
    echo - Destination: F:\OSINT_Backups\project
    echo.
    echo To run backup manually anytime:
    echo   schtasks /run /tn "OSINT Foresight Backup"
    echo.
    echo To check task status:
    echo   schtasks /query /tn "OSINT Foresight Backup"
    echo.
    echo To disable/delete task:
    echo   schtasks /delete /tn "OSINT Foresight Backup"
) else (
    echo.
    echo Failed to create scheduled task!
    echo Please run as Administrator or create manually in Task Scheduler
)

echo.
pause