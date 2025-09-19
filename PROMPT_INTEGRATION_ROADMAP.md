# Prompt Integration Roadmap: Best Practices & MCF Datasets

**Date:** September 18, 2025
**Analysis:** Mapping best practices and MCF datasets to master prompts

---

## Executive Summary

Both master prompts have solid validation frameworks but need specific enhancements for:
1. **Systematic bias prevention** (counterfactual queries, confirmation bias controls)
2. **Standardized uncertainty quantification** (inconsistent confidence scales)
3. **MCF dataset integration** (missing ~70% of available sources)
4. **Evidence tier filtering** (quality controls exist but not systematically enforced)

---

## 🔴 CRITICAL FIXES NEEDED IN PROMPTS

### 1. CONFIDENCE SCALE INCONSISTENCY

**Current Problem:**
- Claude Code prompt: Mixed 0-20 and 0-1 scales
- ChatGPT prompt: 0-20 for artifacts, probability bands for narrative
- Implementation: Various scripts use different scales

**WHERE TO FIX:**

#### Claude Code Master V6 - Line 27-34
```yaml
# CURRENT (INCONSISTENT):
SCORING:
  NARRATIVE:
    use_probability_bands: true  # [10,30) [30,60) [60,90]
  ARTIFACTS:
    numeric_confidence_0_20: major_critical_only

# PROPOSED FIX:
SCORING:
  UNIFIED_SCALE:
    confidence: "0.0-1.0 with uncertainty bands"  # Standardized
    conversion: {0.0-0.35: "Low", 0.35-0.70: "Med", 0.70-1.0: "High"}
    uncertainty_required: true  # ±0.1 minimum
  NARRATIVE:
    use_probability_bands: true  # Keep for readability
    map_to_unified: true  # Convert internally
  ARTIFACTS:
    use_unified_scale: true  # 0.0-1.0 everywhere
    include_uncertainty: true  # e.g., 0.75 ± 0.10
```

#### ChatGPT Master V6 - Line 24-28
```yaml
# Apply same fix as Claude Code for consistency
```

---

### 2. MISSING COUNTERFACTUAL QUERIES

**Current Gap:** No systematic search for disconfirming evidence

**WHERE TO ADD:**

#### Claude Code Master V6 - After Line 196 (Step 4)
```python
#### Step 5: Counterfactual Query Protocol (NEW)
def run_counterfactual_queries(finding):
    """
    MANDATORY - Search for disconfirming evidence
    """
    queries = {
        "opposite_search": "Find evidence that contradicts claim",
        "alternative_explanation": "Search for benign explanations",
        "missing_evidence": "What would disprove this?",
        "statistical_baseline": "Is this normal activity?",
        "temporal_inconsistency": "Does timeline make sense?"
    }

    disconfirming_evidence = []
    for query_type, query in queries.items():
        result = search_contradictory(finding, query)
        disconfirming_evidence.append(result)

    return {
        "confirmatory_count": finding.supporting_evidence,
        "contradictory_count": len(disconfirming_evidence),
        "balance_ratio": calculate_balance(),
        "adjusted_confidence": downgrade_if_unbalanced()
    }
```

#### ChatGPT Master V6 - After Line 204
```python
# Add identical counterfactual query protocol
```

---

### 3. EVIDENCE TIER ENFORCEMENT

**Current Gap:** Quality tiers mentioned but not enforced

**WHERE TO ADD:**

#### Claude Code Master V6 - Line 145-170 (Evidence Verification)
```python
def verify_evidence_with_failsafe(claim, strategic_value):
    """
    ENHANCED with tier filtering
    """
    # ADD THIS:
    evidence_tiers = {
        "TIER_1": ["Official registries", "Government data", "Bulk structured"],
        "TIER_2": ["Peer-reviewed", "Validated sources", "Major databases"],
        "TIER_3": ["News", "Social media", "Unverified reports"]
    }

    # Filter by tier BEFORE validation
    if strategic_value != "CRITICAL":
        evidence = filter_tier_3(evidence)  # Exclude unless corroborated

    # Rest of existing validation...
```

