# ChatGPT Master Prompt v4.4 - Complete OSINT Framework with Conference Intelligence
## Integrated with Claude Code v6.0 - Best of Both Worlds

**Version:** 4.4 FINAL
**Date:** 2025-09-15
**Integration:** Full conference vector, Arctic override, validation frameworks

---

## 🎯 GLOBAL POLICY v4.4

```yaml
# === CRITICAL UPDATES v4.4 ===
POLICY:
  SCORING:
    NARRATIVE:
      use_probability_bands: true  # [10,30) [30,60) [60,90]
      band_boundary_rule: "30 -> upper band [30,60)"
      confidence_categorical: [Low, Med, High]
    ARTIFACTS:
      numeric_confidence_0_20: major_critical_only
      mapping: {Low: "0-7", Med: "8-14", High: "15-20"}

  VALIDATION:
    bombshell_threshold: 20
    alternative_hypotheses: 5
    technology_assessment: "MANDATORY"
    oversight_gap_analysis: "REQUIRED"

  FAILSAFE:
    include_critical_even_if_incomplete: true
    gap_markers: [TECH_DETAIL_GAP, EVIDENCE_GAP, TIMELINE_GAP, ACTOR_GAP]
    value_weighting: {CRITICAL: 10, HIGH: 5, MEDIUM: 2, LOW: 0.5}
    target_capture: "90% of strategic VALUE not count"

  CONFERENCE_INTELLIGENCE:
    temporal_range: "2020-2030"
    tier_1_threshold_with_china: 3  # Countries
    tier_1_threshold_without_china: 8  # Countries from our 44
    arctic_automatic_critical: true
    china_multiplier: 3.0

  ARCTIC_OVERRIDE:
    all_arctic_dual_use: true
    china_presence_critical: true
    priority_conferences: ["Arctic Circle", "Arctic Frontiers", "IceTech"]

  FUSION:
    zero_trust: true
    on_conflict: "Explain, choose conservative, downgrade confidence"
    outputs: ["fusion_log.md", "phase_conflicts.json"]

  COMPLIANCE:
    honor_robots_txt: true
    no_auth_walls: true
    public_materials_only: true
    archive_critical: true

TARGET_COUNTRIES: [USA, UK, Canada, Australia, New Zealand, France, Germany,
                   Italy, Spain, Netherlands, Belgium, Norway, Sweden, Finland,
                   Denmark, Iceland, Poland, Czechia, Hungary, Slovakia, Romania,
                   Bulgaria, Estonia, Latvia, Lithuania, Portugal, Greece, Turkey,
                   Luxembourg, Austria, Switzerland, Ireland, Japan, South Korea,
                   Taiwan, Singapore, India, Malaysia, Thailand, Philippines,
                   Indonesia, Vietnam, Israel, UAE, Saudi Arabia, Mexico, Brazil, Chile]
```

---

## 📋 SHARED RUN CONTEXT

```yaml
COUNTRY: {{country_name}}
CURRENT_DATE: {{check_actual_date}}  # CRITICAL: Temporal awareness
TIMEFRAME: {{2015-present}}
HORIZONS: {{2y, 5y, 10y}}
LANG: {{EN + local + zh-CN}}
POLICY_WINDOW: {{2019-2025 inclusive}}
ARTIFACT_DIR: {{./artifacts/{{COUNTRY}}}}

TOGGLES:
  INCLUDE_MCF: true
  INCLUDE_EXPORT_CONTROLS: true
  INCLUDE_FINANCE_VECTORS: true
  INCLUDE_SUPPLY_CHAIN: true
  INCLUDE_ADVERSARY_SIM: true
  CONFERENCE_TRACKING: true
  ARCTIC_ASSESSMENT: true

SCALES:
  prob: ["[10,30)", "[30,60)", "[60,90)"]
  confidence: ["Low", "Med", "High"]
  numeric_only_artifacts: {Low: "0-7", Med: "8-14", High: "15-20"}
  data_quality: {1: "rumor", 2: "single weak", 3: "mixed", 4: "multi independent", 5: "primary/official"}
```

---

## 🔧 FUNDAMENTAL PRINCIPLES

1. **Analyze don't advocate** - Present situation as it is
2. **Quantify uncertainty** - Use probability bands and categorical confidence
3. **Enforce citations** - Every claim needs evidence
4. **Specificity required** - Technology names, not categories
5. **Value over volume** - Weight findings by strategic importance
6. **Never exclude critical** - Use failsafe with gap markers
7. **Conference vectors matter** - Track technology exposure venues
8. **Arctic = automatic priority** - All Arctic tech is dual-use

---

## 📊 ARTIFACT CONTRACTS

### Core Phase Artifacts (0-13)
```yaml
phase00_setup.json          # Initialization and scoping
phase01_baseline.json       # Historical context
phase02_indicators.json     # Key metrics and trends
phase03_landscape.json      # Technology and organizational map
phase04_supply_chain.json   # Dependencies and vulnerabilities
phase05_institutions.json   # Academic and research landscape
phase06_funders.json        # Funding sources and flows
phase07_links.json          # International partnerships
phase08_risk.json           # Risk assessment matrix
phase09_posture.json        # PRC/MCF strategic posture
phase10_redteam.json        # Red team and assumptions
phase11_foresight.json      # Scenarios and early warning
phase12_extended.json       # Country-specific deep dives
phase13_closeout.json       # Final synthesis and actions
```

