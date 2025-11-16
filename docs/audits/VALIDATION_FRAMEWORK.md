# Cross-Reference Analysis Validation Framework
**Date:** October 2, 2025
**Version:** 2.0 (Anti-Fabrication + Stress Tests)
**Purpose:** Comprehensive validation, testing, and quality assurance framework

---

## 🎯 OVERVIEW

This framework implements **strict anti-fabrication rules**, **validation harnesses**, and **stress testing** for the cross-reference analysis pipeline.

### **Hard Rules (Non-Negotiable)**
1. **NO FABRICATION** — Every claim backed by explicit provenance
2. **PROVENANCE REQUIRED** — Structured evidence for every detection
3. **DETERMINISTIC OUTPUTS** — Identical results on same inputs
4. **HITL FOR CRITICAL** — Human sign-off required for CRITICAL/SANCTIONED labels
5. **FAIL CLOSED** — Missing data → explicit `incomplete: true`, no guesses

---

## 📋 REQUIRED EVIDENCE FORMAT

### **Detection Evidence Schema (JSON)**
```json
{
  "detection_id": "det_uuid_12345",
  "entity_id": "ent_uuid_67890",
  "detector_id": "psc_nationality_v2.0",
  "detector_version": "v2.0_strict_20251002",
  "confidence_score": 95,
  "evidence": {
    "file_id_or_url": "psc-snapshot-2025-09-30.txt",
    "record_id_or_line": "line_123456",
    "field_name": "nationality",
    "field_value": "Chinese",
    "extraction_method": "direct_field_read",
    "feature_hash": "sha256:abc123..."
  },
  "temporal_range": {
    "valid_from": "2020-01-15",
    "valid_to": "9999-12-31",
    "inferred": false
  },
  "incomplete": false,
  "human_verified": false,
  "verification_signature": null
}
```

### **Entity Output Schema (NDJSON)**
```json
{
  "run_id": "run_uuid_20251002_143522",
  "entity_id": "ent_uuid_67890",
  "canonical_name": "Example Company Ltd",
  "entity_type": "company",
  "country_iso3": "GBR",
  "aliases": [
    {"name": "Example Company Limited", "type": "original", "provenance": "companies_house"},
    {"name": "Example Co", "type": "suffix_removed", "provenance": "normalization"}
  ],
  "ids": {
    "companies_house": "12345678",
    "lei": "5493001234567890",
    "uei": "ABC123DEF456",
    "cik": null
  },
  "china_connections": [
    {
      "detection_id": "det_uuid_12345",
      "detector_id": "psc_nationality_v2.0",
      "confidence_score": 95,
      "evidence": { /* see above */ },
      "temporal_range": { /* see above */ },
      "incomplete": false
    }
  ],
  "aggregate_risk": {
    "posterior_probability": 0.78,
    "risk_score": 78,
    "risk_level": "HIGH",
    "detector_independence_weight": 0.85,
    "likelihood_ratio_combined": 12.5,
    "human_override": null
  },
  "detector_versions": {
    "psc_nationality": "v2.0_strict_20251002",
    "usaspending_uei": "v1.5_20251001"
  },
  "provenance": {
    "primary_source": "companies_house_psc",
    "secondary_sources": ["usaspending", "patents"],
    "last_updated": "2025-10-02T14:35:22Z"
  },
  "incomplete_fields": [],
  "human_verified": false,
  "verification_date": null,
  "verification_reviewer": null
}
```

---

## 🚫 ANTI-FABRICATION ENFORCEMENTS

### **1. Provenance Gates**
```python
def validate_detection_provenance(detection):
    """
    Enforce provenance requirements - FAIL if missing
    """
    required_evidence_fields = [
        'file_id_or_url',
        'record_id_or_line',
        'field_name',
        'field_value',
        'extraction_method'
    ]

    missing = [f for f in required_evidence_fields if f not in detection['evidence']]

    if missing:
        raise ValueError(f"Detection {detection['detection_id']} missing provenance: {missing}")

    # Verify file exists
    file_path = detection['evidence']['file_id_or_url']
    if not os.path.exists(file_path) and not file_path.startswith('http'):
        raise ValueError(f"Provenance file not found: {file_path}")

    return True
```

