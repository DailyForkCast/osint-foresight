# SEC ETL Execution & Validation Guide
**Date:** November 4, 2025
**Status:** READY TO EXECUTE (after GLEIF completes)
**Script:** `scripts/etl/etl_corporate_links_from_sec.py`

---

## Pre-Execution Checklist

### 1. Verify GLEIF ETL Complete

**Check GLEIF process status:**
```bash
# Check if GLEIF ETL is still running in other terminal
ps aux | grep gleif
```

**Expected:** No active GLEIF process

### 2. Verify Database Accessible

**Test database connection:**
```bash
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); print('OK'); conn.close()"
```

**Expected:** `OK` printed with no errors

### 3. Backup Current State

**Create backup before SEC ETL:**
```bash
cd F:/OSINT_WAREHOUSE
cp osint_master.db osint_master_backup_before_sec_etl.db
```

**Expected:** Backup file created (~32GB)

---

## Execution Modes

### Dry-Run Mode (Recommended First)

**Purpose:** Test extraction without database writes

```bash
cd C:/Projects/OSINT-Foresight
python scripts/etl/etl_corporate_links_from_sec.py --dry-run
```

**What it does:**
- ✓ Connects in read-only mode
- ✓ Extracts relationships from SEC data
- ✓ Performs deduplication
- ✓ Generates report
- ✗ Does NOT write to database

**Expected output:**
```
================================================================================
SEC EDGAR CORPORATE LINKS ETL
================================================================================
DRY RUN MODE - No database writes
...
Extracted 28-41 unique links
...
ETL COMPLETE
```

**Review dry-run report:**
```bash
cat analysis/etl_validation/sec_etl_report_YYYYMMDD_HHMMSS.json
```

### Production Mode

**Purpose:** Execute full ETL with database writes

```bash
cd C:/Projects/OSINT-Foresight
python scripts/etl/etl_corporate_links_from_sec.py --production
```

**Confirmation prompt:**
```
PRODUCTION MODE: Write to database? (yes/no):
```

**Type:** `yes` and press Enter

**What it does:**
- ✓ Connects in write mode
- ✓ Extracts relationships
- ✓ Deduplicates
- ✓ **Writes to bilateral_corporate_links**
- ✓ Generates report

**Expected runtime:** 2-5 minutes

**Expected output:**
```
================================================================================
EXECUTION SUMMARY
================================================================================
Source Records: 290
Extracted Links: 52
Unique Links: 41
Inserted: 41
Database Growth: 19 -> 60

Relationship Types:
  strategic_stake: 18
  institutional_holding: 12
  strategic_investment: 8
  minority_stake: 2
  acquisition: 1

Zero Fabrication Compliance: ✓
All links traceable to SEC accession numbers

================================================================================
ETL COMPLETE
================================================================================
```

---

## Post-Execution Validation

### 1. Statistical Validation

**Check bilateral_corporate_links growth:**
```python
import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Count total
cursor.execute('SELECT COUNT(*) FROM bilateral_corporate_links')
print(f"Total links: {cursor.fetchone()[0]}")

# Count by source
cursor.execute("""
    SELECT
        CASE
            WHEN investment_id IS NOT NULL THEN 'bilateral_investments'
            WHEN gleif_lei IS NOT NULL THEN 'GLEIF'
            ELSE 'SEC'
        END as source,
        COUNT(*) as count
    FROM bilateral_corporate_links
    GROUP BY source
""")
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")

conn.close()
```

**Expected:**
```
Total links: 60 (or 19+GLEIF+SEC)
bilateral_investments: 19
GLEIF: [depends on GLEIF ETL]
SEC: 28-41
```

### 2. Data Quality Validation