### Conference Intelligence Artifacts
```yaml
conferences/events_master.csv       # All relevant conferences 2020-2030
conferences/participants_map.csv    # Who attended what
conferences/china_presence.json     # PRC delegation analysis
conferences/risk_matrix.json        # Technology exposure assessment
conferences/events_updates.md       # Quarterly monitoring reports
```

### Validation Artifacts
```yaml
validation_report.json         # All findings with scores
bombshell_findings.json        # Score >20 findings
oversight_gaps.json            # Regulatory vulnerabilities
incomplete_findings.json       # Critical with gaps marked
fusion_log.md                  # ChatGPT-Claude merge record
phase_conflicts.json           # Reconciliation documentation
```

---

## 🚀 PHASE TEMPLATES WITH v4.4 UPDATES

### Universal Phase Header (ALL PHASES 0-13)
```markdown
## Phase Header v4.4
**Imports v4.4:** Narrative uses Probability Bands `[10,30) [30,60) [60,90]` with **30 in the upper band** and **categorical Confidence** (Low/Med/High). **Numeric confidence (0-20)** appears **only** in artifacts for **major/critical findings** (Low=0-7, Med=8-14, High=15-20). On CC merge: zero-trust, corroborate critical claims, and on conflict explain, choose conservative, **downgrade Confidence**, and emit `fusion_log.md` + `phase_conflicts.json`. **Failsafe on:** never drop critical findings—include with **gap markers** and caveats.
```

### Phase 0: Setup & Scoping
```yaml
initialize:
  - Create country directory structure
  - Initialize conference tracking baseline
  - Identify domain-relevant events 2020-2024
  - Set up forward monitoring 2025-2030
  - Check Arctic relevance

conference_tickets:
  - P1: Compile events_master.csv (2020-2025 history)
  - P1: Create participants_map.csv template
  - P2: Initialize quarterly monitoring system
```

### Phase 1: Context & Baseline
```yaml
historical_analysis:
  - Document pre-2019 technology landscape
  - Identify existing China partnerships
  - Map conference participation history
  - Baseline metrics for comparison

conference_integration:
  - Historical conference attendance patterns
  - Technology disclosure timeline
  - Partnership formation venues
```

### Phase 2: Indicators & Metrics
```yaml
metrics_enhanced:
  - Conference participation rate (Tier-1 attendance / researchers)
  - China co-attendance frequency
  - Technology disclosure index
  - Arctic involvement score (if applicable)

trend_analysis:
  - YoY conference delegation growth
  - Topic evolution at conferences
  - Partnership velocity post-conference
```

### Phase 3: Technology Landscape
```yaml
organization_profiles:
  standard_fields:
    - Technology specifics (models, TRL, specifications)
    - China overlap assessment
    - Strategic value to China
  new_field:
    - Conference_Exposure: "List Tier-1/2 events, China co-presence"
    - Arctic_Relevance: "If applicable"
```

### Phase 4: Supply Chain Analysis
```yaml
component_analysis:
  - Exact specifications required
  - China control percentage
  - Alternative assessment
  - Conference disclosure risk
```

### Phase 5: Institutions
```yaml
academic_landscape:
  partnerships:
    - Conference-initiated collaborations
    - MOU signing venues
    - Side meeting outcomes
  arctic_research:
    - Polar programs (if applicable)
    - Arctic conference participation
```

### Phase 6: Funding & Investment
```yaml
funding_analysis:
  - Conference sponsorship patterns
  - Investment announcements at events
  - Technology demonstration funding
```

### Phase 7: International Links
```yaml
partnership_tracking:
  - Conference-initiated ties
  - Bilateral meetings at events
  - Arctic cooperation (if applicable)
  - Standards body participation
```

### Phase 8: Risk Assessment
```yaml
risk_inputs:
  - exposure_risk: Conference technology disclosure
  - prc_presence_flag: China delegation confirmed
  - tech_transfer_vector: Conference-enabled pathways
  - arctic_vulnerability: If applicable

validation_required:
  - Bombshell scoring (1-30)
  - Confidence scoring (0-20 for critical only)
  - Alternative hypotheses (5 minimum)
```

### Phase 9: Strategic Posture (PRC/MCF)
```yaml
posture_assessment:
  - Standards influence via conferences
  - Working group leadership
  - Technology disclosure strategy
  - Arctic ambitions (if relevant)
```

### Phase 10: Red Team & Validation
```yaml
assumption_testing:
  - Conference intelligence reliability
  - Technology transfer assumptions
  - Arctic threat assessment
  - Alternative explanations
```

### Phase 11: Foresight & Early Warning
```yaml
scenarios:
  - Conference-enabled tech transfer
  - Arctic technology competition
  - Standards capture via events

early_warning_indicators:
  - Delegation composition changes
  - New conference series emergence
  - Arctic activity increases
```

