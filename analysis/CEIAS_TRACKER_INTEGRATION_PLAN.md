# CEIAS Academic Tracker Integration Plan
**Date:** 2025-10-23
**Priority:** **HIGH** - Critical data gap identified

---

## Executive Summary

The **Central European Institute of Asian Studies (CEIAS) China-Europe Academic Engagement Tracker** contains precisely the granular partnership data we're missing. This tracker provides:

- **Specific university partnerships** (113 for Slovakia alone)
- **Confucius Institute locations** (3 in Slovakia: Comenius, Slovak Tech, Matej Bel)
- **Military-linked partnerships** (25 PLA-affiliated in Slovakia)
- **Risk assessments** (60%+ high/very high risk in Slovakia)
- **Corporate partnerships** (Huawei, ZTE, Dahua)
- **11+ CEE countries covered** (potentially 33 total)

This directly addresses **3 of our top 6 identified data gaps**:
1. ✅ Sister city relationships
2. ✅ **Confucius Institute comprehensive tracking** (CEIAS has this!)
3. ✅ **University partnership agreements** (CEIAS has this!)
4. ✅ Student mobility (partial - may have data)
5. ✅ Joint funding programs (partial - cooperation frameworks)
6. Institution-level risk assessment (CEIAS has risk scores!)

---

## CEIAS Tracker Overview

### Data Source
- **Provider:** Central European Institute of Asian Studies (CEIAS)
- **URL:** https://academytracker.ceias.eu
- **Coverage:** 11 CEE countries confirmed (Romania, Slovakia, others)
- **Partnership count:** 113+ for Slovakia alone (extrapolate: ~1,000-2,000 total?)
- **Format:** Interactive JavaScript map + country reports
- **Methodology:** Partners from 33 countries collaborated on data collection

### Data Types Available

**1. University Cooperation Agreements**
- Bilateral MoUs between European and Chinese universities
- Academic exchange programs
- Joint research initiatives
- Student exchange agreements

**2. Confucius Institutes**
- Host university locations
- Establishment dates
- Focus areas (language, traditional medicine, policy)
- Operational status (active/closed)

**3. Military-Linked Partnerships**
- Partnerships with PLA-affiliated institutions
- Examples from Slovakia:
  - Slovak Academy of Science ↔ Northwestern Polytechnical University
  - Technical University Zvolen ↔ Nanjing University of Science and Technology
  - University of Žilina ↔ Beijing Institute of Technology
  - Technical University Košice ↔ Beijing Institute of Technology

**4. Corporate Partnerships**
- Huawei university collaborations
- ZTE academic programs
- Dahua technology partnerships

**5. Risk Assessments**
- Categorization: Very high / High / Medium / Low risk
- Transparency metrics (contract publication rates)
- National security concerns flagged

---

## Integration Value

### Fills Critical Data Gaps

**Current State:**
```sql
SELECT COUNT(*) FROM academic_partnerships;  -- Returns: 0
SELECT COUNT(*) FROM cultural_institutions;  -- Returns: 0
```

**Post-CEIAS Integration:**
- academic_partnerships: **1,000-2,000 records** (estimated)
- cultural_institutions: **50-100 Confucius Institutes** (estimated)
- Partnership risk scores for institution-level assessment
- Temporal data (establishment/termination dates)

### Validates Our Findings

**Slovakia Example from CEIAS:**
- 113 partnerships total
- 25 military-linked (22%)
- 3 Confucius Institutes

**Our OpenAlex Data (Slovakia):**
- 56 institutions
- 133,431 collaborative works
- Significant collaboration despite no data on specific partnerships

**Correlation:** CEIAS provides **micro-level** (individual partnerships), we have **macro-level** (publication counts). Combined = comprehensive picture.

### Enables New Analysis

**Currently Impossible:**
❌ Which specific universities have PLA-linked partnerships?
❌ When were Confucius Institutes established/closed?
❌ Which partnerships are high-risk vs. low-risk?
❌ Huawei's specific university collaborations?

**With CEIAS Data:**
✅ Map all PLA-affiliated partnerships by country/university
✅ Create Confucius Institute timeline (openings/closures)
✅ Risk-score institutions for security assessment
✅ Track corporate influence (Huawei, ZTE) in academia

---

## Technical Integration Challenges

### Challenge 1: Data Access

