
# Claude Code Master Prompt — v1.1 (Patched)
**Updated:** 2025-09-12 01:00:27  
**Purpose:** Execute the data-heavy lifting that feeds the ChatGPT Master Prompt v3.1 (MCF-enabled). Produce validated JSON/CSV artifacts with strict schemas, enforced evidence rules, and alignment to the analysis phases.

---

## RUN CONTEXT (sync with ChatGPT)
```
COUNTRY = {{country_name}}
TIMEFRAME = {{2015–present}}
HORIZONS = {{2y,5y,10y}}
LANG = {{EN + local + zh-CN}}            # Query/crawl in English, local language(s), and Chinese
POLICY_WINDOW = {{2019–2025 inclusive}}  # Filter policy/strategy docs to this window
ARTIFACT_DIR = {{./artifacts/{COUNTRY}}} # Base output directory (one folder per country)
TOGGLES = {{
  INCLUDE_MCF: true,
  INCLUDE_EXPORT_CONTROLS: true,
  INCLUDE_FINANCE_VECTORS: true,
  INCLUDE_SUPPLY_CHAIN: true,
  INCLUDE_ADVERSARY_SIM: true
}}
```

### Shared Scales (contract)
- **Probability bands:** "10-30%", "30-60%", "60-90%"
- **Confidence:** "Low" | "Med" | "High"
- **DataQuality (1–5):** 1=rumor; 2=single weak source; 3=mixed/secondary; 4=multi independent; 5=primary/official or multi-source convergence

### Evidence Table Schema (mandatory)
CSV: `{ARTIFACT_DIR}/evidence_master.csv`
```
ClaimID,Claim,SourceURL,PubDate,Lang,Corroboration,Contradiction,Probability,Confidence,DataQuality
```
Rules:
- **Moderate+ claims require ≥2 independent URLs** ⇒ Corroboration="Y". Else "N".
- Prefer primary/official docs; include language code; PubDate in YYYY-MM-DD.
- If sources conflict, set Contradiction="Y" and record both claims.

### Artifact Contracts (all paths relative to ARTIFACT_DIR)
- **Phase 1 (Baseline):** `phase1_baseline.json` → actors[], funders[], policies[], infrastructure[]. Policies filtered to **2019–2025**.
- **Phase 2 (Links):** `phase2_links.json` → links[], intl_partners[], standards_activity[].
- **Phase 2.5 (MCF):** `phase2_5_mcf.json` → mcf_summary, actors[], mechanisms[], indicators[], predictions[], gaps[].
- **Standards:** `standards_activity.json` (ISO/IEC/IEEE/ETSI/3GPP/ITU parsed roles & WGs).
- **Procurement signals:** `procurement_signals.csv` (specialized equipment/reagents, proxies).
- **Supply chain:** `supply_chain_map.json` (entities, parts/tools, jurisdictions).
- **Phase 3 (Risks):** `phase3_risks.json`.
- **Phase 4 (Vectors/Controls):** `phase4_vectors.json` (+ `funding_controls_map.json` for NSPM-33/EU hooks).
- **Phase 5 (Scenarios):** `phase5_scenarios.json`.
- **Phase 6 (EWS):** `phase6_ews.json`.
- **Phase 7C (Concepts):** `phase7c_concepts.json`.
- **Phase 7R (Recommendations):** `phase7r_recommendations.json`.
- **Phase 8 (Implementation):** `phase8_implementation.json`.
- **Adversary Sim:** `adversary_plan.json`.

---

## Source Adapters (examples; implement or stub explicitly)
- **Public research & grants:** OpenAIRE, CORDIS, national funding portals (date-filter with POLICY_WINDOW).
- **Publications:** Crossref, OpenAlex; co-authorship networks; DOI Event Data.
- **Patents:** WIPO Patentscope, EPO Espacenet, USPTO PatentsView (inventor mobility, families).
- **Standards:** ISO/IEC/IEEE/ETSI/3GPP/ITU (parse participants, roles, WGs).
- **Corporate/ownership:** OpenCorporates, GLEIF, Orbis-like if available; beneficial ownership scraping where legal.
- **Procurement/trade:** Public procurement portals, customs datasets where legal; build **signals** only.
- **University/lab:** Official directories, org charts, disclosures; dual appointments; talent programs.

*If a source requires a credential or is unavailable, generate a stub artifact and append a gap entry.*

---

## JSON Schemas (enforce with jsonschema or pydantic)

### Phase 1 — Baseline
```json
{{
  "type":"object",
  "properties":{{
    "actors":{{"type":"array","items":{{"type":"object","properties":{{"name":{{"type":"string"}},"type":{{"type":"string"}},"aka":{{"type":"array","items":{{"type":"string"}}},"notes":{{"type":"string"}}}}}}}},
    "funders":{{"type":"array"}},
    "policies":{{"type":"array","items":{{"type":"object","properties":{{"title":{{"type":"string"}},"year":{{"type":"integer"}},"summary":{{"type":"string"}},"link":{{"type":"string"}}}}}}}},
    "infrastructure":{{"type":"array"}}
  }},
  "required":["actors","policies"]
}}
```

