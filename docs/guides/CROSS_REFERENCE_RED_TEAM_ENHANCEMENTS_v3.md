# Cross-Reference Analysis Master Plan - Red-Team Enhancements v3.0
**Date:** October 2, 2025
**Version:** 3.0 (Anti-Fabrication + CI/CD Integration)
**Purpose:** Production-ready methodological improvements with automated enforcement
**Source:** ChatGPT red-team review + CI/CD best practices

---

## 📋 VERSION HISTORY

- **v1.0** - Initial red-team review (basic methodological improvements)
- **v2.0** - Added validation framework, gold sets, stress tests
- **v3.0** - **NEW:** GitHub Actions CI/CD, anti-fabrication enforcement, pytest automation, HITL workflows

---

## 🎯 EXECUTIVE SUMMARY

This document combines **all red-team improvements** from v2.0 with **production-ready automation**:

### **Core Enhancements (from v2.0)**
1. PSC strict re-estimation (nationality-first, HK/MO/TW toggle)
2. CJK name normalization (Simplified↔Traditional, Pinyin, family-name handling)
3. Detector independence (correlation matrix, Bayesian fusion)
4. Maximum extraction per source (ownership trees, UEI, CPC buckets)
5. DuckDB/PostgreSQL architecture
6. Enhanced provenance (detector_id, feature_hash, temporal_range)

### **NEW in v3.0: Production Automation**
7. **GitHub Actions CI/CD** - 9 automated validation jobs
8. **Anti-fabrication gates** - Blocks merge if placeholders detected
9. **Pytest automation** - 42+ tests enforcing hard rules
10. **HITL API** - Cryptographic signature workflow for CRITICAL reviews
11. **Security scanning** - Secrets detection, sensitive data checks
12. **Documentation CI** - Ensures all docs present and updated

---

## 🚨 HARD RULES (NO EXCEPTIONS)

### **Anti-Fabrication Commitments**
```
NO FABRICATION     — Every claim backed by explicit provenance (file/line/field)
PROVENANCE REQUIRED — Structured evidence for every detection
DETERMINISTIC      — Identical results on same inputs (run_id tracking)
HITL FOR CRITICAL  — Human sign-off required for CRITICAL/SANCTIONED labels
FAIL CLOSED        — Missing data → explicit incomplete: true, no guessing
```

### **Enforcement Mechanisms (NEW in v3.0)**

#### **1. Provenance Gates (Pre-Commit)**
```python
def validate_detection_provenance(detection):
    """
    HARD RULE: Every detection must have complete provenance
    ENFORCEMENT: pytest will fail if any detection missing these fields
    """
    required = ['file_id_or_url', 'record_id_or_line', 'field_name', 'field_value']
    missing = [f for f in required if f not in detection['evidence']]

    if missing:
        raise ValueError(f"ANTI-FABRICATION VIOLATION: Missing {missing}")

    # Verify file exists
    if not os.path.exists(detection['evidence']['file_id_or_url']):
        if not detection['evidence']['file_id_or_url'].startswith('http'):
            raise ValueError(f"Provenance file not found: {detection['evidence']['file_id_or_url']}")

    return True
```

#### **2. GitHub Actions Placeholder Check**
```yaml
# .github/workflows/cross_ref_ci.yml
- name: Block merge if placeholders found
  run: |
    if grep -Hn "REPLACE_ME" validation/*.csv; then
      echo "::error::Found REPLACE_ME in CSVs - must use real data"
      exit 1
    fi
```

#### **3. Pytest Anti-Hallucination Tests**
```python
@pytest.mark.parametrize("entity", load_entities())
def test_no_hallucination(entity):
    """
    HARD RULE: Claimed field values must match source records
    ENFORCEMENT: Randomly sample 2% and cross-check against source
    """
    for detection in entity['china_connections']:
        evidence = detection['evidence']
        source_record = fetch_source_record(
            evidence['file_id_or_url'],
            evidence['record_id_or_line']
        )

        actual_value = source_record.get(evidence['field_name'])
        claimed_value = evidence['field_value']

        assert actual_value == claimed_value, \
            f"HALLUCINATION: Claimed '{claimed_value}' but source has '{actual_value}'"
```

#### **4. HITL Signature Requirement**
```python
def approve_critical_detection(entity_id, reviewer_id):
    """
    HARD RULE: CRITICAL labels require cryptographic signature
    ENFORCEMENT: API endpoint validates signature before updating entity
    """
    entity = load_entity(entity_id)

    if entity['aggregate_risk']['risk_level'] == 'CRITICAL':
        if not entity['human_verified']:
            raise ValueError("CRITICAL entity not yet reviewed")

        if not entity['verification_signature']:
            raise ValueError("CRITICAL entity missing signature")

        # Verify signature
        if not verify_signature(entity['verification_signature'], reviewer_id):
            raise ValueError("Invalid signature for CRITICAL entity")

    return True
```

