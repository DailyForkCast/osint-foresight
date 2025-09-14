# Synchronization Deltas: ChatGPT ↔ Claude Code

## ChatGPT Operator Prompt Updates Needed

### Phase 2 - Add API Implementation Details
```diff
@@ Phase 2 — Indicators & Data Sources @@
 **2.A Operating Playbook (Claude ↔ ChatGPT)**
-- - **Publications (Crossref, OpenAlex, OpenAIRE):** weekly→normalize
++ - **Publications (Crossref, OpenAlex, OpenAIRE):** weekly→normalize
++   API: https://api.openalex.org/works (rate: 10/sec, auth: mailto)
++   API: https://api.crossref.org/works (rate: 50/sec, auth: none)
++   Retry: exponential backoff 1-2-4-8s, max 3 attempts
++   Batch: 100 records/request, cursor pagination
```

### Phase 5 - Consume Claude's Entity Resolution
```diff
@@ Phase 5 — Institutions & Accredited Labs @@
 **5.1** Entity resolution & dedupe (ROR/LEI/ORCID, Latin + Han).
++ **5.1.A** Claude provides: resolved_entities.json with confidence scores
++ **5.1.B** ChatGPT validates: spot-check 5% sample, flag <0.8 confidence
++ **5.1.C** Handoff: ChatGPT summarizes top-20 by centrality for briefs
```

### Phase 7 - Standards Mining Details
```diff
@@ Phase 7 — International Links @@
 **7.2** Projects/patents/standards/conferences; record roles
-- (member/rapporteur/editor).
++ (member/rapporteur/editor) from Claude's standards_roles.json:
++ {body:"3GPP", wg:"RAN1", person:"orcid", org:"ror", role:"rapporteur", since:"2023-01"}
++ ChatGPT: identify influence patterns across WGs
```

### Phase 9 - Translation Quality from Claude
```diff
@@ Phase 9 — PRC Interest & MCF @@
 **9.11 Policy anchor crosswalk**
++ Claude provides translation_quality scores (0-1) for all 中文 content
++ ChatGPT: flag for human review if score <0.7 or confidence=="Low"
++ Both: maintain translation_log.csv with method and validator
```

### Phase 11 - Forecast Calculations
```diff
@@ Phase 11 — Foresight & Early Warning @@
 **11.4** Calibration summary (Brier by horizon).
++ Claude calculates: brier_score = mean((forecast_p - outcome)^2)
++ Rolling window: 90 days for 2y, 180 days for 5y, 365 days for 10y
++ ChatGPT interprets: <0.25 good, 0.25-0.35 fair, >0.35 poor
```

## Claude Code Master Prompt Updates Needed

### Phase 2 - Rate Limiting Implementation
```diff
@@ ## 2) Phase Orchestrator (0–13) @@
 ### Phase 0 → 3 (Setup, Indicators, Landscape)
++ Implement rate limiting:
++ ```python
++ class RateLimiter:
++     def __init__(self, calls_per_second):
++         self.min_interval = 1.0 / calls_per_second
++         self.last_call = 0
++
++     async def acquire(self):
++         elapsed = time.time() - self.last_call
++         if elapsed < self.min_interval:
++             await asyncio.sleep(self.min_interval - elapsed)
++         self.last_call = time.time()
++ ```
```

### Phase 5 - Outlier Detection Implementation
```diff
@@ ### Phase 5 — Institutions @@
++ Implement z-score calculation:
++ ```python
++ def calculate_outliers(df, columns, z_threshold=2.0):
++     outliers = []
++     for col in columns:
++         z_scores = np.abs(stats.zscore(df[col]))
++         outliers.extend(df[z_scores > z_threshold]['region'].tolist())
++     return pd.DataFrame({'region': outliers, 'z_score': z_scores[z_scores > z_threshold]})
++ ```
```

### Phase 9 - Translation Quality Scoring
```diff
@@ ### Phase 9 — PRC/MCF @@
++ Add translation quality scoring:
++ ```python
++ def score_translation(original_cn, translated_en):
++     # Use language model or API
++     confidence = 0.0
++     if has_backtranslation_api():
++         back = translate(translated_en, target='zh-CN')
++         confidence = similarity(original_cn, back)
++     return {
++         'confidence': confidence,
++         'method': 'backtranslation' if confidence > 0 else 'none',
++         'needs_review': confidence < 0.7
++     }
++ ```
```

### Makefile - Add Transaction Support
```diff
@@ promote_hubs: $(OUT)/phase05_sub6_auto_hubs.json @@
-- python scripts/promote_hubs.py --country "$(COUNTRY)" --auto $< --conf artifacts/$(COUNTRY)/hubs.conf
++ cp artifacts/$(COUNTRY)/hubs.conf artifacts/$(COUNTRY)/hubs.conf.bak
++ python scripts/promote_hubs.py --country "$(COUNTRY)" --auto $< --conf artifacts/$(COUNTRY)/hubs.conf.tmp --validate
++ if [ $$? -eq 0 ]; then mv artifacts/$(COUNTRY)/hubs.conf.tmp artifacts/$(COUNTRY)/hubs.conf; else mv artifacts/$(COUNTRY)/hubs.conf.bak artifacts/$(COUNTRY)/hubs.conf; exit 1; fi
++ rm -f artifacts/$(COUNTRY)/hubs.conf.bak
```

## Shared Updates (Both Tools)

### Standardize Confidence Scales
```diff
-- confidence: ["Low","Med","High"]
-- confidence: 0.0-1.0
++ confidence: {
++     "score": 0.0-1.0,
++     "label": "Low|Medium|High",
++     "mapping": {"Low": [0.0, 0.4], "Medium": [0.4, 0.7], "High": [0.7, 1.0]}
++ }
```

### Add Validation Gates
```diff
@@ All phase starts @@
++ def validate_prerequisites(phase_num, artifact_dir):
++     required = PHASE_DEPS[phase_num]
++     missing = []
++     for artifact in required:
++         path = os.path.join(artifact_dir, artifact)
++         if not os.path.exists(path):
++             missing.append(artifact)
++         else:
++             # Validate schema
++             if not validate_schema(path, SCHEMAS[artifact]):
++                 missing.append(f"{artifact} (invalid schema)")
++     if missing:
++         raise ValueError(f"Prerequisites missing: {missing}")
```

### Fix EU-Specific Ordering
```diff
-- # EU: TED + national portals; CORDIS. Non-EU: national procurement
++ # National portals (TED for EU), research grants (CORDIS for EU, national equivalents)
++ PROCUREMENT_SOURCES = {
++     'EU': ['TED', 'national_portals', 'CORDIS'],
++     'US': ['SAM.gov', 'USASpending', 'Grants.gov'],
++     'UK': ['Contracts_Finder', 'UKRI'],
++     'default': ['national_procurement', 'national_grants']
++ }
```

## Priority Implementation Order

1. **[IMMEDIATE]** Claude: Implement rate limiting and API specifications
2. **[IMMEDIATE]** Claude: Add validation gates and schema checking
3. **[WEEK 1]** Both: Standardize confidence scales and date formats
4. **[WEEK 1]** Claude: Implement transaction support for hub promotion
5. **[WEEK 2]** ChatGPT: Consume Claude's entity resolution outputs
6. **[WEEK 2]** Claude: Add translation quality scoring
7. **[WEEK 3]** Both: Remove EU-specific language and ordering
8. **[WEEK 3]** ChatGPT: Add forecast interpretation guidelines
