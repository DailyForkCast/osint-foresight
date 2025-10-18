# Claude Code Master Prompt v9.3 — ENFORCEMENT EDITION
## Data-First Reality with Mandatory Connection to 445GB

**PRIME DIRECTIVE:** Process actual data (445GB available) before any analysis. No narratives without data. No frameworks without evidence.

**ENFORCEMENT MODE:** Every claim must trace to machine-readable data with recompute command, or return INSUFFICIENT_EVIDENCE.

---

## 🚨 MANDATORY DATA CONNECTION CHECK

**BEFORE ANY ANALYSIS:**
```python
def pre_flight_data_check():
    available_data = {
        "OpenAlex": "420GB - academic papers",
        "TED": "24GB - EU procurement",
        "SEC_EDGAR": "downloaded filings",
        "USPTO": "patent database",
        "USAspending": "contract data"
    }

    collectors_available = 56  # Built but disconnected

    if not connected_to_actual_data():
        return "STOP: Connect to data first. 445GB waiting."

    if using_fabricated_examples():
        return "STOP: Use real data, not examples."

    return "PROCEED with actual data"
```

---

## A) UNIFIED CONFIDENCE SCALE (MANDATORY)

**ONLY ONE SCALE ALLOWED:** 0.0 to 1.0
```python
CONFIDENCE_SCALE = {
    0.9-1.0: "Very High - Multiple primary sources with data artifacts",
    0.7-0.9: "High - Primary source with verification",
    0.5-0.7: "Moderate - Secondary sources or partial data",
    0.3-0.5: "Low - Weak sources or significant gaps",
    0.0-0.3: "Insufficient - Return INSUFFICIENT_EVIDENCE"
}

# BANNED: Low/Medium/High without numbers
# BANNED: 0-20 scoring systems
# BANNED: Multiple scales in same analysis
```

---

## B) MANDATORY PHASE DEPENDENCIES

**ENFORCEMENT GATE:**
```python
PHASE_DEPENDENCIES = {
    "Phase_1": [],  # Can start immediately
    "Phase_2": ["Phase_1"],  # Requires Phase 1
    "Phase_3": ["Phase_1", "Phase_2"],
    "Phase_4": ["Phase_1", "Phase_2", "Phase_3"],
    "Phase_8_Risk": ["Phase_1", "Phase_2", "Phase_3", "Phase_4", "Phase_5", "Phase_6", "Phase_7"]
}

def enforce_phase_order(requested_phase, completed_phases):
    required = PHASE_DEPENDENCIES[requested_phase]
    missing = [p for p in required if p not in completed_phases]

    if missing:
        return f"BLOCKED: Complete {missing} before {requested_phase}"
    return "PROCEED"
```

**NO JUMPING TO PHASE 8 WITHOUT 1-7 COMPLETE**

---

## C) MANDATORY COUNTERFACTUAL TESTING

**For EVERY positive finding:**
```python
def mandatory_counterfactual(finding):
    counterfactual_queries = [
        f"NO {finding}",
        f"NOT {finding}",
        f"{finding} debunked",
        f"{finding} false",
        f"{finding} disputed"
    ]

    results = {}
    for query in counterfactual_queries:
        results[query] = search_actual_data(query)  # MUST search real data

    if contradicting_evidence_found(results):
        return {
            "finding": finding,
            "supporting": count_supporting,
            "contradicting": count_contradicting,
            "confidence": adjust_confidence_down()
        }

    return results
```

**REQUIREMENT:** 5+ counterfactual queries per Tier-A claim

---

## D) ECHO CHAMBER DETECTION (MANDATORY)

```python
def detect_echo_chamber(sources):
    origin_tracking = {}

    for source in sources:
        # Trace to original
        original = trace_to_primary_source(source)
        origin_tracking[original] = origin_tracking.get(original, 0) + 1

    # Check for single origin
    if len(origin_tracking) == 1:
        return "ECHO CHAMBER: All sources trace to single origin"

    # Check for wire copy
    if is_wire_service(list(origin_tracking.keys())[0]):
        return "WIRE COPY: Not independent sources"

    return "INDEPENDENT: Multiple origins confirmed"
```

---

## E) ADMIRALTY RATINGS (MANDATORY FOR EVERY SOURCE)

```python
def rate_source(source):
    # REQUIRED - Cannot proceed without rating
    reliability = assign_reliability(source)  # A-F
    credibility = assign_credibility(source)  # 1-6

    if not reliability or not credibility:
        return "STOP: Admiralty rating required"

    # Automatic confidence adjustment
    if reliability >= 'D' or credibility >= 4:
        confidence_cap = 0.5  # Low quality sources cap confidence

    return f"{source} [{reliability}{credibility}]"
```

**NO SOURCE WITHOUT RATING**

---

## F) MCF SOURCE CONNECTION (URGENT)

**50 MCF sources identified but disconnected. CONNECT NOW:**
```python
MCF_SOURCES = {
    "TIER_1_MUST_CONNECT": [
        "NDU_CSCMA",
        "CASI",
        "State_Dept_MCF",
        "ASPI_Critical_Tech",
        "USCC"
    ],
    "status": "DISCONNECTED - CRITICAL FAILURE"
}

def connect_mcf_sources():
    for source in MCF_SOURCES["TIER_1_MUST_CONNECT"]:
        if not is_connected(source):
            return "STOP: MCF blindness - connect sources first"
```

---

## G) REGRESSION TEST SUITE (AUTOMATED)

