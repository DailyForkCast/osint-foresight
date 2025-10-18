@echo off
REM HIGH PRIORITY: New countries + Gateway countries
REM Generated: 2025-09-30T05:31:37.768844
REM Countries: 17

cd /d "C:\Projects\OSINT - Foresight"

echo Processing GB - Newly added - expanded coverage
python scripts/process_openalex_country.py --country GB --target CN --streaming
python scripts/process_usaspending_country.py --country GB --china-analysis
python scripts/process_cordis_country.py --country GB --china-collaborations

echo Processing NO - Newly added - expanded coverage
python scripts/process_openalex_country.py --country NO --target CN --streaming
python scripts/process_ted_country.py --country NO --years 2010-2025
python scripts/process_usaspending_country.py --country NO --china-analysis
python scripts/process_cordis_country.py --country NO --china-collaborations

echo Processing CH - Newly added - expanded coverage
python scripts/process_openalex_country.py --country CH --target CN --streaming
python scripts/process_ted_country.py --country CH --years 2010-2025
python scripts/process_usaspending_country.py --country CH --china-analysis
python scripts/process_cordis_country.py --country CH --china-collaborations

echo Processing IS - Newly added - expanded coverage
python scripts/process_openalex_country.py --country IS --target CN --streaming
python scripts/process_ted_country.py --country IS --years 2010-2025
python scripts/process_usaspending_country.py --country IS --china-analysis
python scripts/process_cordis_country.py --country IS --china-collaborations

echo Processing AL - Newly added - expanded coverage
python scripts/process_openalex_country.py --country AL --target CN --streaming
python scripts/process_usaspending_country.py --country AL --china-analysis

echo Processing BA - Newly added - expanded coverage
python scripts/process_openalex_country.py --country BA --target CN --streaming
python scripts/process_usaspending_country.py --country BA --china-analysis

echo Processing MK - Newly added - expanded coverage
python scripts/process_openalex_country.py --country MK --target CN --streaming
python scripts/process_usaspending_country.py --country MK --china-analysis

echo Processing ME - Newly added - expanded coverage
python scripts/process_openalex_country.py --country ME --target CN --streaming
python scripts/process_usaspending_country.py --country ME --china-analysis

echo Processing XK - Newly added - expanded coverage
python scripts/process_openalex_country.py --country XK --target CN --streaming
python scripts/process_usaspending_country.py --country XK --china-analysis

echo Processing AM - Newly added - expanded coverage
python scripts/process_openalex_country.py --country AM --target CN --streaming
python scripts/process_usaspending_country.py --country AM --china-analysis
python scripts/process_cordis_country.py --country AM --china-collaborations

echo Processing AZ - Newly added - expanded coverage
python scripts/process_openalex_country.py --country AZ --target CN --streaming
python scripts/process_usaspending_country.py --country AZ --china-analysis

echo Processing HU - Gateway country - high Chinese penetration
python scripts/process_openalex_country.py --country HU --target CN --streaming
python scripts/process_ted_country.py --country HU --years 2010-2025
python scripts/process_usaspending_country.py --country HU --china-analysis
python scripts/process_cordis_country.py --country HU --china-collaborations

echo Processing GR - Gateway country - high Chinese penetration
python scripts/process_openalex_country.py --country GR --target CN --streaming
python scripts/process_ted_country.py --country GR --years 2010-2025
python scripts/process_usaspending_country.py --country GR --china-analysis
python scripts/process_cordis_country.py --country GR --china-collaborations

echo Processing IT - Gateway country - high Chinese penetration
python scripts/process_openalex_country.py --country IT --target CN --streaming
python scripts/process_ted_country.py --country IT --years 2010-2025
python scripts/process_usaspending_country.py --country IT --china-analysis
python scripts/process_cordis_country.py --country IT --china-collaborations

echo Processing PL - Gateway country - high Chinese penetration
python scripts/process_openalex_country.py --country PL --target CN --streaming
python scripts/process_ted_country.py --country PL --years 2010-2025
python scripts/process_usaspending_country.py --country PL --china-analysis
python scripts/process_cordis_country.py --country PL --china-collaborations

echo Processing RS - Gateway country - high Chinese penetration
python scripts/process_openalex_country.py --country RS --target CN --streaming
python scripts/process_usaspending_country.py --country RS --china-analysis

echo Processing TR - Gateway country - high Chinese penetration
python scripts/process_openalex_country.py --country TR --target CN --streaming
python scripts/process_usaspending_country.py --country TR --china-analysis
python scripts/process_cordis_country.py --country TR --china-collaborations

echo Completed: 17 countries processed
pause
