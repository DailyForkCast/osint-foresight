# Triangle Analysis Template v2.0
## Deep Investigation Framework for US-China Technology Vulnerabilities

**Date:** 2025-09-14
**Purpose:** Standardize deep triangle analysis across all entities

---

## 🎯 Core Principle

**"Company X has office in China" is lazy analysis. We need to know EXACTLY what technologies are at risk and HOW China can exploit them.**

---

## 📋 MANDATORY INVESTIGATION TEMPLATE

For EVERY entity with China connections, complete this analysis:

### SECTION 1: ENTITY MAPPING

```json
{
  "entity_name": "",
  "china_presence": {
    "type": "Office/JV/Subsidiary/Partnership",
    "locations": [],
    "established": "YYYY",
    "activities": "SPECIFIC activities, not generic",
    "personnel_count": "If known",
    "revenue_from_china": "Amount or percentage"
  },
  "us_presence": {
    "defense_contracts": "Count and value",
    "key_programs": "Named programs",
    "classification_levels": "If known",
    "critical_technologies": []
  }
}
```

### SECTION 2: TECHNOLOGY OVERLAP MATRIX

| Technology Domain | US Military Application | China Civil Access | Technology Maturity | Strategic Value to China | Overlap Risk |
|-------------------|------------------------|-------------------|-------------------|------------------------|--------------|
| Example: Helicopter Platform | MH-139 Grey Wolf | AW139 sales (40+ units) | Mature (TRL 9) | MEDIUM - Incremental | CRITICAL |
| Example: OSPREY AESA Radar | MQ-8C Fire Scout | None direct | Cutting-edge (TRL 7-8) | CRITICAL - Leapfrog potential | HIGH |
| Example: Office Supplies | Generic across services | Full access | Commodity (TRL 9) | NONE | MINIMAL |

#### Technology Maturity Levels (TRL)
- **TRL 9**: Fully mature, operational systems
- **TRL 7-8**: Advanced development, cutting-edge
- **TRL 4-6**: Demonstration/validation phase
- **TRL 1-3**: Basic research, emerging

#### Strategic Value to China Assessment
- **CRITICAL - Leapfrog**: Would advance China 5-10 years
- **HIGH - Accelerator**: Would save China 2-5 years development
- **MEDIUM - Incremental**: Would provide useful improvements
- **LOW - Marginal**: Minor benefits only
- **NONE**: No strategic value (commodity items)

### SECTION 3: EXPLOITATION PATHWAY ANALYSIS

For EACH technology overlap, document:

#### Physical Access Assessment
```
Can China physically access this technology?
[ ] Purchase/acquisition
[ ] Maintenance access
[ ] Joint venture access
[ ] Reverse engineering opportunity
[ ] Supply chain infiltration

Evidence: [Specific examples with sources]
```

#### Knowledge Transfer Vectors
```
How does technical knowledge transfer?
[ ] Documentation (manuals, specs)
[ ] Training programs
[ ] Personnel movement
[ ] Software/firmware access
[ ] Academic collaboration

Evidence: [Specific examples with sources]
```

#### Intelligence Collection Value
```
What can China learn?
[ ] Performance parameters
[ ] Vulnerabilities/weaknesses
[ ] Countermeasure development
[ ] Manufacturing techniques
[ ] Operational procedures

Specific Intelligence: [Exactly what China gains]
```

### SECTION 3.5: TECHNOLOGY VALUE ASSESSMENT

#### Strategic Value Calculation
```json
{
  "technology": "[Name]",
  "advancement_level": {
    "global_state_of_art": "Where does this tech rank globally?",
    "us_advantage": "How far ahead is US? (years)",
    "china_current_level": "Where is China now?",
    "gap_size": "Years behind or specific capabilities lacking"
  },
  "strategic_importance": {
    "military_criticality": "Essential/Important/Useful/Marginal",
    "economic_value": "Market size and growth potential",
    "dual_use_applications": "List specific civil/military crossovers",
    "dependency_creation": "Does this create long-term dependence?"
  },
  "china_alternatives": {
    "domestic_development": "Time/cost to develop independently",
    "other_sources": "Can China get this elsewhere?",
    "workarounds": "Can China achieve goals without this?"
  },
  "time_sensitivity": {
    "technology_lifecycle": "How long until obsolete?",
    "first_mover_advantage": "Benefits of early access",
    "integration_timeline": "How quickly can China deploy?"
  }
}
```

