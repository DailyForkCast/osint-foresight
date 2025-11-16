# USPTO Patent NULL Data Handling - Explained

## Your Question:

> "Anything less than 50 points - we need to positively prove they are not Chinese. Are they below 50 because it is a company from Scranton Pennsylvania? or is it below 50 because the data fields are empty? We need to know which is which."

This is a **critical distinction**. Here's how we handle it:

---

## Three Categories of <50 Point Patents

### **Category 1: Confirmed NON-Chinese** (data_quality_flag = `NON_CHINESE_CONFIRMED`)
**Patents with actual evidence they are NOT Chinese**

**Examples**:
```
Patent A:
  country = 'US'
  city = 'SCRANTON'
  company = 'GENERAL ELECTRIC'
  → Score: 0 points
  → Flag: NON_CHINESE_CONFIRMED
  → Negative signals: country_US
  → Fields with data: 3/5 (country, city, company)
  ✓ CORRECTLY EXCLUDED - This is American

Patent B:
  country = 'JP'
  city = 'TOKYO'
  company = 'SONY CORPORATION'
  → Score: 0 points
  → Flag: NON_CHINESE_CONFIRMED
  → Negative signals: country_JP
  → Fields with data: 3/5
  ✓ CORRECTLY EXCLUDED - This is Japanese
```

**Negative Signals** (Definitive non-Chinese country codes):
- US, USA
- JP, JPN, JAPAN
- DE, DEU, GERMANY
- KR, KOR, KOREA
- GB, UK
- FR, FRANCE
- CA, CANADA
- IT, ITALY
- ES, SPAIN
- NL, NETHERLANDS
- SE, SWEDEN
- CH, SWITZERLAND
- AU, AUSTRALIA
- IN, INDIA
- BR, BRAZIL

---

### **Category 2: No Data Available** (data_quality_flag = `NO_DATA` or `LOW_DATA`)
**Patents where we can't tell because fields are NULL/empty**

**Examples**:
```
Patent C:
  country = NULL
  city = NULL
  company = NULL
  address = NULL
  postal_code = NULL
  → Score: 0 points
  → Flag: NO_DATA
  → Fields with data: 0/5
  ⚠️ UNKNOWN - Could be Chinese, could be anything, we just don't know

Patent D:
  country = NULL
  city = 'SPRINGFIELD'  (too generic, no Chinese match)
  company = NULL
  → Score: 0 points
  → Flag: LOW_DATA
  → Fields with data: 1/5
  ⚠️ UNCERTAIN - Minimal data, hard to determine
```

**This is the group you're concerned about** - they scored <50 **not because they're proven non-Chinese**, but because **we lack information**.

---

### **Category 3: Uncertain / Potential Detection Miss** (data_quality_flag = `UNCERTAIN_NEEDS_REVIEW`)
**Patents with data, but no clear Chinese OR non-Chinese signals**

**Examples**:
```
Patent E:
  country = 'SG' (Singapore - not in our Chinese or non-Chinese lists)
  city = 'SINGAPORE'
  company = 'ABC TECHNOLOGIES PTE LTD'
  address = '123 Orchard Road'
  → Score: 0 points
  → Flag: UNCERTAIN_NEEDS_REVIEW
  → Fields with data: 4/5
  ⚠️ POTENTIAL MISS - Has data but doesn't match our patterns
  → Could be a Singapore company, or could be Chinese subsidiary

Patent F:
  country = NULL
  city = 'GUANGZHOU'  → +50 points (Chinese city!)
  company = NULL
  → Score: 50 points
  → Wait, this IS ≥50! This would be INCLUDED as MEDIUM confidence
```

Actually Patent F shows the system working - if there's **any** positive Chinese signal, it scores points.

---

## How We Track This

### **New Database Fields**:

```sql
CREATE TABLE uspto_patents_chinese (
    ...
    confidence_score INTEGER,        -- Raw points (0-300+)
    detection_signals TEXT,          -- What triggered inclusion
    data_quality_flag TEXT,          -- NEW: Why <50 patents scored low
    fields_with_data_count INTEGER,  -- NEW: How many fields had data
    ...
)
```

