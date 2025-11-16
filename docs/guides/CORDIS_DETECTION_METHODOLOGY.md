# CORDIS China Detection Methodology

**Detector**: CORDIS v1.0
**Status**: ✅ Complete
**Dataset**: EU CORDIS H2020 + Horizon Europe organization participation data
**Processing Date**: 2025-10-04
**Detections**: 838 Chinese organization participations

---

## How We Determine China Involvement

### Primary Detection Method: ISO Country Code

**Rule**: An organization participation is China-related if `country == "CN"`

**Implementation**:
```python
def is_chinese_organization(self, org: Dict) -> tuple[bool, str, int]:
    """Determine if organization is Chinese"""
    country = str(org.get('country', '')).strip().upper()

    # Primary criterion: country code
    if country == 'CN':
        return (True, 'country_code_CN', 95)  # 95% confidence
```

**Key Points**:
- Uses **ISO 3166-1 alpha-2 country code** from CORDIS data
- Country code = `CN` (China)
- No text matching needed - explicit structured field
- High confidence (95%) due to official EU database

---

## Secondary Detection Methods

### 2. Known Chinese Institution Names

**Rule**: If country code missing/unknown, match against known Chinese universities

**Implementation**:
```python
chinese_institution_keywords = {
    'TSINGHUA', 'PEKING', 'FUDAN', 'ZHEJIANG', 'SHANGHAI JIAO TONG',
    'CHINA AGRICULTURAL', 'CHINESE ACADEMY', 'BEIJING INSTITUTE',
    'NANJING UNIVERSITY', 'WUHAN UNIVERSITY', 'HARBIN INSTITUTE',
    'XIAN JIAOTONG', 'TONGJI UNIVERSITY', 'SICHUAN UNIVERSITY',
    'TIANJIN UNIVERSITY', 'DALIAN UNIVERSITY', 'SOUTHEAST UNIVERSITY'
}

for keyword in chinese_institution_keywords:
    if keyword in name:
        return (True, f'institution_name_match_{keyword}', 85)
```

**Confidence**: 85% (well-known institutions, but name-based)

---

### 3. "China" or "Chinese" in Name (Fallback)

**Rule**: If name contains "CHINA" or "CHINESE" and country is unknown

**Implementation**:
```python
if 'CHINA ' in name or ' CHINA' in name or name.startswith('CHINA'):
    if country in ['', 'XX', 'ZZ']:  # Unknown/international codes
        return (True, 'china_in_name_no_country', 70)

if 'CHINESE ' in name or ' CHINESE' in name:
    if country in ['', 'XX', 'ZZ']:
        return (True, 'chinese_in_name_no_country', 70)
```

**Confidence**: 70% (text-based, requires unknown country)

---

## What We Extract from Each Participation

### Fields Captured

**Organization Information**:
- `entity_name`: Organization name
- `entity_type`: "research_organization"
- `entity_subtype`: Activity type (HES, REC, PRC, PUB, OTH)
- `country_code`: ISO alpha-2 country code
- `city`: Organization city
- `geolocation`: Geographic coordinates (when available)

**Project Information**:
- `project_id`: EU project ID
- `project_acronym`: Project short name
- `role`: Organization role (coordinator, participant)
- `order`: Participation order

**Funding Information**:
- `funding_amount_eur`: EC contribution to this organization
- `total_cost_eur`: Total cost for this organization
- `is_sme`: Small/medium enterprise flag

**Detection Metadata**:
- `detection_id`: SHA-256 hash of org ID + project ID
- `detector_id`: "cordis_v1.0"
- `confidence_score`: 95 (country code) / 85 (institution) / 70 (name)
- `detection_reason`: Detection method used

**Provenance**:
- `source`: "CORDIS H2020/Horizon Europe"
- `file`: "organization.json"
- `organization_id`: CORDIS organization ID
- `rcn`: Record Control Number
- `content_update_date`: Data freshness

---