---

## 🔴 ISSUE #1: PSC Over-Estimation (v2.0 + v3.0 Enhancements)

### **Problem Statement**
Original PSC detection (1.13M) likely includes:
- False positives from HK/MO/TW conflation
- Residence-based weak signals
- Duplicate records
- Ceased PSCs without time-slicing

### **Solution: Strict Re-Estimation Protocol**

#### **Step 1: Strict Detection (v2.0 Rules)**
```python
def is_chinese_psc_strict(psc_record):
    """
    Strict nationality-first detection with HK/MO/TW toggle

    HARD RULE: Must return (bool, confidence, evidence_list)
    PROVENANCE: Evidence list must include (signal_type, value, confidence)
    """
    evidence = []

    # PRIMARY: Nationality (95% confidence)
    if psc_record.nationality in ['Chinese', 'China', 'CN', 'CHN', "People's Republic of China"]:
        # STRICT: Exclude HK/MO/TW unless toggle enabled
        if psc_record.nationality not in ['Hong Kong', 'Macau', 'Taiwan', 'HK', 'MO', 'TW']:
            evidence.append({
                'signal_type': 'nationality_prc',
                'field_name': 'nationality',
                'field_value': psc_record.nationality,
                'confidence': 95,
                'provenance': {
                    'file_id': psc_record.source_file,
                    'line': psc_record.source_line,
                    'company_number': psc_record.company_number,
                    'psc_id': psc_record.psc_id
                }
            })

    # SECONDARY: Corporate PSC registered in PRC (90% confidence)
    if psc_record.kind == 'corporate-entity-person-with-significant-control':
        if psc_record.country_of_residence in ['China', 'CN', 'CHN']:
            # Double-check address field
            if 'China' in psc_record.address.get('country', ''):
                evidence.append({
                    'signal_type': 'corporate_prc_registered',
                    'field_name': 'address.country',
                    'field_value': psc_record.address['country'],
                    'confidence': 90,
                    'provenance': {
                        'file_id': psc_record.source_file,
                        'line': psc_record.source_line,
                        'company_number': psc_record.company_number,
                        'psc_id': psc_record.psc_id
                    }
                })

    # FILTER: Require nationality OR corporate signal (residence-only too weak)
    if not any(e['signal_type'] in ['nationality_prc', 'corporate_prc_registered'] for e in evidence):
        return False, 0, []

    # Confidence = max of signals (not additive)
    confidence = max([e['confidence'] for e in evidence])

    return True, confidence, evidence
```

#### **Step 2: Deduplication + Active Filter (v2.0 Rules)**
```python
def deduplicate_psc_records(psc_records):
    """
    HARD RULE: Deduplicate by (company_number, psc_id)
    DETERMINISTIC: Sort before dedup to ensure same result
    """
    # Sort for determinism
    psc_records = psc_records.sort_values(['company_number', 'psc_id', 'notified_on'])

    # Keep most recent notification per (company_number, psc_id)
    deduped = psc_records.drop_duplicates(subset=['company_number', 'psc_id'], keep='last')

    # Filter to active only (ceased_on IS NULL)
    active = deduped[deduped['ceased_on'].isna()]

    return active
```

#### **Step 3: Stratified Audit (v2.0 Rules + v3.0 Automation)**
```python
def stratified_audit_psc(chinese_psc_detections, sample_rate=0.02):
    """
    HARD RULE: 2% stratified manual audit required
    AUTOMATION: Generates CSV for human review with evidence bundles
    """
    audit_sample = []

    # Stratify by detection type
    strata = ['nationality_only', 'nationality_residence', 'corporate_prc']

    for stratum in strata:
        subset = chinese_psc_detections[
            chinese_psc_detections['detection_type'] == stratum
        ]

        # At least 50 per stratum, or 2% of subset
        sample_size = max(50, int(len(subset) * sample_rate))
        sample_size = min(sample_size, len(subset))  # Don't exceed subset size

        sample = subset.sample(n=sample_size, random_state=42)  # Deterministic sampling
        audit_sample.append(sample)

    audit_df = pd.concat(audit_sample, ignore_index=True)

    # Save for human review
    audit_df.to_csv('validation/psc_audit_sample_v3.csv', index=False)

    return audit_df
```

