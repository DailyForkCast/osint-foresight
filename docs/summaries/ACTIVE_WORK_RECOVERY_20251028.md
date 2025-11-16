# Active Work Recovery - October 28, 2025
**VS Code Unexpected Shutdown - Multi-Terminal Work Resume Guide**

---

## Quick Status Overview

| Terminal | Task | Status | Time Est. | Priority |
|----------|------|--------|-----------|----------|
| A | Policy URL Verification (Manual) | 🔴 IN PROGRESS | 2-2.5h | **URGENT** |
| B | GLEIF Relationship Processing | ⏸️ READY TO RUN | 30-45min | **HIGH** |
| C | Git Commits (README, cross_ref fixes) | ⏸️ UNCOMMITTED | 10min | **MEDIUM** |
| D | OpenSanctions Database Merge | ⏸️ READY TO RUN | 15-20min | **HIGH** |
| E | Database Lock Resolution + Sector Policies | ⏸️ BLOCKED | 5-10min | **MEDIUM** |

---

## 🔴 TERMINAL A: Policy URL Verification (Manual Work)

### Overview
**What:** Verify 98 European technology policy document URLs to find direct PDF links
**Status:** CSV created, 0% complete (all URLs need verification)
**Blocking:** Manual human work required (web browsing to find PDFs)
**Output:** Updated CSV with verified PDF URLs

### Files Involved
```
INPUT:  policy_urls_PRIORITIZED_20251028_180500.csv
OUTPUT: policy_urls_PRIORITIZED_20251028_180500.csv (updated with verified_pdf_url column filled)
GUIDE:  analysis/PRIORITIZED_CSV_GUIDE.md (detailed instructions)
```

### Breakdown
- ✅ **2 documents:** Already done (Ireland: Cyber Strategy, Italy: Recovery Plan) → SKIP
- 🔴 **45 documents:** Broken URLs (404/403/timeout) → **START HERE**
- 🟡 **51 documents:** HTML landing pages → **THEN THIS**

### Top Broken URL Countries (Fix Priority Order)
1. 🇫🇷 **France:** 9 documents (gouvernement.fr - bot protection)
2. 🇩🇪 **Germany:** 6 documents (bmwk.de, bmbf.de, bmi.bund.de)
3. 🇸🇪 **Sweden:** 4 documents (government.se - bot protection)
4. 🇳🇱 **Netherlands:** 3 documents
5. 🇷🇴 **Romania:** 3 documents (timeouts)

### Workflow

#### Step 1: Open CSV
```bash
# Open in Excel or LibreOffice Calc
start policy_urls_PRIORITIZED_20251028_180500.csv
```

#### Step 2: Sort by Priority Column
- 0_SKIP (2 docs) - ignore
- **1_PRIORITY (45 docs) - START HERE** ← Broken URLs
- 2_NEED_PDF (51 docs) - Do after broken URLs fixed

#### Step 3: For Each Broken URL
1. Copy document title from CSV
2. Search: `[document title] [country] PDF site:gov.[country]`
3. For EU documents: Try EUR-Lex search
4. If found: Copy PDF URL to `verified_pdf_url` column
5. If not found: Note "Document not available online" in `notes` column

#### Step 4: For Each HTML Page
1. Visit the URL in `current_url` column
2. Look for "Download", "PDF", "Télécharger" link
3. Right-click PDF link → Copy link address
4. Paste to `verified_pdf_url` column
5. Add note like "Full version selected" if multiple PDFs exist

#### Step 5: Quality Check
For each verified URL, confirm:
- [ ] URL ends with `.pdf` OR opens PDF in browser
- [ ] File size > 100 KB (not error page)
- [ ] Document title roughly matches
- [ ] Language is English or original

#### Step 6: Save & Import
```bash
# After completing CSV verification:
python scripts/utilities/import_verified_policy_urls.py

# Then download all PDFs:
python scripts/processors/policy_document_processor.py
```

### EUR-Lex Quick Wins (23 EU documents)
Most standardized structure - do these first:

**Pattern:**
- Landing page: `https://eur-lex.europa.eu/eli/reg/2024/1689/oj`
- PDF URL: `https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32024R1689`

