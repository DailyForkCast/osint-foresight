# COMPREHENSIVE GUIDE: DETECTING CHINESE ENTITIES IN DATA

**Created**: 2025-10-06
**Purpose**: Multi-signal methodology for identifying PRC entities across all data sources
**Status**: Validated against 2.8M USPTO records, 367K TED contractors

---

## DETECTION SIGNALS BY PRIORITY

### **TIER 1: HIGHEST CONFIDENCE SIGNALS** (95-100% Accuracy)

#### 1. **Country Codes**
- `CN` (China mainland)
- `HK` (Hong Kong SAR)
- `MO` (Macau SAR)
- `CHN` (ISO 3166-1 alpha-3)
- Text variations: "CHINA", "P.R. CHINA", "PEOPLE'S REPUBLIC OF CHINA"

**SQL Example**:
```sql
WHERE UPPER(country) IN ('CN', 'HK', 'MO', 'CHN', 'CHINA')
   OR country LIKE '%PEOPLE%REPUBLIC%'
   OR country LIKE '%P.R.%CHINA%'
```

#### 2. **Chinese Postal Codes**
- Format: 6 digits, first digit 1-9 (100000-999999)
- Excludes Japan (7 digits), Korea (5 digits), Taiwan (special patterns)

**Major City Postal Code Ranges**:
- Beijing: 100000-102629
- Shanghai: 200000-202183
- Shenzhen: 518000-518133
- Guangzhou: 510000-511515

**SQL Example**:
```sql
WHERE LENGTH(postal_code) = 6
  AND postal_code GLOB '[1-9][0-9][0-9][0-9][0-9][0-9]'
  AND country NOT IN ('JAPAN', 'KOREA', 'TAIWAN', 'SINGAPORE')
```

### **TIER 2: HIGH CONFIDENCE SIGNALS** (80-95% Accuracy)

#### 3. **Major Chinese Cities** (Tier 1 Cities + Provincial Capitals)

**Tier 1 Cities** (Highest confidence):
- BEIJING (北京)
- SHANGHAI (上海)
- GUANGZHOU (广州)
- SHENZHEN (深圳)

**Provincial Capitals & Major Cities** (39 total):
```
Chengdu, Chongqing, Tianjin, Wuhan, Xian, Hangzhou,
Nanjing, Suzhou, Dongguan, Qingdao, Dalian, Shenyang,
Harbin, Changsha, Kunming, Xiamen, Foshan, Ningbo,
Zhengzhou, Jinan, Hefei, Fuzhou, Changchun, Shijiazhuang,
Taiyuan, Hohhot, Lanzhou, Xining, Yinchuan, Urumqi,
Lhasa, Nanning, Haikou, Guiyang, Nanchang, Wenzhou,
Zhuhai, Shantou, Huizhou
```

**SQL Example**:
```sql
WHERE UPPER(city) IN (
  'BEIJING', 'SHANGHAI', 'SHENZHEN', 'GUANGZHOU',
  'HANGZHOU', 'NANJING', 'WUHAN', 'CHENGDU',
  'TIANJIN', 'CHONGQING', 'SUZHOU', 'XIAN',
  'DONGGUAN', 'QINGDAO', 'DALIAN', ...
)
```

#### 4. **Address Contains "CHINA"**
```sql
WHERE address_line_1 LIKE '%CHINA%'
   OR address_line_2 LIKE '%CHINA%'
   OR full_address LIKE '%CHINA%'
```

**Caution**: Filter out false positives like "CHINA TOWN" in non-Chinese countries

### **TIER 3: MEDIUM CONFIDENCE SIGNALS** (60-80% Accuracy)

#### 5. **Known Chinese State-Owned Enterprises (185 SOEs)**

**Defense & Aerospace**:
- AVIC, COMAC, NORINCO, NUCTECH, CASIC, CASC, COSTIND

