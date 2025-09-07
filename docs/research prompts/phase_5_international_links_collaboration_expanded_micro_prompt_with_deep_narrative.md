Below is a single, copy‑paste **micro‑prompt** to run Phase 5 with an expanded, evidence‑rich narrative. It preserves the structured TSV outputs (heat‑map + top relationships) and adds deep analysis on patterns, mechanisms, reciprocity/asymmetry, and risk/benefit framing.

---

# Run Phase 5 — International Links & Collaboration for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 5 — International Links (reports/country=<ISO2>/phase-5_links.md)"
- The canvas must contain **ONLY final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>"]**, toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If sources are thin, still render a complete report with clear “No data yet — drop‑in CSV recipe below” notes.

---

## What to produce (sections)
1) **Front‑matter** — title, author, date.
2) **Tables** — Heat‑Map (long form), Top Relationships, **PRC Entities (mandatory)**, **Vignettes (mandatory)**, Tripwires (optional).
3) **Quality & screening notes** — CER‑lite hygiene, ambiguity handling, recency; soft sanctions/legal cross‑screen (signals‑only; **exclude US persons entirely** from flags/narrative); double‑count guardrail; **mandatory PRC‑entities check**.
4) **Comprehensive Lay Narrative** — extended analysis (see template below) + a **3–5 bullet executive summary** at the end.
5) **Next Data Boost** — 1 pragmatic, high‑ROI suggestion.

---

## TSV outputs (return each as Markdown table + `# excel-tsv`)

### A) HeatMap.tsv (partner × sector × mechanism, long form)
```
# excel-tsv
partner_country	partner_name	partner_type	sector	mechanism	intensity_0_3	risk_LMH	evidence_ids	notes
```
- **partner_type** ∈ {government, university, public_RTO, SOE, private_firm, startup_SME, standards_body, funder, consortium, other}
- **mechanism** ∈ {co_publication, co_project, standards_role, joint_lab, MOU, JV_equity, IP_license, staff_exchange, data_access, compute_access, testbed_access, procurement, funding_cosponsor, other}
- **intensity_0_3**: 0 none/unknown, 1 light, 2 notable, 3 strong (show rule of thumb in notes).
- **risk_LMH**: judgment using source tier + sensitivity of mechanism; keep rationale brief in `notes`.

### B) TopRelationships.tsv (ranked)
```
# excel-tsv
rank	partner_name	partner_country	partner_type	sectors	primary_mechanism	start_year	most_recent_year	why_it_matters	key_sources
```

### C) PRCEntities.tsv (structured subset — **mandatory**)
```
# excel-tsv
entity_name	en_name_zh	entity_type	parent_group	country	mechanism	years_active	sector	registry_id	why_relevant	key_sources
```

### D) Vignettes.tsv (mini case studies — **mandatory**)
```
# excel-tsv
vignette_id	title	actor_set	mechanisms	year_range	sector	what_happened	why_it_matters	links	falsification_or_mitigation
```

### E) Tripwires.tsv (forward-looking monitors — optional) (Optional) Tripwires.tsv (forward-looking monitors)
```
# excel-tsv
tripwire_id	description	sector	partner_name	mechanism	trigger_condition	check_cadence	suggested_data_source
```

---

## Quality & screening (print as bullet list)
- **CER‑lite hygiene:** normalize `partner_name` + `country` prior to ranking; if multiple candidates remain, tag `(ambiguous)` rather than drop.
- **Ambiguity handling:** where names collide, add local/alt names (incl. ZH) and keep registry IDs when available.
- **Recency rule:** highlight activity in the last **24–36 months**; keep older links if structurally important and mark as such.
- **Sanctions/legal cross‑screen (signals only):** soft‑flag if partner (non‑US persons only) appears on official EU/UK/CA/AU/NZ/UN lists or in relevant legal cases; **do not include American citizens/persons** in any hits or narrative.
- **Mandatory PRC‑entities check:** always populate `PRCEntities.tsv` if any PRC links exist; if none found, render the table header with a row `none_observed=true` and explain in narrative how you searched.
- **Double‑count guardrail:** if the same relationship appears via multiple mechanisms (e.g., co‑pub + co‑project + standards), consolidate for ranking but retain mechanism detail in HeatMap rows.

---

## Comprehensive Lay Narrative (write this)
Craft an extended narrative that explains **who collaborates with whom, through which mechanisms, at what intensity, with what benefits and risks**, and **why this matters for dual‑use and standards posture**. Use concise paragraphs and lists; embed links or evidence IDs.