#### Examples of Strategic Value Differences

**HIGH VALUE - Cutting Edge:**
- OSPREY AESA radar algorithms (TRL 7-8)
- Quantum encryption systems (TRL 4-6)
- Hypersonic materials (TRL 5-7)
- AI-enabled target recognition (TRL 6-8)

**MEDIUM VALUE - Mature but Useful:**
- Helicopter platforms (TRL 9)
- Standard encryption (TRL 9)
- Conventional materials (TRL 9)
- Basic sensor fusion (TRL 8-9)

**LOW VALUE - Commodity:**
- Office furniture (TRL 9)
- Standard computers (TRL 9)
- Basic vehicles (TRL 9)
- Common materials (TRL 9)

### SECTION 4: SPECIFIC VULNERABILITY ASSESSMENT

#### Immediate Risks (0-6 months)
- Technology: [Specific system/component]
- Vulnerability: [Exact weakness]
- Exploitation method: [How China could use it]
- Evidence: [Source]
- Probability: [Band] Confidence: [Level]

#### Medium-term Risks (6-24 months)
- Technology: [Specific system/component]
- Vulnerability: [Exact weakness]
- Exploitation method: [How China could use it]
- Evidence: [Source]
- Probability: [Band] Confidence: [Level]

#### Long-term Risks (2+ years)
- Technology: [Specific system/component]
- Vulnerability: [Exact weakness]
- Exploitation method: [How China could use it]
- Evidence: [Source]
- Probability: [Band] Confidence: [Level]

### SECTION 5: COUNTERMEASURE DEVELOPMENT POTENTIAL

What specific countermeasures could China develop?

```json
{
  "electronic_warfare": [
    "Specific jamming frequencies based on knowledge of system",
    "Exploitation of identified electromagnetic signatures"
  ],
  "kinetic_defeat": [
    "Targeting known structural weak points",
    "Exploiting maintenance vulnerabilities"
  ],
  "cyber_exploitation": [
    "Software vulnerabilities from training systems",
    "Firmware backdoors from supply chain"
  ],
  "operational_disruption": [
    "Knowledge of operational limits",
    "Understanding of failure modes"
  ]
}
```

### SECTION 6: EVIDENCE QUALITY ASSESSMENT

| Claim | Evidence Type | Source | Date | Verification Status |
|-------|--------------|--------|------|-------------------|
| 40+ AW139s in China | Corporate filing | Leonardo Annual Report | 2024 | CONFIRMED |
| Simulator installation | Press release | Leonardo.com | 2024 | CONFIRMED |
| MH-139 based on AW139 | Gov procurement | USAF documents | 2023 | CONFIRMED |

### SECTION 7: INTELLIGENCE GAPS

What we still need to know:
1. [Specific question with collection method]
2. [Specific question with collection method]
3. [Specific question with collection method]

---

## 🚨 RED FLAGS REQUIRING IMMEDIATE DEEP DIVE

If you find ANY of these, conduct full analysis immediately:

### CRITICAL Red Flags
- [ ] Same product/platform sold to both US military and China
- [ ] Training systems or simulators provided to China
- [ ] Maintenance facilities in China for US-relevant systems
- [ ] Chinese personnel in facilities that also work on US programs
- [ ] Common software/firmware between US and China systems

### HIGH Red Flags
- [ ] Joint ventures with Chinese entities in relevant tech domains
- [ ] Supply chain dependencies for US programs
- [ ] Technology licensing agreements with Chinese firms
- [ ] Academic partnerships in defense-relevant research
- [ ] Personnel exchanges between programs