### **2. No Inferred Dates Without Labels**
```python
def validate_temporal_range(temporal_range):
    """
    Ensure all date inferences are explicitly labeled
    """
    if temporal_range.get('inferred') is None:
        raise ValueError("Temporal range missing 'inferred' flag")

    if temporal_range['inferred']:
        if 'inference_method' not in temporal_range:
            raise ValueError("Inferred date missing 'inference_method'")

    # Check chronological order
    if temporal_range['valid_from'] > temporal_range['valid_to']:
        raise ValueError(f"Temporal inversion: {temporal_range['valid_from']} > {temporal_range['valid_to']}")

    return True
```

### **3. Reject Hallucinated Text**
```python
def validate_no_hallucination(entity_output, source_databases):
    """
    Cross-check all entity data against source records
    """
    # For each detection, verify field value matches source
    for detection in entity_output['china_connections']:
        evidence = detection['evidence']

        # Load source record
        source_record = fetch_source_record(
            evidence['file_id_or_url'],
            evidence['record_id_or_line']
        )

        # Verify field value
        actual_value = source_record.get(evidence['field_name'])
        claimed_value = evidence['field_value']

        if actual_value != claimed_value:
            raise ValueError(
                f"HALLUCINATION DETECTED: "
                f"Claimed '{claimed_value}' but source has '{actual_value}' "
                f"in {evidence['file_id_or_url']}:{evidence['record_id_or_line']}"
            )

    return True
```

### **4. Sampling-Based Audits**
```python
def run_sampling_audit(entity_outputs, sample_rate=0.02):
    """
    Randomly sample 2% of detections and verify provenance
    """
    all_detections = []
    for entity in entity_outputs:
        for detection in entity['china_connections']:
            all_detections.append((entity['entity_id'], detection))

    sample_size = max(100, int(len(all_detections) * sample_rate))
    sample = random.sample(all_detections, sample_size)

    audit_results = []
    for entity_id, detection in sample:
        try:
            validate_detection_provenance(detection)
            validate_no_hallucination({'china_connections': [detection]}, source_databases)
            audit_results.append({
                'entity_id': entity_id,
                'detection_id': detection['detection_id'],
                'status': 'PASS',
                'error': None
            })
        except Exception as e:
            audit_results.append({
                'entity_id': entity_id,
                'detection_id': detection['detection_id'],
                'status': 'FAIL',
                'error': str(e)
            })

    failures = [r for r in audit_results if r['status'] == 'FAIL']
    failure_rate = len(failures) / len(audit_results)

    if failure_rate > 0.05:  # >5% failure = pipeline failure
        raise ValueError(f"Audit failure rate {failure_rate:.1%} exceeds 5% threshold")

    return audit_results
```

---

## 🎯 GOLD SET & VALIDATION TARGETS

### **Gold Set Structure (300 Entities)**

**Distribution:**
- **100 HIGH:** Verified China-connected entities (not critical sectors)
- **100 LOW:** Verified NOT China-connected (clean entities)
- **100 CRITICAL:** High-risk China-connected (critical tech + govt contracts)

**Gold Set CSV Schema:**
See: `validation/gold_set.csv` (template provided)

**Required Fields:**
- `canonical_name` - Entity name
- `entity_type` - company/institution/individual
- `country_iso3` - ISO 3166-1 alpha-3
- `label` - HIGH/LOW/CRITICAL
- `justification_summary` - Why this label (human-verified)
- `ids__*` - All known identifiers (companies_house, LEI, ROR, etc.)
- `provenance__primary_source` - Where verified
- `sanctions_lists` - OFAC/EU/UK list memberships
- `technology_buckets` - AI/semiconductors/quantum/etc.
- `reviewer` - Who verified this entity
- `review_date` - When verified

### **Negative Controls (200 Entities)**

**Purpose:** Test false positive rate on entities that LOOK Chinese but aren't