---

## 📊 MCF DATASET INTEGRATION POINTS

### Priority 1: Research Identity Sources (Week 1-2)

**ADD TO PROMPTS:**

#### Claude Code Master V6 - Line 516 (Data Source Integrations section)
```yaml
### Research Identity & Normalization (NEW)
**Priority MCF Sources:**
- ROR (Research Organization Registry): https://ror.org/data
  - Monthly dumps for institutional normalization
  - Required for consistent org_ror joins
- ORCID Public Data: https://orcid.org/public-data-file
  - Annual dump for researcher tracking
  - Maps to talent flow analysis
- OpenAIRE Research Graph: https://graph.openaire.eu/data
  - Bulk dumps for EU research linkages
  - Critical for collaboration mapping
```

#### ChatGPT Master V6 - Add after Line 394 (Conference Intelligence)
```yaml
### MCF Identity Sources (REQUIRED)
research_identity:
  ror_registry: "Monthly institutional dumps"
  orcid_data: "Annual researcher mobility"
  openaire_graph: "EU research networks"
```

### Priority 2: Standards Bodies APIs (Week 1-2)

**ADD TO PROMPTS:**

#### Claude Code Master V6 - Line 234 (Phase 2 Indicators)
```python
def phase2_standards_tracking():
    """
    NEW: Standards influence monitoring
    """
    sources = {
        "IETF": "https://datatracker.ietf.org/api/v1",
        "W3C": "GitHub activity tracking",
        "3GPP": "Technical contribution portal",
        "ETSI_IPR": "Standard-essential patents DB"
    }

    metrics = {
        "contribution_volume": "Submissions per quarter",
        "leadership_roles": "Chair/editor positions",
        "sep_declarations": "Patents declared essential",
        "china_participation": "PRC org involvement"
    }

    return calculate_standards_influence_index()
```

### Priority 3: Supply Chain Dependencies (Month 1)

**ADD TO PROMPTS:**

#### Claude Code Master V6 - After conference artifacts (Line 321)
```yaml
code_dependency_artifacts:
  "github_archive.json": {
    "source": "BigQuery: githubarchive",
    "schema": ["repo", "contributors", "dependencies", "china_links"]
  },
  "libraries_io.json": {
    "source": "Libraries.io dumps",
    "schema": ["package", "ecosystem", "maintainers", "dependents"]
  },
  "pypi_stats.csv": {
    "source": "PyPI download statistics",
    "focus": ["AI/ML packages", "crypto modules", "dual-use libs"]
  }
```

### Priority 4: Enhanced Company Intelligence (Month 1)

**ADD TO PROMPTS:**

#### ChatGPT Master V6 - Line 400 (Procurement & Ownership)
```yaml
### Enhanced Ownership Tracking (NEW)
company_intelligence:
  uk_companies_house:
    api: "https://api.company-information.service.gov.uk"
    data: ["Officers", "Beneficial ownership", "Filings"]
  opensanctions:
    bulk: "https://opensanctions.org/data"
    includes: ["Sanctions", "PEPs", "Watchlists"]
  enhanced_gleif:
    parent_chains: true
    ultimate_ownership: true
```

---

## 🚀 IMPLEMENTATION PRIORITY MATRIX

### IMMEDIATE (Week 1-2)

1. **Fix Confidence Scales**
   - Location: Both prompts, SCORING section
   - Action: Standardize to 0.0-1.0 with uncertainty bands
   - Impact: Resolves major inconsistency

2. **Add Counterfactual Queries**
   - Location: Validation requirements section
   - Action: Add Step 5 to validation protocol
   - Impact: Addresses confirmation bias

3. **Integrate ROR & Standards APIs**
   - Location: Data sources section
   - Action: Add MCF identity sources
   - Impact: Enables proper normalization