### 1) Landscape Overview (8–12 sentences)
- Shape of international collaboration: principal **partner countries/regions** and **actor types** (universities, RTOs, SOEs, firms, funders, standards bodies).
- **Dominant sectors & mechanisms** (co‑pub vs co‑project vs standards co‑leadership vs joint labs/JV/equity, etc.).
- **Concentration**: if top‑1 partner or partner‑country accounts for >50% in a sector, state the skew and its implications.
- **Trendline**: how relationships evolved 2015→present (e.g., shift from co‑pub to standards roles; rise of JV/equity; new compute/testbed access).

### 2) Mechanisms Deep‑Dive (explain value & risk)
For the mechanisms that actually exist in this country (omit absent ones):
- **Co‑publications / Co‑projects** — knowledge exchange vs IP control; typical funding sources; examples.
- **Standards participation** — where co‑leadership occurs; implications for adoption and interoperability.
- **Joint labs / MOUs** — scope, staffing, facility access; governance safeguards or gaps.
- **JV / Equity stakes / Corporate alliances** — ownership structure, strategic control, technology direction.
- **IP Licensing / Data or Compute Access / Testbeds** — terms visibility; export‑control considerations; reproducibility.
- **Procurement & Funding Co‑sponsorship** — mission pull; compliance hooks.
Include **1–2 brief vignettes** where helpful (reference `Vignettes.tsv`).

### 3) Geography of Links & Asymmetry
- Regional patterns (EU vs non‑EU; Nordics/Baltics/CEE/Med; trans‑Atlantic vs intra‑EU).
- **Reciprocity vs Asymmetry**: assess whether access, control, and benefits appear one‑sided (e.g., domestic standards work feeding foreign deployments without domestic uptake).
- Note **structural chokepoints** (single‑supplier dependencies; compute/testbed reliance abroad).

### 4) Capability Lift vs Leakage (dual‑use lens)
- Where links lift capability (skills, standards leverage, facility sharing) vs where they pose leakage risks (MCF‑consistent patterns, sensitive subdomains, export‑controlled items).
- Keep **MCF detection label‑independent** (function‑over‑label); require ≥2 anchors for strong claims; otherwise mark uncertainty.

### 5) PRC‑Related Links (mandatory check)
- Summarize PRC‑related partnerships by **mechanism** and **sector** (use `PRCEntities.tsv`), neutrally.
- Add **sanctions/legal overlay** as **signals‑only** (non‑US persons; US persons excluded entirely). Explain **why it matters** in one or two lines per hit and how to corroborate.

### 6) Concern Vignettes (mandatory; 0–5 items)
- **Select the 1–5 most concerning relationships** based on a composite of: `risk_LMH`, mechanism sensitivity (e.g., JV/equity, compute/testbed access in sensitive sectors), presence of sanctions/legal signals (non‑US persons only), and concentration/strategic dependency.
- For each, write **~120 words** covering: who, mechanism(s), sector, why it’s concerning, evidence IDs/links, and **what would falsify or mitigate** the concern. Title each vignette clearly (e.g., `V-1: <Partner> × <Mechanism> in <Sector>`).
- **If none are concerning**, state explicitly: “**No concerning relationships identified** under current evidence and thresholds,” and briefly explain why (e.g., low intensity, benign mechanisms, strong safeguards).

### 7) Tripwires & Early Warnings (3–6 items)
- Derive **machine‑trackable tripwires** from relationships/heat‑map trends (e.g., new JV filings; standards co‑chair changes; sudden growth in compute/testbed access). Place them in `Tripwires.tsv`.

### 8) 3–5 Bullet Executive Summary
- Close with 3–5 crisp bullets capturing **where the country’s international posture helps/hurts** dual‑use outcomes, with any notable **PRC‑related** signals and **mitigations/next checks**.
- Close with 3–5 crisp bullets capturing **where the country’s international posture helps/hurts** dual‑use outcomes, with any notable **PRC‑related** signals and **mitigations/next checks**.

---

## Optional small tables used in narrative (include only if needed)
```
# excel-tsv
Asymmetry.tsv
dimension	indicator	observation	rationale	evidence_ids
```

---

## Next Data Boost (close the report)
Provide **one** pragmatic action (e.g., “Augment HeatMap via CORDIS co‑participation export 2015–2025 and re‑score intensity_0_3; then add standards co‑leadership rows from SDO rosters”).

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 5 report per the contract above.**

