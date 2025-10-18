# IMPLEMENTATION ENFORCEMENT CHECKLIST
## Mandatory Actions to Prevent Future Fabrication

**Date:** 2025-09-20
**Status:** 🔴 CRITICAL - MUST IMPLEMENT BEFORE ANY ANALYSIS

---

## 🚨 THE REALITY CHECK

**Current State:**
- 445GB of data UNPROCESSED (420GB OpenAlex + 24GB TED)
- 56 data collectors BUILT but DISCONNECTED
- 50 MCF sources IDENTIFIED but NOT CONNECTED
- Regression tests WRITTEN but NOT RUNNING
- Fabricated "78 transfers" while real data sat unused

**This checklist ensures we NEVER fabricate again.**

---

## 1️⃣ IMMEDIATE ACTIONS (Do First)

### Connect to Actual Data
```bash
# OpenAlex - 420GB of academic data
python scripts/connect_openalex.py --process-bulk

# TED - 24GB of procurement data
python scripts/connect_ted.py --complete-processing

# Connect all 56 collectors
for collector in src/collectors/*.py; do
    python $collector --connect --verify
done
```

**Success Criteria:** Can query all datasets programmatically

### Implement Single Confidence Scale
```python
# ONLY USE THIS SCALE
CONFIDENCE = {
    0.9-1.0: "Very High",
    0.7-0.9: "High",
    0.5-0.7: "Moderate",
    0.3-0.5: "Low",
    0.0-0.3: "INSUFFICIENT_EVIDENCE"
}

# DELETE/REMOVE:
# - Low/Medium/High text labels without numbers
# - 0-20 scoring systems
# - Any other confidence scales
```

---

## 2️⃣ ENFORCEMENT GATES (Implement in Code)

### Phase Dependency Enforcement
```python
# Add to every phase executor
def check_dependencies(phase_requested):
    if phase_requested == "Phase_8_Risk":
        required = ["Phase_1", "Phase_2", "Phase_3", "Phase_4", "Phase_5", "Phase_6", "Phase_7"]
        if not all_completed(required):
            raise Exception("BLOCKED: Complete all phases 1-7 first")
```

### Mandatory Counterfactual Testing
```python
# Add to every positive finding
def test_counterfactual(claim):
    searches = [
        f"NO {claim}",
        f"NOT {claim}",
        f"{claim} false",
        f"{claim} debunked",
        f"{claim} disputed"
    ]

    for search in searches:
        results = search_actual_data(search)
        if contradicting_evidence:
            adjust_confidence_down()
```

### Echo Chamber Detection
```python
# Add to source verification
def check_echo_chamber(sources):
    # Trace all sources to origin
    origins = [trace_to_primary(s) for s in sources]

    if len(set(origins)) == 1:
        raise Exception("ECHO CHAMBER: All sources from single origin")

    if all_wire_services(origins):
        raise Exception("WIRE COPY: Not independent")
```

---

## 3️⃣ MCF SOURCE CONNECTION (Critical)

### Connect These Sources IMMEDIATELY
```python
MCF_PRIORITY_SOURCES = [
    "https://digitalcommons.ndu.edu/cscma-allpubs/",  # NDU CSCMA
    "https://www.airuniversity.af.edu/CASI/",          # CASI
    "https://www.state.gov/military-civil-fusion/",    # State Dept
    "https://www.aspi.org.au/report/critical-technology-tracker",  # ASPI
    "https://www.uscc.gov/"  # USCC
]

# Create connectors for each
for source in MCF_PRIORITY_SOURCES:
    create_connector(source)
    test_connection(source)
    schedule_daily_check(source)
```

---

## 4️⃣ REGRESSION TEST AUTOMATION

### Tests That Would Have Caught "78 Transfers"
```python
# Run these AUTOMATICALLY on every analysis
def regression_suite():
    tests = [
        test_no_unsourced_numbers(),      # CRITICAL
        test_admiralty_ratings_present(),  # REQUIRED
        test_counterfactuals_executed(),   # MANDATORY
        test_echo_chamber_checked(),       # ESSENTIAL
        test_single_confidence_scale(),    # ENFORCED
        test_phase_dependencies_met(),     # BLOCKED IF NOT
        test_data_actually_searched(),     # FUNDAMENTAL
        test_insufficient_evidence_used()  # DEFAULT
    ]

    if any_test_fails(tests):
        REJECT_ANALYSIS()
```

