# USPTO Patent Chinese Entity Detection Methodology
**Date**: 2025-10-06
**Dataset**: USPTO Patent Filewrapper JSON (2011-2020)
**Total Records**: 240GB (~5 million patents)

---

## Detection Strategy: Multi-Signal Scoring System

### **TIER 1 Signals: Very High Confidence (95-100% Accuracy)**

#### 1. **Country Codes** (100 points)
- `CN`, `CHN` (China mainland)
- `HK` (Hong Kong SAR)
- `MO` (Macau SAR)
- `JPX` (sometimes used for China in USPTO data)

**Validation**: Must be verified with city field to avoid false positives

#### 2. **Chinese Postal Codes** (60 points)
- Format: 6 digits, first digit 1-9 (100000-999999)
- Beijing: 100000-102629
- Shanghai: 200000-202183
- Shenzhen: 518000-518133
- Guangzhou: 510000-511515

---

### **TIER 2 Signals: High Confidence (80-95% Accuracy)**

#### 3. **Known PRC Companies** (80 points)
**Technology Companies**:
- Huawei, ZTE, Xiaomi, Oppo, Vivo, Lenovo, DJI, BYD

**Internet Giants**:
- Alibaba, Tencent, Baidu, ByteDance (TikTok)

**Surveillance & AI**:
- Hikvision, Dahua, SenseTime, Megvii

**Semiconductors**:
- SMIC, BOE, Unisoc, Spreadtrum, Rockchip

**Defense & Aerospace**:
- AVIC, COMAC, NORINCO, NUCTECH, CASIC, CASC

**State-Owned Enterprises**:
- Sinopec, PetroChina, CNOOC, ICBC, Bank of China, China Mobile

**Total**: 45+ major PRC entities with word-boundary matching

#### 4. **Major Chinese Cities** (50 points)
**Tier 1 Cities** (4 municipalities):
- Beijing, Shanghai, Shenzhen, Guangzhou

**Tech Hubs** (39 provincial capitals + major cities):
- Hangzhou, Nanjing, Suzhou, Wuhan, Chengdu, Xi'an, Tianjin, Chongqing
- Dongguan, Qingdao, Dalian, Shenyang, Harbin, Changsha, Kunming
- Xiamen, Foshan, Ningbo, Zhengzhou, Jinan, Hefei, Fuzhou, Changchun
- (+ 17 more provincial capitals)

---

### **TIER 3 Signals: Medium-High Confidence (60-80% Accuracy)**

#### 5. **Address Contains "CHINA"** (30 points)
- Matches: "P.R. CHINA", "PEOPLE'S REPUBLIC OF CHINA"
- Filtered: Excludes "Chinatown" in non-Chinese addresses

---

### **TIER 4 Signals: Supplementary Indicators (40-60% Accuracy)**

#### 6. **Chinese Provinces** (40 points)
**22 Provinces**:
- Anhui, Fujian, Gansu, Guangdong, Guizhou, Hainan, Hebei
- Heilongjiang, Henan, Hubei, Hunan, Jiangsu, Jiangxi, Jilin
- Liaoning, Qinghai, Shaanxi, Shandong, Shanxi, Sichuan, Yunnan, Zhejiang

**5 Autonomous Regions**:
- Guangxi, Inner Mongolia, Ningxia, Tibet, Xinjiang

#### 7. **Tech Hub Districts** (25 points)
- Haidian (Beijing - Silicon Valley of China)
- Pudong (Shanghai - Financial district)
- Nanshan (Shenzhen - Tech hub)
- Zhongguancun (Beijing - Innovation zone)
- Luohu, Futian, Songjiang, Minhang, Baoshan, Chaoyang, Fengtai

#### 8. **Chinese Street Patterns** (15 points)
**Pinyin romanization patterns**:
- Lu (路 - Road)
- Jie (街 - Street)
- Dadao (大道 - Avenue)
- Xiang (巷 - Lane)
- Hutong (胡同 - Alley)

