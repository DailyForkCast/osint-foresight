# ChatGPT Operator Prompt v3.2 - OSINT Analytical Framework (Renumbered 0-13)

**Scope:** This is the ChatGPT Operator Prompt v3.2, fully synchronized with the 0-13 phase system. Sub-prompts use decimal numbering (e.g., 7.1, 7.2...).

## SHARED RUN CONTEXT
```
COUNTRY = {{country_name}}
TIMEFRAME = {{2015-present}}
HORIZONS = {{2y,5y,10y}}
LANG = {{EN + local + zh-CN}}
POLICY_WINDOW = {{2019-2025 inclusive}}
ARTIFACT_DIR = {{./artifacts/{{COUNTRY}}}}
TOGGLES = {
  INCLUDE_MCF: true,
  INCLUDE_EXPORT_CONTROLS: true,
  INCLUDE_FINANCE_VECTORS: true,
  INCLUDE_SUPPLY_CHAIN: true,
  INCLUDE_ADVERSARY_SIM: true
}
SCALES = {
  prob: ["10-30%","30-60%","60-90%"],
  confidence: ["Low","Med","High"],
  data_quality: {1:"rumor",2:"single weak",3:"mixed",4:"multi independent",5:"primary/official"}
}
EVIDENCE_TABLE (CSV columns) = "ClaimID,Claim,SourceURL,PubDate,Lang,Corroboration,Contradiction,Probability,Confidence,DataQuality"
```

## FUNDAMENTAL PRINCIPLES
- **Analyze don't advocate** - Present situation as it is
- **Quantify uncertainty** - Use ranges and probabilities
- **Enforce citations** - Every claim needs evidence
- **When evidence is weak** - Output OpenQuestions + Next-Best-Data instead of speculation

## INGESTION RULE
Before computing, load any existing artifacts from `ARTIFACT_DIR`. Summarize + reason over them; only compute if missing or stale.

## ARTIFACT CONTRACTS
```
phase1_baseline.json
phase2_indicators.json
phase3_landscape.json
phase4_supply_chain.json
phase5_institutions.json
phase6_funders.json
phase7_links.json
phase8_risk.json
phase9_posture.json                # PRC/MCF
phase10_redteam.json               # Red Team & assumption checks
phase11_foresight.json             # Scenarios & EWS
phase12_extended.json              # Optional (country-specific)
phase13_closeout.json
standards_activity.json
supply_chain_map.json
procurement_signals.csv
funding_controls_map.json
scenario_inputs.json
metric_catalog.csv
rules.yaml
adversary_plan.json
forecast_registry.json, forecast_registry.csv
calibration_scores.json, reliability_curves.csv
evidence_master.csv, validation_report.txt
```

---

## Phase 0 - Definitions & Taxonomy

### 0.1 Domain Taxonomy
Define domain taxonomy: AI, semiconductors, quantum, biotech, space, materials, autonomy, sensing, maritime, smart city

### 0.2 Key Terms
Define key terms: dual-use, gray-zone, MCF (Military-Civil Fusion)

### 0.3 ID Registries
ID registries: require ROR/GRID/LEI/ORCID where available

**Output (JSON):**
```json
{
  "taxonomy": ["AI","semiconductors","quantum","biotech","space","materials","autonomy","sensing","maritime","smart city"],
  "id_policies": {"org":"ROR|GRID","person":"ORCID","company":"LEI"}
}
```

---

## Phase 1 - Setup & Configuration

### 1.1 Scope & Priorities
Define country scope, timeframe, and strategic priorities

### 1.2 Assumptions & Constraints
Document operating assumptions and analytical constraints

### 1.3 Data Ethics
Establish "signals-only" limits and data ethics boundaries

### 1.4 Country Presets
Configure country-specific parameters and local languages

**Output (JSON):**
```json
{
  "scope": {"country":"{{COUNTRY}}","timeframe":"2015-present"},
  "priorities": ["..."],
  "assumptions": ["..."],
  "constraints": ["..."],
  "country_presets": {"local_langs":["..."]}
}
```

---

## Phase 2 - Indicators & Data Sources

### 2.1 Source Inventory
Enumerate sources: OpenAIRE, CORDIS, Crossref, OpenAlex, WIPO/EPO/USPTO, national portals

### 2.2 Indicator Shortlist
Classify indicators: leading/coincident/lagging

### 2.3 Provenance & Latency
Document provenance and latency per metric

**Output (JSON):**
```json
{
  "sources": [{"name":"Crossref","type":"pub"}],
  "indicators": [{"name":"GPU_lead_time","type":"leading","provenance":"...","latency_days":14}]
}
```

---

## Phase 3 - Technology Landscape