### HIGH PRIORITY (Month 1)

1. **Evidence Tier Filtering**
   - Location: Evidence verification functions
   - Action: Add tier-based filtering logic
   - Impact: Improves signal-to-noise ratio

2. **OpenAIRE & ORCID Integration**
   - Location: Phase 3 (Technology Landscape)
   - Action: Add bulk data processing requirements
   - Impact: Enhanced collaboration tracking

3. **UK Companies House & OpenSanctions**
   - Location: Phase 5-6 (Institutions/Funding)
   - Action: Add API endpoints and schemas
   - Impact: Better ownership intelligence

### MEDIUM PRIORITY (Month 2-3)

1. **GitHub Archive & Libraries.io**
   - Location: Phase 4 (Supply Chain)
   - Action: Add dependency tracking requirements
   - Impact: Code vulnerability assessment

2. **Enhanced Uncertainty Propagation**
   - Location: Throughout validation sections
   - Action: Add uncertainty cascade logic
   - Impact: More honest confidence reporting

---

## 📝 SPECIFIC PROMPT UPDATES NEEDED

### Claude Code Master V6 Updates

**Line 27-34:** Fix confidence scale (see above)
**Line 196:** Add counterfactual query step
**Line 145:** Add evidence tier filtering
**Line 516:** Add MCF data sources section
**Line 234:** Add standards tracking requirements
**Line 321:** Add code dependency artifacts

### ChatGPT Master V6 Updates

**Line 24-28:** Fix confidence scale
**Line 204:** Add counterfactual queries
**Line 394:** Add MCF identity sources
**Line 400:** Add enhanced ownership tracking
**Line 296:** Add standards participation tracking
**Line 353:** Add infrastructure dependency mapping

---

## 🔧 IMPLEMENTATION SCRIPTS NEEDED

### 1. Confidence Scale Standardization Script
```python
# standardize_confidence.py
def convert_all_confidence_scales():
    """
    Convert all existing 0-20 scores to 0-1 scale
    """
    # Scan all artifacts/
    # Convert numeric_confidence fields
    # Add uncertainty_band fields
    # Update validation logic
```

### 2. Counterfactual Query Implementation
```python
# counterfactual_search.py
def implement_red_team_queries():
    """
    Add systematic disconfirming evidence search
    """
    # For each finding in pipeline
    # Generate opposite queries
    # Search for contradictions
    # Calculate balance ratio
    # Adjust confidence
```

### 3. MCF Dataset Integration Pipeline
```python
# mcf_integration.py
def integrate_priority_sources():
    """
    Week 1-2: ROR, IETF, ETSI
    Month 1: OpenAIRE, Companies House
    Month 2: GitHub Archive, Libraries.io
    """
    # Download bulk data
    # Process to standard schema
    # Create join keys
    # Update analysis pipelines
```

---

## ✅ SUCCESS METRICS

### Week 2 Checkpoint
- [ ] Confidence scales standardized across all code
- [ ] Counterfactual queries operational
- [ ] ROR integration complete
- [ ] Standards APIs connected

### Month 1 Checkpoint
- [ ] Evidence tier filtering active
- [ ] OpenAIRE bulk processing working
- [ ] Companies House API integrated
- [ ] OpenSanctions data flowing

### Month 2 Checkpoint
- [ ] GitHub dependency analysis operational
- [ ] Libraries.io integration complete
- [ ] Uncertainty propagation implemented
- [ ] All MCF priority sources integrated

---

## 📋 NEXT STEPS

1. **Today:** Update both master prompts with confidence scale fix
2. **Tomorrow:** Implement counterfactual query framework
3. **This Week:** Begin ROR and standards API integration
4. **Next Week:** Deploy evidence tier filtering
5. **Month 1:** Complete high-priority MCF integrations

---

**Document Status:** Implementation Roadmap
**Owner:** OSINT Foresight Team
**Review Date:** September 25, 2025
