@echo off
REM Quick manual run of OSINT platform - no admin needed

echo ============================================================
echo OSINT CHINA RISK INTELLIGENCE - MANUAL RUN
echo ============================================================
echo.

cd /d "C:\Projects\OSINT - Foresight"

echo Starting intelligence collection...
echo.

echo [1/4] Patent Intelligence...
python scripts\collectors\google_patents_chinese_simple.py
echo.

echo [2/4] RSS Intelligence...
python scripts\rss_intelligence_simple.py
echo.

echo [3/4] Network Analysis...
python scripts\networkx_entity_graph.py
echo.

echo [4/4] Executive Dashboard...
python scripts\consolidated_intelligence_dashboard.py
echo.

echo ============================================================
echo INTELLIGENCE COLLECTION COMPLETE!
echo ============================================================
echo.
echo Reports saved in: analysis\
echo.
echo To schedule automatic runs:
echo   Right-click scripts\setup_scheduled_tasks.bat
echo   Select "Run as administrator"
echo.

pause