#### 9. **Phone Numbers** (50 points)
- `+86` country code
- China mobile/landline formats

---

### **TIER 5 Signals: Low Confidence (20-40% Accuracy)**

#### 10. **Chinese Inventors** (20 points each, max 60)
- Inventor country code: CN, CHN, HK, MO
- Multiple Chinese inventors increase confidence
- Used as supplementary signal, not primary indicator

---

## Confidence Scoring System

### **Score Thresholds**

| Confidence Level | Points | Use Case |
|------------------|--------|----------|
| **VERY HIGH** | ≥100 | Critical intelligence, high-precision analysis |
| **HIGH** | 70-99 | Reliable for comprehensive analysis |
| **MEDIUM** | 50-69 | Valid but requires context verification |
| **LOW** | <50 | Excluded from final count |

### **Inclusion Threshold**
- **Minimum Score**: 50 points (MEDIUM confidence)
- **Recommended for reporting**: 70+ points (HIGH + VERY HIGH)

---

## Data Fields Analyzed

### **From Patent JSON Structure**

**Assignee Information** (`assignmentBag` → `assigneeBag`):
```json
{
  "assigneeNameText": "HUAWEI TECHNOLOGIES CO., LTD.",
  "assigneeAddress": {
    "addressLineOneText": "BANTIAN, LONGGANG DISTRICT",
    "cityName": "SHENZHEN",
    "geographicRegionCode": "CN",
    "countryCode": "CN",
    "postalCode": "518129"
  }
}
```

**Inventor Information** (`applicationMetaData` → `inventorBag`):
```json
{
  "firstName": "Wei",
  "lastName": "Zhang",
  "countryCode": "CN",
  "inventorNameText": "Wei Zhang"
}
```

**Correspondence Addresses** (`correspondenceAddressBag`):
```json
{
  "telecommunicationNumber": "+86-755-28780808",
  "cityName": "SHENZHEN",
  "countryCode": "CN"
}
```

---

## False Positive Prevention

### **Word-Boundary Matching**
**Problem**: Short company names match unrelated entities
- "NIO" matches "UNION", "SENIOR"
- "BOE" matches "BOEING"
- "TCL" matches "METCL"
- "GREE" matches "AGREE"

**Solution**: Require specific context
```python
special_cases = {
    'NIO': ['NIO INC', 'NIO USA', 'NEXTEV'],
    'BOE': ['BOE TECHOLOG', 'BEIJING BOE'],
    'TCL': ['TCL CORP', 'TCL COMM'],
    'BYD': ['BYD COMPANY', 'BYD AUTO', 'BYD BATTERY'],
    'GREE': ['GREE ELECTRIC', 'ZHUHAI GREE']
}
```

### **Geographic Verification**
**Problem**: Country code alone can be ambiguous
- `JPX` used for both Japan and China in some USPTO records
- `CN` could theoretically include Taiwan in legacy data

**Solution**: Verify country code with city field
```python
if country_code in ('CN', 'CHN', 'HK', 'MO', 'JPX'):
    if city and city.upper() in CHINESE_CITIES:
        score += 100  # Confirmed Chinese entity
```

### **Postal Code Format Validation**
**Problem**: 6-digit codes could match other countries
- Must exclude Japan (7 digits), Korea (5 digits), Singapore (6 digits alphanumeric)

**Solution**: Validate format + context
```python
if len(postal_code) == 6 and postal_code.isdigit():
    if first_digit in range(1, 10):  # Chinese codes start 1-9
        if country_code in (None, 'CN', 'CHN'):  # Avoid Singapore
            score += 60
```

---

## Expected Results

### **Baseline Estimates** (from EPO comparison)
- EPO Chinese patents (2011-2020): ~60,000-80,000
- USPTO Chinese patents (2011-2020): ~40,000-60,000 (estimated)
- China's USPTO filing rate: 5-8% of total US patents

### **By Year Growth Trajectory**
Based on known USPTO Chinese patent growth:

