---
title: "Austria — Phase X: Definitions & Taxonomy (Dual‑Use Clusters, Subdomains, Keywords)"
author: OSINT Foresight (solo analyst)
date: 2025-09-07
---

## Purpose
This chapter establishes a **country‑aware dual‑use taxonomy** for Austria (AT): 6–10 clusters, their subdomains, keyword sets (EN/DE), standards links, and light export‑control hooks. It is designed to be **evidence‑guided but runnable without external data**. Where helpful, we note optional manual data boosts.

## Selection Criteria (how clusters are chosen)
- **Relevance to dual‑use & MCF‑consistent mechanisms** (label‑independent, function‑over‑label).
- **Observable footprint** in AT via labs, standards roles, facilities, or partnerships (from Phases 2/3/5).
- **Standards/Accreditation traction** (IETF/ETSI/ISO/IEC; ISO/IEC 17025/17020).
- **Export‑control sensitivity** (Annex I/ECCN, ML categories; high level only).
- **Feasibility for a solo analyst** (keywords and sources yield signals without paid tools).

## Austria Cluster Shortlist (8)
1. **AI/ML & Autonomy** — model development, safety, deployment; signals via VSC/EuroHPC access and AI initiatives.
2. **High‑Performance Computing (HPC)** — compute/testbeds (VSC; EuroHPC ties); software stacks.
3. **Communications, Networking & Timing** — IP networking, performance measurement, NTP/PTP time sync (IETF roles in IPPM/NTP at TU Wien).
4. **Sensing, PNT & Navigation** — GNSS/time & frequency, radar/LiDAR, photonics sensing; metrology.
5. **Advanced Manufacturing & Materials** — additive mfg, NDT/inspection, specialty steels/alloys, surface treatments.
6. **Semiconductors & Electronics** — power electronics, packaging/test, instrumentation; EMC/RED conformity.
7. **Space, EO & Remote Sensing Interfaces** — smallsat supply, ground segment links, data processing.
8. **Cybersecurity, Cryptography & Safety‑Critical SW** — secure modules, functional safety, software assurance, 27001 posture.

> Optional watchlist: **Energy storage & batteries** (interfaces), **Biotech (methods)** if scope expands.

---

## A) Clusters (authoritative list)

| cluster_id | name | definition | why_in_AT | export_control_refs | primary_SDOs | example_use_cases |
|---|---|---|---|---|---|---|
| C1 | AI/ML & Autonomy | Methods, models, training/inference, assurance | VSC/EuroHPC access; AI initiatives; intl conferences | ECCN 3D/4D (software) high‑level; ML14 (EU) analogues | ISO/IEC JTC1/SC42, CEN/CENELEC AI, IETF AINEMA (obs) | Model evaluation labs; applied autonomy in industry |
| C2 | High‑Performance Computing | Compute/testbeds, schedulers, interconnects, tooling | VSC footprint; EuroHPC collaborations | ECCN 4A/4D (systems/software) high‑level | PRACE/EuroHPC, OpenMP, MPI Forum | Access agreements; HPC codes & benchmarks |
| C3 | Comms, Networking & Timing | IP networking, measurement, NTP/PTP timing | Named roles at IETF IPPM/NTP; test labs | ECCN 5A/5D general (crypto export separate) | IETF (IPPM, NTP, TICTOC), ETSI | Testbeds; perf/latency tooling; time sync infra |
| C4 | Sensing & PNT | GNSS/time&freq, radar/LiDAR, photonics sensing | Metrology labs; optics/photonics expertise | ECCN 7 (nav) / 6 (sensors) high‑level | ISO, IEC TC 37/TC 76, ETSI, CEN | Calibration benches; RF/GNSS labs |
| C5 | Advanced Manufacturing & Materials | AM, welding, NDT, specialty steels/alloys | Industrial base; inspection bodies | ML10 (aircraft parts) analogues; Annex I metals | ISO/ASTM AM, ISO 9712 (NDT), CEN | Aerospace/rail/energy component QA |
| C6 | Semiconductors & Electronics | Power electronics, EMC/RED, test & measurement | EMC/product cert bodies; electronics labs | ECCN 3/5; Annex I semi equipment | IEC TC 47, ETSI RED, CISPR | EMC labs; power modules; instrument chains |
| C7 | Space/EO Interfaces | Smallsat subsystems, ground segment, EO data | EU/ESA ties; research collaborations | ML15/Annex I remote sensing (high‑level) | ECSS, CCSDS, ISO | Payload data chains; downlink; processing |
| C8 | Cybersecurity & Safety‑Critical SW | Crypto modules, 27001, functional safety | Mgmt systems cert bodies (27001); SW safety | ECCN 5A002/5D002 (crypto) high‑level | ISO/IEC 27001, IEC 61508, ISO 26262 | Secure modules; SIL pipelines |

