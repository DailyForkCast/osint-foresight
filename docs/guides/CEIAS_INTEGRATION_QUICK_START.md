# CEIAS Tracker Integration - Quick Start
**Status:** ✅ **READY TO BEGIN** - Tables exist, schemas perfect, just need data

---

## Current State

### Database Tables: ✅ READY

**academic_partnerships:**
- Schema: ✅ Excellent (24 fields including military_involvement, strategic_concerns)
- Records: **0** (EMPTY - needs CEIAS data)
- Key fields match CEIAS data perfectly:
  - `military_involvement` → PLA-affiliated partnerships
  - `strategic_concerns` → CEIAS risk assessments
  - `technology_transfer_concerns` → Dual-use research
  - `partnership_type`, `agreement_date`, `status` → All needed fields

**cultural_institutions:**
- Schema: ✅ Excellent (32 fields including academic_freedom_concerns)
- Records: **0** (EMPTY - needs Confucius Institute data)
- Perfect for CEIAS Confucius Institute tracking:
  - `institution_type` → "confucius_institute"
  - `established_date`, `closure_date` → Timeline tracking
  - `academic_freedom_concerns`, `government_scrutiny` → Risk flags
  - `host_institution` → University locations

---

## CEIAS Data Available

### Confirmed Countries (from search)
1. **Slovakia** - 113 partnerships, 3 Confucius Institutes, 25 PLA-linked
2. **Romania** - Academic cooperation frameworks documented
3. **+9 more CEE countries** (total 11 confirmed)
4. **Potentially 33 countries** (per project coordinator info)

### Data Types in CEIAS
1. ✅ University partnerships (maps to academic_partnerships)
2. ✅ Confucius Institutes (maps to cultural_institutions)
3. ✅ PLA-affiliated partnerships (military_involvement = TRUE)
4. ✅ Risk assessments (strategic_concerns = TRUE)
5. ✅ Corporate partnerships (Huawei, ZTE in cooperation_areas)

---

## Immediate Actions

### Action 1: Extract Slovakia Data (30 minutes)

**Source:** https://ceias.eu/chinas-inroads-into-slovak-universities/

**Data to extract:**

**Confucius Institutes (3):**
```
Comenius University, Bratislava
Slovak University of Technology, Bratislava
Matej Bel University, Banská Bystrica
```

**PLA-Affiliated Partnerships (25):**
```
Slovak Academy of Science ↔ Northwestern Polytechnical University
Technical University Zvolen ↔ Nanjing University of Science & Technology
University of Žilina ↔ Beijing Institute of Technology
Technical University Košice ↔ Beijing Institute of Technology
... (21 more to extract from report)
```

### Action 2: Create Import Script (15 minutes)

**File:** `import_ceias_slovakia.py`

```python
#!/usr/bin/env python3
import sqlite3
from datetime import date

conn = sqlite3.connect("F:/OSINT_WAREHOUSE/osint_master.db")

# Confucius Institutes
confucius_institutes = [
    {
        'institution_id': 'CI_SK_COMENIUS',
        'country_code': 'SK',
        'institution_type': 'confucius_institute',
        'institution_name': 'Confucius Institute at Comenius University',
        'host_institution': 'Comenius University',
        'location_city': 'Bratislava',
        'status': 'unknown',  # Need to verify if still active
        'academic_freedom_concerns': True,
        'source_url': 'https://ceias.eu/chinas-inroads-into-slovak-universities/'
    },
    # Add other 2 CIs...
]

# PLA Partnerships
pla_partnerships = [
    {
        'partnership_id': 'SK_SAS_NPU',
        'country_code': 'SK',
        'foreign_institution': 'Slovak Academy of Science',
        'chinese_institution': 'Northwestern Polytechnical University',
        'partnership_type': 'research_cooperation',
        'military_involvement': True,
        'strategic_concerns': True,
        'controversy_notes': 'PLA Air Force affiliation - defense research concerns',
        'source_url': 'https://ceias.eu/chinas-inroads-into-slovak-universities/'
    },
    # Add other 24 PLA partnerships...
]

# Insert data...
for ci in confucius_institutes:
    conn.execute("""
        INSERT INTO cultural_institutions
        (institution_id, country_code, institution_type, institution_name,
         host_institution, location_city, status, academic_freedom_concerns, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ci['institution_id'], ci['country_code'], ci['institution_type'],
          ci['institution_name'], ci['host_institution'], ci['location_city'],
          ci['status'], ci['academic_freedom_concerns'], ci['source_url']))

conn.commit()
```