### MEDIUM Red Flags
- [ ] Sales offices in China for dual-use technologies
- [ ] Participation in Chinese trade shows/conferences
- [ ] Chinese investment (even minority stakes)
- [ ] Outsourcing to China for any components
- [ ] Historical technology transfers (pre-2020)

---

## 📊 SCORING FRAMEWORK

### Triangle Risk Score Components

#### Technology Criticality (1-5)
- 5: Core US military capability
- 4: Important military system
- 3: Dual-use with military application
- 2: Primarily commercial, some military use
- 1: Commercial only

#### China Access Level (1-5)
- 5: Complete physical possession
- 4: Maintenance/training access
- 3: Documentation/software access
- 2: Observation/interaction only
- 1: Public information only

#### Exploitation Ease (1-5)
- 5: Direct application possible
- 4: Minor adaptation required
- 3: Significant development needed
- 2: Major barriers to exploitation
- 1: Theoretical only

#### Time Sensitivity (1-5)
- 5: Immediate threat (<6 months)
- 4: Near-term threat (6-12 months)
- 3: Medium-term (1-2 years)
- 2: Long-term (2-5 years)
- 1: Speculative (5+ years)

**OVERALL RISK = (Criticality × Access × Ease × Time) / 25**
- 20-25: CRITICAL (Immediate action required)
- 15-19: HIGH (Priority attention needed)
- 10-14: MEDIUM (Monitor closely)
- 5-9: LOW (Routine monitoring)
- 0-4: MINIMAL (Note for records)

---

## 💡 EXAMPLE: COMPLETE ANALYSIS

### Entity: Leonardo S.p.A.
**Triangle Risk Score: 24/25 (CRITICAL)**

**Why this score:**
- Technology Criticality: 5 (MH-139 is frontline USAF asset)
- China Access: 5 (40+ physical aircraft)
- Exploitation Ease: 5 (Same platform, direct study possible)
- Time Sensitivity: 4.8 (Simulator installation 2026)

**Specific Vulnerabilities Identified:**
1. **Rotor Dynamics**: China can measure exact vibration frequencies for interference/jamming
2. **Flight Envelope**: Simulator reveals precise operational limits for exploitation
3. **Maintenance Cycles**: Access to maintenance schedules enables targeted operations
4. **Avionics Architecture**: Understanding of system integration aids cyber operations
5. **Materials/Coatings**: Physical samples enable signature analysis and replication

**Exploitation Pathways Documented:**
- Physical: Complete disassembly of purchased helicopters
- Digital: Flight simulator software reverse engineering
- Personnel: Chinese engineers trained by Leonardo
- Documentary: Full technical manuals and training materials

**Intelligence Value to China:**
- Immediate: US Air Force helicopter vulnerabilities
- 6-month: Countermeasure development
- 2-year: Incorporation into Chinese military systems
- 5-year: Next-generation helicopter informed by US technology

---

## 📝 REPORTING REQUIREMENTS

### For Claude Code:
- Generate `triangle_analysis.json` for each entity
- Calculate risk scores automatically
- Flag entities exceeding threshold
- Create `exploitation_pathways.json`
- Generate `intelligence_gaps.json`

### For ChatGPT:
- Write narrative analysis (1,000+ words) for HIGH/CRITICAL risks
- Include specific examples with citations
- Explain implications for policymakers
- Provide actionable recommendations
- Document evidence quality

---

## ⚠️ QUALITY STANDARDS

### Acceptable Analysis:
✅ Names specific technologies and systems
✅ Documents exact access mechanisms
✅ Calculates quantified risk scores
✅ Provides evidence with sources
✅ Identifies concrete countermeasures China could develop

### Unacceptable Analysis:
❌ "Potential dual-use concerns"
❌ "May pose risks"
❌ "Could be problematic"
❌ "China bad" without specifics
❌ Generic warnings without evidence

---

## FINAL REMINDER

**Every China connection requires this level of analysis. If we can't complete this template, we don't understand the risk well enough to report it.**

The goal is not to find China connections - it's to understand EXACTLY what technologies are at risk and HOW China can exploit them. Only then can we provide actionable intelligence.
