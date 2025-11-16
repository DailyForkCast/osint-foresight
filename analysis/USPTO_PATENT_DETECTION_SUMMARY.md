# USPTO Patent Chinese Detection - Processing Summary
**Start Time**: 2025-10-06 23:25 UTC
**Dataset**: USPTO Patent Filewrapper JSON (2011-2020)
**Size**: 240GB compressed (~5 million patents)

---

## Detection Methodology

### **Multi-Tier Scoring System**

| Tier | Signal | Points | When Applied |
|------|--------|--------|--------------|
| **TIER 1** | Country code (CN, CHN, HK, MO) | 100 | Country field = definitive Chinese code |
| **TIER 1** | Country code (JPX + verified) | 100 | JPX code + Chinese city confirmation |
| **TIER 1** | Chinese postal code (6-digit) | 60 | Postal code matches 100000-999999 format |
| **TIER 2** | Known PRC company (45+ entities) | 80 | Company name matches Huawei, ZTE, Alibaba, etc. |
| **TIER 2** | Major Chinese city (43 cities) | 50 | City = Beijing, Shanghai, Shenzhen, etc. |
| **TIER 3** | Address contains "CHINA" | 30 | Address field mentions China |
| **TIER 4** | Chinese province (27 provinces) | 40 | Province name in address |
| **TIER 4** | Tech hub district (11 districts) | 25 | District = Haidian, Pudong, Nanshan, etc. |
| **TIER 4** | Chinese street pattern | 15 | Street name ends in Lu, Jie, Dadao, etc. |
| **TIER 4** | +86 phone number | 50 | Phone starts with +86 or 86 |
| **TIER 5** | Chinese inventors | 20 each | Inventor country = CN/CHN/HK/MO (max 60) |

### **Confidence Thresholds**

- **≥100 points** = VERY HIGH confidence
- **70-99 points** = HIGH confidence
- **50-69 points** = MEDIUM confidence
- **<50 points** = Excluded (LOW confidence)

**Inclusion Threshold**: 50 points minimum

---

## NULL Data Handling

### **Key Design Principle**: Only score when data MATCHES Chinese patterns

**Examples**:

✅ **Correct Inclusions**:
```
Patent A: country=CN, city=NULL, company=NULL
  → Score: 100 (country_CN)
  → Confidence: VERY_HIGH ✓

Patent B: country=NULL, city=BEIJING, company=NULL
  → Score: 50 (city_BEIJING)
  → Confidence: MEDIUM ✓

Patent C: country=NULL, city=NULL, company=HUAWEI
  → Score: 80 (company_HUAWEI)
  → Confidence: HIGH ✓

Patent D: country=NULL, city=SHENZHEN, postal=518129
  → Score: 110 (city_SHENZHEN + postal_518129)
  → Confidence: VERY_HIGH ✓
```

❌ **Correct Exclusions**:
```
Patent E: country=NULL, city=NULL, company=NULL, address=NULL
  → Score: 0 (no matching signals)
  → Excluded ✓

Patent F: country=JP, city=TOKYO, company=SONY
  → Score: 0 (Japanese entity)
  → Excluded ✓

Patent G: country=NULL, city=NEW YORK, company=IBM
  → Score: 0 (US entity)
  → Excluded ✓
```

### **How NULL vs. Non-Match is Handled**:

1. **Country field**:
   - `country = 'CN'` → +100 points ✓
   - `country = NULL` → 0 points (no penalty, check other signals)
   - `country = 'US'` → 0 points (definitive non-match)

2. **City field**:
   - `city = 'BEIJING'` → +50 points ✓
   - `city = NULL` → 0 points (no penalty)
   - `city = 'NEW YORK'` → 0 points (non-Chinese city)

3. **Company name**:
   - `company = 'HUAWEI TECHNOLOGIES'` → +80 points ✓
   - `company = NULL` → 0 points (no penalty)
   - `company = 'APPLE INC'` → 0 points (non-Chinese company)

**Result**: Patents only reach 50+ points if they have ACTUAL Chinese indicators, not just missing data.

---

## Expected Results

### **Baseline Estimates** (from known USPTO data):

| Year | Estimated Chinese Patents | % of Total USPTO |
|------|---------------------------|------------------|
| 2011 | 1,500-2,000 | ~0.4% |
| 2012 | 2,000-2,500 | ~0.5% |
| 2013 | 2,500-3,000 | ~0.5% |
| 2014 | 3,000-4,000 | ~0.7% |
| 2015 | 4,000-5,000 | ~0.9% |
| 2016 | 5,000-7,000 | ~1.2% |
| 2017 | 7,000-9,000 | ~1.5% |
| 2018 | 9,000-12,000 | ~2.0% |
| 2019 | 12,000-15,000 | ~2.5% |
| 2020 | 15,000-18,000 | ~3.0% |
| **Total** | **60,000-80,000** | **~1.5% avg** |

