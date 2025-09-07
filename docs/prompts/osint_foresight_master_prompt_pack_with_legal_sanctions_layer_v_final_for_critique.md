# How to use this pack
Run **one micro‑prompt at a time**, in order. Each step returns a complete, human‑readable report section **plus** any spreadsheet tables twice: (1) Markdown table and (2) a fenced `# excel-tsv` block for copy/paste into TSV files. Low‑cadence narrative (policy/portals/legal) is designed to be refreshed quarterly/annually.

---

## Global (once per country) — SESSION header & conventions
**You say to ChatGPT:**
```
SESSION_HEADER for <COUNTRY NAME> (<ISO2>)
- timeframe: 2015–present
- languages: ["en", "<local>"]
- toggles:
    include_export_controls: true
    include_us_natsec_8cats: true
    include_energy_tech: false
    deep_research_precedence: true
    wikipedia_citation: off
- watchdog_guardrails: independence, reproducibility, proportionality, privacy/ethics, non-advocacy
- excel_ready_mode: output every table twice (markdown + fenced block labeled `# excel-tsv`)
- evidence_policy: open-source only; cite URLs; log access dates
- happy_path: pull → normalize → build; panic_buttons: write empty-but-valid tables if a source is missing
```

---

# Phase X — Definitions & Taxonomy (insert once before Phase 1)
**Canvas (file):** `Write <COUNTRY> Phase X — Definitions & Taxonomy (reports/country=<ISO2>/phase-x_taxonomy.md)`

**Do:**
- Glossary of key dual‑use terms; sector taxonomy (6–10 clusters → subdomains) with 1–2 example technologies each.
- Competitiveness criteria & bands (Global Leader/Challenger/Regional Leader/Competitive); simple rubric.
- If 8‑Cats toggle ON, map sectors to US NatSec 8 categories.
- Output: short glossary table + ASCII taxonomy + criteria list. (Low cadence; refresh annually.)

---

# Phase 0 — Setup (watchdog/think tank)
**Canvas (file):** `Write <COUNTRY> Phase 0 — Setup (reports/country=<ISO2>/phase-0_setup.md)`

## P0-A — Setup & guardrails
- Print SESSION header & guardrails; Proxy Toolkit mini (tiers, confidence_0to1, red‑team checks).
- Add Happy Path and Panic Buttons.

## P0-B — References & watchlist (low cadence)
- Portals list (gov/regulators; funding/programs; standards/accreditation; research/statistics/IP; trade/logistics/registries; EU/international).
- Add 6–8 watchlist YAML lines: `name, url, cadence` (weekly/monthly/quarterly).

## P0-C — Evidence discipline & audit protocol
- Evidence Register fields; screenshot/versioning rules; audit protocol (target Cohen’s κ ≥ 0.7; re‑verify stale > 36 months).

---

# Phase 1 — Indicators & Data Sources (compact baseline)
**Canvas (file):** `Write <COUNTRY> Phase 1 — Indicators & Data Sources (reports/country=<ISO2>/phase-1_indicators.md)`

## P1-A — Indicators + CN add‑ins
- List compact indicators: CORDIS P1/P2/€1 (H2020 & HE separate), ERC/MSCA, HPC peak/sustained, standards roles, patents, trade/FDI.
- CN add‑ins: PRC co‑authorship rate; CORDIS P1/P2 with PRC; joint patents; standards co‑leadership.
- Output two TSV blocks:
  - `# excel-tsv: Indicators.tsv`
  - `# excel-tsv: Non-Conforming.tsv` (contradictions log)
- Finish with 3–5 plain‑language takeaways.

## P1-B — Multilingual plan & proxy log
- EN + local + ZH search plan; keep H2020 vs HE separate; add Proxy Log TSV with `confidence_0to1`.

**Where data helps (free):** CORDIS/Results & Dashboard; EuroHPC; ETSI/ISO/IEC/OGC; WIPO/EPO; Eurostat; national stats.

---

# Phase 2 — Technology Landscape & Maturity
**Canvas (file):** `Write <COUNTRY> Phase 2 — Technology Landscape (reports/country=<ISO2>/phase-2_landscape.md)`

## P2-A — Per‑sector capture (≤6 sectors)
For each sector: definition; maturity (Strong/Emerging/Nascent) with evidence; capabilities (labs/testbeds/compute/datasets/standards roles); ≤3 examples; export hooks; **show top‑3 matched keywords** used for retrieval transparency.
- Output TSV: `SectorLandscape.tsv`

