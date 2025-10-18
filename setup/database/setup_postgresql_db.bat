@echo off
echo ======================================================================
echo POSTGRESQL DATABASE SETUP FOR USASPENDING
echo ======================================================================

set PGBIN="C:\Program Files\PostgreSQL\15\bin"
set PGUSER=postgres

echo.
echo Step 1: Creating usaspending database...
%PGBIN%\psql -U %PGUSER% -c "CREATE DATABASE usaspending;"

echo.
echo Step 2: Applying performance configuration...
%PGBIN%\psql -U %PGUSER% -d usaspending -f postgres_scripts\04_configure_for_large_import.sql

echo.
echo Step 3: Creating required schemas...
echo Creating schemas for USASpending tables...
%PGBIN%\psql -U %PGUSER% -d usaspending -c "CREATE SCHEMA IF NOT EXISTS raw_data;"
%PGBIN%\psql -U %PGUSER% -d usaspending -c "CREATE SCHEMA IF NOT EXISTS china_analysis;"

echo.
echo Step 4: Checking configuration...
%PGBIN%\psql -U %PGUSER% -d usaspending -c "SELECT name, setting FROM pg_settings WHERE name IN ('shared_buffers', 'work_mem', 'maintenance_work_mem');"

echo.
echo ======================================================================
echo DATABASE SETUP COMPLETE
echo.
echo Database: usaspending
echo Schemas: raw_data, china_analysis
echo.
echo Ready for data import once 5801.dat decompression completes!
echo ======================================================================
pause