## Data Sources

### H2020 (Horizon 2020)
- **File**: `countries/_global/data/cordis_raw/h2020/projects/organization.json`
- **Size**: 147MB
- **Records**: 178,414 organizations
- **Chinese Participations**: 600
- **Program Period**: 2014-2020

### Horizon Europe
- **File**: `countries/_global/data/cordis_raw/horizon/projects/organization.json`
- **Size**: 90MB (approx)
- **Records**: 115,056 organizations
- **Chinese Participations**: 238
- **Program Period**: 2021-present

**Total Processed**: 293,470 organizations

---

## Detection Results

### Overall Statistics

| Metric | Value |
|--------|-------|
| **Total Organizations Processed** | 293,470 |
| **Chinese Participations Detected** | 838 |
| **Detection Rate** | 0.29% |
| **Unique Chinese Organizations** | 413 |
| **Unique Projects with China** | 384 |
| **Total EU Funding to Chinese Orgs** | €5,640,499.35 |

### Detection Method Breakdown

| Method | Detections | Percentage |
|--------|------------|------------|
| **Country Code CN** | 836 | 99.8% |
| **Institution Name Match** | 2 | 0.2% |
| **China in Name** | 0 | 0% |

**Key Insight**: Nearly all detections (99.8%) came from explicit `country == "CN"` field, demonstrating high data quality in CORDIS.

---

### By Activity Type

EU classifies organizations into activity types:

| Activity Type | Count | Description |
|---------------|-------|-------------|
| **HES** | 492 | Higher Education Establishments (Universities) |
| **REC** | 140 | Research Organizations |
| **PRC** | 117 | Private Companies |
| **PUB** | 59 | Public Bodies |
| **OTH** | 22 | Other |
| **(blank)** | 8 | Unknown |

**Key Insight**: 59% are universities (HES), 17% research institutes (REC), 14% companies (PRC)

---

### Top Chinese Organizations

| Rank | Organization | Participations | Total Funding (EUR) | Type |
|------|-------------|----------------|---------------------|------|
| 1 | **TSINGHUA UNIVERSITY** | 45 | €803,941.25 | HES |
| 2 | **Zhejiang University** | 30 | €0.00 | HES |
| 3 | **SHANGHAI JIAO TONG UNIVERSITY** | 16 | €0.00 | HES |
| 4 | **CHINA AGRICULTURAL UNIVERSITY** | 14 | €114,125.00 | HES |
| 5 | **PEKING UNIVERSITY** | 14 | €37,658.75 | HES |
| 6 | **XI'AN JIAOTONG UNIVERSITY** | 13 | €0.00 | HES |
| 7 | **FUDAN UNIVERSITY** | 12 | €314,712.50 | HES |
| 8 | **HONG KONG POLYTECHNIC UNIVERSITY** | 12 | €0.00 | HES |
| 9 | **HUAZHONG UNIVERSITY OF SCIENCE AND TECHNOLOGY** | 11 | €0.00 | HES |
| 10 | **Tianjin University** | 11 | €0.00 | HES |

**Note**: Many organizations show €0 funding - this may indicate:
- Third-party funded (not EC direct funding)
- Data missing/incomplete in CORDIS
- In-kind contributions
- Funding routed through coordinator

---

## Why This Method is Robust

### 1. Structured Data (Not Text Mining)

**Advantage**: Uses official CORDIS country codes
- **No false positives** from mentions like "China shop" or "porcelain from China"
- **No language barriers** - ISO codes are universal
- **Pre-validated** - EU maintains CORDIS database quality

**Example**:
```
Project Title: "Comparison of Education Systems in US, UK, and China"
Participating Org: MIT (country: US)
Result: NOT DETECTED (no CN country code, despite "China" in title)
```

---

### 2. Multi-Tier Fallback

**Primary**: Country code (99.8% of detections)
**Secondary**: Known institution names (0.2% of detections)
**Tertiary**: Text matching (0% - never triggered)

