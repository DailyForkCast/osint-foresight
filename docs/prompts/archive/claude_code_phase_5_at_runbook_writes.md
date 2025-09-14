# Claude Code — Phase 5 (Austria, AT) — Runbook & Writes

## Goal
Render Austria’s **International Links & Collaboration** layer, enforce the **mandatory PRC entities screen**, and scaffold TSVs for heat, vignettes, and counterparts. Prefer free data; degrade gracefully with headers + `no_data_yet=true` rows if thin.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-5_links.md`
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑5 report
- Write the companion canvas **“Write Austria Phase 5 — International Links & Collaboration (reports/country=AT/phase-5_links.md)”** to that exact path. Create directories as needed.

## 2) Ensure source TSVs are present
- `relationships.csv` (edges) — may come from earlier pulls or manual upserts
- `standards_roles.tsv` — IETF roles
- `programs.csv` / `grant_partners.tsv` — optional but helpful

## 3) Create/update Phase‑5 TSVs (idempotent)
Create these (with headers). If no rows yet, add a `notes` column with `no_data_yet=true`.

- `data/processed/country=AT/international_links.tsv`
  Columns: `sector,counterpart_name,counterpart_country,collab_type,year,why_relevant,notes`

- `data/processed/country=AT/phase5_heat.tsv`
  Columns: `country,cluster_id,cluster_name,heat_0_3,last_signal,why,notes`

- `data/processed/country=AT/prc_screen.tsv`
  Columns: `counterpart_name,counterpart_country,flag_type,evidence_ref,why_it_matters,notes`
  **Mandatory** to run for every salient counterpart. Signals‑only. **Exclude US persons.**

- `data/processed/country=AT/phase5_vignettes.tsv`
  Columns: `rank,counterpart_name,counterpart_country,vignette_type,vignette_120w,rationale,evidence_refs,notes`

## 4) Populate from existing data (if available)
- Append edges from `relationships.csv` to `international_links.tsv` (dedupe on `sector+counterpart+year`).
- Derive `phase5_heat.tsv` by grouping on `counterpart_country × cluster` with simple rule:
  `heat = min(3, 1 + recent_edge + diversity)` where `recent_edge` = 1 if last 24 months; `diversity` = 1 if ≥2 link types.

## 5) **Mandatory PRC entities screen**
For each **unique counterpart** (non‑AT) in `international_links.tsv`, screen for PRC nexus (ownership/control, joint labs, CAS/CETC/AVIC/NORINCO ecosystems, ministerial affiliations, industry associations). Record as **signals only** in `prc_screen.tsv` with evidence links. **Do not include US persons.**

## 6) Vignettes (1–5, 120 words each)
Draft short vignettes for the most **promising/concerning** relationships. If none are concerning, explicitly state that. Store in `phase5_vignettes.tsv`.

## 7) Evidence register
For any page or PDF saved, append to `data/evidence_register.tsv`:
`id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 8) Health & report tasks
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 9) Commit
`feat(AT): phase‑5 international links + PRC screen + heat & vignettes`

---

### Optional VS Code task: phase‑5:bootstrap
```jsonc
{
  "label": "phase-5:bootstrap",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "import os; p='data/processed/country=${input:countryCode}'; os.makedirs(p, exist_ok=True);\n"+
    "open(p+'/international_links.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/phase5_heat.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/prc_screen.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/phase5_vignettes.tsv','a+',encoding='utf-8').close(); print('ok')"
  ],
  "problemMatcher": []
}
```

### Note on sanctions/legal overlay
If a counterpart (or parent) appears on **EU/UK/CA/AU/NZ/UN** lists, record it in `sanctions_hits.csv` with links and dates; **exclude US persons**. Treat as signals only.