| Year | Est. Chinese Patents | % Growth |
|------|---------------------|----------|
| 2011 | 1,500-2,000 | - |
| 2012 | 2,000-2,500 | +25% |
| 2013 | 2,500-3,000 | +20% |
| 2014 | 3,000-4,000 | +25% |
| 2015 | 4,000-5,000 | +25% |
| 2016 | 5,000-7,000 | +35% |
| 2017 | 7,000-9,000 | +30% |
| 2018 | 9,000-12,000 | +30% |
| 2019 | 12,000-15,000 | +25% |
| 2020 | 15,000-18,000 | +20% |
| **Total** | **60,000-80,000** | - |

---

## Processing Approach

### **Data Flow**
1. **Extract** year JSON files from 240GB ZIP archive (2011-2020)
2. **Parse** ~500,000 patents per year (~5M total)
3. **Score** each patent using multi-signal detection
4. **Filter** patents with score ≥50 (MEDIUM threshold)
5. **Store** in SQLite database with confidence metadata
6. **Report** final statistics by year, confidence, and signal type

### **Performance Considerations**
- Each year file: 19-27GB uncompressed JSON
- Processing time: ~10-15 minutes per year
- Memory usage: Stream processing, <4GB RAM
- Total runtime: ~2-3 hours for all 10 years

### **Database Schema**
```sql
CREATE TABLE uspto_patents_chinese (
    application_number TEXT PRIMARY KEY,
    patent_number TEXT,
    filing_date TEXT,
    grant_date TEXT,
    title TEXT,
    status TEXT,
    assignee_name TEXT,
    assignee_country TEXT,
    assignee_city TEXT,
    confidence TEXT,           -- VERY_HIGH, HIGH, MEDIUM, LOW
    confidence_score INTEGER,   -- Raw point score
    detection_signals TEXT,     -- Comma-separated signal list
    year INTEGER,
    processed_date TEXT
)
```

---

## Comparison to Previous USPTO Analysis

### **Trademark Database (1823-2006)**
- **Total assignees**: 2.8M
- **Chinese entities found**: 1,500-2,000 (PRC mainland)
- **Data quality issues**:
  - 56% NULL country field
  - Taiwan (ROC) coded as "CHINA"
  - Pre-dates China's economic boom
  - Missing modern tech companies (Huawei: 0, Alibaba: 0)

### **Patent Database (2011-2020)** ← New Analysis
- **Total patents**: ~5M
- **Expected Chinese patents**: 60,000-80,000
- **Data quality**: Modern, complete assignee/inventor data
- **Key difference**: 40-50x more Chinese entities vs. trademarks

---

## Validation Strategy

### **Cross-Reference Checks**
1. **EPO Patent Database**: Compare companies found in both systems
2. **Known Chinese Tech Giants**: Verify Huawei, ZTE, Xiaomi, etc. present
3. **Geographic Distribution**: Beijing/Shanghai should dominate
4. **Growth Trajectory**: Expect 20-35% YoY growth 2011-2020

### **Quality Control**
1. **Manual Review**: Sample 100 random HIGH/VERY_HIGH confidence matches
2. **False Negative Test**: Search for known Chinese companies manually
3. **False Positive Test**: Verify no Japan/Korea/Taiwan misclassifications
4. **Signal Correlation**: Check that multiple signals co-occur as expected

---

## Reporting Format

### **Executive Summary**
- Total patents processed: X million
- Chinese patents identified: X,XXX (X.X% of total)
- Confidence breakdown: XX% VERY_HIGH, XX% HIGH, XX% MEDIUM
- Top 20 Chinese assignees by patent count
- Year-over-year growth analysis

### **Technical Validation**
- Detection signals distribution
- Geographic concentration (Beijing vs. Shanghai vs. Shenzhen)
- Technology classification breakdown
- Comparison to EPO/WIPO benchmarks

---

**Methodology Version**: 2.0
**Last Updated**: 2025-10-06
**Maintained By**: OSINT Foresight Analysis Team