### Phase 2.5 — MCF
```json
{{
  "type":"object",
  "properties":{{
    "mcf_summary":{{"type":"string"}},
    "actors":{{"type":"array","items":{{"type":"object","properties":{{"name":{{"type":"string"}},"aka":{{"type":"array","items":{{"type":"string"}}}},"role":{{"type":"string"}},"links":{{"type":"array","items":{{"type":"object","properties":{{"to":{{"type":"string"}},"type":{{"type":"string"}},"evidence_url":{{"type":"string"}}}}}}}}}}}}}},
    "mechanisms":{{"type":"array","items":{{"type":"object","properties":{{"type":{{"enum":["licit","gray","illicit"]}},"tech":{{"type":"string"}},"event":{{"type":"string"}},"date":{{"type":"string"}},"evidence_url":{{"type":"string"}},"confidence":{{"enum":["Low","Med","High"]}}}}}}}},
    "indicators":{{"type":"array","items":{{"type":"object","properties":{{"indicator":{{"type":"string"}},"threshold":{{"type":"string"}},"status":{{"enum":["rising","stable","declining"]}}}}}}}},
    "predictions":{{"type":"array","items":{{"type":"object","properties":{{"horizon":{{"enum":["2y","5y","10y"]}},"claim":{{"type":"string"}},"prob":{{"enum":["10-30%","30-60%","60-90%"]}},"confidence":{{"enum":["Low","Med","High"]}}}}}}}},
    "gaps":{{"type":"array","items":{{"type":"string"}}}}
  }},
  "required":["actors","mechanisms","indicators","predictions"]
}}
```

### Phase 3 — Risks
```json
{{
  "type":"object",
  "properties":{{
    "risks":{{"type":"array","items":{{"type":"object","properties":{{"name":{{"type":"string"}},"domain":{{"type":"string"}},"mechanism":{{"type":"string"}},"prob":{{"enum":["10-30%","30-60%","60-90%"]}},"impact":{{"enum":["Low","Med","High"]}},"horizon":{{"enum":["2y","5y","10y"]}},"indicators":{{"type":"array","items":{{"type":"string"}}},"uncertainty":{{"type":"string"}}}}}}}}
  }},
  "required":["risks"]
}}
```

*(Define similar schemas for scenarios, ews, recommendations, implementation, adversary_plan.)*

---

## Orchestration Outline
1. **Phase 1 — Baseline:** actors/funders/policies/infrastructure → `phase1_baseline.json` (filter policies by POLICY_WINDOW). Append evidence rows for each policy and key actor claim.
2. **Phase 2 — Links & Standards:** collaborations, MoUs, talent flows, standards roles → `phase2_links.json`; standards roles also saved to `standards_activity.json`. Append evidence.
3. **Phase 2.5 — MCF:** policies, actors (with AKA/中文名), mechanisms (licit/gray/illicit), indicators with thresholds, predictions (2y/5y/10y) → `phase2_5_mcf.json`. Append evidence; list gaps.
4. **Supply Chain & Procurement Signals:** build `supply_chain_map.json` and `procurement_signals.csv` (signals only, no controlled data). Append evidence for notable signals.
5. **Phase 3 — Risks:** compute top ≤6 risks/domain (mechanism one-sentence, prob/impact/horizon/indicators/uncertainty) → `phase3_risks.json`.
6. **Phase 4 — Vectors & Controls:** map talent/standards/vc/lp/grant/procurement/cloud/ip_license/brokers/shell_importers + `controls_hooks` (NSPM-33/EU) → `phase4_vectors.json` and `funding_controls_map.json`.
7. **Phase 5 — Scenarios:** ≤4 scenarios w/ indicators and timelines → `phase5_scenarios.json`.
8. **Phase 6 — EWS:** metrics, thresholds, cadence, owner, playbook → `phase6_ews.json`.
9. **Phase 7C — Concepts:** 1–3 activities → `phase7c_concepts.json`.
10. **Phase 7R — Recommendations:** action items with owner/when/cost/risk_addressed; open_questions; next_best_data → `phase7r_recommendations.json`.
11. **Phase 8 — Implementation:** milestones, metrics, execution risks → `phase8_implementation.json`.
12. **Adversary Simulation:** plan steps with counter_indicators & countermeasures → `adversary_plan.json`.
13. **Validation:** run schema checks on all JSON artifacts; validate Evidence Table completeness; enforce corroboration rule. Fail-fast with error report `validation_report.txt`.

---

## Key Functions (pseudocode)
```python
def fetch_policies(country, years): ...
def fetch_mcf_actors_with_aliases(): ...
def classify_acquisition_events(): ...  # tag licit|gray|illicit
def standards_activity(): ...
def trace_procurement_signals(): ...
def forecast_mcf_vectors(horizons): ...
def compile_evidence_table(): ...
def corroborate(urls:list)->str: return "Y" if len(set(urls))>=2 else "N"
def save_json_validated(path, obj, schema): ...
def validate_phase_outputs(): ...
```

### Performance & Robustness
- Guard centrality on disconnected graphs; set `max_iter` and component-wise fallbacks.
- Rate-limit and page external APIs; on failure, write stub artifacts and log to gaps with retrieval suggestions.
- Deduplicate entities by `name` + `aka` (Latin & Han) to avoid split nodes.

---

## Deliverables
- All artifacts listed under **Artifact Contracts** in `{ARTIFACT_DIR}`.
- `evidence_master.csv` with required columns.
- `validation_report.txt` summarizing schema & corroboration results.

> If gaps block a phase, write the partial artifact, add entries to `evidence_master.csv`, and list the gap in the corresponding JSON under `gaps`.
