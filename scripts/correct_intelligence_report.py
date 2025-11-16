#!/usr/bin/env python3
"""
Apply corrections to FINAL_COMPREHENSIVE_INTELLIGENCE_REPORT.md
Based on DATA_VALIDATION_REPORT_20251006.md findings
"""

import re

REPORT_PATH = "C:/Projects/OSINT - Foresight/analysis/FINAL_COMPREHENSIVE_INTELLIGENCE_REPORT.md"

print("="*80)
print("CORRECTING INTELLIGENCE REPORT")
print("="*80)

# Read current report
with open(REPORT_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"\nOriginal file size: {len(content):,} characters")

# Track changes
changes = []

# 1. Update executive summary table
old_table = '''| **TED (EU Procurement)** | 367,326 contractors | **30** (CN+HK confirmed) | 2 defense SOEs (NUCTECH) |
| **USPTO (Patents)** | 2.8M assignees | **8,381** Chinese assignees | 154 critical SOE patents |
| **EPO (EU Patents)** | 80,817 patents | **80,817** Chinese patents | 24,917 dual-use tech |
| **GLEIF (Corporate LEI)** | 106,883 entities | **106,883** Chinese entities | 4,236 defense indicators |'''

new_table = '''| **TED (EU Procurement)** | 367,326 contractors (full) | **30** (CN+HK confirmed) | 2 defense SOEs (NUCTECH) |
| **USPTO (Patents)** | 2.8M assignees (full) | **5,245** Chinese assignees (0.19%) | 154 critical SOE patents |
| **EPO (EU Patents)** | 80,817 patents (CN subset) | **80,817** Chinese patents | 24,917 dual-use tech |
| **GLEIF (Corporate LEI)** | 106,883 entities (CN subset) | **106,883** Chinese entities | 4,236 defense indicators |'''

if old_table in content:
    content = content.replace(old_table, new_table)
    changes.append("Executive summary table updated")
else:
    print("⚠️  WARNING: Executive summary table not found")

# 2. Update USPTO section (Part 2)
old_uspto = '''### Total Chinese Patent Activity:
- **8,381 Chinese assignees** with USPTO patents
- **157 PRC SOE patents identified**'''

new_uspto = '''### Total Chinese Patent Activity:
- **5,245 Chinese assignees** with USPTO patents (0.19% of 2.8M total)
- Ranks ~7th globally (behind Japan: 549K, Germany: 175K, France: 69K)
- **154 PRC SOE assignees identified** (Huawei: 54, ZTE: 100)

**NOTE**: Multi-signal detection across country codes, cities, company names, addresses, and postal codes. See CHINESE_ENTITY_DETECTION_GUIDE.md for methodology.'''

if old_uspto in content:
    content = content.replace(old_uspto, new_uspto)
    changes.append("USPTO section updated with correct count and methodology note")
else:
    print("⚠️  WARNING: USPTO section not found")

# 3. Add scope note to EPO section
old_epo_header = '''## PART 3: EUROPEAN PATENT OFFICE (EPO) - CHINESE PATENT FILINGS

### Total Chinese Patent Activity in Europe:'''

new_epo_header = '''## PART 3: EUROPEAN PATENT OFFICE (EPO) - CHINESE PATENT FILINGS

**NOTE**: This is a pre-filtered Chinese patent database (80,817 records), not the full EPO database.

### Total Chinese Patent Activity in Europe:'''

if old_epo_header in content:
    content = content.replace(old_epo_header, new_epo_header)
    changes.append("EPO scope note added")
else:
    print("⚠️  WARNING: EPO header not found")

# 4. Add scope note to GLEIF section
old_gleif_header = '''## PART 4: GLEIF CORPORATE ENTITIES - CHINESE LEGAL ENTITY IDENTIFIERS

### Total Chinese Corporate Presence:'''

new_gleif_header = '''## PART 4: GLEIF CORPORATE ENTITIES - CHINESE LEGAL ENTITY IDENTIFIERS

**NOTE**: This is a pre-filtered Chinese entity database (106,883 records), not the full GLEIF database.

### Total Chinese Corporate Presence:'''

if old_gleif_header in content:
    content = content.replace(old_gleif_header, new_gleif_header)
    changes.append("GLEIF scope note added")
else:
    print("⚠️  WARNING: GLEIF header not found")

# 5. Update data quality section
old_quality = '''✅ **USPTO Patents**: 2.8M assignees, 12.7M case files
✅ **EPO Patents**: 80,817 Chinese patents - **FULLY ANALYZED**
✅ **GLEIF Corporate**: 106,883 Chinese entities - **FULLY ANALYZED**'''

new_quality = '''✅ **USPTO Patents**: 2.8M assignees (full database), 5,245 Chinese (0.19%) - multi-signal detection
✅ **EPO Patents**: 80,817 patents (Chinese-only subset) - **FULLY ANALYZED**
✅ **GLEIF Corporate**: 106,883 entities (Chinese-only subset) - **FULLY ANALYZED**'''

if old_quality in content:
    content = content.replace(old_quality, new_quality)
    changes.append("Data quality section updated")
else:
    print("⚠️  WARNING: Data quality section not found")

# 6. Update conclusion totals
old_conclusion = '''**Total PRC Footprint Across All Systems**:
- **30 confirmed** EU procurement contractors (TED)
- **8,381 Chinese** USPTO patent assignees (US)
- **80,817 Chinese** EPO patent applicants (Europe) **← NEW**
- **106,883 Chinese** corporate entities with LEIs **← NEW**
- **4,236 defense-linked** entities globally active **← NEW**
- **6,344 Chinese** research entities (OpenAlex)
- **411 Chinese** organizations in EU research programs (CORDIS)

**Combined Total**: **202,552 distinct Chinese entities** identified across Western systems'''

new_conclusion = '''**Total PRC Footprint Across All Systems**:
- **30 confirmed** EU procurement contractors (TED - full database)
- **5,245 Chinese** USPTO patent assignees (US - full database, 0.19%)
- **80,817 Chinese** EPO patent applicants (Chinese subset database)
- **106,883 Chinese** corporate entities with LEIs (Chinese subset database)
- **4,236 defense-linked** entities globally active
- **6,344 Chinese** research entities (OpenAlex)
- **411 Chinese** organizations in EU research programs (CORDIS)

**Combined Total**: **197,309 distinct Chinese entities** identified across Western systems

**NOTE**: EPO and GLEIF figures represent complete Chinese subsets; TED and USPTO represent findings from full multi-national databases.'''

if old_conclusion in content:
    content = content.replace(old_conclusion, new_conclusion)
    changes.append("Conclusion totals updated (202,552 → 197,309)")
else:
    print("⚠️  WARNING: Conclusion section not found")

# Write corrected report
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n{'='*80}")
print("CORRECTIONS APPLIED:")
print('='*80)
for i, change in enumerate(changes, 1):
    print(f"{i}. {change}")

print(f"\nUpdated file size: {len(content):,} characters")
print(f"\nChanges made: {len(changes)}")
print("\n✅ REPORT CORRECTED SUCCESSFULLY")
print("="*80)
