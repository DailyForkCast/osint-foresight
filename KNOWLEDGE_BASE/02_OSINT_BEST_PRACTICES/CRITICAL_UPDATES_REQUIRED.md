# CRITICAL UPDATES REQUIRED FOR MASTER PROMPTS
**Based on CIA/DIA/OSINT Best Practices**
**Date:** 2025-09-19
**Priority:** IMMEDIATE

---

## 🚨 MUST ADD TO BOTH PROMPTS IMMEDIATELY

### 1. ADMIRALTY CODE RATING SYSTEM

```yaml
# MANDATORY FOR EVERY SOURCE
ADMIRALTY_RATINGS:
  source_reliability:
    A: "Completely reliable"
    B: "Usually reliable"
    C: "Fairly reliable"
    D: "Not usually reliable"
    E: "Unreliable"
    F: "Cannot be judged"

  information_credibility:
    1: "Confirmed by other sources"
    2: "Probably true"
    3: "Possibly true"
    4: "Doubtful"
    5: "Improbable"
    6: "Cannot be judged"

  required_marking:
    example: "[SOURCE: Reuters B2]" # Usually reliable, probably true
    format: "[SOURCE: {name} {letter}{number}]"
```

### 2. FIVE-STEP OSINT PROCESS

```yaml
MANDATORY_PROCESS:
  1_planning:
    - Define objectives
    - Set requirements
    - Establish standards

  2_collection:
    - Multiple sources
    - Document everything
    - Preserve evidence

  3_processing:
    - Organize data
    - Identify patterns
    - Flag inconsistencies

  4_analysis:
    - Apply Admiralty ratings
    - Test alternatives
    - Assess confidence

  5_reporting:
    - Structured presentation
    - Evidence included
    - Limitations documented
```

### 3. ALTERNATIVE HYPOTHESIS REQUIREMENT

```yaml
FOR_EVERY_FINDING:
  mandatory_alternatives:
    - "Coincidence not coordination"
    - "Business practice not espionage"
    - "Market forces not strategy"
    - "Regulatory requirement not targeting"
    - "Technical necessity not theft"

  documentation:
    - Which alternatives tested
    - Evidence for each
    - Evidence against each
    - Why dismissed or accepted

  marking:
    "[ALTERNATIVES CONSIDERED: Business practice, market forces, coincidence]"
    "[ALTERNATIVE REJECTED: Timeline inconsistent with market explanation]"
```

### 4. SOURCE EVALUATION FIVE QUESTIONS

```yaml
BEFORE_USING_ANY_SOURCE:
  evaluate:
    1_relevance: "Does it relate to objective?"
    2_reliability: "Is source trustworthy?"
    3_accuracy: "Is information correct?"
    4_timeliness: "Is data current?"
    5_objectivity: "Is there bias?"

  if_any_fail:
    action: "Mark clearly in analysis"
    example: "[WARNING: Source dated 2019, may not reflect current]"
```

### 5. CHAIN OF CUSTODY DOCUMENTATION (No Screenshots - Text Preservation)

```yaml
FOR_EVERY_CLAIM:
  document:
    source_url: "Exact location"
    access_time: "YYYY-MM-DD HH:MM UTC"
    exact_quote: "Preserve key claims verbatim"
    context: "Surrounding information"
    admiralty: "B2, C3, etc"
    verification_path: "How to find again"
    wayback_check: "Archive.org if available"
    corroboration: "What was sought"
    gaps: "What's missing"
    alternatives: "What was tested"

  example:
    claim: "Technology transfer occurred"
    source: "reuters.com/article/123"
    accessed: "2025-09-19 14:00 UTC"
    exact_quote: "Leonardo signed agreement for maintenance training"
    context: "Article about Asian expansion"
    admiralty: "B2"
    verification: "Search: 'Leonardo China maintenance 2025'"
    wayback: "Check archive.org for March 2025"
    corroboration: "Sought patents, SEC - not found"
    gaps: "Financial details missing"
    alternatives: "Market purchase considered"
```

---

## 🔄 UPDATES TO CHATGPT PROMPT

### Add After Evidence Standards Section:

```yaml
ADMIRALTY_AND_VERIFICATION:
  every_source_requires:
    - Admiralty rating (A-F, 1-6)
    - Verification attempt
    - Alternative hypothesis
    - Documentation chain

  narrative_integration:
    "According to [Reuters B2], technology transfer occurred.
     [ALTERNATIVES: Tested market purchase, regulatory requirement]
     [CORROBORATION: No patents found, SEC silent]
     While only moderately reliable, including due to strategic importance."
```

### Add to Narrative Framework:

```yaml
STORY_WITH_ADMIRALTY:
  not_just: "Sources say"
  but: "Reuters [B2] reports, while industry blog [E4] claims"

  hierarchy:
    lead_with: "A1 and B1 sources"
    support_with: "B2 and C2 sources"
    acknowledge: "D and E sources exist but doubtful"
    avoid: "F sources unless noting uncertainty"
```

---

## 🔄 UPDATES TO CLAUDE CODE PROMPT

### Add to Processing Section:

