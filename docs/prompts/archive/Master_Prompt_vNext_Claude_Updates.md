# Deep Research - Intl Research Security
Master Prompt (vNext) - Claude Updates
Phases X, 0-8 + 2S; Language Expansion; Fusion Orchestrator; Claude Runtime & Ops Policy; Capabilities Probe

## Phase X - Universal Header & Run Controls

### Variables & Horizons

```python
COUNTRY = {{country_name}}
TIMEFRAME = 2015-present
HORIZONS = {2y, 5y, 10y}
```
Language Policy (default multilingual)

# Local + Chinese coverage by default

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
```

### Operating Principles
Narrative independence; manual flags; graceful degradation on partial data.
Bidirectional intelligence: narrative questions drive data pulls; data stress-tests the narrative.
Follow-the-money mindset; adversarial posture; horizon-based claims (2y/5y/10y).

### Evidence Order & Style
Priority: 1) primary gov/reg; 2) EU/official DBs; 3) reputable research; 4) major media; 5) org sites; 6) open web.
Date-stamp facts; mark assumptions vs evidence; prefer structured artifacts (tables/CSV/JSON); log conflicts + likely resolution.
PRC-related content: prioritize Chinese-language primary sources (policies, funders, standards bodies, university institutes).
No PII or non-public sensitive details.
Quick Run Instructions
1) Set variables and toggles. 2) Run Phase 0→8 sequentially (2S between 2 and 3); reuse outputs. 3) For Claude Code runs, request CSV/JSON where specified; save GraphML. 4) Compile a country pack: Exec Summary + Phases + Annexes.
Claude Code - Runtime Defaults (based on capabilities audit)
CLAUDE_RUNTIME = {
  "mode": "TOOL_AUGMENTED+ONLINE_QUERY",
  "web": { "method": "WebFetch", "cache_ttl_min": 15 },
  "io":  { "fs_rw": true, "http_downloads": true },
  "exec":{
    "python": true, "node": true, "bash": true, "java": true, "c_cpp": true,
    "cmd_timeout_sec_default": 120, "cmd_timeout_sec_max": 600,
    "bash_trunc_chars": 30000
  },
  "formats_in":  ["csv","xlsx","json","pdf","ipynb","png","jpg"],
  "formats_out": ["csv","xlsx","json","graphml","png","svg"],
  "pdf_creation": false
}
Claude Code - Data Access & Mode Contract (prepend to every Claude run)
ENVIRONMENT SELF-CHECK
- Can you browse the web? (yes/no; method/tool)
- Can you download files via HTTP? (yes/no; size/format limits)
- Can you read user-provided files? (yes/no; supported formats)
- Can you execute code and write files? (yes/no; limits)

SET MODE
MODE = "OFFLINE_ANALYST"   # no web/IO; analyze only provided inputs
MODE = "ONLINE_QUERY"      # you can search the internet and download public data
MODE = "TOOL_AUGMENTED"    # you can call specific operator-provided tools/APIs

BEHAVIOR BY MODE
OFFLINE_ANALYST:
  - Use only uploaded files, pasted text, or prior phase outputs. Do not invent/fetch data.
  - If data is missing, emit a "DATA REQUEST" block specifying exact files/tables needed.

ONLINE_QUERY:
  - Propose a concrete QUERY PLAN (sources, endpoints, query params, rate limits, dedupe rules).
  - Execute only if allowed; log each fetch; persist artifacts under File Contracts.

TOOL_AUGMENTED:
  - Use operator tools exactly as documented; include tool-call specs and validation steps.

FILE CONTRACTS (if file I/O allowed)
- Write machine-readable artifacts to: /out/{COUNTRY}/phase{N}/claude_{artifact}.{json|csv|tsv|graphml}
- Save raw downloads under:                 /out/{COUNTRY}/phase{N}/raw/
- Always write provenance.json with source URLs/paths, timestamps, languages used.

LANGUAGE POLICY
- Expand queries across LANGS_SEARCH. For PRC sections, always include Chinese queries/keywords.
- Preserve original-language entity names; add transliteration fields where sensible.

OPERATIONS POLICY
- Respect robots.txt and site terms; add randomized 1-3s backoff; limit concurrency to 2.
- If downloads exceed in-memory parse limits, write to /out/{COUNTRY}/phase{N}/raw/ and then parse from disk.
- If a required format is unavailable (e.g., PDF writing), propose an alternative (DOCX/MD/HTML-to-PDF via external tool).

If any capability is blocked, declare it explicitly and proceed in OFFLINE_ANALYST mode with a clear DATA REQUEST.

## Phase 0 - Scoping & Framing
ChatGPT - Prompt
You are a senior research-security analyst scoping COUNTRY. Deliver a 3-page brief:
- COUNTRY’s position in advanced/emerging tech & dual-use research.
- 5-8 priority tech areas (AI, quantum, semiconductors, biotech, space, advanced materials, smart-city/IoT, robotics).
- R&D governance: ministries, funders, national strategies (with dates).
- International posture: EU, U.S., PRC, regional blocs; key agreements/MoUs.
- Strategic strengths/vulnerabilities; likely foreign-interest vectors.
- If INCLUDE_US_NATSEC_FRAMEWORK: add a 1-page annex rating the 8 categories (Critical/High/Moderate/Low) with 1-2 justifications each.

Activate an expert persona panel (geo/PRC/tech/supply-chain/EU-research/OSINT/legal-sanctions/DURC/communications) with
follow-the-money, adversarial, horizon-based mindset.
Claude Code - Prompt
[Apply Data Access & Mode Contract first.]

Return a single JSON object:
{
  "sectors": [],
  "gov_actors": [],
  "funders": [],
  "intl_links": [],
  "agreements": [],
  "strengths": [],
  "vulnerabilities": [],
  "open_questions": [],
  "us_natsec_ratings": [{"dimension": "...", "rating": "...", "rationale": "..."}]   # include iff INCLUDE_US_NATSEC_FRAMEWORK
}
RULES:
- Dates as YYYY-MM where relevant; valid JSON only.
- If MODE="OFFLINE_ANALYST": use only provided inputs or emit DATA REQUEST.
- If MODE in {"ONLINE_QUERY","TOOL_AUGMENTED"}: include provenance.json and note which LANGS_SEARCH were used.

## Phase 1 - Research Ecosystem Baseline (Narrative Map + Legal/Regulatory)
ChatGPT - Prompt
Map COUNTRY’s COMPLETE ecosystem (narrative OK if data partial).

NATIONAL LAYER: ministries (research/defense/economy/intel), funding agencies (basic/applied/defense/innovation),
regulators (export control, FDI screening, standards, accreditation), national labs (defense/civil/dual-use).

INSTITUTIONAL LAYER: universities (technical/research/specialized), research institutes (gov/independent/industry),
private sector (multinationals, national champions, SMEs/startups, defense contractors).

Add Legal/Regulatory review: Export Controls, FDI screening, Research Security policy, Data/IP; list red-flag conditions.

Deliverables: master table; short sector narratives; data gaps; legal/reg summary with red-flag bullets.
Claude Code - Prompt
[Apply Data Access & Mode Contract first.]

Return CSV + JSON:
institutions.csv: name, type{univ,gov,private,RTO}, sectors(list), key_centers, intl_collab{Y/N}, red_flags(list), url
institutions.json: array mirroring the CSV

LANGUAGE:
- Use LANGS_SEARCH for institution names; preserve native script; add romanization/transliteration fields when relevant.

## Phase 2 - Targeted Data Pulls (CORDIS, OpenAIRE, Crossref, Patents, News)
ChatGPT - Prompt
If INCLUDE_DATA_PULLS:
- CORDIS: id, title, dates, amount, partners[], keywords[], lead/beneficiaries.
- OpenAIRE/Crossref: top outputs since 2015, co-author countries, venues, dual_use_keywords hits.
- Patents (WIPO/EPO): assignees, IPC/CPC, co-inventor countries.
- News (3-5y): headline/date/outlet/link; research-security relevance.
Mark PRC/RF joint items. Present structured tables.

PRC coverage requirement: Use CHINA_SECTIONS_LANGS. Preserve Chinese names (汉字) + pinyin; map to local transliterations if used in-country.
Claude Code - Prompt
[Apply Data Access & Mode Contract first.]

If MODE="OFFLINE_ANALYST": do not fetch. Emit DATA REQUEST listing:
- CORDIS export (CSV), OpenAIRE dump (JSON), Crossref/Events (JSON), WIPO/EPO (CSV/JSON), News corpus (CSV),
  local-language corpora (press releases, institutional pages).

If MODE in {"ONLINE_QUERY","TOOL_AUGMENTED"}:
- Produce API-ready query specs (JSON) per source with multilingual keyword sets across LANGS_SEARCH.
- For PRC collaboration queries, include Chinese keywords/entities and CN host domains.
OUTPUTS:
  queries.json
  normalization_notes.md
  provenance.json
  cordis_projects.csv
  openaire_outputs.json
  crossref_hits.json
  patents.csv
  news.csv
Raw pages under /out/{COUNTRY}/phase2/raw/; then dedupe/normalize into the files above.

## Phase 2S - Supply Chain & Finance
ChatGPT - Prompt
Build a dual-use supply-chain map for COUNTRY using Five Pillars: Knowledge, Technology, Materials, Finance, Logistics.
- Identify critical nodes, chokepoints, single points of failure; time-based risks (immediate/30d/90d/long-term).
- FINANCE pillar: public R&D funders, venture funds, sovereign/strategic capital, EIB/DFIs, PPPs, equipment leasing,
  philanthropic/corporate foundations, cross-border capital exposure.
- Add PRC strategy indicators (dependency creation, standards lock-in, vertical integration) + EWIs.
Deliver summary + node table + 5-10 prioritized mitigations.
Claude Code - Prompt
Return:
1) supply_nodes.tsv: node_id, type[supplier,equipment,dataset,lab,financier,logistics], name, location,
   criticality{H/M/L}, alternatives{Y/Limited/N}, vulnerabilities, notes
2) exposure_vectors.tsv: src_node_id, dst_node_id, vector[type], description, risk{H/M/L}
3) finance_map.csv: instrument[type], provider, amount_range, terms, dependency_flag{Y/N}, crossborder_flag{Y/N}, notes
4) chokepoints.json: [{node_id, reason, time_to_mitigate, candidate_alternatives[]}]
Include prc_strategy_flags[] at file-level.
Charts (if any) export to PNG/SVG.

## Phase 3 - Researcher & Collaboration Mapping (Institutional Profiles + Accredited Labs)
ChatGPT - Prompt
From Phases 2/2S: identify Top-20 researchers/institutions (output/impact). Map repeat collaboration with PRC/RF;
academia-industry-government linkages; standards bodies/consortia participation.

Institutional profiles: capabilities, facilities/equipment, partners, funding sources, PRC engagement indicators,
risk assessment (narrative + RAG).

Accredited labs: ISO/IEC scope, accreditor, last audit date; red flags (scope drift, unusual partnerships).
Outputs: short narrative, actor table, network insights, watchlist ties (cautious language).
Claude Code - Prompt
Return artifacts:
- nodes.csv: id, label, type{person,institution,country,standard_body}, sector_tags[]
- edges.csv: src, dst, relation{coauthor,coproject,coinventor,grant,standard}, weight
- centrality.csv: id, degree, betweenness, eigenvector
- graph.graphml (string)

## Phase 4 - Risk & Vulnerability Analysis (Vulnerability Matrix incl. Financial Exposure)
ChatGPT - Prompt
Assess vulnerabilities: IP leakage, espionage, talent pipelines, foreign funding/equipment dependency, cyber posture,
research-integrity, supply-chain, HUMINT, Financial Exposure.
Build a RAG risk matrix by sector with rationale + mitigations (policy/process/technical/training).
If INCLUDE_EXPORT_CONTROLS: add export-control exposure & screening gaps.
If INCLUDE_EWI_CHECKLIST: map 5-10 EWIs to sectors.
Claude Code - Prompt
risk_table.csv:
sector, risk_category, risk_score(1-5), color{R/A/G}, evidence_refs[], mitigation_options[], owner{sponsor/inst}, time_to_implement{short/med/long}
Include scoring_method{rubric, thresholds}.

## Phase 5 - Funding Flow & Partnerships (U.S./PRC/Third-Country + Compliance Hooks)
ChatGPT - Prompt
Trace funding & collaboration: external funders (gov/foundations/corporates), joint centers, industry consortia.
Assess partnerships with U.S., PRC (official/gray), and third-countries; list risk indicators.
Identify compliance leverage points (due-diligence hooks, reporting nodes).
Deliver: flow diagram description, funder-recipient tables, 5-8 case vignettes.
Claude Code - Prompt
Return:
funding_edges.csv: source_country, source_entity, amount, currency, year, recipient_entity, sector, notes
collab_edges.csv: inst_A, inst_B, relation, start_year, end_year, sector, high_risk_flag{Y/N}
compliance_hooks.json: [{field, rationale, screening_rule}]

## Phase 6 - Capacity-Building Program Design (post-awareness)
ChatGPT - Prompt
Design 1-3 targeted interventions for COUNTRY (beyond awareness 101).
For each: Format, Audience, Objectives, Inputs, Outputs, Metrics (pre/post), Timeline (single / 12-18m series), Partners.
Return 1-page blueprint per intervention.
Claude Code - Prompt
programs.json: [{title, type, audience[], agenda_blocks[{min, activity, artifact}],
                 required_inputs[], deliverables[], success_metrics[], risks[], mitigation[]}]
ics_spec.json: {events:[{title, start_dt, duration_min}]}

## Phase 7 - Adversarial / Assumption Testing
ChatGPT - Prompt
Red-team conclusions:
- For each high-confidence claim: falsifiers, counter-narratives, and unknowns.
- Why hasn’t this change happened yet? (constraints/incentives/politics/capacity)
Produce Top-10 fragile assumptions (with evidence rating).
Claude Code - Prompt
assumptions.csv: claim, evidence_for[], evidence_against[], testable_predictions[], falsification_steps[], fragility(1-5)
replication_plan.json: {datasets[], scripts[], recompute_steps[]}

## Phase 8 - Foresight & Early Warning (Strategic Implications & Actions)
ChatGPT - Prompt
Forecast for COUNTRY at 2y/5y/10y: tech trajectories; adversarial interest vectors; policy/market shifts.
If INCLUDE_EWI_CHECKLIST: define EWIs (lead/confirmatory/false-positive) + monitoring cadence.
Add Strategic Implications (mil/intel/economic) and link to an Actions & Policy Matrix with KPIs/EWIs.
Deliver: 3 short scenarios + a watchboard (what to track, where, how often).
Claude Code - Prompt
scenarios.json: [{horizon, drivers[], uncertainties[], scenario, implications[], EWI_links[]}]
watchboard.csv: indicator, signal_source, collection_method, cadence, trigger_threshold, owner
QA & Workflow Backbone
- TSV/CSV contracts for every table; column names fixed; types documented.
- QA checks: dedupe, entity-resolution, date/amount normalization; confidence scores.
- Automation vs. Manual boundaries clearly labeled.
- Red-team & uncertainty checklist before finalization.
Fusion Orchestrator - Combine ChatGPT + Claude Outputs
Recommended location: a small third-entity service (Python/Node) that reads both models’ artifacts and emits fusion.json + fusion_report.md.
File Contracts
/out/{COUNTRY}/phase{N}/chatgpt_{artifact}.{json|csv|md}
/out/{COUNTRY}/phase{N}/claude_{artifact}.{json|csv|md}
/out/{COUNTRY}/phase{N}/fusion.json
/out/{COUNTRY}/phase{N}/fusion_report.md
Fusion Orchestrator Prompt
ROLE: Fusion Orchestrator
INPUTS: chatgpt_output.(md|json|csv), claude_output.(md|json|csv)

TASKS
1) Parse both; build a unified registry (entities, claims, relationships, risks, indicators).
2) De-duplicate & reconcile conflicts:
   {claim_id, views:{chatgpt:{...}, claude:{...}}, reconciliation:{status:"agree|disagree|uncertain",
   chosen_view:"...", evidence_notes:"...", confidence:H/M/L}}
3) Emit fusion_report.md:
   - Agreements (top 10)
   - Disagreements to adjudicate (ranked by impact)
   - Unique insights from each model
   - Next data pulls to resolve uncertainty
4) Emit fusion.json: {entities[], relationships[], risks[], indicators[], actions[], open_questions[]}

RULES
- Prefer stronger provenance & recency.
- If evidence equal: keep BOTH interpretations; confidence=Low.
- Never silently drop a unique claim; log under “unique insights.”
Claude Code - Capabilities-Probe (run once per environment)
ROLE: “Claude Code - Capabilities Auditor.” Determine actionable capabilities in this environment.

Deliver capabilities.json:
{
 "web_browsing": {"available": bool, "method": "builtin|tool|none", "test": "...", "result": "..."},
 "http_download": {"available": bool, "max_bytes": "est", "allowed_mime": ["..."], "test": "..."},
 "code_execution": {"languages": ["python","bash","node","java","c_cpp"], "packages": ["pandas","networkx",...], "limits": {"cpu","mem","timeout"}, "test": "..."},
 "filesystem": {"read_user_uploads": bool, "write_files": bool, "persist_between_turns": bool, "paths": ["..."], "test": "..."},
 "data_analysis": {"max_rows":"est","formats_in":["csv","xlsx","json","pdf","ipynb","png","jpg"],"formats_out":["csv","xlsx","json","graphml","png","svg"]},
 "graphs_charts": {"available": bool, "libs": ["matplotlib","vega","none"], "image_export": ["png","svg","none"]},
 "network_calls": {"available": bool, "domains_allowed": "all|whitelist|none", "rate_limits": "desc"},
 "zip_unzip": {"available": bool, "max_size": "est"},
 "memory_context": {"tokens_context": "est", "long_outputs_handling": "chunk|truncate"},
 "privacy_safety": {"egress_restrictions": "desc", "sandbox_notes": "desc"}
}

TEST BATTERY:
- WEB: GET https://example.com/robots.txt; record status or error.
- DOWNLOAD: tiny JSON (https://httpbin.org/json); if blocked, record error.
- CODE: import json, math, pandas as pd; compute sqrt(2); make 2-row DataFrame; serialize to CSV.
- FILESYSTEM: create temp file; list dir; delete file.
- FORMATS: emit hello.csv, hello.json, hello.graphml (1 node, 0 edges). Record any failures.
- LIMITS: capture exceptions (redact sensitive parts) and set available=false accordingly.

REPORT: Return the JSON + bullets of AVAILABLE vs BLOCKED and practical limits.
