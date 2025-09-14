# OSINT Foresight — Master Prompt (Phases 0–8 + SCS + Narrative Sources)

> **Works out of the box** with processed tables. **Manual Boosts** are optional and clearly marked. Where "find all the data" conflicts with "happy path," the **happy path wins**. Integrated **Supply Chain Security (Phase 2S)** and a **Text Intelligence** module for policy/white-paper sources. Includes the **Analyst Prompt Pack** at the end for copy-paste extraction.

---

## Global Settings
- COUNTRY: `<ISO2>` (e.g., SE)
- YEARS: 2015–2025
- Sectors taxonomy: `taxonomies/keywords_multilingual.yaml` (looser matchers ON)

## Processed Tables (contract of record)
Under `data/processed/country=<ISO2>/`:
- `relationships.csv` — co‑publications/projects/standards ties (OpenAIRE/Crossref/CORDIS)
- `signals.csv` — Crossref Event Data (optional)
- `standards_roles.tsv` — IETF roles (optional)
- `cer_master.csv` — canonical entities
- `institutions.csv` — org/lab identities (+ accreditation)
- `mechanism_incidents.tsv` — corporate/IP mechanisms (OpenCorporates/Patents)
- `programs.csv` — funders/instruments (CORDIS)
- `sanctions_hits.csv` — optional screening from `normalize:screening`
- **Narrative**: `policy_corpus.tsv`, `policy_assertions.tsv`, `policy_quotes.tsv` (optional; from `normalize:policy`)

---

## Output Package (per run)
- `reports/country=<ISO2>/phase-<n>_*.md` (all phases below)
- `summary_phase2-8.md` (1–2 pages)
- **New:** `phase-2s_supply_chain.md` and `policy_brief.md`

---

## Phase 0 — Watchdog / Think Tank Setup
**Objective**: scope, sectors, trackers.
**Deliverable**: `phase-0_setup.md` with scope & data presence checklist.
**Manual Boost**: `docs/references/03-portals.md` for national sites.
**Narrative sources to add (optional)**: Government strategy portals index.

## Phase 1 — Indicators & Data Sources
**Objective**: indicators → tables/columns.
**Deliverable**: `phase-1_indicators.md`.
**Manual Boost**: map additional narrative tables (`policy_*`) to phases.
**Narrative sources to add**: watchlist of ministries/think tanks.

## Phase 2 — Technology Landscape & Maturity
**Objective**: sector maturity, momentum, standards posture.
**Deliverable**: `phase-2_landscape.md`.
**Manual Boost**: OpenAlex CSV for niche subfields.
**Narrative sources to add**: standards roadmaps; national AI/HPC strategies (context for sector narrative).

## Phase 2S — Supply Chain Security (SCS) Snapshot
**Objective**: exposures across **Materials/Knowledge/Technology/Finance/Logistics** with PRC MCF lens.
**Deliverable**: `phase-2s_supply_chain.md`.
**Manual Boost**: UN Comtrade HS6 imports; UNCTAD LSCI; OpenSanctions CSV.
**Narrative sources to add**: port authority reports; export control notices; critical minerals white papers.

## Phase 3 — Institutional Map & Accredited Labs
**Objective**: key orgs/labs with IDs + accreditation.
**Deliverable**: `phase-3_institutions.md`.
**Manual Boost**: national accreditation CSV.
**Narrative sources to add**: accreditation body guidance; lab designation decrees.

## Phase 4 — Funders & Instruments
**Objective**: map programs/instruments.
**Deliverable**: `phase-4_funders.md`.
**Manual Boost**: EU Funding & Tenders CSV.
**Narrative sources to add**: budget bills; ministerial calls; procurement circulars.

## Phase 5 — International Links & Collaboration (SCS overlay)
**Objective**: CN partners, mechanisms, SCS tags.
**Deliverable**: `phase-5_links.md`.
**Manual Boost**: CORDIS participants CSV.
**Narrative sources to add**: MOUs; joint communiqués; standards WG notes.

## Phase 6 — Risk & Best‑Practice Verification (incl. SCS)
**Objective**: risk vectors ↔ observed mechanisms; practical mitigations.
**Deliverable**: `phase-6_risk.md`.
**Manual Boost**: sample contract clauses; policy control notices.
**Narrative sources to add**: export control FAQs; research security guidance; procurement integrity guides.

