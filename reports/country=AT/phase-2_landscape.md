---
title: "Phase 2 — Technology Landscape & Maturity (Austria)"
author: Analyst
date: "2025-09-06"
---

## Overview
Sector intensity, momentum, standards posture, and notable event spikes for Austria (AT), **2015–2025**. *Looser matchers ON.*

### Sources used (high‑confidence)
- **IETF Datatracker / RFC‑Editor** for Austrian standards authorship (TU Wien, IPPM/NTP). citeturn0search0turn0search5turn0search11
- **ICLR 2024 (Vienna) official site / press** for venue and dates. citeturn0search2turn0search7turn0search17
- **EuroHPC / University of Vienna / VSC** for HPC infrastructure access and EuroHPC Leonardo context. citeturn1search2turn0search4turn0search14
- **ASHPC24 (Austrian‑Slovenian HPC Meeting)** for the *VSCrunchy* inauguration program on 11 June 2024. citeturn0search8turn0search13
- **NeurIPS proceedings / program pages** for ISTA & TU Wien collaborations (2022–2024). citeturn1search6turn1search0turn1search4
- **Austrian funding signals**: FFG *Digital Technologies 2023* kickoff; **AI Mission Austria** (aws+FFG+FWF). citeturn2search0turn2search1

---

## Sector Scorecard (computed from evidence below)
| Sector | Intensity (0–3) | Momentum (15–18 / 19–22 / 23–25) | Top counterpart(s) | Consortium skew? |
|---|---:|---|---|---|
| High‑Performance Computing | 3 | 0 / 0 / 3 | EuroHPC LEONARDO; EuroCC Slovenia (SLING) | No |
| AI | 3 | 0 / 1 / 8 | Univ. of Tübingen; UT Austin / CMU / UChicago | No |

**How to read:** Intensity is relative within AT (quartiles over non‑zero sectors). Momentum shows edge counts across year buckets.

---

## Standards Posture (sample evidence)
- **RFC 9198 (IPPM / AURA)** lists *J. Fabini (TU Wien)* as co‑author (Standards Track), showing Austrian participation in IETF IP performance metrics work. citeturn0search0turn0search10
- **NTP packet timestamps** work (Internet‑Draft lineage to RFC 8877) includes *Joachim Fabini* as co‑author, indicating Austrian engagement in time‑sync protocol guidance. citeturn0search1

**Append‑ready `standards_roles.tsv` (add if not present):**
```
wg	role	person_name	org_name	country	sector_hint
IPPM	author	Joachim Fabini	TU Wien (Vienna University of Technology)	AT	Communications/Networking
NTP	author	Joachim Fabini	TU Wien (Vienna University of Technology)	AT	Time Sync/Networking
```

---

## Event Spikes (signals)
| Window | Signal summary | Likely driver |
|---|---|---|
| 2024-06 | Inauguration of Austria's new supercomputer "VSCrunchy" at **ASHPC24** (Grundlsee) | HPC capacity upgrade & community event. citeturn0search8turn0search13 |
| 2024-05 | **ICLR 2024** hosted in Vienna (Messe Wien) | International AI community presence & visibility. citeturn0search2turn0search7 |
| 2023-12 | **FFG "Digital Technologies 2023"** kickoff event | National digital‑tech funding momentum. citeturn2search0 |
| 2022-11 | **AI Mission Austria** (aws+FFG+FWF) announced | Coordinated AI funding pipeline. citeturn2search1 |

**Append‑ready `signals.csv` (add or upsert):**
```
window,signal_summary,likely_driver
2024-06,Inauguration of "VSCrunchy" supercomputer at ASHPC24 (Austria-Slovenia HPC meeting),HPC capacity upgrade (VSC)
2024-05,ICLR 2024 hosted in Vienna (Austria),International AI community presence
2023-12,FFG "Digital Technologies 2023" call kick-off event,National digital tech funding momentum
2022-11,AI Mission Austria joint initiative (aws+FFG+FWF) announced,Strategic AI funding coordination
```

---

## Collaboration Edges (relationships)
**High‑Performance Computing**
- Austrian user access and support for **EuroHPC Leonardo** (CINECA, Bologna) explicitly mentioned by Univ. of Vienna/VSC; EuroHPC confirms Leonardo location and role. citeturn1search2turn0search4
- Regional collaboration visible via **ASHPC24** (Austria–Slovenia HPC) and the joint EuroCC ecosystem. citeturn0search3

**Artificial Intelligence (conference‑driven edges)**
- **NeurIPS 2024 paper** lists **Francesco Locatello (ISTA)** with **UT Austin, CMU, UChicago** co‑authors. citeturn1search6turn1search0
- **NeurIPS 2023 competition (ROAD‑R)** lists **TU Wien** with **University of Oxford** collaborators among organizers/authors. citeturn1search4
- **NeurIPS 2023/2022**: ISTA co‑authorships with **Univ. of Tübingen**, **Max Planck (Tübingen)**, **VIB‑NERF**, **imec** (see proceedings & author pages). citeturn1search6

**Append‑ready `relationships.csv` (add or upsert):**
```
sector,counterpart_name,counterpart_country,collab_type,year
High-Performance Computing,EuroHPC LEONARDO,IT,infrastructure,2024
High-Performance Computing,EuroCC Slovenia (SLING),SI,co-project,2024
High-Performance Computing,Vienna Scientific Cluster (VSC),AT,infrastructure,2024
AI,University of Tübingen,DE,co-publication,2023
AI,Max Planck Institute (Tübingen),DE,co-publication,2023
AI,VIB-NERF,BE,co-publication,2023
AI,imec,BE,co-publication,2023
AI,Neural Magic,US,co-publication,2022
AI,University of Oxford,GB,co-project (competition),2023
AI,University of Texas at Austin,US,co-publication,2024
AI,Carnegie Mellon University,US,co-publication,2024
AI,University of Chicago,US,co-publication,2024
```

---

## Narrative Snapshot
- **HPC** shows sustained activity and **current momentum** tied to VSC upgrades and EuroHPC **Leonardo** access/support; linkages to **EuroCC Slovenia (SLING)** signal regional capability sharing rather than single‑vendor dependence. citeturn0search8turn1search2
- **AI** intensity is broad‑based across academic collaborations (ISTA, TU Wien) with strong 2023–2024 co‑authorships into **DE/BE/GB/US** institutions (Tübingen, Max Planck, VIB‑NERF/imec, Oxford, UT Austin/CMU/UChicago). citeturn1search6turn1search4
- **Standards posture**: TU Wien authorship in **IPPM** and **NTP** lines of work provides concrete, citable evidence of Austrian participation in IETF transport/performance topics. citeturn0search0turn0search1

## Caveats
- Conference‑based edges can overweight a few labs; apply CER‑lite before ranking partners (Phase 5) to reduce duplicate names and verify org identities.
- The relationships above are a minimal **evidence seed**; add CORDIS participants or additional conference slices to improve coverage.

## Next Data Boost (1 actionable)
Add **CORDIS participants (2015–2025)** for AT projects to `data/raw/source=cordis/country=AT/date=<YYYY-MM-DD>/participants.csv` and re‑run normalization; this will expand domestic/foreign edges beyond conferences and HPC.