**Examples:**
- Chang Enterprises (US company, Korean surname)
- Li & Fung Limited (Hong Kong, not PRC)
- Beijing Restaurant (Named after city, US-owned)
- Shanghai Banking Corporation (Historical name, UK bank)

**Negative Controls CSV Schema:**
See: `validation/negative_controls.csv` (template provided)

**Required Fields:**
- `canonical_name` - Entity name
- `lookalike_features` - Why it might be detected (Chinese name, HK address, etc.)
- `reason_clean` - Why it's actually NOT China-connected
- `ids__*` - Known identifiers for lookup
- `provenance__clean_sources` - Sources confirming it's clean

### **Placebo Tokens (20 Random Strings)**

**Purpose:** Estimate false discovery rate (any detections = guaranteed false positives)

**Examples:**
```python
PLACEBO_TOKENS = [
    'Gondwana', 'Pangaea', 'Atlantis', 'Xanadu', 'Shangri-La',
    'Zephyr', 'Quixote', 'Nebula', 'Zenith', 'Aurora',
    'Elysium', 'Valhalla', 'Arcadia', 'Utopia', 'Olympus',
    'Avalon', 'Camelot', 'Narnia', 'Oz', 'Wonderland'
]
```

**Test:**
```python
def test_placebo_detections(entity_outputs, placebo_tokens):
    """
    Search for placebo tokens - ANY detection is a failure
    """
    placebo_detections = []

    for entity in entity_outputs:
        name_lower = entity['canonical_name'].lower()
        for token in placebo_tokens:
            if token.lower() in name_lower:
                placebo_detections.append({
                    'entity_id': entity['entity_id'],
                    'entity_name': entity['canonical_name'],
                    'placebo_token': token,
                    'china_connections': len(entity['china_connections'])
                })

    if placebo_detections:
        raise ValueError(f"PLACEBO FAILURE: {len(placebo_detections)} placebo tokens detected as entities")

    return True
```

---

## ✅ VALIDATION SUITE (pytest)

### **File:** `tests/test_crossref_pipeline.py`

