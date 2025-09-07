Below is a single, copy‑paste **micro‑prompt** to run Phase 8 with a complete, evidence‑based narrative. It integrates structured data from earlier phases **and** new narrative research (policy/white papers, official statements, think tank work). It supports **2‑year / 5‑year / 10‑year** horizons and produces early‑warning tripwires.

---

# Run Phase 8 — Foresight & Early Warning (2y/5y/10y) for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 8 — Foresight & Early Warning (reports/country=<ISO2>/phase-8_foresight.md)"
- The canvas must contain **ONLY final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**; horizons **2y / 5y / 10y**; languages **["en","<local>","zh"]** where relevant; toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If sources are thin, still render a complete report with explicit unknowns, low‑confidence tags, and a punch‑list of boosts.

---

## What to produce (sections)
1) **Front‑matter** — title, author, date.
2) **Scenario Set (2y/5y/10y)** — axes, narratives, likelihood bands, key drivers.
3) **Threats & Opportunities by Sector** — structured threats with mechanisms, evidence, and confidence.
4) **Indicators & Early Warnings** — machine‑trackable signals with cadence and ownership.
5) **Mitigation & Levers** — feasible, solo‑doable options plus policy hooks (country/EU).
6) **Comprehensive Narrative** — explain the threats, justify with evidence, and show *how* conclusions were reached (data + narrative sources).
7) **3–5 Bullet Executive Summary** — decision‑useful close.
8) **Next Data Boost** — one pragmatic action.

---

## TSV outputs (return each as Markdown table + `# excel-tsv`)

### A) Scenarios.tsv (2y/5y/10y)
```
# excel-tsv
scenario_id	horizon	title	axis_1	axis_2	drivers	likelihood_LMH	payoff_note	assumptions_ids
```

### B) Threats.tsv (sectorized, evidence‑backed)
```
# excel-tsv
threat_id	sector	horizon	mechanism	vector_type	related_phases	severity_1to3	likelihood_LMH	confidence_LMH	evidence_ids	key_sources	why_it_matters	mitigation_refs
```
- **vector_type** ∈ {education_talent, joint_lab, JV_equity_control, minority_equity, standards_influence, IP_license, research_grant, procurement, supplier_relationship, shell_company, diaspora_network, VC_fund, conference_outreach, OSS_contributions, data_or_compute_access, testbed_access, logistics_route, recruiting_platform, other}
- **related_phases**: e.g., `P2,P2S,P5,P6,P7C`

### C) Indicators.tsv (signs the world is moving)
```
# excel-tsv
indicator_id	threat_id	observable	collection_method	threshold	check_cadence	owner	where_to_check
```

### D) EarlyWarnings.tsv (tripwires)
```
# excel-tsv
tripwire_id	indicator_id	description	trigger_condition	confidence_impact	action_on_trigger
```

### E) Mitigations.tsv (controls & policy levers)
```
# excel-tsv
mitigation_id	name	description	policy_hook	owner	cost_hours	skill_level_1to3	dependencies	applies_to_threat_ids	status
```

### F) Assumptions.tsv (traceability for scenario math)
```
# excel-tsv
assumption_id	statement	rationale	primary_data_refs	narrative_source_refs	confidence_prior_LMH	stress_test	result	confidence_posterior_LMH
```

### G) Confidence.tsv (why we believe what we say)
```
# excel-tsv
claim_id	claim_text	evidence_mix_data_vs_narrative	confounding_factors	bias_checks_done	confidence_LMH	falsification_path
```

### H) Timeline.tsv (major milestones)
```
# excel-tsv
year_or_quarter	milestone	sector	why_relevant	related_threat_ids
```

---

## Quality & sourcing (print as bullet list)
- **Integrate earlier phases:** pull in structured signals from `Phase 2/2S/3/4/5/6/7C` (relationships, standards roles, facilities, funding programmes, sanctions/legal signals (non‑US persons only), PRC posture). Reference evidence IDs.
- **Narrative research is required:** incorporate **policy/white‑papers/non‑papers/official statements/think‑tank reports** (PRC + country + EU where applicable). Record titles, issuers, dates, and **key quotes**; link sources.
- **Label‑independent MCF detection:** treat MCF‑consistent mechanisms even if not labeled; require **≥2 independent anchors** for strong claims.
- **US‑person exclusion:** in any sanctions/legal overlay, **exclude American citizens/persons entirely** from hits and narrative; all such hits are **signals, not proof**.
- **Recency bias with judgment:** weight the last **24–36 months**, but retain older doctrine if operative; mark status.
- **Confidence & falsification:** every major threat/claim has `confidence_LMH` and a **specific path to falsify**.

---

## Comprehensive Narrative (write this carefully)
Explain **potential threats** over **2y/5y/10y**, **justify with evidence**, and make transparent *how* you reached conclusions (data + narrative).

### 1) How we built the scenarios
- State the axes and drivers; cite which evidence from earlier phases and which policy texts influenced each axis.
- Note key **assumptions** (link to `Assumptions.tsv`) and any **contradictions** you resolved.

### 2) Sector‑by‑sector threat outlook
For each top sector (≤6):
- **Threats** (2–4 per sector) with mechanisms, horizon, severity/likelihood, and **why it matters** for dual‑use.
- **Evidence blend**: name the **data** (relationships/standards/funding/testbeds/supply chain) and the **narrative sources** (policy docs, white papers, think tanks) used.
- **Confounders**: what could explain the same observations benignly.
- **Confidence & falsification**: one observation that would raise/lower the threat call.

### 3) Cross‑cutting risks & compounding effects
- Interactions across sectors (e.g., compute/testbed access → accelerates AI + EO; logistics chokepoints → cross‑sector exposure).
- Where **standards influence** amplifies or mitigates risks.

### 4) Early‑warning architecture
- Explain the **best 5–10 indicators** and why they were chosen; show where/how to monitor; define thresholds and actions on trigger.

### 5) Mitigation playbook (realistic for a solo analyst + partners)
- Short list of **feasible levers** (policy hooks, controls, partnerships) with rough effort levels and dependencies.

### 6) Confidence, limits, and next steps
- Where evidence is thin or ambiguous; how bias was checked; what targeted data would most improve the forecast.

---

## Analyst research aids (inline)
- When writing the narrative, **explicitly cite**: `PolicyCorpus.tsv` rows (issuer/date/quote), `Signals.tsv` (date/actor), and `TopRelationships.tsv` from Phase 5, etc.
- If a claim rests mainly on narrative sources, mark `evidence_mix_data_vs_narrative` accordingly and propose a **data pull** to reduce reliance.

---

## Next Data Boost (close the report)
Suggest **one** high‑ROI action (e.g., “Add 6 policy docs to PolicyCorpus (PRC + <COUNTRY> + EU), then wire 5 tripwires into VS Code tasks for quarterly checks”).

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 8 report per the contract above.**

