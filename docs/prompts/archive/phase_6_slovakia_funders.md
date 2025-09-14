# Phase X – Slovakia (Phase 4)

**Goal:** Convert Phase 2–3 evidence into risk scoring, prioritization, and recommended mitigations. ChatGPT-only content (no external code blocks). Timeframe: 2015–present; focus: batteries/electro‑chemistry, AI & cyber, microelectronics; cross‑cutting: PRC vectors, Horizon EU pipelines, export controls.

---

## 1) Scoring framework

**Dimensions (per actor/link):**
- **L (Likelihood)**: probability of undesirable outcome within 24–36 months (0–5).
- **I (Impact)**: severity on EU/ally research integrity, security, or supply chains (0–5).
- **E (Exposure)**: degree of foreign leverage, data/IP access, or export‑control sensitivity (0–5).
- **C (Confidence)**: evidence strength (Low/Med/High).

**Overall Risk Score (ORS)** = `((L + I + E)/3) × Confidence weight`, where **High=1.0**, **Med=0.8**, **Low=0.6**.

**Qualitative bands:**
- 0–1.4: Low
- 1.5–2.9: Medium
- 3.0–3.9: Elevated
- 4.0–5.0: High

**Mapping to mitigations:**
- **High/Elevated:** immediate due‑diligence, licencing/FDI screening, data minimization, contract re‑papering.
- **Medium:** monitoring, targeted clauses, supplier diversification.
- **Low:** watchlist only.

---

## 2) Risk scoring – priority clusters

> Evidence IDs refer to Phase 2 (**EV‑SK‑…**) and Phase 3 (**EV‑COL‑…**) tables.

### 2.1 Batteries & electro‑chemistry

**A) Gotion–InoBat Batteries (GIB) JV (EV‑SK‑0001/0002/0038/0039; EV‑COL‑0001/0002/0020)**
- L=4 (project financing & state‑aid secured; production target 2027).
- I=4 (20 GWh capacity; strategic for EU automotive/ESS; potential leverage over supply).
- E=5 (PRC parent tech/capital; possible equipment suppliers with export‑control touchpoints).
- C=High.
- **ORS ≈ 4.3 → High.**
**Key concerns:** tech transfer & JV governance; supplier list (formation, coating, BMS); downstream licensing (EV‑SK‑0022; EV‑COL‑0020).
**Mitigations:** golden‑share/negative‑control clauses; EU investment screening; supplier red‑flag list; dual‑use classification audit for cell chemistries & BMS; source‑code escrow for BMS.

**B) InoBat E10 UAV cell (EV‑SK‑0003/0012/0037)**
- L=4; I=3; E=4; C=Med–High → **ORS ≈ 3.5 (Elevated).**
**Concerns:** clear dual‑use; export/licence pathway; customer vetting.
**Mitigations:** 0Y/3A/5A mapping; end‑use screening; NATO‑centric distribution; technical data controls.

### 2.2 AI & cyber

**C) ESET ecosystem & campus build (EV‑SK‑0020/0033/0034; EV‑COL‑0008/0024)**
- L=3; I=4 (telemetry & threat‑intel can touch critical sectors under NIS2); E=3; C=Med → **ORS ≈ 2.9 (Medium).**
**Concerns:** third‑country data access; model/telemetry handling; supply‑chain software risk.
**Mitigations:** data minimization & regionalization; vendor SBOM; red‑team audits aligned to NIS2; export‑controlled tool screening.

**D) Photoneo → Zebra acquisition (EV‑SK‑0016/0026/0027/0028; EV‑COL‑0004/0014/0015)**
- L=3; I=3 (3D sensors, warehouse robotics across logistics & automotive); E=3 (foreign ownership); C=Med → **ORS ≈ 2.4 (Medium).**
**Mitigations:** tech‑transfer guardrails; customer screening in sensitive sectors; export‑classification check for sensors.

### 2.3 Microelectronics & components

**E) IPCEI ME/CT participation (EV‑SK‑0010/0011/0023/0024/0032; EV‑COL‑0022/0023)**
- L=3; I=4 (strategic chips/components pipelines); E=3; C=Med → **ORS ≈ 2.9 (Medium).**
**Mitigations:** partner vetting; third‑country dependency mapping; IP & background‑foreground delineation in grants.

