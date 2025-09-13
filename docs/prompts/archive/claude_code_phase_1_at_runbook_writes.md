# Claude Code — Phase 1 (Austria, AT) — Runbook & Writes

## Goal
Populate **Phase 1** artifacts for Austria so downstream phases can run. Prefer free/API sources. If a source is thin, still write the files with headers and a `no_data_yet=true` row.

## 0) Paths
- Country code: `AT`
- Reports: `reports/country=AT/phase-1_indicators.md`
- Config: `config/` and `queries/`

## 1) Write the Phase‑1 report (from the companion canvas)
- Save the canvas titled **“Write Austria Phase 1 — Indicators & Data Sources (reports/country=AT/phase-1_indicators.md)”** to that exact path.

## 2) Create indicator catalog TSVs
Create these files (with header rows). If content is empty, include one row with `no_data_yet=true` in a `notes` column.

- `config/indicators/country=AT/indicator_catalog.tsv`  
  Columns: `indicator_id,theme,description,why_it_matters,related_phases,collection_mode`

- `config/indicators/country=AT/source_map.tsv`  
  Columns: `source_id,indicator_id,name,type,access,notes`

- `queries/keywords/country=AT/phasewide_keywords.tsv`  
  Columns: `theme,core_keywords,de_synonyms`

> Use the corresponding tables from the Phase‑1 report as initial content.

## 3) Seed watchlists (text‑intelligence)
- Ensure file exists: `queries/policy/watchlist.yaml`  
  Add (idempotent) entries for: IETF (IPPM,NTP), Akkreditierung Austria, CORDIS AT participants, EuroHPC/VSC notices, EU sanctions CSV, GLEIF AT.

## 4) Optional automated pulls (if you want to wire now)
- **OpenAIRE** (publications/grants): `make pull-openaire COUNTRY=AT`
- **Crossref** (publications): `make pull-crossref COUNTRY=AT`
- **IETF** (roles): `make pull-ietf COUNTRY=AT`
- **GLEIF** (LEIs): `make pull-gleif COUNTRY=AT`

Then normalize minimal slices (safe even with thin data):
```
make normalize COUNTRY=AT
```

## 5) Evidence register hygiene
- Append to `data/evidence_register.tsv` whenever you store a portal PDF or scope:  
  Columns: `id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`

## 6) Sanctions/legal (signals‑only; **exclude US persons**)
- Create placeholder: `data/processed/country=AT/sanctions_hits.csv`  
  Columns: `list_name,entity_name,country,link,last_check,notes`  
  Add one row with `no_data_yet=true` if empty.

## 7) Health & reports
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 8) Commit
- Commit all writes with a message like:  
  `feat(AT): phase‑1 indicators catalog, sources map, keyword seeds + report`

---

### Quick sanity checklist
- [ ] Report file written to `reports/country=AT/phase-1_indicators.md`
- [ ] TSVs under `config/indicators/country=AT/` created from tables
- [ ] Phase‑wide keyword TSV present under `queries/keywords/country=AT/`
- [ ] Watchlist YAML has AT entries (IETF, accreditation, CORDIS, EuroHPC/VSC, sanctions, GLEIF)
- [ ] Optional pulls & normalize completed without errors
- [ ] Evidence register updated for any saved PDFs
- [ ] Health check passes (or logs “no_data_yet” rows)

