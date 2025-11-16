# Quick Start Guide - Expanded Geographic Coverage

**Last Updated:** September 30, 2025
**Status:** Production Ready

---

## 🚀 Get Started in 3 Steps

### Step 1: Run High-Priority Processing (2-4 hours)
```bash
cd "C:/Projects/OSINT - Foresight"
.\scripts\process_expanded_countries_high_priority.bat
```
**What it does:**
- Processes 17 high-priority countries (11 new + 6 gateway countries)
- Extracts China-related intelligence from all 4 data sources
- Generates country-specific reports with confidence scoring

**Countries processed:**
- 🆕 UK, Norway, Switzerland, Iceland
- 🆕 Albania, Bosnia, North Macedonia, Montenegro, Kosovo
- 🆕 Armenia, Azerbaijan
- 🔥 Hungary, Greece, Italy, Poland, Serbia, Turkey

### Step 2: Start Automated Monitoring (runs continuously)
```bash
python scripts/automated_expanded_monitor.py --continuous --interval 60
```
**What it does:**
- Scans all priority countries every 60 minutes
- Monitors data sources for new records
- Generates alerts for significant events
- Creates daily summary reports (6 AM)

**Press Ctrl+C to stop**

### Step 3: View Results
```bash
# Daily report (JSON)
type analysis\monitoring_reports\daily_report_20250930.json

# Processing status
type analysis\country_expansion_status.json

# Scan summaries
dir analysis\monitoring_scans\
```

---

## 📊 What You'll Get

### Immediate Results (Step 1):
- **11 new countries** analyzed for China involvement
- **Multi-source intelligence** (OpenAlex + TED + USAspending + CORDIS)
- **Confidence-scored findings** (0.0-1.0 scale)
- **Multilingual detection** (11 languages)

### Continuous Intelligence (Step 2):
- **Real-time alerts** for new China activities
- **Daily summary reports** at 6 AM
- **Data source health monitoring**
- **Trend tracking over time**

### Expected Findings:
- UK: Huawei telecoms, academic collaborations
- Norway: Arctic projects, energy sector
- Switzerland: Financial ties, pharma collaborations
- Balkans: BRI infrastructure projects
- Caucasus: Energy corridors, strategic partnerships

---

## 📁 Key Files & Locations

### Configuration
- `config/expanded_countries.json` - 81 country catalog

### Scripts
- `scripts/process_expanded_countries_high_priority.bat` - High-priority batch (17 countries)
- `scripts/process_expanded_countries_all.bat` - All countries (42 countries)
- `scripts/automated_expanded_monitor.py` - Monitoring system

### Reports & Data
- `analysis/country_expansion_status.json` - Processing queue status
- `analysis/monitoring_reports/` - Daily monitoring reports
- `analysis/monitoring_scans/` - Individual scan summaries
- `database/expanded_monitoring.db` - Event/alert database

### Documentation
- `docs/EXPANDED_COVERAGE_SUMMARY.md` - Complete implementation guide
- `IMPLEMENTATION_SUMMARY_20250930.md` - Technical summary
- `QUICKSTART_EXPANDED_COVERAGE.md` - This guide

---

## 🎯 Common Tasks

### View Monitoring Status
```bash
python scripts/automated_expanded_monitor.py
```
Runs single scan and displays results.

### Generate Daily Report
```bash
python scripts/automated_expanded_monitor.py --daily-report
```
Creates daily summary (anytime, not just 6 AM).

### Process All Countries (6-8 hours)
```bash
.\scripts\process_expanded_countries_all.bat
```
Comprehensive processing of all 42 countries.

### Process Specific Data Source
```bash
# OpenAlex only
.\scripts\process_openalex_expanded.bat

# TED only (EU/EEA countries)
.\scripts\process_ted_expanded.bat

# USAspending only
.\scripts\process_usaspending_expanded.bat

# CORDIS only
.\scripts\process_cordis_expanded.bat
```

### Query Monitoring Database
```bash
sqlite3 database/expanded_monitoring.db
```
```sql
-- Recent events
SELECT * FROM monitoring_events ORDER BY timestamp DESC LIMIT 10;

-- Country status
SELECT * FROM countries_status ORDER BY total_events DESC;

-- Unacknowledged alerts
SELECT * FROM alerts WHERE acknowledged = 0;
```

---

## 🔍 Understanding the Output

### Confidence Scores
- **0.9-1.0:** Very high confidence (multiple sources, known entities)
- **0.7-0.9:** High confidence (strong patterns, good context)
- **0.5-0.7:** Medium confidence (decent evidence, needs review)
- **0.3-0.5:** Low confidence (weak signals, manual review required)
- **<0.3:** Very low confidence (likely false positive)

### Alert Severity
- **critical:** Immediate attention required
- **high:** Review within 24 hours
- **medium:** Review within week
- **info:** For awareness only

