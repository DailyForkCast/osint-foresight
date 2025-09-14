# Claude Code — Phase 3 (Austria, AT) — Runbook & Writes

## Goal
Build the **Institutional Map** for Austria with emphasis on **accreditation‑backed capabilities** and a clean join layer for downstream phases. Prefer low‑cost/manual‑friendly steps that the solo analyst can sustain.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-3_institutions.md`
  (Use the companion canvas titled **“Write Austria Phase 3 — Institutional Map & Accredited Labs (reports/country=AT/phase-3_institutions.md)”**.)
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑3 report
- Write the companion canvas to the exact report path above. Create directories if needed.

## 2) Bootstrap TSVs (idempotent)
Create these files with headers. If nothing to add yet, include one `notes` column row with `no_data_yet=true`.

- `data/processed/country=AT/AccreditedLabs.tsv`
  Columns: `org_name,alt_name_local,cab_code,accreditation_standard,program,cert_no,status,valid_to,scope_link,scope_text_hash,technical_fields,site_address,website,last_check,evidence_id,notes`

- `data/processed/country=AT/roster.tsv`
  Columns: `person_name,role,org_name,country,standard_or_wg,contact_link,last_check,evidence_id`

- `data/processed/country=AT/institutions.csv`
  Columns: `institution_id,name,alt_names,org_type,city,country,website,accreditation_flags,clusters,key_subdomains,source_refs,last_check,notes`

- `data/processed/country=AT/capability_heat.tsv`
  Columns: `cluster_id,name,capability_0_3,rationale,supporting_refs`

> If `standards_roles.tsv` exists, you **don’t** need to rewrite it; just read and summarize for the report.

## 3) Optional scraper hook (manual now, code later)
- Manual pass: use the national registry search by **standard** + **field** (EMC/RED, RF/microwave, time/frequency/GNSS, optics/photonics, NDT, AM). Copy the entries and paste into `AccreditedLabs.tsv`.
- If/when you want automation, create `src/pulls/accreditation_pull.py` (Playwright) to iterate queries and download scope PDFs; compute SHA‑256 and write `scope_text_hash`. (Not required to complete Phase 3.)

## 4) Evidence register discipline
- For any scope PDFs or portal pages saved, append to `data/evidence_register.tsv` with:
  `id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 5) Integrations (optional but helpful)
- If you’ve pulled `GLEIF` / `OpenCorporates`, you can enrich `institutions.csv` with LEI or registry links and **org_type=company** rows for key suppliers.
- Merge `standards_roles.tsv` people/orgs into `roster.tsv` (dedupe by `person_name+org_name`).

## 6) Health & rebuild
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 7) Commit
`feat(AT): phase‑3 institutions map + accredited labs roster + capability heat`

---

### Optional VS Code task: phase‑3:bootstrap
Add a small task to create the TSVs above if missing.

```jsonc
{
  "label": "phase-3:bootstrap",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "import os, csv; p='data/processed/country=${input:countryCode}'; os.makedirs(p, exist_ok=True);\n"+
    "open(p+'/AccreditedLabs.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/roster.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/institutions.csv','a+',encoding='utf-8').close();\n"+
    "open(p+'/capability_heat.tsv','a+',encoding='utf-8').close(); print('ok')"
  ],
  "problemMatcher": []
}
```
(If you want headers auto‑written, mirror the pattern used in the Phase‑2 bootstrap helper.)

---

### Quick checklist
- [ ] Report saved to `reports/country=AT/phase-3_institutions.md`
- [ ] TSVs created with headers (and optional `no_data_yet=true` rows)
- [ ] Evidence register updated for any saved scopes
- [ ] Health/report tasks run cleanly
- [ ] Commit created with clear message
