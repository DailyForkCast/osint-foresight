@echo off
cls
echo ============================================================
echo          CHINA PATTERN ANALYSIS SUITE - MAIN MENU
echo ============================================================
echo.
echo Current Status:
echo   - Data Located: 956 GB
echo   - Data Analyzed: ~10 GB
echo   - China Patterns Found: 1,894 (US: 1,799, EU: 95)
echo   - Critical Sectors: 52 EU contracts flagged
echo.
echo ============================================================
echo.
echo Select an option:
echo.
echo [1] Install PostgreSQL (Required for full analysis)
echo [2] Run Overnight Decompression (64 GB, 8-12 hours)
echo [3] Analyze New China Patterns (Quick scan)
echo [4] Generate Status Report
echo [5] Schedule Daily Monitoring
echo [6] View Latest Findings
echo [7] Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo Launching PostgreSQL installer...
    call install_postgresql.bat
    pause
    goto :menu
)

if "%choice%"=="2" (
    echo.
    echo Starting overnight decompression...
    echo This will process 5 large files (64 GB compressed)
    echo Expected time: 8-12 hours
    echo.
    set /p confirm="Are you sure? (Y/N): "
    if /i "%confirm%"=="Y" (
        start run_overnight.bat
        echo Decompression started in new window.
    )
    pause
    goto :menu
)

if "%choice%"=="3" (
    echo.
    echo Running China pattern analysis...
    cd scripts
    python analyze_china_patterns.py
    python analyze_ted_china_patterns.py
    cd ..
    pause
    goto :menu
)

if "%choice%"=="4" (
    echo.
    echo Generating status report...
    type CHINA_COMPREHENSIVE_FINAL_REPORT.md
    echo.
    echo ============================================================
    echo Report location: CHINA_COMPREHENSIVE_FINAL_REPORT.md
    pause
    goto :menu
)

if "%choice%"=="5" (
    echo.
    echo Setting up daily monitoring...
    call schedule_china_monitoring.bat
    pause
    goto :menu
)

if "%choice%"=="6" (
    echo.
    echo Latest China Pattern Findings:
    echo ============================================================
    echo.
    echo US Federal Contracts (USASpending):
    echo   - Total patterns: 1,799
    echo   - Contracts analyzed: 10
    echo   - Flagged as suspicious: 5
    echo   - Primary finding: Chinese-manufactured office supplies
    echo.
    echo EU Public Tenders (TED):
    echo   - Files analyzed: 150
    echo   - China presence: 95 files (63.3%)
    echo   - Critical sectors: 52 contracts
    echo   - Chinese companies: 19 identified
    echo.
    echo Key Risk Areas:
    echo   - Office supplies from China (GSA, DoD)
    echo   - Critical infrastructure (EU)
    echo   - Telecom equipment (Huawei, ZTE)
    echo   - Surveillance systems
    echo.
    pause
    goto :menu
)

if "%choice%"=="7" (
    echo.
    echo Exiting China Analysis Suite...
    exit /b
)

:menu
cls
START_CHINA_ANALYSIS_SUITE.bat
