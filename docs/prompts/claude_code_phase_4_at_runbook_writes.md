# Claude Code — Phase 4 (Austria, AT) — Runbook & Writes

## Goal
Create the **Funding & Instruments** layer for Austria. Prefer free sources; degrade gracefully with headers + `no_data_yet=true` rows if information is thin.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-4_funders.md`
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑4 report
- Take the companion canvas titled **“Write Austria Phase 4 — Funding & Instruments (reports/country=AT/phase-4_funders.md)”** and write it to the exact path above. If the directory doesn’t exist, create it.

## 2) Create TSV/CSV scaffolds (idempotent)
Create these files with headers (append if exist). If empty, add one row with `notes=no_data_yet=true`.

- `data/processed/country=AT/funders.tsv`  
  Columns: `funder_id,name,org_type,level,website,mandate_summary,notes`

- `data/processed/country=AT/instruments.tsv`  
  Columns: `instrument_id,name,type,typical_ticket,maturity,cofunding?,why_it_matters,notes`

- `data/processed/country=AT/programs.csv`  
  Columns: `program_id,funder_id,title,year,topic_tags,url,at_participation,notes`

- `data/processed/country=AT/calls.tsv`  
  Columns: `call_id,funder_id,title,open_date,close_date,topics,url,notes`

- `data/processed/country=AT/grant_partners.tsv`  
  Columns: `edge_id,program_id,partner_name,partner_country,role,why_relevant,notes`

- `data/processed/country=AT/funding_signals.tsv`  
  Columns: `window,signal_summary,likely_driver,notes`

## 3) Optional: CORDIS pull (free) — if the pull module exists
```
python -m src.pulls.cordis_pull --country AT --years 2015-2025 --topics cluster4,cluster5 --keywords-file queries/keywords/country=AT/phaseX_keywords.yaml --out data/raw/source=cordis/country=AT
python -m src.normalize.cordis_to_programs --country AT
```
This should produce/update `programs.csv` and `grant_partners.tsv`.

## 4) National portals
If you don’t have a puller for national funders yet, do a **manual pass**:
- FFG: list last 10 relevant calls (AI/HPC/EMC/GNSS/NDT) → `calls.tsv`
- FWF: add program families (e.g., Stand‑Alone Projects) → `programs.csv`
- aws: note innovation/SME instruments → `instruments.tsv`
Record URLs and dates, and append the sources to `data/evidence_register.tsv`.

## 5) Evidence register
For each portal page saved, append to `data/evidence_register.tsv`:  
`id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 6) Health & report tasks
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 7) Commit
`feat(AT): phase‑4 funders & instruments; programs/calls/partners scaffolds + report`

---

### Optional VS Code task: phase‑4:bootstrap
```jsonc
{
  "label": "phase-4:bootstrap",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "import os, csv; p='data/processed/country=${input:countryCode}'; os.makedirs(p, exist_ok=True);\n"+
    "open(p+'/funders.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/instruments.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/programs.csv','a+',encoding='utf-8').close();\n"+
    "open(p+'/calls.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/grant_partners.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/funding_signals.tsv','a+',encoding='utf-8').close(); print('ok')"
  ],
  "problemMatcher": []
}
```

### Sanctions/legal overlay (signals‑only; **non‑US persons**)
If any consortium partner or intermediary appears on EU/UK/CA/AU/NZ/UN lists, record as **signals** in `sanctions_hits.csv` with explicit source links and dates. **Exclude US persons** entirely.

