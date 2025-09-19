# Phase-Specific Validation Guide
## How to Apply Rigor Requirements in Each Phase

**Version:** 1.0
**Date:** 2025-09-14
**Purpose:** Phase-by-phase implementation of validation standards

---

## 📋 Phase 0: Scoping & Setup

### Validation Focus
- Initial threat assessment accuracy
- Domain prioritization justification
- Data source verification

### Required Validations
```python
phase0_validation = {
    "threat_vectors": {
        "china_interest": "Must cite specific Chinese publications/investments",
        "evidence": "Patent filings, academic papers, investment records",
        "not_acceptable": "Generic 'China interested in technology'"
    },
    "domain_selection": {
        "justification": "Quantified importance metrics",
        "evidence": "Trade data, patent counts, investment flows",
        "alternatives": "Why these domains over others?"
    }
}
```

### Example Output
```json
{
  "domain": "Quantum Computing",
  "china_interest_evidence": [
    "127 patents filed by Chinese Academy of Sciences in 2023",
    "€2.1B investment in quantum research announced",
    "47 joint papers with target country institutions"
  ],
  "strategic_value": "Would advance China 5-7 years",
  "confidence": 16
}
```

---

## 📊 Phase 1: Setup & Indicators

### Validation Focus
- Data source reliability assessment
- Baseline metric accuracy
- Trend validation

### Required Validations
```python
phase1_validation = {
    "data_sources": {
        "quality_check": "API availability, update frequency, coverage",
        "alternatives": "What sources unavailable and why",
        "limitations": "Explicit gaps in coverage"
    },
    "metrics": {
        "verification": "Cross-check with 2+ sources",
        "time_series": "Validate historical data points",
        "anomalies": "Explain outliers with evidence"
    }
}
```

### Triple Source Example
```
R&D Spending Claim: "1.45% of GDP"
Source 1: [GOV] National Statistics Office
Source 2: [OECD] Science & Technology Indicators
Source 3: [EU] Eurostat R&D Statistics
Confidence: High (sources align within 0.02%)
```

---

## 🔬 Phase 2: Technology Indicators

### Validation Focus
- Innovation metrics verification
- China collaboration quantification
- Technology maturity assessment

### Required Validations
```python
phase2_validation = {
    "patent_analysis": {
        "classification": "IPC codes must be specific",
        "china_overlap": "Joint patents with evidence",
        "quality": "Citations, not just counts"
    },
    "collaboration": {
        "evidence": "Named researchers, specific projects",
        "timeline": "When collaboration started/peaked",
        "alternatives": "Commercial vs strategic intent"
    },
    "trl_assessment": {
        "required": "Every technology gets TRL score",
        "evidence": "Publications, prototypes, deployments",
        "china_gap": "Years behind with evidence"
    }
}
```

### Technology Assessment Template
```json
{
  "technology": "Photonic quantum processors",
  "trl": 6,
  "evidence": "Laboratory demonstration published Nature 2024",
  "china_status": "TRL 4, 2-3 years behind",
  "strategic_value": "HIGH - would enable unbreakable encryption",
  "exploitation_pathway": "Joint PhD program provides access"
}
```

---

## 🏭 Phase 3: Technology Landscape

### Validation Focus
- Organization capability verification
- China connection depth analysis
- Technology overlap identification

### Required Validations
```python
phase3_validation = {
    "organization_claims": {
        "capabilities": "Specific products/services, not categories",
        "evidence": "Annual reports, patents, contracts",
        "china_ties": "MOUs, joint ventures, sales offices"
    },
    "deep_dive_triggers": {
        "same_platform": "Full Leonardo-style analysis",
        "training_systems": "Document access level",
        "maintenance": "Map vulnerability exposure"
    },
    "alternatives": {
        "business_logic": "Why China connection exists",
        "historical": "When relationship started",
        "regulatory": "What rules permit this"
    }
}
```

### Deep Dive Example
```json
{
  "trigger": "Same navigation system in civilian and military aircraft",
  "validation_performed": {
    "sameness_check": "Model numbers compared - 90% identical",
    "china_access": "27 civilian aircraft with system",
    "alternatives_tested": [
      "Export version (FALSE - same hardware)",
      "Old technology (FALSE - latest generation)",
      "No military value (FALSE - jamming vulnerabilities)"
    ],
    "confidence": 17,
    "oversight_gap": "Civilian certification doesn't consider military implications"
  }
}
```

---

## 🔗 Phase 4: Supply Chain

### Validation Focus
- Dependency verification
- China control quantification
- Alternative assessment

### Required Validations
```python
phase4_validation = {
    "dependencies": {
        "specificity": "Exact components, not categories",
        "evidence": "Supply chain disclosures, customs data",
        "china_percentage": "Documented market share"
    },
    "alternatives": {
        "technical": "Performance impact quantified",
        "timeline": "Qualification period specified",
        "cost": "Price differential calculated"
    },
    "exploitation": {
        "methods": "Specific ways to weaponize",
        "timeline": "When shortage would impact",
        "programs": "Named US systems affected"
    }
}
```