### Action 3: Validate Import (5 minutes)

```sql
-- Check imports
SELECT COUNT(*) FROM cultural_institutions WHERE country_code = 'SK';
-- Expected: 3 (Confucius Institutes)

SELECT COUNT(*) FROM academic_partnerships
WHERE country_code = 'SK' AND military_involvement = TRUE;
-- Expected: 25 (PLA partnerships)
```

---

## Slovakia Data Extraction Template

### Confucius Institutes

| Institution ID | Host University | City | Status | Notes |
|----------------|-----------------|------|--------|-------|
| CI_SK_COMENIUS | Comenius University | Bratislava | ? | Language & culture |
| CI_SK_TECH | Slovak University of Technology | Bratislava | ? | Tech focus |
| CI_SK_MATEJ_BEL | Matej Bel University | Banská Bystrica | ? | Regional focus |

### High-Risk PLA Partnerships

| European Institution | Chinese Partner | PLA Affiliation | Risk Level |
|----------------------|-----------------|----------------|------------|
| Slovak Academy of Science | Northwestern Polytechnical University | PLA Air Force | Very High |
| Technical University Zvolen | Nanjing University of Science & Tech | PLA Ground Force | Very High |
| University of Žilina | Beijing Institute of Technology | PLA | Very High |
| Technical University Košice | Beijing Institute of Technology | PLA | Very High |

*Need to extract remaining 21 partnerships from full report*

---

## Integration Impact

### Before CEIAS Integration
```
SELECT COUNT(*) FROM academic_partnerships;  → 0
SELECT COUNT(*) FROM cultural_institutions;  → 0
```

### After Slovakia Integration (minimal)
```
SELECT COUNT(*) FROM academic_partnerships;  → 25+
SELECT COUNT(*) FROM cultural_institutions;  → 3
```

### After Full CEIAS Integration (11 countries)
```
SELECT COUNT(*) FROM academic_partnerships;  → 1,000-2,000
SELECT COUNT(*) FROM cultural_institutions;  → 50-100
```

---

## Validation Against Our Findings

### Slovakia: Micro (CEIAS) + Macro (OpenAlex)

**CEIAS Data (Micro-level):**
- 113 partnerships total
- 3 Confucius Institutes
- 25 PLA-affiliated (22% of total)
- 60%+ high/very high risk

**Our OpenAlex Data (Macro-level):**
- 56 Slovak institutions tracked
- 133,431 collaborative research works
- 898,554 total citations
- Active collaboration despite no partnership details

**Combined Intelligence:**
- **Quantity:** 133K research works published
- **Quality concern:** 25 PLA partnerships (22% military-linked)
- **Risk:** 60%+ partnerships high risk
- **Cultural influence:** 3 Confucius Institutes

**Conclusion:** High collaboration volume + significant military links + cultural influence = **comprehensive China engagement** in Slovakia

---

## Next Steps Checklist

- [ ] Extract Slovakia Confucius Institute data (3 records)
- [ ] Extract Slovakia PLA partnerships (25 records)
- [ ] Create import script `import_ceias_slovakia.py`
- [ ] Run import and validate
- [ ] Update SESSION_SUMMARY with CEIAS integration
- [ ] Repeat for Romania (next country)
- [ ] Draft CEIAS data sharing request email
- [ ] Continue systematic extraction for all 11 countries

---

## Files Created
- ✅ `analysis/CEIAS_TRACKER_INTEGRATION_PLAN.md` - Comprehensive plan
- ✅ `CEIAS_INTEGRATION_QUICK_START.md` - This file (quick reference)
- ⏳ `import_ceias_slovakia.py` - Next to create

---

**Status:** READY TO BEGIN SLOVAKIA DATA EXTRACTION
**Estimated time:** 1 hour for Slovakia complete integration
**Priority:** HIGH - Fills critical data gap identified in validation