**Steps:**
1. Visit EUR-Lex URL
2. Look for "Download" dropdown → Select "PDF"
3. Copy direct PDF URL
4. Paste to `verified_pdf_url` column

### UK Government Quick Wins (11 documents)
**Pattern:**
- Landing page: `https://www.gov.uk/government/publications/national-ai-strategy`
- PDF URL: `https://assets.publishing.service.gov.uk/media/[ID]/[filename].pdf`

**Steps:**
1. Visit gov.uk URL
2. Scroll to "Documents" section
3. Right-click PDF link → Copy link address
4. Paste to `verified_pdf_url` column

### Progress Tracking
Add "DONE" to `notes` column as you complete each country to track progress.

**Estimated Time:**
- Phase 1 (EUR-Lex): 30 min (23 docs)
- Phase 2 (UK): 20 min (11 docs)
- Phase 3 (Broken URLs): 45-60 min (45 docs)
- Phase 4 (Other HTML): 30-45 min (remaining)
- **Total: 2-2.5 hours**

---

## 🟠 TERMINAL B: GLEIF Relationship Processing

### Overview
**What:** Process 464K GLEIF relationship records that failed on Oct 11 due to database locks
**Status:** Script ready, files available, database lock issue documented
**Impact:** Enables corporate ownership network analysis, Chinese company registry linkage
**Why it failed:** Database locking during Oct 11 processing

### The Gap
- ✅ `gleif_entities`: 3,086,233 records LOADED (Oct 11)
- ❌ `gleif_relationships`: **1 record** (should have ~464,000)
- ❌ 6 mapping tables empty despite 140MB of files existing

### Files to Process

**Location:** `F:/GLEIF/`

**Relationship Files (32-33MB):**
```
20251011-0800-gleif-goldencopy-rr-golden-copy.json.zip (32MB)
20251011-0800-gleif-goldencopy-rr-golden-copy.json (1).zip (32MB duplicate)
20251011-gleif-concatenated-file-rr.xml.68ea1f4a31eb4.zip (33MB XML)
```

**Mapping Files (~140MB total):**
```
LEI-BIC-*.zip              (365KB - Bank Identifier Codes)
isin-lei-*.zip             (26MB - Securities mapping)
LEI-QCC-*.zip              (29MB x2 - Chinese corporate registry) ← CRITICAL for China analysis
oc-lei-*.zip               (23MB - OpenCorporates linkage)
repex-golden-copy.json.zip (55MB - Reporting exceptions)
```

### Processing Scripts

#### Primary: Relationship Processing
```bash
# Script specifically designed to fix the Oct 11 database lock failure
python scripts/reprocess_gleif_relationships.py
```

**Script features:**
- Retry logic for database locks
- WAL mode for better concurrency
- Focuses only on 464K relationship records
- Expected runtime: 30-45 minutes

**Expected output:**
```
Processing GLEIF relationships...
Found 464,000 relationship records in JSON
Processing batch 1/47... (10,000 records)
Processing batch 2/47... (10,000 records)
...
✅ Complete: 464,000 relationship records inserted
```

#### Secondary: Mapping File Processing
After relationships complete, process mapping files. Check if scripts exist:
```bash
# Check for mapping processors
ls scripts/processors/gleif_*
ls scripts/collectors/gleif_*

# If not exist, we'll need to create them
# Priority order:
# 1. QCC mapping (Chinese corporate registry) - HIGHEST VALUE
# 2. BIC mapping (bank identifiers)
# 3. ISIN mapping (securities)
# 4. OpenCorporates mapping
# 5. REPEX (reporting exceptions)
```

### Verification After Processing
```bash
# Connect to database and verify
python -c "
import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()

# Check relationships loaded
cur.execute('SELECT COUNT(*) FROM gleif_relationships')
print(f'Relationships: {cur.fetchone()[0]:,}')

# Check mapping tables
tables = ['gleif_bic_mapping', 'gleif_isin_mapping', 'gleif_qcc_mapping',
          'gleif_opencorporates_mapping', 'gleif_cross_references', 'gleif_repex']
for table in tables:
    cur.execute(f'SELECT COUNT(*) FROM {table}')
    print(f'{table}: {cur.fetchone()[0]:,}')

conn.close()
"
```