### **Signal Distribution (Expected)**:

**Primary Detection Signals** (expect 80%+ of matches):
- Country codes (CN/CHN/HK): 65-70% of matches
- Chinese cities: 25-30% of matches
- Known companies: 15-20% of matches

**Supplementary Signals** (expect 20-30% of matches):
- Postal codes: 10-15%
- Address contains "CHINA": 15-20%
- Provinces: 10-12%
- Chinese inventors: 30-40% (but rarely sole signal)

**Multi-Signal Validation**:
- Single signal: 60-70% of matches
- 2+ signals: 30-35% of matches
- 3+ signals: 5-10% of matches (highest confidence)

---

## Processing Status

**Current Status**: RUNNING (Background process ID: 89332d)

**Processing Sequence**:
1. ✓ Extract 2011.json from ZIP (19GB)
2. ⏳ Parse 493,318 patents from 2011
3. ⏳ Detect Chinese entities using multi-signal scoring
4. ⏳ Save to osint_master.db
5. ⏳ Repeat for 2012-2020

**Estimated Completion**: 2-3 hours total (~15 min per year)

**Output Files**:
- `F:/OSINT_WAREHOUSE/osint_master.db` → `uspto_patents_chinese` table
- `C:/Projects/OSINT - Foresight/analysis/uspto_patent_chinese_stats.json` → Statistics by year
- `C:/Projects/OSINT - Foresight/analysis/uspto_patent_processing_log.txt` → Full processing log

---

## Database Schema

```sql
CREATE TABLE uspto_patents_chinese (
    application_number TEXT PRIMARY KEY,  -- USPTO application number
    patent_number TEXT,                   -- Granted patent number (if issued)
    filing_date TEXT,                     -- YYYY-MM-DD format
    grant_date TEXT,                      -- YYYY-MM-DD format (NULL if not granted)
    title TEXT,                           -- Invention title
    status TEXT,                          -- "Patented Case", "Abandoned", etc.
    assignee_name TEXT,                   -- Company/entity name
    assignee_country TEXT,                -- Country code
    assignee_city TEXT,                   -- City name
    confidence TEXT,                      -- VERY_HIGH, HIGH, MEDIUM
    confidence_score INTEGER,             -- Raw points (50-300+ range)
    detection_signals TEXT,               -- Comma-separated signal list
    year INTEGER,                         -- Filing year (2011-2020)
    processed_date TEXT                   -- ISO 8601 timestamp
)
```

**Indexes** (to be created after processing):
```sql
CREATE INDEX idx_confidence ON uspto_patents_chinese(confidence);
CREATE INDEX idx_year ON uspto_patents_chinese(year);
CREATE INDEX idx_assignee_name ON uspto_patents_chinese(assignee_name);
CREATE INDEX idx_assignee_city ON uspto_patents_chinese(assignee_city);
```

---

## Validation Strategy

### **Post-Processing Checks** (to run when complete):

1. **Known Entity Verification**:
   - Search for "HUAWEI" → Should find 500-1,000+ patents
   - Search for "ZTE" → Should find 200-400+ patents
   - Search for "TENCENT" → Should find 100-200+ patents

2. **Geographic Distribution**:
   - Beijing should be #1 city (30-40% of matches)
   - Shanghai should be #2 city (20-25%)
   - Shenzhen should be #3 city (15-20%)

3. **Growth Trajectory**:
   - Year-over-year growth should be 20-35%
   - 2020 count should be ~10x 2011 count

4. **Confidence Distribution**:
   - VERY_HIGH: 60-70% of matches
   - HIGH: 25-30% of matches
   - MEDIUM: 5-10% of matches

5. **False Positive Check**:
   - Random sample 100 patents from each confidence level
   - Manual verification should show >95% accuracy for VERY_HIGH
   - Manual verification should show >85% accuracy for HIGH

---

## Comparison to Previous Analysis

### **USPTO Trademark Database (1823-2006)** ← Old Analysis
- Total: 2.8M trademarks
- Chinese: 1,500-2,000 (PRC mainland only)
- Issues: 56% NULL country, Taiwan/ROC mixed, pre-modern era

### **USPTO Patent Database (2011-2020)** ← Current Analysis
- Total: ~5M patents
- Chinese: 60,000-80,000 expected (40-50x more)
- Quality: Modern data, complete fields, includes patent boom era

**Key Differences**:
- Patents vs. Trademarks (different entity types)
- 2011-2020 vs. 1823-2006 (modern vs. historical)
- Complete vs. sparse data (better field coverage)
- Patent boom era vs. pre-boom (captures China's rise)

---

**Analysis By**: Claude (Anthropic) + OSINT Foresight Team
**Processing Status**: ⏳ IN PROGRESS
**Last Updated**: 2025-10-06 23:30 UTC
