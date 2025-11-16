# Thinktank Reports Automation - Setup Instructions

**Date**: 2025-10-11
**Status**: Ready to deploy - Week 1 monitoring period

---

## Quick Start

### Option 1: Automatic Setup (Recommended)

Run the setup script as Administrator:

```bash
# Right-click and "Run as Administrator"
scripts\automation\setup_windows_scheduler.bat
```

This will create 3 scheduled tasks:
- `OSINT_Weekly_MCF_Sweep` - Mondays at 9:00 AM
- `OSINT_Regional_Sprint` - Sundays at 10:00 AM
- `OSINT_Gap_Map_Refresh` - Daily at 11:00 PM

### Option 2: Manual Verification

Check the schedule is active:

```bash
python scripts/automation/intake_scheduler.py --schedule
```

View Windows scheduled tasks:
```bash
taskschd.msc
```

---

## What Happens Next Week

### Monday, October 14, 9:00 AM - First Weekly Sweep
**Action**: Automatic EU/MCF sweep runs
- Targets: MERICS, EUISS, RUSI, Bruegel, IFRI, SWP, IISS
- Output: `data/external/eu_mcf_reports/eu_mcf_reports_[timestamp].json`
- Log: `logs/weekly_sweep.log`

**You'll receive**: List of new reports found with download links

### Sunday, October 13, 10:00 AM - First Regional Sprint
**Action**: Nordic countries intelligence sprint
- Targets: Swedish Defense Research Agency, Norwegian Defence Research, DIIS (Denmark)
- Output: Regional-specific collection results
- Log: `logs/regional_sprint.log`

**Next regions**: Balkans (Week 2), DACH (Week 3), Benelux (Week 4), Baltics (Week 5)

### Daily, 11:00 PM - Gap Map Refresh
**Action**: Coverage analysis updates
- Recalculates region × topic matrix
- Identifies new gaps
- Tracks coverage improvements

---

## Monitoring Week 1

### What to Check

**Monday Morning (After 9 AM)**:
```bash
# Check weekly sweep results
cat logs/weekly_sweep.log

# View found reports
python -c "import json; print(json.load(open(sorted(glob.glob('data/external/eu_mcf_reports/eu_mcf_reports_*.json'))[-1]))['total_found'])"
```

**Sunday Evening (After 10 AM)**:
```bash
# Check regional sprint
cat logs/regional_sprint.log

# Verify rotation advanced
python scripts/automation/intake_scheduler.py --schedule | grep "Current Region"
```

**Daily**:
```bash
# Check gap map refresh
cat logs/gap_refresh.log
```

### Expected First Week Results

**Weekly Sweep (Monday)**:
- Estimated: 2-5 new reports
- Success rate: 50-80% (needs refinement)
- Download: 1-3 PDFs

**Regional Sprint (Sunday)**:
- Estimated: 1-3 Nordic reports
- Focus: Arctic coverage (current gap)
- Next region: Balkans (Week 2)

**Gap Map**:
- Current: 55% gaps (10 empty cells)
- Target: <40% by Week 4

---

## Manual Operations

### Run Weekly Sweep Manually
```bash
python scripts/automation/intake_scheduler.py --run-weekly
```

### Run Regional Sprint Manually
```bash
python scripts/automation/intake_scheduler.py --run-sprint
```

### Refresh Gap Map Manually
```bash
python scripts/automation/intake_scheduler.py --refresh-gap
```

---

## Troubleshooting

### Tasks Not Running

**Check if tasks exist**:
```bash
schtasks /query /tn "OSINT_Weekly_MCF_Sweep"
schtasks /query /tn "OSINT_Regional_Sprint"
schtasks /query /tn "OSINT_Gap_Map_Refresh"
```

**Re-create tasks**:
```bash
# Run as Administrator
scripts\automation\setup_windows_scheduler.bat
```

### No Reports Found

**Check scrapers**:
```bash
# Test EU MCF finder
python scripts/collectors/eu_mcf_report_finder.py
```

**Expected**: Some websites may require manual collection (government sites)

### Logs Not Appearing

**Create logs directory**:
```bash
mkdir logs
```

**Check permissions**: Ensure scripts can write to `logs/` directory

---

## Post-Week 1 Actions

### After First Successful Run