**Expected results:**
- `gleif_relationships`: ~464,000 (currently 1)
- `gleif_qcc_mapping`: ~50,000+ (currently 0)
- `gleif_bic_mapping`: ~10,000+ (currently 0)
- `gleif_isin_mapping`: ~200,000+ (currently 0)

### What This Unlocks
Once complete, you can:
- **Corporate ownership networks:** Parent-subsidiary relationships for 3M+ entities
- **Chinese company registry links:** QCC mapping enables Chinese entity resolution
- **Bank identifier cross-referencing:** Link LEI to BIC codes
- **Securities mapping:** Connect legal entities to traded securities
- **Supply chain analysis:** Multi-hop relationship traversal

---

## 🟡 TERMINAL C: Git Commits (Quick Cleanup)

### Overview
**What:** Commit uncommitted changes to README.md and cross_reference_analyzer.py
**Status:** Changes staged but not committed
**Time:** 10 minutes
**Priority:** Medium (good housekeeping, prevents conflicts)

### Files to Commit

#### 1. README.md (Large additions)
**Changes:**
- Added EU-China Bilateral Relations Intelligence Platform section (Oct 23)
- Added BCI Technology Domain section (Oct 26)
- Added BCI Technology Ecosystem section (15 related technologies)

**Review changes:**
```bash
git diff README.md | head -200
```

**Commit:**
```bash
git add README.md
git commit -m "docs: Add EU-China bilateral relations platform and BCI technology framework

- EU-China Bilateral Relations Intelligence Platform (Oct 23, 2025)
  - 124 bilateral events across 28 EU countries
  - 1.56M academic collaborations tracked
  - Lithuania Taiwan office impact: -89.3% research drop in 2021
  - 304 multi-source citations (99.7% Level 1-2 quality)

- BCI Technology Domain (Oct 26, 2025)
  - 20+ BCI conferences cataloged
  - China Brain Project (2016-2031) strategic assessment
  - Dual-use military/medical applications tracked
  - 15 related technology ecosystem framework

- Documentation links to analysis reports and configuration files"
```

#### 2. cross_reference_analyzer.py (Schema fixes)
**Changes:**
- Disabled broken queries referencing non-existent tables
- Updated leonardo database query to use correct table
- Fixed mcf_entities column names
- Added comments documenting fixes

**Review changes:**
```bash
git diff scripts/cross_reference_analyzer.py
```

**Test before committing:**
```bash
# Verify script doesn't crash with schema fixes
python scripts/cross_reference_analyzer.py --dry-run 2>&1 | head -50
```

**Commit:**
```bash
git add scripts/cross_reference_analyzer.py
git commit -m "fix: Update cross_reference_analyzer.py for current database schemas

- Fixed leonardo database query (technology_assessments -> document_entities)
- Disabled mcf_entities queries due to schema mismatch
- Disabled patent/arctic queries for non-existent tables
- Added comments documenting all fixes
- Prevents crashes when running cross-reference analysis"
```

#### 3. Other Modified Files
Check git status for other changes:
```bash
git status

# You should see:
# M .claude/settings.local.json  (probably skip this)
# M analysis/CROSS_REFERENCE_ANALYSIS.md  (include if substantive)
# M scripts/process_usaspending_305_column.py  (review and commit if complete)
# D create_pm_dashboard_old.py  (commit deletion)
```

**Selective commits:**
```bash
# If process_usaspending_305_column.py is complete:
git add scripts/process_usaspending_305_column.py
git commit -m "feat: Update usaspending processing for 305-column schema"

# Delete old file:
git add create_pm_dashboard_old.py
git commit -m "chore: Remove obsolete dashboard creation script"

# Skip .claude/settings.local.json (personal settings)
```

### Final Status Check
```bash
git status
git log --oneline -5
```

---

## 🟠 TERMINAL D: OpenSanctions Database Merge

### Overview
**What:** Merge OpenSanctions separate database (182K records) into master database
**Status:** Ready to run
**Impact:** Enables sanctions cross-referencing with BIS Entity List, procurement, GLEIF
**Why needed:** Currently only 1,000 of 183K records in master database

### The Gap
**Separate database:** `F:/OSINT_Data/OpenSanctions/processed/sanctions.db` (210MB)
- `entities`: 183,766 records
- `chinese_analysis`: 4,697 records

