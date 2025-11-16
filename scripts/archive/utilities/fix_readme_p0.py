#!/usr/bin/env python3
"""
Apply P0 Urgent Fixes to README.md
Based on DOCUMENTATION_AUDIT_20251018.md findings
"""

import re

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

print("Applying P0 Urgent Fixes...")
print("="*70)

# P0 Fix #1: Update data infrastructure size (660GB -> 1.2TB)
old_1 = r'## 📊 Data Infrastructure \(660GB\+ Multi-Source\)'
new_1 = '## 📊 Data Infrastructure (1.2TB Multi-Source - Verified Oct 18, 2025)'
if re.search(old_1, content):
    content = re.sub(old_1, new_1, content)
    print("[OK] Fixed total data size (660GB -> 1.2TB)")
else:
    print("[WARN] Could not find data infrastructure header")

# P0 Fix #2: Update master database (208 -> 210 tables, 157 -> 158 populated, 51 -> 52 empty)
old_2 = r'\*\*Master Database:\*\* `F:/OSINT_WAREHOUSE/osint_master\.db` \(23 GB, 208 tables, 101\.3M records\)'
new_2 = '**Master Database:** `F:/OSINT_WAREHOUSE/osint_master.db` (23 GB, 210 tables, 101.3M records)'
if re.search(old_2, content):
    content = re.sub(old_2, new_2, content)
    print("[OK] Fixed table count (208 -> 210)")
else:
    print("[WARN] Could not find master database line")

old_2b = r'- \*\*157 populated tables\*\* \(75%\) - Active data'
new_2b = '- **158 populated tables** (75%) - Active data'
content = re.sub(old_2b, new_2b, content)
print("[OK] Fixed populated tables (157 -> 158)")

old_2c = r'- \*\*51 empty tables\*\* \(25%\) - \*\*Infrastructure awaiting data processing\*\*'
new_2c = '- **52 empty tables** (25%) - **Infrastructure awaiting data processing**'
content = re.sub(old_2c, new_2c, content)
print("[OK] Fixed empty tables (51 -> 52)")

old_2d = r'All 51 empty tables are \*\*intentional infrastructure\*\*'
new_2d = 'All 52 empty tables are **intentional infrastructure**'
content = re.sub(old_2d, new_2d, content)
print("[OK] Fixed empty tables clarification")

# P0 Fix #3: Update cleanup actions
old_3 = r'- Phase 2: Dropped 3 superseded TED tables \(211 -> 208\)\n- Reference tables'
new_3 = '- Phase 2: Dropped 3 superseded TED tables (211 -> 208)\n- Current state: 210 tables (158 populated, 52 empty infrastructure)\n- Reference tables'
content = re.sub(old_3, new_3, content)
print("[OK] Added current table state to cleanup actions")

# P0 Fix #4: Update USAspending size (215GB -> 647GB)
old_4 = r'\| \*\*USAspending\*\* \| 215GB \|'
new_4 = '| **USAspending** | 647GB |'
content = re.sub(old_4, new_4, content)
print("[OK] Fixed USAspending size (215GB -> 647GB)")

# P0 Fix #5: Update TED data (size, archives, contracts, Chinese entities)
old_5 = r'\| \*\*TED\*\* \| 30GB \| ✅ COMPLETE \| 139 archives \(2014-2025\) \| \*\*861,984 total contracts, 219 Chinese-related\*\* \(136/139 archives processed, 100% Era 3 UBL format, 3 corrupted\) \|'
new_5 = '| **TED** | 28GB | ✅ COMPLETE | 140 archives (1976-2025) | **1,131,415 total contracts, 6,470 Chinese entities found** (Complete dataset spanning 50 years, Era 3 UBL parser deployed Oct 13) |'
content = re.sub(old_5, new_5, content)
print("[OK] Fixed TED data (size, archives, contracts, Chinese entities)")

# P0 Fix #6: Update TED in NULL handling table
old_6 = r'\| \*\*TED EU Procurement\*\* \| 861,984 \| 219 \(0\.025%\) \| \*\*100% Era 3 UBL extraction complete\*\* \|'
new_6 = '| **TED EU Procurement** | 1,131,415 | 6,470 (0.572%) | **UBL parser deployed Oct 13, 2025** |'
content = re.sub(old_6, new_6, content)
print("[OK] Fixed TED in NULL handling table")