**Problem:** CEIAS tracker is JavaScript-heavy interactive map
- WebFetch cannot render JavaScript applications
- Data not available via public API (as far as we know)
- No bulk download option visible

**Solutions:**
1. **Manual extraction:** Review country-specific reports
   - Slovakia report: https://ceias.eu/chinas-inroads-into-slovak-universities/
   - Romania report: https://ceias.eu/romania-balancing-the-rising-interest-and-challenges-of-china-as-an-academic-partner/
   - Find reports for all 11 countries

2. **Contact CEIAS directly:**
   - Request data sharing for research purposes
   - Explain our intelligence platform integration
   - Offer to cite CEIAS as data source

3. **Browser automation:**
   - Use Selenium/Playwright to interact with JavaScript map
   - Extract partnership data programmatically
   - Requires local browser automation setup

4. **Structured extraction from reports:**
   - Parse PDF/HTML country reports
   - Extract partnership tables
   - Manual entry for critical partnerships

### Challenge 2: Data Structure Mapping

**CEIAS Data Fields (inferred from Slovakia report):**
- European institution name
- Chinese partner institution
- Partnership type (agreement, exchange, research)
- Risk level (Very high / High / Medium / Low)
- Military linkage (Yes/No, which entity)
- Corporate involvement (Huawei, ZTE, etc.)
- Transparency (contract published Y/N)

**Our Database Schema (academic_partnerships table):**
```sql
-- Need to check actual schema
PRAGMA table_info(academic_partnerships);
```

**Mapping Strategy:**
1. Check existing schema
2. Add fields if needed (risk_level, military_linked, contract_transparency)
3. Create partnership_type taxonomy
4. Link to bilateral_events timeline

### Challenge 3: Temporal Data

**CEIAS May Have:**
- Partnership establishment dates
- Confucius Institute opening/closure dates
- Agreement expiration dates

**Integration Plan:**
- Create bilateral_events entries for major partnerships
- Link to temporal analysis (correlate with research collaboration trends)
- Identify partnership terminations post-2020 restrictions

---

## Recommended Approach

### Phase 1: Manual High-Value Extraction (Immediate)

**Action:** Extract data from available country reports
**Priority:** HIGH
**Effort:** 2-4 hours
**Countries:** Slovakia, Romania, + any others with published reports

**Data to Extract:**
1. **Confucius Institutes:**
   - All locations by country
   - Host universities
   - Establishment dates
   - Closure dates (if applicable)
   - Current status

2. **High-Risk Partnerships:**
   - University name (European)
   - Chinese partner
   - Risk classification
   - Military linkage (if PLA-affiliated)

3. **Corporate Partnerships:**
   - Huawei university collaborations
   - ZTE programs
   - Other tech company partnerships

**Output:** Populate academic_partnerships and cultural_institutions tables with ~50-200 critical records

### Phase 2: CEIAS Outreach (Next Session)

**Action:** Contact CEIAS for data sharing
**Priority:** MEDIUM-HIGH
**Effort:** Email + potential follow-up
**Timeline:** 1-2 weeks for response

**Email Template:**
```
Subject: Research Collaboration - EU-China Academic Intelligence Platform

Dear CEIAS Team,

I am developing a comprehensive intelligence platform analyzing EU-China
bilateral relations, including academic collaboration patterns. Your
China-Europe Academic Engagement Tracker is an invaluable resource that
perfectly complements our temporal analysis of 1.56M research publications
from OpenAlex.

Would CEIAS be willing to share the underlying dataset for research purposes?
We would:
- Properly cite CEIAS as the data source
- Share our integrated analysis findings
- Acknowledge CEIAS in any publications/presentations

Our platform currently integrates:
- 124 bilateral diplomatic/economic events (28 EU countries)
- 1.56M EU-China collaborative research works (OpenAlex)
- Temporal analysis (2000-2024)
- Multi-source validation framework

Adding CEIAS partnership data would enable institution-level risk assessment
and validation of our macro-level findings.

Thank you for your consideration.
```

### Phase 3: Systematic Collection (Future)

**Action:** Comprehensive data extraction from all countries
**Priority:** MEDIUM
**Effort:** 8-16 hours (depending on data availability)
**Timeline:** After CEIAS response or if no response after 2 weeks