**Master database:** `F:/OSINT_WAREHOUSE/osint_master.db`
- `opensanctions_entities`: 1,000 records (only 0.5% of available data)
- `bilateral_sanctions_links`: 0 records

**Missing:** 182,766 sanction entities not available for cross-referencing

### Processing Steps

#### Step 1: Verify Source Database
```bash
# Check what's in the OpenSanctions database
python -c "
import sqlite3
conn = sqlite3.connect('F:/OSINT_Data/OpenSanctions/processed/sanctions.db')
cur = conn.cursor()

# Get table list
cur.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
print('Tables:', [row[0] for row in cur.fetchall()])

# Get record counts
cur.execute('SELECT COUNT(*) FROM entities')
print(f'Entities: {cur.fetchone()[0]:,}')

cur.execute('SELECT COUNT(*) FROM chinese_analysis')
print(f'Chinese analysis: {cur.fetchone()[0]:,}')

# Sample entity
cur.execute('SELECT * FROM entities LIMIT 1')
print('Sample columns:', [desc[0] for desc in cur.description])

conn.close()
"
```

#### Step 2: Check if Merge Script Exists
```bash
# Look for existing OpenSanctions processor
ls scripts/processors/opensanctions* scripts/collectors/opensanctions*

# If exists, review it:
cat scripts/processors/opensanctions_merge.py  # or similar

# If doesn't exist, we'll need to create one
```

#### Step 3A: If Script Exists - Run It
```bash
python scripts/processors/opensanctions_merge.py
```

#### Step 3B: If Script Doesn't Exist - Create Quick Merge
```bash
# Create merge script
cat > scripts/processors/merge_opensanctions.py << 'EOF'
#!/usr/bin/env python3
"""
Merge OpenSanctions separate database into master database
"""
import sqlite3
import sys
from pathlib import Path

SOURCE_DB = Path("F:/OSINT_Data/OpenSanctions/processed/sanctions.db")
TARGET_DB = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def merge_opensanctions():
    if not SOURCE_DB.exists():
        print(f"❌ Source database not found: {SOURCE_DB}")
        sys.exit(1)

    if not TARGET_DB.exists():
        print(f"❌ Target database not found: {TARGET_DB}")
        sys.exit(1)

    print(f"Merging OpenSanctions data...")
    print(f"Source: {SOURCE_DB}")
    print(f"Target: {TARGET_DB}")

    # Connect to both databases
    source_conn = sqlite3.connect(SOURCE_DB)
    target_conn = sqlite3.connect(TARGET_DB)

    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()

    # Get source record count
    source_cur.execute("SELECT COUNT(*) FROM entities")
    source_count = source_cur.fetchone()[0]
    print(f"\nSource entities: {source_count:,}")

    # Get target current count
    target_cur.execute("SELECT COUNT(*) FROM opensanctions_entities")
    target_before = target_cur.fetchone()[0]
    print(f"Target before: {target_before:,}")

    # Get schema of source table
    source_cur.execute("PRAGMA table_info(entities)")
    source_schema = {row[1]: row[2] for row in source_cur.fetchall()}
    print(f"\nSource columns: {list(source_schema.keys())}")

    # Get schema of target table
    target_cur.execute("PRAGMA table_info(opensanctions_entities)")
    target_schema = {row[1]: row[2] for row in target_cur.fetchall()}
    print(f"Target columns: {list(target_schema.keys())}")

    # Find common columns
    common_cols = set(source_schema.keys()) & set(target_schema.keys())
    print(f"\nCommon columns ({len(common_cols)}): {sorted(common_cols)}")

    if not common_cols:
        print("❌ No common columns found - schema mismatch!")
        sys.exit(1)

    # Clear existing data to avoid duplicates
    print("\nClearing existing opensanctions_entities...")
    target_cur.execute("DELETE FROM opensanctions_entities")
    target_conn.commit()

    # Merge data
    cols_str = ", ".join(sorted(common_cols))
    placeholders = ", ".join(["?" for _ in common_cols])

    print(f"\nMerging {source_count:,} entities...")
    source_cur.execute(f"SELECT {cols_str} FROM entities")

    batch_size = 10000
    batch = []
    inserted = 0

    for row in source_cur:
        batch.append(row)
        if len(batch) >= batch_size:
            target_cur.executemany(
                f"INSERT INTO opensanctions_entities ({cols_str}) VALUES ({placeholders})",
                batch
            )
            inserted += len(batch)
            print(f"  Inserted {inserted:,}/{source_count:,}...", end='\r')
            batch = []

    # Insert remaining
    if batch:
        target_cur.executemany(
            f"INSERT INTO opensanctions_entities ({cols_str}) VALUES ({placeholders})",
            batch
        )
        inserted += len(batch)

    target_conn.commit()

    # Verify
    target_cur.execute("SELECT COUNT(*) FROM opensanctions_entities")
    target_after = target_cur.fetchone()[0]

    print(f"\n\n✅ Merge complete!")
    print(f"Target before: {target_before:,}")
    print(f"Target after:  {target_after:,}")
    print(f"Added:         {target_after - target_before:,}")

    # Close connections
    source_conn.close()
    target_conn.close()

if __name__ == "__main__":
    merge_opensanctions()
EOF

chmod +x scripts/processors/merge_opensanctions.py
```

