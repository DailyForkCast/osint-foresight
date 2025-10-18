@echo off
cls
echo ============================================================
echo           OVERNIGHT DECOMPRESSION LAUNCHER
echo ============================================================
echo.
echo This will decompress 5 large files (64 GB compressed)
echo Estimated uncompressed size: ~300 GB
echo Estimated time: 8-12 hours
echo.
echo Files to process:
echo   - 5801.dat.gz (14.3 GB)
echo   - 5836.dat.gz (13.1 GB)
echo   - 5847.dat.gz (15.6 GB)
echo   - 5848.dat.gz (16.5 GB)
echo   - 5862.dat.gz (4.7 GB)
echo.
echo Progress will be logged to: overnight_progress.log
echo.
echo ============================================================
pause

echo.
echo Starting decompression...
python scripts\overnight_decompress_enhanced.py

echo.
echo ============================================================
echo DECOMPRESSION COMPLETE
echo Check overnight_progress.log for results
echo ============================================================
pause
