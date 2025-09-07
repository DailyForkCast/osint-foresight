---
title: "Phase 2S — Supply Chain Security (Austria)"
author: Analyst
date: "<AUTO>"
---

## Data presence
- relationships.csv: yes (rows=12)
- mechanism_incidents.tsv: no
- sanctions_hits.csv: no
- cer_master.csv: no

## Sector Exposure Summary
| Sector | K | T | M | F | L | PRC edges | PRC share | Top PRC counterpart(s) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| AI | 9 | 0 | 0 | 0 | 0 | 0 | 0.00 | – |
| High-Performance Computing | 1 | 3 | 0 | 0 | 2 | 0 | 0.00 | – |

**Pillars:** K=Knowledge, T=Technology, M=Materials, F=Finance, L=Logistics. Collab→pillar mapping is heuristic and conservative by default.

## Sanctions Overlay (optional)
| Sector | Sanctioned counterpart hits |
|---|---:|
| – | – |

## Mechanism Signals (if available)
| Sector | Mechanism family | Count |
|---|---|---:|
| – | – | – |

## Narrative Snapshot
- HPC likely shows T+L activity via infrastructure edges; validate with procurement or facility logistics where possible.

## Next Data Boost (one actionable)
Add a **procurement/tenders** CSV (2019–2025) with columns `buyer, supplier, item, date, value, sector_hint` to `data/raw/source=procurement/country=AT/date=<YYYY-MM-DD>/tenders.csv`, then run `make normalize-all COUNTRY=AT` and rebuild.