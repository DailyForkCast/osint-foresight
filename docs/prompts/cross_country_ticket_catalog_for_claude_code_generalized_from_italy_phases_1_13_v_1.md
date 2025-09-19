# Cross‑Country Ticket Catalog for Claude Code (Generalized from Italy Phases 1–13) — v1
**Purpose:** Reusable backlog of data‑engineering + analyst tickets you can apply to any country case.
**Covers:** Conferences, MoUs, standards, procurement, patents/publications, funding, ownership chains, supply chains, EWIs, adversarial, validation, registries, dashboards.
**Join‑Key Standard:** `org_ror` (org), `lei` (company), `orcid` (person), `cage`/`ncage` (supplier), `country_iso3`, `cpc` (patents), `cpv` (procurement), `hs_cn` (trade), `grid_id?` (legacy), `event_uid` (conferences), `project_id` (EU/NSF/etc).
**Artifact Conventions:** numeric confidence (0–20) lives in artifacts only; narratives carry probability band + categorical confidence.

---

## 0) Global Setup
**T0.1 — Country Bootstrap**
- **Input:** `country_iso3`
- **Output:** `country_config.json` (endpoints, language, tier‑1/2 event list, code lists)
- **Cadence:** once per country; refresh quarterly
- **Success:** All downstream jobs resolve endpoints + code lists.

**T0.2 — ID Registry Seed**
- **Output:** `id_registry.json` with `org_ror ↔ aliases`, `lei ↔ company`, `orcid ↔ person`, `cage/ncage`, `domain_names`, `twitter/linkedin`, `country_iso3`
- **Notes:** treat as canonical join map across all tickets.

---

## 1) Conferences & MoUs
**T1.1 — Conference Harvester**
- **Goal:** Build event and participant baselines (2018→present).
- **Inputs:** curated Tier‑1/2 list per domain (defense, aero/space, semicon, photonics, cyber, quantum, robotics); web scrapes, PDFs, press pages.
- **Outputs:**
  - `conferences/events_master.csv` → `series, event_uid, year, location, tier, url, archived_url`
  - `conferences/participants_map.csv` → `event_uid, year, entity_name, org_ror?, country, role, panel, session_url, prc_presence, us_presence`
- **Join keys:** `event_uid`, `org_ror`
- **Cadence:** quarterly harvest + on‑demand backfill.

**T1.2 — MoU & Side‑Deal Extractor**
- **Goal:** Capture conference‑initiated agreements.
- **Sources:** conference newsrooms, institutional press rooms, gov gazettes.
- **Outputs:** `mou_links.json` → `mou_id, event_uid?, parties[], date, scope, doc_url, is_binding, country_tags[]`
- **Derivatives:** `org_event_exposure.csv` join with participants.

**T1.3 — China Exposure Index (CEI) Calculator**
- **Inputs:** participants_map, mou_links; tier weights; session sensitivity tags.
- **Output:** `conference_risk.csv` → `event_uid, year, tier, prc_presence, disclosure_risk, partnership_depth, cei_0_1`.
- **Rule:** apply `china_multiplier=3.0` to Tier‑1 critical.

---

## 2) Standards & Committees
**T2.1 — Standards Role Normalizer**
- **Bodies:** ETSI/3GPP/ISO/IEC/IEEE.
- **Output:** `standards_roles.csv` → `body, wg, role, person, orcid?, org_ror, country, start_q, end_q`
- **Metric:** quarterly `role_weight_sum` (member=1, rapporteur=3, editor=5).
- **Alert:** > +2σ surge/drop.

---

## 3) Procurement & Awards
**T3.1 — TED / National Procurement Harvester**
- **Scope:** CPVs relevant to dual‑use; place of performance = target country.
- **Outputs:** `procurement_signals.csv` → `notice_id, type, date, buyer, supplier, cpv, amount_eur, status, url`
- **Indicator:** rolling 90‑day counts (All vs Awards).

**T3.2 — NATO/Allied Overlap Integrator**
- **Goal:** Cross‑match national awards with NATO/US defense supplier lists.
- **Output:** `award_overlap.csv` → `award_id, source, date, buyer, supplier, nato_overlap_bool, notes, url`.

**T3.3 — CAGE/NCAGE Resolver**
- **Output:** `cage_ncage_registry.json` with `entity, cage, ncage, org_ror, lei, country`
- **Use:** Join across supply‑chain components and awards.

---

## 4) Patents, Publications, Projects
**T4.1 — Patent Signals (EPO/WIPO/USPTO)**
- **Output:** `patent_signals.csv` → `family_id, cpc, assignee, org_ror?, country, pub_date, grant_date, title, link`
- **Cadence:** semi‑annual.

**T4.2 — Publications & Co‑authorships**
- **Output:** `coauthorship_network.csv` → `paper_id, year, italy_institution|target_country, prc_institution, field, venue, doi`
- **Metric:** growth rates and centrality per country pair.

**T4.3 — Grants & Projects (CORDIS/OpenAIRE + National)**
- **Outputs:** `fts_grants.csv` / `national_project_codes.json` with PRC partner flags and UBO notes.

---

## 5) Funding & Ownership
**T5.1 — Ownership Chains (GLEIF/OpenCorporates)**
- **Output:** `ownership_chains.json` → `org_ror|lei, parents[], ultimate_owner, country`
- **Flag:** PRC beneficial owners; confidence score.

**T5.2 — VC/LP Transparency Scanner**
- **Goal:** Detect PRC LPs in funds backing spin‑outs.
- **Output:** `vc_exposure.json` → `fund, lp_country_mix, prc_lp_flag, portfolio_orgs[], evidence_urls[]`.

---