**F) SPINEA (Timken) precision reducers (EV‑SK‑0017/0029; EV‑COL‑0005)**
- L=2; I=3; E=2; C=High → **ORS ≈ 1.9 (Medium‑Low).**
**Mitigations:** export screening for defence end‑users; monitor CN distribution channels.

**G) EVPÚ defence electronics exports (EV‑SK‑0019/0036; EV‑COL‑0012/0019/0026)**
- L=3; I=3; E=3; C=Med → **ORS ≈ 2.4 (Medium).**
**Mitigations:** enhanced end‑use checks; EO/test equipment export‑control review; sanctions screening.

---

## 3) Vulnerability map (country‑level)

- **Ownership/FDI leverage:** High in **battery JV**; Medium in **AI/robotics** via foreign acquisitions; Low–Medium in microelectronics via multi‑country projects.
- **Export‑control exposure:** Elevated for **UAV batteries**, defence electronics; Medium for 3D sensors, precision reducers; baseline for software (crypto/dual‑use modules) under NIS2.
- **Data/telemetry risk:** Medium in **cyber** (ESET ecosystem) absent strict data localization & access controls.
- **Academic collaborations:** Pockets of **CN co‑authorship** (physics/quantum) warrant monitoring but currently moderate scale.

---

## 4) Priority mitigations & actions (12–18 months)

### 4.1 Country‑level
- Stand‑up **battery JV oversight taskforce** (economy + foreign affairs + defence + NBU) to review governance, supplier list, and data/IP clauses (quarterly).
- Expand **FDI screening playbook** for JV equipment vendors; require disclosure of sub‑suppliers and maintenance access rights.
- Launch **NIS2 + export‑controls convergence guidance** for Slovak firms handling telemetry, AI models, or defence‑adjacent hardware.

### 4.2 Programme/consortium level
- In IPCEI/Horizon contracts, mandate **third‑country dependency statements** and **IP segregation** (background vs foreground) with audit rights.
- For AI/robotics acquisitions, require **tech‑transfer registers** and **off‑EU access approvals** for repositories and design files.

### 4.3 Entity‑specific
- **GIB JV:** independent audit of BMS/code escrow; supplier country‑of‑origin mapping; add **change‑of‑control vetoes**; create export‑licence playbook.
- **InoBat (UAV):** product export‑classification and end‑use due diligence; NATO‑aligned distribution only; register of UAS customers.
- **ESET:** regional data processing with **access transparency**, SBOM for endpoint/EDR components, targeted third‑party code reviews.
- **Photoneo (Zebra):** sensitive‑sector customer KYC; export controls on 3D sensors; EU site residency for model/data repos.
- **EVPÚ/SPINEA/MSM:** enhanced screening for end‑users in high‑risk jurisdictions; periodic sanctions re‑checks.

---

## 5) Early‑Warning Indicators (operationalized)

- **Ownership:** filings indicating equity changes or new SPVs around GIB/InoBat; equipment procurement contracts referencing PRC vendors.
- **Collab:** new MoUs with CN institutions in batteries/AI; sudden participation spikes in sensitive Horizon topics by small Slovak actors.
- **Trade/IP:** increases in CN co‑assigned patents with Slovak assignees in target domains; licensing announcements involving GIB tech.
- **Compliance:** NIS2 incident trends in covered Slovak sectors; public notices of export‑licence denials/queries.

---

## 6) Watchlist (living)

- **High Priority:** GIB JV (battery gigafactory & supply chain); InoBat UAV battery line.
- **Medium:** ESET ecosystem; Photoneo (post‑acquisition integration); EVPÚ exports; IPCEI ME/CT Slovak participants.
- **Background:** SPINEA (Timken) distribution to APAC; university labs with CN co‑authorships.

---

## 7) Handoff to Phase 5

- Generate a **one‑page risk heatmap** (per cluster/entity) using ORS bands.
- Prepare **policy & engagement recommendations** tailored to Slovak interlocutors (economy, defence, HEI leadership, regulators).
- Deliver **source package** linking back to EV‑SK and EV‑COL rows; flag gaps for targeted pulls (procurement IDs, supplier lists, patent family details).
