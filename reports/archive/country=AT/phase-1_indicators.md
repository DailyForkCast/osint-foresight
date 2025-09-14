---
title: "Austria — Phase 1: Indicators & Data Sources"
author: OSINT Foresight (solo analyst)
date: 2025-09-07
---

## Scope & Principles
- **Country / ISO2:** Austria (AT); **Years:** 2015–2025; **Languages:** en, de
- **Objective:** establish the **indicator catalog** and **source map** used by later phases; runnable with or without paid tools.
- **Guardrails:** neutral tone; signals ≠ proof; **exclude US persons entirely** from any sanctions/legal hits; mark uncertainty.

## Indicator Catalog (what we track)

| indicator_id | theme | description | why_it_matters | related_phases | collection_mode |
|---|---|---|---|---|---|
| IND1 | Research output & links | Co-publications, conference co-authorships, grant co-participation | Reveals collaboration edges and maturity | P2, P5 | OpenAIRE, Crossref (API) + manual conf pages |
| IND2 | Standards roles | Named authors/co-chairs/editors in IETF/ETSI/ISO/IEC | Standards leverage, influence channels | P2, P5, P6 | IETF Datatracker scrape; ETSI rosters |
| IND3 | Accredited capabilities | ISO/IEC 17025/17020 scopes; 17065 product cert | Real test/measure capacity; dual-use footprints | P3, P6 | National registry (portal scrape/manual) |
| IND4 | Funding & programs | National calls; CORDIS/Horizon projects | Drives co-project links and sector maturity | P4, P5 | National portals + CORDIS API/CSV |
| IND5 | Facilities & compute | HPC/testbeds/EO ground segment; EuroHPC/VSC | Enable development and scale | P2, P8 | Facility pages; EuroHPC, VSC news |
| IND6 | Corporate/institutional registry | Legal entities, BO/LEI, JV/equity | Ownership/control vectors; JV watch | P2S, P5, P7C | OpenCorporates + GLEIF (LEI) |
| IND7 | Sanctions/legal signals (non‑US only) | EU/UK/CA/AU/NZ/UN listings; legal cases | Risk posture signals, not proof | P6, P7C, P7R | Official lists; case repositories |
| IND8 | Policy & doctrine corpus | PRC + AT + EU tech/standards/export/FDI docs | Align signals with doctrine; foresee posture | P7C, P8 | Official portals; think‑tanks (free) |
| IND9 | Supply chain & logistics | Ports/FTZ/rail/air, customs, trade corridors | Exposure and alternative routes | P2S, P8 | Govt & industry registries (free) |

```text
# excel-tsv
indicator_id	theme	description	why_it_matters	related_phases	collection_mode
IND1	Research output & links	Co-publications, conference co-authorships, grant co-participation	Reveals collaboration edges and maturity	P2,P5	OpenAIRE,Crossref (API)+manual conf pages
IND2	Standards roles	Named authors/co-chairs/editors in IETF/ETSI/ISO/IEC	Standards leverage, influence channels	P2,P5,P6	IETF Datatracker scrape; ETSI rosters
IND3	Accredited capabilities	ISO/IEC 17025/17020 scopes; 17065 product cert	Real test/measure capacity; dual-use footprints	P3,P6	National registry (portal scrape/manual)
IND4	Funding & programs	National calls; CORDIS/Horizon projects	Drives co-project links and sector maturity	P4,P5	National portals + CORDIS API/CSV
IND5	Facilities & compute	HPC/testbeds/EO ground segment; EuroHPC/VSC	Enable development and scale	P2,P8	Facility pages; EuroHPC, VSC news
IND6	Corporate/institutional registry	Legal entities, BO/LEI, JV/equity	Ownership/control vectors; JV watch	P2S,P5,P7C	OpenCorporates + GLEIF (LEI)
IND7	Sanctions/legal signals (non‑US only)	EU/UK/CA/AU/NZ/UN listings; legal cases	Risk posture signals, not proof	P6,P7C,P7R	Official lists; case repositories
IND8	Policy & doctrine corpus	PRC + AT + EU tech/standards/export/FDI docs	Align signals with doctrine; foresee posture	P7C,P8	Official portals; think‑tanks (free)
IND9	Supply chain & logistics	Ports/FTZ/rail/air, customs, trade corridors	Exposure and alternative routes	P2S,P8	Govt & industry registries (free)
```

## Source Map (free-first; APIs where possible)

