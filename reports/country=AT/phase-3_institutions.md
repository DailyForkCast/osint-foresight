---
title: "Phase 3 — Institutions & Accredited Labs (Austria)"
author: Analyst
date: "<AUTO>"
---

## Data presence
- institutions.csv: no
- relationships.csv: yes (rows=12)
- standards_roles.tsv: yes (rows=2)
- cer_master.csv: no

## Institutional Map (counts by type)
| Org type | Count |
|---|---:|
| – | – |


## Accredited Labs (top 10)
| Name | Accreditation ID | Scope | City |
|---|---|---|---|
| – | – | – | – |


## Standards‑linked Organizations (sample)
| WG/SDO | Role | Person | Organization | Sector hint |
|---|---|---|---|---|
| – | – | – | – | – |


## Relationship Coverage (top counterparts in Phase‑2 edges)
| Organization (normalized) | Edge count |
|---|---:|
| carnegie mellon university | 1 |
| eurocc slovenia (sling) | 1 |
| eurohpc leonardo | 1 |
| imec | 1 |
| max planck institute (tübingen) | 1 |
| neural magic | 1 |
| university of chicago | 1 |
| university of oxford | 1 |
| university of texas at austin | 1 |
| university of tübingen | 1 |


## CER‑lite Snapshot
| Canonical entities | Ambiguous entities |
|---:|---:|
| – | – |


## Narrative Snapshot
- Phase‑2 edges include identifiable institutions; use CER‑lite to improve naming.

## Minimal CSV (drop‑in) — if you have 10 minutes
Add `data/raw/source=accreditation/country=AT/date=<YYYY-MM-DD>/labs.csv` with header:

```
name,country,accreditation_id,scope,city,is_lab
```
Then run `make normalize-all COUNTRY=AT` and rebuild.