# Claude Code Master Prompt v9.3 — ENFORCEMENT EDITION
## Data-First Reality with Mandatory Connection to 447GB

**PRIME DIRECTIVE:** Process actual data (447GB available) before any analysis. No narratives without data. No frameworks without evidence.

**ENFORCEMENT MODE:** Every claim must trace to machine-readable data with recompute command, or return INSUFFICIENT_EVIDENCE.

---

## 🚨 MANDATORY DATA CONNECTION CHECK

**BEFORE ANY ANALYSIS:**
```python
def pre_flight_data_check():
    # Updated from UNIFIED_DATA_INFRASTRUCTURE_INVENTORY.md
    available_data = {
        "OpenAlex": "422GB at F:/OSINT_Backups/openalex/data/ - 0.5% processed",
        "TED": "25GB at F:/TED_Data/ - 0% processed - HIGHEST PRIORITY",
        "CORDIS": "1.1GB multiple locations - H2020 100% done, HE 0%",
        "SEC_EDGAR": "127MB at F:/OSINT_Data/SEC_EDGAR/ - 0% processed",
        "EPO_Patents": "120MB at F:/OSINT_DATA/EPO_PATENTS/ - 0% processed",
        "USPTO": "PatentsView API + BigQuery available",
        "USAspending": "Contract data available"
    }

    # Hardware requirements from inventory
    hardware_requirements = {
        "RAM": "32GB minimum for OpenAlex streaming",
        "Disk": "500GB free for decompression",
        "Processing": "Multi-core for parallel processing"
    }

    processing_status = {
        "OpenAlex": "1,225,874 papers analyzed, 68 Germany-China found",
        "TED": "0 files processed - START IMMEDIATELY",
        "CORDIS": "168 Italy-China projects found from H2020",
        "Checkpoint": "OpenAlex at 1.2M records in checkpoint.json"
    }

    collectors_available = 56  # Built but disconnected

    if not connected_to_actual_data():
        return "STOP: Connect to data first. 447GB waiting."

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

**The 447GB Reality Check (Updated from UNIFIED_DATA_INFRASTRUCTURE_INVENTORY.md):**
```python
DATA_REALITY = {
    "OpenAlex": {
        "size": "422GB",
        "location": "F:/OSINT_Backups/openalex/data/",
        "status": "0.5% PROCESSED (1.2M of 250M records)",
        "findings": "68 Germany-China collaborations",
        "checkpoint": "data/processed/openalex_real_data/checkpoint.json",
        "action": "RESUME FROM CHECKPOINT"
    },
    "TED": {
        "size": "25GB",
        "location": "F:/TED_Data/",
        "status": "0% PROCESSED",
        "priority": "HIGHEST - Government contracts",
        "action": "START PROCESSING IMMEDIATELY"
    },
    "CORDIS": {
        "size": "1.1GB",
        "location": "Multiple (see inventory)",
        "status": "H2020 100% done, Horizon Europe 0%",
        "findings": "168 Italy-China projects",
        "action": "PROCESS HORIZON EUROPE"
    },
    "SEC_EDGAR": {
        "size": "127MB",
        "location": "F:/OSINT_Data/SEC_EDGAR/",
        "status": "NOT PROCESSED",
        "action": "EXTRACT LEONARDO/DEFENSE DATA"
    },
    "EPO_Patents": {
        "size": "120MB",
        "location": "F:/OSINT_DATA/EPO_PATENTS/",
        "status": "NOT PROCESSED (Leonardo only)",
        "action": "PARSE PATENT APPLICATIONS"
    },
    "Collectors": {
        "built": 56,
        "connected": 8,
        "orphaned": 48,
        "action": "RECONNECT ALL COLLECTORS"
    }
}

def enforce_data_reality():
    if analyzing_without_data():
        return "STOP: Process 447GB first"

    if using_frameworks_without_data():
        return "STOP: Frameworks need data foundation"

    if creating_narrative_without_evidence():
        return "STOP: Every claim needs data trace"
```

---

## J) STREAMING ARCHITECTURE (REQUIRED FOR 422GB)

**From UNIFIED_DATA_INFRASTRUCTURE_INVENTORY.md:**
```python
# CORRECT - Stream processing (MANDATORY for OpenAlex)
def process_openalex_correctly():
    """Required approach for 422GB dataset"""
    import gzip, json

    with gzip.open(file, 'rt') as f:
        for line in f:  # One line at a time - NO LOADING ENTIRE FILE
            paper = json.loads(line)
            if meets_criteria(paper):
                process(paper)

    # Save checkpoint every 10 files
    if file_idx % 10 == 0:
        save_checkpoint()  # Can resume from here

