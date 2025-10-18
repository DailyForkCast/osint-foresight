@echo off
REM CORDIS: Expanded country processing
REM Generated: 2025-09-30T05:31:38.589065
REM Countries: 42

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

echo Processing DE - Major economy - high R&D volume
python scripts/process_openalex_country.py --country DE --target CN --streaming
python scripts/process_ted_country.py --country DE --years 2010-2025
python scripts/process_usaspending_country.py --country DE --china-analysis
python scripts/process_cordis_country.py --country DE --china-collaborations

echo Processing FR - Major economy - high R&D volume
python scripts/process_openalex_country.py --country FR --target CN --streaming
python scripts/process_ted_country.py --country FR --years 2010-2025
python scripts/process_usaspending_country.py --country FR --china-analysis
python scripts/process_cordis_country.py --country FR --china-collaborations

echo Processing ES - Major economy - high R&D volume
python scripts/process_openalex_country.py --country ES --target CN --streaming
python scripts/process_ted_country.py --country ES --years 2010-2025
python scripts/process_usaspending_country.py --country ES --china-analysis
python scripts/process_cordis_country.py --country ES --china-collaborations

echo Processing NL - Major economy - high R&D volume
python scripts/process_openalex_country.py --country NL --target CN --streaming
python scripts/process_ted_country.py --country NL --years 2010-2025
python scripts/process_usaspending_country.py --country NL --china-analysis
python scripts/process_cordis_country.py --country NL --china-collaborations

echo Processing BE - Major economy - high R&D volume
python scripts/process_openalex_country.py --country BE --target CN --streaming
python scripts/process_ted_country.py --country BE --years 2010-2025
python scripts/process_usaspending_country.py --country BE --china-analysis
python scripts/process_cordis_country.py --country BE --china-collaborations

echo Processing SE - Major economy - high R&D volume
python scripts/process_openalex_country.py --country SE --target CN --streaming
python scripts/process_ted_country.py --country SE --years 2010-2025
python scripts/process_usaspending_country.py --country SE --china-analysis
python scripts/process_cordis_country.py --country SE --china-collaborations

echo Processing AT - Comprehensive coverage
python scripts/process_openalex_country.py --country AT --target CN --streaming
python scripts/process_ted_country.py --country AT --years 2010-2025
python scripts/process_usaspending_country.py --country AT --china-analysis
python scripts/process_cordis_country.py --country AT --china-collaborations

echo Processing BG - Comprehensive coverage
python scripts/process_openalex_country.py --country BG --target CN --streaming
python scripts/process_ted_country.py --country BG --years 2010-2025
python scripts/process_usaspending_country.py --country BG --china-analysis
python scripts/process_cordis_country.py --country BG --china-collaborations

echo Processing CY - Comprehensive coverage
python scripts/process_openalex_country.py --country CY --target CN --streaming
python scripts/process_ted_country.py --country CY --years 2010-2025
python scripts/process_usaspending_country.py --country CY --china-analysis
python scripts/process_cordis_country.py --country CY --china-collaborations

echo Processing CZ - Comprehensive coverage
python scripts/process_openalex_country.py --country CZ --target CN --streaming
python scripts/process_ted_country.py --country CZ --years 2010-2025
python scripts/process_usaspending_country.py --country CZ --china-analysis
python scripts/process_cordis_country.py --country CZ --china-collaborations

echo Processing DK - Comprehensive coverage
python scripts/process_openalex_country.py --country DK --target CN --streaming
python scripts/process_ted_country.py --country DK --years 2010-2025
python scripts/process_usaspending_country.py --country DK --china-analysis
python scripts/process_cordis_country.py --country DK --china-collaborations

echo Processing EE - Comprehensive coverage
python scripts/process_openalex_country.py --country EE --target CN --streaming
python scripts/process_ted_country.py --country EE --years 2010-2025
python scripts/process_usaspending_country.py --country EE --china-analysis
python scripts/process_cordis_country.py --country EE --china-collaborations

echo Processing FI - Comprehensive coverage
python scripts/process_openalex_country.py --country FI --target CN --streaming
python scripts/process_ted_country.py --country FI --years 2010-2025
python scripts/process_usaspending_country.py --country FI --china-analysis
python scripts/process_cordis_country.py --country FI --china-collaborations

echo Processing IE - Comprehensive coverage
python scripts/process_openalex_country.py --country IE --target CN --streaming
python scripts/process_ted_country.py --country IE --years 2010-2025
python scripts/process_usaspending_country.py --country IE --china-analysis
python scripts/process_cordis_country.py --country IE --china-collaborations

echo Processing LT - Comprehensive coverage
python scripts/process_openalex_country.py --country LT --target CN --streaming
python scripts/process_ted_country.py --country LT --years 2010-2025
python scripts/process_usaspending_country.py --country LT --china-analysis
python scripts/process_cordis_country.py --country LT --china-collaborations

echo Processing LV - Comprehensive coverage
python scripts/process_openalex_country.py --country LV --target CN --streaming
python scripts/process_ted_country.py --country LV --years 2010-2025
python scripts/process_usaspending_country.py --country LV --china-analysis
python scripts/process_cordis_country.py --country LV --china-collaborations

echo Processing MT - Comprehensive coverage
python scripts/process_openalex_country.py --country MT --target CN --streaming
python scripts/process_ted_country.py --country MT --years 2010-2025
python scripts/process_usaspending_country.py --country MT --china-analysis
python scripts/process_cordis_country.py --country MT --china-collaborations

echo Processing PT - Comprehensive coverage
python scripts/process_openalex_country.py --country PT --target CN --streaming
python scripts/process_ted_country.py --country PT --years 2010-2025
python scripts/process_usaspending_country.py --country PT --china-analysis
python scripts/process_cordis_country.py --country PT --china-collaborations

echo Processing RO - Comprehensive coverage
python scripts/process_openalex_country.py --country RO --target CN --streaming
python scripts/process_ted_country.py --country RO --years 2010-2025
python scripts/process_usaspending_country.py --country RO --china-analysis
python scripts/process_cordis_country.py --country RO --china-collaborations

echo Processing SI - Comprehensive coverage
python scripts/process_openalex_country.py --country SI --target CN --streaming
python scripts/process_ted_country.py --country SI --years 2010-2025
python scripts/process_usaspending_country.py --country SI --china-analysis
python scripts/process_cordis_country.py --country SI --china-collaborations

echo Processing SK - Comprehensive coverage
python scripts/process_openalex_country.py --country SK --target CN --streaming
python scripts/process_ted_country.py --country SK --years 2010-2025
python scripts/process_usaspending_country.py --country SK --china-analysis
python scripts/process_cordis_country.py --country SK --china-collaborations

echo Processing UA - Comprehensive coverage
python scripts/process_openalex_country.py --country UA --target CN --streaming
python scripts/process_usaspending_country.py --country UA --china-analysis
python scripts/process_cordis_country.py --country UA --china-collaborations

echo Processing GE - Comprehensive coverage
python scripts/process_openalex_country.py --country GE --target CN --streaming
python scripts/process_usaspending_country.py --country GE --china-analysis
python scripts/process_cordis_country.py --country GE --china-collaborations

echo Processing FO - Comprehensive coverage
python scripts/process_openalex_country.py --country FO --target CN --streaming
python scripts/process_usaspending_country.py --country FO --china-analysis

echo Processing GL - Comprehensive coverage
python scripts/process_openalex_country.py --country GL --target CN --streaming
python scripts/process_usaspending_country.py --country GL --china-analysis

echo Completed: 42 countries processed
pause