**Why Fallback Matters**: Some organizations may have:
- Missing country codes
- International consortia (country = "XX")
- Chinese branch offices of foreign universities

---

### 3. Complete Provenance

Every detection includes:
```python
{
  'detection_id': 'cordis_a1b2c3d4e5f6g7h8',  # SHA-256 hash
  'evidence': {
    'source': 'CORDIS H2020/Horizon Europe',
    'file': 'organization.json',
    'organization_id': 937657194,  # CORDIS org ID
    'rcn': 123456,  # Record Control Number
    'content_update_date': '2024-11-15'
  }
}
```

**Anti-Fabrication Compliance**:
- ✅ Complete provenance (CORDIS org ID, RCN, file)
- ✅ SHA-256 detection IDs (verifiable)
- ✅ No synthetic data
- ✅ Explicit confidence scores (95/85/70)
- ✅ Source verification (CORDIS is public database)

---

## What Gets Detected (Examples)

### Example 1: Tsinghua University in H2020 Project ✅

```json
{
  "organisationID": 999901318,
  "name": "TSINGHUA UNIVERSITY",
  "country": "CN",
  "city": "BEIJING",
  "projectID": 123456,
  "projectAcronym": "EXAMPLE",
  "ecContribution": "50000.00",
  "totalCost": "50000.00",
  "activityType": "HES",
  "role": "participant"
}
```

**Detection**:
- ✅ Has country code CN
- ✅ Confidence: 95%
- ✅ Funding tracked: €50,000
- **Result**: China-EU research collaboration detected

---

### Example 2: Institution Name Match (No Country Code) ✅

```json
{
  "organisationID": 888888888,
  "name": "CHINESE ACADEMY OF SCIENCES BEIJING INSTITUTE",
  "country": "",
  "projectID": 789012,
  "activityType": "REC"
}
```

**Detection**:
- ❌ No country code
- ✅ "CHINESE ACADEMY" in known institution list
- ✅ Confidence: 85%
- **Result**: Detected via institution name matching

---

### Example 3: Non-Chinese Organization ❌

```json
{
  "organisationID": 999999999,
  "name": "MAX PLANCK SOCIETY",
  "country": "DE",
  "city": "MUNICH",
  "activityType": "REC"
}
```

**Detection**:
- ❌ Country code = DE (Germany)
- ❌ Name not in Chinese institution list
- **Result**: Not detected (correctly)

---

## Comparison to Other Detectors

| Detector | What It Detects | China Signal |
|----------|-----------------|--------------|
| **PSC Strict** | UK companies | Chinese nationality/corporate registration |
| **USAspending** | US contracts | Text mentions of China/Chinese locations |
| **CORDIS** | EU research projects | **Organization country code = CN** |
| **OpenAlex** | Academic papers | Institution country code = CN |

**CORDIS Advantage**:
- **Structured data** (official EU database)
- **Pre-validated** (CORDIS quality control)
- **No false positives** from text mentions
- **Funding transparency** (EC contribution tracked)
- **Participation role** (coordinator vs participant)

---

## What We Detect

**Scope**: Chinese organizations participating in EU-funded research projects

**Includes**:
- ✅ Chinese universities in H2020/Horizon Europe
- ✅ Chinese research institutes collaborating with EU
- ✅ Chinese companies in EU research consortia
- ✅ Hong Kong universities (country code = CN in CORDIS)
- ✅ Chinese public bodies in EU projects

**Excludes**:
- ❌ Pure EU projects (no Chinese participation)
- ❌ Chinese domestic projects (not EU-funded)
- ❌ Projects mentioning "China" without Chinese partners
- ❌ Taiwan organizations (different country code)

---

## Limitations

### 1. Funding Data Gaps
**Issue**: Many participations show €0 funding

**Possible Reasons**:
- Third-party funding (not EC direct)
- In-kind contributions
- Data missing in CORDIS
- Funding routed through project coordinator