```text
# excel-tsv
cluster_id	name	definition	why_in_AT	export_control_refs	primary_SDOs	example_use_cases
C1	AI/ML & Autonomy	Methods, models, training/inference, assurance	VSC/EuroHPC access; AI initiatives; intl conferences	ECCN 3D/4D (software) high‑level; ML14 (EU) analogues	ISO/IEC JTC1/SC42; CEN/CENELEC AI; IETF AINEMA (obs)	Model evaluation labs; applied autonomy in industry
C2	High‑Performance Computing	Compute/testbeds, schedulers, interconnects, tooling	VSC footprint; EuroHPC collaborations	ECCN 4A/4D (systems/software) high‑level	PRACE/EuroHPC; OpenMP; MPI Forum	Access agreements; HPC codes & benchmarks
C3	Comms, Networking & Timing	IP networking, measurement, NTP/PTP timing	Named roles at IETF IPPM/NTP; test labs	ECCN 5A/5D general (crypto export separate)	IETF (IPPM, NTP, TICTOC); ETSI	Testbeds; perf/latency tooling; time sync infra
C4	Sensing & PNT	GNSS/time&freq, radar/LiDAR, photonics sensing	Metrology labs; optics/photonics expertise	ECCN 7 (nav) / 6 (sensors) high‑level	ISO; IEC TC 37/TC 76; ETSI; CEN	Calibration benches; RF/GNSS labs
C5	Advanced Manufacturing & Materials	AM, welding, NDT, specialty steels/alloys	Industrial base; inspection bodies	ML10 (aircraft parts) analogues; Annex I metals	ISO/ASTM AM; ISO 9712 (NDT); CEN	Aerospace/rail/energy component QA
C6	Semiconductors & Electronics	Power electronics, EMC/RED, test & measurement	EMC/product cert bodies; electronics labs	ECCN 3/5; Annex I semi equipment	IEC TC 47; ETSI RED; CISPR	EMC labs; power modules; instrument chains
C7	Space/EO Interfaces	Smallsat subsystems, ground segment, EO data	EU/ESA ties; research collaborations	ML15/Annex I remote sensing (high‑level)	ECSS; CCSDS; ISO	Payload data chains; downlink; processing
C8	Cybersecurity & Safety‑Critical SW	Crypto modules, 27001, functional safety	27001 cert bodies; SW safety	ECCN 5A002/5D002 (crypto) high‑level	ISO/IEC 27001; IEC 61508; ISO 26262	Secure modules; SIL pipelines
```

---

## B) Subdomains & Keywords (EN/DE, with loose matchers)

