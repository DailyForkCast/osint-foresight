# Detector Comparison Summary

**Date**: 2025-10-04
**Purpose**: Quick reference for how each detector determines China involvement

---

## Quick Comparison

| Detector | Primary Signal | Data Type | China Indicator | False Positive Risk |
|----------|----------------|-----------|-----------------|---------------------|
| **PSC Strict v3.0** | Nationality field | Structured | `nationality == "Chinese"` | LOW (verified nationality) |
| **USAspending v2.0** | Text matching | Unstructured | Multilingual patterns + 310 locations | MEDIUM (text mentions) |
| **CORDIS v1.0** | Country code | Structured | `country == "CN"` | VERY LOW (EU database) |
| **OpenAlex v2.0** | Institution code | Structured | `country_code == "CN"` | VERY LOW (pre-validated institutions) |

---

## Detailed Methodologies

### 1. PSC Strict v3.0 (UK Companies)

**Question**: Is this UK company controlled by Chinese persons?

**Primary Detection**:
```python
psc.nationality == "Chinese"  # 95% confidence
```

**Secondary Detection** (if no nationality):
```python
psc.address.includes("China") AND legal_form.is_corporate()  # 70% confidence
```

**REJECTED**:
- Residence-only matches (e.g., "Chinese national living in London")
- Hong Kong, Macau, Taiwan (excluded per config)

**Result**: 209,061 UK companies with Chinese PSCs (1.42% hit rate)

**Documentation**: Internal to PSC processor

---

### 2. USAspending v2.0 (US Government Contracts)

**Question**: Does this contract mention China in any capacity?

**Detection Stages** (all applied):

1. **Multilingual patterns** (40 languages)
   ```regex
   English: \b(China|Chinese|PRC|Beijing)\s+(company|contractor|supplier)\b
   French: \b(chinois|Chine)\s+(société|entreprise|fournisseur)\b
   ... (38 more languages)
   ```

2. **Known Chinese companies** (30+)
   ```
   Huawei, ZTE, SMIC, CNOOC, Sinopec, Alibaba, Tencent, ...
   ```

3. **Chinese locations** (310 comprehensive)
   ```
   All provinces, autonomous regions, municipalities, SARs
   All 28 provincial capitals
   Tier 1-5 cities (Beijing, Shanghai, Xi'an, Urumqi, Lhasa, ...)
   Alternative spellings (Xi'an → Xian, Guangzhou → Canton)
   ```

4. **Technology keywords**
   ```
   5G, AI, quantum, semiconductor, surveillance, drone, ...
   ```

5. **BRI keywords**
   ```
   Belt and Road, BRI, Silk Road, infrastructure, ...
   ```

**Fields Analyzed**: First 50 text fields from each contract record

**Confidence**: Weighted score from all 5 stages (threshold: 0.5)

**Result**: 1,046 US contracts mentioning China (0.000071% hit rate)

**Documentation**: `USASPENDING_DETECTION_METHODOLOGY.md`

---

### 3. OpenAlex v2.0 (Academic Research)

**Question**: Is this paper a China-[Target Country] research collaboration?

**Detection Logic**:

```python
# Step 1: Check for Chinese institution (REQUIRED)
has_chinese_author = False
for author in paper.authors:
    for institution in author.institutions:
        if institution.country_code == "CN":
            has_chinese_author = True
            break

if not has_chinese_author:
    return SKIP  # No China involvement

# Step 2: Check for collaboration with 81 target countries
collaboration_countries = []
for author in paper.authors:
    for institution in author.institutions:
        if institution.country_code != "CN":
            collaboration_countries.append(institution.country_code)

target_countries = [c for c in collaboration_countries if c in [81_COUNTRY_LIST]]

if not target_countries:
    return SKIP  # Pure domestic Chinese research

# Step 3: Text validation (40 languages, 310 locations)
text = paper.title + paper.abstract + institution_names + concepts
for country in target_countries:
    result = CompleteEuropeanValidator.validate(text, country)
    if result.china_detected and result.confidence >= 0.5:
        return DETECTED
```

**What It Detects**: Papers with:
- ≥1 author from Chinese institution (`country_code == "CN"`)
- ≥1 author from target country (81 countries: EU, NATO, Five Eyes, BRI, Indo-Pacific)
- Text validation passes (mentions China/Chinese entities)

**What It DOESN'T Detect**:
- Pure domestic Chinese research (all authors from CN)
- China collaborations with non-target countries (e.g., CN-LK Sri Lanka, unless LK added to 81)
- Papers that only mention "China" in title without Chinese authors

**Result** (projected): ~40,000-50,000 collaborations from 504 partitions

**Documentation**: `OPENALEX_DETECTION_METHODOLOGY.md`

---

### 4. CORDIS v1.0 (EU Research Projects)

**Question**: Does this EU-funded project have Chinese organization participation?

**Detection Logic**:

```python
# Step 1: Check organization country code (PRIMARY)
if org.country == 'CN':
    return DETECTED  # 95% confidence

# Step 2: Check known Chinese institutions (if country missing)
if org.name contains ['TSINGHUA', 'PEKING', 'FUDAN', ...]:
    return DETECTED  # 85% confidence

# Step 3: Check for "CHINA" in name (if country unknown)
if 'CHINA' in org.name and org.country in ['', 'XX', 'ZZ']:
    return DETECTED  # 70% confidence
```

**What It Detects**: EU-funded research projects with:
- Organizations with country code = CN
- Known Chinese universities (17 institutions)
- Organizations with "China" in name and unknown country

**What It DOESN'T Detect**:
- Non-EU funded research (outside CORDIS scope)
- Pure domestic Chinese research (no EU involvement)
- Pre-2014 projects (H2020 started 2014)
- Chinese companies not participating in EU projects

