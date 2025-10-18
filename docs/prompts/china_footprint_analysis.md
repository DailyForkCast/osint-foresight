perfect—here’s a drop-in, field-aware prompt for Claude Code that produces a real **China Footprint Analysis** across your sources (USAspending, TED, CORDIS, OpenAlex, Patents, SEC-EDGAR). It replaces naive keyword counting with country codes, org metadata, transliterations, and alias dictionaries, and it outputs auditable evidence tables you can slice by country/region/aggregate, time (month/year/decade), tech, and org.

---

# Prompt for Claude Code
**Title:** China Footprint Analysis — Field-Aware, Multilingual, Evidence-First (v1.0)

**Operator intent (read me first):**
Perform a **substantive, auditable China footprint analysis** across all loaded datasets. Do not rely on raw substring hits. Use **field-aware detection** (country codes, org metadata, registries), **transliteration + aliases**, and **entity resolution**. Produce evidence tables that can be grouped **by country, region, aggregate; by month, year, 10-year; by technology; by organization**. All claims must cite filepaths/row ids or query hashes. No fabrication.

## Session header
- SESSION_ID: `china_fp_{YYYYMMDD}_{hhmm}_v1`
- ROOT_DIR: `.` (override with ENV: ROOT_DIR)
- OUTPUT_DIR: `./_china_fp/{SESSION_ID}`
- LOCALE_LANGS: `["en","local_language_candidates","zh"]`
- DEFAULT_ENCODINGS: try `utf-8`, fallback `utf-8-sig`, then `latin-1` (log chosen)
- CONFUSABLES_MAP: enable Unicode confusables normalization
- JSON_FLATTEN: depth=2 (overflow to `{field}_json`)
- RANDOM_SEED: 42 (for any sampling)

---

## China footprint: detection logic (tiers)
Define **positive signals** at three confidence tiers. Record the tier for each match.

- **Tier A (high confidence, structured):**
  - Country fields equal `CN`, `CHN`, or ISO-mapped China in standardized geography columns.
  - Org/assignee domiciled in China via authoritative IDs (e.g., ROR/GRID/LEI) or country-of-registration = China.
  - Patents: applicant/assignee country = China; inventor affiliation in China.
  - SEC-EDGAR: registrant/incorporation/address in China; significant subsidiary in China.

- **Tier B (medium, entity resolution / aliasing):**
  - Organization normalized to a Chinese entity via alias table or fuzzy match (Jaro/Levenshtein) with **transliteration** (e.g., 华为/华為 → Huawei; 中兴 → ZTE).
  - Known Chinese parent/subsidiary relationship from ownership tables (e.g., GLEIF/LEI mapping) or curated list.

- **Tier C (supporting, contextual):**
  - Chinese city/province names in structured location fields (北京/Beijing, 上海/Shanghai, 深圳/Shenzhen, etc.).
  - Contract/performance locations in China when org country not set.
  - Co-authorship/award collaboration with Chinese institutions (OpenAlex/CORDIS linkages).

> Store the **rationale** and **evidence fields** driving each tier assignment.

---

## Inputs you should auto-discover or create (and save to OUTPUT_DIR)
1. **Alias dictionaries**
   - `entities/china_aliases.csv`: columns `{raw, norm, script, transliteration, source}` (seed with anything you find locally: org lists, prior runs; add discovered variants).
   - `entities/city_province_list.csv`: major CN cities/provinces in EN/zh with variants.

2. **Registries / crosswalks (if present)**
   - ROR/GRID → country; GLEIF/LEI → legal jurisdiction & ultimate parent; SEC subsidiaries → country.

3. **Technology taxonomy**
   - Load or create `tech/taxonomy.csv` with categories (AI, quantum, semiconductors/microelectronics, biotech, space/satellite, advanced materials, photonics, robotics, cyber/5G, energy storage, etc.) and keyword/IPC/CPC/HS cues. You may reuse existing taxonomy if found.

---

## Per-source extraction (field-aware)

