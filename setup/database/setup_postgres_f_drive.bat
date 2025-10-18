@echo off
echo ======================================================================
echo SETTING UP POSTGRESQL DATA DIRECTORY ON F: DRIVE
echo ======================================================================

REM Create data directory on F: drive
echo Creating PostgreSQL data directory on F: drive...
mkdir "F:\PostgreSQL_Data\15"

REM Initialize the database cluster on F: drive
echo.
echo Initializing database cluster on F: drive...
echo This may take a minute...
"C:\Program Files\PostgreSQL\15\bin\initdb" -D "F:\PostgreSQL_Data\15" -U postgres --encoding=UTF8

echo.
echo ======================================================================
echo.
echo Data directory created at: F:\PostgreSQL_Data\15
echo.
echo NEXT STEPS:
echo 1. Stop default PostgreSQL service
echo 2. Reconfigure to use F: drive
echo 3. Restart PostgreSQL
echo ======================================================================
pause
