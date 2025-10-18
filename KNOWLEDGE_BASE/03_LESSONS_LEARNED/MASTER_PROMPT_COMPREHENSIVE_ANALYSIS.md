# Comprehensive Analysis of Master Prompts vs. Established Standards
**Analysis Date:** 2025-09-19
**Analyst:** Claude Code
**Scope:** ChatGPT v6.0 and Claude Code v6.0 Master Prompts

---

## EXECUTIVE SUMMARY

Both master prompts (ChatGPT v6.0 and Claude Code v6.0) contain sophisticated frameworks but have critical gaps when compared to your established standards. While they include advanced features like bombshell validation and conference intelligence, they lack proper integration with your actual data infrastructure, phase dependencies, and evidence hierarchy.

**Key Finding:** The prompts are strategically sound but operationally disconnected from your 445GB data reality and validated phase framework.

---

## 1. ALIGNMENT ANALYSIS

### ✅ AREAS OF STRONG ALIGNMENT

#### Both Prompts Correctly Implement:
1. **Leonardo Standard** (8-point specificity checklist)
   - Specific technology naming
   - Exact overlap identification
   - Physical access documentation
   - Exploitation pathway analysis
   - Timeline specification
   - Alternative testing (5+ minimum)
   - Oversight gap identification
   - Confidence scoring (0-20)

2. **Bombshell Validation Protocol**
   - 6-factor scoring system
   - Threshold at 20 points
   - Escalation procedures
   - Special handling requirements

3. **Evidence Tiering**
   - Three-tier hierarchy (Authoritative/Verified/Unverified)
   - Source type classifications
   - Corroboration requirements

4. **Failsafe Mechanisms**
   - Include critical even if incomplete
   - Gap marking requirements
   - Value weighting system

### ❌ CRITICAL GAPS AND MISALIGNMENTS

#### 1. Phase Interdependency Violations
**Your Standard (PHASE_INTERDEPENDENCY_MATRIX.md):**
```yaml
Phase_Flow:
  P0 → P1 → P2 → P2S/P3 → P4/P5 → P6 → P7C/P7R → P8
  Validation_Gates: Required between each phase
  Confidence_Thresholds: Phase-specific minimums
```

**Prompt Reality:**
- Lists phases 0-13 sequentially without dependency mapping
- No validation gate enforcement
- Missing Phase 2S (Supply Chain) integration
- No Phase X (Definitions) requirement

#### 2. Evidence Standards Mismatch
**Your Standard (MINIMUM_EVIDENCE_STANDARDS.md):**
```yaml
CRITICAL_FINDINGS:
  minimum_sources: 1*  # With caveats
  confidence_floor: 0.3
  gap_marking: MANDATORY [EVIDENCE GAP] tags
```

**Prompt Claims:**
- ChatGPT: "Triple source for critical claims" (too restrictive)
- Claude Code: "minimum_sources: 3" for validation (excessive)
- Missing your pragmatic single-source allowance for critical findings

#### 3. Data Source Disconnect
**Your Reality (445GB Available):**
- OpenAlex: 420GB academic data
- TED: 24GB procurement data
- CORDIS: EU project data
- SEC EDGAR: Corporate filings
- 56 orphaned collectors

**Prompts Mention:**
- Generic "data sources"
- No specific collector integration
- No streaming processing requirements
- Missing data volume considerations

---

## 2. DETAILED CRITIQUE BY COMPONENT

### A. NARRATIVE REQUIREMENTS

#### ChatGPT v6.0
**Strengths:**
- Detailed word counts per phase (600-1,500 words)
- Clear structure requirements
- "What It Means" sections mandated

**Weaknesses:**
- Overly prescriptive word counts may force padding
- Citation format (roman numerals) unnecessarily complex
- No integration with actual data artifacts

**Recommendation:**
```yaml
NARRATIVE_REQUIREMENTS:
  minimum_analytical_content: 400 words  # Not padding
  maximum_per_phase: 2000 words  # Unless complexity demands
  citations: Simple [1], [2], [3] with hyperlinks
  data_integration: Reference actual artifacts/YYYYMMDD_analysis.json
```

#### Claude Code v6.0
**Strengths:**
- Data pipeline focus
- Validation requirements
- Technical implementation details

**Weaknesses:**
- Lacks narrative structure guidance
- Missing word count requirements
- No "What It Means" translation

**Recommendation:**
```yaml
ADD_TO_CLAUDE:
  narrative_framework: From ChatGPT structure
  analytical_depth: 400+ words substantive analysis
  policy_translation: "What It Means" for every finding
```

