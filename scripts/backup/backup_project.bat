@echo off
echo ========================================
echo OSINT Foresight Project Backup
echo ========================================
echo.

cd /d "C:\Projects\OSINT - Foresight"

echo Starting backup process...
python backup_manager.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Backup completed successfully!
) else (
    echo.
    echo Backup failed with error code %ERRORLEVEL%
)

echo.
pause
