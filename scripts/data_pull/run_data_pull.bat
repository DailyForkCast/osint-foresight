@echo off
echo ========================================
echo OSINT Foresight Data Pull to External Drive
echo ========================================
echo.

cd /d "C:\Projects\OSINT - Foresight"

echo Checking external drive space...
echo.

REM Check if F: drive is available
if not exist F:\ (
    echo ERROR: External drive F: not found!
    echo Please connect your external drive and try again.
    pause
    exit /b 1
)

echo External drive F: is connected
echo.

REM Create data directories if needed
if not exist "F:\OSINT_Data" mkdir "F:\OSINT_Data"
if not exist "F:\OSINT_Data\logs" mkdir "F:\OSINT_Data\logs"
if not exist "F:\OSINT_Data\manifests" mkdir "F:\OSINT_Data\manifests"
if not exist "F:\OSINT_Data\reports" mkdir "F:\OSINT_Data\reports"

echo Starting data pull process...
echo.

REM Run the master data pull script
python scripts\data_pull\master_data_pull.py --mode test

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Data pull completed successfully!
    echo Check F:\OSINT_Data\reports for the pull report
) else (
    echo.
    echo Data pull failed with error code %ERRORLEVEL%
    echo Check F:\OSINT_Data\logs for details
)

echo.
pause