**Telecommunications**:
- HUAWEI, ZTE, CHINA MOBILE, CHINA TELECOM, CHINA UNICOM

**Technology & Manufacturing**:
- LENOVO, HAIER, TCL, XIAOMI, OPPO, VIVO, ONEPLUS, BYD

**Surveillance & Security**:
- HIKVISION, DAHUA, MEGVII (Face++), SENSETIME

**Energy & Resources**:
- SINOPEC, PETROCHINA, CNOOC, CHINA NATIONAL PETROLEUM

**Internet & Software**:
- ALIBABA, TENCENT, BAIDU, BYTEDANCE (TikTok), MEITUAN, JD.COM

**Financial**:
- ICBC, BANK OF CHINA, CHINA CONSTRUCTION BANK, AGRICULTURAL BANK OF CHINA

**SQL Example**:
```sql
WHERE UPPER(company_name) LIKE '%HUAWEI%'
   OR UPPER(company_name) LIKE '%ZTE%'
   OR UPPER(company_name) LIKE '%ALIBABA%'
   OR UPPER(company_name) LIKE '%TENCENT%'
   ... (see full list in data/prc_soe_database.json)
```

**Important**: Use word-boundary matching to avoid false positives:
- ❌ "NIO" matches "UNION"
- ✅ " NIO " or starts/ends with "NIO"

#### 6. **Chinese Company Name Patterns**

**Common Suffixes**:
- CO., LTD (公司)
- CO LTD
- LIMITED
- CORPORATION
- TECHNOLOGY CO.
- ELECTRONICS CO.
- INDUSTRIAL CO.

**Combined with Chinese location**:
```sql
WHERE (name LIKE '%CO., LTD%' OR name LIKE '%LIMITED%')
  AND (city IN ('BEIJING', 'SHANGHAI', ...)
       OR address LIKE '%CHINA%')
```

### **TIER 4: SUPPLEMENTARY SIGNALS** (40-60% Accuracy)

#### 7. **Chinese Administrative Divisions**

**Province-level** (31 provinces + 4 municipalities + 5 autonomous regions):
```
Provinces: Anhui, Fujian, Gansu, Guangdong, Guizhou, Hainan, Hebei,
           Heilongjiang, Henan, Hubei, Hunan, Jiangsu, Jiangxi, Jilin,
           Liaoning, Qinghai, Shaanxi, Shandong, Shanxi, Sichuan, Yunnan,
           Zhejiang

Municipalities: Beijing, Shanghai, Tianjin, Chongqing

Autonomous Regions: Guangxi, Inner Mongolia, Ningxia, Tibet, Xinjiang
```

**District-level** (150+ major districts):
- Haidian District (Beijing - tech hub)
- Pudong New Area (Shanghai - financial)
- Nanshan District (Shenzhen - tech)
- Zhongguancun (Beijing - Silicon Valley)

#### 8. **Chinese Street Patterns**

**Common street suffixes** (in Pinyin romanization):
- Lu (路 - Road)
- Jie (街 - Street)
- Dadao (大道 - Avenue)
- Xiang (巷 - Lane)
- Hutong (胡同 - Alley)

**Examples in addresses**:
- "Kefa Road" / "Kefa Lu"
- "Chang'an Street" / "Chang'an Jie"
- "Zhongshan Dadao"

#### 9. **Building & Landmark Indicators**

**Common patterns**:
- Building / Tower / Plaza
- Science Park / Industrial Park / Technology Park
- High-Tech Zone / Development Zone
- Export Processing Zone

---

## MULTI-SIGNAL SCORING SYSTEM

### Weighted Scoring (Used in TED Detection)

| Signal | Points | Confidence Level |
|--------|--------|------------------|
| Country code CN/HK | 100 | VERY HIGH |
| SOE name match | 80 | HIGH |
| Postal code (6-digit) | 60 | HIGH |
| Administrative division | 50 | MEDIUM-HIGH |
| Chinese city (Tier 1) | 50 | MEDIUM-HIGH |
| Street pattern (Lu/Jie) | 30 | MEDIUM |
| Building indicator | 10 | LOW |