**Result**: 838 Chinese participations in 384 EU projects

**Documentation**: `CORDIS_DETECTION_METHODOLOGY.md`

---

## Key Differences

### Data Type

| Detector | Data Type | Advantage | Disadvantage |
|----------|-----------|-----------|--------------|
| **PSC** | Structured (nationality field) | No false positives from mentions | Limited to UK companies |
| **USAspending** | Unstructured (free text) | Catches indirect mentions | False positives from casual mentions |
| **CORDIS** | Structured (country code) | Official EU database, funding tracked | Limited to EU-funded projects |
| **OpenAlex** | Structured (institution codes) | Pre-validated, no false positives | Requires author affiliation data |

---

### China Signal Strength

| Detector | Signal Type | Confidence | Verification |
|----------|-------------|------------|--------------|
| **PSC** | Legal nationality declaration | 95% | UK government verified |
| **USAspending** | Text pattern matching | 50-85% | Requires manual review |
| **CORDIS** | Country code field | 95% | EU CORDIS database |
| **OpenAlex** | Institution database lookup | 95%+ | OpenAlex curated database |

---

### What Each Detector Misses

**PSC**:
- ❌ Companies outside UK
- ❌ Indirect ownership (Chinese PSC → UK company → another company)
- ❌ Former Chinese nationals who changed citizenship

**USAspending**:
- ❌ Contracts without text descriptions
- ❌ Subcontractor chains (buried in descriptions)
- ❌ Redacted fields (PII/security)
- ❌ Contracts pre-2000 (dataset limitation)

**CORDIS**:
- ❌ Non-EU funded research (outside CORDIS scope)
- ❌ Pre-2014 projects (H2020 started 2014)
- ❌ Pure domestic Chinese projects (no EU funding)
- ❌ Projects not reported to CORDIS

**OpenAlex**:
- ❌ Publications not in OpenAlex (conference proceedings, patents, reports)
- ❌ Pure domestic Chinese research (no international collaboration)
- ❌ Collaborations with non-target countries
- ❌ Publications without proper institution metadata

---

## When to Use Each Detector

### Use PSC When:
- ✅ Investigating UK-specific supply chains
- ✅ Finding Chinese ownership of UK entities
- ✅ High-confidence requirement (nationality is legal declaration)
- ✅ Need to identify specific companies (company numbers provided)

### Use USAspending When:
- ✅ Investigating US government procurement
- ✅ Finding China-related contract scopes
- ✅ Researching embassy operations in China
- ✅ Need broad text-based coverage (catches indirect mentions)

### Use CORDIS When:
- ✅ Investigating EU-funded research collaborations
- ✅ Finding Chinese participation in H2020/Horizon Europe
- ✅ Tracking EU funding flows to Chinese organizations
- ✅ Analyzing EU-China research partnerships
- ✅ High-confidence requirement (country codes are official)

### Use OpenAlex When:
- ✅ Investigating research collaborations
- ✅ Tracking technology transfer through academic partnerships
- ✅ Analyzing trends over time (2000-2025)
- ✅ Identifying dual-use research domains
- ✅ High-confidence requirement (institution codes are verified)

---

## Combined Use (Phase 2 Bayesian Fusion)

**Why Combine All Three?**

Each detector finds **different types of China connections**:

```
PSC: "UK Company #12345678 is controlled by Chinese national Li Wei"
USAspending: "US Army contract mentions 'Beijing research facility'"
CORDIS: "Tsinghua University received €50K in H2020 project EXAMPLE"
OpenAlex: "MIT-Tsinghua joint paper on quantum computing"
```

**Bayesian Fusion** combines these **independent signals**:
- If entity appears in **multiple detectors** → Higher confidence
- If entity appears in **only one detector** → Detector-specific confidence
- **Correlation adjustment** prevents double-counting (e.g., if PSC and USAspending always find same entities)

**Example**:
```
Entity: "Huawei Technologies"
- PSC: Not detected (Huawei is Chinese company, not UK company)
- USAspending: DETECTED (confidence 85% - mentions in contract descriptions)
- OpenAlex: DETECTED (confidence 92% - research collaborations)

Bayesian Fusion:
- Prior probability: 1.4% (base rate from all detectors)
- Likelihood ratios: USAspending (3.5x), OpenAlex (4.2x)
- Correlation discount: 0.85 (some overlap expected)
- POSTERIOR: 94% (high confidence - 2 independent detectors agree)
```

---

## Summary Table

| Criterion | PSC Strict v3.0 | USAspending v2.0 | CORDIS v1.0 | OpenAlex v2.0 |
|-----------|-----------------|------------------|-------------|---------------|
| **China Signal** | `nationality == "Chinese"` | Text patterns + 310 locations | `country == "CN"` | `country_code == "CN"` |
| **Data Quality** | Structured (government verified) | Unstructured (free text) | Structured (EU database) | Structured (curated database) |
| **False Positive Risk** | Low | Medium | Very Low | Very Low |
| **Coverage** | UK companies only | US contracts only | EU-funded projects | Global academic research |
| **Detections** | 209,061 | 1,046 | 838 | ~40,000-50,000 (projected) |
| **Hit Rate** | 1.42% | 0.000071% | 0.29% | ~2% (of China-involved papers) |
| **Best For** | Ownership analysis | Procurement analysis | EU research funding analysis | Research collaboration analysis |
| **Limitation** | Geographic (UK) | Text quality dependent | EU-funded projects only | Requires collaboration |

---

**Recommendation**: Use **all detectors** together via Phase 2 Bayesian fusion for comprehensive China connection analysis across ownership, procurement, EU research, and global academic collaboration domains.
