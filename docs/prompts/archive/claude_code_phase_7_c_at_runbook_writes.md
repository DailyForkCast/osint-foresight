# Claude Code — Phase 7C (Austria, AT) — Runbook & Writes

## Goal
Render the **PRC Interest & MCF Acquisition Assessment** for Austria with doctrine alignment, mechanism mapping, counterparty screening, and optional vignettes. Keep all legal/sanctions references as **signals only** and **exclude US persons**.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-7c_prc_mcf.md`
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑7C report
- Write the companion canvas **“Write Austria Phase 7C — PRC Interest & MCF Assessment (reports/country=AT/phase-7c_prc_mcf.md)”** to that exact path.

## 2) Create TSV scaffolds (idempotent)
Create these with headers (append if exist). If no rows yet, include a `notes` column with `no_data_yet=true`.

- `data/processed/country=AT/p7c_interest_assessment.tsv`
  Columns: `capability_cluster,short_rationale,signal_types,confidence_LMH,notes`

- `data/processed/country=AT/p7c_policy_refs.tsv`
  Columns: `jurisdiction,doc_type,title_or_ref,year,themes,why_it_matters,evidence_link,notes`

- `data/processed/country=AT/p7c_mo_map.tsv`
  Columns: `mo_id,mechanism,at_plausibility_0_3,why_here,local_hooks,watch_signals,notes`

- `data/processed/country=AT/p7c_acquisition_signals.tsv`
  Columns: `date_or_window,mechanism,counterparty,country,what_happened,source_ref,evidence_strength_0_3,notes`

- `data/processed/country=AT/p7c_counterparty_flags.tsv`
  Columns: `counterparty,country,flag_type,source_ref,notes`

- `data/processed/country=AT/p7c_vignettes.tsv` (optional)
  Columns: `rank,topic,vignette_120w,rationale,evidence_refs,notes`

- `data/processed/country=AT/p7c_early_indicators.tsv`
  Columns: `indicator,why_it_matters,collection_hint,notes`

## 3) Populate from existing inputs
- Bring edges from `international_links.tsv`, roles from `standards_roles.tsv`, programs from `programs.csv`, and PRC checks from `prc_screen.tsv`.
- If `sanctions_hits.csv` exists, keep **non‑US only** mentions as **signals** and add to `p7c_counterparty_flags.tsv` (with source links & dates).

## 4) Policy corpora (manual, free sources)
- Add 8–12 entries each to `policy_PRC.tsv`, `policy_AT.tsv`, `policy_EU.tsv` under `data/processed/country=AT/` or `data/processed/global/` (your choice).
  Columns: `jurisdiction,doc_type,title_or_ref,year,themes,why_it_matters,evidence_link`.

## 5) Evidence Register discipline
For every policy PDF or portal saved, append to `data/evidence_register.tsv`:
`id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 6) Health & report tasks
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 7) Commit
`feat(AT): phase‑7C PRC interest & MCF assessment — policy refs, MO map, signals, flags`

---

### Optional VS Code task: phase‑7c:bootstrap
```jsonc
{
  "label": "phase-7c:bootstrap",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "import os; p='data/processed/country=${input:countryCode}'; os.makedirs(p, exist_ok=True);\n"+
    "open(p+'/p7c_interest_assessment.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7c_policy_refs.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7c_mo_map.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7c_acquisition_signals.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7c_counterparty_flags.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7c_vignettes.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7c_early_indicators.tsv','a+',encoding='utf-8').close(); print('ok')"
  ],
  "problemMatcher": []
}
```

### Notes
- Vignettes are **optional** for now; include only if 1–5 credible topics emerge.
- Keep all PRC/sanctions mentions as **signals only**; avoid US‑person references entirely.
