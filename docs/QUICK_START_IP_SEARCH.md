# Quick Start Guide: IP Data Collection & Analysis

## 🚀 3-Step Process

### Step 1: Manual Search & Export
1. Open `docs/MANUAL_SEARCH_PROCESS.md` for detailed instructions
2. Search target companies on:
   - EUIPO: https://euipo.europa.eu/eSearch/
   - Espacenet: https://worldwide.espacenet.com/
3. Export results as CSV files
4. Save files in:
   - Trademarks: `data/collected/trademarks/[source]/`
   - Patents: `data/collected/patents/[source]/`

### Step 2: Aggregate Data
```python
from src.aggregators.csv_aggregator import IPDataAggregator

aggregator = IPDataAggregator()
aggregator.run_full_aggregation()
```

### Step 3: Analyze Results
```python
from src.analysis.ip_analyzer import IPAnalyzer

analyzer = IPAnalyzer()
report = analyzer.create_summary_report()
```

---

## 📁 Directory Structure

```
data/collected/
├── trademarks/
│   ├── euipo/         # EUIPO exports
│   ├── wipo/          # WIPO exports
│   └── uibm/          # Italian office exports
├── patents/
│   ├── epo/           # EPO/Espacenet exports
│   ├── google/        # Google Patents exports
│   └── wipo/          # WIPO patents
└── aggregated/
    ├── trademarks_aggregated_[timestamp].csv
    ├── patents_aggregated_[timestamp].csv
    └── analysis_outputs/
        └── ip_analysis_report_[timestamp].json
```

---

## 🎯 Target Italian Companies

**Defense & Aerospace**
- Leonardo S.p.A.
- Fincantieri
- Thales Alenia Space Italia
- Telespazio

**Technology**
- STMicroelectronics
- Datalogic
- Engineering Ingegneria Informatica
- Reply

**Industrial**
- Ansaldo Energia
- Prysmian Group
- Danieli

---

## 📊 Key Analysis Outputs

1. **Filing Trends**: Historical patterns and growth rates
2. **Technology Areas**: Classification analysis (Nice/IPC)
3. **Collaboration Patterns**: Joint ownership detection
4. **Security Insights**: Critical technology identification
5. **Risk Assessment**: Technology transfer implications

---

## 💡 Tips

- Export maximum records (typically 500 per search)
- Use consistent file naming: `[SOURCE]_[COMPANY]_[TYPE]_[DATE].csv`
- Check UTF-8 encoding for Italian characters
- Run aggregation after each batch of exports
- Review JSON reports for security insights

---

## ⚠️ Compliance

✅ All methods are ToS compliant
✅ Uses official export features
✅ No web scraping involved
✅ Respects rate limits
✅ Suitable for commercial research

---

**Last Updated:** 2025-09-16