**Run on EVERY analysis:**
```python
REGRESSION_TESTS = [
    "test_no_unsourced_numbers",  # Would catch "78 transfers"
    "test_admiralty_ratings_present",
    "test_counterfactuals_executed",
    "test_echo_chamber_check",
    "test_confidence_single_scale",
    "test_phase_dependencies_met",
    "test_data_actually_searched",
    "test_insufficient_evidence_used"
]

def run_regression_suite(analysis):
    failures = []
    for test in REGRESSION_TESTS:
        if not execute_test(test, analysis):
            failures.append(test)

    if failures:
        return f"ANALYSIS REJECTED: Failed {failures}"
    return "PASSED regression suite"
```

---

## H) STATISTICAL BASELINES (REQUIRED)

**Cannot assess without baselines:**
```python
BASELINES_REQUIRED = {
    "personnel_transfers": {
        "industry_avg": "get from data",
        "company_size_adjusted": "calculate from peers",
        "temporal_pattern": "extract from historical"
    },
    "patent_collaboration": {
        "global_average": "calculate from USPTO",
        "sector_specific": "extract from OpenAlex",
        "country_pair_normal": "derive from data"
    }
}

def assess_anomaly(value, metric):
    if metric not in BASELINES_REQUIRED:
        return "INSUFFICIENT_EVIDENCE: No baseline for comparison"

    baseline = calculate_baseline_from_actual_data(metric)
    z_score = (value - baseline.mean) / baseline.std

    return {
        "value": value,
        "baseline": baseline.mean,
        "z_score": z_score,
        "anomalous": abs(z_score) > 2
    }
```

---

## I) DATA REALITY ENFORCEMENT

**The 445GB Reality Check:**
```python
DATA_REALITY = {
    "OpenAlex": {
        "size": "420GB",
        "status": "UNPROCESSED",
        "action": "START PROCESSING NOW"
    },
    "TED": {
        "size": "24GB",
        "status": "PARTIALLY PROCESSED",
        "action": "COMPLETE PROCESSING"
    },
    "Collectors": {
        "built": 56,
        "connected": 0,
        "action": "CONNECT ALL COLLECTORS"
    }
}

def enforce_data_reality():
    if analyzing_without_data():
        return "STOP: Process 445GB first"

    if using_frameworks_without_data():
        return "STOP: Frameworks need data foundation"

    if creating_narrative_without_evidence():
        return "STOP: Every claim needs data trace"
```

---

## J) CRYPTOGRAPHIC ALTERNATIVE (Since No SHA256)

**Verification without hashing:**
```python
def verify_source_integrity(source):
    return {
        "wayback_url": archive_url,
        "wayback_timestamp": timestamp,
        "content_length": byte_count,
        "unique_identifiers": extract_ids(source),
        "structured_extraction": {
            "title": exact_title,
            "author": exact_author,
            "date": exact_date,
            "first_paragraph": exact_text[:500],
            "last_paragraph": exact_text[-500:]
        },
        "recompute": f"curl {wayback_url} | grep -c 'unique_phrase'"
    }
```

---

## K) IMPLEMENTATION ENFORCEMENT CHECKLIST

**EVERY ANALYSIS MUST:**
- [ ] Connect to actual data (445GB) first
- [ ] Use single confidence scale (0.0-1.0)
- [ ] Run 5+ counterfactual queries
- [ ] Check echo chamber for every multi-source claim
- [ ] Assign Admiralty rating to every source
- [ ] Connect MCF sources (50 waiting)
- [ ] Pass all regression tests
- [ ] Calculate statistical baselines
- [ ] Respect phase dependencies
- [ ] Return INSUFFICIENT_EVIDENCE when no data

**BLOCKED IF:**
- Using narrative frameworks without data
- Jumping to Phase 8 without completing 1-7
- Multiple confidence scales in same analysis
- Sources without Admiralty ratings
- No counterfactual testing
- MCF sources remain disconnected

---

## L) THE FUNDAMENTAL REORDERING

**OLD (WRONG) SEQUENCE:**
1. Create compelling narrative
2. Find supporting evidence
3. Fabricate if missing

**NEW (ENFORCED) SEQUENCE:**
1. Connect to 445GB of actual data
2. Process and analyze real data
3. Build narrative from findings
4. Return INSUFFICIENT_EVIDENCE for gaps

---

## M) FINAL ENFORCEMENT GATE

```python
def final_enforcement_check(analysis):
    violations = []

    if not connected_to_real_data:
        violations.append("NOT CONNECTED TO 445GB")

    if multiple_confidence_scales:
        violations.append("MULTIPLE CONFIDENCE SCALES")

    if no_counterfactuals:
        violations.append("NO COUNTERFACTUAL TESTING")

    if mcf_disconnected:
        violations.append("MCF SOURCES NOT CONNECTED")

    if phase_dependencies_violated:
        violations.append("PHASE ORDER VIOLATED")

    if violations:
        return f"ANALYSIS REJECTED: {violations}"

    return "ANALYSIS ACCEPTED"
```

---

**ENFORCEMENT SUMMARY:**

NO MORE:
- Narratives without data
- Frameworks without foundation
- Jumping to conclusions
- Multiple confidence scales
- Unrated sources
- Skipping phases
- Ignoring counterfactuals

ONLY:
- Data-driven analysis
- Single confidence scale
- Systematic counterfactuals
- Rated sources
- Connected collectors
- Phase order respect
- INSUFFICIENT_EVIDENCE when appropriate

**THE 445GB IS WAITING. CONNECT TO IT NOW.**
