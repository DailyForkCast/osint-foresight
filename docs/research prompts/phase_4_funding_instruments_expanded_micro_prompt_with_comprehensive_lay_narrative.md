Below is a single, copy‑paste **micro‑prompt** to run Phase 4 with a comprehensive lay narrative (like Phase 3). It preserves the original TSV outputs (B1–B4) and adds deep, category‑wise coverage of funders and instruments.

---

# Run Phase 4 — Funding & Instruments for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 4 — Funding & Instruments (reports/country=<ISO2>/phase-4_funding.md)"
- The canvas must contain **ONLY final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>"]**, toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If sources are thin, still render a complete report with “No data yet — drop‑in CSV recipe below” notes.

---

## What to produce (sections)
1) **Front‑matter** — title, author, date.
2) **Tables B1–B4** — Funders & Instruments registry; Regional Programmes; Bank/Guarantee/Equity lines; Optional Call Snapshot.
3) **Quality & screening notes** — name normalization, recency, portal verification; soft sanctions/legal cross‑screen (signals‑only; exclude US persons entirely from flags/narrative).
4) **Comprehensive Lay Narrative** — expanded treatment (see template below) + a **3–5 bullet summary**.
5) **Next Data Boost** — one pragmatic, high‑ROI action.

---

## TSV outputs (return each as Markdown table + `# excel-tsv`)

### B1 — Funders.tsv (registry of funding bodies)
```
# excel-tsv
funder_id	funder_name	level	funder_type	country	website	scope	sector_focus	instruments_offered	typical_award_band	cofunding_match_req	foreign_eligibility	compliance_hooks	portal_url	notes	evidence_id
```
- **level** ∈ {national, regional, EU, international}
- **funder_type** ∈ {ministry, agency, council, EU_body, public_bank, foundation, development_fund, other}
- **compliance_hooks**: ethics/export/data‑protection/dual‑use clauses, etc.

### B2 — Programmes.tsv (named programmes/initiatives)
```
# excel-tsv
programme_id	funder_id	programme_name	instrument_type	description_short	sector_tags	budget_total_est	award_band	cadence	years_active	calls_portal_url	eligibility_summary	consortium_rules	notes	evidence_id
```
- **instrument_type** ∈ {grant, procurement, prize, mixed}
- **cadence** ∈ {rolling, annual, ad‑hoc}

### B3 — BankGuaranteeLines.tsv (risk finance / credit / equity)
```
# excel-tsv
instrument_id	provider_name	instrument_type	target_beneficiary	ticket_size_band	tech_focus	terms_summary	portal_url	notes	evidence_id
```
- **instrument_type** ∈ {loan, guarantee, equity, blended}

### B4 — CallSnapshot.tsv (optional observation‑only)
```
# excel-tsv
call_id	programme_id	title	status	open_date	close_date	sector_tags	TRL_band	budget_est	country_focus	consortium_req	link	notes	evidence_id
```

---

## Quality & screening (print as bullet list)
- **CER‑lite hygiene:** normalize `funder_name` and `programme_name`; keep official acronyms; retain portal URLs.
- **Recency rule:** prefer items with activity/updates in the last **24–36 months**; if older, include but mark `notes`.
- **Instrument taxonomy:** map each instrument to {grant/procurement/prize/mixed}. If unclear, pick the **closest** and set `notes="unclear subtype"`.
- **Sanctions/legal cross‑screen (signals only):** soft‑flag if a funder/beneficiary name (non‑US persons only) matches official EU/UK/CA/AU/NZ/UN lists or appears in a relevant legal case. These are **signals, not proof**. **Exclude American citizens/persons entirely** from flags and from narrative.
- **Verification path:** each row should have at least one **click‑through portal link** an analyst can use to verify quickly.

---

## Comprehensive Lay Narrative (write this)
Provide a **structured, category‑wise narrative** that explains **who funds what, through which instruments, at what cadence/scale, with what access and compliance hooks**, and **how this shapes dual‑use outcomes**.

### 1) Landscape Overview (8–12 sentences)
- Summarize the **funding system topology**: principal national funders, EU overlays, regional actors, and public banks/foundations.
- Explain **instrument mix** (grant vs procurement vs prize vs risk finance) and the typical **award bands** and **cadence**.
- Note **concentration** (e.g., top‑1 programme share; if `top1_share > 0.5`, add a caution) and any **foreign‑partner eligibility** norms.

### 2) Category‑wise Funders (short blurbs with links & exemplars)
Include the categories that exist; omit those with no presence (or say “none observed”):
- **National Ministries/Agencies/Councils** — mandates, instrument mix, exemplar programmes.
- **EU/International Bodies** — Horizon Europe/EDF/COST/EUREKA/Xecs/EuroHPC/ESA/NATO SPS, etc.; where the country plugs in.
- **Regional/Local Authorities** — smart‑specialization programmes; cluster funds.
- **Public Banks/Development Funds** — EIB/EIF/national development banks; guarantees/credit/equity lines; typical tickets.
- **Foundations/Philanthropy** — thematic grants relevant to dual‑use enabling tech.

For each sub‑section: list **2–5 exemplars** with **instrument type**, **award band/cadence**, **sector tags**, **portal link**.

### 3) Instruments Typology & Use‑Cases
- Explain the **use‑cases** of grants vs **procurement** (mission pull), **prizes** (incentivized breakthroughs), and **risk finance** (scale‑up, capital intensity).
- Name **1–2 concrete examples** of each instrument type relevant to dual‑use sectors in this country.

### 4) Flow of Funds & Access Rules
- Who can apply (universities/RTOs/SMEs/consortia); **consortium rules**, **match‑funding**, **TRL bands**.
- **Foreign participation**: whether third‑country partners are eligible; special clauses for sensitive tech.
- **Compliance hooks**: ethics, export‑control/dual‑use clauses, data‑protection, security clearances (if any). Provide **exact portal links**.

### 5) Market Signals & Skews
- Identify **programme cadence** (rolling/annual/ad‑hoc) and any **award concentration** (repeat winners, dominant regions).
- If amounts are opaque, use **proxies** (cadence, award‑band norms, winner‑region concentration) and log in `ProxyLog` (add a small table if used).

### 6) Risks, Gaps, Mitigations
- Note any **opacity** (unclear instrument types, missing portals), **eligibility bottlenecks**, or **procurement bias** that could affect dual‑use pathways.
- Add **soft sanctions/legal hits** (non‑US persons only) where relevant to funders/beneficiaries; treat as **signals** and explain the verification path.

### 7) What to Watch (3–5 bullets)
- Upcoming calls, new instruments (e.g., challenge prizes), policy changes (state‑aid rules), or public‑bank facilities.

### 8) 3–5 Bullet Summary (executive close)
- Provide 3–5 crisp bullets summarizing **who funds what, how, and why it matters** for dual‑use and standards/MCF‑consistent pathways.

---

## Optional small tables used in narrative (include only if needed)
```
# excel-tsv
ProxyLog.tsv
metric_id	description	value	unit	source_tier	confidence_0to1	evidence_ids	comment
```
```
# excel-tsv
TopInstruments.tsv
instrument_type	count	median_award_band	cadence_mode	comment
```

---

## Next Data Boost (close the report)
Provide **one** pragmatic action (e.g., “Scrape the national funding portal index page to seed B1/B2; normalize instrument types; re‑rank programmes by cadence”).

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 4 report per the contract above.**