```python
import json
import pytest
from jsonschema import validate, ValidationError
from pathlib import Path
import pandas as pd
from datetime import datetime

# Load schemas
ENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "run_id": {"type": "string"},
        "entity_id": {"type": "string"},
        "canonical_name": {"type": "string"},
        "entity_type": {"type": "string", "enum": ["company", "institution", "individual", "government"]},
        "country_iso3": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "china_connections": {"type": "array"},
        "aggregate_risk": {
            "type": "object",
            "required": ["posterior_probability", "risk_score", "risk_level"]
        },
        "detector_versions": {"type": "object"},
        "incomplete_fields": {"type": "array"}
    },
    "required": ["run_id", "entity_id", "canonical_name", "china_connections", "detector_versions"]
}

DETECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "detection_id": {"type": "string"},
        "detector_id": {"type": "string"},
        "confidence_score": {"type": "number", "minimum": 0, "maximum": 100},
        "evidence": {
            "type": "object",
            "required": ["file_id_or_url", "record_id_or_line", "field_name", "field_value"]
        },
        "temporal_range": {
            "type": "object",
            "required": ["valid_from", "valid_to", "inferred"]
        },
        "incomplete": {"type": "boolean"}
    },
    "required": ["detection_id", "detector_id", "confidence_score", "evidence"]
}

# Fixtures
@pytest.fixture
def load_entities():
    """Load entities.ndjson output"""
    with open("entities.ndjson", "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

@pytest.fixture
def load_gold_set():
    """Load gold set CSV"""
    return pd.read_csv("validation/gold_set.csv")

@pytest.fixture
def load_negative_controls():
    """Load negative controls CSV"""
    return pd.read_csv("validation/negative_controls.csv")

# Test 1: Schema Validation
@pytest.mark.parametrize("entity", load_entities())
def test_entity_schema_valid(entity):
    """Every entity must conform to schema"""
    try:
        validate(instance=entity, schema=ENTITY_SCHEMA)
    except ValidationError as e:
        pytest.fail(f"Entity schema validation failed: {e}")

@pytest.mark.parametrize("entity", load_entities())
def test_detection_schema_valid(entity):
    """Every detection must conform to schema"""
    for detection in entity.get("china_connections", []):
        try:
            validate(instance=detection, schema=DETECTION_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"Detection schema validation failed: {e}")

# Test 2: Anti-Fabrication
@pytest.mark.parametrize("entity", load_entities())
def test_provenance_required(entity):
    """Every detection must have complete provenance"""
    for detection in entity.get("china_connections", []):
        evidence = detection.get("evidence", {})
        required = ["file_id_or_url", "record_id_or_line", "field_name", "field_value"]
        missing = [f for f in required if f not in evidence]
        assert not missing, f"Missing provenance fields: {missing}"

@pytest.mark.parametrize("entity", load_entities())
def test_no_inferred_without_label(entity):
    """Inferred dates must be explicitly labeled"""
    for detection in entity.get("china_connections", []):
        temporal = detection.get("temporal_range", {})
        if temporal:
            assert "inferred" in temporal, "Missing 'inferred' flag in temporal_range"
            if temporal["inferred"]:
                assert "inference_method" in temporal, "Inferred date missing 'inference_method'"

# Test 3: Determinism
@pytest.mark.parametrize("entity", load_entities())
def test_run_id_present(entity):
    """Every entity must have run_id for reproducibility"""
    assert "run_id" in entity, "Missing run_id"
    assert entity["run_id"].startswith("run_"), "Invalid run_id format"

@pytest.mark.parametrize("entity", load_entities())
def test_detector_versions_present(entity):
    """Every entity must declare detector versions"""
    assert "detector_versions" in entity, "Missing detector_versions"
    assert isinstance(entity["detector_versions"], dict), "detector_versions must be dict"

def test_round_trip_determinism(load_entities):
    """Re-running on same input should produce identical results"""
    # Load current run entities
    entities_run1 = load_entities

    # Load previous run (if exists)
    previous_run_path = Path("entities_previous.ndjson")
    if previous_run_path.exists():
        with open(previous_run_path, "r", encoding="utf-8") as f:
            entities_run2 = [json.loads(line) for line in f]

        # Compare (excluding run_id, timestamps)
        assert len(entities_run1) == len(entities_run2), "Different entity counts"

        for e1, e2 in zip(entities_run1, entities_run2):
            assert e1['entity_id'] == e2['entity_id'], "Entity ID mismatch"
            assert e1['canonical_name'] == e2['canonical_name'], "Name mismatch"
            assert len(e1['china_connections']) == len(e2['china_connections']), "Detection count mismatch"

# Test 4: Temporal Sanity
@pytest.mark.parametrize("entity", load_entities())
def test_temporal_chronological(entity):
    """valid_from must be <= valid_to"""
    for detection in entity.get("china_connections", []):
        temporal = detection.get("temporal_range", {})
        if temporal and temporal.get("valid_from") and temporal.get("valid_to"):
            assert temporal["valid_from"] <= temporal["valid_to"], \
                f"Temporal inversion: {temporal['valid_from']} > {temporal['valid_to']}"

# Test 5: Gold Set Evaluation
def test_gold_set_auc(load_entities, load_gold_set):
    """AUC on gold set must be >= 0.85"""
    from sklearn.metrics import roc_auc_score

    # Match entities to gold set
    gold_entities = {}
    for _, row in load_gold_set.iterrows():
        gold_entities[row['canonical_name'].lower()] = row['label']

    y_true = []
    y_scores = []

    for entity in load_entities:
        name_lower = entity['canonical_name'].lower()
        if name_lower in gold_entities:
            label = gold_entities[name_lower]
            y_true.append(1 if label in ['HIGH', 'CRITICAL'] else 0)
            y_scores.append(entity['aggregate_risk']['posterior_probability'])

    if len(y_true) >= 50:  # Need sufficient gold set matches
        auc = roc_auc_score(y_true, y_scores)
        assert auc >= 0.85, f"AUC {auc:.3f} below 0.85 threshold"

# Test 6: Negative Controls (False Positive Rate)
def test_negative_controls_fpr(load_entities, load_negative_controls):
    """False positive rate on negative controls must be < 5%"""
    negative_names = set(load_negative_controls['canonical_name'].str.lower())

    false_positives = 0
    total_checked = 0

    for entity in load_entities:
        name_lower = entity['canonical_name'].lower()
        if name_lower in negative_names:
            total_checked += 1
            if len(entity['china_connections']) > 0:
                false_positives += 1

    if total_checked >= 20:  # Need sufficient negative controls
        fpr = false_positives / total_checked
        assert fpr < 0.05, f"False positive rate {fpr:.1%} exceeds 5%"

# Test 7: Placebo Check
def test_placebo_zero_detections(load_entities):
    """Placebo tokens must have ZERO detections"""
    placebo_tokens = [
        'gondwana', 'pangaea', 'atlantis', 'xanadu', 'shangri-la',
        'zephyr', 'quixote', 'nebula', 'zenith', 'aurora'
    ]

    placebo_detections = []
    for entity in load_entities:
        name_lower = entity['canonical_name'].lower()
        for token in placebo_tokens:
            if token in name_lower:
                placebo_detections.append(entity['canonical_name'])

    assert len(placebo_detections) == 0, \
        f"PLACEBO FAILURE: Found {len(placebo_detections)} placebo entities"

# Test 8: Canary Vendors
def test_canary_vendors_detected(load_entities):
    """Known China-linked vendors MUST be detected"""
    canary_vendors = [
        'huawei', 'zte', 'dji', 'hikvision', 'dahua',
        'bytedance', 'tiktok', 'alibaba', 'tencent', 'baidu'
    ]

    detected_canaries = set()
    for entity in load_entities:
        name_lower = entity['canonical_name'].lower()
        for canary in canary_vendors:
            if canary in name_lower and len(entity['china_connections']) > 0:
                detected_canaries.add(canary)

    missing_canaries = set(canary_vendors) - detected_canaries
    assert len(missing_canaries) == 0, \
        f"CANARY FAILURE: Missing detections for {missing_canaries}"
```

