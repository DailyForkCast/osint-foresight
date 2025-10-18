@echo off
REM Scheduled Intelligence Collection Runner
REM Runs all intelligence systems in sequence
REM Schedule this with Windows Task Scheduler

echo ========================================
echo OSINT Intelligence Collection Starting
echo Time: %date% %time%
echo ========================================

cd /d "C:\Projects\OSINT - Foresight"

echo.
echo [1/4] Running Patent Intelligence...
python scripts\collectors\google_patents_chinese_simple.py

echo.
echo [2/4] Running RSS Intelligence...
python scripts\rss_intelligence_simple.py

echo.
echo [3/4] Running Network Analysis...
python scripts\networkx_entity_graph.py

echo.
echo [4/4] Running Executive Dashboard...
python scripts\consolidated_intelligence_dashboard.py

echo.
echo ========================================
echo Intelligence Collection Complete
echo Time: %date% %time%
echo ========================================

REM Keep window open for 5 seconds to see results
timeout /t 5 /nobreak > nul