## P2-B — PRC add‑ins + QA + proxies
- PRC policy alignment (title/date/issuer/key line); standards posture (WGs where PRC co‑leads vs local co‑chairs). If claiming MCF relevance, link to annex/ECCN or mark “unclear”.
- Add Non‑Conforming Signals TSV and Proxy Log (lab CAGR, effective HPC ratio, specialist kit). Apply **recency weighting**.

## P2-C — Lay summary & consortium skew
- 3–5 bullets per top sector; momentum/event spikes; caution if `top1_share > 0.5`.

**Where data helps (free):** facility/testbed pages, SDO rosters, accreditation registries.

---

# Phase 2S — Supply Chain Security (five‑pillar lens + legal overlay)
**Canvas (file):** `Write <COUNTRY> Phase 2S — Supply Chain Security (reports/country=<ISO2>/phase-2s_supply_chain.md)`

## P2S-A — Five‑pillar exposure (K/T/M/F/L)
- Map `collab_type→pillar` and count per sector. Add brief narrative per top sector on Knowledge/Technology/Materials/Finance/Logistics exposure.
- Output TSV: `SupplyPillars.tsv` with columns: `sector, K, T, M, F, L`.

## P2S-B — PRC exposure & **Sanctions/Legal overlay**
- Compute PRC share per sector; list top 1–2 CN counterparts.
- **Sanctions overlay:** exact/normalized joins to sanctioned names; add counts + exemplars; mark as **signal, not proof**.
- Output TSVs:
  - `sanctions_hits.csv`: `match_type, source_list, name_matched, canon_name, country, matched_on, evidence_url, notes`
  - `legal_cases.tsv` (optional, if found): `case_id, jurisdiction, law/policy, defendant, alias(es), entity_type, tech_domain, allegation, outcome, year, country, source_url`

## P2S-C — Logistics/procurement narrative & Next Data Boost
- One paragraph on procurement/logistics exposure (ports/customs/national procurement portal); **1 example** if available.
- “Next Data Boost” suggestion (e.g., add tenders CSV 2019–2025) and path to rebuild.

**Where data helps (free):** national procurement portals, EU TED summaries, customs/dual‑use guidance pages; OFAC/EU/UK/CA/AU/NZ/UN lists (official), OpenSanctions (secondary search), DOJ/BIS enforcement press.

---

# Phase 3 — Institutions & Accredited Labs
**Canvas (file):** `Write <COUNTRY> Phase 3 — Institutions & Accredited Labs (reports/country=<ISO2>/phase-3_institutions.md)`

## P3-A — Roster (with CN/controls fields)
- Output TSV `Roster.tsv` with:
  `id, org_name, alt_name_zh, lei_or_national_id, org_type, city_region, sectors, capability_notes, facility_name, metric_1, metric_2, funders_partners, standards_roles, prc_links_note, beneficial_owner_summary, ci_stem_y_n, risk_note, evidence_id, url`.
- Use **CER‑lite** (name+country) before rankings; tag `(ambiguous)` if unresolved.

## P3-B — Accredited labs shortlist + QA
- Output TSV `AccreditedLabs.tsv` with:
  `organisation, iso_standard, accreditation_id, scope_short, sector_tags, city_region, status_note, last_check, links`.
- If none, print header + “drop‑in later” note.

## P3-C — Lay summary
- Who the players are; which facilities matter for dual‑use; PRC‑linked ties + diligence actions; partnership opportunities & gaps.

**Where data helps (free):** national accreditation bodies; company/BO registries; university directories; GLEIF/LEI.

---

# Phase 4 — Funders & Instruments (observation‑only)
**Canvas (file):** `Write <COUNTRY> Phase 4 — Funding & Instruments (reports/country=<ISO2>/phase-4_funding.md)`

## P4-A — Funders & instruments lists
- Output TSV blocks: **B1 Funders & Instruments**, **B2 Regional Programmes**, **B3 Bank/Guarantee Lines**, optional **B4 Call Snapshot**.
- Map instrument into **grant / procurement / prize**. Add search portal links.

## P4-B — **Sanctions/Legal cross‑screen** (soft flags) & lay summary
- Cross‑screen funders/beneficiaries vs `sanctions_registry.csv` and `legal_cases.tsv` → **soft red flags** (narrative‑only; no dispositive claims). Add 3–5 bullet lay summary.

