# Claude Code — Phase 6 (Austria, AT) — Runbook & Writes

## Goal
Render the **Risk Assessment & Best‑Practice Verification** layer for Austria, including a transparent risk register, control evidence, and short vignettes. Enforce the **non‑US persons** rule for sanctions/legal signals.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-6_risk.md`
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑6 report
- Take the companion canvas **“Write Austria Phase 6 — Risk Assessment & Best‑Practice Verification (reports/country=AT/phase-6_risk.md)”** and write to that exact path.

## 2) Scaffold TSVs (idempotent)
Create these files with headers; include a `notes` column where useful. If no rows, add one `no_data_yet=true` row.

- `data/processed/country=AT/risk_vectors.tsv`
  Columns: `vector_id,name,definition,exemplar_observables,related_phases,notes`

- `data/processed/country=AT/risk_register.tsv`
  Columns: `risk_id,vector_id,cluster_id,context,severity_1to3,likelihood_LMH,confidence_LMH,evidence_refs,notes`

- `data/processed/country=AT/control_evidence.tsv`
  Columns: `control_id,control_name,where_observed,applies_to_vector,strength_0_3,evidence_refs,notes`

- `data/processed/country=AT/phase6_vignettes.tsv`
  Columns: `rank,risk_id,vignette_120w,rationale,evidence_refs,notes`

- (Already present in earlier phases) `sanctions_hits.csv` (signals‑only; **exclude US persons**)

## 3) Populate from existing inputs
- Use `capability_heat.tsv`, `AccreditedLabs.tsv`, `standards_roles.tsv`, and `international_links.tsv` to propose initial rows in `risk_register.tsv`.
- Bring over **PRC screen** hints from `prc_screen.tsv` only as **context**; keep signals separate from determinations.

## 4) Evidence discipline
- For every policy page, scope PDF, or portal saved, append to `data/evidence_register.tsv`:
  `id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 5) Health & reports
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 6) Commit
`feat(AT): phase‑6 risk register + control evidence + vignettes + report`

---

### Optional VS Code task: phase‑6:bootstrap
```jsonc
{
  "label": "phase-6:bootstrap",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "import os; p='data/processed/country=${input:countryCode}'; os.makedirs(p, exist_ok=True);\n"+
    "open(p+'/risk_vectors.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/risk_register.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/control_evidence.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/phase6_vignettes.tsv','a+',encoding='utf-8').close(); print('ok')"
  ],
  "problemMatcher": []
}
```

### Sanctions/legal overlay
If any party appears on **EU/UK/CA/AU/NZ/UN** lists, record in `sanctions_hits.csv` with URLs and dates; **exclude US persons**. Treat as **signals only**.
