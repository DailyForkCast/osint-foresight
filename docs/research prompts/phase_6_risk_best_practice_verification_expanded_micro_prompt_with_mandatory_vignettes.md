Below is a single, copy‑paste **micro‑prompt** to run Phase 6 with a comprehensive lay narrative and **mandatory concern vignettes**. It preserves structured TSV outputs (RiskRegister, ControlsLibrary, DecisionGates, FindingsRemediation) and adds tight legal/sanctions hygiene (signals‑only; exclude US persons).

---

# Run Phase 6 — Risk & Best‑practice Verification for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 6 — Risk & Best-practice (reports/country=<ISO2>/phase-6_risk.md)"
- The canvas must contain **ONLY final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>"]**, toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If sources are thin, still render a complete report with clear “No data yet — drop‑in CSV recipe below” notes.

---

## What to produce (sections)
1) **Front‑matter** — title, author, date.
2) **Tables** — RiskRegister, ControlsLibrary, DecisionGates, FindingsRemediation, **Vignettes (mandatory)**.
3) **Quality & screening notes** — evidence tiers, CER‑lite hygiene, ambiguity handling, recency, **sanctions/legal overlay (signals‑only; exclude US persons entirely)**, falsification discipline.
4) **Comprehensive Lay Narrative** — expanded analysis (template below) + **3–5 bullet executive summary** at the end.
5) **Next Data Boost** — one pragmatic, high‑ROI suggestion.

---

## TSV outputs (return each as Markdown table + `# excel-tsv`)

### A) RiskRegister.tsv (observed risks)
```
# excel-tsv
risk_id	risk_category	description	sector	mechanism	likelihood_LMH	impact_LMH	risk_score_1to9	evidence_ids	uncertainty_note	related_controls	sanctions_or_legal_signal	notes
```
- **risk_category** ∈ {IP_leakage, export_control, model_weights, standards_capture, supply_chain, data_protection, ethics, facility_ops, governance, other}
- **sanctions_or_legal_signal**: yes/no (signals‑only, non‑US persons)

### B) ControlsLibrary.tsv (C1–C10 library and mapping)
```
# excel-tsv
control_id	name	description	policy_hook	where_applies	evidence_needed	owner	cadence	status	link
```
- **policy_hook**: export classification, FDI screen, sanctions/BO/KYC, DPIA/data map, IRB/IBC, facility SOPs, model‑weight policy, pre‑publication, etc.

### C) DecisionGates.tsv (gates with criteria)
```
# excel-tsv
gate_id	name	criteria_pass	criteria_fail	required_controls	risk_threshold	owner	status	notes
```

### D) FindingsRemediation.tsv (issues → action)
```
# excel-tsv
finding_id	description	severity_1to3	recommended_action	owner	due_date	status	evidence_id
```

### E) Vignettes.tsv (concern mini‑cases — **mandatory**)
```
# excel-tsv
vignette_id	title	actor_set	mechanisms	year_range	sector	what_happened	why_it_matters	links	falsification_or_mitigation	related_risk_ids	related_control_ids
```

---

## Quality & screening (print as bullet list)
- **Evidence tiers:** prioritize primary/official; mark tier for others; cite URLs + access dates where possible.
- **CER‑lite hygiene:** normalize names + country; keep registry IDs; tag `(ambiguous)` rather than drop collisions.
- **Recency rule:** emphasize items in last **24–36 months**; include older if structurally relevant with note.
- **Sanctions/legal overlay (signals‑only):** soft‑flag matches to official EU/UK/CA/AU/NZ/UN lists or relevant legal cases; **do not include American citizens/persons** anywhere in hits or narrative; treat all hits as **signals, not proof**.
- **Falsification discipline:** for high‑impact risks, state what observation would overturn or materially lower the risk.

---

## Comprehensive Lay Narrative (write this)
Explain **what the top risks are, why they matter for dual‑use, which controls mitigate them, and how we’ll verify**.

### 1) Risk Landscape Overview (8–12 sentences)
- Summarize the dominant risk categories and where they arise (sectors, mechanisms).
- Name the **highest‑scoring risks** (score, mechanism, sector) and the evidence tiers supporting them.
- Note any **structural protections** (accreditation culture, model‑weight policies, export‑control competence) and obvious **gaps**.

### 2) Controls & Legal/Policy Hooks
- Map top risks → specific **controls** (C1–C10) → **policy hooks** (export classification, sanctions/KYC/BO, FDI screening, DPIA/data map, IRB/IBC, facility SOPs, model‑weight policy, pre‑publication).
- Provide **1–2 concrete examples** of how a control would be implemented in this ecosystem (owner, cadence, verification data).

### 3) Decision Gates (Go/No‑Go logic)
- Define key gates (e.g., *Proceed with partnership only if export classification X is cleared and model‑weight policy Y is in place*).
- Specify **pass/fail criteria** and **required controls** per gate.

### 4) Concern Vignettes (mandatory; 0–5 items)
- **Select the 1–5 most concerning items** by combining risk score, mechanism sensitivity, sanctions/legal signals (non‑US persons only), and strategic dependency.
- For each, write **~120 words**: who/what, mechanism(s), sector, why it’s concerning, evidence IDs/links, **related risk IDs**, **related control IDs**, and **what would falsify or mitigate** the concern.
- **If none are concerning**, state explicitly: “**No concerning risk vignettes identified** under current evidence and thresholds,” and explain briefly why (e.g., low intensity, benign mechanisms, strong safeguards).

### 5) Falsification & Monitoring
- For the **top 3 risks**, specify **one machine‑trackable tripwire** each and the check cadence (link to Phase 5 Tripwires if already present).

### 6) 3–5 Bullet Executive Summary
- Close with 3–5 bullets covering **top risks → matched controls → verification plan**, with current confidence.

---

## Next Data Boost (close the report)
Provide **one** pragmatic action (e.g., “Import the national sanctions/BO portal extracts (non‑US persons), re‑resolve partners → auto‑flag signals in RiskRegister; wire DecisionGates to those flags”).

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 6 report per the contract above.**