#### Step 4: Run the Merge
```bash
python scripts/processors/merge_opensanctions.py
```

**Expected output:**
```
Merging OpenSanctions data...
Source: F:/OSINT_Data/OpenSanctions/processed/sanctions.db
Target: F:/OSINT_WAREHOUSE/osint_master.db

Source entities: 183,766
Target before: 1,000

Source columns: [...]
Target columns: [...]
Common columns (X): [...]

Clearing existing opensanctions_entities...
Merging 183,766 entities...
  Inserted 183,766/183,766...

✅ Merge complete!
Target before: 1,000
Target after:  183,766
Added:         182,766
```

#### Step 5: Verify Cross-Reference Capability
```bash
# Test that we can now cross-reference sanctions with other data
python -c "
import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()

# Example: Find sanctioned entities that appear in USAspending
cur.execute('''
    SELECT DISTINCT
        s.entity_name,
        s.countries,
        COUNT(u.award_id) as contract_count
    FROM opensanctions_entities s
    JOIN usaspending_contracts u
        ON UPPER(u.recipient_name) LIKE '%' || UPPER(s.entity_name) || '%'
    WHERE s.entity_name IS NOT NULL
    GROUP BY s.entity_name
    LIMIT 20
''')

print('Sanctioned entities with US contracts:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[2]} contracts')

conn.close()
"
```

### What This Unlocks
- Cross-reference sanctions with procurement (USAspending, TED)
- Link sanctioned entities to GLEIF corporate registries
- Track sanctioned entities in patent applications
- Identify front companies and aliases
- Supply chain risk assessment

**Estimated time:** 15-20 minutes

---

## 🟡 TERMINAL E: Database Lock Resolution + Sector Policies

### Overview
**What:** Resolve database lock preventing insertion of 30 sector-specific technology strategy documents
**Status:** Blocked on Oct 27 due to database lock
**When resolved:** 5-10 minutes to complete insertion
**Impact:** Completes European technology policy framework (98 total documents)

### The Situation
**Target:** 98 strategic technology policy documents
**Loaded:** 68 documents
  - 36 core technologies (EU + 8 countries)
  - 32 geographic expansion (10 countries)
**Pending:** 30 sector-specific documents
  - Biotech/Life Sciences: 5 docs
  - Space/Satellites: 6 docs
  - Energy (Batteries/Hydrogen): 6 docs
  - Advanced Manufacturing: 4 docs
  - Cloud/Data Infrastructure: 5 docs
  - Advanced Materials: 2 docs
  - Other strategic sectors: 2 docs

### File Ready to Run
```
scripts/collectors/european_sector_specific_technology_strategies.py
```

### Step 1: Check Database Lock Status
```bash
# Check if database is locked
python -c "
import sqlite3
try:
    conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db', timeout=5)
    conn.execute('BEGIN IMMEDIATE')
    print('✅ Database is NOT locked - ready to proceed')
    conn.rollback()
    conn.close()
except sqlite3.OperationalError as e:
    print(f'❌ Database is LOCKED: {e}')
"
```

