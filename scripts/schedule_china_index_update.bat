@echo off
REM Batch file to update China Analysis Index
REM Runs every 12 hours via Windows Task Scheduler

cd /d "C:\Projects\OSINT - Foresight"
echo [%date% %time%] Starting China Analysis Index update... >> scripts\china_index_update.log
python scripts\update_china_index.py >> scripts\china_index_update.log 2>&1
echo [%date% %time%] Update complete. >> scripts\china_index_update.log
echo. >> scripts\china_index_update.log
