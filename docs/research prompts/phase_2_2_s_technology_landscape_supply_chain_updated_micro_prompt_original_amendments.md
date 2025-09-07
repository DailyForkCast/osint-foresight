Below is a single, copy‑paste **micro‑prompt** to run Phase 2 and Phase 2S. It preserves the original structure and merges all amendments (MCF label‑independent detection, sanctions exclusions, flexible logistics narrative).

---

# Run Phase 2 — Technology Landscape & Phase 2S — Supply Chain for <COUNTRY> (<ISO2>)

## Output contract
- Create two canvases (two files):
  1) **Phase 2** → title exactly:
     "Write <COUNTRY> Phase 2 — Technology Landscape (reports/country=<ISO2>/phase-2_landscape.md)"
  2) **Phase 2S** → title exactly:
     "Write <COUNTRY> Phase 2S — Supply Chain Security (reports/country=<ISO2>/phase-2s_supply_chain.md)"
- Each canvas must contain **ONLY the final file content** (Markdown + front‑matter).
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>"]**; toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If sources are thin, still render complete reports with clear “No data yet” notes.

---

## Phase 2 — Technology Landscape (P2)

### P2‑A — Per‑sector capture (≤6 sectors)
For each selected sector:
- **Definition** (1–2 sentences) in country context.
- **Maturity** = Strong / Emerging / Nascent (justify with evidence IDs).
- **Capabilities**: labs/testbeds/compute/datasets/standards roles (name + 1‑line proof each).
- **Notable examples**: ≤3 with links; add EN/<local>/ZH names if applicable.
- **Export hooks** (if any): program/legal/standards notes (1 line each).
- **Retrieval transparency**: show **top‑3 matched keywords** used.

**Output TSV:** `SectorLandscape.tsv`
```
# excel-tsv
sector	definition	maturity	capabilities_summary	examples	standards_roles	export_hooks	retrieval_keywords	evidence_ids
```

**Where data helps (free)**: facility/testbed pages, SDO rosters (IETF/ETSI/ISO/IEC/OGC/CCSDS/ITU), accreditation registries.

---

### P2‑B — PRC add‑ins + QA + proxies (updated)
- **PRC policy alignment**: capture title/date/issuer/key line from authoritative sources.
- **Standards posture**: list WGs where PRC entities co‑lead vs domestic co‑chairs; note role types.
- **MCF relevance — label‑independent**: If claiming MCF relevance, link to annex/ECCN or mark **“unclear.”** **Do not rely on the literal label “MCF.”** Treat activities as **MCF‑consistent** when they align with dual‑use integration patterns even if not named as such. For each candidate, add a short rationale and tag `mcf_consistent=y/n/unclear`.
  - **Detection cues (EN/中文):** defense SOE group involvement; procurement by defense/PLA‑linked units; military end‑use/export‑control notes; dual‑use grants/programmes; standards with defense implications; university labs with defense MOUs; phrasings like *civil–military integration/collaboration*, *dual‑use transformation*, *defense‑related S&T*, *军民融合 / 军民协同创新 / 军地 / 军民两用*.
  - **Function‑over‑label rule:** prioritize concrete **mechanisms** (ownership chain, funding line, procurement customer, standards deliverable, lab charter) over terminology. Require **≥2 independent anchors** for high‑impact calls; otherwise keep confidence low and add `uncertainty_note`.
- **Non‑Conforming Signals** + **Proxy Log**: capture contradictions and proxies (lab CAGR, effective HPC ratio, specialist kit) with `confidence_0to1` and `source_tier`.
- **Recency weighting:** prefer last 24–36 months; keep older with a note if uniquely probative.

**Output TSVs:**
```
# excel-tsv
NonConforming.tsv
phase	what_conflicts	where_seen	date	severity_1to3	evidence_ids	comment
```
```
# excel-tsv
ProxyLog.tsv
metric_id	description	value	unit	source_tier	confidence_0to1	evidence_ids	comment
```

---

### P2‑C — Lay summary & consortium skew
- 3–5 bullets per top sector capturing momentum and event spikes.
- Compute entity concentration; if `top1_share > 0.5`, add a caution line (“Dominated by <entity>; breadth uncertain”).

---

## Phase 2S — Supply Chain Security (P2S)

### P2S‑A — Five‑pillar exposure (K/T/M/F/L)
Map relationships to pillars and summarize exposure by sector.

**Output TSV:** `SupplyPillars.tsv`
```
# excel-tsv
sector	K	T	M	F	L	method_note
```

### P2S‑B — PRC exposure & **Sanctions/Legal overlay** (with exclusions)
- Compute PRC share per sector; list top 1–2 CN counterparts (EN/中文 names + registry IDs).
- **Sanctions overlay (signals, not proof):** join partners against `sanctions_registry.csv` and list exemplars.
  - **Hard exclusion:** **Do not include American citizens/persons** in sanctions hits or narratives. If a match is a US person, **drop** it and note `excluded_us_person=true` in the internal join log (omit from report text).
  - Record `match_type`, `source_list`, `name_matched`, `canon_name`, `country`, `matched_on`, `evidence_url`, `notes`.
- **Optional legal cases:** add brief vignettes tied to supply chain vectors when relevant.

**Output TSVs:**
```
# excel-tsv
sanctions_hits.csv
match_type	source_list	name_matched	canon_name	country	matched_on	evidence_url	notes
```
```
# excel-tsv
legal_cases.tsv
case_id	jurisdiction	law_or_policy	defendant	aliases	entity_type	tech_domain	allegation	outcome	year	country	source_url
```

### P2S‑C — Logistics/procurement exposure (flexible narrative) — **amended**
Write a **flexible, evidence‑scaled** section that adapts to each country’s reality:
- **Narrative core:** at least **one paragraph** explaining logistics/procurement exposure channels: ports, corridors, free zones, national procurement systems, customs rulings, critical vendors, freight chokepoints, subsea cables, ground stations, data center interconnects.
- **Examples:** include **as many concrete examples as exist**, within these **elastic** bounds:
  - If **0 examples** → write the paragraph + a “no concrete examples found” line and a Next Data Boost.
  - If **1–5 examples** → list each as a bullet with link and 1‑line relevance.
  - If **6–25 examples** → print a **table** with key fields (name, type, location/route, sector link, date, source) and follow with 2–3 synthesis bullets.
  - If **>25 examples** → print a **top‑N table** (N=25 by default) ranked by relevance, then a **roll‑up summary** (counts by type/region/sector link) and **outlier callouts**. Provide a TSV appendix for **all** examples.
- **Country fit:** this accommodates inland countries (e.g., Czechia) with few/no ports vs maritime hubs (e.g., Greece, Sweden). Focus on **what actually exists**; avoid padding.

**Output TSVs (as applicable):**
```
# excel-tsv
LogisticsExamples.tsv
name	type	geo_or_route	sector_link	date	role_in_supply_chain	source_url	notes
```
```
# excel-tsv
LogisticsSummary.tsv
example_count	top_types	top_regions	top_sector_links	outliers_note
```

**Where data helps (free)**: national procurement portals; EU TED (summaries); customs/dual‑use guidance; port/rail/air timetables; subsea cable maps (public); space ground station lists; official sanctions portals (search only; exclude US persons); DOJ/BIS/EU enforcement press (narrative vignettes).

---

## Close (both phases)
- End each report with **Next Data Boost** (1 high‑ROI action) and note refresh cadence: P2 (quarterly/biannual), P2S (quarterly, or faster if supply events occur).

**Run now for <COUNTRY>/<ISO2> and return both reports per the contracts above.**