# WRONG - Memory overflow (WILL CRASH)
def process_openalex_wrong():
    """This will fail with 422GB"""
    data = json.load(open(file))  # NEVER DO THIS - Loads entire file
    # System will run out of memory
```

**Hardware Requirements (from inventory):**
- RAM: 32GB minimum for OpenAlex
- Disk: 500GB free for decompression
- Processing: Multi-core for parallel processing

---

## K) CRYPTOGRAPHIC ALTERNATIVE (Since No SHA256)

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

## L) PROCESSING PRIORITY ORDER (FROM INVENTORY)

**IMMEDIATE ACTIONS IN ORDER:**
```python
PROCESSING_PRIORITY = {
    1: {
        "source": "TED",
        "priority": "HIGHEST",
        "reason": "Government contracts most relevant",
        "action": "Create parse_ted_contracts.py and run",
        "commands": [
            "cd F:/TED_Data",
            "tar -xzf TED_monthly_2024_01.tar.gz",
            "grep -r 'Italy' . | grep 'China'",
            "python parse_ted_contracts.py"
        ]
    },
    2: {
        "source": "OpenAlex",
        "priority": "MEDIUM",
        "reason": "Academic collaboration patterns",
        "action": "Resume from checkpoint at 1.2M records",
        "commands": [
            "cd C:/Projects/OSINT - Foresight",
            "python scripts/process_openalex_large_files.py --resume"
        ]
    },
    3: {
        "source": "Horizon Europe CORDIS",
        "priority": "QUICK WIN",
        "reason": "1-2 hours to complete",
        "action": "Process remaining CORDIS data",
        "commands": [
            "python scripts/process_horizon_europe.py"
        ]
    }
}
```

---

## M) IMPLEMENTATION ENFORCEMENT CHECKLIST

**EVERY ANALYSIS MUST:**
- [ ] Connect to actual data (447GB) first - check all paths
- [ ] Use single confidence scale (0.0-1.0)
- [ ] Run 5+ counterfactual queries
- [ ] Check echo chamber for every multi-source claim
- [ ] Assign Admiralty rating to every source
- [ ] Connect MCF sources (50 waiting)
- [ ] Pass all regression tests
- [ ] Calculate statistical baselines
- [ ] Respect phase dependencies
- [ ] Use streaming for OpenAlex (422GB)
- [ ] Check hardware meets 32GB RAM minimum
- [ ] Return INSUFFICIENT_EVIDENCE when no data

**BLOCKED IF:**
- Using narrative frameworks without data
- Jumping to Phase 8 without completing 1-7
- Multiple confidence scales in same analysis
- Sources without Admiralty ratings
- No counterfactual testing
- MCF sources remain disconnected
- Not using streaming for large files
- Ignoring TED as HIGHEST PRIORITY

---

## N) THE FUNDAMENTAL REORDERING

**OLD (WRONG) SEQUENCE:**
1. Create compelling narrative
2. Find supporting evidence
3. Fabricate if missing

**NEW (ENFORCED) SEQUENCE:**
1. Connect to 447GB of actual data (corrected from 445GB)
2. Process and analyze real data with streaming
3. Build narrative from findings
4. Return INSUFFICIENT_EVIDENCE for gaps

---

## O) FINAL ENFORCEMENT GATE

```python
def final_enforcement_check(analysis):
    violations = []

    if not connected_to_real_data:
        violations.append("NOT CONNECTED TO 447GB")

    if not using_correct_paths:
        violations.append("WRONG DATA PATHS - CHECK INVENTORY")

    if multiple_confidence_scales:
        violations.append("MULTIPLE CONFIDENCE SCALES")

    if no_counterfactuals:
        violations.append("NO COUNTERFACTUAL TESTING")

    if mcf_disconnected:
        violations.append("MCF SOURCES NOT CONNECTED")

    if phase_dependencies_violated:
        violations.append("PHASE ORDER VIOLATED")

    if not using_streaming_for_openalex:
        violations.append("NOT USING STREAMING - WILL CRASH")

    if ted_not_prioritized:
        violations.append("TED NOT PROCESSED - HIGHEST PRIORITY")

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
- Wrong data sizes (445GB → 447GB)
- Loading entire files into memory

ONLY:
- Data-driven analysis from 447GB
- Single confidence scale (0.0-1.0)
- Systematic counterfactuals
- Rated sources (Admiralty)
- Connected collectors
- Phase order respect
- Streaming architecture for large files
- TED as HIGHEST PRIORITY
- INSUFFICIENT_EVIDENCE when appropriate

**THE 447GB IS WAITING. CONNECT TO IT NOW.**

**PROCESSING ORDER:**
1. TED (25GB) - IMMEDIATE
2. OpenAlex (resume from 1.2M checkpoint)
3. Horizon Europe CORDIS (quick win)