**Methods:**
1. Review all CEIAS country reports
2. Extract partnership data systematically
3. Create standardized import format
4. Populate database comprehensively

**Target:** 1,000+ partnership records across all countries

---

## Database Schema Validation

### Check Existing Schema

**Tables to Examine:**
1. `academic_partnerships` - University cooperation agreements
2. `cultural_institutions` - Confucius Institutes, cultural centers
3. `bilateral_events` - Add partnership events to timeline

**Required Fields for CEIAS Integration:**

**academic_partnerships:**
- partnership_id (PK)
- european_institution (text)
- european_country (text, FK to bilateral_countries)
- chinese_institution (text)
- partnership_type (agreement/exchange/research/corporate)
- establishment_date (date)
- termination_date (date, nullable)
- status (active/terminated/suspended)
- risk_level (very_high/high/medium/low)
- military_linked (boolean)
- pla_affiliated_entity (text, nullable)
- corporate_partner (text, nullable - Huawei, ZTE, etc.)
- contract_transparency (published/unpublished)
- source_url (text)
- notes (text)

**cultural_institutions:**
- institution_id (PK)
- institution_type (confucius_institute/cultural_center/other)
- european_institution (text - host university)
- european_country (text, FK)
- city (text)
- establishment_date (date)
- closure_date (date, nullable)
- status (active/closed/suspended)
- focus_areas (text - language, medicine, policy, etc.)
- source_url (text)
- notes (text)

---

## Integration Steps

### Step 1: Schema Preparation

```sql
-- Check existing schemas
PRAGMA table_info(academic_partnerships);
PRAGMA table_info(cultural_institutions);

-- Add missing fields if needed
ALTER TABLE academic_partnerships ADD COLUMN risk_level TEXT;
ALTER TABLE academic_partnerships ADD COLUMN military_linked BOOLEAN DEFAULT 0;
ALTER TABLE academic_partnerships ADD COLUMN corporate_partner TEXT;

-- Create indexes for performance
CREATE INDEX idx_partnerships_risk ON academic_partnerships(risk_level);
CREATE INDEX idx_partnerships_military ON academic_partnerships(military_linked);
CREATE INDEX idx_confucius_status ON cultural_institutions(status);
```

### Step 2: Data Extraction Template

**CSV Format for Manual Entry:**
```csv
european_institution,european_country,chinese_institution,partnership_type,risk_level,military_linked,pla_entity,notes,source_url
"Comenius University","SK","Confucius Institute","cultural","medium","false","","Language education","https://ceias.eu/..."
"Slovak Academy of Science","SK","Northwestern Polytechnical University","research","very_high","true","PLA Air Force","Defense research concerns","https://ceias.eu/..."
```

### Step 3: Import Script

**Create:** `import_ceias_partnerships.py`
```python
def import_ceias_data(csv_path):
    # Read CSV
    # Validate data
    # Insert into academic_partnerships
    # Insert into cultural_institutions
    # Create bilateral_events for major partnerships
    # Link citations to CEIAS reports
```

### Step 4: Validation

**After import, verify:**
- Total partnerships imported
- Risk level distribution
- Military-linked percentage
- Confucius Institute count
- Country coverage

---

## Expected Outcomes

### Quantitative

**Database Enhancement:**
- academic_partnerships: 0 → **1,000-2,000 records**
- cultural_institutions: 0 → **50-100 records**
- New bilateral_events: +**50-100 partnership milestones**

**Coverage:**
- 11+ CEE countries with granular partnership data
- 50-100 Confucius Institutes tracked
- 200-400 PLA-affiliated partnerships identified
- 100+ corporate partnerships documented

### Qualitative

**Analysis Capabilities:**
1. **Institution-Level Risk Assessment**
   - Cross-reference OpenAlex collaboration volumes with CEIAS risk scores
   - Identify universities with high collaboration + high risk

2. **Confucius Institute Impact**
   - Correlate CI presence with research collaboration trends
   - Analyze closure impact on bilateral relations

3. **Military-Civil Fusion Mapping**
   - Track PLA-affiliated institution partnerships
   - Identify dual-use research vulnerabilities

4. **Corporate Influence**
   - Map Huawei/ZTE university penetration
   - Cross-reference with technology restrictions timeline

5. **Validation of Macro Findings**
   - Micro-level partnership data validates macro-level publication trends
   - Slovakia: 113 partnerships (CEIAS) + 133K works (OpenAlex) = comprehensive picture

