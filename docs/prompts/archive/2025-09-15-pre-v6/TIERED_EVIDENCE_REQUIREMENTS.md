# Tiered Evidence Requirements Framework
## Strategic Value-Based Validation Standards

**Version:** 1.0
**Date:** 2025-09-14
**Purpose:** Ensure critical findings aren't lost to perfectionism

---

## 🎯 Core Principle

**"Evidence requirements must be INVERSELY proportional to strategic importance."**

The MORE critical a finding, the LOWER the evidence bar for inclusion (with appropriate caveats).

---

## 📊 EVIDENCE REQUIREMENT TIERS

### Tier 1: CRITICAL Findings (Relaxed Requirements)
**Definition:** Game-changing intelligence that could alter strategic assessments

**Examples:**
- Same exact system sold to US military and China
- Active technology transfer to adversary
- Imminent capability loss
- Deception operations discovered
- Novel exploitation pathways

**Evidence Requirements:**
```python
critical_requirements = {
    "minimum_sources": 1,  # Even single source acceptable
    "corroboration": "Preferred but not required",
    "specificity": "Best available, gaps acceptable",
    "confidence_threshold": "Any level with transparency",
    "inclusion_decision": "ALWAYS INCLUDE with caveats",
    "gap_marking": "MANDATORY - all unknowns documented"
}
```

**Presentation Template:**
```markdown
⚠️ CRITICAL FINDING - LIMITED EVIDENCE ⚠️
Finding: [Description]
Strategic Impact: [Why this matters]
Available Evidence: [What we have]
Gaps: [What we don't know]
Confidence: LOW/MEDIUM (adjusted for gaps)
Collection Priority: URGENT
Caveat: Requires immediate verification
```

---

### Tier 2: HIGH Findings (Standard Requirements)
**Definition:** Significant intelligence affecting multiple programs or capabilities

**Examples:**
- Major technology overlap identified
- New Chinese partnership in sensitive domain
- Supply chain vulnerability discovered
- Key personnel movement
- Strategic funding flows

**Evidence Requirements:**
```python
high_requirements = {
    "minimum_sources": 2,  # Two sources preferred
    "corroboration": "One source must corroborate",
    "specificity": "Technology categories acceptable",
    "confidence_threshold": ">10/20",
    "inclusion_decision": "Include if confidence >10",
    "gap_marking": "Required for all gaps"
}
```

---

### Tier 3: MEDIUM Findings (Elevated Requirements)
**Definition:** Notable intelligence with focused impact

**Examples:**
- Routine technology sales
- Academic collaborations
- Known partnerships continuing
- Standard commercial activity
- Historical relationships

**Evidence Requirements:**
```python
medium_requirements = {
    "minimum_sources": 2,  # Two required
    "corroboration": "Both must align",
    "specificity": "Specific details needed",
    "confidence_threshold": ">12/20",
    "inclusion_decision": "Include if well-evidenced",
    "gap_marking": "Note significant gaps"
}
```

---

### Tier 4: LOW Findings (Strict Requirements)
**Definition:** Background information or context

**Examples:**
- Public information
- Well-known facts
- Generic capabilities
- Non-sensitive commerce
- Administrative details

**Evidence Requirements:**
```python
low_requirements = {
    "minimum_sources": 3,  # Full validation
    "corroboration": "All must align",
    "specificity": "Complete details required",
    "confidence_threshold": ">15/20",
    "inclusion_decision": "Exclude if gaps exist",
    "gap_marking": "Not worth noting gaps"
}
```

---

## 🎯 STRATEGIC VALUE ASSESSMENT

### How to Determine Strategic Value:

```python
def assess_strategic_value(finding):
    """
    Score each factor 1-5, total determines tier
    """
    factors = {
        "us_military_impact": 0,  # Direct effect on US capabilities
        "china_advancement": 0,  # Years of progress gained
        "exploitation_speed": 0,  # How quickly weaponized
        "mitigation_difficulty": 0,  # How hard to counter
        "detection_difficulty": 0  # How hard to discover
    }

    total = sum(factors.values())

    if total >= 20:
        return "CRITICAL"
    elif total >= 15:
        return "HIGH"
    elif total >= 10:
        return "MEDIUM"
    else:
        return "LOW"
```

---

## 📈 WEIGHTED QUALITY CALCULATION

### Not All Findings Are Equal:

```python
def calculate_quality_score(all_findings):
    """
    Weight findings by strategic value
    """
    scoring = {
        "CRITICAL": {"weight": 10, "required_inclusion": 1.0},
        "HIGH": {"weight": 5, "required_inclusion": 0.95},
        "MEDIUM": {"weight": 2, "required_inclusion": 0.90},
        "LOW": {"weight": 0.5, "required_inclusion": 0.50}
    }

    results = {
        "total_value": 0,
        "captured_value": 0,
        "critical_missed": [],
        "high_missed": []
    }

    for finding in all_findings:
        tier = assess_strategic_value(finding)
        weight = scoring[tier]["weight"]
        required = scoring[tier]["required_inclusion"]

        results["total_value"] += weight

        if finding.included:
            results["captured_value"] += weight
        elif tier == "CRITICAL":
            results["critical_missed"].append(finding)  # UNACCEPTABLE
        elif tier == "HIGH":
            results["high_missed"].append(finding)  # PROBLEMATIC

    results["capture_rate"] = results["captured_value"] / results["total_value"]
    results["acceptable"] = len(results["critical_missed"]) == 0

    return results
```

---

## 💡 PRACTICAL EXAMPLES

