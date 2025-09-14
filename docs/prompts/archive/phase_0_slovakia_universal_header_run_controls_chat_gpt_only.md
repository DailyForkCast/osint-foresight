# Phase X — Universal Header & Run Controls (ChatGPT‑only)

## Variables & Horizons (Instantiated for Slovakia)

```python
COUNTRY = "Slovakia"
TIMEFRAME = "2015–present"
HORIZONS = {2y, 5y, 10y}

# Regional comparators
REGIONAL_COMPARATORS_PRIMARY = ["Czechia", "Poland", "Hungary"]   # Visegrád Group (V4)
REGIONAL_COMPARATORS_ALT = ["Austria", "Slovenia", "Germany"]      # Border/CE neighbors
```

## Language Policy (Local + Chinese coverage by default)

```python
LOCAL_LANGS = ["sk"]                                # Slovak
LANGS_SEARCH = ["en"] + LOCAL_LANGS + ["zh"]        # broaden queries across EN/SK/ZH
LANGS_OUTPUT = ["en"]                                # main narrative in English
CHINA_SECTIONS_LANGS = ["zh", "en"] + LOCAL_LANGS    # PRC-related sections include Chinese by default

# Notes
# - PRC sections must include Chinese-language sources.
# - Retain original-language strings and provide an English gloss.
# - Capture multilingual entity names: native script + romanization/transliteration when relevant.
# - Mark machine translations and keep the original string in the source log.
```

## Seed Query-Tokens (EN • ZH • SK) — expandable later

> Use these as starting points to build multilingual search strings; extend per phase.

```python
TOKENS = {
  "semiconductors": {
    "en": ["semiconductor", "chip", "integrated circuit"],
    "zh": ["半导体", "芯片", "集成电路"],
    "sk": ["polovodič", "mikročip", "integrovaný obvod"]
  },
  "ai_ml": {
    "en": ["artificial intelligence", "machine learning"],
    "zh": ["人工智能", "机器学习"],
    "sk": ["umelá inteligencia", "strojové učenie"]
  },
  "quantum": {
    "en": ["quantum", "quantum technologies", "quantum computing"],
    "zh": ["量子", "量子技术", "量子计算"],
    "sk": ["kvantový", "kvantové technológie", "kvantové počítače"]
  },
  "research_innovation": {
    "en": ["research", "innovation", "Horizon Europe", "Horizon 2020"],
    "zh": ["研究", "创新", "地平线欧洲", "地平线2020"],
    "sk": ["výskum", "inovácie", "Horizont Európa", "Horizont 2020", "grant"]
  },
  "defense_security": {
    "en": ["defense", "dual-use", "export controls"],
    "zh": ["国防", "两用", "出口管制"],
    "sk": ["obrana", "dvojité použitie", "exportné kontroly"]
  },
  "collab_terms": {
    "en": ["MoU", "joint research", "research agreement"],
    "zh": ["谅解备忘录", "联合研究", "研究协议"],
    "sk": ["memorandum o porozumení", "spoločný výskum", "dohoda o výskume"]
  }
}

# Example entity-name rules
# EN: "Ministry of Education, Science, Research and Sport" (MESRS)
# ZH: 保留中文官方或媒体常用译名（如有）
# SK: "Ministerstvo školstva, vedy, výskumu a športu SR"; "Slovenská akadémia vied (SAV)"
```

## Toggles (true/false)

```python
INCLUDE_EXPORT_CONTROLS = true       # EU Dual-Use + EAR/ITAR touchpoints & screening gaps
INCLUDE_US_NATSEC_FRAMEWORK = true   # 8-dimension lens + ratings annex
INCLUDE_EWI_CHECKLIST = true         # Early Warning Indicators overlay + Phase-8 signals
INCLUDE_DATA_PULLS = true            # CORDIS/OpenAIRE/Crossref/Patents/News (Phases 2–5)
INCLUDE_COLLAB_MAPPING = true        # network graphing (Phase 3)
INCLUDE_CHINESE_LANG_SOURCES = true  # enforce CN-language coverage where applicable
INCLUDE_LOCAL_LANG_SOURCES   = true  # enforce Slovak-language coverage across phases
CITE_SOURCES = true                  # inline citations & source log
ENABLE_PARALLEL_PROCESSING = true    # run independent ops in parallel when possible
ENABLE_WEBSEARCH = true              # use web search for recency-sensitive items
ENABLE_VALIDATION = true             # post-phase validation checks

# OPTIONAL — only when explicitly requested
INCLUDE_INTERVENTIONS = false        # Phase 6 capacity-building programs (OFF by default)
```

## Operating Principles

- Narrative independence with explicit uncertainty labeling.
- Bidirectional workflow: questions → data pulls; data → stress-test narrative.
- Follow-the-money mindset; adversarial posture on PRC-linked vectors (licit/gray/illicit).
- **PARALLEL FIRST** for independent tasks; **CACHE AWARE** (15‑min TTL) for fetches.
- **FAIL GRACEFULLY**: proceed with partial data; emit clear DATA REQUEST blocks.
- **HORIZONED CLAIMS**: tie forward-looking statements to {2y, 5y, 10y}.

## Universal Checklist Hooks (abbrev.)

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

## Enhanced Output Formats

```python
ENHANCED_OUTPUT_FORMATS = {
  "structured_data": {
    "CSV": {"separator": ",", "encoding": "utf-8", "header": true},
    "JSON": {"indent": 2, "ensure_ascii": false},
    "GRAPHML": {"directed": true}
  },
  "narrative": {
    "exec_summary": {"length": "~400–600 words", "bullets": true},
    "policy_brief": {"length": "2–3 pages", "audience": "policy/leadership"}
  }
}
```

## Source Logging & Citations

- Inline citations for non-obvious claims.
- Maintain a source log with URL, title, author, date, language, access date, and a one‑line rationale for inclusion.
- For translated content, keep original quote + English gloss in the log.
- Note and reconcile conflicts across sources; document rationale.

## Evidence Handling

- Prefer primary sources; clearly mark secondary sources.
- Tag low‑confidence or speculative statements and map them to HORIZONS.

## Universal DATA REQUEST (when something is unavailable)

```
DATA REQUEST — Slovakia / Phase X
• Specific data needed: …
• Suggested sources/platforms: …
• Language(s): EN, SK, (ZH if PRC‑related)
• Date range: 2015–present (override if needed)
• Why it matters for the next phase: …
```

## Outputs (Phase X)

- Ready‑to‑run header (variables, language policy, toggles) for subsequent phases.
- Shared Operating Principles block inherited by all phases.
- Universal checklist + output‑format guidance to standardize deliverables.
- Citation and evidence‑handling policy.

## File/Folder Conventions (Slovakia)

- Base path: `/out/Slovakia/phaseX/`
- Filenames: `Slovakia_phaseX_{artifact}_{YYYYMMDD}.md|json|csv|graphml`
- Always write `provenance.json` with source URLs/paths, timestamps, and languages used.

## Operations Policy (summary)

- Respect robots.txt and site terms.
- Add randomized 1–3 s backoff; limit concurrency to 2 when scraping.
- Check a 15‑min cache before new requests.
- If a required format is unavailable (e.g., PDF writer), propose an alternative (MD/DOCX/HTML→PDF via external tool).
- If any capability is blocked, declare it and proceed in OFFLINE_ANALYST mode with a clear DATA REQUEST.