## 6) Supply Chains & Resilience
**T6.1 — Critical Component Mapper**
- **Domains:** semicon/SiC, HPC/quantum, EO, robotics, naval/undersea, optics.
- **Output:** `phaseXX_supply_chain.json` → `component, supplier, org_ror, lei, cage, country, bottleneck_bool, notes`

**T6.2 — Resilience Simulator**
- **Output:** `resilience_matrix.csv` → `component, alt_supplier, tech_delta, qualification_timeline_months, cost_multiple, risk_notes`
- **Scenarios:** GPU export curbs; cryogenics disruption; rare‑earth shock.

---

## 7) Early Warning Indicators (EWIs)
**T7.1 — EWI Registry Builder**
- **Output:** `ewi_registry.csv` → `date, category, signal, entity, severity{green/yellow/amber/red}, evidence_url, status, notes`
- **Categories:** conferences/MoUs, spin‑outs/VC, funding/ownership, talent flows, procurement overlaps, supply shocks.

**T7.2 — CEI Watcher (Rolling 36m)**
- **Output:** `cei_trends.csv` → `month, event_tier_mix, prc_presence_score, disclosure_risk_score, cei_0_1`
- **Alert:** CEI > 0.65 sustained 2+ months.

---

## 8) Talent & Mobility
**T8.1 — Scholar Flow Integrator (ORCID/Scopus)**
- **Output:** `talent_flows.json` → `person_orcid, from_org_ror, to_org_ror, country_pair, field, start, end, funding_source?`
- **Flag:** inbound PRC scholars in sensitive domains.

---

## 9) Adversarial & Incidents
**T9.1 — Case Study Ledger**
- **Output:** `case_studies.csv` → `case_id, title, date, vector{licit|gray|illicit}, impact, evidence_url, status`.

**T9.2 — APT/Cyber Event Tracker**
- **Output:** `cyber_events.csv` → `event_id, date, target_org, vector, suspected_actor, impact, source_url`.

---

## 10) Validation, Provenance, and Negative Evidence
**T10.1 — Validation Reporter**
- **Output:** `validation_report.json` with checks `completeness|consistency|recency` and `major_findings_confidence[]` (0–20).

**T10.2 — Web Capture & Hashing**
- **Output:** `evidence_hashes.csv` → `url, archived_url, hash, captured_at`

**T10.3 — Negative Evidence Logger**
- **Output:** `negative_evidence.json` → `claim, where_searched, result{not_found|contradicted}, evidence_link`.

---

## 11) Governance & Compliance
**T11.1 — Oversight/Governance Map**
- **Output:** `governance_map.json` → `agency, mandate, legal_refs, gaps, contact`

**T11.2 — Export‑Control Lens**
- **Output:** `export_controls.csv` → `item, regime, country_rule, notes`
- **Use:** tag records in supply chains and publications.

---

## 12) Dashboards & Master Artifacts
**T12.1 — Country Master Summary Builder**
- **Output:** `country_master_summary.json` + `implementation_timeline.csv`
- **Inputs:** all phase outputs; produce BLUF + weighted risks + top recs.

**T12.2 — Atlas Dashboard (Multi‑Country)**
- **Goal:** Side‑by‑side comparison across countries.
- **Outputs:** `atlas_index.csv` → `country_iso3, cei_now, award_overlap_risk, top_bottlenecks, open_mous_count, ewi_red_count`.

---

## 13) Run‑Book (Orchestration)
**T13.1 — Phase DAG & Dependencies**
- **Graph:** `T0.1 → T0.2 → (T1.*, T2.*, T3.*, T4.*, T5.*, T6.*, T8.*) → T7.* → T9.*, T10.*, T11.* → T12.*`
- **Policy:** Fail‑open with **gap markers** but never drop a critical finding.

**T13.2 — Cadence & Owners**
- Weekly: conferences, procurement, EWIs.
- Monthly: ownership chains, VC exposure, standards roles.
- Quarterly: patents, atlas roll‑ups.
- Ad‑hoc: incidents, bombshell follow‑ups.

---

## 14) Minimal Schemas (for immediate reuse)
- `events_master.csv`: `series,event_uid,year,location,tier,url,archived_url`
- `participants_map.csv`: `event_uid,year,entity_name,org_ror?,country,role,session_url,prc_presence`
- `mou_links.json`: `mou_id,event_uid?,parties[],date,scope,doc_url,is_binding`
- `award_overlap.csv`: `award_id,source,date,buyer,supplier,nato_overlap_bool,notes,url`
- `resilience_matrix.csv`: `component,alt_supplier,tech_delta,qualification_timeline_months,cost_multiple,risk_notes`
- `ewi_registry.csv`: `date,category,signal,entity,severity,evidence_url,status,notes`
- `ownership_chains.json`: `org_ror|lei,parents[],ultimate_owner,country`

---

## 15) Success Criteria (per country)
- ≥12 Tier‑1/2 conferences harvested (3y window).
- CEI computed; triad co‑appearance rate published.
- Standards roles normalized and scored.
- Procurement overlaps cross‑matched with NATO.
- Supply bottlenecks mapped with at least one alternative each.
- Funding/ownership chains resolved to UBO where possible.
- EWIs live with escalation rules.
- Validation + negative evidence artifacts shipped.

---

## 16) Starter Backlog (Prioritized)
1) T1.1 Conference Harvester
2) T1.2 MoU Extractor
3) T3.1 Procurement Harvester
4) T6.1 Supply Component Mapper
5) T5.1 Ownership Chains
6) T2.1 Standards Roles
7) T7.1 EWI Registry
8) T3.2 Award Overlap
9) T6.2 Resilience Simulator
10) T12.1 Master Summary Builder

> This catalog is country‑agnostic. To deploy for a new country, clone `T0.1/T0.2`, load code lists, then run Section **16** top‑down. Add or remove domain modules (e.g., Arctic) as needed.
