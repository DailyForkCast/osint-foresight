---
title: "Austria — Phase 3: Institutional Map & Accredited Labs"
author: OSINT Foresight (solo analyst)
date: 2025-09-07
---

## Scope & Inputs
- **Country / ISO2:** Austria (AT) · **Years:** 2015–2025 · **Languages:** en, de · **Looser matchers:** ON
- **Primary files (if present):** `data/processed/country=AT/standards_roles.tsv`, `relationships.csv`, optional `AccreditedLabs.tsv`, `institutions.csv`, `cer_master.csv`.
- **Guardrails:** Neutral tone; *signals ≠ proof*. **Exclude US persons** from any sanctions/legal mentions. **MCF detection is label‑independent** (function‑over‑label); if asserting MCF relevance, cite annex/ECCN or mark **"unclear."**

## Data presence
- institutions.csv: no
- relationships.csv: yes (rows=12)
- standards_roles.tsv: yes (rows=2)
- cer_master.csv: no
- AccreditedLabs.tsv: no

---

## What counts as an "Institution" here
We include **government/regulators**, **accreditation & metrology**, **universities & RTOs**, **accredited labs (17025/17020)**, **product/system cert bodies (17065/17021‑1)**, and **standards participants** (IETF/ETSI/ISO/IEC). Private firms appear when they hold **relevant accreditations** or play a central role in standards/testbeds.

---

## A) National System Map (starter, to verify as we collect evidence)

| layer | exemplar entities (to verify) | role in ecosystem | evidence hook |
|---|---|---|---|
| Government & funding | (e.g., Ministry of Labour & Economy; FFG; FWF; aws) | Policy & funding programs (Phase 4); export/FDI screen | Program portals; legal gazettes |
| Accreditation | Akkreditierung Austria | Accredits labs/cert/inspection (17025/17020/17065/17021‑1/15189/17043/17034) | National registry page, scopes PDFs |
| Metrology | (e.g., BEV metrology functions) | Time/frequency, dimensional, electrical standards | Metrology pages; calibration scope references |
| RTOs & labs | (e.g., AIT Austrian Institute of Technology) | Applied research; test facilities; standards links | Facility pages; accreditation scopes |
| Universities | (e.g., TU Wien, TU Graz, JKU Linz, ISTA) | Academic research; standards authorship; HPC users | Dept pages; IETF/ETSI rosters; VSC references |
| Standards bodies | IETF/ETSI/ISO/IEC (AT participants) | Roles in IPPM/NTP/RED/etc. | `standards_roles.tsv`; rosters |

> **Note:** Items in parentheses are **candidates to verify**—record as evidence only once a source is captured in the Evidence Register.

---

## B) Accredited Bodies (signals of real capability)
Capture from the national registry by **standard** and **technical field**. Primary targets for dual‑use relevance:
- **ISO/IEC 17025 (Testing & Calibration):** EMC/RED, RF/microwave, time & frequency/GNSS, optics/photonics, radiation, dimensional/electrical/thermal.
- **ISO/IEC 17020 (Inspection):** NDT (UT/RT/MT/PT/ET), pressure vessels, AM parts.
- **ISO/IEC 17065 (Product certification):** radio/EMC, machinery, cyber/IT products (where present).
- **ISO/IEC 17021‑1 (Management systems):** include 27001 cert bodies only when useful as **signals** of cyber maturity.
- **ISO 15189 / ISO/IEC 17043 / ISO 17034:** optional but **high‑signal** for biotech and metrology strength.

### Accredited Labs (top 10)
| Name | Accreditation ID | Scope | City |
|---|---|---|---|
| (To be captured) | – | EMC/RED testing | – |
| (To be captured) | – | Time & frequency cal | – |
| (To be captured) | – | RF/microwave | – |
| (To be captured) | – | GNSS testing | – |
| (To be captured) | – | Photonics/optics | – |
| (To be captured) | – | NDT inspection | – |
| (To be captured) | – | AM parts testing | – |
| (To be captured) | – | Dimensional cal | – |
| (To be captured) | – | Electrical cal | – |
| (To be captured) | – | Thermal testing | – |

---

## C) Institutional Map (counts by type)
| Org type | Count | Examples |
|---|---:|---|
| Universities | 2+ | TU Wien (IETF participant), ISTA (AI research) |
| RTOs | TBD | AIT Austrian Institute of Technology (candidate) |
| Standards participants | 1 | TU Wien (IETF IPPM/NTP) |
| Government/funding | TBD | FFG, FWF, aws (candidates) |
| Accreditation bodies | 1 | Akkreditierung Austria |
| Labs (17025) | TBD | To be captured from registry |
| Cert bodies (17065) | TBD | To be captured from registry |
| Inspection (17020) | TBD | To be captured from registry |

---

## D) Standards‑linked Organizations (from existing data)
| WG/SDO | Role | Person | Organization | Sector hint |
|---|---|---|---|---|
| IPPM | author | Joachim Fabini | TU Wien (Vienna University of Technology) | Communications/Networking |
| NTP | author | Joachim Fabini | TU Wien (Vienna University of Technology) | Time Sync/Networking |