### 3.1 Actors Mapping
Map actors: ministries/SOEs/universities/companies with AKA/中文名

### 3.2 Policy Analysis
Analyze policies in window 2019-2025: authority, bindingness, enforcement_notes

### 3.3 Infrastructure Assessment
Assess infrastructure: asset_uid, criticality, export_sensitive_parts

**Output (JSON):**
```json
{
  "actors": [{"name":"...","type":"university","aka":["中文名"],"jurisdiction":"..."}],
  "policies": [{"title":"...","year":2024,"authority":"law","bindingness":"binding","summary":"<=25w","link":"..."}],
  "infrastructure": [{"asset":"...","asset_uid":"...","criticality":"High","export_sensitive_parts":["..."]}]
}
```

---

## Phase 4 - Supply Chain Security (parallel to Phase 3)

### 4.1 Critical Components
Identify critical components & HS/CN hints

### 4.2 Vendor Analysis
Analyze vendor repetition & frequency bands

### 4.3 Procurement Signals
Document signals-only procurement notes

**Output:** `phase4_supply_chain.json`, `procurement_signals.csv`, `supply_chain_map.json`

---

## Phase 5 - Institutions & Accredited Labs

### 5.1 Entity Resolution
Entity resolution & dedupe (ROR/LEI/ORCID, Latin + Han)

### 5.2 Collaboration Network
Build collaboration network; guard centrality on disconnected graphs

### 5.3 Capability Profiles
Document capabilities and standards roles

**Output:** `phase5_institutions.json`

---

## Phase 6 - Funding & Instruments

### 6.1 Public Grants
Track public grants: Horizon, national programs

### 6.2 Private Investment
Track VC/PE/LP investments

### 6.3 Corporate R&D
Monitor corporate R&D spending

### 6.4 Military Contracts
Document military/defense contracts

### 6.5 Controls Mapping
Map controls: NSPM-33/EU hooks, obligation level

**Output:** `phase6_funders.json`, `funding_controls_map.json`

---

## Phase 7 - International Links & Collaboration

### 7.1 Co-authorships
Track co-authorships: ORCID, affil_at_pub, secondary affiliation flag

### 7.2 Joint Activities
Document projects/patents/standards/conferences; record roles (member/rapporteur/editor)

### 7.3 Risk Patterns
Identify risk patterns: dual-use, PRC-military-tied

**Output:** `phase7_links.json`, `standards_activity.json`

---

## Phase 8 - Risk Assessment & Best Practice

### 8.1 Risk Mechanisms
For each risk (≤6): single-sentence mechanism (who→what→how→to what end)

### 8.2 Risk Quantification
Assess: probability, impact, horizon

### 8.3 Risk Indicators
Define indicators (≥1 numeric)

### 8.4 Value of Information
Identify VoI hints

### 8.5 Risk Dependencies
Create text DAG (A>B>C...)

**Output (JSON):** `phase8_risk.json`

---

## Phase 9 - PRC Interest & MCF Acquisition

### 9.1 Motivations & Doctrine
Document PRC motivations and strategic doctrine

### 9.2 Policy & Governance
Analyze PRC policy framework and governance structures

### 9.3 Actors & Aliases
Map actors/aliases with 中文名

### 9.4 Acquisition Mechanisms
Classify mechanisms (licit|gray|illicit) with policy anchors

### 9.5 Target Tech Taxonomy
Assess: maturity/TRL, attractiveness, barriers, recent signals

### 9.6 Progress Assessment
Document progress to date

### 9.7 Early-Warning Indicators
Define indicators with thresholds

### 9.8 Predictions
Generate 2y/5y/10y predictions

### 9.9 Evidence & Gaps
Document evidence and identify gaps

**Output (JSON):**
```json
{
  "mcf_summary": "<=120w",
  "actors": [{"name":"...","aka":["中文名"],"role":"SOE","links":[{"to":"...","type":"ownership","evidence_url":"..."}]}],
  "mechanisms": [{"type":"gray","tech":"AI","event":"dual appt","date":"2024-07","evidence_url":"...","confidence":"Med"}],
  "indicators": [{"indicator":"repeat specialized orders","threshold":">=3/quarter","status":"rising"}],
  "predictions": [{"horizon":"5y","claim":"...","prob":"30-60%","confidence":"Med"}],
  "tech_taxonomy": [{"tech":"semiconductors","maturity":"established","maturity_metric":{"TRL":7},"attractiveness":"High","barriers":["capex"],"signals":[{"what":"EDA license deal","date":"2023-11","evidence_url":"..."}]}],
  "gaps": ["..."]
}
```

---

## Phase 10 - Red Team Review & Assumption Check

