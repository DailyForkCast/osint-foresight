# PROJECT KNOWLEDGE BASE PROPOSAL
**Date:** 2025-09-20
**Purpose:** Centralize all lessons learned, standards, and knowledge

---

## 🎯 THE PROBLEM

### Current State:
- **180 files** in docs/prompts/
- Knowledge mixed with prompts
- Standards scattered across folders
- Lessons learned in various documents
- No single source of truth
- Old prompts without security updates

### What's Mixed Together:
1. **Actual Prompts** (for LLMs)
2. **Standards** (anti-fabrication, corroboration)
3. **Lessons Learned** (what went wrong)
4. **Best Practices** (OSINT methods)
5. **Technical Guides** (how to process data)
6. **Project Architecture** (system design)
7. **Analysis Reports** (findings)

---

## 💡 PROPOSED SOLUTION

### Create: `KNOWLEDGE_BASE/`

A single folder containing ALL project knowledge, organized by type:

```
KNOWLEDGE_BASE/
├── 📕 README.md (Master index of all knowledge)
│
├── 🔴 01_CRITICAL_STANDARDS/
│   ├── NUCLEAR_ANTI_FABRICATION_PROTOCOL.md
│   ├── TRUE_CORROBORATION_STANDARD.md
│   ├── TRANSPARENCY_DEFINITION_STANDARD.md
│   ├── MINIMUM_EVIDENCE_STANDARDS.md
│   ├── ADMIRALTY_RATING_SYSTEM.md
│   └── INSUFFICIENT_EVIDENCE_PROTOCOL.md
│
├── 🎯 02_OSINT_BEST_PRACTICES/
│   ├── OSINT_BEST_PRACTICES_SYNTHESIS.md
│   ├── FIVE_STEP_OSINT_PROCESS.md
│   ├── SOURCE_EVALUATION_CRITERIA.md
│   ├── DOCUMENTATION_ALTERNATIVES.md
│   ├── PROVENANCE_WITHOUT_SHA256.md
│   └── CHAIN_OF_CUSTODY.md
│
├── 📚 03_LESSONS_LEARNED/
│   ├── FABRICATION_INCIDENT_ANALYSIS.md
│   ├── 78_TRANSFERS_POSTMORTEM.md
│   ├── WHAT_WENT_WRONG.md
│   ├── LEONARDO_CASE_STUDY.md
│   └── REGRESSION_TEST_REQUIREMENTS.md
│
├── 🏭 04_PROJECT_ARCHITECTURE/
│   ├── SYSTEM_OVERVIEW.md
│   ├── DATA_INFRASTRUCTURE.md (445GB reality)
│   ├── PHASE_DEPENDENCIES.md
│   ├── SUB_PHASE_BREAKDOWN.md
│   ├── COLLECTOR_INVENTORY.md (56 available)
│   └── PROCESSING_PIPELINE.md
│
├── 🔧 05_TECHNICAL_GUIDES/
│   ├── DATA_COLLECTION_GUIDE.md
│   ├── STREAMING_PROCESSING.md (OpenAlex)
│   ├── TED_DATA_PROCESSING.md
│   ├── PATENT_ANALYSIS.md
│   ├── API_INTEGRATION.md
│   └── DATABASE_QUERIES.md
│
├── 🎯 06_ANALYSIS_FRAMEWORKS/
│   ├── LEONARDO_STANDARD.md (8-point validation)
│   ├── BOMBSHELL_PROTOCOL.md (score >20)
│   ├── RISK_TIER_CLASSIFICATION.md (A/B/C)
│   ├── ACH_METHODOLOGY.md (competing hypotheses)
│   ├── CONFIDENCE_SCORING.md
│   └── ALTERNATIVE_EXPLANATIONS.md
│
├── 🌐 07_DATA_SOURCES/
│   ├── PRIMARY_SOURCES.md
│   ├── OPENALEX_GUIDE.md (420GB academic)
│   ├── TED_PROCUREMENT.md (24GB contracts)
│   ├── SEC_EDGAR.md
│   ├── USPTO_PATENTS.md
│   └── DATA_ACCESS_STATUS.md
│
└── 📋 08_VALIDATION_CHECKLISTS/
    ├── PRE_ANALYSIS_CHECKLIST.md
    ├── QUALITY_CONTROL.md
    ├── SELF_VERIFICATION.md
    ├── OUTPUT_REQUIREMENTS.md
    └── REVIEWER_CHECKLIST.md
```

---

## 📦 WHAT MOVES WHERE

### From docs/prompts/ to KNOWLEDGE_BASE/:

#### To 01_CRITICAL_STANDARDS/
- NUCLEAR_ANTI_FABRICATION_PROTOCOL.md
- TRUE_CORROBORATION_STANDARD.md
- TRANSPARENCY_DEFINITION_STANDARD.md
- MINIMUM_EVIDENCE_STANDARDS.md
- PHASE_INTERDEPENDENCY_MATRIX.md