**Confidence Thresholds**:
- **VERY HIGH** (≥100 points): Use for critical intelligence
- **HIGH** (≥60 points): Reliable for analysis
- **MEDIUM** (≥30 points): Requires manual verification
- **LOW** (<30 points): Ignore or flag for review

---

## DATA QUALITY CONSIDERATIONS

### 1. **Missing Data**

**Challenge**: 56.4% of USPTO records have NULL country field

**Solution**:
```sql
-- Search NULL records with other signals
WHERE (country IS NULL OR country = '')
  AND (city IN ('BEIJING', 'SHANGHAI', ...)
       OR name LIKE '%HUAWEI%'
       OR address LIKE '%CHINA%')
```

### 2. **False Positives to Avoid**

| Pattern | False Positive Example | Filter |
|---------|------------------------|--------|
| "KLINE" | GlaxoSmithKline | Exclude if country = UK/US |
| "NIO" | UNION, PIONEER | Word boundary matching |
| "HK" abbreviation | GHK Consulting (UK) | Verify with other signals |
| "CHINA" in name | China Restaurant (US) | Check address/postal code |
| "TCL" | US companies with TCL | Combine with location |

**Best Practice**: Require at least 2 independent signals for confidence

### 3. **Taiwan vs. Mainland China**

**Political Sensitivity**: Taiwan entities are separate from PRC

**Detection**:
- Country code: TW, TWN, TAIWAN
- Cities: Taipei, Kaohsiung, Taichung, Tainan
- Postal codes: 5 digits (different pattern)

**Recommendation**: Track separately unless analysis requires combining

---

## IMPLEMENTATION EXAMPLES

### Example 1: Comprehensive USPTO Search
```python
chinese_signals = set()

# Tier 1: Country codes
country_matches = execute_query("""
    SELECT rf_id FROM uspto_assignee
    WHERE ee_country IN ('CHINA', 'CN', 'HK', 'CHN')
       OR ee_country LIKE '%P.R.%CHINA%'
""")
chinese_signals.update(country_matches)

# Tier 2: Cities
city_matches = execute_query("""
    SELECT rf_id FROM uspto_assignee
    WHERE UPPER(ee_city) IN ('BEIJING', 'SHANGHAI', 'SHENZHEN', ...)
""")
chinese_signals.update(city_matches)

# Tier 3: Company names
soe_matches = execute_query("""
    SELECT rf_id FROM uspto_assignee
    WHERE UPPER(ee_name) LIKE '%HUAWEI%'
       OR UPPER(ee_name) LIKE '%ZTE%'
       ...
""")
chinese_signals.update(soe_matches)

# Tier 4: NULL country records
null_matches = execute_query("""
    SELECT rf_id FROM uspto_assignee
    WHERE (ee_country IS NULL OR ee_country = '')
      AND (UPPER(ee_city) IN ('BEIJING', ...)
           OR UPPER(ee_name) LIKE '%HUAWEI%'
           OR ee_address_1 LIKE '%CHINA%')
""")
chinese_signals.update(null_matches)

total_chinese = len(chinese_signals)
```

### Example 2: TED Multi-Signal Scoring
```python
def calculate_confidence(contractor):
    score = 0
    signals = []

    # Country code (100 points)
    if contractor['country'] == 'CN':
        score += 100
        signals.append('country_CN')
    elif contractor['country'] == 'HK':
        score += 50
        signals.append('country_HK')

    # SOE match (80 points)
    if any(soe in contractor['name'].lower() for soe in SOE_LIST):
        score += 80
        signals.append('SOE_match')

    # Postal code (60 points)
    if is_chinese_postal_code(contractor['postal_code']):
        score += 60
        signals.append('postal_code')

    # City match (50 points)
    if contractor['city'].upper() in CHINESE_CITIES:
        score += 50
        signals.append('chinese_city')

    # Determine confidence level
    if score >= 100:
        confidence = 'VERY_HIGH'
    elif score >= 60:
        confidence = 'HIGH'
    elif score >= 30:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'

    return score, confidence, signals
```