## Phase 7C — PRC Interest & MCF Acquisition Assessment
**Objective**: interest ladder, specificity 0–5, mechanisms (incl. SCS levers).
**Deliverable**: `phase-7c_posture.md`.
**Manual Boost**: `policy_corpus.tsv` (MIIT/NDRC/SASAC + provincial DRCs).
**Narrative sources to add**: five‑year plans; provincial implementation measures; MCF program descriptions.

## Phase 8 — Foresight & Early Warning (2y / 5y / 10y)
**Objective**: scenarios + tripwires + actions.
**Deliverable**: `phase-8_foresight.md` + `summary_phase2-8.md`.
**Manual Boost**: parliamentary inquiries; watchdog reports.
**Narrative sources to add**: industry association forecasts; government horizon scanning docs.

---

## Where narrative sources strengthen phases
- **P2/P2S**: standards roadmaps, export-control notices → explain why intensity/momentum matters and where chokepoints come from.
- **P3**: accreditation decrees/ministerial designations → validate lab status.
- **P4**: budget acts/calls → pin instrument maturity and timing.
- **P5**: MOUs/communiqués → provide context for spikes in collaboration; indicate intent vs. binding.
- **P6**: research security guidance/contract clauses → concrete mitigations.
- **P7C**: official plans and think‑tank reports → elevate **Specificity** from 2→3+ with citations.
- **P8**: public horizon scanning → anchor 5y/10y narratives.

---

## Analyst Prompt Pack (embed in repo under `/prompts/textint/`)

### 0) Quick Triage (10 minutes)
> I will paste an excerpt from a policy document. In a numbered list, tell me: (1) what this is (type/issuer), (2) top three points, (3) concrete mechanisms/controls, (4) SCS pillar relevance (Materials/Knowledge/Technology/Finance/Logistics), (5) a 2‑sentence summary.

### 1) Policy Snapshot (single TSV row)
> Output one TSV row with fields: source_id, title, issuer, issuer_level, pub_date, url, lang, country_scope, policy_domain, sectors, instruments, maturity, stance_prc_mcf, enforcement_tools, time_horizon, review_cycle, credibility_1_5, confidence, summary. Leave unknowns blank; keep summary ≤500 chars.

### 2) Mechanisms & Controls (claims TSV)
> Extract claims as TSV: source_id, claim_id, page, paragraph, claim_text, claim_type (mechanism/control/funding/standardization/restriction/capacity_building), sectors, scs_pillars, mechanisms, controls, evidence_refs, confidence.

### 3) Quote Capture (verbatim)
> 3–10 quotes ≤300 chars with page number + relevance tag. TSV: source_id, page, quote, context, relevance, sectors, scs_pillars.

### 4) Specificity to 7C (policy alignment)
> Build a table: sector → specificity contribution (0–5) with 1‑line justification citing the policy.

### 5) Controls to Phase 6 (risk mitigations)
> Convert controls into Phase‑6 mitigations: control name, risk vector, sector, pillar, implementation burden (low/med/high), one‑line how‑to for SMEs/universities.

### 6) SCS Levers Map (Phase 2S)
> Map each assertion to SCS pillars; list named entities, leverage path, and confidence.

### 7) Contradiction & Tension Finder
> Compare with past `policy_assertions.tsv`; list contradictions and resolution ideas (authority/recency).

### 8) One‑Pager Policy Brief
> Write a 1‑pager with: (a) 5 bullets of what matters, (b) 3 mechanisms + 3 controls with sectors/pillars, (c) a 6‑row sector→specificity table, (d) 3 trackable tripwires.

---

## Natural Stopping Points (per phase)
Follow **Check → Compute → Render → Narrate**. Stop after any step if the assistant struggles with context length.
- P0/1: Check files → Render scope matrix ✓
- P2: Compute edges & momentum → Render scorecard ✓
- P2S: Map pillars → Identify chokepoints ✓
- P3: List institutions → (optional) add accreditation ✓
- P4: List instruments → Join sectors ✓
- P5: Rank partners → Tag SCS pillars ✓
- P6: Fill matrix → Draft mitigations ✓
- P7C: Assign L1/L2/L3 → Score specificity ✓
- P8: Draft 2y/5y/10y scenarios → Add tripwires ✓

---

## Ready‑to‑Run
- Happy path: `make pull COUNTRY=<ISO2> && make normalize COUNTRY=<ISO2> && make build COUNTRY=<ISO2>`
- Add policy sources: place TSVs → `make normalize-policy COUNTRY=<ISO2>` → `make build-policy-brief COUNTRY=<ISO2>`
- SCS screening: place sanctions CSV → `make normalize:screening COUNTRY=<ISO2>` → `make build:phase-2s COUNTRY=<ISO2>`