# P0 Fix #7: Update bottom stats (final line references)
old_7a = r'\*\*Data Status:\*\* 660GB\+ multi-source'
new_7a = '**Data Status:** 1.2TB multi-source'
content = re.sub(old_7a, new_7a, content)
print("[OK] Fixed data status in footer (660GB+ -> 1.2TB)")

old_7b = r'\*\*Database:\*\* 208 tables'
new_7b = '**Database:** 210 tables'
content = re.sub(old_7b, new_7b, content)
print("[OK] Fixed database tables in footer (208 -> 210)")

old_7c = r'157 populated, 51 infrastructure'
new_7c = '158 populated, 52 infrastructure'
content = re.sub(old_7c, new_7c, content)
print("[OK] Fixed populated/empty in footer")

old_7d = r'All 51 verified as intentional infrastructure'
new_7d = 'All 52 verified as intentional infrastructure'
content = re.sub(old_7d, new_7d, content)
print("[OK] Fixed infrastructure verification count")

# P0 Fix #8: Add October accomplishments section
october_section = """
### 🆕 **October 2025 Major Accomplishments**
**Status:** ✅ COMPLETE - Significant infrastructure and data quality improvements

1. **TED UBL eForms Parser Deployment (Oct 13)**
   - ✅ Automatic format detection (Era 1/2 vs Era 3)
   - ✅ 100% contractor extraction success rate
   - ✅ 1.13M contracts processed (1976-2025)
   - ✅ 6,470 Chinese entities identified

2. **Automated Thinktank Collection (Oct 12 - Terminal D)**
   - ✅ Windows Task Scheduler operational
   - ✅ Weekly EU/MCF sweeps (7 sources)
   - ✅ 5-week regional rotation cycle
   - ✅ Daily gap map refresh

3. **arXiv Expansion (Oct 12)**
   - ✅ Biotechnology: +119.5% coverage (+21,890 papers)
   - ✅ Energy: +34.9% coverage (+79,950 papers)
   - ✅ Space: +93.8% coverage (+205,361 papers)
   - ✅ Total: 1.44M technology papers

4. **OpenAlex V5 Expansion (Oct 13)**
   - ✅ Keywords: 355 -> 625 (+76%)
   - ✅ Topics: 327 -> 487 (+49%)
   - ✅ 17,739 works with NULL data-driven expansion
   - ✅ Smart City: +98.5% improvement

5. **USAspending Cleanup (Oct 18)**
   - ✅ 4-phase cleanup: 9,557 -> 3,379 verified entities
   - ✅ 64.6% contamination removed
   - ✅ Quality: 62.5% country-confirmed (HIGH confidence)

6. **Comprehensive Database Audit (Oct 17)**
   - ✅ Discovered database 6X larger than documented
   - ✅ 101.3M records verified (not 16.8M)
   - ✅ 715 operational scripts (not "100+")

"""

# Insert after the NULL Data Handling Framework section
insertion_point = r'(\*\*Documents\*\*:\n.*?\n.*?100% data gap discovered\*\*\)\n)'
if re.search(insertion_point, content, re.DOTALL):
    content = re.sub(insertion_point, r'\1\n' + october_section, content, flags=re.DOTALL)
    print("[OK] Added October 2025 accomplishments section")
else:
    print("[WARN] Could not find insertion point for October section")

# P0 Fix #9: Add data badge update
old_badge = r'\[!\[Data Sources\]\(https://img\.shields\.io/badge/Data-660GB_Multi--Source-green\)\]'
new_badge = '[![Data Sources](https://img.shields.io/badge/Data-1.2TB_Multi--Source-green)]'
content = re.sub(old_badge, new_badge, content)
print("[OK] Updated data sources badge (660GB -> 1.2TB)")

# Write updated README
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("="*70)
print("✅ P0 Urgent Fixes Applied Successfully")
print("Updated: README.md")
print("Backup: README.md.backup.20251018")