1. **Review Results**:
   - Check `logs/weekly_sweep.log` for errors
   - Validate downloaded reports in `data/external/eu_mcf_reports/downloads/`
   - Confirm gap map updated

2. **Adjust Schedule** (if needed):
   - Edit `config/intake_schedule.json`
   - Modify times, frequencies, or sources
   - Re-run setup script to apply changes

3. **Scale Up**:
   - Add more think tank sources
   - Implement CORDIS/OpenAlex entity matching
   - Run full cross-reference wiring (986 entities)

### Week 2 Priorities

1. **Fill Arctic Gap**: Target NATO, OECD Arctic reports
2. **Semiconductor Coverage**: Netherlands Chips Act manual collection
3. **Entity Matching**: Run full TED cross-reference (20-min job)
4. **URL Collection**: Add missing canonical URLs (25 reports)

---

## Configuration

### Schedule Configuration File
**Location**: `config/intake_schedule.json`

```json
{
  "weekly_sweep": {
    "enabled": true,
    "day_of_week": "Monday",
    "time": "09:00",
    "sources": ["MERICS", "EUISS", "RUSI", "Bruegel", "IFRI", "SWP", "IISS"]
  },
  "regional_sprints": {
    "enabled": true,
    "rotation": ["Nordics", "Balkans", "DACH", "Benelux", "Baltics"],
    "current_region": "Nordics"
  }
}
```

### Modify Schedule

**Change sweep day/time**:
```json
"day_of_week": "Tuesday",
"time": "14:00"
```

**Add/remove sources**:
```json
"sources": ["MERICS", "EUISS", "RUSI", "Bruegel", "CSIS", "Carnegie"]
```

**Then re-run setup**:
```bash
scripts\automation\setup_windows_scheduler.bat
```

---

## Performance Expectations

### Week 1 Baseline
- **Weekly Sweep**: 2-5 reports found, 1-3 downloaded
- **Regional Sprint**: 1-3 Nordic reports
- **Gap Coverage**: Small improvement (~2-3%)
- **Total Time**: ~30 min automation runtime/week

### Week 4 Target
- **Weekly Sweep**: 5-10 reports found, 4-7 downloaded
- **Regional Sprint**: Consistent 3-5 reports per region
- **Gap Coverage**: <40% (from 55%)
- **Total Reports**: 75+ (from 25)

### Month 1 Goal
- **Database**: 100+ reports
- **Coverage**: <30% gaps
- **Automation**: 90%+ success rate
- **Cross-references**: Full entity matching complete

---

## Support

### Documentation
- [Complete Session Summary](analysis/COMPLETE_SESSION_SUMMARY.md)
- [Detailed Progress Report](analysis/SESSION_SUMMARY_20251010.md)
- [Gap Map Analysis](analysis/gap_map_region_topic.json)
- [Extraction Test Results](analysis/extraction_smoke_test_results.json)

### Scripts
- **Scheduling**: `scripts/automation/intake_scheduler.py`
- **EU Finder**: `scripts/collectors/eu_mcf_report_finder.py`
- **Downloader**: `scripts/collectors/eu_mcf_report_downloader.py`
- **Enrichment**: `scripts/maintenance/enrich_report_metadata.py`
- **Cross-ref**: `scripts/maintenance/wire_report_cross_references.py`

### Quick Commands
```bash
# View schedule
python scripts/automation/intake_scheduler.py --schedule

# Check Windows tasks
taskschd.msc

# Monitor logs
tail -f logs/weekly_sweep.log
tail -f logs/regional_sprint.log
tail -f logs/gap_refresh.log
```

---

## Success Metrics

**Week 1 Pass Criteria**:
- ✅ All 3 tasks execute successfully
- ✅ At least 1 new report downloaded
- ✅ Gap map refreshes without errors
- ✅ Logs show no critical failures

**Week 4 Pass Criteria**:
- ✅ Consistent 5+ reports per weekly sweep
- ✅ All 5 regions successfully rotated
- ✅ Gap coverage <40%
- ✅ Automation requires minimal intervention

---

**Setup Date**: 2025-10-11
**First Run**: Monday, October 14, 2025, 9:00 AM
**Review Date**: Monday, October 21, 2025 (after Week 1)

**Status**: ✅ READY TO DEPLOY - Let automation run for 1 week!