**Check for required fields:**
```python
import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Check for NULLs in required fields
cursor.execute("""
    SELECT COUNT(*)
    FROM bilateral_corporate_links
    WHERE chinese_entity IS NULL OR foreign_entity IS NULL
""")
null_count = cursor.fetchone()[0]
print(f"Records with NULL required fields: {null_count}")
# Expected: 0

# Check for duplicates
cursor.execute("""
    SELECT chinese_entity, foreign_entity, COUNT(*) as cnt
    FROM bilateral_corporate_links
    GROUP BY chinese_entity, foreign_entity
    HAVING cnt > 1
""")
dupes = cursor.fetchall()
print(f"Duplicate pairs: {len(dupes)}")
# Expected: 0

conn.close()
```

### 3. Manual 100-Record Sample Review

**Generate random sample:**
```python
import sqlite3
import random

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Get SEC-sourced links only
cursor.execute("""
    SELECT link_id, chinese_entity, foreign_entity, relationship_type, ownership_percentage
    FROM bilateral_corporate_links
    WHERE investment_id IS NULL
    AND gleif_lei IS NULL
    ORDER BY created_at DESC
""")

sec_links = cursor.fetchall()
print(f"Total SEC links: {len(sec_links)}")

# Sample 100 (or all if <100)
sample_size = min(100, len(sec_links))
sample = random.sample(sec_links, sample_size)

print(f"\nManual Review Sample ({sample_size} records):")
print("=" * 80)
for i, link in enumerate(sample[:10], 1):  # Show first 10
    print(f"{i}. {link[1]} -> {link[2]}")
    print(f"   Type: {link[3]}, Ownership: {link[4] if link[4] else 'N/A'}")

# Export full sample for review
with open('analysis/etl_validation/sec_links_sample_for_review.txt', 'w') as f:
    for link in sample:
        f.write(f"{link[1]} -> {link[2]} | {link[3]} | {link[4] if link[4] else 'N/A'}\n")

print(f"\nFull sample exported to: analysis/etl_validation/sec_links_sample_for_review.txt")
conn.close()
```

**Manual review checklist:**
- [ ] Chinese entity names look plausible (not obviously Western companies)
- [ ] Foreign entity names are US/Western companies
- [ ] Relationship types make sense for context
- [ ] No obvious false positives
- [ ] Ownership percentages (if present) are reasonable

**Target precision: ≥90%** (≤10 false positives in 100-record sample)

### 4. Cross-Reference Validation

**Verify against known relationships:**
```python
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Check for known Chinese investment cases
known_cases = [
    'Alibaba',
    'Tencent',
    'Baidu',
    'China Investment Corporation',
    'SAFE Investment'
]

print("Known Chinese entities in SEC links:")
for entity in known_cases:
    cursor.execute("""
        SELECT chinese_entity, foreign_entity, relationship_type
        FROM bilateral_corporate_links
        WHERE chinese_entity LIKE ?
    """, (f'%{entity}%',))

    results = cursor.fetchall()
    if results:
        print(f"\n{entity}: {len(results)} links found")
        for r in results[:3]:
            print(f"  -> {r[1]} ({r[2]})")
    else:
        print(f"\n{entity}: Not found")

conn.close()
```

---

## Expected Results Summary

### Quantitative Targets

| Metric | Target Range | Validation Method |
|--------|-------------|-------------------|
| New links created | 28-41 | Post-execution count |
| strategic_stake | 15-25 | Relationship type breakdown |
| institutional_holding | 10-15 | Relationship type breakdown |
| strategic_investment | 3-5 | Relationship type breakdown |
| NULL required fields | 0 | Data quality check |
| Duplicate pairs | 0 | Deduplication check |
| Precision | ≥90% | 100-record manual sample |

### Qualitative Targets

- ✅ All links traceable to SEC accession numbers
- ✅ No inferred ownership percentages
- ✅ Relationship types match form types
- ✅ No self-referential links (company → itself)
- ✅ Chinese entities are plausibly Chinese
- ✅ Foreign entities are US-listed companies

---

## Rollback Procedure

**If validation fails or errors occur:**

```bash
# Stop any running processes
# Kill ETL if still running

# Restore from backup
cd F:/OSINT_WAREHOUSE
cp osint_master_backup_before_sec_etl.db osint_master.db

# Verify restoration
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM bilateral_corporate_links'); print(f'Count: {cursor.fetchone()[0]}'); conn.close()"
# Expected: Original count (19 or 19+GLEIF)
```