### Set Up Automated Running
```bash
# Add to pre-commit hooks
echo "python scripts/run_regression_tests.py" >> .git/hooks/pre-commit

# Add to CI/CD pipeline
# Add to GitHub Actions or equivalent
```

---

## 5️⃣ ADMIRALTY RATING ENFORCEMENT

### Make Ratings Mandatory
```python
def rate_source(source):
    reliability = None  # A-F
    credibility = None  # 1-6

    # FORCE rating before proceeding
    while not reliability:
        reliability = assign_reliability(source)

    while not credibility:
        credibility = assign_credibility(source)

    # Auto-adjust confidence for poor sources
    if reliability >= 'D' or credibility >= 4:
        max_confidence = 0.5  # Cap at moderate

    return f"[{reliability}{credibility}]"
```

---

## 6️⃣ STATISTICAL BASELINES

### Calculate Normal Patterns
```python
# BEFORE claiming anomaly, know what's normal
BASELINES = {
    "personnel_transfers": {
        "calculate": "SELECT AVG(transfers) FROM companies WHERE similar_size",
        "source": "SEC filings only (LinkedIn violates ToS)"
    },
    "patent_collaboration": {
        "calculate": "SELECT AVG(joint_patents) FROM USPTO WHERE country_pair",
        "source": "USPTO bulk data"
    },
    "paper_collaboration": {
        "calculate": "SELECT AVG(coauthorship) FROM OpenAlex WHERE countries",
        "source": "OpenAlex 420GB dataset"
    }
}

# Can't call something unusual without knowing usual
```

---

## 7️⃣ DATA-FIRST WORKFLOW

### The New Mandatory Sequence
```python
def analyze(topic):
    # 1. CONNECT TO DATA FIRST
    data_sources = connect_to_445gb()

    # 2. SEARCH ACTUAL DATA
    results = search_real_data(topic)

    # 3. RUN COUNTERFACTUALS
    counter = search_counterfactuals(topic)

    # 4. CHECK BASELINES
    baseline = get_statistical_normal(topic)

    # 5. BUILD FROM EVIDENCE
    if insufficient_data:
        return "INSUFFICIENT_EVIDENCE"
    else:
        return evidence_based_narrative(results)

    # NEVER: Create narrative first, find evidence second
```

---

## 8️⃣ ENFORCEMENT MONITORING

### Daily Checks
- [ ] All 56 collectors connected?
- [ ] MCF sources being harvested?
- [ ] Regression tests passing?
- [ ] Single confidence scale used?
- [ ] Phase dependencies respected?

### Weekly Audits
- [ ] Random sample 10 analyses for compliance
- [ ] Check for narrative-before-data patterns
- [ ] Verify counterfactuals being run
- [ ] Ensure Admiralty ratings present
- [ ] Confirm INSUFFICIENT_EVIDENCE being used

### Red Flags Requiring Immediate Stop
- 🔴 Specific number without source
- 🔴 Jumping to Phase 8 without 1-7
- 🔴 Multiple confidence scales
- 🔴 No counterfactual queries
- 🔴 Unrated sources
- 🔴 MCF sources disconnected

---

## 9️⃣ VERIFICATION WITHOUT SHA256

Since we can't generate SHA256, use these alternatives:
```python
def verify_source(source):
    return {
        "wayback_url": get_wayback_url(source),
        "content_length": len(source.content),
        "unique_phrases": extract_unique_phrases(source),
        "structured_data": {
            "title": source.title,
            "author": source.author,
            "date": source.date,
            "first_500_chars": source.content[:500],
            "last_500_chars": source.content[-500:]
        }
    }
```

---

## 🎯 SUCCESS METRICS

**Analysis is ACCEPTABLE only when:**
- ✅ Connected to actual data (445GB)
- ✅ Single confidence scale (0.0-1.0)
- ✅ 5+ counterfactuals per major claim
- ✅ Echo chamber check performed
- ✅ All sources Admiralty rated
- ✅ MCF sources connected
- ✅ Regression tests pass
- ✅ Statistical baselines calculated
- ✅ Phase dependencies respected
- ✅ INSUFFICIENT_EVIDENCE used for gaps

**Analysis is REJECTED if ANY of above missing.**

---

## 🔴 THE FUNDAMENTAL RULE

**Before:** Sophisticated frameworks → Compelling narratives → Fabricated evidence

**After:** Real data → Verified evidence → Honest narratives → INSUFFICIENT_EVIDENCE for gaps

**THE 445GB IS WAITING. NO MORE EXCUSES. NO MORE FABRICATION.**

---

*This checklist is mandatory. No analysis proceeds without compliance.*
