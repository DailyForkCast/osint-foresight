Below is a single, copy‑paste **micro‑prompt** to run Phase 3 with a fully expanded lay summary. It keeps the structured TSV outputs and adds a comprehensive, category‑wise narrative that covers the full actor landscape (government, academia, RTOs, SOEs, finance, industry, consortia, etc.).

---

# Run Phase 3 — Institutions & Accredited Labs for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 3 — Institutions & Accredited Labs (reports/country=<ISO2>/phase-3_institutions.md)"
- The canvas must contain **ONLY final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>"]**, and toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If sources are thin, still render a complete report with clear “No data yet — drop‑in CSV recipe below” notes.

---

## What to produce (sections)
1) **Front‑matter** — title, author, date.
2) **Roster tables** — master roster + accredited labs.
3) **Quality & screening notes** — CER‑lite hygiene, ambiguity handling, recency, accreditation validity, optional sanctions/legal screen note (no US persons; signals‑only).
4) **Comprehensive Lay Summary** — structured narrative (see template below), category‑wise coverage.
5) **Next Data Boost** — 1 actionable, high‑ROI suggestion.

---

## TSV outputs (return as Markdown table + `# excel-tsv`)

### A) Roster.tsv (master actor roster)
```
# excel-tsv
id	org_name	alt_name_local	alt_name_zh	lei_or_national_id	org_type	actor_category	city_region	sectors	capability_notes	facility_name	metric_1	metric_2	funders_partners	standards_roles	prc_links_note	beneficial_owner_summary	ci_stem_y_n	risk_note	evidence_id	url
```
- **org_type** (free text) vs **actor_category** (controlled list below).
- **actor_category** ∈ {government_ministry, regulator, funding_agency, university, research_university, public_RTO, private_RTO, SOE, defense_affiliate, private_firm, startup_SME, consortium_cluster, standards_body_local, accreditation_body, foundation_NGO, financial_institution, incubator_accelerator, think_tank, other}.
- **metric_1/metric_2**: context‑appropriate (e.g., HPC peak/sustained; publication or project counts; accreditation totals).
- **ci_stem_y_n**: Confucius Institute STEM presence y/n (if applicable).
- **prc_links_note**: brief, neutral; cite evidence id.
- **beneficial_owner_summary**: concise BO/ownership highlights.

### B) AccreditedLabs.tsv (shortlist)
```
# excel-tsv
organisation	iso_standard	accreditation_id	scope_short	sector_tags	city_region	status_note	last_check	links
```
- Include ISO/IEC 17025/17020 etc. If accreditation registry is unavailable, render table header with a note on how to drop in CSV later.

---

## Quality & screening (print as bullet list)
- **CER‑lite hygiene:** normalize `org_name` + `country` before ranking. If multiple candidates remain, tag `(ambiguous)` rather than drop; keep URLs.
- **Ambiguity handling:** where names collide, add `alt_name_local` and `alt_name_zh` when available; retain registry IDs (LEI or national) in the row.
- **Recency rule:** prefer entries with activity/updates in the last **24–36 months**; if older, include but flag `status_note`.
- **Accreditation validity:** add `last_check` and any expiration/validity notes from the registry.
- **Optional sanctions/legal screen (signals only):** soft‑flag if an entity name (non‑US persons only) appears on official EU/UK/CA/AU/NZ/UN lists or in relevant legal cases; these are **signals, not proof**. Do **not** include American citizens/persons; exclude them entirely from flags and narrative.

---

## Comprehensive Lay Summary (write this narrative)
Write a **structured, category‑wise** narrative that answers not just “who the players are,” but also **what they do, why they matter for dual‑use, and how they interconnect**. Use concise paragraphs and lists.

### 1) Landscape Overview (8–12 sentences)
- Summarize the **size and shape** of the ecosystem (counts of universities/RTOs/labs/firms/government bodies; note concentration: if `top1_share > 0.5` in any key sector, call it out).
- Identify **anchor institutions or facilities** (e.g., national HPC, flagship labs/testbeds) and their dual‑use relevance.
- Mention any **governance features** (e.g., strong accreditation culture; BO transparency; standards participation).

### 2) Category‑wise Profiles (write short, factual blurbs with links)
For each category that exists in the country, include a sub‑section; omit categories with no presence (or state “none observed”):
- **Government & Regulators** — key ministries/agencies; mandates in R&I, export control, accreditation, standards; how they convene/coordinate.
- **Funding Agencies** — principal R&D funders (national/EU); typical instruments (grant/procurement/prize); any dual‑use or defense‑adjacent programs.
- **Universities & Research Universities** — top labs/departments; notable strengths; flagship facilities; international links that matter for dual‑use.
- **Public RTOs & SOEs/Defense affiliates** — missions, core capabilities, relevant programmes; note **defense‑adjacent** work where evident (neutral tone).
- **Private Firms & Startups/SMEs** — leading companies in dual‑use subdomains; supplier roles; integration into EU/global chains.
- **Standards & Accreditation Bodies** — local standards participation (WGs, editors/chairs); accreditation coverage (17025/17020); where to verify scopes.
- **Consortia/Clusters & Incubators/Accelerators** — who convenes collaboration; notable cluster programmes; testbeds/sandboxes; public‑private bridges.
- **Financial Institutions & Foundations/NGOs** — public banks, development funds, philanthropic funders supporting tech; instruments that touch dual‑use.
- **Think Tanks & Academic Centers** — policy/ethics/export‑control expertise; watchpoints for guidance.

For each sub‑section: **name 2–5 exemplars** with one‑line functions/capabilities and a link. If more than 5 exist, provide a table or link to the TSV and summarize patterns (e.g., regional clustering, sector focus).

### 3) Interconnection Map (textual)
- Describe **typical paths** from research to deployment (e.g., funding → lab → testbed → standards → procurement) and name **1–2 concrete cross‑category linkages** (e.g., University X + RTO Y + Firm Z in standards WG Q).
- Note **international ties** that are structurally important (anchor partners by country/category; reference Phase 5 where applicable).

### 4) Diligence & Gaps
- Call out **beneficial ownership opacity**, **accreditation gaps**, or **governance red flags** observed in the roster.
- Mention **MCF‑consistent** signals if present (label‑independent), but keep them as **signals** with `uncertainty_note` unless backed by ≥2 anchors.
- State **verification paths** (where an analyst can click to confirm claims quickly).

### 5) What to watch (3–5 bullets)
- Upcoming calls/programmes that could reshape the map, major facility upgrades, standards milestones, or policy reforms.

---

## Narrative tone & sourcing
- Neutral, watchdog‑style; avoid speculation; mark uncertainty explicitly.
- Every non‑obvious claim should have an **evidence_id** and URL in the roster or be hyperlinked in the narrative.

---

## Next Data Boost (close the report)
Provide **one** pragmatic action (e.g., “Import the national 17025 registry CSV and auto‑populate AccreditedLabs.tsv; re‑rank top facilities by recency of validation”).

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 3 report per the contract above.**

