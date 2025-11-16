# GKG Collection - Challenges and Solution

**Updated:** November 6, 2025 at 20:34 UTC (3:34 PM EST)

---

## Current Status

**Collected So Far:**
- **1,073,271 China-related GKG records**
- **20 dates collected** (out of 100 target)
- **80 dates remaining**
- **Storage used:** ~3.5 GB

---

## Challenges Encountered

###  1: Process Getting Killed (Memory Issue)

**Problem:** Background collection process repeatedly killed by system (exit code 137)

**Root Cause:** System OOM (Out of Memory) killer terminating process

**Solution Attempts:**
- ✅ Modified script to skip already-collected dates (avoids re-processing)
- ⏳ Switched to smaller batches (10 dates at a time instead of 81)

---

### Challenge 2: Database Locking

**Problem:** "database is locked" errors when multiple processes try to write

**Root Cause:** Multiple background processes attempting concurrent writes

**Solution:** Killed all old processes before starting new collection

---

### Challenge 3: Unicode Logging Errors

**Problem:** Windows console couldn't display ✓ checkmark character

**Impact:** Minor - doesn't affect data collection

**Solution:** Changed ✓ to `[SKIP]` in log messages

---

## Current Approach: Batch Collection

**New Strategy:**
- Collect 10 dates at a time (instead of all 81 remaining)
- Reduced memory footprint
- Easier to monitor and troubleshoot
- Can resume if interrupted

**Batch 1 (Currently Running):**
```
20230619, 20220804, 20200207, 20250831, 20230411,
20250409, 20220803, 20230406, 20220805, 20240516
```

**Estimated for 10 dates:**
- Records: ~560,000 China-related
- Storage: ~1.8 GB
- Time: ~40-50 minutes
- Cost: $0.00

---

## Data Already Collected

**Dates Successfully Collected (20):**

**COVID Outbreak Period:**
- Jan 28-30, 2020
- Jan 31 - Feb 6, 2020

**2023 High Activity:**
- Mar 27, 29, 30, 2023
- Apr 5, 2023
- Apr 27, 2023 (partial - 5,196 records)
- June 20, 2023

**2023 Fall:**
- Oct 17, 2023

**Recent 2025:**
- Sept 1-2, 2025
- Oct 30, 2025

---

## Remaining Work

**After Batch 1 Completes:**
- 70 dates still to collect
- Plan: Run 7 more batches of 10 dates each
- Total time estimate: ~6-7 hours
- Can be done overnight or over multiple sessions

**Total When Complete (100 dates):**
- ~5.6M China-related GKG records
- ~18 GB storage
- ~$0.00 cost
- Keyword search capability enabled

---

## Lessons Learned

1. **Batch processing is better than all-at-once** for large datasets
2. **Database locking requires process cleanup** between runs
3. **Memory limits** on this system require smaller chunks
4. **Progress is being saved** - each completed date is permanently stored

---

## Next Steps

1. **Monitor Batch 1:** Wait for 10 dates to complete (~40-50 min)
2. **Verify Data:** Check record counts and data quality
3. **Continue Batches:** Run batches 2-8 to complete remaining 70 dates
4. **Test Keyword Searches:** Once complete, validate GKG usefulness

---

## Process ID for Current Collection

**Bash ID:** 714003
**Started:** 20:31 UTC (3:31 PM EST)
**Status:** Running
**Command:**
```bash
python scripts/collectors/gdelt_gkg_free_collector.py \
  --dates "20230619,20220804,20200207,20250831,20230411,20250409,20220803,20230406,20220805,20240516"
```

---

## Monitoring Commands

```bash
# Check if still running
ps aux | grep gdelt_gkg | grep -v grep

# Check current record count
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM gdelt_gkg'); print(f'{cursor.fetchone()[0]:,}'); conn.close()"

# Count completed dates
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(DISTINCT SUBSTR(CAST(publish_date AS TEXT), 1, 8)) FROM gdelt_gkg'); print(f'Dates: {cursor.fetchone()[0]}'); conn.close()"
```

---

**Status:** Batch 1 collection in progress. Will continue with remaining batches once this completes.
