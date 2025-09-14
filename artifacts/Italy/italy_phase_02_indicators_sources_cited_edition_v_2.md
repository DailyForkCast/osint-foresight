# Italy — Phase 02 (Indicators & Sources) — CITED Edition v2
**Date:** 2025-09-13
**Mode:** INTEGRATED (artifacts + web)
**Provenance:** mixed (web|artifact)

## 1) Indicator framework
We organize indicators as **Leading / Coincident / Lagging**, mapped to the master taxonomy (Phase 00) and wired for joins via `id_registry.json` (ROR/LEI/ORCID), `alias_map.json`, CPC/IPC (patents), HS/CN (trade), CPV (procurement).

- **Leading (directional, early‑warning):**
  - **Procurement signals** by CPV in security‑relevant categories (cloud, cyber, sensors, UAV, HPC). Owner: Operator (weekly triage); Source: TED advanced search and individual notice pages [5]. Thresholds: 3‑month moving count ↑≥50% vs 12‑month median; or appearance of novel CPV clusters linked to dual‑use taxonomy.
  - **Standards role momentum** (ETSI/3GPP/ISO/IEC): net change in Italy‑affiliated rapporteur/editor seats (weighted) (see ETSI [6]; 3GPP [7]). Owner: Operator; cadence: quarterly. Thresholds: +/−2σ vs trailing eight quarters.
  - **DIANA/NATO innovation pipeline**: new Italy‑linked accelerator/test‑centre cohorts or grants [9]. Owner: Operator; cadence: monthly. Thresholds: ≥3 cohort additions in a quarter in any single domain.

- **Coincident (current state):**
  - **R&D intensity and composition** (GERD, by sector of performance, source of funds; national & NUTS2) [1]. Owner: Operator; cadence: annual refresh with Eurostat. Thresholds: benchmark to EU median and top‑quartile peers.
  - **FDI series (net inflows, BoP)** as context for exposure [2]. Owner: Operator; cadence: annual (World Bank/IMF BoP). Thresholds: >1σ changes YoY.
  - **Research outputs & projects** (OpenAIRE/CORDIS): counts and collaboration networks for Italy entities in dual‑use domains [3][4]. Owner: Operator; cadence: quarterly snapshots.

- **Lagging (structural outcomes):**
  - **Patent families** in targeted CPC subclasses (e.g., QKD, EO/ISR, MEMS sensors) (EPO Espacenet/OPS [10][11]). Owner: Operator; cadence: semi‑annual. Thresholds: Italy share vs EU average.
  - **Company‑level outcomes** (revenue, export mix, sanctions/enforcement resolutions) for flagged nodes from Phases 4–6. Owner: Operator; cadence: semi‑annual.

## 2) What exists in artifacts (quick integration)
- `phase02_indicators.json` and `metric_catalog.csv` are present. We align their fields to the above buckets and add **join‑key requirements** (`org_ror`, `person_orcid?`, `cpc`, `cpv`, `hs_cn`) plus **latency** and **owner** assignments.

## 3) Indicator specifications (examples to operationalize now)
**A. Procurement early‑warning (Leading)**
**Definition:** Count of TED notices with CPV codes \[30200000, 30230000, 30240000, 30250000, 32340000, 48800000, 48820000, 72200000\] where **Place of performance = IT**, rolling 90‑day window.
**Join keys:** `buyer_name` (alias‑resolved), `cpv`, `award_id`.
**Why it matters:** Fast, public signal of intent before delivery.
**Primary sources:** TED advanced search and individual notice detail pages [5].
**Owner/cadence:** Operator; weekly.

**B. Standards role momentum (Leading)**
**Definition:** Weighted sum of Italy‑affiliated roles per quarter: `member=1, rapporteur=3, editor=5`.
**Join keys:** `org_ror`, `person_orcid?`, `body`, `wg`.
**Primary sources:** ETSI membership queries [6]; 3GPP corporate group lists and WG election pages [7].
**Owner/cadence:** Operator; quarterly.

**C. R&D intensity & composition (Coincident)**
**Definition:** GERD levels/shares by sector of performance and funding source; national and NUTS‑2 regional.
**Join keys:** `nuts2`, `sector`.
**Primary sources:** Eurostat datasets `rd_e_gerdtot`, `rd_e_gerdfund`, `rd_e_gerdreg` [1].
**Owner/cadence:** Operator; annual.

**D. Research outputs & EU projects (Coincident)**
**Definition:** Counts of Italy‑affiliated publications/datasets/software and EU projects in target domains.
**Join keys:** `org_ror`, `project_id`, `funding_program`.
**Primary sources:** OpenAIRE Graph API (country/org filters) [3]; CORDIS SPARQL / project pages [4].
**Owner/cadence:** Operator; quarterly.

**E. FDI exposure (Coincident)**
**Definition:** Net FDI inflows (BoP, current US$) for Italy (context only).
**Primary sources:** World Bank indicator `BX.KLT.DINV.CD.WD?locations=IT` [2].
**Owner/cadence:** Operator; annual.

**F. Patents by CPC (Lagging)**
**Definition:** Families/grants in dual‑use CPCs (e.g., H04B/ H04L for QKD/crypto; G01S/G01C for EO/ISR).
**Primary sources:** EPO Espacenet/OPS [10][11] (exact CPC queries to be scripted by Claude).

**Context for compute exposure:** Presence of EuroHPC **Leonardo** at CINECA (Bologna Technopole) informs EWS signal selection [8].

