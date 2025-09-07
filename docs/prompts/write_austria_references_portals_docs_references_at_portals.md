---
title: "Austria — References & Portals (Seed List)"
author: Analyst
date: "<AUTO>"
---

> Purpose: authoritative, mostly-stable sources to support narratives, verification, and optional manual data boosts. Keep this list short; expand only when a later phase needs it.

## Government & Regulators
- **Federal Chancellery (BKA)** — government strategies & press.
- **Ministry for Labour & Economy (BMAW)** — includes **Akkreditierung Austria** (national accreditation), export control/licensing.
- **Ministry for Climate Action, Environment, Energy, Mobility, Innovation & Technology (BMK)** — R&I policy, digital/space.
- **Ministry of Finance (BMF)** — customs/sanctions notices, public finance.
- **RTR** (Telecom/Media Regulator) — spectrum, 5G/6G, market data.
- **GovCERT Austria / CERT.at** — cybersecurity advisories.

## Funding & Programs
- **FFG** — Austrian Research Promotion Agency; national R&D calls & results.
- **aws** — Austria Wirtschaftsservice; innovation financing & guarantees.
- **BBG** — Federal procurement (Bundesbeschaffung) & e‑procurement portals.

## Standards & Accreditation
- **Akkreditierung Austria** (within BMAW) — ISO/IEC 17025/17020, etc.
- **Austrian Standards (ASI)** — EN/ISO adoptions, committees, ballots.

## Research, Statistics, IP
- **ÖAW** — Austrian Academy of Sciences (institutes & programs).
- **Statistics Austria** — R&D, trade, tech indicators.
- **Austrian Patent Office** — patents/trademarks; complements WIPO/EPO.
- Major university portals: **TU Wien**, **TU Graz**, **University of Vienna**, **JKU Linz** (research groups & labs).

## Trade, Logistics, Registries
- **Customs / Zollamt Österreich** — dual‑use guidance.
- **ÖBB Rail Cargo** — logistics flows/insights.
- **Firmenbuch** (company register) and **data.gv.at** (open data).

## EU/International (stable)
- **CORDIS** & **EU Funding & Tenders** — EU projects/programs.
- **Eurostat** — statistics.
- **UNCTAD** — trade & logistics indicators.
- **OpenSanctions** — consolidated sanctions data.
- **GLEIF** — LEI reference data.
- **IETF Datatracker** — standards roles & WGs.

---

## How to Use This Page
- Cite these sources in phase narratives for verification and context.
- When you have ~15 minutes, add **one** manual CSV from a relevant portal:
  - **Phase 3 (Institutions):** Akkreditierung Austria directory → accredited labs CSV.
  - **Phase 4 (Funders):** FFG call/program list → instruments CSV.
  - **Phase 2/5 (Landscape/Links):** CORDIS participants slice for Austria → co‑participation edges.

## Suggested Cadence
- **Quarterly:** Austrian Standards (ASI), FFG calls, IETF Datatracker highlights.
- **Semiannual:** RTR spectrum/market stats; national think‑tank reports.
- **Annual:** Akkreditierung Austria directory; Statistics Austria R&D/innovation statistics; Austrian Patent Office snapshot.

---

## Watchlist Entries (YAML snippet)
Paste into `queries/policy/watchlist.yaml` and adjust URLs as needed.

```yaml
- name: Akkreditierung Austria (BMAW) — accredited labs
  cadence: annual
  country: AT
  notes: ISO/IEC 17025/17020 directory; Phase 3 booster
  url: https://www.bmaw.gv.at/akkreditierung

- name: Austrian Standards (ASI) — committees & ballots
  cadence: quarterly
  country: AT
  notes: standards roles; Phase 2 narrative & Phase 5 context
  url: https://www.austrian-standards.at/

- name: FFG — national R&D calls & results
  cadence: quarterly
  country: AT
  notes: programs/instruments; Phase 4 booster
  url: https://www.ffg.at/

- name: RTR — telecom spectrum & market stats
  cadence: semiannual
  country: AT
  notes: 5G/6G/sectors; Phase 2/8 context
  url: https://www.rtr.at/

- name: Austrian Patent Office — patent search
  cadence: annual
  country: AT
  notes: complements WIPO/EPO; mechanisms; Phase 7C context
  url: https://www.patentamt.at/

- name: Statistics Austria — R&D/trade indicators
  cadence: annual
  country: AT
  notes: context charts; Phase 2/8 narrative
  url: https://www.statistik.at/

- name: GovCERT Austria / CERT.at
  cadence: monthly
  country: AT
  notes: cyber advisories; Phase 6 mitigation context
  url: https://www.cert.at/
```

---

## Notes
- This is a **seed list**. Add specific sub‑pages (directory endpoints, download links) only when a phase needs them.
- Prefer official portals and authoritative pages; keep third‑party sources as secondary context only.

