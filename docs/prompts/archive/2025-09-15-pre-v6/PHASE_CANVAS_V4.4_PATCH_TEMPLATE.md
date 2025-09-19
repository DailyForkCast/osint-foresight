# Phase Canvas v4.4 Patch Template
## How to Update ALL Phase Canvases (0-13)

**Purpose:** Standard template for patching all phase canvases with v4.4 requirements
**Application:** Apply to all country phase files (Italy, Slovakia, etc.)

---

## 📋 UNIVERSAL HEADER (ADD TO TOP OF EVERY PHASE)

```markdown
## Phase Header v4.4
**Imports v4.4:** Narrative uses Probability Bands `[10,30) [30,60) [60,90]` with **30 in the upper band** and **categorical Confidence** (Low/Med/High). **Numeric confidence (0-20)** appears **only** in artifacts for **major/critical findings** (Low=0-7, Med=8-14, High=15-20). On CC merge: zero-trust, corroborate critical claims, and on conflict explain, choose conservative, **downgrade Confidence**, and emit `fusion_log.md` + `phase_conflicts.json`. **Failsafe on:** never drop critical findings—include with **gap markers** and caveats.

**Temporal Awareness:** Current date September 2025. Cannot recommend past actions. Minimum 8-12 month implementation delay.
```

---

## 📁 PHASE-SPECIFIC PATCHES

### PHASE 0: Setup & Scoping

**Add to Initialization Section:**
```markdown
### Conference Intelligence Setup
- [ ] Initialize conference baseline (2020-2024 complete)
- [ ] Identify domain-relevant conferences for {{COUNTRY}}
- [ ] Map historical attendance patterns
- [ ] Set up forward monitoring (2026-2030)
- [ ] Check Arctic conference relevance

### Tickets (Add to existing):
- P1: `conferences/events_master.csv` - Compile 2020-2025 history
- P1: `conferences/participants_map.csv` - China delegation analysis
- P2: `conferences/events_updates.md` - Quarterly monitoring
```

### PHASE 1: Context & Baseline

**Add to Historical Analysis:**
```markdown
### Conference Participation History
- Document {{COUNTRY}} presence at major conferences 2020-2024
- Identify China co-attendance patterns
- Track technology demonstrations
- Note partnership formations at events

### Metrics Addition:
- Conference participation rate (baseline)
- China overlap frequency
- Technology disclosure index
```

### PHASE 2: Indicators & Metrics

**Add to Metrics Section:**
```markdown
### Conference Intelligence Indicators
- **Participation Rate:** Tier-1 conferences attended / total relevant
- **China Co-presence:** Frequency of China delegation overlap
- **Technology Disclosure:** Papers/demos at international venues
- **Arctic Involvement:** If applicable (auto-priority if yes)

### Trend Analysis:
- YoY conference delegation size
- Topic evolution at major events
- Partnership velocity post-conference
```

### PHASE 3: Technology Landscape

**Add to Each Organization/Technology Profile:**
```markdown
### Organization Profile Enhancement
**Conference Exposure:**
- Tier-1 Events: [List with years]
- China Co-presence: [Yes/No, which events]
- Technology Disclosed: [What was shown/presented]
- Arctic Relevance: [If applicable]

### Example:
```json
{
  "org_name": "Leonardo S.p.A.",
  "conference_exposure": {
    "tier_1_events": [
      "Paris Air Show 2023 (China: Large delegation)",
      "Farnborough 2024 (China: Limited)",
      "HAI HELI-EXPO 2025 (China: Indirect)"
    ],
    "technology_disclosed": "AW139 helicopter demonstrations",
    "partnership_risk": "HIGH - Same venue as Chinese manufacturers"
  }
}
```
```

### PHASE 4: Supply Chain

**Add to Component Analysis:**
```markdown
### Supply Chain Conference Exposure
For each critical component:
- **Disclosed at conferences:** [Which events, what details]
- **China awareness:** [Confirmed presence when disclosed]
- **Alternative suppliers:** [Met at which conferences]
```

### PHASE 5: Institutions

**Add to Partnership Tracking:**
```markdown
### Conference-Initiated Collaborations
- **First Contact Venue:** [Conference where partnership began]
- **MOU Signing Location:** [Often at major conferences]
- **Joint Papers:** [Conference proceedings]
- **Arctic Research:** [If polar conferences attended]

### Example:
```yaml
partnership:
  entities: "University X + Chinese Academy Y"
  initiated: "IAC 2023 side meeting"
  formalized: "MOU at Singapore Airshow 2024"
  risk: "CRITICAL - Space technology focus"
```
```

### PHASE 6: Funding & Investment

**Add to Funding Analysis:**
```markdown
### Conference-Related Funding
- **Sponsorship Patterns:** [Who sponsors what]
- **Investment Announcements:** [Made at conferences]
- **Demo Funding:** [Technology demonstrations]
```

### PHASE 7: International Links

**Add to Relationship Mapping:**
```markdown
### Conference Relationship Vectors
- **Bilateral Meetings:** [At which conferences]
- **Working Groups:** [Standards bodies at events]
- **Arctic Cooperation:** [If relevant]
- **Side Events:** [Closed-door sessions]
```

### PHASE 8: Risk Assessment

**Add to Risk Inputs:**
```markdown
### Conference Risk Factors
- **exposure_risk:** Technology shown at open conferences
- **prc_presence_flag:** Confirmed China delegation
- **tech_transfer_vector:** Conference-enabled pathway
- **arctic_vulnerability:** If Arctic conferences involved

### Risk Scoring Enhancement:
```python
if conference_exposure == "TIER_1" and china_present:
    risk_score *= 1.5  # Increase risk