---

## Risk Assessment Enhancement

### Current Gap

**We know:**
- Which countries have high collaboration volumes (UK: 365K works)
- Which technologies are most collaborated on (AI: 12.2%, semiconductors: 8.6%)

**We don't know:**
- Which specific institutions have high-risk partnerships
- Which partnerships involve PLA-affiliated entities
- Which universities host Confucius Institutes

### Post-CEIAS Integration

**We will know:**
- Institution-level risk scores (from CEIAS)
- Specific PLA partnerships (Northwestern Polytechnical, Beijing Institute of Technology, etc.)
- Confucius Institute locations and status
- Corporate influence vectors (Huawei, ZTE)

**Example Analysis:**
```sql
-- High-risk institutions with high collaboration
SELECT
    oe.name as institution,
    oe.country_code,
    oe.works_count,
    ap.risk_level,
    COUNT(ap.partnership_id) as high_risk_partnerships
FROM openalex_entities oe
JOIN academic_partnerships ap ON oe.name = ap.european_institution
WHERE ap.risk_level IN ('very_high', 'high')
  AND oe.works_count > 10000
GROUP BY oe.name, oe.country_code
ORDER BY oe.works_count DESC;
```

**Output:** Universities with massive China collaboration (10K+ works) AND high-risk partnerships

---

## Timeline

### Immediate (Today)
- ✅ Created integration plan
- ⏳ Check academic_partnerships/cultural_institutions schema
- ⏳ Extract Slovakia data from CEIAS report

### Next Session (2025-10-24)
- Draft CEIAS outreach email
- Extract Romania data
- Create import script template
- Begin manual data entry for critical partnerships

### Week 1 (2025-10-24 to 2025-10-31)
- Send CEIAS outreach email
- Extract data from all available country reports
- Populate Confucius Institute data (complete list)
- Identify high-risk PLA-affiliated partnerships

### Week 2+ (Response-dependent)
- If CEIAS shares data: Comprehensive import
- If no response: Continue systematic manual extraction
- Validate imported data
- Generate enhanced risk assessment reports

---

## Success Metrics

**Phase 1 Success (Manual Extraction):**
- ✅ 50+ Confucius Institutes documented
- ✅ 100+ high-risk partnerships identified
- ✅ 11 CEE countries with partial coverage
- ✅ Database tables populated (no longer empty)

**Full Integration Success:**
- ✅ 1,000+ partnerships documented
- ✅ All 11+ CEIAS countries with complete data
- ✅ Institution-level risk scores available
- ✅ Temporal correlation analysis (partnerships ↔ collaboration trends)
- ✅ Military-civil fusion mapping complete

---

## Next Actions

### Priority 1: Schema Check
```bash
python -c "
import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()
print('=== academic_partnerships schema ===')
cur.execute('PRAGMA table_info(academic_partnerships)')
for row in cur.fetchall():
    print(row)
print('\n=== cultural_institutions schema ===')
cur.execute('PRAGMA table_info(cultural_institutions)')
for row in cur.fetchall():
    print(row)
"
```

### Priority 2: Slovakia Data Extraction
**Extract from:** https://ceias.eu/chinas-inroads-into-slovak-universities/
- 3 Confucius Institutes (Comenius, Slovak Tech, Matej Bel)
- 25 PLA-affiliated partnerships
- High-risk partnership list

### Priority 3: Create Import Template
**File:** `import_ceias_slovakia.csv`
**Fields:** european_institution, chinese_partner, type, risk_level, military_linked, source

---

## Conclusion

The CEIAS China-Europe Academic Engagement Tracker is a **critical missing piece** of our intelligence platform. Integration will:

1. **Fill 3 major data gaps** (Confucius Institutes, partnerships, risk assessments)
2. **Enable institution-level analysis** (currently only country/aggregate level)
3. **Validate macro findings** with micro-level partnership data
4. **Enhance security assessment** with PLA-affiliation tracking
5. **Complete the academic layer** of our bilateral framework

**Recommendation:** Begin immediate manual extraction from available reports while pursuing CEIAS data sharing agreement.

---

**Plan Created:** 2025-10-23
**Next Review:** 2025-10-24 (after schema check and Slovakia extraction)
**Status:** READY FOR EXECUTION
