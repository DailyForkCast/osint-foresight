@echo off
echo ============================================================
echo         AUTOMATED PostgreSQL 15 INSTALLATION
echo ============================================================
echo.
echo This will install PostgreSQL 15 using Windows Package Manager (winget)
echo.
echo Installation details:
echo   - Version: PostgreSQL 15.14
echo   - Default port: 5432
echo   - Default superuser: postgres
echo   - Installation path: C:\Program Files\PostgreSQL\15
echo.
echo ============================================================
echo.
set /p confirm="Proceed with installation? (Y/N): "

if /i "%confirm%"=="Y" (
    echo.
    echo Installing PostgreSQL 15...
    echo This may take several minutes...
    echo.

    REM Install PostgreSQL 15
    winget install PostgreSQL.PostgreSQL.15 --silent --accept-source-agreements --accept-package-agreements

    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ============================================================
        echo PostgreSQL 15 installed successfully!
        echo ============================================================
        echo.
        echo Next steps:
        echo 1. Set the postgres password (if prompted during installation)
        echo 2. Add PostgreSQL to your PATH:
        echo    - C:\Program Files\PostgreSQL\15\bin
        echo.
        echo 3. Initialize the database:
        echo    cd "C:\Projects\OSINT - Foresight\scripts"
        echo    python setup_postgresql_windows.py
        echo.
        echo 4. Run SQL setup scripts:
        echo    psql -U postgres -f postgres_scripts\01_init_database.sql
        echo    psql -U postgres -f postgres_scripts\02_china_analysis_views.sql
        echo.
    ) else (
        echo.
        echo Installation failed or was cancelled.
        echo Please try manual installation from: https://www.postgresql.org/download/windows/
    )
) else (
    echo.
    echo Installation cancelled.
)

pause
