# PROJECT KNOWLEDGE BASE
## Single Source of Truth for OSINT Foresight

**Last Updated:** 2025-09-20
**Purpose:** Centralized repository of all lessons learned, standards, and project knowledge

---

### Quick Start

- **New to project?** Start with `03_LESSONS_LEARNED/`
- **Running analysis?** Check `01_CRITICAL_STANDARDS/`
- **Processing data?** See `05_TECHNICAL_GUIDES/`
- **Quality check?** Use `08_VALIDATION_CHECKLISTS/`

### Critical Rules

1. **NO FABRICATION** - See `01_CRITICAL_STANDARDS/ZERO_FABRICATION_PROTOCOL.md`
2. **NO ASSUMPTIONS** - See `01_CRITICAL_STANDARDS/ZERO_ASSUMPTIONS_PROTOCOL.md`
3. **Evidence required** - See `01_CRITICAL_STANDARDS/MINIMUM_EVIDENCE_STANDARDS.md`
4. **Corroboration mandatory** - See `01_CRITICAL_STANDARDS/TRUE_CORROBORATION_STANDARD.md`

### If You Only Read 5 Documents:

1. `01_CRITICAL_STANDARDS/ZERO_FABRICATION_PROTOCOL.md` - Never claim data we don't have
2. `01_CRITICAL_STANDARDS/ZERO_ASSUMPTIONS_PROTOCOL.md` - Never add interpretation to facts
3. `03_LESSONS_LEARNED/LEONARDO_ANALYTICAL_FAILURE_ANALYSIS.md` - Learn from failures
4. `01_CRITICAL_STANDARDS/INTEGRATED_ZERO_PROTOCOLS.md` - Combined enforcement framework
5. `08_VALIDATION_CHECKLISTS/ZERO_FABRICATION_VERIFICATION_CHECKLIST.md` - Compliance checklist

---

## Complete Index

### 01_CRITICAL_STANDARDS

**Core anti-fabrication and evidence standards**

- `ZERO_FABRICATION_PROTOCOL.md` - **🔴 CRITICAL** - Never claim data we don't have (Web of Science incident)
- `ZERO_ASSUMPTIONS_PROTOCOL.md` - **🔴 CRITICAL** - Never add interpretation to facts (Shell company incident)
- `INTEGRATED_ZERO_PROTOCOLS.md` - **🔴 CRITICAL** - Combined fabrication + assumptions enforcement
- `NUCLEAR_ANTI_FABRICATION_PROTOCOL.md` - Absolute prohibition on data fabrication
- `TRUE_CORROBORATION_STANDARD.md` - Defining real vs echo-chamber corroboration
- `TRANSPARENCY_DEFINITION_STANDARD.md` - What transparency means (30% confidence with disclosure)
- `MINIMUM_EVIDENCE_STANDARDS.md` - Baseline evidence requirements for any claim
- `ADMIRALTY_RATING_SYSTEM.md` - A1-F6 source reliability/credibility ratings
- `INSUFFICIENT_EVIDENCE_PROTOCOL.md` - What to output when data is unavailable

### 02_OSINT_BEST_PRACTICES

**Intelligence community best practices**

- `OSINT_BEST_PRACTICES_SYNTHESIS.md` - Synthesis of CIA/DIA OSINT methodologies
- `FIVE_STEP_OSINT_PROCESS.md` - Standard OSINT workflow
- `SOURCE_EVALUATION_CRITERIA.md` - How to evaluate source credibility
- `DOCUMENTATION_ALTERNATIVES.md` - Text-based documentation methods (no screenshots)
- `PROVENANCE_WITHOUT_SHA256.md` - Verification methods without hash generation
- `CHAIN_OF_CUSTODY.md` - Maintaining evidence integrity

### 03_LESSONS_LEARNED

**Critical failures and postmortems**

- `LEONARDO_ANALYTICAL_FAILURE_ANALYSIS.md` - Analysis of Leonardo/78 transfers fabrication
- `WHAT_WENT_WRONG.md` - Comprehensive failure analysis
- `LEONARDO_CASE_STUDY.md` - Deep dive into specific failure
- `REGRESSION_TEST_REQUIREMENTS.md` - Tests to prevent future failures

### 04_PROJECT_ARCHITECTURE

**System design and structure**

- `SYSTEM_OVERVIEW.md` - High-level architecture
- `DATA_INFRASTRUCTURE.md` - 445GB data reality
- `PHASE_DEPENDENCIES.md` - How phases interconnect
- `SUB_PHASE_BREAKDOWN.md` - Breaking phases into manageable chunks
- `COLLECTOR_INVENTORY.md` - 56 available data collectors
- `PROCESSING_PIPELINE.md` - Data flow and processing
- `cross_country_ticket_catalog_for_claude_code_generalized_from_italy_phases_1_13_v_1.md` - Phase implementation catalog

