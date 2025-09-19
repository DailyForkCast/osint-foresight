# TED Historical Data Download Status

**Started:** 2025-09-16
**Target:** F:/TED_Data/monthly/
**Period:** 2015-2024 (10 years)
**Status:** 🔄 DOWNLOADING IN BACKGROUND

---

## 📊 Download Overview

### What's Being Downloaded
- **10 years** of EU public procurement data
- **120 monthly packages** (12 months × 10 years)
- **Period:** January 2015 - December 2024
- **Format:** Compressed TAR.GZ archives
- **Content:** All EU tenders, awards, notices for 67 target countries

### Expected Volume
- **Per Year:** ~2-4 GB compressed / ~15-25 GB uncompressed
- **Total (10 years):** ~30-50 GB compressed / ~200-300 GB uncompressed
- **Available Space:** 7+ TB on F: drive

---

## 🎯 Download Progress by Year

### Already Downloaded (2024-2025)
✅ **2025** (Partial)
- 2025-08: Downloaded (299.5 MB)
- 2025-07: Downloaded (385.9 MB)
- 2025-06: Downloaded (367.4 MB)
- 2025-05: Downloaded (355.6 MB)
- 2025-04: Downloaded (325.3 MB)
- 2025-03: Downloaded (329.9 MB)
- 2025-02: Downloaded (327.2 MB)
- 2025-01: Downloaded (327.0 MB)

✅ **2024** (Partial)
- 2024-12: Downloaded (261.2 MB)
- 2024-11: Downloaded (248.0 MB)
- 2024-10: Downloaded (220.0 MB)
- **Total:** 3.24 GB for recent 11 months

### Currently Downloading (2015-2024)
🔄 **2024** (Jan-Sep) - In Progress
🔄 **2023** - Queued
🔄 **2022** - Queued
🔄 **2021** - Queued
🔄 **2020** - Queued
🔄 **2019** - Queued
🔄 **2018** - Queued
🔄 **2017** - Queued
🔄 **2016** - Queued
🔄 **2015** - Queued

---

## 💡 Key Insights from Historical Data

### Why 10 Years?
1. **Technology Evolution** - Track China's tech acquisition patterns
2. **Market Penetration** - See growth in Chinese bidders over time
3. **Strategic Shifts** - Identify when China targeted specific sectors
4. **Baseline Establishment** - Pre-Belt & Road vs Post-BRI patterns
5. **COVID Impact** - 2020-2021 disruption and recovery patterns

### Analysis Opportunities

#### Temporal Patterns
- Pre-2017: Baseline Chinese participation
- 2017-2019: Belt & Road Initiative expansion
- 2020-2021: COVID disruption period
- 2022-2024: Post-COVID strategic positioning

#### Technology Categories to Track
- 5G and telecommunications equipment
- Surveillance and security systems
- Critical infrastructure components
- Dual-use technologies
- Green energy systems
- Transportation infrastructure

---

## 🔧 Processing Pipeline

### Phase 1: Download (Current)
```bash
python src/pulls/ted_bulk_download_historical.py
```
- Downloads 2015-2024 monthly packages
- Skips already downloaded files
- ~2-3 minutes per package
- Total time: ~5-6 hours

### Phase 2: Extraction (Next)
```bash
python src/pulls/ted_extract_all.py
```
- Extract TAR.GZ archives
- Organize by year/month
- Parse XML structure

### Phase 3: Analysis
```python
# Parse for Chinese entities
python src/analysis/ted_china_scanner.py

# Generate risk reports
python src/analysis/ted_risk_assessment.py

# Cross-reference with conference data
python src/analysis/ted_conference_correlation.py
```

---

## 📈 Quick Stats Commands

### Check Download Progress
```python
from pathlib import Path
ted_path = Path("F:/TED_Data/monthly")
files = list(ted_path.rglob("*.tar.gz"))
print(f"Downloaded: {len(files)} packages")
print(f"Years covered: {sorted(set(f.parent.name for f in files))}")
```

### Monitor Active Download
```bash
# Check background process
python -c "import psutil; [print(p.info) for p in psutil.process_iter(['pid', 'name', 'cmdline']) if 'ted_bulk' in str(p.info['cmdline'])]"
```

### Calculate Total Size
```python
from pathlib import Path
ted_path = Path("F:/TED_Data/monthly")
total_gb = sum(f.stat().st_size for f in ted_path.rglob("*.tar.gz")) / (1024**3)
print(f"Total downloaded: {total_gb:.2f} GB")
```

---

## 🚨 China Risk Indicators to Extract

### Priority Search Terms
1. **Companies:** Huawei, ZTE, Hikvision, Dahua, DJI, Alibaba Cloud
2. **Technologies:** 5G, AI, surveillance, quantum, semiconductor
3. **Sectors:** Telecom, energy, transport, defense, healthcare
4. **Patterns:** Unusually low bids, consortium participation, subcontracting

### Risk Scoring Framework
- **Critical (Score 9-10):** Military/defense contracts, critical infrastructure
- **High (Score 7-8):** Telecommunications, energy grid, transportation
- **Medium (Score 5-6):** Healthcare systems, education technology
- **Low (Score 1-4):** Consumer goods, non-sensitive services

---

## 📝 Notes

- Download runs at ~500 KB/s (respectful to TED servers)
- Script can be safely interrupted and resumed
- Already downloaded files are automatically skipped
- Each package contains all EU procurement data for that month
- XML format allows detailed parsing and analysis
- No authentication or payment required (EU Open Data)

---

## 🔗 Resources

- **Download Script:** `src/pulls/ted_bulk_download_historical.py`
- **Base Downloader:** `src/pulls/ted_bulk_download.py`
- **TED Website:** https://ted.europa.eu
- **Data Format Docs:** https://docs.ted.europa.eu/home/data-formats.html

---

*This download provides comprehensive historical EU procurement data for deep OSINT analysis of China's technology acquisition and market penetration strategies across all 67 target countries from 2015-2024.*
