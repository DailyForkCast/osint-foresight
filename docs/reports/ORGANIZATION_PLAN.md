# PROJECT ORGANIZATION PLAN
**Date:** 2025-09-19
**Purpose:** Clean up root folder and archive untrusted analysis

---

## 📁 PROPOSED FOLDER STRUCTURE

```
C:/Projects/OSINT - Foresight/
├── 📦 archive/
│   ├── untrusted_analysis_20250919/  # All questionable analysis
│   │   ├── audit_results_*.json
│   │   ├── confidence_standardization_log.json
│   │   └── [any analysis without clear provenance]
│   └── legacy_prompts/  # Old prompt versions
│
├── 📝 docs/
│   ├── prompts/
│   │   ├── active/
│   │   │   ├── master/  # v8.0 master prompts
│   │   │   └── templates/  # Phase templates
│   │   └── archive/  # Old versions
│   ├── standards/
│   │   ├── NUCLEAR_ANTI_FABRICATION_PROTOCOL.md
│   │   ├── OSINT_BEST_PRACTICES_SYNTHESIS.md
│   │   ├── TRUE_CORROBORATION_STANDARD.md
│   │   └── TRANSPARENCY_DEFINITION_STANDARD.md
│   ├── reports/  # Status reports
│   │   ├── DATA_PROCESSING_STATUS_REPORT.md
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   └── PHASE_ORCHESTRATOR_SUCCESS_REPORT.md
│   ├── guides/  # How-to documents
│   │   ├── CLAUDE_CODE_README.md
│   │   └── OPENALEX_SCHEDULED_PROCESSING_SETUP.md
│   └── inventory/  # Data inventories
│       ├── RAW_DATA_INVENTORY.md
│       ├── EMERGENCY_INVENTORY.json
│       └── CLEAN_WORKSPACE_INVENTORY.md
│
├── 🔧 scripts/  # [Already organized]
├── 📊 data/  # [Already organized - raw data safe]
├── 🌍 countries/  # [Country-specific work]
├── ⚙️ config/  # [Configuration files]
│
└── 📄 ROOT (clean)
    ├── README.md
    ├── requirements.txt
    ├── .gitignore
    ├── .env.local
    └── .pre-commit-config.yaml
```

---

## 🔴 FILES TO ARCHIVE (Untrusted Analysis)

### Audit Results (Questionable)
- audit_results_Germany_consolidated_20250919_072500.json
- audit_results_Germany_consolidated_20250919_074009.json
- audit_results_Italy_20250919_072500.json
- audit_results_Italy_20250919_074009.json
- audit_results_REWORKED_Italy_20250919_074151.json
- confidence_standardization_log.json

### Fabrication Documentation
- FABRICATED_DATA_INVENTORY.md
- FINAL_INTEGRITY_STATEMENT.md

---

## 📚 FILES TO ORGANIZE INTO DOCS

### To docs/standards/
- BEST_PRACTICES_ANALYSIS_AND_MCF_INTEGRATION_FINDINGS.md
- PHASE_BY_PHASE_AUDIT_PROTOCOL.md

### To docs/reports/
- DATA_PROCESSING_STATUS_REPORT.md
- IMPLEMENTATION_SUMMARY.md
- PHASE_ORCHESTRATOR_SUCCESS_REPORT.md
- ITALY_GERMANY_REMEDIATION_PLAN.md
- PROMPT_INTEGRATION_ROADMAP.md

### To docs/guides/
- CLAUDE_CODE_README.md
- OPENALEX_SCHEDULED_PROCESSING_SETUP.md
- PROJECT_STRUCTURE.md
- FINAL_STRUCTURE.md

### To docs/inventory/
- RAW_DATA_INVENTORY.md
- EMERGENCY_INVENTORY.json
- EMERGENCY_INVENTORY_SUMMARY.md
- CLEAN_WORKSPACE_INVENTORY.md

---

## 📂 FOLDERS TO CHECK

### Already Looks Archived
- ARCHIVED_ALL_ANALYSIS_20250919/
- archive/

### Suspicious - Need Review
- analysis/
- china_tech_analysis/
- artifacts/Germany_consolidated/
- artifacts/Italy_consolidated/

### Keep As-Is (Verified Data)
- data/ (raw data is safe)
- scripts/ (tools are fine)
- config/ (settings are fine)

---

## ✍️ ACTION PLAN

### Step 1: Create Archive for Untrusted
```bash
mkdir -p archive/untrusted_analysis_20250919
mv audit_results_*.json archive/untrusted_analysis_20250919/
mv confidence_standardization_log.json archive/untrusted_analysis_20250919/
mv FABRICATED_DATA_INVENTORY.md archive/untrusted_analysis_20250919/
mv FINAL_INTEGRITY_STATEMENT.md archive/untrusted_analysis_20250919/
```

### Step 2: Organize Documentation
```bash
# Standards
mkdir -p docs/standards
mv BEST_PRACTICES_ANALYSIS_AND_MCF_INTEGRATION_FINDINGS.md docs/standards/
mv PHASE_BY_PHASE_AUDIT_PROTOCOL.md docs/standards/

# Reports
mkdir -p docs/reports
mv DATA_PROCESSING_STATUS_REPORT.md docs/reports/
mv IMPLEMENTATION_SUMMARY.md docs/reports/
mv PHASE_ORCHESTRATOR_SUCCESS_REPORT.md docs/reports/
mv ITALY_GERMANY_REMEDIATION_PLAN.md docs/reports/
mv PROMPT_INTEGRATION_ROADMAP.md docs/reports/

# Guides
mkdir -p docs/guides
mv CLAUDE_CODE_README.md docs/guides/
mv OPENALEX_SCHEDULED_PROCESSING_SETUP.md docs/guides/
mv PROJECT_STRUCTURE.md docs/guides/
mv FINAL_STRUCTURE.md docs/guides/

# Inventory
mkdir -p docs/inventory
mv RAW_DATA_INVENTORY.md docs/inventory/
mv EMERGENCY_INVENTORY*.* docs/inventory/
mv CLEAN_WORKSPACE_INVENTORY.md docs/inventory/
```

### Step 3: Review Suspicious Folders
```bash
# Check what's in analysis/
ls -la analysis/

# Check china_tech_analysis/
ls -la china_tech_analysis/

# Check artifacts subdirs
ls -la artifacts/Germany_consolidated/
ls -la artifacts/Italy_consolidated/
```

---

## ✅ EXPECTED RESULT

Root folder will only contain:
- README.md
- requirements.txt
- Configuration files (.gitignore, .env.local, etc.)
- Well-organized subdirectories

All analysis without clear provenance will be in:
- `archive/untrusted_analysis_20250919/`

All documentation will be organized in:
- `docs/` with clear subcategories

---

## ⚠️ IMPORTANT NOTES

1. **RAW DATA IS SAFE** - Everything in `data/` that's actual downloads (TED, SEC, etc.) is fine
2. **SCRIPTS ARE FINE** - Tools in `scripts/` are just processors
3. **ARCHIVE SUSPICIOUS** - Any analysis, especially with numbers, goes to archive
4. **KEEP STANDARDS** - All our new anti-fabrication docs stay in docs/standards/