### Step 2A: If Database is Locked - Find the Lock
```bash
# Check for processes holding the database
tasklist /FI "IMAGENAME eq python.exe" /FO CSV

# On Windows, check what has the file open
# You may need to use Process Explorer or handle.exe from Sysinternals
# Or just identify and close any Python processes working with the database

# Nuclear option if needed (CAREFUL):
# Close all Python processes:
# taskkill /F /IM python.exe
```

### Step 2B: If Database is Not Locked - Run the Script
```bash
python scripts/collectors/european_sector_specific_technology_strategies.py
```

**Expected output:**
```
Loading sector-specific technology strategies...

Processing Biotechnology/Life Sciences (5 documents)...
  ✅ EU Pharmaceutical Strategy for Europe
  ✅ EU Health Technology Assessment Regulation
  ✅ Germany National Bioeconomy Strategy
  ✅ France Health Innovation 2030
  ✅ UK Life Sciences Vision

Processing Space/Satellite Technologies (6 documents)...
  ✅ EU Space Programme 2021-2027
  ✅ EU Secure Connectivity Programme IRIS²
  ✅ Germany Space Strategy 2023
  ✅ France Space Strategy 2030
  ✅ UK National Space Strategy
  ✅ Italy National Aerospace Plan 2023-2025

[... continues for all 30 documents ...]

✅ Complete: 30 sector-specific documents inserted
Total policy documents: 98
```

### Step 3: Verify Total Document Count
```bash
python -c "
import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()

# Get total policy document count
cur.execute('SELECT COUNT(*) FROM technology_policies')
total = cur.fetchone()[0]
print(f'Total policy documents: {total}')

# Break down by country
cur.execute('''
    SELECT country_code, COUNT(*) as count
    FROM technology_policies
    GROUP BY country_code
    ORDER BY count DESC
''')
print('\nBy country:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Break down by document type
cur.execute('''
    SELECT document_type, COUNT(*) as count
    FROM technology_policies
    GROUP BY document_type
    ORDER BY count DESC
''')
print('\nBy type:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
"
```

**Expected results:**
```
Total policy documents: 98

By country:
  EU: 21
  GB: 11
  DE: 9
  FR: 9
  [... etc ...]

By type:
  strategy: 45
  regulation: 12
  directive: 8
  [... etc ...]
```

### What This Completes
- **Geographic coverage:** 18 European countries (EU-level + national)
- **Technology domains:** AI, Quantum, Semiconductors, Cyber, 5G, Digital, Biotech, Space, Energy, Manufacturing, Cloud, Materials
- **Investment mapped:** €900B+ across all domains
- **Regulatory framework:** 9 binding EU regulations + national strategies
- **Ready for text extraction:** All 98 documents have official URLs

**Estimated time:** 5-10 minutes (once lock resolved)

---

## Parallel Execution Strategy

### Recommended Terminal Assignment

**Terminal 1 (Manual - Your Active Work):**
- Policy URL Verification (2-2.5 hours)
- Requires web browsing, human judgment
- Can't be automated

**Terminal 2 (Automated - Long Running):**
```bash
# GLEIF relationship processing (30-45 min)
python scripts/reprocess_gleif_relationships.py
```

**Terminal 3 (Automated - Medium):**
```bash
# OpenSanctions merge (15-20 min)
python scripts/processors/merge_opensanctions.py
```

**Terminal 4 (Quick Tasks):**
```bash
# Git commits (10 min)
git add README.md
git commit -m "docs: Add EU-China bilateral relations platform and BCI framework"

git add scripts/cross_reference_analyzer.py
git commit -m "fix: Update cross_reference_analyzer.py for current database schemas"

# Then handle database lock + sector policies
# Check lock, resolve, run:
python scripts/collectors/european_sector_specific_technology_strategies.py
```

### Execution Order by Priority

**Phase 1: Start Long-Running (5 min setup)**
1. Terminal 2: Start GLEIF processing
2. Terminal 3: Start OpenSanctions merge
3. Terminal 4: Quick git commits

**Phase 2: Manual Work (2-2.5 hours)**
4. Terminal 1: Policy URL verification
   - While automated processes run in background
   - Check Terminal 2 & 3 periodically for completion

**Phase 3: Completion (10 min)**
5. Terminal 4: Database lock + sector policies
6. Verify all tasks complete