### **Data Quality Flags**:

| Flag | Meaning | Fields Count | Negative Signals |
|------|---------|--------------|------------------|
| `NON_CHINESE_CONFIRMED` | Has US/JP/DE/etc. country code | Any | Yes |
| `NO_DATA` | Completely blank assignee info | 0 | No |
| `LOW_DATA` | Only 1-2 fields populated | 1-2 | No |
| `UNCERTAIN_NEEDS_REVIEW` | 3+ fields but no clear signals | 3+ | No |

---

## Workflow After Processing

### **Step 1: Review NON_CHINESE_CONFIRMED**
```sql
SELECT COUNT(*) FROM uspto_patents_chinese
WHERE data_quality_flag = 'NON_CHINESE_CONFIRMED';
-- Expected: ~4.5M patents (90% of total)
```
✓ These are correctly excluded

### **Step 2: Review NO_DATA / LOW_DATA**
```sql
SELECT COUNT(*) FROM uspto_patents_chinese
WHERE data_quality_flag IN ('NO_DATA', 'LOW_DATA');
-- Expected: ~200K-400K patents (4-8%)
```
⚠️ These are **unknown** - might include Chinese patents we can't detect

**Options**:
1. Accept data limitation (conservative approach)
2. Flag for manual review of sample
3. Cross-reference with other databases (EPO, WIPO)

### **Step 3: Review UNCERTAIN_NEEDS_REVIEW**
```sql
SELECT * FROM uspto_patents_chinese
WHERE data_quality_flag = 'UNCERTAIN_NEEDS_REVIEW'
LIMIT 100;
```
⚠️ These are **potential detection misses** - have data but didn't match our patterns

**Action**: Manual review sample to improve detection rules

---

## Example Queries After Processing

### **Count by Data Quality**:
```sql
SELECT
    data_quality_flag,
    COUNT(*) as count,
    AVG(fields_with_data_count) as avg_fields
FROM uspto_patents_chinese
WHERE confidence_score < 50
GROUP BY data_quality_flag;
```

**Expected Output**:
```
NON_CHINESE_CONFIRMED  | 4,200,000 | 3.2 fields
NO_DATA                |   150,000 | 0.0 fields
LOW_DATA               |   280,000 | 1.4 fields
UNCERTAIN_NEEDS_REVIEW |    50,000 | 3.8 fields
```

### **Sample UNCERTAIN Patents**:
```sql
SELECT
    assignee_name,
    assignee_country,
    assignee_city,
    fields_with_data_count
FROM uspto_patents_chinese
WHERE data_quality_flag = 'UNCERTAIN_NEEDS_REVIEW'
LIMIT 20;
```

This shows us **potential Chinese companies we might have missed**.

---

## Answering Your Question Directly

> "Are they below 50 because it is a company from Scranton Pennsylvania? or is it below 50 because the data fields are empty?"

**Now we can answer precisely**:

1. **Scranton, Pennsylvania** → `NON_CHINESE_CONFIRMED` (has country=US)
2. **Empty data fields** → `NO_DATA` or `LOW_DATA` (0-2 fields populated)
3. **Has data but unclear** → `UNCERTAIN_NEEDS_REVIEW` (3+ fields, no matches)

**The database will tell us exactly which category each patent falls into.**

---

## Validation Checks

### **After processing completes, run**:

```sql
-- Check distribution
SELECT data_quality_flag, COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
FROM uspto_patents_chinese
WHERE confidence_score < 50
GROUP BY data_quality_flag;

-- Sample each category
SELECT * FROM uspto_patents_chinese
WHERE data_quality_flag = 'NO_DATA' LIMIT 10;

SELECT * FROM uspto_patents_chinese
WHERE data_quality_flag = 'UNCERTAIN_NEEDS_REVIEW' LIMIT 10;
```

---

**Status**: Updating script now to include these data quality tracking fields.