---

## E) Relationship Coverage (top counterparts in Phase‑2 edges)
| Organization (normalized) | Edge count | Type |
|---|---:|---|
| Carnegie Mellon University | 1 | AI co-publication |
| EuroCC Slovenia (SLING) | 1 | HPC co-project |
| EuroHPC LEONARDO | 1 | HPC infrastructure |
| imec | 1 | AI co-publication |
| Max Planck Institute (Tübingen) | 1 | AI co-publication |
| Neural Magic | 1 | AI co-publication |
| University of Chicago | 1 | AI co-publication |
| University of Oxford | 1 | AI co-project |
| University of Texas at Austin | 1 | AI co-publication |
| University of Tübingen | 1 | AI co-publication |
| VIB-NERF | 1 | AI co-publication |
| Vienna Scientific Cluster (VSC) | 1 | HPC infrastructure |

---

## F) Capability Heat (qualitative, 0–3)
Score **by cluster** using combined signals from accreditation scopes, standards roles, facilities, and relationships.

| cluster_id | name | capability_0_3 | rationale | supporting_refs |
|---|---|---:|---|---|
| C1 | AI/ML & Autonomy | 2 | VSC/EuroHPC access; national AI initiative; conf links | [VSCrunchy_2024, ICLR_2024_Vienna] |
| C2 | High‑Performance Computing | 3 | VSC established; EuroHPC links | [VSC_upgrade, EuroHPC_node] |
| C3 | Comms/Networking & Timing | 2 | IETF authorship; likely test labs | [IPPM_role, NTP_role] |
| C4 | Sensing & PNT | 1 | Expect time&freq/GNSS scopes; need evidence | [Accreditation_scrape_todo] |
| C5 | Advanced Manufacturing & Materials | 1 | Expect NDT/AM inspection scopes | [17020_scrape_todo] |
| C6 | Semiconductors & Electronics | 1 | Expect EMC/RED labs | [EMC_scope_todo] |
| C7 | Space/EO Interfaces | 1 | Likely research interfaces; need evidence | [EO_links_todo] |
| C8 | Cybersecurity & Safety‑Critical SW | 1 | 27001 signals; safety SW pockets | [27001_bodies] |

> **Note:** Adjust scores as evidence lands. Keep rationales short and cite **IDs** from the Evidence Register.

---

## G) CER‑lite Snapshot
| Canonical entities | Ambiguous entities |
|---:|---:|
| 12 | 0 |

---

## H) Lay Narrative (who the players are & why it matters)
Austria's **institutional backbone** for dual‑use‑relevant technologies appears to center on: the **national HPC facility (VSC)** and its university users; **standards participants** in **networking/timing**; and an expected spread of **accredited laboratories** covering **EMC/RED, RF/microwave, time & frequency/GNSS, photonics**, and **industrial NDT/AM**. As the accreditation scopes are captured, we will elevate labs and RTOs with **demonstrated bench capabilities** and link them to **clusters/subdomains** from Phase X. Funding bodies and ministries provide programmatic context for capabilities growth (to be mapped in Phase 4). The **accreditation registry** is the most direct, low‑cost route to verifying **real test capacity**—far stronger than marketing claims.

**MCF‑consistent angle (label‑independent).** Where patterns combine **sensitive scopes** (e.g., time/frequency calibration, RF/microwave), **international standards roles**, and **cross‑border projects**, we will flag **MCF‑consistent signals** and carry them forward to Phases 5–7C for deeper scrutiny—**without** inferring intent.

---

## I) Sanctions/Legal Overlay (signals‑only; **non‑US persons**)
If any accredited bodies or parent companies appear on EU/UK/CA/AU/NZ/UN lists, record as **signals only** in `sanctions_hits.csv` with explicit source links and dates. Do **not** include US persons.

---

## 3–5 Bullet Executive Summary
- **Backbone:** VSC + university users; standards roles in networking/timing; accreditation to confirm capabilities in EMC/GNSS/NDT/AM.
- **Why accreditation matters:** Scopes reveal **actual test methods & equipment**, enabling precise cluster/subdomain mapping.
- **Next fastest lifts:** Capture 10–20 accreditation scopes in high‑signal fields (EMC/RED; time & frequency/GNSS) and seed **Institutions**.
- **MCF‑consistent patterns:** Use multi‑anchor evidence (scopes + standards roles + partnerships) and defer determinations to Phases 6–7C.
- **Phase‑2 edges include identifiable institutions:** Use CER‑lite to improve naming and entity resolution.

---

## Next Data Boost (1 step)
Scrape/capture **EMC/RED** and **time & frequency/GNSS** scopes first; write to `AccreditedLabs.tsv`, hash PDFs, and add entries to the Evidence Register. Then enrich **institutions.csv** with those labs and re‑score **capability_heat.tsv`. Alternatively, add `data/raw/source=accreditation/country=AT/date=<YYYY-MM-DD>/labs.csv` with header:

```
name,country,accreditation_id,scope,city,is_lab
```

Then run `make normalize-all COUNTRY=AT` and rebuild.