---

## 🔥 STRESS TESTS

### **Stress Test 1: Mass Missing Fields (PSC)**
```python
def test_psc_missing_nationality_handling():
    """
    Test PSC processor with 50% missing nationality fields
    Should NOT fabricate, should mark incomplete
    """
    # Create test PSC data with missing fields
    test_psc = [
        {"company_number": "12345", "psc_name": "John Doe", "nationality": "Chinese"},  # Complete
        {"company_number": "67890", "psc_name": "Jane Smith", "nationality": None},     # Missing
        {"company_number": "11111", "psc_name": "李明", "nationality": None},            # Missing + Chinese chars
    ]

    results = process_psc_strict(test_psc)

    # Check: No fabrication
    for result in results:
        if result['incomplete']:
            assert 'nationality' in result['incomplete_fields']
            assert result['china_connection_confidence'] == 0 or 'residence' in result['evidence']
```

### **Stress Test 2: Corrupted Encodings**
```python
def test_corrupted_utf8_handling():
    """
    Test entity resolution with corrupted UTF-8 characters
    Should gracefully handle, not crash
    """
    corrupted_names = [
        "Huawei\x00Technologies",  # Null byte
        "�北京�科技",                # Replacement characters
        bytes.fromhex('C3 28').decode('utf-8', errors='replace')  # Invalid UTF-8
    ]

    for name in corrupted_names:
        try:
            normalized = normalize_company_name(name)
            assert normalized is not None, "Returned None instead of handling error"
        except Exception as e:
            pytest.fail(f"Crashed on corrupted input: {e}")
```

### **Stress Test 3: High-Similarity Flood**
```python
def test_high_similarity_flood():
    """
    Test entity resolution with 1000 near-identical names
    Should not merge incorrectly, should maintain disambiguation
    """
    flood_names = [f"Huawei Technology Co Ltd {i}" for i in range(1000)]

    entities = [create_test_entity(name, country='CN') for name in flood_names]
    resolved = entity_resolution_pipeline(entities)

    # Should NOT collapse all into one entity
    assert len(resolved) >= 900, f"Over-merged: {len(resolved)} entities from 1000"

    # Should use network disambiguation (addresses, registration numbers)
    for entity in resolved:
        if len(entity['merged_from']) > 1:
            # If merged, must have confirming signals
            assert 'shared_address' in entity['merge_evidence'] or \
                   'shared_directors' in entity['merge_evidence']
```