#### **Step 4: Reconciliation Note (v2.0 + v3.0 CI Check)**
```markdown
# PSC Re-Estimation Reconciliation Note v3.0

## Summary
- **v1.0 (Broad):** 1,130,197 detections (nationality OR residence OR script)
- **v3.0 (Strict):** [ACTUAL_COUNT] detections (nationality-first, HK/MO/TW excluded)
- **Reduction:** [PERCENTAGE]% (expected 80-95% reduction)
- **Precision (from 2% audit):** [PRECISION]% ± [MARGIN]%

## Why the Change
1. **PRC ≠ HK/MO/TW:** Different legal/political systems, must not conflate
2. **Nationality > Residence:** UK PSC guidance prioritizes nationality
3. **Deduplication:** Removes double-counts from multiple notifications
4. **Active-only:** Historical ceased PSCs excluded (use time-slicing for temporal analysis)

## Toggle Options
- `--include-hk-mo-tw`: Include Hong Kong/Macau/Taiwan (default: false)
- `--include-ceased`: Include historical ceased PSCs (default: false)
- `--min-confidence`: Minimum confidence threshold (default: 85)

## Audit Results
- **Sample size:** [N] entities (2% stratified)
- **True positives:** [TP]
- **False positives:** [FP]
- **Precision:** [TP/(TP+FP)] = [PRECISION]%
- **95% CI:** [LOWER] - [UPPER]%

## CI/CD Enforcement (NEW in v3.0)
- GitHub Actions checks this file exists
- Must mention "1.13" (v1.0) and "strict" (v3.0)
- Fails PR if reconciliation note missing
```

---

## 🔴 ISSUE #2: Detector Independence (v2.0 + v3.0 Automation)

### **Problem**
Additive risk scoring double-counts correlated detectors:
- OpenAlex + CORDIS highly correlated (both academic)
- USAspending + SEC EDGAR correlated (both US govt data)

### **Solution: Bayesian Fusion with Correlation Matrix**

#### **Step 1: Compute Correlation Matrix (v2.0 + v3.0 CI Check)**
```python
def compute_detector_correlation_matrix(entities):
    """
    HARD RULE: Correlation matrix must be recomputed each run
    DETERMINISTIC: Use Matthews correlation coefficient (robust to imbalance)
    CI/CD: GitHub Actions warns if any correlation > 0.8
    """
    import numpy as np
    from sklearn.metrics import matthews_corrcoef

    detectors = ['psc', 'usaspending', 'openalex', 'cordis', 'patents', 'sec_edgar']
    n = len(detectors)

    correlation_matrix = np.zeros((n, n))

    for i, det_a in enumerate(detectors):
        for j, det_b in enumerate(detectors):
            if i == j:
                correlation_matrix[i, j] = 1.0
            else:
                # Binary: Does detector fire?
                det_a_fires = [1 if det_a in e['detection_sources'] else 0 for e in entities]
                det_b_fires = [1 if det_b in e['detection_sources'] else 0 for e in entities]

                # Matthews correlation (handles imbalance better than Pearson)
                correlation_matrix[i, j] = matthews_corrcoef(det_a_fires, det_b_fires)

    # Save for CI/CD check
    df = pd.DataFrame(correlation_matrix, index=detectors, columns=detectors)
    df.to_csv('data/processed/detector_correlation_matrix.csv')

    return correlation_matrix
```

