@echo off
REM USPTO and ESTAT Data Processing Batch Script
REM Runs the decompression and processing pipeline

echo ============================================
echo USPTO and ESTAT DATA PROCESSING
echo Started: %date% %time%
echo ============================================
echo.

REM Navigate to project directory
cd /d "C:\Projects\OSINT - Foresight"

REM Activate Python environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Run the processing script
echo Starting data processing...
echo.
python scripts\process_uspto_estat_data.py

REM Check if successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo Processing completed successfully
    echo Finished: %date% %time%
    echo ============================================
) else (
    echo.
    echo ============================================
    echo ERROR: Processing failed with error code %ERRORLEVEL%
    echo Finished: %date% %time%
    echo ============================================
)

echo.
echo Check logs in: logs\
echo Check progress in: data\processing_progress.json
echo.
pause