| cluster_id | subdomain_id | subdomain_name | description | keywords_core (EN/DE) | keywords_loose (EN/DE) | example_techs |
|---|---|---|---|---|---|---|
| C1 | SD1 | Model training & eval | Training/inference; eval/bench | "model training", "fine‑tuning", "benchmark", **de:** "Modelltraining", "Bewertung" | "GPU", "EuroHPC", "VSC", **de:** "Hochleistungsrechner" | LLM eval suites; HPC training jobs |
| C1 | SD2 | Safety & assurance | testing, red‑teaming, RAI | "model safety", "assurance", **de:** "Sicherheit", "Gewährleistung" | "risk card", "eval harness" | Safety test harnesses |
| C2 | SD3 | Schedulers & interconnect | SLURM, MPI, IB | "SLURM", "MPI", "Infiniband", **de:** "Clusterverwaltung" | "job queue", **de:** "Warteschlange" | HPC cluster configs |
| C3 | SD4 | Performance measurement | IPPM metrics; NTP/PTP | "IPPM", "NTP", "PTP", **de:** "Zeit同步"/"Zeitprotokoll" | "latency", "jitter", **de:** "Latenz" | Perf probes; time sync |
| C4 | SD5 | GNSS & time/freq | receivers; calibration | "GNSS", "time frequency", **de:** "Zeit/Frequenz" | "disciplining", "rubidium" | GNSS labs |
| C4 | SD6 | Photonics sensing | lidar, lasers | "LiDAR", "laser", **de:** "Laser", "Photonik" | "TOF", "range" | LiDAR benches |
| C5 | SD7 | AM & NDT | AM processes; ISO 9712 | "additive manufacturing", "NDT", **de:** "Additive Fertigung", "ZfP" | "powder bed", "UT/RT/MT" | AM part QA |
| C6 | SD8 | EMC/RED & electronics test | EMC chambers; radio | "EMC", "RED", **de:** "EMV", "Funk" | "anechoic", "conformity" | EMC test labs |
| C7 | SD9 | Ground segment & EO | downlink, processing | "ground segment", "remote sensing", **de:** "Bodenstation" | "CCSDS", "payload" | EO data chains |
| C8 | SD10 | Crypto & safety SW | 27001, 61508, 26262 | "27001", "61508", **de:** "Funktionale Sicherheit" | "HSM", "module" | Safety pipelines |

```text
# excel-tsv
cluster_id	subdomain_id	subdomain_name	description	keywords_core	keywords_loose	example_techs
C1	SD1	Model training & eval	Training/inference; eval/bench	model training; fine‑tuning; benchmark; de:Modelltraining; de:Bewertung	GPU; EuroHPC; VSC; de:Hochleistungsrechner	LLM eval suites; HPC training jobs
C1	SD2	Safety & assurance	testing, red‑teaming, RAI	model safety; assurance; de:Sicherheit; de:Gewährleistung	risk card; eval harness	Safety test harnesses
C2	SD3	Schedulers & interconnect	SLURM, MPI, IB	SLURM; MPI; Infiniband; de:Clusterverwaltung	job queue; de:Warteschlange	HPC cluster configs
C3	SD4	Performance measurement	IPPM metrics; NTP/PTP	IPPM; NTP; PTP; de:Zeitprotokoll	latency; jitter; de:Latenz	Perf probes; time sync
C4	SD5	GNSS & time/freq	receivers; calibration	GNSS; time frequency; de:Zeit/Frequenz	disciplining; rubidium	GNSS labs
C4	SD6	Photonics sensing	lidar, lasers	LiDAR; laser; de:Laser; de:Photonik	TOF; range	LiDAR benches
C5	SD7	AM & NDT	AM processes; ISO 9712	additive manufacturing; NDT; de:Additive Fertigung; de:ZfP	powder bed; UT/RT/MT	AM part QA
C6	SD8	EMC/RED & electronics test	EMC chambers; radio	EMC; RED; de:EMV; de:Funk	anechoic; conformity	EMC test labs
C7	SD9	Ground segment & EO	downlink, processing	ground segment; remote sensing; de:Bodenstation	CCSDS; payload	EO data chains
C8	SD10	Crypto & safety SW	27001, 61508, 26262	27001; 61508; de:Funktionale Sicherheit	HSM; module	Safety pipelines
```

