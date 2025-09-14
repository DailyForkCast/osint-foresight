Below is a copy‑paste prompt for Claude Code. It will **append or create** minimal Phase‑2 enrichments for Austria (AT) from authoritative narrative sources. Idempotent: replace rows with same natural key.

---

# Claude Code — AT Phase 2 quick enrichment from authoritative pages
**Goal:** Seed `data/processed/country=AT/` with small, well‑sourced tables to help Phase‑2 render useful scores even if bulk collectors are thin.

## Guardrails
- Write the three files **verbatim** as given below. If the file exists, **upsert** by natural key.
- Do **not** push. Print a one‑liner per file: `UPDATED <path>`.
- Natural keys:
  - `standards_roles.tsv`: `(wg, role, person_name, org_name)`
  - `signals.csv`: `(window, signal_summary)`
  - `relationships.csv`: `(sector, counterpart_name, collab_type, year)`

---

## 1) `data/processed/country=AT/standards_roles.tsv`
**Rows source:** TU Wien authorship of IETF work (RFCs/drafts) in IPPM/NTP areas.
- Evidence: RFC 9198 lists **TU Wien / Joachim Fabini (Vienna, Austria)** as an author (IPPM). citeturn2search12
- Evidence: RFC 7312 credits **Vienna University of Technology** (TU Wien) author **J. Fabini**. (IPPM). citeturn2search18
- Evidence: Draft `draft-ietf-ntp-packet-timestamps` shows TU Wien contact in NTP context. citeturn2search15

**Write this TSV content (tab‑separated; include header):**
```
wg	role	person_name	org_name	country	sector_hint
IPPM	author	Joachim Fabini	TU Wien (Vienna University of Technology)	AT	Communications/Networking
NTP	author	Joachim Fabini	TU Wien (Vienna University of Technology)	AT	Time Sync/Networking
```

**Then print:**
```
UPDATED data/processed/country=AT/standards_roles.tsv
```

---

## 2) `data/processed/country=AT/signals.csv`
**Rows source:** National HPC and AI program milestones.
- Evidence: **ASHPC24 booklet**: inauguration of Austria’s new supercomputer **“VSCrunchy”** on 10–13 June 2024. citeturn1view0
- Evidence: **FFG Digital Technologies 2023** call kick‑off on 13 Dec 2023. citeturn0search3
- Evidence: **AI Mission Austria** (aws+FFG+FWF) launch/portfolio note (2022). citeturn0search9turn0search21

**Write this CSV content (comma‑separated; include header):**
```
window,signal_summary,likely_driver
2024-06,Inauguration of "VSCrunchy" supercomputer at ASHPC24 (Austria-Slovenia HPC meeting),HPC capacity upgrade (VSC)
2023-12,FFG "Digital Technologies 2023" call kick-off event,National digital tech funding momentum
2022-11,AI Mission Austria joint initiative (aws+FFG+FWF) announced,Strategic AI funding coordination
```

**Then print:**
```
UPDATED data/processed/country=AT/signals.csv
```

---

## 3) `data/processed/country=AT/relationships.csv`
**Rows source:** HPC infrastructure & EuroHPC collaboration; EuroCC2 cross‑border cooperation.
- Evidence: **University of Vienna HPC** page lists **Vienna Scientific Cluster (VSC)**, **MUSICA**, and **EuroHPC LEONARDO** as available systems. (LEONARDO is in Italy → cross‑border infrastructure link.) citeturn0search10
- Evidence: **ASHPC24 booklet** credits **EuroCC Austria** & **EuroCC Slovenia (SLING)** and VSC as organizers/partners (Austria–Slovenia linkage). citeturn1view0

**Write this CSV content (comma‑separated; include header):**
```
sector,counterpart_name,counterpart_country,collab_type,year
High-Performance Computing,EuroHPC LEONARDO,IT,infrastructure,2024
High-Performance Computing,EuroCC Slovenia (SLING),SI,co-project,2024
High-Performance Computing,Vienna Scientific Cluster (VSC),AT,infrastructure,2024
```

**Then print:**
```
UPDATED data/processed/country=AT/relationships.csv
```

---

## Final step
After updating all three, run (optional):
```bash
make build COUNTRY=AT
```
Then print a one‑line summary:
```
OK: seeded standards_roles.tsv, signals.csv, relationships.csv for AT
```