### Data Source Status
- **active:** New data found in last 24h
- **idle:** No new data, all systems working
- **unavailable:** Data source not accessible
- **error:** Processing error occurred

---

## ⚠️ Troubleshooting

### "Data source not accessible"
**Problem:** F:/ drive paths not found
**Solution:** Verify data sources exist:
```bash
ls F:/OSINT_Backups/openalex/data/
ls F:/TED_Data/monthly/
ls F:/OSINT_DATA/USAspending/
```

### "No country config found"
**Problem:** Config file missing or corrupt
**Solution:** Check config file:
```bash
type config\expanded_countries.json
```

### "Database locked"
**Problem:** Multiple processes accessing database
**Solution:** Stop monitoring system, then restart

### "Processing script hangs"
**Problem:** Large dataset processing
**Solution:** This is normal - processing can take hours. Check logs:
```bash
type logs\automated_monitoring.log
```

---

## 📈 Next Steps After Initial Processing

### 1. Review High-Priority Findings
- Check `analysis/monitoring_reports/` for daily summaries
- Review country-specific reports for each of 11 new countries
- Identify high-confidence matches for deeper analysis

### 2. Cross-Reference Data Sources
- Compare OpenAlex (academic) with USAspending (contracts)
- Look for entities appearing in multiple sources
- Track temporal patterns (research → contracts → deployment)

### 3. Generate Intelligence Reports
- Use findings to populate master intelligence reports
- Cross-validate with existing EU27 findings
- Identify new patterns visible only with expanded coverage

### 4. Set Up Continuous Monitoring
- Keep monitoring system running 24/7
- Review daily reports each morning
- Acknowledge/resolve alerts as they appear

---

## 🎓 Tips for Best Results

### Priority Focus
Start with Tier 1+2 countries (high-priority batch). These have highest likelihood of significant findings.

### Patience with Processing
Initial processing takes hours. The system is scanning 660GB+ of data across multiple sources.

### Monitor Logs
Watch `logs/automated_monitoring.log` to see progress in real-time.

### Check Database
Query the database periodically to see events accumulating.

### Daily Routine
- **Morning:** Review daily report from 6 AM run
- **Midday:** Check alerts, acknowledge/resolve as needed
- **Evening:** Quick scan to see any new events

---

## 🆘 Getting Help

### Documentation
1. **This guide** - Quick start basics
2. `docs/EXPANDED_COVERAGE_SUMMARY.md` - Complete technical guide
3. `IMPLEMENTATION_SUMMARY_20250930.md` - Implementation details
4. `README.md` - Project overview

### Common Questions

**Q: How long does initial processing take?**
A: High-priority: 2-4 hours. All countries: 6-8 hours.

**Q: Can I run multiple batch scripts simultaneously?**
A: Yes, but monitor system resources. Recommend running one at a time initially.

**Q: How much disk space do I need?**
A: Minimal - reports are JSON text. Database will grow slowly (~100MB/month).

**Q: Can I stop and resume processing?**
A: Yes - press Ctrl+C to stop, re-run script to continue.

**Q: What if I only care about specific countries?**
A: Edit batch scripts to process only desired countries, or process one data source at a time.

---

## ✅ Verification Checklist

Before starting, verify:
- [ ] All F:/ drive data sources accessible
- [ ] Python 3.7+ installed
- [ ] SQLite3 available
- [ ] At least 10GB free disk space
- [ ] Config file exists: `config/expanded_countries.json`
- [ ] Validation framework exists: `src/core/enhanced_validation_v2.py`

After processing, verify:
- [ ] Country reports generated for each processed country
- [ ] Database has events: `monitoring_events` table populated
- [ ] Daily report generated successfully
- [ ] No critical errors in logs

---

## 🎯 Success Indicators

### Day 1 (Initial Processing):
- ✅ High-priority batch completes without errors
- ✅ At least 50 events detected across 17 countries
- ✅ Database contains country status for all processed countries
- ✅ Monitoring system runs successfully

### Week 1 (Continuous Operation):
- ✅ Daily reports generated automatically
- ✅ Alerts generated for new data
- ✅ Patterns emerging across multiple countries
- ✅ High-confidence matches identified

### Month 1 (Mature Operation):
- ✅ All 42 countries processed at least once
- ✅ Multi-source validation demonstrated
- ✅ Cross-country pattern analysis underway
- ✅ Intelligence reports incorporating new findings

---

**Ready to Start?**

```bash
# Go!
cd "C:/Projects/OSINT - Foresight"
.\scripts\process_expanded_countries_high_priority.bat
```

**Questions?** See `docs/EXPANDED_COVERAGE_SUMMARY.md` for complete guide.

---

*Quick Start Guide - Expanded Coverage | Version 1.0 | September 30, 2025*