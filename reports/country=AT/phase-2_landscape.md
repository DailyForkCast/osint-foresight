---
title: "Phase 2 — Technology Landscape & Maturity (Austria)"
author: Analyst
date: "<AUTO>"
---

## Overview
Sector intensity, momentum, standards posture, and notable event spikes for Austria (AT), **2015–2025**. *Looser matchers ON.*

### Data presence
- relationships.csv: yes (rows=12)
- standards_roles.tsv: yes (rows=2)
- signals.csv: yes (rows=6)
- partners_cerlite.csv: no

---

## Sector Scorecard
| Sector | Intensity (0–3) | Momentum (15–18 / 19–22 / 23–25) | Top counterpart(s) | Consortium skew? |
|---|---:|---|---|---|
| AI | 3 | 0 / 1 / 8 | Carnegie Mellon University, Max Planck Institute (Tübingen) | No |
| High-Performance Computing | 1 | 0 / 0 / 3 | EuroCC Slovenia (SLING), EuroHPC LEONARDO | No |

**Notes:** Intensity is relative within AT; 0 = no edges, 1–3 = quartile buckets among non‑zero sectors.

---

## Standards Posture
| WG / SDO | Role | Person | Organization |
|---|---|---|---|
| IPPM | author | Joachim Fabini | TU Wien (Vienna University of Technology) |
| NTP | author | Joachim Fabini | TU Wien (Vienna University of Technology) |

---

## Event Spikes
| Window | Signal summary | Likely driver |
|---|---|---|
| 2024-06 | Inauguration of "VSCrunchy" supercomputer at ASHPC24 (Austria-Slovenia HPC meeting) | HPC capacity upgrade (VSC) |
| 2023-12 | FFG "Digital Technologies 2023" call kick-off event | National digital tech funding momentum |
| 2022-11 | AI Mission Austria joint initiative (aws+FFG+FWF) announced | Strategic AI funding coordination |
| 2024-05 | ICLR 2024 hosted in Vienna (Austria) | International AI community presence |
| 2023-12 | TU Wien visible at NeurIPS 2023 (competition track) | Benchmarking & methods community presence |

---

## Narrative Snapshot
- **AI** shows intensity 3 with momentum 0/1/8. Top counterpart: Carnegie Mellon University, Max Planck Institute (Tübingen).
- **High-Performance Computing** shows intensity 1 with momentum 0/0/3. Top counterpart: EuroCC Slovenia (SLING), EuroHPC LEONARDO.

## Caveats
- Looser matchers can over‑include adjacent subfields; review outliers in Phase 5.
- Edges aggregate heterogeneous collaboration types; mechanism details live in Phase 5.

## Next Data Boost
Add a **CORDIS participants** slice for AT (2015–2025) to `data/raw/source=cordis/country=AT/date=<YYYY-MM-DD>/participants.csv`, then run `make normalize-all COUNTRY=AT` and rebuild.
