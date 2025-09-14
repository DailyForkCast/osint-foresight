---
title: "Austria — Phase 7R: Assumption Check & Red‑Team Review"
author: OSINT Foresight (solo analyst)
date: 2025-09-07
---

## Scope & Inputs
- **Country / ISO2:** Austria (AT) · **Years:** 2015–2025 · **Languages:** en, de · **Looser matchers:** ON
- **Primary files (if present):** `data/processed/country=AT/phase-0_setup.md`, `phase-1_indicators.md`, `phase-2_landscape.md`, `phase-2s_supply_chain.md`, `phase-3_institutions.md`, `phase-4_funders.md`, `phase-5_links.md`, `phase-6_risk.md`, `phase-7c_prc_mcf.md`, plus TSV/CSV from those phases. Optional `sanctions_hits.csv` (signals‑only; **exclude US persons**), `policy_*.tsv` corpora.
- **Guardrails:** Neutral tone; *signals ≠ proof*; label‑independent MCF reasoning; avoid essentialist framing. Highlight uncertainty and error bars.

---

## Purpose (what this chapter does)
Surface and **challenge assumptions**, document **contradictions**, call out **coverage gaps** and **weak assertions**, and propose **quick discriminators** (tests) to resolve uncertainty. All legal/sanctions references remain **signals‑only** and **exclude US persons**.

---

## A) Assumptions Inventory (extract from prior phases)
List assumptions that materially shape interpretation or priority.

```text
# excel-tsv — data/processed/country=AT/p7r_assumptions.tsv
assumption_id	statement	phase_origin	basis	impact_if_wrong	confidence_LMH	notes
A1	HPC access (VSC/EuroHPC) enables AI maturity	P2	signals+facilities	Overstates AI capability if allocations tiny	M	Need allocation proof
A2	AT has accredited EMC/GNSS capacity	P3	expected from registry	Risk posture relies on real benches	L	Confirm scopes first
A3	Standards roles → deployment influence	P2,P5	IETF IPPM/NTP authorship	May overstate leverage if roles minor	M	Check editorship, doc adoption
```

---

## B) Contradictions & Tensions (sources disagree)
Where two credible sources point in **different directions**, log it.

```text
# excel-tsv — data/processed/country=AT/p7r_contradictions.tsv
claim_id	claim_text	source_a	source_b	why_in_tension	status
C1	“AI maturity is strong in AT”	Event signals (ICLR Vienna)	Thin co‑pub/co‑project density	Events ≠ capacity	open
C2	“GNSS/time benches exist at scale”	Metrology references	No registry scope captured yet	Evidence gap	open
```

---

## C) Coverage Gaps & Blind Spots
Document **where we didn’t look enough** or **data is missing**.

```text
# excel-tsv — data/processed/country=AT/p7r_gaps.tsv
gap_id	domain	why_it_matters	how_to_close	effort_1to3
G1	Accreditation scopes (EMC/GNSS)	Bench capability confirmation	Scrape/capture 10–20 scopes; hash PDFs	2
G2	CORDIS AT co‑projects	Edges & partner heat	Run CORDIS pull 2015–2025; normalize	1
G3	Ownership/control (LEI/OpenCorporates)	Supplier vectors	Pull/normalize LEI + OC; merge into CER	2
```

---

## D) Assertions With Weak/No Evidence
Flag statements that **sound definitive** but rely on **thin sources**.

```text
# excel-tsv — data/processed/country=AT/p7r_weak_assertions.tsv
assertion_id	text	current_evidence	needed_evidence	priority_1to3
W1	“Austria has robust EMC lab coverage.”	None captured	Registry scopes, client base, equipment	2
W2	“Standards roles give Austria outsized influence.”	1 named author	Editorship, draft adoption data	2
```

---

## E) Bias & Framing Check (incl. racism/xenophobia guardrails)
Audit language and logic for **stereotypes** or **essentialist claims**. Keep focus on **behaviors, mechanisms, and evidence**.

```text
# excel-tsv — data/processed/country=AT/p7r_bias.tsv
bias_id	bias_type	description	mitigation
B1	Attribution bias	Assuming intent from capability	Use signals‑only; require multi‑anchor evidence
B2	Availability bias	Overweighting conference signals	Balance with allocations, scopes, rosters
B3	National/ethnic essentialism	Inferring risk from identity	Center analysis on functions & governance
```

---

## F) Alternative Hypotheses & Discriminators
Propose **plausible alternatives** and **tests** (what evidence would favor one over another).

```text
# excel-tsv — data/processed/country=AT/p7r_hypotheses.tsv
hid	hypothesis	plausibility_LMH	discriminator_test	data_needed
H1	AI strength is mostly event‑driven, not capacity	M	Compute allocation logs; sustained co‑pub growth	VSC/EuroHPC allocations; OpenAIRE deltas
H2	EMC/GNSS capability is narrow and commercial	M	Registry scope granularity; equipment lists	Accreditation scopes; lab brochures
```

---

## G) Stress Tests / What‑if Scenarios
Check how conclusions change under **credible shocks**.

```text
# excel-tsv — data/processed/country=AT/p7r_stresstests.tsv
sid	scenario	expected_observables	implications	trigger_to_watch
S1	Compute allocation tightening at EU level	Fewer external MoUs; slower co‑dev	Lower AI trajectory; reduced spillovers	EuroHPC policy minutes
S2	Rapid lab scope expansion in RF/GNSS	New scopes; equipment PR	Higher dual‑use bench capability	Accreditation updates
```

---

## H) Red‑Team Verdict (snapshot)
- **Most fragile assumptions:** A1 (allocation effect on AI), A2 (unconfirmed EMC/GNSS scopes).
- **Highest‑value discriminators:** CORDIS export; accreditation capture; LEI+OC merges.
- **Net posture today:** **Moderate‑uncertain**—credible strengths in HPC/networking but key confirmation pending.

---

## I) Sanctions/Legal Overlay (signals‑only; **non‑US persons**)
If contradictions or gaps hinge on **sanctioned entities**, record **EU/UK/CA/AU/NZ/UN** listings in `sanctions_hits.csv` with URLs/dates; keep usage as **signals only** and **exclude US persons** entirely.

---

## Executive Summary (3–5 bullets)
- **Core uncertainties:** real bench capability (EMC/GNSS) and the scale of compute allocations.
- **Where sources disagree:** events vs. capacity; metrology references vs. missing scopes.
- **How to resolve quickly:** accreditation capture, CORDIS export, LEI/OpenCorporates merges.
- **Bias guardrails:** avoid intent attribution; avoid essentialist frames; require multi‑anchor evidence.

---

## Next Data Boost (1 step)
Complete **10–20 accreditation scopes** (EMC/GNSS) with **scope_text_hash** and update Phase 3/6; parallel **CORDIS (AT)** export to enrich Phase 4/5 edge density.