### B. CONFIDENCE SCORING

#### Current Prompt Approach:
```yaml
ChatGPT:
  probability_bands: [10,30) [30,60) [60,90]
  confidence: Low/Med/High
  numeric: 0-20 for critical only

Claude:
  same probability system
  0-20 scoring more prominent
```

#### Your Standard Requirements:
```yaml
From MINIMUM_EVIDENCE_STANDARDS:
  confidence_floor: 0.3 for critical
  transparency: More important than high scores
  uncertainty_bands: Required
```

**CRITICAL ISSUE:** Both prompts emphasize high confidence over transparency

**Recommendation:**
```yaml
CONFIDENCE_FRAMEWORK:
  principle: "Low confidence with transparency > false confidence"
  critical_findings:
    minimum: 0.3 (30%)
    include_anyway: true
    mark_uncertainty: MANDATORY

  scoring_translation:
    0.0-0.3: "Low confidence - provisional finding"
    0.3-0.6: "Medium confidence - likely accurate"
    0.6-0.9: "High confidence - well evidenced"
    0.9-1.0: "Very high confidence - multiply verified"
```

### C. TECHNOLOGY SPECIFICITY

#### Good Implementation (Both Prompts):
- Leonardo standard properly included
- Specific technology requirements
- TRL assessments mentioned

#### Missing Elements:
- Connection to your actual technology data
- Integration with patent databases
- OpenAlex publication mapping
- TED procurement categories

**Recommendation:**
```yaml
TECHNOLOGY_ASSESSMENT:
  data_sources:
    patents: "F:/OSINT_DATA/EPO_PATENTS/"
    publications: "F:/OSINT_Backups/openalex/data/"
    procurement: "F:/TED_Data/monthly/"

  specificity_requirements:
    level_1: Product name/model (e.g., "AW139")
    level_2: Technical specifications
    level_3: Performance metrics
    level_4: Cost/timeline data

  verification:
    cross_reference: Patent + Publication + Procurement
    china_overlap: Exact model/variant matching
```

### D. CONFERENCE INTELLIGENCE

#### Overly Complex Classification:
Both prompts have elaborate conference tier systems that don't connect to actual data collection.

**Simplification Needed:**
```yaml
CONFERENCE_TRACKING:
  tier_1_critical:
    - China + US + Target present
    - OR: Major technology disclosure
    - OR: Arctic (for Arctic states only)

  data_collection:
    historical: Search archived proceedings
    current: Monitor registration lists
    future: Track CFPs and programs

  artifacts:
    events_master.csv: Simple flat file
    china_presence.json: Attendance tracking
    tech_disclosures.md: What was revealed
```

### E. ARCTIC FOCUS

#### Current Implementation:
- 6 primary Arctic states identified correctly
- Complex survey requirements for others
- Automatic Tier-1 for Arctic conferences

**Issue:** Arctic requirements feel "bolted on" rather than integrated

**Recommendation:**
```yaml
ARCTIC_INTEGRATION:
  IF country IN [Canada, Denmark, Finland, Iceland, Norway, Sweden]:
    THEN include_arctic_section: true
  ELSE:
    quick_check: "Any Arctic technology?"
    if_no: skip_arctic_entirely
    if_yes: brief_mention_only
```

---

## 3. STRUCTURAL ISSUES

### A. Token Management Problem

ChatGPT prompt states:
> "Token Management: NEVER cut the narrative"

**Reality Check:** This is impossible with token limits

**Better Approach:**
```yaml
TOKEN_PRIORITIZATION:
  preserve_order:
    1. Key findings and risks
    2. Evidence for critical claims
    3. Analytical narrative
    4. Supporting data

  cut_order:
    1. Redundant examples
    2. Background context
    3. Extended methodology
    4. Detailed appendices
```

### B. Phase Execution Flow

Current prompts list phases 0-13 linearly. Your PHASE_INTERDEPENDENCY_MATRIX shows complex dependencies.

**Required Fix:**
```yaml
PHASE_EXECUTION:
  parallel_capable:
    - [Phase_2, Phase_3] after Phase_1
    - [Phase_4, Phase_5] after Phase_3

  validation_gates:
    phase_2_requires: Phase_1 data sources validated
    phase_6_requires: Phases 2,2S,3,4,5 complete
    phase_8_requires: Phase 7C and 7R validation

  minimum_confidence:
    phase_0: 0.6
    phase_1: 0.7
    phase_2: 0.7
    phase_2s: 0.8
    phase_6: 0.9
```

### C. Output Artifact Disconnect

