---
title: "Phase 0 — Setup (Austria)"
author: Analyst
date: "<AUTO>"
---

## Scope
- **Country:** AT (Austria)
- **Years:** 2015–2025 (fixed for comparability)
- **Sectors (initial focus):** AI; Semiconductors; Quantum; Advanced Materials; Biotech/Biosecurity; Space; Robotics & Autonomous Systems; Cybersecurity; Photonics; High‑Performance Computing; Energy Storage & Batteries; Precision/Advanced Manufacturing; Sensors; Communications (5G/6G); Additive Manufacturing.
- **Lenses:** Military‑Civil Fusion (MCF) and **Supply Chain Security (SCS)** across **Materials • Knowledge • Technology • Finance • Logistics**.
- **Matching:** *Looser matchers ON* (broad keyword families; multi‑lingual when available).

## Key Questions
1. What public signals exist about Austria’s capabilities and international links in the target sectors?
2. Where might PRC MCF pathways intersect with Austrian institutions, programs, firms, or standards roles?
3. Which SCS pillars show potential **chokepoints** (single‑source or concentrated dependencies)?
4. What practical **controls/mitigations** could reduce exposure without harming legitimate research and trade?

## Operating Principles
- **Happy Path first:** All phases must render from existing processed tables; optional boosts never block output.
- **Conservative inference:** Escalate claims only with evidence; assign confidence **low/med/high**.
- **Entity hygiene:** Use CER‑lite (name+country) to reduce duplicates; flag **(ambiguous)** when uncertain.
- **Guardrails:** Note when a sector is dominated by a single consortium/entity (>50% edges).

## Data Presence Checklist (expected under `data/processed/country=AT/`)
- [ ] `relationships.csv`
- [ ] `signals.csv`
- [ ] `standards_roles.tsv`
- [ ] `cer_master.csv`
- [ ] `institutions.csv`
- [ ] `mechanism_incidents.tsv`
- [ ] `programs.csv`
- [ ] `sanctions_hits.csv` *(optional; from screening)*
- [ ] `policy_corpus.tsv` *(optional; narrative)*
- [ ] `policy_assertions.tsv` *(optional; narrative)*
- [ ] `policy_quotes.tsv` *(optional; narrative)*

> If a file is missing or empty, later phases will still render with an explicit “No data yet” note and a suggested action.

## References & Portals (seed list — expand later)
- National: accreditation body; research & innovation ministry/agency portals; export‑control authority; statistics office.
- EU/International: CORDIS; EU Funding & Tenders; Eurostat; UNCTAD; OpenSanctions; GLEIF; IETF Datatracker.
- Internal watchlist: `queries/policy/watchlist.yaml` (low‑cadence narrative refreshes).

## Working Notes
- Treat every build as a **snapshot**; add one manual boost when time permits, then rebuild.
- Keep narratives short and source‑anchored; use tables for counts and clear caveats for data gaps.
- Preferred order of effort: run Happy Path → scan Phase‑2/5 highlights → draft bullets → consider one manual CSV.

## Next Data Boost (optional)
Add **one** of the following when time allows, then re‑run normalize/build:
- **CORDIS participants CSV** for Austrian projects (improves Phases 2 & 5 linkage clarity), or
- **Accredited labs CSV** from the national accreditation body (improves Phase 3).

