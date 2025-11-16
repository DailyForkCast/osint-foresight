# Performance Optimization Plan - Deferred Execution
**Created:** October 18, 2025
**Status:** READY - Defer until FIX_PLAN.md complete
**Estimated Time:** 4.5 hours (unattended)
**Prerequisites:** Other terminal completes tests/FIX_PLAN.md work

---

## ⚠️ Important: Execution Timing

**DO NOT RUN WHILE:**
- tests/FIX_PLAN.md is being executed
- Any pytest tests are running
- Any scripts are querying the database

**SAFE TO RUN:**
- After FIX_PLAN.md completes (3-4 hours)
- During off-hours/overnight
- When no other database access happening

---

## Execution Order (Critical)

### Step 1: Backup Database (5 minutes)
```bash
cd "C:\Projects\OSINT - Foresight"

# Create backup
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db ".backup F:/OSINT_WAREHOUSE/osint_master_backup_20251018.db"

# Verify backup
ls -lh F:/OSINT_WAREHOUSE/osint_master_backup_20251018.db

# Expected: ~23GB file created
```

**Safety:** If anything goes wrong, restore with:
```bash
cp F:/OSINT_WAREHOUSE/osint_master_backup_20251018.db F:/OSINT_WAREHOUSE/osint_master.db
```

---

### Step 2: VACUUM Database (30-60 minutes)
**Impact:** 30-40% query performance improvement
**Lock Status:** BLOCKS ENTIRE DATABASE (exclusive lock)

```bash
# Run VACUUM + ANALYZE
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "VACUUM; ANALYZE;"
```

**What this does:**
1. Rebuilds database file, removing fragmentation
2. Reclaims unused space from deleted records
3. Reorganizes data for sequential access
4. Updates query optimizer statistics

**Expected Output:**
```
(No output = success, returns to prompt after 30-60 min)
```

**Verification:**
```bash
# Check file size (may be slightly smaller)
ls -lh F:/OSINT_WAREHOUSE/osint_master.db

# Test query speed improvement
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "SELECT COUNT(*) FROM ted_contracts_production WHERE publication_date >= '2024-01-01';"
# Should be noticeably faster
```

---

### Step 3: Add Critical Indexes (20 minutes)
**Impact:** 5-10x speedup on specific queries
**Lock Status:** Locks individual tables during creation

Create file: `add_performance_indexes.sql`
```sql
-- arxiv_authors indexes (7.6M rows, currently 0 indexes)
-- Speeds up author-based queries and paper lookups
CREATE INDEX IF NOT EXISTS idx_arxiv_authors_arxiv_id ON arxiv_authors(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_arxiv_authors_author_name ON arxiv_authors(author_name);

-- uspto_case_file indexes (12.7M rows, currently 1 index)
-- Speeds up patent number lookups
CREATE INDEX IF NOT EXISTS idx_uspto_case_file_patent_number ON uspto_case_file(patent_number);
CREATE INDEX IF NOT EXISTS idx_uspto_case_file_filing_date ON uspto_case_file(filing_date);

-- uspto_patents_chinese indexes (425K rows, currently 2 indexes)
-- Speeds up date range and country queries
CREATE INDEX IF NOT EXISTS idx_uspto_patents_chinese_filing_date ON uspto_patents_chinese(filing_date);
CREATE INDEX IF NOT EXISTS idx_uspto_patents_chinese_country ON uspto_patents_chinese(assignee_country);

-- Completion message
SELECT 'Indexes created successfully' AS status;
```

**Execute:**
```bash
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db < add_performance_indexes.sql
```

**Expected Output:**
```
status
------
Indexes created successfully
```

**Verification:**
```bash
# Check indexes were created
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name IN ('arxiv_authors', 'uspto_case_file', 'uspto_patents_chinese') ORDER BY tbl_name, name;"
```

---

### Step 4: TED Chinese Entity Sync (2 hours)
**Impact:** Fixes data integrity (6,180 missing flags)
**Lock Status:** Write lock on ted_contracts_production table