### 05_TECHNICAL_GUIDES

**How-to documentation**

- `DATA_COLLECTION_COMPLETE_SETUP.md` - Complete data collection guide
- `FREE_DATA_INTEGRATION_GUIDE.md` - Using free/open data sources
- `OPENALEX_SCHEDULED_PROCESSING_SETUP.md` - OpenAlex streaming setup (420GB)
- `STREAMING_PROCESSING.md` - Handling large data streams
- `TED_DATA_PROCESSING.md` - Processing EU procurement data
- `PATENT_ANALYSIS.md` - Patent search and analysis
- `API_INTEGRATION.md` - Connecting to data APIs
- `DATABASE_QUERIES.md` - SQL and data queries
- `MCF_IMPLEMENTATION_ROADMAP.md` - 30-day MCF intelligence implementation plan

### 06_ANALYSIS_FRAMEWORKS

**Analytical methodologies**

- `LEONARDO_STANDARD.md` - 8-point validation framework
- `BOMBSHELL_PROTOCOL.md` - Handling claims with score >20
- `RISK_TIER_CLASSIFICATION.md` - Tier A/B/C risk categories
- `ACH_METHODOLOGY.md` - Analysis of Competing Hypotheses
- `CONFIDENCE_SCORING.md` - High/Moderate/Low confidence scales
- `ALTERNATIVE_EXPLANATIONS.md` - Considering mundane explanations

### 07_DATA_SOURCES

**Available data and access**

- `PRIMARY_SOURCES.md` - List of primary data sources
- `OPENALEX_GUIDE.md` - 420GB academic database
- `TED_PROCUREMENT.md` - 24GB EU contracts database
- `OPENSANCTIONS_DATA.md` - **NEW** 376MB global sanctions (7,177 Chinese entities from 183,766 total)
- `GLEIF_LEI_DATA.md` - **NEW** 525MB legal entity identifiers (1,750 Chinese LEIs with ownership trees)
- `SEC_EDGAR.md` - US corporate filings
- `USPTO_PATENTS.md` - US patent database
- `DATA_ACCESS_STATUS.md` - What we have vs need
- `MCF_HARVESTING_STRATEGY.md` - Military-Civil Fusion intelligence collection
- `CHINA_SOURCES_MASTER.json` - 50 verified China research sources
- `PROVENANCE_TRACKING_CONFIG.json` - MCF intelligence provenance schema

### 08_VALIDATION_CHECKLISTS

**Quality control processes**

- `ZERO_FABRICATION_VERIFICATION_CHECKLIST.md` - **🔴 MANDATORY** - Compliance for all outputs
- `PRE_ANALYSIS_CHECKLIST.md` - Before starting analysis
- `QUALITY_CONTROL.md` - During analysis checks
- `SELF_VERIFICATION.md` - Self-audit requirements
- `OUTPUT_REQUIREMENTS.md` - What must be in outputs
- `REVIEWER_CHECKLIST.md` - For reviewing others' work
- `FINAL_V7_VALIDATION_CHECKLIST.md` - Comprehensive validation
- `PROMPT_V7_VALIDATION_CHECKLIST.md` - Prompt-specific validation
- `PHASE_BY_PHASE_AUDIT_PROTOCOL.md` - Phase-level validation

---

## Usage Notes

### For New Team Members
1. Read all documents in `03_LESSONS_LEARNED/` first
2. Study `01_CRITICAL_STANDARDS/` thoroughly
3. Review relevant `05_TECHNICAL_GUIDES/` for your tasks
4. Use `08_VALIDATION_CHECKLISTS/` before submitting work

### For Analysis Tasks
1. Start with `01_CRITICAL_STANDARDS/INSUFFICIENT_EVIDENCE_PROTOCOL.md`
2. Apply frameworks from `06_ANALYSIS_FRAMEWORKS/`
3. Follow guides in `02_OSINT_BEST_PRACTICES/`
4. Validate using `08_VALIDATION_CHECKLISTS/`

### For Development
1. Understand `04_PROJECT_ARCHITECTURE/`
2. Follow `05_TECHNICAL_GUIDES/`
3. Test against `03_LESSONS_LEARNED/REGRESSION_TEST_REQUIREMENTS.md`

---

## The Prime Directive

**If no evidence exists:**
```
Return "INSUFFICIENT_EVIDENCE"
```

**Never:**
- Fabricate data
- Estimate without basis
- Fill gaps with plausible fiction
- Skip verification

**Always:**
- Require sources
- Verify claims
- Consider alternatives
- Document uncertainty

---

*This knowledge base is the single source of truth for project standards, lessons, and methodology.*