> **German synonyms help recall** on AT portals. Adjust terms as you learn local phrasing (Phase 7R bias check).

---

## C) Standards Map (starter)

| sdo | wg_or_tc | scope | related_clusters | signals_evidence_hint |
|---|---|---|---|---|
| IETF | IPPM | Internet performance metrics | C3 | Named authors from AT in prior signals |
| IETF | NTP | Network Time Protocol | C3,C4 | Time sync relevance |
| ETSI | RED/EMC groups | Conformity for radio/EMC | C6 | Product cert bodies in AT |
| ISO/IEC | JTC1/SC42 | AI standardization | C1 | AI methods & assurance |
| IEC | TC 47 | Semiconductor devices | C6 | Electronics ecosystem |
| ISO/ASTM | AM CoE | Additive manufacturing | C5 | AM/NDT scope in labs |
| CCSDS | WGs | Space data systems | C7 | EO/ground segment |

```text
# excel-tsv
sdo	wg_or_tc	scope	related_clusters	signals_evidence_hint
IETF	IPPM	Internet performance metrics	C3	Named authors from AT in prior signals
IETF	NTP	Network Time Protocol	C3;C4	Time sync relevance
ETSI	RED/EMC groups	Conformity for radio/EMC	C6	Product cert bodies in AT
ISO/IEC	JTC1/SC42	AI standardization	C1	AI methods & assurance
IEC	TC 47	Semiconductor devices	C6	Electronics ecosystem
ISO/ASTM	AM CoE	Additive manufacturing	C5	AM/NDT scope in labs
CCSDS	WGs	Space data systems	C7	EO/ground segment
```

---

## D) Export‑Control Map (high‑level hooks)

| framework | code | label | applies_to_subdomains | notes |
|---|---|---|---|---|
| EU Annex I | 3 | Electronics | SD8 | General pointer only |
| EU Annex I | 4 | Computers | SD3 | Compute/HPC hooks |
| EU Annex I | 5 | Telecom/"Information Security" | SD4, SD10 | Crypto handled carefully |
| EU Annex I | 6 | Sensors & Lasers | SD6 | Photonics |
| EU Annex I | 7 | Navigation & Avionics | SD5 | GNSS/time |
| EU Annex I | 9 | Aerospace & Propulsion | SD7, SD9 | Manufacturing & space interfaces |

```text
# excel-tsv
framework	code	label	applies_to_subdomains	notes
EU Annex I	3	Electronics	SD8	General pointer only
EU Annex I	4	Computers	SD3	Compute/HPC hooks
EU Annex I	5	Telecom/Information Security	SD4,SD10	Crypto handled carefully
EU Annex I	6	Sensors & Lasers	SD6	Photonics
EU Annex I	7	Navigation & Avionics	SD5	GNSS/time
EU Annex I	9	Aerospace & Propulsion	SD7,SD9	Manufacturing & space interfaces
```

> These are **orientation cues only**; do not assert classification in narrative—use Phase 6 gates.

---

## E) Keyword Pack (to save as YAML)