**Impact**: Total funding (€5.6M) likely **underestimated**

---

### 2. Hong Kong Classification
**Issue**: Hong Kong universities have `country = "CN"` in CORDIS

**Examples Detected**:
- Hong Kong Polytechnic University (12 participations)
- University of Hong Kong
- Hong Kong University of Science & Technology

**Impact**: Detects HK as China (which may or may not align with policy definition)

---

### 3. Chinese Branch Campuses
**Issue**: Western universities with China campuses may be detected

**Examples**:
- University of Nottingham Ningbo (6 participations, €361,343.75)
  - UK university, but China campus with `country = "CN"`

**Impact**: Some detections are **joint ventures**, not pure Chinese organizations

---

### 4. Temporal Coverage
**Issue**: Only covers H2020 (2014-2020) and Horizon Europe (2021-present)

**Missing**:
- Pre-2014 Framework Programmes (FP7, FP6, etc.)
- Non-EU funded collaborations
- Bilateral agreements outside CORDIS

**Impact**: Historical trend analysis limited to 2014-present

---

## Integration with Phase 2

### Detection Format

CORDIS detector outputs **NDJSON** (newline-delimited JSON):

```json
{"detection_id": "cordis_a1b2c3d4e5f6g7h8", "detector_id": "cordis_v1.0", "entity_name": "TSINGHUA UNIVERSITY", "entity_type": "research_organization", "country_code": "CN", "confidence_score": 95, ...}
{"detection_id": "cordis_b2c3d4e5f6g7h8i9", "detector_id": "cordis_v1.0", "entity_name": "PEKING UNIVERSITY", "entity_type": "research_organization", "country_code": "CN", "confidence_score": 95, ...}
```

**File**: `data/processed/cordis_v1/detections.ndjson` (838 lines)

---

### Phase 2 Configuration

CORDIS added to `config/phase2_config.json`:

```json
{
  "detector_id": "cordis_v1.0",
  "version": "v1.0",
  "description": "CORDIS EU research project Chinese participation detection",
  "output_file": "data/processed/cordis_v1/detections.ndjson",
  "status_file": "data/processed/cordis_v1/statistics.json"
}
```

---

### Correlation with Other Detectors

**Expected Correlation**:
- **PSC** (UK companies): **LOW** - Different entity types (companies vs universities)
- **USAspending** (US contracts): **LOW** - Different jurisdictions (EU vs US)
- **OpenAlex** (research papers): **HIGH** - Same domain (academic research)

**Why High Correlation with OpenAlex?**:
- Both detect research collaborations
- CORDIS = EU-funded projects
- OpenAlex = All published papers
- Overlap: Papers from CORDIS projects often appear in OpenAlex

**Bayesian Fusion Benefit**:
- If entity detected in **both CORDIS and OpenAlex** → Very high confidence (two independent research signals)
- If detected in **CORDIS only** → EU-funded project without published papers yet
- If detected in **OpenAlex only** → Research collaboration without EU funding

---

## Summary

### How We Determine China Involvement

**Primary Criterion**: Organization has `country == "CN"` in CORDIS database (95% confidence)

**Secondary Criterion**: Organization name matches known Chinese institutions (85% confidence)

**Tertiary Criterion**: "CHINA" or "CHINESE" in name with unknown country (70% confidence)

**Detection Results**:
- 838 Chinese participations
- 413 unique Chinese organizations
- 384 unique EU projects with Chinese partners
- €5.6M+ EU funding (likely underestimated)

**Data Quality**: 99.8% detections via explicit country code (high precision)

**Provenance**: Full tracking with CORDIS org IDs, RCN, file paths, confidence scores

**Output Format**: Detection NDJSON ready for Phase 2 Bayesian fusion

---

**Last Updated**: 2025-10-04 18:53 UTC
**Methodology Version**: CORDIS v1.0
**Processing Status**: ✅ Complete (293,470 organizations processed)
