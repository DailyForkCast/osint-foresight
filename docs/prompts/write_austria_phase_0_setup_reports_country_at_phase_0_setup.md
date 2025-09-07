---
title: "Austria — Phase 0: Setup"
author: OSINT Foresight (solo analyst)
date: 2025-09-07
---

## Project Setup Snapshot
- **Country / ISO2:** Austria (AT)
- **Horizon:** 2015–2025
- **Looser matchers:** ON
- **Languages:** en, de
- **Evidence framing:** Neutral, signals ≠ proof; uncertainty marked.

## Operating Parameters
- **Sectors in scope (initial):** AI/ML & Autonomy; High‑Performance Computing; Communications/Networking & Timing; Sensing/PNT; Advanced Materials/Manufacturing (select); Space/EO (watchlist).
- **MCF detection:** label‑independent (function‑over‑label). Claims need ≥2 anchors for high confidence.
- **Sanctions/legal overlay:** signals‑only; **exclude US persons entirely** from flags/narrative.
- **Standards focus:** IETF/ETSI/CEN/CENELEC/ISO/IEC (roles, editorships, test methods).
- **Accreditation focus:** ISO/IEC 17025/17020 and national registries.

## Data Inventory (processed layer)

| file | present | bytes | last_update | notes |
|---|:---:|---:|---|---|
| data/processed/country=AT/relationships.csv | ✔ | 707 | 2025‑09‑06 | Seed edges from conferences/EuroHPC/VSC |
| data/processed/country=AT/signals.csv | ✔ | 670 | 2025‑09‑06 | Seed signals (ICLR 2024 Vienna; VSC upgrade; AI Mission Austria) |
| data/processed/country=AT/standards_roles.tsv | ✔ | 238 | 2025‑09‑06 | IETF (IPPM/NTP) authorship (Joachim Fabini, TU Wien) |
| data/processed/country=AT/cer_master.csv | ✖ | — | — | Not yet generated (GLEIF/LEI merge pending) |
| data/processed/country=AT/institutions.csv | ✖ | — | — | Will be built in Phase 3 |
| data/processed/country=AT/mechanism_incidents.tsv | ✖ | — | — | Optional for P6/P7C |
| data/processed/country=AT/programs.csv | ✖ | — | — | For Phase 4 funding map |
| data/processed/country=AT/sanctions_hits.csv | ✖ | — | — | Signals‑only, non‑US persons |
| data/processed/country=AT/policy_PRCCorpus.tsv | ✖ | — | — | For P7C/P8 doctrine links |

> If a file is missing, later phases will degrade gracefully and show “No data yet” notes.

## Evidence Register & Versioning
- **Evidence IDs:** Use stable IDs per claim; link to URLs where possible.
- **Capture & hash (Phase‑0 protocol):** When saving a key web page or PDF, store `source_url`, `retrieved_at`, SHA‑256 of the file, and an anchor hash for the quoted passage.
- **Diffability:** Keep TSVs under version control; prefer additive rows with `last_check` timestamps.

### EvidenceRegister.tsv (create/append as data/evidence_register.tsv)
```text
# excel-tsv
id	country	type	title	issuer_or_site	url	retrieved_at	sha256	anchor_hash	notes
```

## References & Portals (seed)
See **docs/references/AT-portals.md** for the operational portal list (government, funders, standards/accreditation, research/IP, trade/logistics, EU/international). Use it to:
- Verify accreditation: national 17025/17020 registries.
- Pull funding/program info: national portal + CORDIS.
- Check standards roles: IETF/ETSI rosters.

## Minimal QA (can be run anytime)
- **Name hygiene:** Normalize org/person names; add `alt_name_local` where needed.
- **Country codes:** Use ISO‑3166 (AT) consistently in paths and tables.
- **Dates:** Use ISO (YYYY‑MM or YYYY‑MM‑DD). Record access dates for web sources.
- **Recency:** Prefer last 24–36 months; keep older items if still operative and mark as such.

## Risk, Ethics & Bias Guardrails
- Avoid stigmatizing language; root analysis in **observables**.
- Call out contradictions and unsupported assertions in **Phase 7R**.
- For sanctions/legal references: signals‑only, non‑US persons, cite source explicitly.

## Ready‑to‑Run Checks (manual or task)
- `make reports-init COUNTRY=AT` — (bulk‑copy templates; safe to re‑run)
- `make health COUNTRY=AT` — sanity/staleness snapshot
- `make bootstrap-textint COUNTRY=AT` — ensures Text Intelligence prompts/watchlist present

## Next Data Boost (1 step)
Import **national accreditation (17025) registry** into `AccreditedLabs.tsv` and re‑rank top labs/facilities by **last_check** recency; this will strengthen Phase 3 and downstream confidence.

