@echo off
echo Starting overnight decompression...
echo This will take 8-12 hours
echo.
python overnight_decompress.py > decompression_log.txt 2>&1
echo.
echo Decompression complete! Check decompression_log.txt for details.
pause
