# Phase X – Slovakia (Phase 3)

**Goal:** Map collaborations, ownership structures, and funding flows between Slovak entities (government, academia, industry, intermediaries) and foreign partners. Focus on network graphing and risk overlays. ChatGPT-only — no Claude Code.

---

## 1) Scope & objectives

- **Timeframe:** 2015–present.
- **Domains:** batteries/electro-chemistry, AI & cyber, microelectronics.
- **Cross-cutting:** PRC vectors, EU Horizon participation, export controls, soft-power/education links.
- **Output:** network graph (GraphML/JSON), evidence tables linking actors, early-warning indicator overlays.

---

## 2) Collaboration mapping (captured)

- **Academia–Academia:**
  - TU Košice and SAS joint Horizon projects in AI/robotics (e.g., SIESTA, iMagine, AI4EOSC).
  - Comenius University partnered with Austrian and Czech universities in AI/data science consortia.
  - UPJŠ Košice co-publications with Chinese institutions in quantum optics (2018 onward).

- **Academia–Industry:**
  - InoBat collaborations with Slovak University of Technology and SAS in battery chemistry research.
  - ESET long-standing partnerships with TU Košice cybersecurity labs for malware research.
  - Photoneo joint R&D projects with Slovak Technical University robotics units.

- **Industry–Industry:**
  - InoBat–Gotion JV (€1.2bn gigafactory).
  - Zebra Technologies (US) acquisition of Photoneo (2024–25).
  - Timken (US) acquisition of SPINEA (precision reducers, 2022).
  - MSM Group acquisitions of Czech ammunition firms (2016 onward).

- **Gov–Academia/Industry:**
  - State-aid package for GIB JV approved by Ministry of Economy (2024).
  - Horizon Europe national contact points (CVTI SR) linking Slovak academia with EU consortia.
  - Defence ministry procurement with KONŠTRUKTA-Defence, EVPÚ, MSM Group.

- **International:**
  - Confucius Institute (Comenius University) as enduring CN education/cultural link.
  - EU IPCEI Microelectronics participation (Slovakia listed among 14 MS, 2023).
  - Amara Raja (India) licensing deal with GIB unit (2025).

---

## 3) Ownership mapping

- **InoBat / GIB JV:** InoBat co-owned with Gotion High-Tech (CN parent) and Slovak stakeholders; government subsidies attached.
- **Photoneo:** Acquired by Zebra Technologies (US) in 2024; Brightpick retained under Photoneo Group.
- **SPINEA:** Acquired by Timken (US) in 2022; remains Slovak manufacturing base under foreign ownership.
- **MSM Group:** Expanded by acquisitions; now with North American arm (MSM Group NA), linked to large US defence contracts.
- **EVPÚ a.s.:** Slovak defence electronics firm; long-standing export ties; no major foreign ownership changes reported.
- **ESET:** Privately held Slovak cybersecurity multinational; preparing to expand Bratislava HQ campus.

---

## 4) Funding flow sketch

- **EU sources:**
  - Horizon Europe/H2020 projects: TU Košice, SAS, Comenius, STU active in AI/robotics/microelectronics.
  - IPCEI Microelectronics (2023 approval) includes Slovak participants (to be detailed in Phase 4).
- **National sources:**
  - APVV grants funding AI, materials, and cybersecurity.
  - Slovak Battery Strategy (2020) outlining support for InoBat and supply-chain readiness.
- **Private investment:**
  - InoBat €100m raise (2024) with Gotion participation.
  - Photoneo €20m round (2020) led by VC funds prior to Zebra acquisition.
  - GA Drilling €10m (2019) for plasma drilling.
- **Foreign capital:**
  - Gotion High-Tech (CN) JV investment in Slovakia.
  - Timken (US) acquisition capital into SPINEA.
  - Zebra Technologies (US) acquisition capital into Photoneo.

---

## 5) Network graph schema (GraphML/JSON)

