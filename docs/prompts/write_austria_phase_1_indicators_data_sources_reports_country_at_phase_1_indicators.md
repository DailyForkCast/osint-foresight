---
title: "Phase 1 — Indicators & Data Sources (Austria)"
author: Analyst
date: "<AUTO>"
---

## Purpose & Scope
Establish the **minimum indicator set** and data table contracts used across Phases 2–8, with defaults that render even when inputs are sparse. Fixed settings: **Years 2015–2025**, **looser matchers ON**.

## Data Inventory (expected under `data/processed/country=AT/`)
- relationships.csv — collaboration edges (OpenAIRE/Crossref/CORDIS)
- signals.csv — Crossref Event Data (optional)
- standards_roles.tsv — IETF roles (optional)
- cer_master.csv — canonical entities
- institutions.csv — organizations/labs (+ accreditation when present)
- mechanism_incidents.tsv — corporate/IP mechanisms
- programs.csv — funders/instruments (CORDIS/EU/FFG)
- sanctions_hits.csv — screening results (optional)
- policy_corpus.tsv, policy_assertions.tsv, policy_quotes.tsv — narrative sources (optional)

> If any file is missing, reports still render; later phases will show explicit “No data yet” notes and one Next Data Boost.

## Core Indicators (contract of record)
| Source file | Indicator families | Used by phases | Notes |
|---|---|---|---|
| relationships.csv | sector intensity (0–3), top partners, partner concentration, year buckets | 2, 5, 7C, 8, 2S | CER‑lite applied before ranking; caution when top‑1 >50%. |
| signals.csv | spikes/events by DOI/venue/year | 2, 7C | Optional qualitative context (“spike in 2021Q4”). |
| standards_roles.tsv | participant roles (chair/editor/author), WGs | 2, 5, 7C | Maturity & posture; ties to Knowledge pillar. |
| cer_master.csv | canonical name + country, ambiguous flag | 2, 5, 2S, 7C | Reduces duplicates; ambiguous flagged, never deleted. |
| institutions.csv | org type, lab flags, accreditation refs | 3, 6 | Accreditation strengthens credibility. |
| mechanism_incidents.tsv | JV, co‑assignment, BO, investment, licensing | 5, 6, 7C, 2S | Mechanism → mitigation mapping in Phase 6. |
| programs.csv | funder, instrument (grant/procurement/prize), amount, year | 4, 2 | Bin instruments to 3 types for clarity. |
| sanctions_hits.csv | list name, date | 2S, 6 | Screening overlay; optional. |
| policy_* .tsv | stance, mechanisms/controls, quotes | 6, 7C, 2S, 4 | Narrative anchors; credibility rubric 1–5. |

## Column Contracts (tolerant; leave blank if unknown)
- **relationships.csv**: `sector, counterpart_name, counterpart_country, collab_type, year`
- **standards_roles.tsv**: `wg, role, person_name, org_name, country, sector_hint`
- **mechanism_incidents.tsv**: `entity, country, sector, mechanism_family, year, ref`
- **programs.csv**: `program, instrument, funder, year, amount, sector_hint`
- **sanctions_hits.csv**: `name, country, list, listed_on, url`
- **policy_corpus.tsv**: `source_id, title, issuer, issuer_level, pub_date, url, lang, country_scope, policy_domain, sectors, instruments, maturity, stance_prc_mcf, enforcement_tools, time_horizon, review_cycle, credibility_1_5, confidence, summary`
- **policy_assertions.tsv**: `source_id, claim_id, page, paragraph, claim_text, claim_type, sectors, scs_pillars, mechanisms, controls, evidence_refs, confidence`

## Minimal Collection Plan (Happy Path)
1. Pull public sources (optional now): `make pull COUNTRY=AT`
2. Normalize with guardrails: `make normalize-all COUNTRY=AT`
3. Build core phases: `make build COUNTRY=AT`

## Narrative Snapshot (auto‑short)
- Data presence as of this run is unknown in this file; use **`make health COUNTRY=AT`** for freshness and missing files.
- Phase 2 will compute sector intensity and show top counterparts; Phase 5 will overlay SCS and mechanisms where present.

## Next Data Boost (one actionable)
Add a **CORDIS participants CSV** for Austria (2015–2025) to `data/raw/source=cordis/country=AT/date=<YYYY-MM-DD>/participants.csv`, then re‑run `make normalize-all COUNTRY=AT` and `make build COUNTRY=AT`. 

