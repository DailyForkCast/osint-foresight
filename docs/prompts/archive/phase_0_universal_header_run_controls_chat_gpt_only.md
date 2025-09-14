## Phase X - Universal Header & Run Controls

### Variables & Horizons

```python
COUNTRY = {{country_name}}
TIMEFRAME = 2015-present
HORIZONS = {2y, 5y, 10y}

# Regional Comparators (NEW)
REGIONAL_COMPARATORS = {{regional_group}}
# Examples:
# DACH: Germany, Austria, Switzerland
# Nordic: Sweden, Denmark, Norway, Finland, Iceland
# Baltic: Estonia, Latvia, Lithuania
# Benelux: Belgium, Netherlands, Luxembourg
...
```

### Local + Chinese coverage by default

```python
LOCAL_LANGS = {{list local languages, e.g., ["de","fr","it"]}}     # country official/local languages
LANGS_SEARCH = ["en"] + LOCAL_LANGS + ["zh"]                      # default query/search languages
LANGS_OUTPUT = ["en"]                                             # main narrative in English
CHINA_SECTIONS_LANGS = ["zh","en"] + LOCAL_LANGS                  # PRC sections include Chinese by default

# Notes:
# - PRC sections must check Chinese-language sources by default.
# - When quoting or listing sources, retain original language strings + supply an English gloss.
# - Capture multilingual names: native script + romanization (e.g., pinyin) + local transliteration if used.
# - Preserve original-language quotes for key terms; add English gloss in brackets.
# - If automated translation is used, mark segments as machine-translated and include the original string.
# - Include local acronyms and ministry/agency common names.
```

### C. Query Language Sets
For each concept/entity, create language-specific tokens:
- English: ["semiconductor", "chip", "integrated circuit"]
- Chinese: ["半导体", "芯片", "集成电路"]
- Local: [relevant translations in LOCAL_LANGS]

**Rules:**
- EN: "National Science Foundation", NSF
- ZH: "国家自然科学基金委员会", "自然科学基金"
- LOCAL: [local ministry/agency names and acronyms]

### Toggles (true/false)

```python
INCLUDE_EXPORT_CONTROLS = true      # EU Dual-Use + EAR/ITAR touchpoints & screening gaps
INCLUDE_US_NATSEC_FRAMEWORK = true  # 8-dimension lens + ratings annex
INCLUDE_EWI_CHECKLIST = true        # Early Warning Indicators overlay + Phase-8 signals
INCLUDE_DATA_PULLS = true           # CORDIS/OpenAIRE/Crossref/Patents/News (Phases 2-5)
INCLUDE_COLLAB_MAPPING = true       # network graphs (Phase 3)
INCLUDE_CHINESE_LANG_SOURCES = true # enforce Chinese-language coverage on PRC sections
INCLUDE_LOCAL_LANG_SOURCES   = true # enforce local-language coverage across phases
CITE_SOURCES = true                 # inline citations & source log
ENABLE_PARALLEL_PROCESSING = true   # Enable parallel tool execution
ENABLE_WEBSEARCH = true             # Use WebSearch for recent content
ENABLE_VALIDATION = true            # Run post-phase validation checks

# OPTIONAL - Only when explicitly requested
INCLUDE_INTERVENTIONS = false       # Phase 6 capacity building programs (OFF by default)
```

### Operating Principles
Narrative independence; manual flags; graceful degradation on partial data.
Bidirectional intelligence: narrative questions drive data pulls; data stress-tests the narrative.
Follow-the-money mindset; adversarial posture; horizon-based claims (2y/5y/10y).
**PARALLEL FIRST**: Always execute independent operations in parallel.
**CACHE AWARE**: Reuse WebFetch cache (15min TTL) between phases.
**FAIL GRACEFULLY**: Continue with partial data; log failures for human review.
**RESEARCH FOCUS**: Prioritize understanding the current situation before forecasting horizons.

### Universal Checklist Hooks (abbrev.)

```python
CHECKLIST = {
  "provenance": {
    "source_types": ["gov", "thinktank", "academic", "news", "patent", "funding DB"],
    "languages": LANGS_SEARCH,
    "freshness": {"prefer_recent": true, "min_year": 2015}
  },
  "PRC_specific": {
    "MFA/MOST/MIIT": true,
    "talent_programs": true,
    "SOEs_and_POEs": true,
    "front_companies": true,
    "M/LFZ": true
  },
  "EU_specific": {
    "CORDIS_open_projects": true,
    "Horizon_2020/Europe": true,
    "ETAs/EDIDs": true
  },
  "compliance": {
    "export_controls": INCLUDE_EXPORT_CONTROLS,
    "data_protection": true,
    "IP_contracting": true
  },
  "risk": {
    "dual_use_flags": true,
    "funding_anomalies": true,
    "collab_outliers": true,
    "entity_watchlist_hits": true
  },
  "monitoring": {
    "github": {"repo_dependencies": true, "contributor_networks": true},
    "conference_proceedings": {"speaker_affiliations": true},
    "tender_platforms": {"new_rfps": true, "award_notices": true}
  }
}
```

## Enhanced Output Formats (NEW)

```python
ENHANCED_OUTPUT_FORMATS = {
  "structured_data": {
    "CSV": {"separator": ",", "encoding": "utf-8", "header": true},
    "JSON": {"indent": 2, "ensure_ascii": false},
    "GRAPHML": {"directed": true}
  },
  "narrative": {
    "exec_summary": {"length": "~400-600 words", "bullets": true},
    "policy_brief": {"length": "2-3 pages", "audience": "policy/leadership"}
  }
}
```

### Source Logging & Citations
- Inline citations for all non-obvious claims.
- Maintain a source log with URL, title, author, date, language, access date, and a one-line rationale for inclusion.
- For translated content, keep original quote + English gloss in the log.

### Evidence Handling
- Prefer primary sources; when using secondary sources, cite them clearly.
- If multiple sources conflict, note the conflict and supply the most plausible resolution with rationale.
- Label any low-confidence or speculative statements; tie to HORIZONS where relevant.

### Universal Data Request (when offline)
If a required capability or data source is unavailable, output a concise DATA REQUEST block listing:
- Specific data needed
- Suggested sources (by name/platform)
- Language(s)
- Date range
- Why it matters for the next phase

### Outputs (Phase X)
- A ready-to-run header (variables, language policy, toggles) for subsequent phases.
- A shared Operating Principles block that each phase can inherit.
- A universal checklist + output format guidance to standardize deliverables.
- A citation and evidence handling policy section.

### File/Folder Conventions
- Use `/out/{COUNTRY}/phase{N}/` for phase artifacts.
- Filenames: `{COUNTRY}_phase{N}_{artifact}_{YYYYMMDD}.md|json|csv|graphml`.
- Always write `provenance.json` with source URLs/paths, timestamps, and languages used.

### LANGUAGE POLICY (summary)
- Expand queries across LANGS_SEARCH. For PRC sections, always include Chinese queries/keywords.
- Preserve original-language entity names; add transliteration fields where sensible.
- Retain original quotes for key terms with an English gloss in brackets.

### OPERATIONS POLICY (summary)
- Respect robots.txt and site terms.
- Add randomized 1–3s backoff; limit concurrency to 2 when scraping.
- Check a 15‑min cache before new requests.
- If a required format is unavailable (e.g., PDF writing), propose an alternative (DOCX/MD/HTML‑to‑PDF via external tool).
- If any capability is blocked, declare it and proceed in OFFLINE_ANALYST mode with a clear DATA REQUEST.
