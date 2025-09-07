Below is a single, copy‑paste **micro‑prompt** to run **Phase 3**. It preserves the original outputs (Roster + Accredited Labs) and adds **full actor‑coverage requirements** and a **richer lay summary** so we capture government, academia, corporate, finance, intermediaries, standards/accreditation, and testing facilities comprehensively.

---

# Run Phase 3 — Institutions & Accredited Labs for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 3 — Institutions & Accredited Labs (reports/country=<ISO2>/phase-3_institutions.md)"
- The canvas must contain **ONLY the final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: any table must be returned twice — (1) Markdown table and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>"]**; use **CER‑lite** (name+country) before any ranking; tag `(ambiguous)` if unresolved.
- If sources are thin, still render a complete report with “No data yet — drop‑in CSV recipe below” notes.

---

## Sections to produce
1) **Front‑matter** (title, author, date).
2) **Scope & actor taxonomy** (short) — list actor groups and what “counts” for each.
3) **Roster (institutions & firms)** — with dual‑use relevant fields and PRC/controls notes (TSV).
4) **Accredited labs & facilities** — ISO/IEC testing & calibration, plus national facilities (TSV).
5) **Coverage matrix & summaries** — counts by actor group × sector, top hubs, gaps (TSV).
6) **Lay summary (expanded)** — structured narrative (see prompt below).
7) **Next Data Boost** — one high‑ROI action.

---

## Actor taxonomy (must check all)
- **Government & Regulators:** ministries, S&T agencies, export‑control/licensing bodies, FDI screening body, defense/R&D agencies.
- **Academia:** universities, technical faculties, research centers, university‑affiliated labs.
- **Public RTOs / National Labs:** government‑linked research and technology organizations, standards mirror committees.
- **Accredited Labs / Test Facilities:** ISO/IEC 17025/17020; national metrology; sector testbeds (HPC, robotics ranges, RF anechoic, EO/space ground stations, bio labs if in scope).
- **Private Sector (Tech & Industrial):** national champions, SMEs, startups with dual‑use relevance.
- **Finance (Public):** innovation agencies, development banks/funds, state holding entities.
- **Finance (Private):** VC/PE with deep‑tech focus, banks with defense/dual‑use lending products (observation‑only).
- **Intermediaries & Clusters:** industry associations, tech parks, incubators, competence centers.
- **Standards & Accreditation Bodies:** national standards org, mirror committees, accreditation bodies.
- **NGOs/Non‑profits (relevant):** civil society actors shaping norms/ethics.

---

## TSV 1 — Roster.tsv (institutions & firms)
**Output both as Markdown table and `# excel-tsv`.** Columns:
```
# excel-tsv
id	org_name	alt_name_zh	lei_or_national_id	org_type	city_region	sectors	capability_notes	facility_name	metric_1	metric_2	funders_partners	standards_roles	prc_links_note	beneficial_owner_summary	ci_stem_y_n	risk_note	evidence_id	url
```
- **org_type** (allowed): government_ministry|regulator|soe_agency|university|rto|national_lab|accredited_lab|company_large|company_sme|startup|finance_public|finance_private|intermediary|standards_body|accreditation_body|ngo|hospital
- **metrics**: pick the 2 most meaningful (e.g., HPC peak TFLOPS; #17025 scopes; #WG roles); write the unit.
- **prc_links_note**: concise, neutral (signal, not proof). **Apply the sanctions/legal rule set elsewhere; do not list US persons.**
- **ci_stem_y_n**: any Confucius‑linked STEM program present (y/n/unknown).

---

## TSV 2 — AccreditedLabs.tsv
**Output both as Markdown table and `# excel-tsv`.** Columns:
```
# excel-tsv
organisation	iso_standard	accreditation_id	scope_short	sector_tags	city_region	status_note	last_check	links
```
- Accept ISO/IEC 17025/17020/15189 and national equivalents; include HPC/compute and national metrology if relevant (status_note explains why included).

---

## TSV 3 — CoverageMatrix.tsv (actor coverage × sector)
**Output both as Markdown table and `# excel-tsv`.** Long format for easy pivoting:
```
# excel-tsv
actor_group	sector	count	primary_sources	notes
```
- **actor_group** ∈ the exact taxonomy above.
- **primary_sources**: ≥1 authoritative link per non‑zero cell.

---

## TSV 4 — OrgCoverageSummary.tsv (quick roll‑up)
**Output both as Markdown table and `# excel-tsv`.** Columns:
```
# excel-tsv
actor_group	total_count	top_hubs	data_gaps
```
- **top_hubs**: cities/regions with multiple entries; **data_gaps**: what’s likely missing and where to look next.

---

## Lay summary (expanded — write this prose)
Write a **structured narrative** (600–900 words max) that:
1) **Ecosystem snapshot.** Quantify and describe the mix across **all actor groups** (gov/regulators; academia; RTOs/national labs; accredited labs/testbeds; private sector large/SME/startups; finance public/private; intermediaries; standards/accreditation; NGOs). Name the **top hubs** and why they matter.
2) **Who does what (by sector).** For each top sector (≤6), name 1–3 **anchor institutions/firms**, their **capability or facility** (1 line), and **how they interconnect** (funding/standards/testbeds).
3) **Governance & ownership.** Note **beneficial‑ownership patterns** (state holdings, conglomerates), **public‑private interfaces**, and any **university‑industry** structures relevant to dual‑use.
4) **Standards & accreditation posture.** Summarize presence in **mirror committees**, **WG roles**, and **ISO/IEC 17025/17020/15189** coverage relevant to the sectors.
5) **Finance interface.** Identify the **public instruments** and notable **private capital** that touch deep/dual‑use (observation‑only). If unknown, say so and point to where to check.
6) **Risk & diligence signals (light).** List 3–5 **neutral diligence flags** we will test later in Phase 6 (e.g., unresolved BO, accreditation lapsed, heavy reliance on a single hub). Keep tone factual; defer judgments.
7) **What’s missing.** Call out **coverage gaps** (by actor group/region/sector) and suggest **one concrete Next Data Boost** to close them (e.g., import 17025 CSV; scrape national R&I registry; add LEI IDs).

**Comprehensiveness guardrail (checklist):** Before closing, confirm each actor group has either (a) at least one row in **Roster.tsv** or (b) an explicit **data_gaps** note in **OrgCoverageSummary.tsv**.

---

## QA & hygiene
- **CER‑lite join** for names before ranking; tag `(ambiguous)` when uncertain; keep such rows but do not over‑rank.
- **No over‑claiming:** PRC notes are **signals**; reserve determinations for Phase 6/7C.
- **Sanctions/legal overlay:** optional cross‑screen for **non‑US persons only**; if any hit is a US person, **exclude** from report. If you ran a join, note: “Cross‑screened against official sanctions lists; no US persons included.”
- **Recency note:** Prefer last 24–36 months; older allowed with a short justification.

---

## Where data helps (free)
- National accreditation bodies (17025/17020/15189 lists), national metrology; university institute directories; national R&I registries; company/BO registers; GLEIF/LEI; standards mirror committees.

---

## Degrade gracefully
- If no accredited list is available, print the **AccreditedLabs.tsv header** with a “drop‑in later” note and proceed with narrative based on facilities/testbeds pages.
- If private finance is opaque, state that clearly and point to likely sources (company registry, fund manager directory) as Next Data Boost.

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 3 report per the contract above.**