Prompts define elaborate artifact structures but don't match your actual data:

**Your Reality:**
```
data/processed/
├── country=DE/
│   ├── phase_2/
│   ├── orchestrated/
│   └── ted_analysis/
├── openalex_systematic/
└── orchestrated_results/
```

**Prompt Fantasy:**
```
artifacts/{COUNTRY}/_national/
├── phase00_setup.json through phase13_closeout.json
├── validation_report.json
├── conferences/events_master.csv
└── arctic/arctic_conferences.json
```

---

## 4. CRITICAL RECOMMENDATIONS

### IMMEDIATE FIXES (Do Now)

#### 1. Add Data Reality Block
```yaml
DATA_INFRASTRUCTURE:
  available_now:
    openalex: "420GB at F:/OSINT_Backups/openalex/"
    ted: "24GB at F:/TED_Data/monthly/"
    cordis: "F:/2025-09-14 Horizons/"

  processing_requirement:
    streaming: true  # Can't load 420GB in memory
    batch_size: 1000 records
    checkpoint: Every 10000 records

  collectors_available:
    count: 56
    connected: 8
    priority: "Connect remaining 48 urgently"
```

#### 2. Fix Evidence Requirements
```yaml
EVIDENCE_STANDARDS_CORRECTED:
  critical_findings:
    sources: 1+ (even single if critical enough)
    confidence: 0.3+ (low is OK if transparent)
    inclusion: ALWAYS (mark gaps clearly)

  validation:
    leonardo_8_points: true
    alternatives: 5+ for extraordinary
    bombshell: Score if >20

  gap_marking:
    format: "[EVIDENCE GAP: missing component]"
    required: ALL provisional findings
```

#### 3. Simplify Probability Bands
```yaml
PROBABILITY_SIMPLIFIED:
  narrative_use:
    low: "unlikely" (10-30%)
    medium: "possible" (30-60%)
    high: "probable" (60-90%)

  artifacts_only:
    numeric_0_1: For data files
    numeric_0_20: For bombshell scoring

  never_use:
    exact_percentages: In narrative
    false_precision: "73.2% likely"
```

### STRATEGIC IMPROVEMENTS (This Week)

#### 1. Create Integration Layer
```yaml
PROMPT_TO_DATA_BRIDGE:
  phase_2_technology:
    prompt_requirement: "Technology landscape"
    data_source: "OpenAlex + EPO Patents"
    processor: "systematic_data_processor.py"
    output: "data/processed/country={CC}/phase_2/"

  phase_2s_supply:
    prompt_requirement: "Supply chain"
    data_source: "TED procurement"
    processor: "process_ted_data.py"
    output: "data/processed/ted_analysis/"
```

#### 2. Add Validation Gate Implementation
```python
def validate_phase_transition(from_phase, to_phase):
    """Actually enforce the requirements"""

    gates = {
        "phase_1_to_2": {
            "required": ["data_sources_validated"],
            "confidence": 0.7
        },
        "phase_2_to_2s": {
            "required": ["technology_landscape_complete"],
            "confidence": 0.7
        }
    }

    if not check_requirements(gates[f"{from_phase}_to_{to_phase}"]):
        return "BLOCKED: Requirements not met"
```

#### 3. Reality-Check All Requirements
```yaml
FEASIBILITY_FILTER:
  before: "Triple source everything"
  after: "Single source OK if critical + marked"

  before: "600+ words mandatory"
  after: "400+ substantive words"

  before: "Conference Tier-1/2/3 complex classification"
  after: "China present? → Important. Not? → Skip"

  before: "Arctic assessment for all"
  after: "Arctic states only + quick check others"
```

### LONG-TERM STRUCTURAL CHANGES (This Month)

#### 1. Merge Best of Both Prompts
```yaml
UNIFIED_MASTER_PROMPT:
  from_chatgpt:
    - Narrative structure
    - Citation standards
    - "What It Means" sections

  from_claude:
    - Data pipeline focus
    - Validation implementation
    - Technical precision

  from_your_standards:
    - Evidence hierarchy
    - Phase dependencies
    - Confidence floors
    - Data infrastructure reality
```

#### 2. Create Prompt Validation Suite
```python
def validate_prompt_compliance(prompt, output):
    """Check if output meets prompt requirements"""

    checks = {
        "narrative_length": len(output.narrative) >= 400,
        "evidence_cited": all(claim.has_citation for claim in output.claims),
        "confidence_marked": output.confidence is not None,
        "gaps_marked": "[EVIDENCE GAP]" in output if output.provisional,
        "leonardo_standard": validate_leonardo_8_points(output),
        "data_connected": output.references_actual_data()
    }

    return check_results
```