### Critical Dependency Template
```json
{
  "component": "Gallium arsenide wafers, 6-inch, semi-insulating",
  "china_control": "73% global production",
  "evidence": [
    "USGS Mineral Commodity Summary 2024",
    "Industry association data",
    "Company 10-K supply risk disclosures"
  ],
  "programs_affected": ["AN/APG-81 radar", "5G base stations"],
  "alternatives": {
    "option": "Japanese suppliers",
    "capacity": "27% global",
    "lead_time": "18 months to scale",
    "cost_impact": "2.3x current"
  }
}
```

---

## 🏛️ Phase 5: Institutions

### Validation Focus
- Partnership verification
- Personnel flow documentation
- Technology transfer evidence

### Required Validations
```python
phase5_validation = {
    "partnerships": {
        "documentation": "MOUs, agreements, announcements",
        "specificity": "Named programs, not 'collaboration'",
        "personnel": "Actual researcher names when possible"
    },
    "technology_transfer": {
        "documented": "Patents, publications proof",
        "suspected": "Circumstantial evidence",
        "confirmed": "Direct evidence required"
    },
    "oversight_gaps": {
        "classification": "Why transfer not caught",
        "incentives": "Why institutions allow",
        "barriers": "What prevents detection"
    }
}
```

---

## 💰 Phase 6: Funding

### Validation Focus
- Investment source verification
- Control mechanism identification
- Strategic intent assessment

### Required Validations
```python
phase6_validation = {
    "chinese_investment": {
        "ultimate_owner": "Trace through shells",
        "evidence": "Corporate registries, filings",
        "control": "Board seats, veto rights documented"
    },
    "alternatives": {
        "profit_motive": "ROI calculation",
        "market_access": "Commercial justification",
        "strategic": "Technology acquisition evidence"
    }
}
```

---

## 🌍 Phase 7: International Links

### Validation Focus
- Triangle completion mapping
- Data flow verification
- Control effectiveness

### Required Validations
```python
phase7_validation = {
    "triangles": {
        "mapping": "US → Country → China pathways",
        "evidence": "Specific programs, technologies",
        "timeline": "When connections established"
    },
    "controls": {
        "effectiveness": "What works/doesn't",
        "gaps": "Where controls absent",
        "evidence": "Enforcement actions, or lack thereof"
    }
}
```

---

## ⚠️ Phase 8: Risk Assessment

### Validation Focus
- Threat specificity
- Vulnerability verification
- Scenario plausibility

### Required Validations
```python
phase8_validation = {
    "every_risk": {
        "specificity": "Named technology, not category",
        "pathway": "Exact exploitation method",
        "evidence": "Supporting documentation",
        "alternatives": "5+ explanations tested",
        "confidence": "0-20 score calculated"
    },
    "extraordinary_claims": {
        "bombshell_score": "1-30 calculated",
        "peer_review": "Second opinion if >20",
        "language": "Measured, not alarmist"
    }
}
```

### Risk Validation Example
```json
{
  "risk": "Quantum algorithm exposure via joint research",
  "specific_technology": "Variational quantum eigensolver v2.3",
  "pathway": "GitHub commit by visiting researcher",
  "evidence": [
    "Commit hash: a4f2c3d",
    "Researcher affiliation confirmed",
    "Algorithm now in Chinese paper"
  ],
  "alternatives_tested": 5,
  "alternatives_rejected": 4,
  "mixed_factors": true,
  "confidence": 16,
  "classification": "SIGNIFICANT_FINDING"
}
```

---

## 🔮 Phase 9-13: Advanced Analysis

### Validation Focus
- Projection justification
- Assumption documentation
- Uncertainty quantification

### Required Validations
```python
advanced_validation = {
    "forecasts": {
        "basis": "Evidence for projections",
        "alternatives": "Different scenarios",
        "confidence": "Probability bands"
    },
    "assumptions": {
        "explicit": "All assumptions stated",
        "tested": "Evidence for/against",
        "impact": "Sensitivity analysis"
    },
    "gaps": {
        "identified": "What we don't know",
        "impact": "How gaps affect analysis",
        "collection": "How to fill gaps"
    }
}
```

---

## 📊 VALIDATION METRICS BY PHASE

Track these metrics for each phase:

| Phase | Key Metrics | Target |
|-------|------------|--------|
| 0 | Claims sourced | 95% |
| 1 | Data verified | 90% |
| 2 | TRL assessed | 100% |
| 3 | Deep dives completed | 100% critical |
| 4 | Dependencies quantified | 95% |
| 5 | Partnerships verified | 90% |
| 6 | Investment traced | 95% |
| 7 | Triangles mapped | 100% |
| 8 | Risks validated | 100% |
| 9-13 | Assumptions explicit | 100% |

---

## ✅ PHASE TRANSITION CHECKLIST

Before moving to next phase:
- [ ] All required validations complete
- [ ] Extraordinary findings validated
- [ ] Alternatives documented
- [ ] Confidence scores calculated
- [ ] Gaps identified
- [ ] Quality metrics met

---

## REMEMBER

**Every phase has specific validation requirements.**

**Later phases build on earlier validation.**

**Extraordinary findings in ANY phase trigger deep validation.**

**Document what you can't verify as explicitly as what you can.**

**Quality over speed - better to be thorough.**
