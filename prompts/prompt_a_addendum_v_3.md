# Prompt A — Addendum v3.9 — Micro‑Artifacts & Dept‑Level Overlaps (applies to ChatGPT Operator & Claude Code)

**Purpose:** Incorporate micro‑artifacts and institution→department collaboration logic; strengthen US–Italy overlap analysis without dropping evidence when department details are missing.

---

## New micro‑artifacts (create if missing)

### Phase 04 — Supply Chain (US–Italy overlaps)
- **`phase04_sub8_us_italy_supply_overlap.json`**
```json
[{
  "us_prime_or_tier": "prime|tier1|tier2",
  "program": "e.g., F-35|NGJ|Copernicus|EO/ISR",
  "italy_entity_ror": "https://ror.org/...",
  "italy_site": "plant/campus/lab name (if known)",
  "component": "e.g., blisk, EO sensor, HPC module",
  "export_flag": "ITAR|EAR|EU-dual|none",
  "single_source_risk": true,
  "evidence_urls": ["https://…", "https://…"],
  "last_checked": "YYYY-MM-DD"
}]
```

### Phase 06 — Funding & Control
- **`phase06_sub8_us_equity_links.json`**
```json
[{
  "italy_entity_lei": "…",
  "italy_entity_ror": "…",
  "ultimate_parent_country": "US",
  "ownership_pct": 0.23,
  "control_rights": ["board","veto","information"],
  "funding_round_or_deal": "Series B|Acquisition|Grant",
  "program": "(if grant/contract)",
  "year": 2024,
  "evidence_urls": ["https://…"],
  "last_checked": "YYYY-MM-DD"
}]
```

### Phase 07 — Links & Standards
- **`phase07_sub7_us_italy_standards_roles.json`**
```json
[{
  "body": "ETSI|3GPP|ISO|IEC",
  "wg": "…",
  "role": "member|rapporteur|editor",
  "role_weight": 1,
  "org_it_ror": "…",
  "org_us_ror": "…",
  "dept_id_it": "sapienza:phys:nuclear (optional)",
  "dept_id_us": "mit:nse (optional)",
  "person_orcid": "0000-0002-… (optional)",
  "evidence_url": "https://…",
  "year": 2024
}]
```

- **`dept_registry.json`** — canonical department names & aliases per institution
```json
[{"org_ror":"https://ror.org/...","dept_name":"Department of Nuclear Physics","aka":["Dip. Fisica Nucleare"],"dept_id":"sapienza:phys:nuclear","dept_url":"https://…"}]
```

- **`phase07_sub8_dept_collab_pairs.json`** — department↔department edges (fallback to org↔org when dept unknown)
```json
[{
  "country_a": "IT",
  "org_a_ror": "…",
  "dept_a_id": "sapienza:phys:nuclear | null",
  "country_b": "US",
  "org_b_ror": "…",
  "dept_b_id": "mit:nse | null",
  "domain": "Quantum Sensing",
  "outputs": {"pubs":3,"reports":1,"projects":1,"yrs":[2022,2024]},
  "evidence": [{"type":"paper","doi":"…","url":"…","year":2023},{"type":"report","url":"…","year":2024}],
  "last_checked": "YYYY-MM-DD"
}]
```

**Rule:** If department cannot be resolved with ≥2 independent sources, **record org↔org first**, set `dept_*` = null, **do not drop the edge**. Later enrich with department data when found.

---

## Prompt instructions (insertions)

### Phase 04 (Supply Chain) — add after 4.5
- *“Build a **US–Italy overlap** view using `phase04_sub8_us_italy_supply_overlap.json`. Link Italian sites/components to **US primes/programs**; tag **export_flag** and **single_source_risk**; attach exact document URLs. Proceed even if department/site granularity is unknown; add as org-level and flag `site=null`.”*

### Phase 06 (Funding & Control) — add after 6.7
- *“Map **partial US ownership or control** (≥10% or documented control rights) using `phase06_sub8_us_equity_links.json`. Cite **LEI/GLEIF**, filings, and official releases with exact URLs. If only org-level is available, record it; enrich later.”*

### Phase 07 (Links & Standards) — replace first paragraph of 7.1
- *“Resolve collaborations **institution→department**. First, build **org↔org** edges from OpenAIRE/Crossref/CORDIS. Then, where supported by ≥2 sources (author affiliation department + ORCID employment or department webpage), enrich to **dept↔dept** and store in `phase07_sub8_dept_collab_pairs.json`. Do **not** drop edges when department is unknown—use nulls and backfill later.”*

- *“For standards roles, attempt `dept_id_*` via ORCID/institution pages; otherwise keep org-level only. Store to `phase07_sub7_us_italy_standards_roles.json` with **role_weight** and **evidence_url**.”*

### QA — add under Citations
- *“Place bracketed endnote numbers **immediately after the sentence** they support. Maintain an **Endnotes** section with **exact document URLs** and **Accessed** dates. No homepage links.”*

---

## Tickets for Claude (to industrialize)
1) **ORCID employment puller** for Italy/US authors (2019–2025) in target domains; enrich affiliations with departments → `dept_registry.json` + `phase07_sub8_dept_collab_pairs.json`.
2) **Crossref/OpenAIRE affiliation parser** with department extraction and alias matching.
3) **Standards role expander** — resolve `dept_id` where possible and compute `role_weight`.
4) **Ownership joiner** — LEI/GLEIF + filings to populate `phase06_sub8_us_equity_links.json`.
5) **US–Italy supply map** — crosswalk `supply_chain_map.json` with US program/vendor lists to emit `phase04_sub8_us_italy_supply_overlap.json`.