Create file: `sync_ted_chinese_entities.py`
```python
#!/usr/bin/env python3
"""
Sync Chinese entity flags from ted_procurement_chinese_entities_found
to ted_contracts_production table.

Fixes critical data integrity issue where 6,470 detections exist in
analysis table but only 290 flagged in production table.
"""

import sqlite3
import time
from datetime import datetime

def sync_ted_entities():
    print("TED Chinese Entity Synchronization")
    print("="*70)
    print()

    conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db', timeout=30.0)
    cursor = conn.cursor()

    try:
        # Step 1: Count current state
        print("Step 1: Checking current state...")
        cursor.execute('SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1')
        before_count = cursor.fetchone()[0]
        print(f"  Current flagged contracts: {before_count:,}")

        cursor.execute('SELECT COUNT(*) FROM ted_procurement_chinese_entities_found')
        detection_count = cursor.fetchone()[0]
        print(f"  Detections in analysis table: {detection_count:,}")

        gap = detection_count - before_count
        print(f"  Gap to fix: {gap:,} records")
        print()

        # Step 2: Identify records to update
        print("Step 2: Identifying records to update...")
        cursor.execute('''
            SELECT COUNT(DISTINCT tcp.notice_number)
            FROM ted_contracts_production tcp
            JOIN ted_procurement_chinese_entities_found tpcef
                ON tcp.notice_number = tpcef.notice_number
            WHERE tcp.is_chinese_related != 1 OR tcp.is_chinese_related IS NULL
        ''')
        to_update = cursor.fetchone()[0]
        print(f"  Records to update: {to_update:,}")
        print()

        # Step 3: Update flags
        print("Step 3: Updating is_chinese_related flags...")
        print("  This may take several minutes...")
        start_time = time.time()

        cursor.execute('''
            UPDATE ted_contracts_production
            SET is_chinese_related = 1,
                updated_at = datetime('now')
            WHERE notice_number IN (
                SELECT DISTINCT notice_number
                FROM ted_procurement_chinese_entities_found
            )
            AND (is_chinese_related != 1 OR is_chinese_related IS NULL)
        ''')

        updated_count = cursor.rowcount
        elapsed = time.time() - start_time
        print(f"  Updated {updated_count:,} records in {elapsed:.1f} seconds")
        print()

        # Step 4: Verify update
        print("Step 4: Verifying update...")
        cursor.execute('SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1')
        after_count = cursor.fetchone()[0]
        print(f"  Flagged contracts after update: {after_count:,}")

        difference = after_count - before_count
        print(f"  Net change: +{difference:,} records")
        print()

        # Step 5: Commit changes
        print("Step 5: Committing changes...")
        conn.commit()
        print("  ✓ Changes committed successfully")
        print()

        # Step 6: Final statistics
        print("Final Statistics:")
        print("-"*70)
        print(f"  Before: {before_count:,} flagged")
        print(f"  After:  {after_count:,} flagged")
        print(f"  Added:  {difference:,} flags")
        print(f"  Target: {detection_count:,} detections")

        if after_count >= detection_count:
            print()
            print("SUCCESS: All Chinese entities properly flagged!")
        else:
            remaining_gap = detection_count - after_count
            print()
            print(f"WARNING: {remaining_gap:,} records still not synced")

        # Create log file
        log_file = f'logs/ted_entity_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        with open(log_file, 'w') as f:
            f.write(f"TED Entity Sync - {datetime.now()}\n")
            f.write(f"Before: {before_count:,}\n")
            f.write(f"After: {after_count:,}\n")
            f.write(f"Updated: {updated_count:,}\n")
            f.write(f"Elapsed: {elapsed:.1f}s\n")

        print()
        print(f"Log saved to: {log_file}")

    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    sync_ted_entities()
```

**Execute:**
```bash
python sync_ted_chinese_entities.py
```

**Expected Output:**
```
TED Chinese Entity Synchronization
======================================================================

Step 1: Checking current state...
  Current flagged contracts: 290
  Detections in analysis table: 6,470
  Gap to fix: 6,180 records

Step 2: Identifying records to update...
  Records to update: 6,180

Step 3: Updating is_chinese_related flags...
  This may take several minutes...
  Updated 6,180 records in 87.3 seconds

Step 4: Verifying update...
  Flagged contracts after update: 6,470
  Net change: +6,180 records

Step 5: Committing changes...
  ✓ Changes committed successfully

Final Statistics:
----------------------------------------------------------------------
  Before: 290 flagged
  After:  6,470 flagged
  Added:  6,180 flags
  Target: 6,470 detections

SUCCESS: All Chinese entities properly flagged!

Log saved to: logs/ted_entity_sync_20251018_230145.log
```

---

## Post-Execution Validation