if arctic_conference and china_present:
    risk_classification = "CRITICAL"  # Automatic
```
```

### PHASE 9: Strategic Posture (PRC/MCF)

**Add to Assessment:**
```markdown
### Conference Influence Strategy
- **Standards Leadership:** [Working groups chaired]
- **Technology Disclosure:** [What China shows vs. hides]
- **Partnership Formation:** [Strategic meetings]
- **Arctic Ambitions:** [Polar conference presence]
```

### PHASE 10: Red Team

**Add to Assumption Testing:**
```markdown
### Conference Intelligence Validation
- Test: "Conference attendance = technology interest"
- Test: "Side meetings = partnership formation"
- Test: "Arctic presence = military interest"
- Alternative: [Other explanations for patterns]
```

### PHASE 11: Foresight

**Add to Scenarios:**
```markdown
### Conference-Enabled Futures
- **2026 Scenario:** Major tech transfer at Farnborough
- **2027 Scenario:** Arctic conference partnership surge
- **2030 Scenario:** Standards capture via conference leadership

### Early Warning Indicators:
- Delegation size changes
- New conference series
- Arctic event frequency
```

### PHASE 12: Extended Analysis

**Country-Specific Deep Dives:**
```markdown
### {{COUNTRY}} Conference Profile
- Unique conference series
- Special Arctic considerations
- Domain-specific events
- Regional gatherings
```

### PHASE 13: Closeout

**Add to Final Synthesis:**
```markdown
### Conference Monitoring Priorities
- **Q4 2025:** [Remaining events]
- **2026 Priority:** [Top 5 conferences]
- **Arctic Watch:** [If applicable]
- **Collection Gaps:** [What we missed]
```

---

## 📦 ARTIFACT UPDATES (ALL PHASES)

**Add to Artifact Lists:**
```yaml
conference_artifacts:
  required:
    - conferences/events_master.csv
    - conferences/participants_map.csv

  conditional:
    - conferences/china_presence.json  # If China involved
    - conferences/risk_matrix.json     # Phase 8+
    - arctic/arctic_assessment.json    # If Arctic relevant

  fusion:
    - fusion_log.md                    # When merging ChatGPT
    - phase_conflicts.json              # Document conflicts
```

---

## ✅ VALIDATION RULES (ALL PHASES)

**Add to Quality Checks:**
```markdown
### v4.4 Validation Requirements
- [ ] Narrative uses ONLY categorical confidence
- [ ] Probability bands with 30 in upper [30,60)
- [ ] Numeric 0-20 ONLY in JSON for critical findings
- [ ] Conference exposure documented
- [ ] Arctic relevance checked
- [ ] Temporal awareness verified (no past recommendations)
- [ ] Value weighting applied (Critical=10, Low=0.5)
```

---

## 🚨 CRITICAL REMINDERS

### For EVERY Phase Canvas:

1. **Header First:** Add v4.4 header before any content
2. **Conference Fields:** Add to all organization profiles
3. **Arctic Check:** Assess relevance in each phase
4. **Temporal Check:** Verify all dates ≥ current date
5. **Fusion Ready:** Include conflict resolution process
6. **Failsafe Active:** Never drop critical findings

### Common Errors to Avoid:
- ❌ Numeric confidence in narrative text
- ❌ Probability band 30 in lower band
- ❌ Missing conference exposure
- ❌ Ignoring Arctic relevance
- ❌ Recommendations for past events
- ❌ Dropping critical findings for poor evidence

---

## 🔄 INTEGRATION SEQUENCE

1. **Add universal header** to top of phase file
2. **Insert conference sections** per phase template
3. **Update artifact lists** with conference files
4. **Add validation rules** to quality section
5. **Verify temporal awareness** throughout
6. **Test Arctic override** if applicable

---

## EXAMPLE: PATCHED PHASE 3 OPENING

```markdown
# Italy - Phase 3: Technology Landscape

## Phase Header v4.4
**Imports v4.4:** Narrative uses Probability Bands `[10,30) [30,60) [60,90]` with **30 in the upper band** and **categorical Confidence** (Low/Med/High). **Numeric confidence (0-20)** appears **only** in artifacts for **major/critical findings** (Low=0-7, Med=8-14, High=15-20). On CC merge: zero-trust, corroborate critical claims, and on conflict explain, choose conservative, **downgrade Confidence**, and emit `fusion_log.md` + `phase_conflicts.json`. **Failsafe on:** never drop critical findings—include with **gap markers** and caveats.

**Temporal Awareness:** Current date September 2025. Cannot recommend past actions.

## Technology Landscape Assessment

### Leonardo S.p.A.
**Domain:** Aerospace & Defense
**Technology:** AW139 helicopter platform (SPECIFIC)
**TRL:** 9 (Mature, operational)
**Strategic Value to China:** HIGH (5-year leapfrog)

**Conference Exposure:**
- Paris Air Show 2023: Full platform display (China: 200+ delegation)
- Farnborough 2024: Limited presence (China: Restricted)
- Singapore Airshow 2024: Major presence (China: MASSIVE)
- HAI HELI-EXPO 2025: US focus (China: Indirect monitoring)

**Arctic Relevance:** Helicopters used in Norwegian Arctic ops

[Continue with standard phase content...]
```

---

*This template ensures all phase canvases meet v4.4 requirements*