### USAspending (SQLite/CSV/Parquet)
- Keys: `recipient_name`, `recipient_duns/uei`, `recipient_country_code`, `recipient_parent_name`, `place_of_performance_country_code`, NAICS/PSC, `awarding_agency`.
- China signal rules: any recipient or place_of_performance mapped to **CN**; parent/ultimate in CN; recipients matched via alias/resolution.
- Output: `usa_spending_china.csv` with columns
  `{contract_id, fiscal_year, recipient_norm, country_resolved, perf_country_resolved, tier, tech_tags[], amount, awarding_agency, evidence_fields{...}}`.

### TED (EU procurement)
- Keys: buyer/supplier countries (ISO), CN/TED IDs, participant org names, CPV codes.
- China rules: participant country=CN; supplier resolved to CN entity; performance location in CN.
- Output: `ted_china.csv` with `{notice_id, year, org_norm, role(buyer/supplier), country_resolved, cpv, tier, tech_tags[], value_eur, evidence_fields{...}}`.

### CORDIS (EU research funding)
- Keys: participant country codes, org names/IDs, project dates, H2020/FP tags.
- China rules: any participant with country=CN; partner org resolved to CN; collaborating EU-CN projects.
- Output: `cordis_china.csv` with `{project_id, start_date, end_date, participant_norm, participant_country, tier, tech_tags[], evidence_fields{...}}`.

### OpenAlex (publications/affiliations)
- Keys: author affiliations, institution ROR IDs, country metadata.
- China rules: institution country=CN; author affiliation resolved to CN; co-authorship with CN.
- Output: `openalex_china.csv` with `{work_id, pub_year, author_id, institution_norm, institution_country, tier, tech_tags[], evidence_fields{...}}`.

### Patents (USPTO/EPO/WIPO JSON)
- Keys: applicant/assignee names, applicant_country, inventor_country, IPC/CPC codes.
- China rules: applicant/assignee/inventor country=CN; resolved CN org; IPC codes linked to sensitive tech.
- Output: `patents_china.csv` with `{patent_id, filing_date, applicant_norm, applicant_country, inventor_country, tier, tech_tags[], evidence_fields{...}}`.

### SEC-EDGAR (10-K, filings)
- Keys: registrant name, address, subsidiaries table, incorporation country.
- China rules: registrant/incorporation=CN; subsidiary in CN; address fields normalized to CN.
- Output: `sec_edgar_china.csv` with `{filing_id, filing_year, company_norm, country_resolved, subsidiary_norm, tier, tech_tags[], evidence_fields{...}}`.

---

## Fusion & aggregation tasks
1. Merge all per-source outputs into `china_fp_master.csv` with unified schema.
2. Build aggregate tables:
   - By country & year
   - By region & decade
   - By technology & tier
   - By organization (top CN-linked recipients/suppliers/collaborators)
3. Create summary report `china_fp_report.md` with:
   - BLUF (main findings, scale of CN presence)
   - Heatmaps (country-year, tech-year)
   - Top entities & projects
   - Tier distribution (A/B/C)
   - Known gaps & false negative risks

---

## Outputs required
- `{OUTPUT_DIR}/usa_spending_china.csv`
- `{OUTPUT_DIR}/ted_china.csv`
- `{OUTPUT_DIR}/cordis_china.csv`
- `{OUTPUT_DIR}/openalex_china.csv`
- `{OUTPUT_DIR}/patents_china.csv`
- `{OUTPUT_DIR}/sec_edgar_china.csv`
- `{OUTPUT_DIR}/china_fp_master.csv`
- `{OUTPUT_DIR}/china_fp_report.md`
- `{OUTPUT_DIR}/logs/query_log.jsonl` (with hashed query terms)

---

## Execution notes
- **No fabrication.** Each claim must reference `path+row_id` or query.
- **Multilingual:** normalize EN/zh terms, transliterations, confusables.
- **Evidence-first:** include sample evidence rows per match.
- **Performance:** stream large files; log truncations.
- **Safety:** do not output raw PII; counts only for NER.
- **Reproducibility:** record versions of libraries used.
