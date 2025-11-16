# Chinese Company Definition - Detection Methodology
## How We Identify Chinese Entities

**Date**: 2025-10-18
**Script**: `process_usaspending_305_column.py`

---

## Current Definition

A company is classified as **"Chinese"** if the recipient name or vendor name contains:

### 1. Chinese City Names (Geographic Patterns)
```python
'beijing', 'shanghai', 'guangzhou', 'shenzhen',
'chongqing', 'tianjin', 'wuhan', "xi'an",
'hangzhou', 'nanjing', 'chengdu', 'dalian'
```

**Examples**:
- Beijing Jieyuan Tianyu Petrochemical Company
- Shanghai Electric Group
- Shenzhen Feiyue Dianqi Shebei

### 2. Country/Identity Keywords
```python
'china', 'chinese', 'sino'
```

**Examples**:
- China Way Logistics Co., Ltd.
- Chinese Academy of Sciences
- Sino-American Pharmaceuticals

### 3. Known Major Chinese Companies
```python
'huawei', 'zte', 'alibaba', 'tencent', 'baidu',
'lenovo', 'haier', 'xiaomi', 'byd', 'geely'
```

**Examples**:
- Lenovo (United States) Inc.
- Huawei Technologies Co., Ltd.
- ZTE Corporation

---

## Detection Rules

### Word Boundary Matching
All patterns use **word boundaries** to avoid false positives:
```python
word_pattern = r'\b' + re.escape(pattern) + r'\b'
```

**Why this matters**:
- ✅ "LENOVO GROUP" matches (contains word "LENOVO")
- ❌ "AZTEC ENVIRONMENTAL" doesn't match "ZTE" (not word boundary)
- ✅ "CHINA WAY LOGISTICS" matches (contains word "CHINA")
- ❌ "HOMER LAUGHLIN CHINA COMPANY" excluded (false positive list)

### Taiwan Exclusion (Critical)
Taiwan (ROC) is **explicitly excluded**:
```python
# Exclude Taiwan
if 'republic of china' in name_lower and 'taiwan' in name_lower:
    return False
if 'taiwan' in name_lower:
    return False
```