---

## Common Issues & Solutions

### Issue: Database is locked

**Symptom:** `sqlite3.OperationalError: database is locked`

**Cause:** GLEIF ETL still running or another process accessing database

**Solution:**
```bash
# Check for running processes
ps aux | grep gleif
ps aux | grep python

# Kill if necessary (Windows)
tasklist | findstr python
taskkill /PID <pid> /F

# Wait 30 seconds for locks to release
# Retry SEC ETL
```

### Issue: No records extracted

**Symptom:** `Extracted Links: 0`

**Cause:** Database schema mismatch or data missing

**Solution:**
```bash
# Verify sec_13d_13g_filings has data
python -c "import sqlite3; conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM sec_13d_13g_filings WHERE is_chinese = 1'); print(cursor.fetchone()[0]); conn.close()"
# Expected: 52

# If 0, check source data collection
```

### Issue: High false positive rate

**Symptom:** >10% false positives in manual sample

**Cause:** `is_chinese` detection flag incorrect

**Solution:**
1. Document specific false positives
2. Adjust `is_chinese` detection in source collector
3. Rollback SEC ETL
4. Fix detection system
5. Re-run SEC ETL

---

## Next Steps After Successful Execution

### 1. Combine GLEIF + SEC Analysis

**Generate combined report:**
```python
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT
        CASE
            WHEN investment_id IS NOT NULL THEN 'bilateral_investments'
            WHEN gleif_lei IS NOT NULL THEN 'GLEIF'
            ELSE 'SEC'
        END as source,
        relationship_type,
        COUNT(*) as count,
        AVG(ownership_percentage) as avg_ownership
    FROM bilateral_corporate_links
    GROUP BY source, relationship_type
    ORDER BY source, count DESC
""")

print("Combined GLEIF + SEC Results:")
print("=" * 80)
for row in cursor.fetchall():
    avg = f"{row[3]:.1f}%" if row[3] else 'N/A'
    print(f"{row[0]:25} | {row[1]:25} | {row[2]:5} | {avg}")

conn.close()
```

### 2. Update Documentation

- [ ] Update README with SEC ETL completion
- [ ] Document actual vs. expected results
- [ ] Note any limitations discovered
- [ ] Update data source inventory

### 3. Plan Next ETL

**Priority order:**
1. ✅ bilateral_investments (19 links) - DONE
2. ✅ GLEIF (1,000-3,000 links) - IN PROGRESS
3. ✅ SEC 13D/13G (28-41 links) - READY
4. ⏳ TED contractors (500-1,000 links) - NEXT
5. ⏳ OpenAlex institutions (200-500 links)
6. ⏳ Patent assignees (100-300 links)

**Target:** 2,000+ bilateral_corporate_links by end of Phase 1

---

## Files Generated

**Execution log:**
```
analysis/etl_validation/sec_etl_log_YYYYMMDD_HHMMSS.log
```

**JSON report:**
```
analysis/etl_validation/sec_etl_report_YYYYMMDD_HHMMSS.json
```

**Sample for review:**
```
analysis/etl_validation/sec_links_sample_for_review.txt
```

---

## Contact & Support

**Questions about execution:**
- Review design doc: `scripts/etl/etl_corporate_links_from_sec_DESIGN.md`
- Check ETL script: `scripts/etl/etl_corporate_links_from_sec.py`
- Review logs in: `analysis/etl_validation/`

**Zero Fabrication Protocol:**
- All claims must be traceable to SEC filings
- No inferred data - use NULL when not in source
- Document limitations clearly
- Manual validation required (≥90% precision)

---

**Document Status:** COMPLETE
**Ready to Execute:** YES (after GLEIF completes)
**Estimated Runtime:** 2-5 minutes
**Expected Output:** 28-41 new bilateral_corporate_links
**Validation Required:** 100-record manual sample review
