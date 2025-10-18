@echo off
REM Weekly Documentation Audit Runner
REM Runs documentation validation and archival automatically
REM Scheduled via Windows Task Scheduler

echo ============================================================
echo OSINT Foresight - Weekly Documentation Audit
echo %date% %time%
echo ============================================================
echo.

cd "C:\Projects\OSINT - Foresight"

REM Run documentation validation
echo [1/3] Running documentation validation...
python validate_documentation.py > logs\doc_validation_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Documentation validation found issues
    echo Check logs\doc_validation_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
) else (
    echo PASS: Documentation validation successful
)
echo.

REM Run archival in dry-run mode to preview
echo [2/3] Running archival preview...
python archive_old_docs.py --dry-run > logs\archive_preview_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1
echo Preview saved to logs\archive_preview_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
echo.

REM Generate database audit report
echo [3/3] Running database audit...
python audit_database.py > logs\database_audit_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Database audit encountered issues
) else (
    echo PASS: Database audit complete
)
echo.

echo ============================================================
echo Weekly audit complete
echo Logs saved to logs\ directory
echo ============================================================
echo.

pause
