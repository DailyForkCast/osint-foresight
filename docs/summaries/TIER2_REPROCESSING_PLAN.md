# TIER_2 Comprehensive Reprocessing Plan
**Date:** 2025-10-18
**Status:** Ready for Implementation
**Scope:** 166,557 total records → Re-classify TIER_2

---

## Issues Identified from Manual Review

### 1. **Substring Matching Errors** (CRITICAL)
Current detection logic matches "china" anywhere in text, causing false positives:

**Examples found:**
- **Ka**CHINA (Kachina Investments/Ventures)
- Catalina **CHINA** Inc (US company)
- Fac**CHINA** (Italian logistics)
- **CHINA** Grove, **CHINA** Lake, **CHINA** Spring (US locations)

**Root cause:** No word boundary enforcement on "china" keyword

---

### 2. **Porcelain/Tableware False Positives** (NEW - User identified)
Companies selling china/porcelain dishes, not Chinese entities:

**Keywords to exclude:**
- china porcelain
- fine china
- bone china
- china dinnerware
- china dishes
- china plates
- china glassware
- china tableware
- royal china
- china cabinet

**Example patterns:**
- "ROYAL CHINA COMPANY" (US dinnerware manufacturer)
- "LENOX CHINA" (US porcelain brand)
- "Purchase of fine china dishes"

---

### 3. **Place of Performance vs. Entity Nationality**
Entities detected because contracts performed in China, not because entity is Chinese:

**Categories:**
- Casinos/Hotels: 9 records (Harrah's, Safari Park, Riverside Casino)
- Recreational: Skydive Elsinore, gaming facilities
- US companies with China operations

---

### 4. **Insurance Companies** (8 records)
Most are international insurers, not Chinese entities:
- China Life Insurance (legitimate, but over-represented)
- SinoAsia B&R Insurance
- AIA Life Insurance Beijing Branch

**Issue:** "China" in company name ≠ Chinese state-owned entity

---

### 5. **Italian Companies** (3 records)
False positives from Italian text:
- SOC COOP LIVORNESE FACCHINAGGI E TRASPORTI
- FACCHINA GLOBAL SERVICES LLC

---

### 6. **Under-Classified Strategic Entities** (10 records)

**Biotech/Pharma CROs - Should be TIER_1:**
- PHARMARON (BEIJING) - 6 contracts ⚠️
- SHANGHAI CHEMPARTNER - 1 contract ⚠️
- FUDAN UNIVERSITY (Occupational Health) - 1 contract

**Dual-Use Technology - Should be TIER_1:**
- SHANGHAI LASER & OPTICS CENTURY CO. LTD. - 1 contract ⚠️

---

## Reprocessing Strategy

### Phase 1: Word Boundary Enforcement

**Current (BROKEN):**
```python
if 'china' in text.lower():
    # Matches: Kachina, Facchina, porcelain china, etc.
```

**Fixed:**
```python
import re
if re.search(r'\bchina\b', text, re.IGNORECASE):
    # Only matches "China" as complete word
    # Excludes: Kachina, Facchina, etc.
```

**Apply to ALL detection methods:**
- Country name matching
- Geographic references
- Entity name detection
- Place of performance fields

---

### Phase 2: Enhanced False Positive Filters

**Add to existing FALSE_POSITIVES list:**

```python
FALSE_POSITIVES_TIER2 = [
    # Substring "china" (not Chinese entities)
    r'\bkachina\b',
    r'\bcatalina\s+china\b',
    r'\bfacchina\b',

    # Porcelain/tableware (NEW)
    r'\bchina\s+porcelain\b',
    r'\bfine\s+china\b',
    r'\bbone\s+china\b',
    r'\bchina\s+dinnerware\b',
    r'\bchina\s+dishes\b',
    r'\bchina\s+plates\b',
    r'\bchina\s+cabinet\b',
    r'\broyal\s+china\b',
    r'\blenox\s+china\b',

    # US locations with "china"
    r'\bchina\s+grove\b',
    r'\bchina\s+lake\b',
    r'\bchina\s+spring\b',
    r'\bchina\s+ranch\b',

    # Casinos/Hotels/Resorts
    r'\bcasino\b',
    r'\bresort\b',
    r'\bhotel\b',
    r'\bgaming\s+corporation\b',
    r'\bharrahs\b',
    r'\bboyd\s+gaming\b',

    # Insurance (context-dependent)
    r'\binsurance\s+company\b.*(?!beijing|shanghai|shenzhen)',

    # Italian companies
    r'\bsoc\s+coop\s+livornese\b',
    r'\bfacchinaggi\b',
    r'\btrasporti\b',

    # Recreational
    r'\bskydive\b',

    # US consulting
    r'\bmsd\s+biztech\b',
]
```

---

### Phase 3: Context-Aware Detection

**Add contextual checks:**

```python
def is_false_positive_context(text, entity_name):
    """Check if 'china' reference is contextual, not entity-based"""

    # Product origin (not entity)
    if re.search(r'(made|manufactured|produced|shipped)\s+(in|from)\s+china', text, re.I):
        return True

    # Porcelain/dinnerware
    if re.search(r'(porcelain|dinnerware|dishes|plates|glassware|tableware)', text, re.I):
        if re.search(r'\bchina\b', text, re.I):
            return True

    # Place of performance vs entity
    if re.search(r'(performance location|delivery to|shipped to).*china', text, re.I):
        # Check if entity name contains China
        if not re.search(r'\bchina\b', entity_name, re.I):
            return True

    return False
```

---

### Phase 4: Entity Type Reclassification

**Tier Upgrade Rules:**

```python
def assess_tier_upgrade(entity_name, description):
    """Check if TIER_2 should be upgraded to TIER_1"""

    text = f"{entity_name} {description}".lower()

    # Biotech/Pharma CROs
    biotech_indicators = [
        'pharmaron', 'chempartner', 'wuxi', 'cro', 'cdmo',
        'drug development', 'biologics', 'clinical research'
    ]
    if any(ind in text for ind in biotech_indicators):
        return 'TIER_1', 'Biotech/pharma CRO - dual-use risk'

    # Laser/Optics (military dual-use)
    laser_indicators = [
        'laser', 'optics', 'photonics', 'electro-optical',
        'infrared', 'lidar', 'fiber optic'
    ]
    if any(ind in text for ind in laser_indicators):
        return 'TIER_1', 'Laser/optics - military dual-use'

    # Defense universities
    seven_sons = [
        'beijing institute of technology',
        'beihang', 'harbin engineering',
        'harbin institute of technology',
        'nanjing.*aeronautics',
        'nanjing.*science.*technology',
        'northwestern polytechnical',
        'national university of defense'
    ]
    if any(re.search(uni, text, re.I) for uni in seven_sons):
        return 'TIER_1', 'Seven Sons defense university'

    return 'TIER_2', 'No upgrade needed'
```

**Supply Chain Separation:**

```python
def is_supply_chain_entity(entity_name):
    """Check if entity should move to supply chain tracker"""

    supply_chain = [
        'lenovo', 'huawei technologies usa', 'zte corporation',
        'tp-link', 'haier', 'hisense', 'tcl', 'xiaomi'
    ]

    return any(supplier in entity_name.lower() for supplier in supply_chain)
```

---

### Phase 5: Improved Country Code Validation

**Cross-check entity name with country code:**

```python
def validate_country_match(entity_name, country_code, country_name):
    """Verify country code matches entity, not just description"""

    # If country_code = "CHN" but entity name has no Chinese indicators
    if country_code in ['CHN', 'HKG']:
        chinese_indicators = [
            r'\bbeijing\b', r'\bshanghai\b', r'\bshenzhen\b',
            r'\bguangzhou\b', r'\bhong\s+kong\b', r'\bchina\b',
            r'\bchinese\b', r'\bprc\b'
        ]

        if not any(re.search(ind, entity_name, re.I) for ind in chinese_indicators):
            # Country code might be place of performance, not entity nationality
            return False

    return True
```

---

## Implementation Steps

### 1. Update Processors
Modify these files:
- `scripts/process_usaspending_305_column.py`
- `scripts/process_usaspending_101_column.py`
- `scripts/process_usaspending_comprehensive.py`

**Changes:**
- Add word boundary enforcement (\\b)
- Add porcelain/tableware filters
- Add context-aware detection
- Add tier upgrade logic
- Add supply chain separation

---

### 2. Create Test Script
Test on 300-record sample before full reprocessing:

```bash
python scripts/test_tier2_reprocessing.py \
  --input data/processed/usaspending_manual_review/importance_tier_sample_20251018_075329.csv \
  --output analysis/tier2_reprocessing_test_results.json
```

**Expected results:**
- 30 false positives → REMOVED
- 10 under-classified → TIER_1
- 3 supply chain → SUPPLY_CHAIN table
- 201 correct → TIER_2 (no change)

---

### 3. Full Dataset Reprocessing
Re-process all 166,557 records:

```bash
# Backup current data
python scripts/backup_usaspending_tables.py

# Reprocess 305-column (159,513 records - 95.8%)
python scripts/run_305_production.py --reprocess-tier2

# Reprocess 101-column (5,108 records - 3.1%)
python scripts/run_101_production.py --reprocess-tier2

# Reprocess comprehensive (1,936 records - 1.2%)
python scripts/run_206_production.py --reprocess-tier2
```

**Estimated time:** 8-10 hours total

---

### 4. Validation
After reprocessing:

```bash
# Generate new sample
python scripts/generate_simple_sample.py --post-reprocessing

# Compare before/after
python scripts/compare_tier2_before_after.py
```

---

## Expected Improvements

### Before Reprocessing:
- TIER_2: 244 records (in sample)
- False Positives: 30 (12.3%)
- Under-classified: 10 (4.1%)
- Precision: ~70-75%

### After Reprocessing:
- TIER_2: 201 records (in sample)
- False Positives: 0-2 (target <1%)
- Properly classified: 10 → TIER_1
- Precision: Target ~90-95%

### Full Dataset (166K records):
- Estimated removals: ~5,000-8,000 false positives (3-5%)
- Estimated upgrades: ~1,500-2,000 → TIER_1 (biotech/pharma/dual-use)
- Estimated supply chain: ~500-1,000 entities

---

## Risk Mitigation

### Backup Strategy:
1. Create full database backup before reprocessing
2. Export current TIER_2 classifications to CSV
3. Run test on sample (300 records) first
4. Validate test results manually
5. Only proceed to full reprocessing after test validation

### Rollback Plan:
If reprocessing fails:
1. Restore from backup
2. Restore original classification tables
3. Review error logs
4. Fix issues and re-test

---

## Success Criteria

- [ ] Zero substring false positives (Kachina, Facchina, etc.)
- [ ] Zero porcelain/tableware false positives
- [ ] All biotech/pharma CROs assessed for TIER_1
- [ ] All laser/optics entities assessed for TIER_1
- [ ] Supply chain entities separated
- [ ] TIER_2 precision ≥90%
- [ ] Manual review of 100-record post-reprocessing sample confirms improvements

---

## Timeline

**Day 1 (Today):**
- [x] Complete audit
- [ ] Create reprocessing scripts
- [ ] Test on 300-record sample
- [ ] Manual validation of test results

**Day 2:**
- [ ] Full dataset reprocessing (8-10 hours)
- [ ] Post-processing validation
- [ ] Generate comparison reports

**Day 3:**
- [ ] Manual review of 100-record post-reprocessing sample
- [ ] Final precision calculation
- [ ] Documentation update

---

## Additional Considerations

### China Porcelain Patterns (User Request):
Watch for these additional patterns in full dataset:
- "Wedgwood china"
- "Mikasa china"
- "Noritake china"
- "Spode china"
- "Churchill china"
- Any "china" in conjunction with:
  - dinnerware, tableware, flatware
  - dishes, plates, bowls, cups
  - porcelain, ceramic, earthenware
  - glassware, crystal

### Product Origin vs Entity:
Distinguish between:
- ✅ "Beijing Pharmaron Ltd" (entity IS Chinese)
- ❌ "Dell computers made in China" (entity is US, product origin is China)
- ❌ "Shipped from China to US" (shipping route, not entity)

---

**Status:** Ready for implementation
**Next action:** Create test reprocessing script
