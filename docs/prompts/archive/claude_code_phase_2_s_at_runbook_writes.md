# Claude Code — Phase 2S (Austria, AT) — Runbook & Writes

## Goal
Produce the Phase 2S Supply‑Chain snapshot for Austria and create/update TSVs the analysis can consume. Keep it flexible: if a node type doesn’t exist, write **no rows** (not forced) or a single `no_data_yet=true` note.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-2s_supply_chain.md`
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑2S report
- From the companion canvas **“Write Austria Phase 2S — Supply Chain Exposure (reports/country=AT/phase-2s_supply_chain.md)”**, write to that exact path. Create directories if needed.

## 2) Create TSVs (idempotent)
Create these with headers; include a `notes` column. If empty, either leave 0 rows or include one `no_data_yet=true` row.

- `data/processed/country=AT/supply_nodes.tsv`  
  Columns: `node_id,node_type,name,location,role,relevance_note,notes`

- `data/processed/country=AT/exposure_vectors.tsv`  
  Columns: `vector_id,vector_type,description,likely_goods_or_knowledge,detection_anchor,related_phases,severity_1to3,likelihood_LMH,confidence_LMH,notes`

- `data/processed/country=AT/logistics_routes.tsv`  
  Columns: `route_id,origin,via,destination,mode,goods_class,notes`

- (Optional overlay) `data/processed/country=AT/supplychain_sanctions.csv`  
  Columns: `list_name,entity_name,country,link,last_check,notes`  
  **Exclude US persons**; signals‑only.

## 3) Optional pulls to support this phase
```
make pull-gleif COUNTRY=AT
python -m src.pulls.opencorporates_pull --country AT --out data/raw/source=opencorporates/country=AT
python -m src.normalize.gleif_to_cer --country AT
python -m src.normalize.opencorporates_to_cer --country AT
```
This should produce/refresh `cer_master.csv` and `institutions.csv`.

## 4) Evidence register
If you added operator docs/portals, append to `data/evidence_register.tsv` with the usual schema.

## 5) Health & reports
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 6) Commit
`feat(AT): phase‑2S supply‑chain snapshot + TSV scaffolding`

---

### Optional VS Code task
Add a convenience task to run the TSV bootstrap for 2S:
```jsonc
{
  "label": "phase-2s:bootstrap",
  "type": "shell",
  "command": "python",
  "args": ["-c", "import os;import csv;import sys;p='data/processed/country=AT';os.makedirs(p,exist_ok=True);print('ok')"],
  "problemMatcher": []
}
```
(Replace hard‑coded `AT` with `${input:countryCode}` if you prefer.)