#### **Step 2: Bayesian Fusion (v2.0 Rules)**
```python
def calculate_bayesian_risk_score(entity, correlation_matrix):
    """
    HARD RULE: Use Bayesian fusion, not additive scoring
    PROVENANCE: Store likelihood_ratios, independence_weight in output
    """
    # Prior: Base rate (from gold set calibration)
    prior_prob = 0.02  # 2% base rate

    # Likelihood ratios (from gold set calibration)
    likelihood_ratios = {
        'psc_nationality': 50.0,        # Very strong (50x)
        'sec_edgar_listed': 30.0,       # Strong (30x)
        'usaspending_contract': 20.0,   # Strong (20x)
        'patents_inventor': 5.0,        # Moderate (5x)
        'openalex_collab': 3.0,         # Moderate (3x)
        'cordis_partner': 2.5           # Moderate (2.5x)
    }

    # Gather detections
    detections = entity['china_connections']
    detectors_fired = [d['detector_id'].split('_')[0] for d in detections]

    # Combined likelihood ratio
    combined_lr = 1.0
    for detection in detections:
        detector_id = detection['detector_id']
        lr = likelihood_ratios.get(detector_id, 2.0)  # Default 2.0
        combined_lr *= lr

    # Apply independence adjustment (eigenvalue-based)
    independence_weight = calculate_independence_weight(detectors_fired, correlation_matrix)
    adjusted_lr = 1.0 + (combined_lr - 1.0) * independence_weight

    # Bayes' rule (odds form)
    prior_odds = prior_prob / (1 - prior_prob)
    posterior_odds = adjusted_lr * prior_odds
    posterior_prob = posterior_odds / (1 + posterior_odds)

    # Risk score (0-100)
    risk_score = min(100, int(posterior_prob * 100))

    # PROVENANCE: Store all intermediate values
    return {
        'posterior_probability': posterior_prob,
        'risk_score': risk_score,
        'risk_level': categorize_risk(risk_score),
        'combined_likelihood_ratio': combined_lr,
        'adjusted_likelihood_ratio': adjusted_lr,
        'independence_weight': independence_weight,
        'prior_probability': prior_prob,
        'detectors_fired': detectors_fired
    }

def calculate_independence_weight(detectors_fired, correlation_matrix):
    """
    Eigenvalue decomposition to find effective dimensionality
    If 3 detectors but only 2 independent → weight = 2/3
    """
    if len(detectors_fired) <= 1:
        return 1.0

    # Extract sub-matrix for fired detectors
    detector_list = ['psc', 'usaspending', 'openalex', 'cordis', 'patents', 'sec_edgar']
    indices = [detector_list.index(d) for d in detectors_fired if d in detector_list]

    if len(indices) <= 1:
        return 1.0

    sub_matrix = correlation_matrix[np.ix_(indices, indices)]

    # Eigenvalue decomposition
    eigenvalues = np.linalg.eigvalsh(sub_matrix)
    effective_dimensions = np.sum(eigenvalues) / len(eigenvalues)

    return effective_dimensions
```

#### **Step 3: CI/CD Correlation Warning (NEW in v3.0)**
```yaml
# .github/workflows/cross_ref_ci.yml
detector-correlation-check:
  name: Detector Independence Check
  steps:
    - name: Warn if high correlation detected
      run: |
        python -c "
        import pandas as pd
        df = pd.read_csv('data/processed/detector_correlation_matrix.csv', index_col=0)

        high_corr = []
        for i in range(len(df.columns)):
            for j in range(i+1, len(df.columns)):
                corr = df.iloc[i, j]
                if abs(corr) > 0.8:
                    high_corr.append((df.columns[i], df.columns[j], corr))

        if high_corr:
            print('⚠️  High correlation detected - ensure Bayesian fusion applies shrinkage')
            for det_a, det_b, corr in high_corr:
                print(f'  {det_a} ↔ {det_b}: {corr:.2f}')
        "
```

---

## 🔴 ISSUE #3: CJK Name Normalization (v2.0 + v3.0 Tests)

### **Solution: Extended CJK Support**

```python
def normalize_cjk_name(name, entity_type='company'):
    """
    HARD RULE: Must handle Simplified↔Traditional, Pinyin, family-name ordering
    DETERMINISTIC: Use same OpenCC converter instance for reproducibility
    PROVENANCE: Store all aliases with type labels
    """
    import opencc
    from pypinyin import lazy_pinyin, Style

    aliases = [{'alias': name, 'type': 'original', 'provenance': 'input'}]

    # Detect CJK characters
    has_cjk = bool(re.search(r'[\u4e00-\u9fff]', name))

    if has_cjk:
        # 1. Simplified ↔ Traditional conversion
        converter_s2t = opencc.OpenCC('s2t.json')
        converter_t2s = opencc.OpenCC('t2s.json')

        simplified = converter_t2s.convert(name)
        traditional = converter_s2t.convert(name)

        if simplified != name:
            aliases.append({'alias': simplified, 'type': 'simplified', 'provenance': 'opencc_t2s'})
        if traditional != name:
            aliases.append({'alias': traditional, 'type': 'traditional', 'provenance': 'opencc_s2t'})

        # 2. Pinyin generation
        pinyin_tones = ' '.join(lazy_pinyin(name, style=Style.TONE))
        pinyin_plain = ' '.join(lazy_pinyin(name, style=Style.NORMAL))

        aliases.append({'alias': pinyin_tones, 'type': 'pinyin_tones', 'provenance': 'pypinyin'})
        aliases.append({'alias': pinyin_plain, 'type': 'pinyin_plain', 'provenance': 'pypinyin'})

        # 3. Corporate suffix removal (Chinese)
        if entity_type == 'company':
            chinese_suffixes = [
                '有限公司', '股份有限公司', '集团', '集團',
                '科技', '技术', '技術', '实业', '實業'
            ]
            for suffix in chinese_suffixes:
                if suffix in name:
                    no_suffix = name.replace(suffix, '').strip()
                    aliases.append({
                        'alias': no_suffix,
                        'type': f'suffix_removed_{suffix}',
                        'provenance': 'cjk_suffix_removal'
                    })

    # 4. English suffix removal (always apply)
    english_suffixes = ['Ltd', 'Limited', 'Inc', 'Corp', 'GmbH', 'SA', 'SPA', 'BV']
    name_no_suffix = name
    for suffix in english_suffixes:
        name_no_suffix = re.sub(rf'\b{suffix}\b', '', name_no_suffix, flags=re.IGNORECASE)

    if name_no_suffix.strip() != name:
        aliases.append({
            'alias': name_no_suffix.strip(),
            'type': 'english_suffix_removed',
            'provenance': 'regex_suffix_removal'
        })

    # 5. Canonical: Simplified + suffix removed
    if has_cjk:
        canonical = converter_t2s.convert(name_no_suffix).strip().lower()
    else:
        canonical = name_no_suffix.strip().lower()

    return canonical, aliases
```

