# Terminal C Launch Guide

**Mission**: Process 215 GB USAspending data to detect Chinese entity involvement in US federal spending

**Status**: ✅ READY TO LAUNCH

---

## Infrastructure Checklist

- ✅ **Data Verified**: 74 files, 216 GB at `F:/OSINT_DATA/USAspending/extracted_data/`
- ✅ **Master Database**: 19 GB at `F:/OSINT_WAREHOUSE/osint_master.db`
- ✅ **Processing Script**: `scripts/process_usaspending_comprehensive.py` (752 lines, production-ready)
- ✅ **Production Runner**: `scripts/usaspending_production_full_run.py` (with checkpoint support)
- ✅ **Monitoring Script**: `scripts/monitor_usaspending_production.py`
- ✅ **Output Directory**: `data/processed/usaspending_production_full/`

---

## Launch Commands

### Option 1: Launch in Current Terminal
```bash
cd "C:/Projects/OSINT - Foresight"
python scripts/usaspending_production_full_run.py
```

### Option 2: Launch in Separate Terminals (Recommended)

**Terminal 1 - Run Processing:**
```bash
cd "C:/Projects/OSINT - Foresight"
python scripts/usaspending_production_full_run.py
```

**Terminal 2 - Monitor Progress:**
```bash
cd "C:/Projects/OSINT - Foresight"
python scripts/monitor_usaspending_production.py
```

---

## Expected Results

Based on test runs (100K records):

- **Detection Rate**: 0.51% (514 detections per 100K records)
- **Expected Detections**: 250K-500K records
- **Estimated Value**: $100B+ in federal spending
- **Processing Time**: 8-10 hours for all 74 files
- **Key Finding**: 81% of detections are SUB-CONTRACTORS (hidden under US prime contractors)

---

## Detection Strategy

**7-Field Multi-Layer Detection:**

1. **Country Fields** (HIGH confidence):
   - [29] recipient_location_country_name
   - [39] pop_country_name
   - [65] sub_awardee_country_name

2. **Entity Name Fields** (HIGH confidence):
   - [23] recipient_name
   - [27] recipient_parent_name
   - [59] sub_awardee_name
   - [63] sub_awardee_parent_name

3. **Description Analysis** (MEDIUM confidence):
   - [46] award_description
   - [82] subaward_description
   - (Only flagged if sensitive tech context)

---

## Safety Features

✅ **Checkpoint System**: Automatically saves progress after each file
✅ **Resume Capability**: Can restart from interruption without data loss
✅ **Error Handling**: Failed files logged and skipped, processing continues
✅ **False Positive Prevention**: Word boundary matching, exclusion lists
✅ **Null Handling**: Proper NULL value handling (no fabrication)

---

## Monitoring

While processing runs, the monitoring script provides:
- Files completed / remaining
- Total detections found
- Detection rate (%)
- Database size growth
- Estimated time to completion
- Real-time detection rate

Updates every 30 seconds.

---

## Output Files

**During Processing:**
- `checkpoint.json` - Progress tracker (resume capability)
- `<filename>_<timestamp>.json` - Individual file results

**After Completion:**
- `PRODUCTION_RUN_SUMMARY.json` - Complete statistics
- `PRODUCTION_RUN_REPORT.txt` - Human-readable report

**Database:**
- Table: `usaspending_china_comprehensive` in `F:/OSINT_WAREHOUSE/osint_master.db`

---

## Zero Fabrication Protocol

✅ Only flag records with explicit evidence
✅ No assumptions or guesses
✅ All detections include rationale and confidence level
✅ NULL values handled properly (not fabricated)

---

## Commands Reference

**Start Processing:**
```bash
python scripts/usaspending_production_full_run.py
```

**Monitor Progress:**
```bash
python scripts/monitor_usaspending_production.py
```

**Check Checkpoint:**
```bash
cat data/processed/usaspending_production_full/checkpoint.json
```

**Check Database:**
```bash
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "SELECT COUNT(*) FROM usaspending_china_comprehensive"
```

---

## Estimated Timeline

- **File 1**: Starts immediately
- **Hour 2**: ~15 files complete
- **Hour 5**: ~37 files complete (50%)
- **Hour 8**: ~60 files complete (80%)
- **Hour 10**: All 74 files complete ✅

**Note**: Times vary based on file size and detection density.

---

## Next Steps After Completion

1. Review `PRODUCTION_RUN_REPORT.txt`
2. Query database for high-value detections
3. Analyze sub-contractor exposure (expected 81%)
4. Cross-reference with other intelligence sources
5. Generate executive summary

---

**Terminal C Mission Statement:**

*Extract all Chinese entity involvement in US federal spending (2000-2025) using multi-field detection across 215 GB of USAspending data, with Zero Fabrication Protocol and comprehensive evidence capture.*

---

**Ready to Launch!** 🚀
