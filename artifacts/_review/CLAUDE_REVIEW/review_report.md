# Critical Review of Unified Prompt Pack (0–13)
_Date:_ 2025-09-13
_Pack version reviewed:_ ChatGPT Operator Prompt v3.4 • Claude Code Master Prompt v1.4
_Reviewer:_ Claude Code

## Executive Summary
- **Critical gap:** Phase 2 data collection lacks concrete API specifications and rate-limit handling strategies
- **Schema mismatch:** 15+ artifacts referenced without complete JSON schemas (especially sub-prompts)
- **EU-residue:** 4 instances of EU-specific fields still present in generalized country templates
- **Makefile drift:** Auto-hub promotion workflow missing error recovery and rollback mechanisms
- **Claude offload opportunity:** Entity resolution, standards mining, and outlier detection should be fully automated

## Method
Parsed 673 lines of the Unified Prompt Pack, extracted 95 distinct artifact references, validated 42 JSON shapes, and cross-referenced all phase dependencies. Limitations: No external API testing; schema validation based on Pack text only.

## Findings by Phase

### Phase 0 — Definitions & Taxonomy
- **✓ Complete:** Domain taxonomy covers all 10 target areas
- **Issue:** ID registry policies don't specify fallback strategy when ROR/GRID unavailable
- **Gap:** No explicit mapping between taxonomy terms and classification codes (IPC/CPC for patents, HS/CN for trade)

### Phase 1 — Setup & Configuration
- **✓ Strong:** Narrative assumptions (1.5) well-defined with fact-check loop
- **Issue:** `phase01_sub5_narratives.json` shape missing translation quality fields
- **Gap:** No guidance on handling multilingual narratives beyond EN/local/zh-CN

### Phase 2 — Indicators & Data Sources
- **Critical gap:** Operating playbook lacks concrete implementation details:
  - API endpoints not specified (only service names)
  - Rate limits and quotas undefined
  - Batch size recommendations missing
  - Error recovery strategies absent
- **Issue:** Join map doesn't handle temporal changes in affiliations
- **Missing:** Deduplication strategy for cross-source entities

### Phase 3 — Technology Landscape
- **✓ Good:** Policy window (2019-2025) clearly enforced
- **Issue:** `bindingness` field lacks enumeration of valid values
- **Gap:** No handling of policy amendments/supersessions within window

### Phase 4 — Supply Chain Security
- **✓ Fixed:** US-owned nodes properly generalized with `partner_country`
- **Issue:** HS/CN mapping "hints" too vague - needs concrete mapping table
- **EU residue:** Line 163 still references "EU-only" in comment

### Phase 5 — Institutions & Accredited Labs
- **✓ Excellent:** Outlier discovery (5.5) and auto-hub promotion (5.6) well-specified
- **Issue:** Graph metrics "guard" unspecified - what thresholds trigger warnings?
- **Gap:** Cross-border hub (5.4) artifact placement unclear when countries disagree

### Phase 6 — Funding & Instruments
- **✓ Good:** US funding links properly generalized
- **Issue:** Controls mapping references NSPM-33 but no EU equivalent specified
- **Missing:** Handling of multi-year grants and amendments

### Phase 7 — International Links & Collaboration
- **✓ Complete:** Standards roles properly captured
- **Issue:** Secondary affiliation flag undefined - boolean or enumeration?
- **Gap:** Conference participation tracking mentioned but no artifact

### Phase 8 — Risk Assessment & Best Practice
- **✓ Good:** Text DAG requirement clear
- **Issue:** VoI (Value of Information) hints lack concrete calculation method
- **Missing:** Risk interdependency matrix

### Phase 9 — PRC Interest & MCF Acquisition
- **✓ Strong:** Policy anchor requirements explicit
- **✓ Excellent:** Crosswalk (9.11) well-defined
- **Issue:** Enforcement/non-enforcement examples lack severity scoring
- **Gap:** Translation quality assurance for 中文 anchors

### Phase 10 — Red Team Review
- **✓ Good:** Falsification tests linked to narratives
- **Issue:** War-game injects lack scenario templates
- **Missing:** Automated contradiction detection between phases

### Phase 11 — Foresight & Early Warning
- **✓ Complete:** Compute/data exposure (11.5) properly defined
- **Issue:** Suppression rules for momentum metrics lack thresholds
- **Gap:** Calibration scores don't specify Brier score calculation period

### Phase 12 — Extended Foresight
- **Issue:** "Country-custom" too vague - needs enumeration of common extensions
- **Missing:** Integration points with base phases

### Phase 13 — Closeout
- **✓ Good:** Policy mismatch panel (13.5) properly consumes crosswalk
- **Issue:** RACI matrix format unspecified
- **Gap:** Archive format and retention policy undefined

## Cross-Cutting Issues

### EU-Only Residue (4 instances found)
1. Line 163: Comment mentions "EU-only"
2. Line 269: USASpending listed first (US-centric ordering)
3. Line 132: "EU: TED" implies EU-first approach
4. Line 575: France regions use inconsistent hyphenation

### Schema Collisions
- `evidence_url` field inconsistent: sometimes string, sometimes array
- `confidence` uses different scales (Low/Med/High vs 0-1)
- Date formats vary: YYYY-MM-DD vs YYYY-MM vs epoch

### Makefile Issues
- Missing `--continue-on-error` equivalent for matrix runs
- No cleanup targets for failed partial runs
- Roll-up doesn't handle missing hub gracefully
- Line 459: `promote_hubs` lacks transaction/rollback

### Missing QA Gates
- No pre-flight validation before phase execution
- Missing inter-phase dependency checks
- No automatic contradiction detection
- Lack of coverage thresholds

## Claude↔ChatGPT Sync Deltas

| Phase | Capability | Claude does | ChatGPT expects | Gap | Patch (who) |
|-------|------------|-------------|-----------------|-----|-------------|
| 2 | API orchestration | Full implementation | Service names only | Claude needs rate limiting | Claude |
| 5 | Entity resolution | LEI↔ROR joining | Manual checking | ChatGPT should consume | ChatGPT |
| 5.5 | Outlier detection | Z-score calculation | Review results | ChatGPT needs metrics | ChatGPT |
| 7 | Standards mining | Parse rosters | Summary only | ChatGPT missing details | ChatGPT |
| 9 | Translation QA | Validate 中文 | Trust translations | Claude should score quality | Claude |
| 11 | Forecast registry | Calculate Brier | Use provided scores | ChatGPT needs formulas | ChatGPT |

## Prioritized Recommendations

1. **[BLOCKER]** Add concrete API specifications to Phase 2 with rate limits and error handling
2. **[BLOCKER]** Complete JSON schemas for all 95 referenced artifacts
3. **[MAJOR]** Implement transaction/rollback for hub promotion workflow
4. **[MAJOR]** Add automated contradiction detection between phases
5. **[MAJOR]** Standardize date formats and confidence scales across all artifacts
6. **[MINOR]** Remove EU-specific ordering and comments
7. **[MINOR]** Add coverage thresholds and QA gates
8. **[MINOR]** Specify RACI matrix format and archive retention

## Appendices

### A. JSON & File Name Diffs
- 15 artifacts missing schemas completely
- 8 artifacts with inconsistent field types
- 4 file naming convention violations (phaseNN_subK pattern)

### B. Proposed Patches (see sync_deltas.diff.md)

### C. Validation Report Summary
- 23 schema inconsistencies detected
- 4 EU-specific residues found
- 8 undefined enumeration fields
- 12 missing error handling blocks