### **Stress Test 4: Temporal Inversion**
```python
def test_temporal_inversion_rejection():
    """
    Test that temporally impossible events are rejected
    """
    # PSC notified AFTER company dissolved
    invalid_entity = {
        'company_number': '12345',
        'incorporation_date': '2015-01-01',
        'dissolution_date': '2020-12-31',
        'psc_records': [
            {'notified_on': '2021-05-15', 'nationality': 'Chinese'}  # AFTER dissolution!
        ]
    }

    with pytest.raises(ValueError, match="PSC notified after dissolution"):
        validate_temporal_consistency(invalid_entity)
```

### **Stress Test 5: ETL Backfill Correctness**
```python
def test_etl_backfill_idempotency():
    """
    Test that re-running ETL on same data produces identical results
    """
    # Run ETL twice on same input
    results_run1 = run_etl_pipeline('test_data.csv', run_id='run1')
    results_run2 = run_etl_pipeline('test_data.csv', run_id='run2')

    # Compare (excluding run_id, timestamps)
    assert len(results_run1) == len(results_run2)

    for r1, r2 in zip(results_run1, results_run2):
        assert r1['entity_id'] == r2['entity_id']
        assert r1['canonical_name'] == r2['canonical_name']
        assert r1['aggregate_risk']['risk_score'] == r2['aggregate_risk']['risk_score']
```

---

## 👤 HUMAN-IN-THE-LOOP (HITL)

### **HITL Policy**
- **CRITICAL detections** → Queue for human review BEFORE publication
- **SANCTIONED entities** → Mandatory review + legal sign-off
- **Low-confidence merges** (fuzzy matching <85%) → Human disambiguation

### **HITL Queue Schema**
```json
{
  "review_id": "review_uuid_12345",
  "entity_id": "ent_uuid_67890",
  "canonical_name": "Suspicious Entity Ltd",
  "review_type": "CRITICAL_DETECTION",
  "evidence_bundle": {
    "detections": [ /* all china_connections */ ],
    "source_records": [ /* original source data snapshots */ ],
    "cross_references": [ /* links to other entities */ ]
  },
  "recommended_action": "APPROVE",
  "reviewer_notes": "",
  "status": "PENDING",
  "queued_at": "2025-10-02T14:35:22Z",
  "reviewed_at": null,
  "reviewer_id": null,
  "decision": null,  // APPROVE, REJECT, MODIFY
  "signature": null  // Cryptographic signature
}
```

### **HITL API Endpoint**
```python
@app.post("/api/hitl/review/{review_id}")
def submit_review(review_id: str, decision: str, reviewer_id: str, notes: str):
    """
    Submit human review decision
    """
    # Validate decision
    assert decision in ['APPROVE', 'REJECT', 'MODIFY']

    # Load review
    review = load_review(review_id)

    # Update entity
    entity = load_entity(review['entity_id'])

    if decision == 'APPROVE':
        entity['human_verified'] = True
        entity['verification_date'] = datetime.now().isoformat()
        entity['verification_reviewer'] = reviewer_id
    elif decision == 'REJECT':
        entity['china_connections'] = []  # Clear detections
        entity['aggregate_risk']['risk_level'] = 'LOW'
        entity['human_override'] = f"Rejected by {reviewer_id}: {notes}"

    # Create signature
    signature = sign_decision(review_id, decision, reviewer_id)

    # Log audit trail
    append_to_audit_log({
        'timestamp': datetime.now().isoformat(),
        'review_id': review_id,
        'entity_id': review['entity_id'],
        'decision': decision,
        'reviewer_id': reviewer_id,
        'notes': notes,
        'signature': signature
    })

    return {'status': 'success', 'signature': signature}
```

---

## 📦 OUTPUT ARTIFACTS