**Why**: Taiwan (Republic of China) ≠ PRC (People's Republic of China)

### False Positive Exclusions
Known false positives are excluded:
```python
FALSE_POSITIVES = {
    # US companies
    'homer laughlin china company',  # American ceramics
    'aztec',  # American contractors (contained "ZTE")
    'cosco fire protection',  # Not COSCO shipping

    # Italian surnames
    'facchinaggi', 'vecchini',

    # Other US companies
    'comac pump',  # Not COMAC aircraft
    'mavich',  # Contains 'avic'
}
```

---

## Limitations of Current Approach

### What It Catches Well ✅
1. **Chinese companies with geographic names**
   - Beijing Enjie Decoration Co., Ltd. ✅
   - Shanghai Pudong Development Bank ✅

2. **Major Chinese tech companies**
   - Lenovo, Huawei, ZTE, Alibaba ✅

3. **Companies with "China" in name**
   - China Way Logistics ✅
   - China South Locomotive ✅

### What It Might Miss ❌

1. **Chinese companies without geographic/keyword indicators**
   - Example: "MMG Technology Group, Inc." (788 records in database)
   - Could be Chinese-owned but doesn't match patterns

2. **Chinese subsidiaries with Western names**
   - Example: "FGS, LLC" (362 records)
   - May be Chinese-owned but uses generic name

3. **Chinese state-owned enterprises without obvious names**
   - Non-branded SOEs
   - Generic industrial names

4. **Chinese companies using romanized names**
   - If company uses pinyin without city name
   - Example: "Jiashining Technology" caught (Beijing prefix)
   - But "Jiashining" alone might be missed

### What It Might Over-Include ⚠️

1. **US/EU subsidiaries of Chinese companies**
   - "Lenovo (United States) Inc." - **Correct to include?**
   - This is Lenovo's US subsidiary
   - Chinese-owned but US-incorporated

2. **Restaurants/businesses named after Chinese cities**
   - Unlikely in government procurement but theoretically possible
   - "Beijing Restaurant" would match

---

## Database Reality Check

Let's examine actual top vendors in your database:

### Top 10 Vendors (Main Database)
1. **MMG Technology Group, Inc.** - 788 records
   - **Question**: Is this actually Chinese?
   - No obvious Chinese pattern match
   - Needs verification

2. **Catalina China, Inc.** - 533 records
   - Matches pattern: "china" in name
   - But could be false positive (like Homer Laughlin China Company)
   - **Needs manual verification**

3. **Lenovo (United States) Inc.** - 442 records
   - Matches pattern: "lenovo"
   - **Chinese-owned, US subsidiary** ✅ Correct

4. **FGS, LLC** - 362 records
   - **Does not match any pattern**
   - **Why is this in the database?**
   - Needs investigation

5. **SOC COOP LIVORNESE FACCHINAGGI E TRASPORTI** - 297 records
   - Italian name (Livorno, Italy)
   - **Should be excluded by false positive filter**
   - **Potential issue - needs investigation**

---

## Critical Questions

### 1. Should We Include US Subsidiaries?
**Example**: Lenovo (United States) Inc.

**Current**: YES, included
**Reasoning**: Chinese-owned, even if US-incorporated

**User decision needed**:
- Include Chinese-owned US subsidiaries? (Current approach)
- Exclude US subsidiaries, only PRC-based entities?

### 2. What About These Records?

Let me query the database to understand why some non-obvious names are included:

**MMG Technology Group, Inc.** (788 records)
- No "China" in name
- No Chinese city
- Not in major companies list
- **How did this get detected?**

**FGS, LLC** (362 records)
- Generic US-style name
- No Chinese indicators
- **How did this get detected?**

**Need to check detection_types for these.**

---

## Recommended Actions

### Immediate Investigation
1. **Query top vendors' detection types**
   - Understand why MMG, FGS, Catalina China are in database
   - Check if they have `pop_country_china` detection
   - Verify they're not place-of-performance-only leaks

2. **Manual verification of top 20 vendors**
   - Confirm they're actually Chinese entities
   - Identify any remaining false positives

3. **Review Italian companies**
   - "FACCHINAGGI" should be excluded
   - Check if false positive filter is working

### Potential Improvements

#### Option 1: Stricter Definition (Only PRC-Based)
- Exclude US subsidiaries (Lenovo United States Inc.)
- Require physical presence in China
- Focus on mainland China operations only

#### Option 2: Enhanced Pattern Matching
- Add more known Chinese company names
- Include romanized Chinese business terms
- Add Chinese SOE indicators (集团, 公司, etc.)

#### Option 3: External Validation
- Cross-reference with:
  - GLEIF database (corporate ownership)
  - Entity List (US Commerce Dept)
  - Chinese corporate registries
  - OpenSanctions data

---

## Current Status

**Definition**: Name-based pattern matching
- City names (Beijing, Shanghai, etc.)
- Keywords (China, Chinese, Sino)
- Known companies (Lenovo, Huawei, ZTE, etc.)
- Word boundary matching
- False positive exclusions

**Strengths**:
- Fast and scalable
- Catches obvious Chinese entities
- Good precision for major companies

**Weaknesses**:
- May miss generic/Western-named Chinese companies
- Requires manual verification of edge cases
- Limited to known patterns

**Accuracy**: Unknown - needs validation
- **Recommended**: Manual review of top 50 vendors
- **Critical**: Investigate MMG, FGS, Catalina China, Facchinaggi

---

## Next Steps

1. **Immediate**: Query detection_types for top vendors
2. **Short-term**: Manual verification of top 50 vendors
3. **Medium-term**: Consider external data sources for validation
4. **Long-term**: Build verified Chinese entity database

---

**User Input Needed**:
1. Should US subsidiaries of Chinese companies be included? (Lenovo US Inc.)
2. Should we investigate the top vendors (MMG, FGS, etc.)?
3. Do you want stricter or broader definition?