```yaml
# Save to: queries/keywords/country=AT/phaseX_keywords.yaml
clusters:
  C1_AI_ML:
    core: ["model training", "fine-tuning", "benchmark", "evaluation", "safety"]
    loose: ["EuroHPC", "VSC", "GPU", "inference", "dataset"]
    de: { core: ["Modelltraining", "Bewertung"], loose: ["Hochleistungsrechner", "GPU"] }
    excludes: ["art exhibition", "children's AI toy"]
  C2_HPC:
    core: ["SLURM", "MPI", "scheduler", "Infiniband"]
    loose: ["queue", "job", "node"]
    de: { core: ["Clusterverwaltung"], loose: ["Warteschlange"] }
  C3_Comms_Timing:
    core: ["IPPM", "NTP", "PTP", "time synchronization"]
    loose: ["latency", "jitter", "packet loss"]
    de: { core: ["Zeitprotokoll"], loose: ["Latenz"] }
  C4_Sensing_PNT:
    core: ["GNSS", "time frequency", "LiDAR", "laser"]
    loose: ["rubidium", "TOF", "calibration"]
    de: { core: ["Zeit/Frequenz", "Photonik"], loose: ["Reichweite"] }
  C5_AdvMfg_Materials:
    core: ["additive manufacturing", "NDT", "ISO 9712"]
    loose: ["powder bed", "ultrasonic testing"]
    de: { core: ["Additive Fertigung", "ZfP"], loose: ["Pulverbett"] }
  C6_Semiconductors_Electronics:
    core: ["EMC", "RED", "CISPR", "IEC 61000"]
    loose: ["anechoic", "shielded room"]
    de: { core: ["EMV", "Funk"], loose: ["Schirmkammer"] }
  C7_Space_EO:
    core: ["ground segment", "remote sensing", "CCSDS"]
    loose: ["payload", "downlink"]
    de: { core: ["Bodenstation"], loose: ["Nutzlast"] }
  C8_Cyber_SafetySW:
    core: ["ISO 27001", "IEC 61508", "ISO 26262", "HSM"]
    loose: ["secure module", "SIL"]
    de: { core: ["Funktionale Sicherheit"], loose: ["SIL"] }
```

---

## F) Glossary (practical, analyst‑oriented)
- **MCF‑consistent:** Activity that integrates civilian R&D/industry with defense‑relevant outcomes, regardless of label.
- **Standards influence:** Co‑chair/editor/authorship positions that shape technical specs/test methods.
- **Accredited scope:** The exact tests/measurements a lab is authorized to perform (read the PDF!).
- **Intensity_0_3:** Link strength heuristic used in Phase 5 heat‑maps.
- **Signals vs Proof:** Sanctions/legal or doctrine hits are **signals only**; require multiple anchors for strong claims.

---

## Country Pivots (AT specifics to watch)
- **German terminology** in portals: EMV (EMC), Funk (radio), Zeit/Frequenz (time/frequency), ZfP (NDT), Additive Fertigung (AM), Bodenstation (ground station).
- **Institutions** likely to surface: VSC sites; TU Wien networking/time groups; EMC labs; inspection bodies with ISO 9712.
- **Manual boosts:** national accreditation search (Phase 3); CORDIS collab exports; IETF roster scrape for AT names; OpenAIRE for co‑pub edges.

---

## Claude Code — File Writes & Hooks (do these now)
1. **Write YAML** → `queries/keywords/country=AT/phaseX_keywords.yaml` (content above).
2. **Write clusters** → `config/taxonomy/country=AT/clusters.tsv` (table A as TSV).
3. **Write subdomains** → `config/taxonomy/country=AT/subdomains.tsv` (table B as TSV).
4. **Write standards map** → `config/taxonomy/country=AT/standards_map.tsv` (table C as TSV).
5. **Write export hooks** → `config/taxonomy/country=AT/export_map.tsv` (table D as TSV).
6. Ensure `reports/country=AT/phase-X_taxonomy.md` (this file) is saved.
7. Optional: add German synonym expansion to `src/utils/normalize.py` keyword matcher (append `de:` entries).

**VS Code Task to suggest:** `Taxonomy: AT bootstrap`
```json
{
  "label": "taxonomy:bootstrap:AT",
  "type": "shell",
  "command": "python -m src.utils.ensure_template --country AT --phase X && echo 'Taxonomy written'"
}
```

## Next Data Boost
Pull **accreditation scopes** for EMC/RED (C6) and time/frequency (C4) labs and expand `keywords_core` with exact instrument/model terms observed (e.g., "spectrum analyzer", "GPSDO", model numbers).