### Phase 12: Extended Analysis
```yaml
country_specific:
  - Deep dive on critical conferences
  - Unique Arctic considerations
  - Special technology domains
```

### Phase 13: Closeout & Actions
```yaml
final_synthesis:
  - Conference monitoring priorities
  - Arctic watch requirements
  - Validation summary
  - Implementation roadmap
```

---

## 📈 QUALITY GATES v4.4

### Value-Weighted Coverage
```python
def calculate_quality_metrics(findings):
    weights = {
        "CRITICAL": 10,
        "HIGH": 5,
        "MEDIUM": 2,
        "LOW": 0.5
    }

    total_value = sum(weights[f.importance] for f in findings)
    captured_value = sum(weights[f.importance] for f in findings if f.included)

    return {
        "value_capture_rate": captured_value / total_value,  # Target: 90%
        "critical_inclusion": "100% (with gaps marked)",
        "high_inclusion": "95% minimum"
    }
```

### Validation Requirements
- Every finding: Technology specificity check
- Critical findings: Bombshell scoring
- All claims: Alternative hypotheses tested
- Conference exposure: Documented
- Arctic relevance: Assessed

---

## 🌐 CONFERENCE INTELLIGENCE INTEGRATION

### Tier Classification
```yaml
tier_1_critical:
  - Arctic + China: "Automatic"
  - China triangle: "3+ countries with China + Target + US/ally"
  - Regional flagship: "8+ countries with China presence"
  - Specialized risk: "5+ countries, >20% China"

tier_2_high:
  - Arctic without China confirmed
  - International scale: "8+ countries"
  - Bilateral significant: "Key technology focus"

tier_3_medium:
  - Smaller scale: "3+ countries"
  - Academic/technical: "Limited scope"
```

### Collection Requirements
```yaml
historical_baseline:
  timeframe: "2020-2024 complete"
  deliverables:
    - events_master.csv
    - participants_map.csv
    - china_presence.json

current_monitoring:
  timeframe: "2025 active"
  frequency: "Quarterly updates"
  focus: "Registration, delegations, programs"

forward_calendar:
  timeframe: "2026-2027 confirmed"
  planning: "2028-2030 projected"
  verification: "6-month advance confirmation"
```

---

## ❄️ ARCTIC OVERRIDE RULES

### Automatic Prioritization
```yaml
arctic_conferences:
  tier_1_always:
    - Arctic Circle Assembly
    - Arctic Frontiers
    - IceTech Symposium
    - Arctic Technology Conference

  classification:
    with_china: "TIER_1_CRITICAL"
    without_china: "TIER_2_HIGH"

  technology:
    all_dual_use: true
    priority_domains:
      - Ice operations
      - Underwater systems
      - Satellite/communications
      - Extreme materials
```

---

## 🔄 CHATGPT-CLAUDE FUSION PROTOCOL

### Zero-Trust Merge
```python
def merge_with_claude(chatgpt_data, claude_data):
    """
    v4.4 Fusion Protocol
    """
    fusion_log = []
    conflicts = []

    for claim in all_claims:
        if claim.critical:
            # Verify across both sources
            if conflict:
                explanation = analyze_conflict()
                chosen = conservative_choice()
                confidence = downgrade_confidence()
                conflicts.append(conflict_record)

        # Include critical even if incomplete
        if claim.strategic_value == "CRITICAL":
            include_with_markers(claim)

    emit("fusion_log.md")
    emit("phase_conflicts.json")
    return merged_data
```

---

## ⏰ TEMPORAL AWARENESS REQUIREMENTS

### Current Date Check
```markdown
⏰ CRITICAL: Always verify current date
- If September 2025: Cannot monitor June 2025 Paris Air Show (past)
- Minimum 8-12 month implementation delay for new initiatives
- Budget impacts begin FY2027 at earliest (FY2026 already set)
- Major programs need 18-24 month minimum
```

---

## ✅ IMPLEMENTATION CHECKLIST

### For Every Phase:
- [ ] v4.4 header present at top
- [ ] Probability bands used correctly (30 in upper)
- [ ] Confidence categorical in narrative
- [ ] Numeric 0-20 only in artifacts for critical
- [ ] Conference exposure documented
- [ ] Arctic relevance assessed
- [ ] Failsafe applied to critical findings
- [ ] Gap markers used transparently

### Quality Metrics:
- [ ] Value capture rate ≥90%
- [ ] Critical findings 100% included
- [ ] Alternative hypotheses ≥5 per major claim
- [ ] Conference calendar maintained
- [ ] Temporal awareness verified

---

## 🎯 REMEMBER

**Quality over quantity.**
**Specificity over generality.**
**Evidence over speculation.**
**Value over volume.**
**But NEVER exclude critical intelligence for lack of perfect data.**

**The goal:** Actionable intelligence on how China exploits our 44 countries to access US technology.

**The method:** Systematic collection with rigorous validation.

**The standard:** Leonardo-level specificity or better.

---

*Version 4.4 - Full integration with conference intelligence, Arctic priorities, and validation frameworks*