| source_id | indicator_id | name | type | access | notes |
|---|---|---|---|---|---|
| SRC1 | IND1 | OpenAIRE Explore/Graph | API/portal | Free | Co-authorship, grants (EU) |
| SRC2 | IND1 | Crossref + Event Data | API | Free | Pubs + citations/events |
| SRC3 | IND2 | IETF Datatracker | Web/CSV | Free | WG roles; drafts; authors |
| SRC4 | IND2 | ETSI portal (WG rosters) | Web | Free | Roles, groups (manual scrape) |
| SRC5 | IND3 | Akkreditierung Austria registry | Web | Free | 17025/17020/17065 scopes |
| SRC6 | IND4 | CORDIS | API/CSV | Free | Projects, partners, topics |
| SRC7 | IND5 | EuroHPC/VSC portals | Web/RSS | Free | Facility nodes/allocations |
| SRC8 | IND6 | GLEIF (LEI) | API/CSV | Free | Legal entity IDs |
| SRC9 | IND6 | OpenCorporates | API | Token | Ownership/JV links |
| SRC10 | IND7 | EU/UK/CA/AU/NZ/UN sanctions | Web/CSV | Free | Signals only; exclude US persons |
| SRC11 | IND8 | AT ministries/EU/PRC policy portals | Web/PDF | Free | Doctrine corpus |
| SRC12 | IND9 | Ports/rail/air registries; customs | Web | Free | Exposure checks |

```text
# excel-tsv
source_id	indicator_id	name	type	access	notes
SRC1	IND1	OpenAIRE Explore/Graph	API/portal	Free	Co-authorship, grants (EU)
SRC2	IND1	Crossref + Event Data	API	Free	Pubs + citations/events
SRC3	IND2	IETF Datatracker	Web/CSV	Free	WG roles; drafts; authors
SRC4	IND2	ETSI portal (WG rosters)	Web	Free	Roles, groups (manual scrape)
SRC5	IND3	Akkreditierung Austria registry	Web	Free	17025/17020/17065 scopes
SRC6	IND4	CORDIS	API/CSV	Free	Projects, partners, topics
SRC7	IND5	EuroHPC/VSC portals	Web/RSS	Free	Facility nodes/allocations
SRC8	IND6	GLEIF (LEI)	API/CSV	Free	Legal entity IDs
SRC9	IND6	OpenCorporates	API	Token	Ownership/JV links
SRC10	IND7	EU/UK/CA/AU/NZ/UN sanctions	Web/CSV	Free	Signals only; exclude US persons
SRC11	IND8	AT ministries/EU/PRC policy portals	Web/PDF	Free	Doctrine corpus
SRC12	IND9	Ports/rail/air registries; customs	Web	Free	Exposure checks
```

## Keyword Seeds (EN/DE) — Phase‑wide
Use these **loose matchers** to start. Refine with German synonyms as you capture real scopes.

| theme | core_keywords | de_synonyms |
|---|---|---|
| EMC/RED | emc, red, cispr, etsi, radio, conformity, anechoic | emv, funk, konformität, schirmkammer |
| Time/Frequency | time synchronization, ntp, ptp, disciplining, gnss | zeit, frequenz, zeitprotokoll, gnss |
| HPC/Compute | slurm, mpi, infiniband, queue, allocation | clusterverwaltung, warteschlange |
| AM/NDT | additive manufacturing, ndt, iso 9712, ultrasonic, radiography | additive fertigung, zfp, zerstörungsfrei |
| EO/Space | ground segment, ccsds, payload, downlink | bodenstation, nützlast |

```text
# excel-tsv
theme	core_keywords	de_synonyms
EMC/RED	emc; red; cispr; etsi; radio; conformity; anechoic	emv; funk; konformität; schirmkammer
Time/Frequency	time synchronization; ntp; ptp; disciplining; gnss	zeit; frequenz; zeitprotokoll; gnss
HPC/Compute	slurm; mpi; infiniband; queue; allocation	clusterverwaltung; warteschlange
AM/NDT	additive manufacturing; ndt; iso 9712; ultrasonic; radiography	additive fertigung; zfp; zerstörungsfrei
EO/Space	ground segment; ccsds; payload; downlink	bodenstation; nützlast
```

## Coverage & Gaps (today's snapshot)
- We **have** seeds in `relationships.csv`, `signals.csv`, `standards_roles.tsv` for AT.
- We **lack**: CORDIS exports, accreditation scope TSV, LEI/OpenCorporates merges, sanctions signals TSV (non‑US only), policy corpus TSV.

## Narrative (how to use this chapter)
This chapter defines what we will watch and where to fetch it, so later phases can run **even with thin data**. It prioritizes **free sources** and APIs (OpenAIRE, Crossref, IETF, CORDIS, GLEIF) and points clearly to **manual boosts** (national accreditation portal, ETSI rosters). It also sets **German synonym seeds** to reduce language bias in search. For legal/sanctions mentions, it requires a **signals‑only** stance and excludes **US persons entirely** to avoid overreach. As data accrues, we will fold the new evidence into Phases 2/3/4/5 automatically through the normalizers.

## Next Data Boost (1 step)
Pull **CORDIS (AT participants 2015–2025)** and produce `programs.csv` + co‑project edges; then re‑run Phase 2 and Phase 5 to capture new links.