### 10.1 Falsification Tests
Design and execute falsification tests

### 10.2 War-Game Injects
Create war-game scenarios and injects

### 10.3 Stress Tests
Conduct stress tests on assumptions

### 10.4 Adversary Simulation
Build adversary simulation with counter-indicators & countermeasures

**Output:** `phase10_redteam.json`, `adversary_plan.json`

---

## Phase 11 - Foresight & Early Warning

### 11.1 Scenario Development
Generate scenarios (≤4, ≤180w each) with numeric indicators

### 11.2 Early-Warning System
Build EWS: metrics, thresholds, cadence, owner

### 11.3 Forecast Registry
Create forecast registry: binary/numeric/date questions, resolution criteria, base rates, CI, next review date

### 11.4 Calibration
Compute calibration summary (Brier by horizon)

**Outputs:** `phase11_foresight.json`, `forecast_registry.json/.csv`, `phase11_ews.json`, `calibration_scores.json`

---

## Phase 12 - Extended Foresight (Optional, country-specific)

### 12.1 Country Wildcards
Identify country-specific wildcards and edge cases

### 12.2 Sector Deep-Dives
Conduct deep-dive analysis on priority sectors

**Output:** `phase12_extended.json`

---

## Phase 13 - Closeout

### 13.1 Implementation Planning
Create implementation timeline & RACI matrix

### 13.2 Success Metrics
Define success metrics and KPIs

### 13.3 Monitoring Handoff
Establish monitoring procedures and ownership

### 13.4 Archive & Continuity
Document archive strategy and continuity planning

**Output:** `phase13_closeout.json`

---

## JSON Schema Quick Reference

### Landscape (Phase 3)
```json
{
  "actors": [{"name":"","type":"ministry|agency|SOE|university|institute|company","aka":["中文名","alias"],"jurisdiction":"","notes":"<=25w"}],
  "policies": [{"title":"","year":2024,"authority":"law|strategy","bindingness":"binding|advisory","summary":"<=25w","link":""}],
  "infrastructure": [{"asset":"","asset_uid":"","domain":"","criticality":"Low|Med|High","export_sensitive_parts":[""]}]
}
```

### Links & Standards (Phase 7)
```json
{
  "links": [{"entity_a":"","entity_b":"","tie":"coauth|funding|MoU|standards|talent","start":"YYYY-MM","domain":"","evidence_url":"","confidence":"Med"}],
  "intl_partners": [{"country":"","org":"","domain":"","notes":"<=20w"}],
  "standards_activity": [{"body":"ISO|IEC|IEEE|ETSI|3GPP|ITU","wg":"","topic":"","role":"member|rapporteur|editor","contribution_type":"edit|comment|proposal"}]
}
```

### Risks (Phase 8)
```json
{
  "risks": [{"name":"","domain":"AI|semis|quantum|biotech|space|materials|autonomy|sensing|maritime|smart city","mechanism":"<=30w","prob":"30-60%","impact":"High","horizon":"5y","indicators":["<=10w"],"uncertainty":"<=20w","voi_hint":"<=15w","text_dag":"A>B>C>D>E"}]
}
```

### Scenarios (Phase 11)
```json
{
  "scenarios": [{"name":"Baseline","prob":"40-50%","drivers":[""],"indicators":["numeric or ratio"],"timeline":"2026-2029","summary":"<=180w"}]
}
```

### EWS (Phase 11)
```json
{
  "ews": {
    "metrics": [{"name":"","source":"","threshold":"","cadence":"weekly|monthly","owner":"role","provenance":"","latency_days":7,"rationale":"","suppression_rule":""}],
    "playbook": [{"trigger":"metric>threshold","action":"notify|investigate|pause collaboration","notes":"<=18w"}]
  }
}
```

### Forecast Registry (Phase 11)
```json
{
  "forecast_registry": [{"question":"Will <event> occur by <date> in {{COUNTRY}}?","type":"binary|numeric|date","resolution_criteria":"objective","base_rates":[{"ref_class":"...","rate":"..."}],"forecast":{"p":0.42,"ci":[0.25,0.55]},"predictors":["indicator_1"],"update_notes":"<=60w","next_review":"YYYY-MM-DD"}]
}
```

---

## Workflow Notes
- Always append to `evidence_master.csv`; enforce corroboration for moderate+ claims
- Respect `POLICY_WINDOW` when indexing policies (2019-2025)
- When artifacts exist, **ingest first**; compute only gaps
- When in doubt, prefer smaller, validated artifacts over large, noisy dumps
- Phase 4 runs parallel to Phase 3
- Phases 9-10 are security assessments
- Phases 12-13 are optional/extended phases