**Where data helps (free):** HE/EDF/COST/EUREKA/Xecs/EuroHPC/ESA/NATO SPS; UKRI/NSF/NIH/DFG/ANR/NEDO/JST; DIANA; EIB; official sanctions portals.

---

# Phase 5 — International Links & Collaboration
**Canvas (file):** `Write <COUNTRY> Phase 5 — International Links (reports/country=<ISO2>/phase-5_links.md)`

## P5-A — Heat‑map & top relationships
- Partner‑country × sector heat‑map (Intensity 0–3; Risk L/M/H) with ≥1 primary source per non‑zero cell.
- Output TSVs: `HeatMap.tsv` (long), `TopRelationships.tsv`.
- Optional: `PRCEntities.tsv` (gov/university/SOE/corporate). Run **CER‑lite** pre‑ranking.

## P5-B — **Sanctions/Legal join** (signals) & lay summary
- Join top partners to `sanctions_registry.csv` and `legal_cases.tsv`; write 2–3 lines per hit on **why it matters** to a sector (signal, not proof). Close with benefits/risks, PRC ties, and mitigations.

**Where data helps (free):** CORDIS co‑participation, standards co‑leadership, JV/equity filings, SOE/SASAC tags, official sanctions portals, OpenSanctions (search).

---

# Phase 6 — Risk & Best‑practice Verification
**Canvas (file):** `Write <COUNTRY> Phase 6 — Risk & Best-practice (reports/country=<ISO2>/phase-6_risk.md)`

## P6-A — Controls & ethics/legal hooks
- Controls Library C1–C10; Ethics/Legal checklist (IRB/IBC; export classification; DPIA/data map; MTAs/DUAs; KYC/BO/sanctions; facility SOPs; **model‑weight policy**; pre‑publication).
- Map each control to an observed mechanism/standards role; one line each.
- Output TSVs: `RiskRegister.tsv`, `ControlsLibrary.tsv`, `DecisionGates.tsv`, `FindingsRemediation.tsv`.

## P6-B — **Legal/Controls Evidence** & falsification
- Add **case vignettes** (≤120 words each) drawn from `legal_cases.tsv` (or narrative if not available): defendant/entity, tech, allegation, outcome/status, year, source.
- Add falsification tests per top risk; proxies when incident data missing (export‑advisory trend; transfer notices; FDI reviews; model‑weight flags; vendor HHI). Summarize top 5 risks → expected controls → verification plan → G/A/R → Go/No‑Go.

**Where data helps (free):** DOJ/BIS/Treasury press; EU sanctions map; national enforcement; official list portals.

---

# Phase 7C — PRC Interest & MCF Acquisition Assessment
**Canvas (file):** `Write <COUNTRY> Phase 7C — PRC Interest & MCF (reports/country=<ISO2>/phase-7c_interest_mcf.md)`

## P7C-A — Signals & footprint (with legal layer)
- Populate **PRC Interest Signals**, **In‑Country Footprint**, **Acquisition Vectors** from registries, gov portals, awards DBs, standards rosters, filings. Record EN+ZH names, registry IDs, dates, amounts/stakes; `source_tier` & `confidence`.
- Cross‑reference `sanctions_registry.csv` and `legal_cases.tsv`; use as **specificity** anchors.

## P7C-B — Policy/white papers & scoring
- Add policy/white‑paper snippets; compute **Priority Index vs Convenience Index** with rationale & uncertainty.

## P7C-C — Lay summary (watchdog tone)
- Key takeaways; vectors with dates/amounts/stakes; posture call + uncertainty; mitigations suitable for a watchdog.

**Rule:** To escalate L1→L2, require ≥1 evidence row; to L3, require ≥1 policy anchor **or** legal/sanctions anchor.

---

# Phase 7R — Assumption Check & Red‑team Review
**Canvas (file):** `Write <COUNTRY> Phase 7R — Red-Team (reports/country=<ISO2>/phase-7r_redteam.md)`

- Journalist‑style critique per phase; contradictions with severity; coverage gaps; method stress‑tests (double counting; keyword bias; Tier‑3 overreliance); ethics/export blind spots.
- Output TSVs: `ContradictionsLog.tsv`, `RedTeamActions.tsv`. Close with Top‑5 fixes (owners, due dates) and fit‑for‑public decision.

---

