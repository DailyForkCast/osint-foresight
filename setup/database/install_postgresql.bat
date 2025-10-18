@echo off
echo ============================================
echo PostgreSQL Installation Helper for Windows
echo ============================================
echo.

echo This script will help you install PostgreSQL for USASpending data analysis.
echo.

echo OPTION 1: Download PostgreSQL Installer
echo ----------------------------------------
echo 1. Visit: https://www.postgresql.org/download/windows/
echo 2. Download PostgreSQL 15 installer
echo 3. Run installer with these settings:
echo    - Port: 5432
echo    - Password: postgres (or your choice)
echo    - Data directory: C:\PostgreSQL\data
echo.

echo OPTION 2: Use Command Line (if you have chocolatey)
echo -----------------------------------------------------
echo Run: choco install postgresql15
echo.

echo OPTION 3: Use Command Line (if you have winget)
echo ------------------------------------------------
echo Run: winget install PostgreSQL.PostgreSQL
echo.

echo After installation, run: setup_postgresql_windows.py again
echo.
pause
