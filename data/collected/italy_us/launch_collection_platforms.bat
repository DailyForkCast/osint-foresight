@echo off
echo ==========================================
echo Italy-US Intelligence Collection Launcher
echo ==========================================
echo.

echo Opening Priority 1 Platforms...

start "" "https://www.fpds.gov/ezsearch/fpdsportal"
timeout /t 2 /nobreak >nul

start "" "https://www.sec.gov/edgar/browse/?CIK=1698027"
timeout /t 2 /nobreak >nul

start "" "https://www.scopus.com/search/form.uri"
timeout /t 2 /nobreak >nul

echo.
echo Priority 1 platforms opened.
echo.

echo Press any key to open Priority 2 platforms...
pause >nul

start "" "https://sam.gov/content/entity-information"
timeout /t 2 /nobreak >nul

start "" "https://patents.google.com"
timeout /t 2 /nobreak >nul

start "" "https://www.linkedin.com/search/"
timeout /t 2 /nobreak >nul

echo.
echo All platforms opened. Begin collection.
echo.

echo Collection Tips:
echo - Start with FPDS Leonardo DRS search
echo - Export all results to CSV
echo - Save to: C:\Projects\OSINT - Foresight\data\collected\italy_us
echo.

pause
