@echo off
echo PostgreSQL Database Restore Instructions
echo =========================================
echo.
echo 1. Install PostgreSQL 13+ if not installed:
echo    https://www.postgresql.org/download/windows/
echo.
echo 2. Create database:
echo    createdb -U postgres usaspending_db
echo.
echo 3. Restore from dump (run from USAspending folder):
echo    pg_restore -U postgres -d usaspending_db -v toc.dat
echo.
echo 4. For partial restore (specific tables):
echo    pg_restore -U postgres -d usaspending_db -t vendor_table -v toc.dat
echo.
echo Note: Full restore will take 2-4 hours for 9.4M records
echo.
pause