# Phase 8 — Foresight & Early Warning (2y/5y/10y)
**Canvas (file):** `Write <COUNTRY> Phase 8 — Foresight (reports/country=<ISO2>/phase-8_foresight.md)`

## P8-A — Methods & variables
- Pick ≥3 methods (signals→trendlines, standards velocity, programme pipeline, scenario cones, structural breaks, hindcast/backtest). Define forecast variables (activity index, maturity trajectory, standards velocity, funding outlook, capacity, talent, policy).

## P8-B — PRC targeting model (2y/5y/10y)
- Score = Attractiveness + Access + Payoff − Friction (defaults okay). Output: targeting scores, institution watchlist, country risk, triggers.

## P8-C — Red‑team & calibration
- Hindcast/backtest (MAE/MAPE); remove Tier‑C to test fragility; publish uncertainty bands and attributions.

**Where data helps (free):** historical signals; standards pipeline; programme cadence; policy cycles.

---

## Legal/Sanctions Casework — shared artifacts & micro‑prompts
**Files (append‑ready; optional but recommended):**
- `sanctions_registry.csv` (normalized index across lists):
  `list_name, list_agency, program, name, aka, entity_type, birth_or_incorp_year, country, lei, id_native, date_listed, date_updated, url`
- `sanctions_hits.csv` (joins into our ecosystem):
  `match_type, source_list, name_matched, canon_name, country, matched_on, evidence_url, notes`
- `legal_cases.tsv` (export‑control/tech‑transfer/enforcement):
  `case_id, jurisdiction, law_or_policy, defendant, aliases, entity_type, tech_domain, allegation, outcome, year, country, source_url`
- `fdi_screening_policies.tsv`:
  `country, regime_name, scope, screening_body, trigger_thresholds, sectoral_focus, defense_link, year_effective, url`
- `export_controls_baseline.tsv`:
  `country, regime, law_or_reg, dual_use_scope, licensing_body, penalties_blurb, url`

**Micro‑prompts (paste to ChatGPT whenever needed):**
1) *Legal framework explainer (country)* — “Summarize <Country>’s FDI screening (CFIUS‑like) and export‑control regime in ≤180 words; cite the legal basis and screening/enforcement bodies; add 1 example action since 2018 if found.”
2) *Sanctions posture snapshot* — “List official sanctions list portal(s) for US/EU/UK/CA/AU/NZ/UN and <Country>, with one‑line scope notes; add a cadence (weekly/monthly/quarterly).”
3) *Case vignettes* — “Find 1–3 tech‑transfer/export‑control cases relevant to <Country> or its institutions (2015–present). For each: defendant/entity, tech domain, allegation, outcome/status, year, source link. ≤120 words each.”
4) *Cross‑hit narrative* — “From our Top Relationships (Phase‑5) and Roster, check if any counterpart is sanctioned or named in a legal case; write 2–3 lines on why this matters to sector X (signal, not proof).”
5) *Controls mapping* — “Given Risk Register top items, map each to at least one control and one legal/policy hook (export classification, FDI screen, sanctions check, data‑protection). 1–2 lines each.”

**Free, stable sources to target narratively:** official sanctions portals (OFAC/EU/UK OFSI/CA/AU/NZ/UN), national sanctions pages; DOJ/BIS/Treasury press releases; EU Council/Commission notices; national prosecutor/justice ministry releases; CourtListener/RECAP; EU CURIA; OpenSanctions (search only, mark as secondary); GLEIF/LEI and national company registers for entity verification.

---

## Solo‑friendly guardrails (baked in)
- **Happy Path** at P0; **panic buttons** produce empty‑but‑valid tables when data thin.
- **CER‑lite** (name+country) before any partner ranking; tag `(ambiguous)` not dropped.
- **Consortium skew** guardrail: caution if `top1_share > 0.5`.
- **Low‑cadence narrative** (P0 portals; Phase‑3 roster notes; Phase‑4 funder descriptions) — refresh quarterly/annually.
- **Three highest‑ROI boosts:** CORDIS participants CSV; one national accreditation CSV; two PRC policy docs.

---

## Output contract reminder (applies to every micro‑prompt)
- **Create the canvas with the exact title** and write **only** final file content.
- If templates/data are missing, still render a complete report with “No data yet — drop‑in CSV recipe below” notes.
- Include inline citations for non‑obvious facts (URLs + access dates where possible).
- Return TSVs in fenced blocks labeled `# excel-tsv` for copy/paste.