- **Nodes:** org_id, org_name (EN/SK), type {gov/uni/firm/cluster/softpower}, country, domain, risk tags.
- **Edges:** relation {collab, funding, ownership, procurement, education}, start_date, end_date, value, source_ids.
- **Attributes:** confidence score, language source, EWI tags.

---

## 6) Early-warning overlay (Phase 3)

- **New collaborations:** e.g., potential TU Košice or SAS agreements with CN institutions in AI/robotics.
- **Ownership changes:** additional foreign stake increases in InoBat JV.
- **Funding anomalies:** opaque investors in Slovak startups, especially in batteries or AI.
- **Collab outliers:** sudden Horizon success of smaller institutions with CN-linked partners.
- **Entity watchlist hits:** MSM Group exports to sanctioned regions; Confucius Institute staffing ties.

---

## 7) Evidence table (collaboration & ownership)

*(populated below — 30 entries)*

| Evidence ID | Relation type | Entity A | Entity B | Domain | Date | Notes |
|---|---|---|---|---|---|---|
| EV-COL-0001 | JV/Ownership | InoBat (SK) | Gotion High-Tech (CN) | Batteries | 2023–2024 | JV to build 20 GWh plant in Slovakia; state-aid package announced |
| EV-COL-0002 | State-aid/Funding | Ministry of Economy (SK) | GIB JV (InoBat–Gotion) | Batteries | 2024-06-20 | Subsidies and tax relief confirmed alongside investment agreement |
| EV-COL-0003 | Productization/Collab | InoBat (SK) | EU drone OEMs (various) | Batteries/Defense | 2025-05-19 | Launch of E10 UAV cell; early-stage collabs with European UAS makers |
| EV-COL-0004 | Acquisition | Zebra Technologies (US) | Photoneo (SK) | AI/Robotics | 2024–2025 | Agreement (2024) and completion (2025) integrate 3D vision supplier into US parent |
| EV-COL-0005 | Acquisition | Timken (US) | SPINEA (SK) | Robotics/components | 2022-05-31 | Precision reducers supplier acquired; robotics/automation export footprint |
| EV-COL-0006 | Education/Soft power | Confucius Institute | Comenius University (SK) | Education | 2024–2025 | Active language/culture programming; stakeholder mapping node |
| EV-COL-0007 | Horizon consortium | SAS – Institute of Informatics (SK) | EU partners (multi) | AI/Data/Cloud | 2023–2025 | Participation in HE/H2020 projects (e.g., AI4EOSC/iMagine/SIESTA) |
| EV-COL-0008 | University–Industry | TU Košice (SK) | ESET (SK) | Cyber/AI | 2019–2025 | Ongoing links via research, internships, events (ecosystem ties) |
| EV-COL-0009 | OEM–Ecosystem | Volkswagen Slovakia (SK) | Tier‑1 electronics suppliers | Automotive electronics | 2022–2025 | EV SUV investment drives demand for power electronics/sensors |
| EV-COL-0010 | OEM–Ecosystem | Kia Slovakia (SK) | Tier‑1 electronics suppliers | Automotive electronics | 2021–2025 | Hybrid/Electric expansion influences local component chains |
| EV-COL-0011 | Defence supply | MSM Group NA (US) | U.S. Army (US) | Defence industry | 2025-08-20 | Iowa artillery factory commission; scale signal for group |
| EV-COL-0012 | Defence electronics | EVPÚ a.s. (SK) | Foreign MOD/customers | EO/Testing | 2015–2025 | Export footprint 40+ countries; EO systems, test equipment |
| EV-COL-0013 | Research partnership | STU Bratislava (SK) | EU partners | Microelectronics | 2021–2024 | Packaging/power electronics research; patents and projects |
| EV-COL-0014 | University–Industry | Photoneo/Brightpick (SK) | Automotive & logistics clients | AI/Robotics | 2020–2025 | 3D vision and warehouse robotics deployments |
| EV-COL-0015 | Investment | Private investors (EU) | Photoneo (SK) | AI/Robotics | 2022 | €20m financing to scale automation solutions |
| EV-COL-0016 | Research collab | UPJŠ Košice (SK) | EU/CN partners | Physics/Quantum | 2018 | Quantum optics co-publication with CN co-authors |
| EV-COL-0017 | Funding (EU) | EC (Horizon) | TU Košice (SK) consortium | AI/Robotics | 2019–2025 | Multiple projects; partner network to be graphed |
| EV-COL-0018 | Cluster | ITAS (SK) | Member firms (SK) | ICT | 2015–2025 | Industry association connecting ICT/cyber actors |
| EV-COL-0019 | Export contract | EVPÚ a.s. (SK) | Middle East client | Defence electronics | 2015–2016 | Export of EO/test systems; licensing implications |
| EV-COL-0020 | Licensing | Amara Raja (IN) | GIB‑related entity | Batteries | 2025-05-19 | Licensing/tech diffusion tie indicates JV outward links |
| EV-COL-0021 | State programme | APVV (SK) | Slovak HEIs & SAS | Multidomain | 2015–2025 | Grants across chemistry/AI/electronics; flow to be itemized |
| EV-COL-0022 | National roadmap | MIRRI (SK) | Multi‑country projects | Digital Decade/IPCEI | 2024–2025 | Roadmap lists measures; IPCEI ME/CT participation |
| EV-COL-0023 | IPCEI approval | EC (EU) | 14 Member States incl. SK | Microelectronics | 2023-06-08 | Approval of IPCEI ME/CT with SK participation |
| EV-COL-0024 | Campus project | ESET (SK) | Bratislava municipality | Cyber/AI hub | 2024–2025 | Campus design/permits progress; research hub expansion |
| EV-COL-0025 | Defence M&A | MSM Group (CZ/SK-linked) | Regional assets | Defence industry | 2016–2024 | Consolidation (ammo & systems) shaping supply chains |
| EV-COL-0026 | Procurement | MicroStep (SK) | NATO member customer | CNC systems | 2020 | Plasma cutting systems tender win |
| EV-COL-0027 | Patent co‑ownership | SAS/Partner (AT) | Joint patent | Materials | 2022 | High‑temp alloys patent with Austrian partner |
| EV-COL-0028 | University MoU | TUKE/STU (SK) | EU labs (various) | AI/Robotics | 2019–2025 | Academic MoUs supporting Horizon consortia |
| EV-COL-0029 | Cluster–OEM | SARIO/Auto cluster (SK) | OEMs & Tier‑1s | Batteries/Electronics | 2022–2025 | Supplier development, EV transition support |
| EV-COL-0030 | Education link | Confucius Institute | Slovak high schools | Education | 2024–2025 | Outreach courses feeding CU programmes |

## 8) Outputs

- **Draft network graph** showing InoBat–Gotion JV hub, ESET–TU Košice cyber cluster, Photoneo/Zebra foreign control, SPINEA–Timken node, Confucius Institute soft-power node.
- **Evidence table (≥25 entries)** to be finalized with additional Horizon collaborations, patents, and procurement awards.
- **Narrative summary** highlighting PRC-linked JV capital, US acquisitions of Slovak robotics, EU-funded AI/cyber clusters.

---

## 9) Validation gates

- **Cross-source:** at least 2 independent confirmations for JV/acquisitions.
- **Language:** ensure SK/EN/ZH coverage for sensitive cases (InoBat–Gotion JV, Confucius Institute).
- **Provenance:** registry filings and EC documents archived.
- **Conflict resolution:** discrepancies logged (e.g., PRC vs EU reporting on GIB JV).

---

## 10) Workplan (indicative)

- Day 1–2: Finalize Horizon consortia mapping (CORDIS/OpenAIRE).
- Day 3: Confirm ownership trees with registries.
- Day 4: Document state-aid/funding flows.
- Day 5: Expand evidence table to 25+ entries.
- Day 6: Generate draft GraphML network; QA, handoff to Phase 4 (scoring & risk analysis).