```python
def rate_source(source):
    """
    MANDATORY Admiralty rating
    """
    reliability = assess_source_history(source)
    credibility = assess_information_quality(source)

    return {
        "rating": f"{reliability}{credibility}",
        "confidence_impact": calculate_impact(reliability, credibility)
    }

def test_alternatives(finding):
    """
    MANDATORY alternative testing
    """
    alternatives = [
        "coincidence",
        "business_practice",
        "market_forces",
        "regulation",
        "technical_necessity"
    ]

    results = {}
    for alt in alternatives:
        results[alt] = {
            "evidence_for": find_supporting(alt),
            "evidence_against": find_contradicting(alt),
            "likelihood": calculate_likelihood(alt)
        }

    return results
```

### Add to Output Format:

```yaml
EVERY_OUTPUT_MUST_INCLUDE:
  source_ratings:
    "Reuters [B2]"
    "SEC Filing [A1]"
    "Blog post [E4]"

  alternatives_tested:
    "[ALTERNATIVES: 5 tested]"
    "[MUNDANE EXPLANATION: Publisher schedule]"
    "[REJECTED: Timeline inconsistent]"

  verification_attempts:
    "[VERIFICATION: Sought patents - none found]"
    "[CORROBORATION: SEC silent on matter]"
    "[ECHO CHECK: All cite same source]"
```

---

## ⚠️ COGNITIVE BIAS WARNINGS

### Must Add to Both Prompts:

```yaml
BIAS_CHECKPOINT_QUESTIONS:
  confirmation_bias:
    ask: "Am I seeking only supporting evidence?"
    fix: "Actively search for contradicting data"

  anchoring_bias:
    ask: "Am I over-weighting first information?"
    fix: "Re-evaluate with all evidence equally"

  availability_bias:
    ask: "Am I overvaluing recent/memorable events?"
    fix: "Check historical patterns"

  mirror_imaging:
    ask: "Am I assuming they think like us?"
    fix: "Consider cultural/strategic differences"

REQUIRED_CHECKS:
  - Run bias check before conclusions
  - Document which biases considered
  - Note potential remaining biases
```

---

## 🎯 IMPLEMENTATION CHECKLIST

### For ChatGPT v7.1:
- [ ] Add Admiralty rating system
- [ ] Integrate 5-step OSINT process
- [ ] Require alternative hypotheses
- [ ] Add source evaluation criteria
- [ ] Include chain of custody
- [ ] Add bias warnings

### For Claude Code v7.0:
- [ ] Add Admiralty rating functions
- [ ] Implement alternative testing
- [ ] Add verification tracking
- [ ] Include documentation requirements
- [ ] Add bias checks
- [ ] Update output formats

### For Both:
- [ ] Reference OSINT_BEST_PRACTICES_SYNTHESIS.md
- [ ] Emphasize "evaluation is ongoing"
- [ ] Add "trace to original source" requirement
- [ ] Include echo chamber detection
- [ ] Mandate structured reporting

---

## 📝 SAMPLE OUTPUT WITH NEW STANDARDS

```markdown
## Finding: Technology Transfer to China

**Primary Source:** Reuters [B2] - Usually reliable, probably true
**URL:** reuters.com/article/leonardo-china-12345
**Accessed:** 2025-09-19 14:00 UTC
**Exact Quote:** "Leonardo S.p.A. signed a 50 million euro agreement for helicopter maintenance training"
**Context:** Article about Leonardo's expansion in Asian markets
**Verification Path:** Search "Leonardo China helicopter 50 million 2025"
**Wayback Check:** archive.org/web/*/reuters.com/article/leonardo-china-12345

**Corroboration Attempted:**
- SEC EDGAR: No relevant filings found
- USPTO: No matching patents
- LinkedIn: No personnel transfers identified
- Conference records: No joint presentations

**Admiralty Assessment:**
- Reuters report: B2 (Usually reliable, probably true)
- No corroborating sources found: Single source warning

**Alternative Hypotheses Tested:**
1. Coincidence: Rejected - timing too specific
2. Market purchase: Possible - cannot rule out
3. Business practice: Unlikely - unusual for sector
4. Regulation: Rejected - no regulatory requirement
5. Technical necessity: Possible - standard compatibility

**Confidence:** 35% (Single B2 source, no corroboration)

**Gaps:**
- [EVIDENCE GAP: Financial details unavailable]
- [VERIFICATION GAP: No primary documents]
- [CORROBORATION GAP: Single source only]

**Inclusion Rationale:** Despite low confidence, strategic importance warrants inclusion with heavy caveats.
```

---

## 🔥 THE BOTTOM LINE

These aren't suggestions - they're requirements from CIA/DIA/OSINT standards:

1. **Admiralty ratings** - MANDATORY
2. **Alternative hypotheses** - MANDATORY
3. **Verification attempts** - MANDATORY
4. **Chain of custody** - MANDATORY
5. **Bias checks** - MANDATORY

**Failure to implement = Analytical failure waiting to happen**

---

*Based on synthesis of CIA, DIA, and industry OSINT standards*
*These updates will prevent fabrication and ensure analytical rigor*