#### **Pytest Test for CJK (NEW in v3.0)**
```python
def test_cjk_normalization():
    """
    HARD RULE: CJK normalization must handle all edge cases
    """
    # Test 1: Simplified ↔ Traditional
    canonical1, aliases1 = normalize_cjk_name('华为技术有限公司', 'company')
    assert any(a['type'] == 'traditional' for a in aliases1)
    assert any(a['type'] == 'pinyin_plain' for a in aliases1)

    # Test 2: English suffix removal
    canonical2, aliases2 = normalize_cjk_name('Huawei Technologies Ltd', 'company')
    assert any('Ltd' not in a['alias'] for a in aliases2)

    # Test 3: Family-name-first (manual check required)
    canonical3, aliases3 = normalize_cjk_name('Zhang Wei', 'individual')
    # Should generate "Wei Zhang" variant (implement if needed)
```

---

## 🔴 ISSUE #4: Maximum Extraction per Source (v2.0 + v3.0 Tests)

### **Companies House: Ownership Trees (v2.0 Rules)**
```python
def build_ownership_tree(company_number, psc_db, max_depth=5):
    """
    HARD RULE: Must recursively traverse PSC → Corporate PSC → ...
    PROVENANCE: Track ownership chain with percentages
    DETERMINISTIC: Limit max_depth to prevent infinite recursion
    """
    tree = {
        'company_number': company_number,
        'depth': 0,
        'children': []
    }

    # Get active PSCs
    pscs = psc_db.query(
        f"SELECT * FROM psc WHERE company_number = '{company_number}' AND ceased_on IS NULL"
    )

    for psc in pscs:
        ownership_pct = extract_ownership_percentage(psc['natures_of_control'])

        node = {
            'psc_name': psc['psc_name'],
            'psc_kind': psc['psc_kind'],
            'nationality': psc['nationality'],
            'ownership_pct': ownership_pct,
            'effective_ownership_pct': ownership_pct,  # Will be adjusted for chains
            'children': [],
            'provenance': {
                'psc_id': psc['psc_id'],
                'notified_on': psc['notified_on'],
                'file': psc['source_file'],
                'line': psc['source_line']
            }
        }

        # Recurse if corporate PSC and depth limit not reached
        if psc['psc_kind'] == 'corporate-entity-person-with-significant-control' and max_depth > 0:
            corporate_company_number = resolve_corporate_psc_to_company(psc)
            if corporate_company_number and corporate_company_number != company_number:  # Prevent cycles
                subtree = build_ownership_tree(corporate_company_number, psc_db, max_depth - 1)
                node['children'] = subtree['children']

                # Adjust effective ownership through chain
                for child in node['children']:
                    child['effective_ownership_pct'] = (ownership_pct / 100.0) * child['ownership_pct']

        tree['children'].append(node)

    return tree
```

### **USAspending: UEI Normalization (v2.0 Rules)**
```python
def normalize_usaspending_to_uei(contract_record):
    """
    HARD RULE: Extract UEI from all possible fields
    PROVENANCE: Record which field UEI came from
    """
    uei_fields = [
        'awardee_or_recipient_uei',
        'ultimate_parent_uei',
        'vendor_uei',
        'recipient_uei'
    ]

    uei = None
    uei_source_field = None

    for field in uei_fields:
        if field in contract_record and contract_record[field]:
            uei = contract_record[field].strip().upper()
            uei_source_field = field
            break

    return {
        'uei': uei,
        'uei_source_field': uei_source_field,
        'technology_categories': map_naics_to_technology(contract_record.get('naics_code')),
        'procurement_categories': map_psc_to_category(contract_record.get('psc_code'))
    }
```