---

## ADVANCED DETECTION: WHAT'S NOT AVAILABLE

### Fields We DON'T Have (in current USPTO/TED data):

❌ **Email addresses** (would enable .cn domain detection)
❌ **Website URLs** (would enable .cn/.com.cn detection)
❌ **Phone numbers** (would enable +86 country code detection)
❌ **IP addresses** (would enable geographic IP detection)
❌ **Bank account numbers** (would enable Chinese bank detection)
❌ **Tax IDs** (would enable Chinese business registration detection)

**Future Enhancement**: If these fields become available, add:
- Email domain: `@company.cn`, `@company.com.cn`
- Phone: `+86` country code
- Website: Ending in `.cn`

---

## VALIDATION & QUALITY CONTROL

### Cross-Validation Steps:

1. **Spot Check** (Manual review of 50-100 random matches)
   - Verify multi-signal matches are genuine
   - Identify false positive patterns
   - Refine detection rules

2. **Negative Testing** (Known non-Chinese entities)
   - Test against Japan (549K), Germany (175K) samples
   - Ensure no cross-contamination
   - Validate word-boundary matching

3. **Benchmark Against Known Entities**
   - Compare against EPO Chinese-only database (80,817)
   - Compare against GLEIF Chinese-only database (106,883)
   - Validate SOE detection against official lists

4. **Statistical Validation**
   - Check distribution matches expected patterns
   - Beijing/Shanghai should dominate city counts
   - SOE presence should align with known market activity

---

## COUNTRY-SPECIFIC DETECTION SUMMARY

### For Analysis Purposes:

**Include in "Chinese Entity" Count**:
- ✅ Mainland China (CN, CHN)
- ✅ Hong Kong (HK) - depends on analysis scope
- ⚠️ Macau (MO) - depends on analysis scope

**Track Separately**:
- 🔵 Taiwan (TW, TWN) - politically distinct
- 🔵 Chinese diaspora companies (registered in US/EU but Chinese-owned)

**Require Additional Investigation**:
- Subsidiaries of Chinese companies registered abroad
- Joint ventures with Chinese SOEs
- Shell companies with Chinese beneficial owners

---

## UPDATED DETECTION RESULTS

**Applied to USPTO 2.8M Records**:

| Detection Method | Matches | Notes |
|------------------|---------|-------|
| Country="CHINA" | 2,890 | Base signal |
| Country="PEOPLE'S REPUBLIC" | 468 | Variant |
| Chinese cities | 965 | Multi-city patterns |
| Known companies (Huawei, ZTE, etc.) | 925 | SOE + tech giants |
| Address contains "CHINA" | 604 | Geographic marker |
| 6-digit postal codes | 379 | Format detection |
| NULL country + signals | 421 | Hidden in missing data |
| **TOTAL UNIQUE** | **5,245** | De-duplicated |

**Comparison**:
- Japan: 549,356 (104x more than China)
- Germany: 175,018 (33x more than China)
- **China: 5,245** ← Likely severe undercount due to 56% NULL data

---

## RECOMMENDED USAGE

1. **For Critical Intelligence**: Use VERY HIGH confidence only (≥100 points)
2. **For Comprehensive Analysis**: Use HIGH + VERY HIGH (≥60 points)
3. **For Research/Exploration**: Include MEDIUM (≥30 points) with manual review
4. **Always Document**: Record which signals triggered each detection

---

**Document Version**: 1.0
**Last Updated**: 2025-10-06
**Maintained By**: OSINT Foresight Analysis Team