### **Required Outputs (Every Run)**
1. **`entities.ndjson`** - Main entity database (NDJSON format)
2. **`china_connections.parquet`** - Detections table (Parquet for analytics)
3. **`audit_log.jsonl`** - Append-only audit trail
4. **`validation_report.json`** - Test results from pytest suite
5. **`reconciliation_note.md`** - PSC re-estimation explanation
6. **`goldset_evaluation.csv`** - Gold set predictions vs. labels
7. **`run_manifest.json`** - Run metadata (run_id, timestamps, versions)

### **Run Manifest Schema**
```json
{
  "run_id": "run_uuid_20251002_143522",
  "run_started_at": "2025-10-02T14:35:22Z",
  "run_completed_at": "2025-10-02T18:22:15Z",
  "run_duration_seconds": 13013,
  "input_sources": {
    "psc_snapshot": "psc-snapshot-2025-09-30.txt",
    "usaspending_dumps": "F:/OSINT_DATA/USAspending/raw/*.dat.gz",
    "openalex_partitions": "F:/OSINT_Backups/openalex/*.gz",
    "companies_house_basic": "BasicCompanyDataAsOneFile-2025-09-01.zip"
  },
  "detector_versions": {
    "psc_nationality_v2.0": "strict_20251002",
    "usaspending_uei_v1.5": "20251001",
    "openalex_collab_v1.3": "20250930"
  },
  "output_counts": {
    "total_entities": 125430,
    "china_connected_entities": 8542,
    "high_risk_entities": 1253,
    "critical_entities": 87
  },
  "validation_results": {
    "pytest_tests_passed": 42,
    "pytest_tests_failed": 0,
    "gold_set_auc": 0.89,
    "negative_controls_fpr": 0.031,
    "placebo_detections": 0,
    "canary_vendors_detected": 10
  },
  "human_reviews_pending": 87,
  "pipeline_version": "v2.0_anti_fabrication",
  "git_commit": "abc123def456"
}
```

---

## 🚀 QUICK START IMPLEMENTATION

### **Step 1: Set Up Test Infrastructure**
```bash
# Create validation directory
mkdir -p validation tests

# Copy templates
cp gold_set_template.csv validation/gold_set.csv
cp negative_controls_template.csv validation/negative_controls.csv

# Install dependencies
pip install pytest jsonschema pandas scikit-learn duckdb psycopg2
```

### **Step 2: Build Gold Set (Manual)**
```
1. Identify 100 HIGH entities (e.g., Huawei subsidiaries, China ADRs)
2. Identify 100 LOW entities (e.g., Western companies no China links)
3. Identify 100 CRITICAL entities (e.g., Huawei + semiconductors + US contracts)
4. Fill out validation/gold_set.csv with full provenance
```

### **Step 3: Build Negative Controls (Manual)**
```
1. Find entities with Chinese-sounding names but NOT Chinese
2. Find HK/MO/TW entities to test strict PRC distinction
3. Find entities named after Chinese cities but Western-owned
4. Fill out validation/negative_controls.csv
```

### **Step 4: Run PSC Strict Re-Estimation**
```bash
python scripts/psc_strict_reestimation.py \
  --input F:/OSINT_DATA/CompaniesHouse_UK/raw/psc-snapshot-2025-09-30.txt \
  --output data/processed/psc_strict_v2/ \
  --audit-sample-rate 0.02 \
  --reconciliation-note reconciliation_note.md
```

### **Step 5: Run Full Pipeline**
```bash
python scripts/cross_reference_pipeline_v2.py \
  --run-id $(uuidgen) \
  --config config/pipeline_config_v2.yaml \
  --output entities.ndjson
```

### **Step 6: Run Validation Suite**
```bash
pytest tests/test_crossref_pipeline.py -v --html=validation_report.html
```

### **Step 7: Review HITL Queue**
```bash
python scripts/hitl_review_ui.py --queue data/hitl_queue.jsonl
```

---

**END OF VALIDATION FRAMEWORK**

**Next Action:** Populate gold set and negative controls templates, then implement pytest suite.
