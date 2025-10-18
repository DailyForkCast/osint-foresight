@echo off
REM EPO Patent Collection Batch Script
REM Runs every 2-3 hours to collect patents

echo ========================================
echo EPO Patent Collection Starting
echo Time: %date% %time%
echo ========================================

cd /d "C:\Projects\OSINT - Foresight"

REM Run the automated scheduler once
python scripts\epo_automated_scheduler.py --once

echo.
echo Collection cycle complete
echo Next run scheduled in 2-3 hours
echo ========================================