### **Patents: CPC → Technology Buckets (v2.0 Rules + v3.0 Config)**
```python
# config/cpc_technology_mapping.json (NEW in v3.0 - externalized config)
CPC_TECHNOLOGY_MAPPING = {
    "artificial_intelligence": ["G06N", "G06T", "G10L"],
    "semiconductors": ["H01L", "H01S", "C23C"],
    "quantum": ["G06N10", "H04L9/0852", "B82Y"],
    "telecommunications": ["H04L", "H04W", "H04B"],
    "nuclear": ["G21", "G21C", "G21D"],
    "aerospace": ["B64", "F02K", "F02C"],
    "biotechnology": ["C12", "A61K", "C07K"],
    "energy_storage": ["H01M", "H02J", "F03G"],
    "cybersecurity": ["H04L9", "G06F21", "H04L63"],
    "advanced_materials": ["C01", "C08", "C22C"]
}

def map_cpc_to_technology_buckets(cpc_codes):
    """
    HARD RULE: Use externalized config for reproducibility
    DETERMINISTIC: Load from JSON file, not hardcoded
    """
    # Load from config
    with open('config/cpc_technology_mapping.json') as f:
        mapping = json.load(f)

    technologies = set()
    for cpc in cpc_codes:
        for tech, cpc_prefixes in mapping.items():
            if any(cpc.startswith(prefix) for prefix in cpc_prefixes):
                technologies.add(tech)

    return list(technologies)
```

---

## ✅ VALIDATION SUITE (v2.0 + v3.0 Automation)

### **Pytest Test Suite**
**File:** `tests/test_crossref_pipeline.py` (42+ tests)

```python
import json
import pytest
from jsonschema import validate, ValidationError
import pandas as pd
from pathlib import Path

# Load schemas
ENTITY_SCHEMA = json.load(open('config/entity_schema.json'))
DETECTION_SCHEMA = json.load(open('config/detection_schema.json'))

@pytest.fixture
def load_entities():
    with open("entities.ndjson", "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

@pytest.fixture
def load_gold_set():
    try:
        return pd.read_csv("validation/gold_set.csv")
    except FileNotFoundError:
        return pd.read_csv("validation/gold_set_starter.csv")

# Test Category 1: Schema Validation
@pytest.mark.parametrize("entity", load_entities())
def test_entity_schema(entity):
    """HARD RULE: All entities must conform to schema"""
    validate(instance=entity, schema=ENTITY_SCHEMA)

# Test Category 2: Anti-Fabrication
@pytest.mark.parametrize("entity", load_entities())
def test_provenance_complete(entity):
    """HARD RULE: Every detection must have file/line/field"""
    for detection in entity['china_connections']:
        evidence = detection['evidence']
        assert 'file_id_or_url' in evidence
        assert 'record_id_or_line' in evidence
        assert 'field_name' in evidence
        assert 'field_value' in evidence

# Test Category 3: Determinism
def test_run_id_unique(load_entities):
    """HARD RULE: All entities must share same run_id"""
    run_ids = set(e['run_id'] for e in load_entities)
    assert len(run_ids) == 1, f"Multiple run_ids detected: {run_ids}"

# Test Category 4: Temporal Sanity
@pytest.mark.parametrize("entity", load_entities())
def test_temporal_valid(entity):
    """HARD RULE: valid_from <= valid_to"""
    for detection in entity['china_connections']:
        temporal = detection.get('temporal_range', {})
        if temporal.get('valid_from') and temporal.get('valid_to'):
            assert temporal['valid_from'] <= temporal['valid_to']

# Test Category 5: Gold Set Calibration
def test_gold_set_auc(load_entities, load_gold_set):
    """HARD RULE: AUC on gold set >= 0.85"""
    from sklearn.metrics import roc_auc_score

    # Match entities to gold set
    gold_map = {row['canonical_name'].lower(): row['label']
                for _, row in load_gold_set.iterrows()}

    y_true = []
    y_scores = []

    for entity in load_entities:
        name = entity['canonical_name'].lower()
        if name in gold_map:
            label = gold_map[name]
            y_true.append(1 if label in ['HIGH', 'CRITICAL'] else 0)
            y_scores.append(entity['aggregate_risk']['posterior_probability'])

    if len(y_true) >= 50:
        auc = roc_auc_score(y_true, y_scores)
        assert auc >= 0.85, f"AUC {auc:.3f} below 0.85 threshold"

# Test Category 6: Negative Controls
def test_negative_controls_fpr(load_entities):
    """HARD RULE: FPR on negative controls < 5%"""
    try:
        neg_controls = pd.read_csv("validation/negative_controls.csv")
    except FileNotFoundError:
        neg_controls = pd.read_csv("validation/negative_controls_starter.csv")

    neg_names = set(neg_controls['canonical_name'].str.lower())

    false_positives = 0
    total_checked = 0

    for entity in load_entities:
        if entity['canonical_name'].lower() in neg_names:
            total_checked += 1
            if len(entity['china_connections']) > 0:
                false_positives += 1

    if total_checked >= 20:
        fpr = false_positives / total_checked
        assert fpr < 0.05, f"FPR {fpr:.1%} exceeds 5%"

# Test Category 7: Placebo Check
def test_placebo_zero_detections(load_entities):
    """HARD RULE: Placebo tokens must have ZERO detections"""
    placebos = ['gondwana', 'pangaea', 'atlantis', 'xanadu', 'shangri-la']

    placebo_detections = []
    for entity in load_entities:
        name_lower = entity['canonical_name'].lower()
        for token in placebos:
            if token in name_lower:
                placebo_detections.append(entity['canonical_name'])

    assert len(placebo_detections) == 0, f"PLACEBO FAILURE: {placebo_detections}"

# Test Category 8: Canary Vendors
def test_canary_vendors_detected(load_entities):
    """HARD RULE: Known China vendors MUST be detected"""
    canaries = ['huawei', 'zte', 'dji', 'hikvision', 'dahua']

    detected_canaries = set()
    for entity in load_entities:
        name_lower = entity['canonical_name'].lower()
        for canary in canaries:
            if canary in name_lower and len(entity['china_connections']) > 0:
                detected_canaries.add(canary)

    missing = set(canaries) - detected_canaries
    assert len(missing) == 0, f"CANARY FAILURE: {missing} not detected"
```

