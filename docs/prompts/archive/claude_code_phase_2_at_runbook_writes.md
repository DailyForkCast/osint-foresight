# Claude Code — Phase 2 (Austria, AT) — Runbook & Writes

## Goal
Render the **Phase 2 Technology Landscape** for Austria, wiring data that already exists and creating/update TSVs so downstream phases can consume consistent outputs. Prefer free sources; degrade gracefully with `no_data_yet=true` when thin.

## 0) Paths & Inputs
- Country: `AT`
- Report to write: `reports/country=AT/phase-2_landscape.md` (from the companion canvas)
- Inputs used if present:  
  `data/processed/country=AT/relationships.csv`,  
  `data/processed/country=AT/signals.csv`,  
  `data/processed/country=AT/standards_roles.tsv`

## 1) Save the report
- Save the canvas titled **“Write Austria Phase 2 — Technology Landscape (reports/country=AT/phase-2_landscape.md)”** exactly to that path.

## 2) Ensure minimal processed TSVs exist (idempotent)
Create files if missing (write headers even if empty, with an optional `notes` column and a single `no_data_yet=true` row):
- `data/processed/country=AT/relationships.csv`
- `data/processed/country=AT/signals.csv`
- `data/processed/country=AT/standards_roles.tsv`

## 3) Optional pulls (free sources)
Run these as available (tokens optional for OpenCorporates; skip if not configured):
```
make pull-openaire COUNTRY=AT
make pull-crossref COUNTRY=AT
make pull-ietf COUNTRY=AT
make pull-gleif COUNTRY=AT
```

## 4) Normalize
```
make normalize COUNTRY=AT
```
This should (re)build:
- `src/normalize.openaire_to_relationships`
- `src/normalize.crossref_to_relationships`
- `src/normalize.ietf_to_standards_roles`
- `src/normalize.gleif_to_cer`

## 5) (Re)build Phase 2 analysis
Run the analysis script directly so it regenerates derived artifacts and the report’s tables:
```
python -m src.analysis.phase2_landscape --country AT
```
If the script writes derived TSVs, ensure they land under:
- `outputs/country=AT/phase-2/sector_maturity.tsv`
- `outputs/country=AT/phase-2/top_institutions.tsv`
- `outputs/country=AT/phase-2/standards_roles.tsv` (copy‑through)
- `outputs/country=AT/phase-2/signals.tsv` (copy‑through)

## 6) Evidence register hygiene
When you save any scope PDF or official page during manual boosts, append a row to:
- `data/evidence_register.tsv` with: `id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 7) Health & reports
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```
Ensure the Phase‑2 report exists and opens cleanly.

## 8) Commit
Commit all changes with a clear message, e.g.:
```
feat(AT): phase‑2 landscape report + refreshed signals/roles; sector maturity snapshot
```

---

### Quick sanity checklist
- [ ] Report saved to `reports/country=AT/phase-2_landscape.md`
- [ ] Processed inputs exist (relationships/signals/standards_roles)
- [ ] Optional pulls/normalize ran without errors
- [ ] Derived TSVs present under `outputs/country=AT/phase-2/`
- [ ] Evidence register updated for any saved PDFs
- [ ] Health check passes; report renders with tables populated (or clear no‑data notes)

