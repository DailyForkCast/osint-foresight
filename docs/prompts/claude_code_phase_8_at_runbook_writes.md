# Claude Code — Phase 8 (Austria, AT) — Runbook & Writes

## Goal
Produce the **Foresight & Early Warning (2y/5y/10y)** snapshot for Austria, including baseline and alternative scenarios, early‑warning indicators with thresholds, a PRC‑relevant targeting view (signals‑only), and an optional intervention menu. Keep sanctions/legal mentions **signals‑only** and **exclude US persons**.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-8_foresight.md`
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑8 report
- Write the companion canvas **“Write Austria Phase 8 — Foresight & Early Warning (reports/country=AT/phase-8_foresight.md)”** to that exact path. Create directories if needed.

## 2) Scaffold TSVs (idempotent)
Create these files with headers. If empty, insert one `notes=no_data_yet=true` row.

- `data/processed/country=AT/p8_baseline.tsv`  
  Columns: `cluster_id,cluster_name,2027_outlook_0_3,2030_outlook_0_3,2035_outlook_0_3,drivers,drags,confidence_LMH,notes`

- `data/processed/country=AT/p8_scenarios.tsv`  
  Columns: `scenario_id,horizon,scenario_family,title,short_path,implications,confidence_LMH,notes`

- `data/processed/country=AT/p8_wildcards.tsv`  
  Columns: `wildcard_id,horizon,title,trigger,first_order_effect,second_order_effect,notes`

- `data/processed/country=AT/p8_ewi.tsv`  
  Columns: `indicator_id,indicator,threshold,favours_scenario,collection_plan,source_hint,notes`

- `data/processed/country=AT/p8_targeting.tsv`  
  Columns: `cluster_id,mechanism,2y_attraction_0_3,5y_attraction_0_3,10y_attraction_0_3,rationale,notes`

- `data/processed/country=AT/p8_interventions.tsv` (optional)  
  Columns: `intervention_id,class,what,why_linked_to_evidence,effort_1to3,owner_hint,notes`

## 3) Populate from prior phases
- Read `capability_heat.tsv`, `risk_register.tsv`, `p7c_mo_map.tsv`, `p7c_early_indicators.tsv`, `international_links.tsv`, `programs.csv`, `AccreditedLabs.tsv`, and `domain_maturity.tsv` to seed **baseline** and **scenarios**.
- Map **EWIs** to concrete collection plans (e.g., Datatracker diffs, accreditation scrape cadence, CORDIS export deltas, LEI/OC merges).

## 4) Evidence Register discipline
Append any policy/portal/scope documents to `data/evidence_register.tsv` with:  
`id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 5) Health & reports
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 6) Commit
`feat(AT): phase‑8 foresight — baseline/scenarios/EWIs/targeting (+ optional interventions)`

---

### Optional VS Code task: phase‑8:bootstrap
```jsonc
{
  "label": "phase-8:bootstrap",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "import os; p='data/processed/country=${input:countryCode}'; os.makedirs(p, exist_ok=True);\n"+
    "open(p+'/p8_baseline.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p8_scenarios.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p8_wildcards.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p8_ewi.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p8_targeting.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p8_interventions.tsv','a+',encoding='utf-8').close(); print('ok')"
  ],
  "problemMatcher": []
}
```

### Notes
- Treat **targeting** scores as **signals‑only** and integrate with Phase 7C narratives.
- EWIs should be **few and measurable**; aim for 3–7 indicators you can realistically track quarterly.