### Example 1: CRITICAL with Single Source
```json
{
  "finding": "Chinese engineer photographed inside F-35 facility",
  "evidence": {
    "sources": 1,
    "type": "HUMINT report",
    "credibility": "Unknown"
  },
  "strategic_value": "CRITICAL",
  "decision": "INCLUDE",
  "presentation": "URGENT: Unconfirmed report of Chinese personnel in F-35 facility. Single source, requires immediate verification. Including due to critical implications if true.",
  "confidence": "LOW (5/20)",
  "gaps": ["Identity unconfirmed", "Facility unnamed", "Date uncertain"]
}
```

### Example 2: HIGH with Good Evidence
```json
{
  "finding": "Quantum algorithm shared via GitHub",
  "evidence": {
    "sources": 3,
    "type": "Technical analysis + commits + paper",
    "credibility": "High"
  },
  "strategic_value": "HIGH",
  "decision": "INCLUDE",
  "presentation": "Confirmed: Quantum algorithm transferred via public repository.",
  "confidence": "HIGH (17/20)",
  "gaps": []
}
```

### Example 3: MEDIUM with Gaps
```json
{
  "finding": "Italian university collaboration with Beijing",
  "evidence": {
    "sources": 2,
    "type": "MOU + news report",
    "credibility": "Medium"
  },
  "strategic_value": "MEDIUM",
  "specific_technology": "Unknown",
  "decision": "INCLUDE with caveats",
  "presentation": "Partnership confirmed, specific technologies unknown.",
  "confidence": "MEDIUM (12/20)",
  "gaps": ["Technology focus unclear", "Personnel numbers unknown"]
}
```

### Example 4: LOW with Perfect Evidence
```json
{
  "finding": "Office supplies sold to Chinese firms",
  "evidence": {
    "sources": 5,
    "type": "Trade data + invoices + reports",
    "credibility": "High"
  },
  "strategic_value": "NONE",
  "decision": "EXCLUDE",
  "rationale": "No strategic relevance, not worth report space"
}
```

---

## 🔄 DECISION FLOWCHART

```
Finding Identified
        |
        v
Assess Strategic Value
        |
    ____|____
    |        |
CRITICAL    OTHER
    |        |
    v        v
INCLUDE   Evidence Check
(mark      |
 gaps)  ___|___
        |      |
      GOOD   POOR
        |      |
        v      v
    INCLUDE  Value Check
             |
          HIGH?
          /    \
        YES     NO
         |       |
     INCLUDE  EXCLUDE
     w/GAPS
```

---

## 📝 GAP DOCUMENTATION STANDARDS

### When Including with Gaps, Document:

```markdown
## Finding: [Title]

### What We Know:
- Confirmed: [List definite facts]
- Sources: [Available evidence]

### What We Don't Know:
- [ ] Gap 1: [Specific missing information]
- [ ] Gap 2: [Another gap]
- [ ] Gap 3: [Another gap]

### Why Included Despite Gaps:
- Strategic importance: [Explanation]
- Potential impact: [If confirmed]
- Risk of exclusion: [What we miss if wrong]

### Confidence Impact:
- Base confidence: X/20
- Adjusted for gaps: Y/20 (reduced by Z)

### Collection Priorities:
1. URGENT: [Most critical gap to fill]
2. HIGH: [Important gap]
3. MEDIUM: [Useful addition]
```

---

## ⚖️ BALANCING INCLUSION VS CREDIBILITY

### Include When:
- Strategic value is HIGH or CRITICAL
- Exclusion creates analytical blind spot
- Pattern wouldn't be visible without it
- Time-sensitive action needed
- Deception indicators present

### Exclude When:
- Strategic value is LOW
- Evidence completely absent
- Contradicting evidence stronger
- Including would mislead
- Noise overwhelms signal

### Always:
- Mark gaps transparently
- Adjust confidence appropriately
- Document decision rationale
- Identify collection needs
- Review if new evidence emerges

---

## 📊 REPORTING METRICS

### Track These Statistics:

```python
reporting_metrics = {
    "critical_findings": {
        "total": 10,
        "included": 10,  # MUST BE 100%
        "with_gaps": 3,
        "gap_transparency": "100%"
    },
    "high_findings": {
        "total": 20,
        "included": 19,  # 95% minimum
        "with_gaps": 5,
        "gap_transparency": "100%"
    },
    "medium_findings": {
        "total": 50,
        "included": 40,  # 80% typical
        "excluded_for_evidence": 10
    },
    "low_findings": {
        "total": 200,
        "included": 20,  # 10% typical
        "excluded_for_relevance": 180
    },
    "weighted_capture": "94%"  # What matters
}
```

---

## ✅ IMPLEMENTATION CHECKLIST

For every finding:

1. **Assess Strategic Value**
   - [ ] Score impact factors
   - [ ] Determine tier (CRITICAL/HIGH/MEDIUM/LOW)

2. **Apply Appropriate Evidence Standard**
   - [ ] Use tier-specific requirements
   - [ ] Don't over-require for CRITICAL

3. **Make Inclusion Decision**
   - [ ] CRITICAL = always include
   - [ ] HIGH = include unless terrible evidence
   - [ ] MEDIUM = include if decent evidence
   - [ ] LOW = include only if perfect

4. **Document Transparently**
   - [ ] Mark all gaps
   - [ ] Adjust confidence
   - [ ] Explain decision
   - [ ] Add collection priorities

5. **Calculate Weighted Metrics**
   - [ ] Weight by value not count
   - [ ] Ensure critical capture = 100%
   - [ ] Track gap transparency

---

## REMEMBER

**A possible F-35 compromise with single-source reporting > 100 confirmed pencil sales with perfect documentation**

**Evidence standards must serve intelligence value, not bureaucratic completeness**

**Transparency about uncertainty maintains credibility while ensuring critical intelligence isn't lost**

**Mark what you don't know as clearly as what you do know**

**The goal is preventing strategic surprise, not winning documentation awards**