#### To 02_OSINT_BEST_PRACTICES/
- OSINT_BEST_PRACTICES_SYNTHESIS.md
- DOCUMENTATION_ALTERNATIVES.md
- PROVENANCE_ALTERNATIVES_NO_SHA256.md
- CRITICAL_UPDATES_REQUIRED.md

#### To 03_LESSONS_LEARNED/
- MASTER_PROMPT_COMPREHENSIVE_ANALYSIS.md
- CHATGPT_NARRATIVE_ENHANCEMENTS.md
- CRITICAL_NEW_ELEMENTS_TO_ADD.md

#### To 04_PROJECT_ARCHITECTURE/
- PHASE_BREAKDOWN_PROPOSAL.md
- MASTER_PROMPT_V8_INTEGRATION.md

#### To 08_VALIDATION_CHECKLISTS/
- FINAL_V7_VALIDATION_CHECKLIST.md
- PROMPT_V7_VALIDATION_CHECKLIST.md

---

## 📁 CLEAN PROMPTS STRUCTURE

### After Cleanup:

```
docs/prompts/
├── active/
│   └── master/
│       ├── CHATGPT_MASTER_PROMPT_V8.0_ZERO_FABRICATION.md ✅
│       └── CLAUDE_CODE_MASTER_V8.0_ZERO_FABRICATION.md ✅
│
└── archive/
    ├── pre_v8_outdated/ (all pre-v8 versions)
    └── templates_legacy/ (old phase templates)
```

**Only 2 active prompts - the v8.0 masters with full security**

---

## 📌 KNOWLEDGE_BASE/README.md Structure

```markdown
# PROJECT KNOWLEDGE BASE
## Single Source of Truth for OSINT Foresight

### Quick Start
- **New to project?** Start with 03_LESSONS_LEARNED/
- **Running analysis?** Check 01_CRITICAL_STANDARDS/
- **Processing data?** See 05_TECHNICAL_GUIDES/
- **Quality check?** Use 08_VALIDATION_CHECKLISTS/

### Index
[Complete listing of all documents with descriptions]

### Critical Rules
1. NO FABRICATION - See NUCLEAR_ANTI_FABRICATION_PROTOCOL
2. Evidence required - See MINIMUM_EVIDENCE_STANDARDS
3. Corroboration mandatory - See TRUE_CORROBORATION_STANDARD

### If You Only Read 5 Documents:
1. NUCLEAR_ANTI_FABRICATION_PROTOCOL.md
2. 78_TRANSFERS_POSTMORTEM.md
3. OSINT_BEST_PRACTICES_SYNTHESIS.md
4. DATA_INFRASTRUCTURE.md
5. INSUFFICIENT_EVIDENCE_PROTOCOL.md
```

---

## ✅ BENEFITS

### Single Source of Truth
- One folder for ALL knowledge
- Clear organization by type
- Easy to reference
- No confusion with prompts

### Clean Separation
- Knowledge in KNOWLEDGE_BASE/
- Prompts in docs/prompts/
- Data in data/
- Scripts in scripts/

### Easy Onboarding
- New team member? Read KNOWLEDGE_BASE/
- Need standards? Check folder 01
- Want guides? Check folder 05
- Everything indexed in README

### Version Control
- Knowledge evolves separately from prompts
- Standards updated in one place
- Lessons learned accumulated
- No duplication

---

## 🎯 IMPLEMENTATION PLAN

### Step 1: Create Structure
```bash
mkdir -p KNOWLEDGE_BASE/{01_CRITICAL_STANDARDS,02_OSINT_BEST_PRACTICES,03_LESSONS_LEARNED,04_PROJECT_ARCHITECTURE,05_TECHNICAL_GUIDES,06_ANALYSIS_FRAMEWORKS,07_DATA_SOURCES,08_VALIDATION_CHECKLISTS}
```

### Step 2: Move Standards
Move all non-prompt knowledge from docs/prompts/ to appropriate KNOWLEDGE_BASE/ folders

### Step 3: Archive Old Prompts
Move all pre-v8 prompts to archive/pre_v8_outdated/

### Step 4: Create Master Index
Generate KNOWLEDGE_BASE/README.md with complete index

### Step 5: Update References
Point v8.0 prompts to KNOWLEDGE_BASE/ for standards

---

## 💡 BEST PRACTICE ALIGNMENT

This follows standard practices:
- **Separation of Concerns** - Knowledge ≠ Prompts
- **Single Source of Truth** - One knowledge location
- **Clear Hierarchy** - Numbered folders show priority
- **Self-Documenting** - README explains everything
- **Maintainable** - Easy to update and extend

---

## 🔴 CRITICAL SUCCESS FACTOR

**When you say:**
> "Read all our standards and lessons learned"

**You can now say:**
> "Read everything in KNOWLEDGE_BASE/"

**One command. One location. Complete knowledge.**