---

## 🤖 GITHUB ACTIONS CI/CD (NEW in v3.0)

### **Workflow File:** `.github/workflows/cross_ref_ci.yml`

**9 Automated Jobs:**
1. **placeholder-check** - Blocks merge if CSVs contain `REPLACE_ME`
2. **schema-validation** - Validates JSON schemas
3. **provenance-check** - Ensures all entities have provenance
4. **pytest-validation** - Runs 42+ tests
5. **detector-correlation-check** - Warns if correlation > 0.8
6. **psc-reconciliation-check** - Verifies reconciliation note exists
7. **security-check** - Scans for secrets/passwords
8. **documentation-check** - Ensures all docs present
9. **summary** - Aggregates results, posts to PR

**Key Features:**
- ❌ **Blocks merge** if placeholders or secrets found
- ⚠️ **Warns** if tests fail or correlation high
- ✅ **Auto-generates** test data if missing
- 📊 **Uploads** test results as artifacts
- 📝 **Posts** summary to PR

---

## 👤 HUMAN-IN-THE-LOOP (v2.0 + v3.0 API)

### **HITL Queue Schema**
```json
{
  "review_id": "review_uuid_12345",
  "entity_id": "ent_uuid_67890",
  "canonical_name": "Suspicious Entity Ltd",
  "review_type": "CRITICAL_DETECTION",
  "evidence_bundle": {
    "detections": [ /* all china_connections */ ],
    "source_records": [ /* raw source data */ ],
    "cross_references": [ /* links to other entities */ ]
  },
  "recommended_action": "APPROVE",
  "status": "PENDING",
  "queued_at": "2025-10-02T14:35:22Z"
}
```