### Test 1: Verify Performance Improvement
```bash
python -c "
import sqlite3
import time

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

print('POST-OPTIMIZATION PERFORMANCE TEST')
print('='*70)
print()

# Test 1: arxiv_authors with new indexes
print('Test 1: arxiv_authors query (WITH indexes)')
start = time.time()
cursor.execute('SELECT COUNT(*) FROM arxiv_authors WHERE arxiv_id LIKE \"2024%\"')
result = cursor.fetchone()[0]
elapsed = time.time() - start
print(f'  Result: {result:,} records')
print(f'  Time: {elapsed:.2f} seconds (should be <0.5s)')
print()

# Test 2: TED Chinese entities
print('Test 2: TED Chinese entity count')
cursor.execute('SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1')
chinese_count = cursor.fetchone()[0]
print(f'  Chinese entities: {chinese_count:,}')
print(f'  Expected: 6,470')
print(f'  Status: {\"PASS\" if chinese_count >= 6470 else \"FAIL\"}')
print()

conn.close()
"
```

### Test 2: Verify Data Integrity
```bash
# Check TED entity sync
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "
SELECT
    COUNT(*) as total_contracts,
    SUM(CASE WHEN is_chinese_related = 1 THEN 1 ELSE 0 END) as chinese_flagged,
    (SELECT COUNT(*) FROM ted_procurement_chinese_entities_found) as detections
FROM ted_contracts_production;
"

# Expected output:
# total_contracts|chinese_flagged|detections
# 1131415|6470|6470
```

### Test 3: Query Performance Comparison
Create benchmark before/after comparison.

---

## Rollback Procedures

### If Something Goes Wrong

**Immediate Rollback:**
```bash
# Stop any running processes
# Restore from backup
cp F:/OSINT_WAREHOUSE/osint_master_backup_20251018.db F:/OSINT_WAREHOUSE/osint_master.db

# Verify restoration
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "SELECT COUNT(*) FROM ted_contracts_production;"
# Should return original count
```

**Drop Indexes Only:**
```bash
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "
DROP INDEX IF EXISTS idx_arxiv_authors_arxiv_id;
DROP INDEX IF EXISTS idx_arxiv_authors_author_name;
DROP INDEX IF EXISTS idx_uspto_case_file_patent_number;
DROP INDEX IF EXISTS idx_uspto_case_file_filing_date;
DROP INDEX IF EXISTS idx_uspto_patents_chinese_filing_date;
DROP INDEX IF EXISTS idx_uspto_patents_chinese_country;
"
```

**Revert TED Entity Flags:**
```bash
sqlite3 F:/OSINT_WAREHOUSE/osint_master.db "
UPDATE ted_contracts_production
SET is_chinese_related = 0
WHERE notice_number IN (
    SELECT notice_number FROM ted_procurement_chinese_entities_found
)
AND updated_at > datetime('2025-10-18 22:00:00');
"
```

---

## Success Criteria

All of the following must be true after execution:

- [ ] Backup created successfully (~23GB file exists)
- [ ] VACUUM completed without errors
- [ ] All 6 indexes created successfully
- [ ] TED entities synced (6,470 flagged, up from 290)
- [ ] Query performance improved (measurable with benchmarks)
- [ ] No data loss or corruption
- [ ] All validation queries return expected results

---

## Files Created

This plan creates the following files:
1. `F:/OSINT_WAREHOUSE/osint_master_backup_20251018.db` (23GB backup)
2. `add_performance_indexes.sql` (SQL script for indexes)
3. `sync_ted_chinese_entities.py` (Python script for entity sync)
4. `logs/ted_entity_sync_YYYYMMDD_HHMMSS.log` (Execution log)

---

## Estimated Timeline

| Step | Time | Lock Status |
|------|------|-------------|
| 1. Backup | 5 min | Read lock |
| 2. VACUUM | 30-60 min | **Exclusive lock** |
| 3. Add indexes | 20 min | Table locks |
| 4. TED entity sync | 2 hours | Table lock |
| 5. Validation | 10 min | No locks |
| **Total** | **3-4 hours** | **Safe to run unattended overnight** |

---

## When to Execute

**Best Times:**
- ✅ Tonight after FIX_PLAN.md completes
- ✅ Weekend morning (unattended)
- ✅ Overnight (set up and let run)

**Worst Times:**
- ❌ During active development
- ❌ During test suite execution
- ❌ When other processes query database

---

## Communication

**Before Starting:**
- Announce in team chat/notes that database maintenance happening
- Confirm no one else needs database access for next 4 hours

**During Execution:**
- Monitor progress every 30 minutes
- Check for error messages

**After Completion:**
- Run validation tests
- Report results (before/after performance, entities synced)
- Update documentation with new indexes

---

**Status:** READY TO EXECUTE
**Prerequisites:** tests/FIX_PLAN.md complete
**Next Action:** Wait for green light, then execute Step 1 (Backup)

---

**Created:** October 18, 2025
**Last Updated:** October 18, 2025
**Execution Date:** TBD (after FIX_PLAN.md complete)
