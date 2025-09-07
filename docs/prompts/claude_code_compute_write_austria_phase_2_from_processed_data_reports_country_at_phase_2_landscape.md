Below is a copy‑paste prompt for Claude Code to **compute** Phase 2 using existing processed data and **write** the finished report. It degrades gracefully if inputs are thin/missing. No pushes.

---

# Claude Code — Compute & Write Phase 2 (Austria, AT)

## Guardrails
- Do **not** push. Commit locally only if you must (but writing the file is enough).
- Deterministic write: save the final content **verbatim** to the path below and print a single confirmation line.

## Inputs (best‑effort)
Read from `data/processed/country=AT/` if present:
- `relationships.csv` with columns: `sector,counterpart_name,counterpart_country,collab_type,year`
- `signals.csv` (optional) with at least: `year,window,signal`
- `standards_roles.tsv` (optional) with: `wg,role,person_name,org_name,country,sector_hint`
- `partners_cerlite.csv` (optional) with: `raw_name,canon_name,country,ambiguous`

If a file is missing, continue and note it in the report.

## Computation logic (exact)
1) **Edges & intensity** (if `relationships.csv` exists)
   - Filter years to 2015–2025 (inclusive).
   - Group by `sector` → `edge_count`.
   - **Intensity 0–3**: if `edge_count==0` → 0. Else compute sector counts >0, take empirical quartiles (25/50/75) and map:
     - `<=Q1`→1, `<=Q2`→2, `>Q2`→3. (So only truly empty is 0.)
2) **Momentum** buckets
   - Compute counts in `2015–2018`, `2019–2022`, `2023–2025` per sector.
3) **Top counterparts** per sector (max 2 names)
   - Prefer `canon_name` from `partners_cerlite.csv` if a join on (raw_name ≈ counterpart_name, country) is possible; else use `counterpart_name`.
   - For each sector, compute the share of edges for the top entity; mark **Consortium skew** if `top1_share > 0.5`.
4) **Standards posture** (if `standards_roles.tsv` exists)
   - List up to 10 rows: `WG/SDO | Role | Person/Org | Sector hint`.
5) **Event spikes** (if `signals.csv` exists)
   - Group by `window` or `year` (whichever exists); show top 3 windows with a short note.

## Output path
Write the final Markdown file **verbatim** to:
`reports/country=AT/phase-2_landscape.md`

## Render rules
- Include front‑matter and clear notes when inputs are missing.
- Tables must render even if empty (use “–”).
- Add 3–5 narrative bullets summarizing what the numbers show (or what’s missing), plus a single **Next Data Boost**.

## File content to write (compute and fill the placeholders)
Construct the Markdown below using your computed values. Replace all `{{like_this}}` placeholders with actual values or `–` if unknown.

```
---
title: "Phase 2 — Technology Landscape & Maturity (Austria)"
author: Analyst
date: "<AUTO>"
---

## Overview
Sector intensity, momentum, standards posture, and notable event spikes for Austria (AT), **2015–2025**. *Looser matchers ON.*

### Data presence
- relationships.csv: {{rel_present}}
- standards_roles.tsv: {{std_present}}
- signals.csv: {{sig_present}}
- partners_cerlite.csv: {{cerlite_present}}

---

## Sector Scorecard
| Sector | Intensity (0–3) | Momentum (15–18 / 19–22 / 23–25) | Top counterpart(s) | Consortium skew? |
|---|---:|---|---|---|
{{sector_rows}}

**Notes:** Intensity is relative within AT; 0 = no edges, 1–3 = quartile buckets among non‑zero sectors.

---

## Standards Posture {{std_section_note}}
| WG / SDO | Role | Person/Org | Sector hint |
|---|---|---|---|
{{standards_rows}}

---

## Event Spikes {{sig_section_note}}
| Window | Signal summary | Likely driver |
|---|---|---|
{{signal_rows}}

---

## Narrative Snapshot
- {{bullet_1}}
- {{bullet_2}}
- {{bullet_3}}
- {{bullet_4}}
- {{bullet_5}}

## Caveats
- Looser matchers can over‑include adjacent subfields; review outliers in Phase 5.
- Edges aggregate heterogeneous collaboration types; mechanism details live in Phase 5.

## Next Data Boost
Add a **CORDIS participants** slice for AT (2015–2025) to `data/raw/source=cordis/country=AT/date=<YYYY-MM-DD>/participants.csv`, then run `make normalize-all COUNTRY=AT` and rebuild.
```

## Save and confirm
After computing and writing the file, print exactly:
```
WRITE reports/country=AT/phase-2_landscape.md
```