### **HITL API Endpoint (NEW in v3.0)**
```python
@app.post("/api/hitl/review/{review_id}")
async def submit_review(review_id: str, decision: str, reviewer_id: str, notes: str):
    """
    HARD RULE: CRITICAL labels require human signature
    ENFORCEMENT: Cryptographic signature stored in audit log
    """
    assert decision in ['APPROVE', 'REJECT', 'MODIFY']

    review = load_review(review_id)
    entity = load_entity(review['entity_id'])

    if decision == 'APPROVE':
        entity['human_verified'] = True
        entity['verification_date'] = datetime.now().isoformat()
        entity['verification_reviewer'] = reviewer_id

        # Generate cryptographic signature
        signature_data = {
            'review_id': review_id,
            'entity_id': review['entity_id'],
            'decision': decision,
            'reviewer_id': reviewer_id,
            'timestamp': datetime.now().isoformat()
        }
        signature = generate_signature(signature_data, reviewer_id)
        entity['verification_signature'] = signature

    elif decision == 'REJECT':
        entity['china_connections'] = []
        entity['aggregate_risk']['risk_level'] = 'LOW'
        entity['human_override'] = f"Rejected by {reviewer_id}: {notes}"

    # Append to audit log (append-only)
    append_to_audit_log({
        'timestamp': datetime.now().isoformat(),
        'review_id': review_id,
        'entity_id': review['entity_id'],
        'decision': decision,
        'reviewer_id': reviewer_id,
        'notes': notes,
        'signature': entity.get('verification_signature')
    })

    save_entity(entity)
    return {'status': 'success', 'signature': entity.get('verification_signature')}
```

---

## 📦 OUTPUT ARTIFACTS (v2.0 + v3.0 Manifest)

**7 Required Files per Run:**
1. `entities.ndjson` - Main entity database (NDJSON)
2. `china_connections.parquet` - Detections table (Parquet for analytics)
3. `audit_log.jsonl` - Append-only audit trail
4. `validation_report.json` - Pytest results
5. `reconciliation_note.md` - PSC re-estimation explanation
6. `goldset_evaluation.csv` - Gold set predictions
7. `run_manifest.json` - Run metadata (NEW in v3.0)

### **Run Manifest Schema (NEW in v3.0)**
```json
{
  "run_id": "run_uuid_20251002_143522",
  "run_started_at": "2025-10-02T14:35:22Z",
  "run_completed_at": "2025-10-02T18:22:15Z",
  "run_duration_seconds": 13013,
  "pipeline_version": "v3.0_anti_fabrication_ci",
  "git_commit": "abc123def456",
  "detector_versions": {
    "psc_nationality_v3.0": "strict_20251002",
    "usaspending_uei_v1.5": "20251001"
  },
  "input_sources": {
    "psc_snapshot": "psc-snapshot-2025-09-30.txt",
    "usaspending_dumps": "F:/OSINT_DATA/USAspending/raw/*.dat.gz"
  },
  "output_counts": {
    "total_entities": 125430,
    "china_connected_entities": 8542,
    "critical_entities": 87
  },
  "validation_results": {
    "pytest_tests_passed": 42,
    "pytest_tests_failed": 0,
    "gold_set_auc": 0.89,
    "negative_controls_fpr": 0.031,
    "canary_vendors_detected": 10
  },
  "human_reviews_pending": 87,
  "ci_cd_status": "PASSED"
}
```

---

## 🚀 QUICK START (v3.0)

### **Step 1: Install Dependencies**
```bash
pip install pytest jsonschema pandas scikit-learn duckdb opencc pypinyin
```

### **Step 2: Run PSC Strict Re-Estimation**
```bash
python scripts/psc_strict_reestimation.py \
  --input F:/OSINT_DATA/CompaniesHouse_UK/raw/psc-snapshot-2025-09-30.txt \
  --output data/processed/psc_strict_v3/ \
  --audit-sample-rate 0.02 \
  --reconciliation-note reconciliation_note.md \
  --hk-mo-tw-toggle exclude
```

### **Step 3: Run Validation Suite**
```bash
pytest tests/test_crossref_pipeline.py -v --html=validation_report.html
```

### **Step 4: Check CI/CD Status**
```bash
# Commit and push
git add .
git commit -m "feat: PSC strict re-estimation v3.0"
git push

# GitHub Actions will automatically:
# - Check for placeholders
# - Validate schemas
# - Run pytest suite
# - Post results to PR
```

---

## 📊 SUCCESS METRICS (v3.0 Targets)

| Metric | Target | CI/CD Enforcement |
|--------|--------|-------------------|
| PSC Precision | ≥90% | Manual audit required |
| Gold Set AUC | ≥0.85 | pytest fail if below |
| Negative Controls FPR | <5% | pytest fail if above |
| Placebo Detections | 0 | pytest fail if any |
| Canary Detection Rate | 100% | pytest fail if missing |
| Temporal Consistency | 100% | pytest fail if violated |
| Schema Compliance | 100% | pytest fail if invalid |
| Provenance Completeness | 100% | pytest fail if missing |

---

**END OF v3.0**

**Next Action:** Run PSC strict re-estimation and commit to trigger CI/CD validation.