#### 3. Build Feedback Loop
```yaml
CONTINUOUS_IMPROVEMENT:
  track:
    - Which requirements get ignored
    - Which add no value
    - Which catch real issues

  measure:
    - Time per phase
    - Evidence quality
    - Finding accuracy

  adjust:
    - Remove unused complexity
    - Add missing connections
    - Simplify where possible
```

---

## 5. SPECIFIC LINE-BY-LINE CORRECTIONS

### ChatGPT v6.0 Master Prompt

**Line 39:** Change "NEVER_numeric_in_narrative: true" to "avoid_false_precision: true"

**Line 96-122:** Reduce TARGET_COUNTRIES from 67 to your actual priority list

**Line 143:** Change "3-7 bullets maximum" to "3-5 focused bullets"

**Line 271:** Fix "Triple source for critical claims" to "Single source OK if critical + transparent"

**Lines 456-462:** Remove forbidden phrases section (too restrictive)

**Line 469:** Fix "NEVER cut narrative" to realistic token management

### Claude Code v6.0 Master Prompt

**Line 110:** Add "data_source_path: str" to technology assessment

**Line 146:** Change "minimum_sources: 1" for critical (not 3)

**Line 232:** Remove complex Arctic assessment for non-Arctic states

**Line 460:** Add specific data paths not generic "artifacts/{COUNTRY}"

**Line 585:** Add "But pragmatism over perfection"

---

## 6. VALIDATION CHECKLIST

### Before Prompt Deployment:
- [ ] Evidence requirements match MINIMUM_EVIDENCE_STANDARDS.md
- [ ] Phase dependencies match PHASE_INTERDEPENDENCY_MATRIX.md
- [ ] Data sources point to actual 445GB infrastructure
- [ ] Collectors map to 56 identified tools
- [ ] Confidence floors allow critical findings at 0.3
- [ ] Gap marking uses [EVIDENCE GAP] format
- [ ] Validation gates enforce phase transitions
- [ ] Token management is realistic
- [ ] Arctic requirements are proportionate
- [ ] Conference tracking connects to real data

### After Each Analysis:
- [ ] Critical findings included even if low confidence?
- [ ] Gaps marked transparently?
- [ ] Actual data files referenced?
- [ ] Phase dependencies respected?
- [ ] Leonardo standard applied?
- [ ] Bombshell protocol used if score >20?
- [ ] Evidence tier documented?
- [ ] Confidence appropriate to evidence?

---

## 7. FINAL RECOMMENDATIONS SUMMARY

### TOP PRIORITY CHANGES

1. **Fix Evidence Requirements**
   - Allow single source for critical findings
   - Set confidence floor at 0.3
   - Require transparent gap marking

2. **Connect to Data Reality**
   - Reference actual 445GB data locations
   - Map to 56 orphaned collectors
   - Include streaming processing needs

3. **Simplify Complexity**
   - Reduce conference tiers to simple China/No-China
   - Limit Arctic to actual Arctic states
   - Remove excessive word count requirements

4. **Enforce Dependencies**
   - Add validation gates between phases
   - Require Phase X definitions
   - Include Phase 2S supply chain

5. **Prioritize Transparency**
   - Low confidence + transparent > high false confidence
   - Mark every assumption
   - Document what you don't know

### IMPLEMENTATION SEQUENCE

**Week 1:**
- Update evidence requirements
- Add data infrastructure block
- Fix confidence scoring

**Week 2:**
- Implement validation gates
- Connect to actual collectors
- Simplify conference tracking

**Week 3:**
- Merge best of both prompts
- Create validation suite
- Test with real data

**Week 4:**
- Deploy unified prompt
- Monitor compliance
- Iterate based on results

---

## BOTTOM LINE

Your master prompts are sophisticated but disconnected from operational reality. They need to:

1. **Embrace your pragmatic evidence standards** (not perfectionist requirements)
2. **Connect to your actual data** (not hypothetical sources)
3. **Simplify where possible** (Arctic, conferences, citations)
4. **Enforce what matters** (phase gates, Leonardo standard, transparency)
5. **Accept low confidence** (when marked transparently)

The prompts try to prevent analytical failures through strictness, but your standards correctly recognize that transparency about limitations is better than false confidence. Update the prompts to match your standards, not the reverse.

**Remember:** The goal is actionable intelligence from imperfect data, not perfect intelligence never delivered.

---

*End of Analysis*