## 4) Gaps & risks
- **Latency:** Eurostat GERD releases lag up to ~12 months; mitigate with ISTAT interim reports when available.
- **Coverage:** Standards role attribution to Italy requires careful org/person resolution (company subsidiaries, universities with multiple legal names).
- **Noise:** TED contains planning/cancellation notices; we restrict to **Result/Contract award** for outcome measures; keep **All** for early‑warning.

## 5) Tickets for Claude Code (ingestion/normalization)
1) **TED collector (Italy CPV set):** Implement query templates + pagination to extract both **Active** and **Result** notices [5]; write `procurement_signals.csv` fields: `award_id, buyer, supplier, cpv, title, url, publication_date, place, amount, status`. Add daily cursor & backoff.
2) **Standards roster normalizer:** Quarterly snapshot of **ETSI** membership query pages [6] + **3GPP** corporate groups and WG election lists [7]; map roles and compute `role_weight`. Write to `standards_activity.json` with `org_ror/person_orcid?` where available.
3) **Eurostat pull:** Programmatic pulls of `rd_e_gerdtot`, `rd_e_gerdfund`, `rd_e_gerdreg` for Italy and NUTS2 [1]; store with `generated_at` and notes on `latency_days`.
4) **OpenAIRE/CORDIS:** Use OpenAIRE Graph API filters for Italy orgs and targeted domains [3]; complement with **CORDIS SPARQL** for EU projects [4]. Store to `phase07_links.json` (coauthorship graph) and `phase03_landscape.json` (project counts by org).
5) **EPO patents:** CPC queries for dual‑use classes; write patent families into `phase07_links.json` (co‑inventorship) and a new `patent_signals.csv` [10][11].

---

## Endnotes
1. **Eurostat — GERD by sector of performance (rd_e_gerdtot).** https://ec.europa.eu/eurostat/databrowser/product/view/rd_e_gerdtot
   *Accessed:* 2025-09-13.
   **By source of funds (rd_e_gerdfund):** https://ec.europa.eu/eurostat/databrowser/view/rd_e_gerdfund/default/table?lang=en
   *Accessed:* 2025-09-13.
   **Regional GERD (rd_e_gerdreg):** https://ec.europa.eu/eurostat/product?code=rd_e_gerdreg&mode=view
   *Accessed:* 2025-09-13.
2. **World Bank — FDI, net inflows (BoP, current US$), Italy (BX.KLT.DINV.CD.WD?locations=IT).** https://data.worldbank.org/indicator/BX.KLT.DINV.CD.WD?locations=IT
   *Accessed:* 2025-09-13.
3. **OpenAIRE Graph API — Docs & Filters.** https://graph.openaire.eu/docs/apis/graph-api/
   *Accessed:* 2025-09-13.
   **Filtering tutorial:** https://graph.openaire.eu/docs/apis/graph-api/searching-entities/filtering-search-results/
   *Accessed:* 2025-09-13.
   **Latest dataset (release on Zenodo):** https://zenodo.org/records/14851262
   *Accessed:* 2025-09-13.
4. **CORDIS — SPARQL endpoint.** https://cordis.europa.eu/about/sparql
   *Accessed:* 2025-09-13.
   **Project detail example:** https://cordis.europa.eu/project/id/262229/reporting
   *Accessed:* 2025-09-13.
5. **TED — Advanced search & results.** https://ted.europa.eu/en/advanced-search
   *Accessed:* 2025-09-13.
   **Notice example (Italy):** https://ted.europa.eu/en/notice/-/detail/229303-2025
   *Accessed:* 2025-09-13.
   **Result example:** https://ted.europa.eu/en/notice/-/detail/784137-2024
   *Accessed:* 2025-09-13.
6. **ETSI — Membership query portal.** https://portal.etsi.org/Portal_IntegrateAppli/QueryResult.asp?Al=
   *Accessed:* 2025-09-13.
   **ETSI Directives (process reference):** https://portal.etsi.org/directives/41_directives_feb_2020.pdf
   *Accessed:* 2025-09-13.
7. **3GPP — Corporate group list / elections (role attribution examples).** https://www.3gpp.org/dynareport?code=corporate-groups.htm
   *Accessed:* 2025-09-13.
   **WG election voting list example:** https://www.3gpp.org/ftp/webExtensions/elections/SA/SA1/Election_November_2021/votingList_mtg-SA1-96-e.htm
   *Accessed:* 2025-09-13.
8. **EuroHPC — Leonardo supercomputer (context for compute exposure indicators).** https://www.eurohpc-ju.europa.eu/supercomputers/our-supercomputers_en
   *Accessed:* 2025-09-13.
   **CINECA Leonardo — about page:** https://leonardo-supercomputer.cineca.eu/about/
   *Accessed:* 2025-09-13.
9. **NATO DIANA — Network & sites (for Italy-linked cohorts/test centres).** https://www.diana.nato.int/accelerator-programme.html
   *Accessed:* 2025-09-13.
   **Turin accelerator page:** https://www.diana.nato.int/accelerator-programme/takeoff.html
   *Accessed:* 2025-09-13.
10. **EPO — Espacenet patent search (official).** https://www.epo.org/en/searching-for-patents/espacenet
   *Accessed:* 2025-09-13.
11. **EPO — Open Patent Services (OPS) v3.2 docs.** https://developers.epo.org/ops-v3-2
   *Accessed:* 2025-09-13.
