@echo off
REM Schedule regular fabrication checks
REM Can be added to Windows Task Scheduler to run every 12 hours

cd /d "C:\Projects\OSINT - Foresight"
python scripts\schedule_fabrication_checks.py

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo Fabrication check found violations!
    echo Review report at: docs\reports\FABRICATION_CHECK_REPORT.md
    REM Optionally send notification or email here
    exit /b 1
) else (
    echo Fabrication check passed.
    exit /b 0
)