---

## Success Criteria

### Terminal A: Policy URLs
- [ ] CSV file updated with 96 verified PDF URLs (or "not available" notes)
- [ ] Import script run successfully
- [ ] Policy processor downloaded all available PDFs
- [ ] Text extraction complete for available documents

### Terminal B: GLEIF
- [ ] gleif_relationships table has ~464,000 records (not 1)
- [ ] gleif_qcc_mapping populated (Chinese corporate registry)
- [ ] gleif_bic_mapping populated (bank identifiers)
- [ ] Can query corporate ownership networks

### Terminal C: Git
- [ ] README.md committed with new sections
- [ ] cross_reference_analyzer.py committed with fixes
- [ ] Other modified files reviewed and committed
- [ ] Git status shows clean working tree

### Terminal D: OpenSanctions
- [ ] opensanctions_entities has ~183,766 records (not 1,000)
- [ ] Can cross-reference with USAspending, TED, GLEIF
- [ ] bilateral_sanctions_links populated if applicable

### Terminal E: Sector Policies
- [ ] Database lock resolved
- [ ] 30 sector-specific documents inserted
- [ ] Total technology_policies count = 98
- [ ] All documents have valid URLs

---

## Emergency Contacts / Notes

### If Database Lock Persists
1. Check `data/ted_production_checkpoint.json` - may be locked by TED processor
2. Check `data/openalex_v4_checkpoint.json` - may be locked by OpenAlex processor
3. Restart all Python processes
4. As last resort: Reboot system

### If Scripts Fail
1. Check Python environment: `python --version` (should be 3.10+)
2. Check database path accessible: `ls -lh F:/OSINT_WAREHOUSE/osint_master.db`
3. Check disk space: `df -h F:/`
4. Review error messages carefully - may need schema adjustments

### If CSV Import Fails
1. Verify CSV format with: `head -5 policy_urls_PRIORITIZED_20251028_180500.csv`
2. Check for encoding issues (should be UTF-8)
3. Verify column headers match expected schema
4. Check for empty verified_pdf_url fields (script should handle gracefully)

---

## Progress Tracking

Use this checklist to track completion:

```
TERMINAL A - Policy URLs:
[ ] Phase 1: EUR-Lex (23 docs) - 30 min
[ ] Phase 2: UK gov (11 docs) - 20 min
[ ] Phase 3: Broken URLs (45 docs) - 60 min
[ ] Phase 4: Other HTML (remaining) - 45 min
[ ] Import verified URLs
[ ] Download PDFs
[ ] Extract text

TERMINAL B - GLEIF:
[ ] Run reprocess_gleif_relationships.py
[ ] Verify 464K relationships loaded
[ ] Process QCC mapping (Chinese registry)
[ ] Process BIC mapping (bank IDs)
[ ] Process ISIN mapping (securities)
[ ] Process OpenCorporates mapping
[ ] Process REPEX (reporting exceptions)

TERMINAL C - Git:
[ ] Commit README.md changes
[ ] Commit cross_reference_analyzer.py fixes
[ ] Review/commit other modified files
[ ] Verify clean git status

TERMINAL D - OpenSanctions:
[ ] Create/verify merge script
[ ] Run merge (183K entities)
[ ] Verify record count
[ ] Test cross-reference queries

TERMINAL E - Sector Policies:
[ ] Check database lock status
[ ] Resolve lock if present
[ ] Run sector strategies script
[ ] Verify 98 total documents
[ ] Celebrate completion! 🎉
```

---

## Estimated Total Time

**Parallel execution (recommended):**
- Manual work (Terminal 1): 2-2.5 hours
- Automated work (Terminals 2-4): Completes in background
- **Total wall-clock time: 2-3 hours**

**Sequential execution (not recommended):**
- Terminal A: 2.5 hours
- Terminal B: 0.75 hours
- Terminal C: 0.17 hours
- Terminal D: 0.33 hours
- Terminal E: 0.17 hours
- **Total: 3.92 hours**

**Savings from parallel: ~1 hour**

---

**Document created:** 2025-10-28 21:30
**Status:** Ready for multi-terminal execution
**Next action:** Open 4 terminals and execute in parallel per strategy above
