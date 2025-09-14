# Project Organization & Architecture Guide

## Current Issues Identified

### 1. Root Directory Clutter
- **33 loose files** in root directory (Python scripts, docs, configs)
- Mixed purposes: utilities, analysis, documentation, configuration
- No clear separation between development tools and project outputs
- Temporary files (e.g., `~$eland_OSINT_Foresight_Analysis.docx`) not excluded

### 2. Inconsistent Naming
- Mixed conventions: snake_case, PascalCase, kebab-case
- Country reports have inconsistent formats
- Python modules don't follow package conventions

### 3. Missing Standard Directories
- No `scripts/` for utilities
- No `tools/` for development helpers
- No `notebooks/` for exploratory analysis
- No `tests/` for quality assurance

## Proposed Directory Structure

```
osint-foresight/
├── README.md                      # Project overview
├── LICENSE                        # License file
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── Makefile                       # Build automation
├── pyproject.toml                 # Python project configuration
│
├── src/                          # Source code (existing, good!)
│   ├── __init__.py
│   ├── analysis/                 # Phase analysis modules
│   │   ├── __init__.py
│   │   ├── phase3_landscape.py   # Renamed from phase2
│   │   ├── phase4_supply_chain.py
│   │   └── ...
│   ├── collectors/               # Data collection modules
│   │   ├── __init__.py
│   │   ├── openalex.py
│   │   ├── cordis.py
│   │   └── patents.py
│   └── utils/                    # Shared utilities
│       ├── __init__.py
│       ├── bigquery.py
│       └── validation.py
│
├── scripts/                      # Standalone scripts (NEW)
│   ├── backup/                   # Backup utilities
│   │   ├── backup_manager.py
│   │   └── backup_project.bat
│   ├── setup/                    # Setup and configuration
│   │   ├── setup_bigquery.py
│   │   └── configure_environment.py
│   ├── analysis/                 # One-off analysis scripts
│   │   ├── analyze_chinese_institutions.py
│   │   ├── analyze_cordis.py
│   │   └── analyze_google_patents.py
│   └── utils/                    # Utility scripts
│       ├── convert_to_word.py
│       └── verify_renumbering.py
│
├── tools/                        # Development tools (NEW)
│   ├── data_loaders/            # BigQuery loaders
│   │   ├── load_country_data.py
│   │   └── load_autodetect.py
│   └── visualization/            # Visualization tools
│       └── visualize_country_data.py
│
├── config/                       # Configuration (existing, good!)
│   ├── models.yaml
│   ├── indicators/
│   └── taxonomy/
│
├── data/                         # Data directory (existing, good!)
│   ├── raw/                     # Original data
│   ├── interim/                  # Intermediate processing
│   └── processed/                # Final processed data
│       └── country={CODE}/       # Country-specific data
│
├── artifacts/                    # Generated artifacts (NEW)
│   └── country={CODE}/           # Country-specific artifacts
│       ├── phase1_baseline.json
│       ├── phase2_indicators.json
│       └── ...
│
├── reports/                      # Reports (existing, good!)
│   └── country={CODE}/           # Country reports
│       ├── phase-0_taxonomy.md
│       ├── phase-1_setup.md
│       └── ...
│
├── docs/                         # Documentation (reorganize)
│   ├── architecture/             # System architecture docs (NEW)
│   │   ├── PROJECT_ORGANIZATION_GUIDE.md
│   │   ├── PHASE_RENUMBERING_GUIDE.md
│   │   └── NAMING_CONVENTIONS.md
│   ├── methodology/              # Methodology docs (NEW)
│   │   ├── FORESIGHT_METHODOLOGY.md
│   │   ├── CRITICAL_TECH_ASSESSMENT.md
│   │   └── CONTEXTUALIZATION_FRAMEWORK.md
│   ├── guides/                   # How-to guides (NEW)
│   │   ├── SETUP.md
│   │   ├── BACKUP_GUIDE.md
│   │   └── bigquery_setup_guide.md
│   ├── prompts/                  # Prompt library (existing)
│   │   ├── CHATGPT_MASTER_PROMPT_V3.2.md
│   │   ├── CLAUDE_CODE_MASTER_PROMPT_V1.2.md
│   │   └── archive/
│   └── references/               # Reference materials
│
├── notebooks/                    # Jupyter notebooks (NEW)
│   ├── exploratory/             # Exploratory analysis
│   └── reports/                 # Report generation notebooks
│
├── tests/                        # Test suite (NEW)
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data
│
├── evidence/                     # Evidence & validation (existing)
│   ├── screenshots/
│   └── validation_reports/
│
├── queries/                      # Query definitions (existing)
│   └── keywords/
│       └── country={CODE}/
│
├── archive/                      # Archived materials (existing)
│   └── country={CODE}/
│
└── out/                         # Build outputs (NEW)
    └── exports/                 # Export files
        └── country={CODE}/
            └── *.docx           # Word documents
```

## Naming Conventions

### 1. Files
- **Python modules**: `snake_case.py` (e.g., `phase3_landscape.py`)
- **Scripts**: `verb_noun.py` (e.g., `analyze_patents.py`, `load_data.py`)
- **Documentation**: `UPPER_SNAKE_CASE.md` for guides, `Title_Case.md` for reports
- **Configuration**: `snake_case.yaml` or `snake_case.json`
- **Data files**: `phase{N}_{description}.{ext}` (e.g., `phase3_actors.json`)

### 2. Directories
- **Source code**: `snake_case/` (e.g., `src/analysis/`)
- **Country-specific**: `country={CODE}/` (e.g., `country=AT/`)
- **Archive with dates**: `YYYYMMDD_description/` for timestamped archives

### 3. Variables & Functions (Python)
- **Functions**: `snake_case()` (e.g., `load_country_data()`)
- **Classes**: `PascalCase` (e.g., `DataLoader`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `POLICY_WINDOW`)
- **Private**: `_leading_underscore` (e.g., `_internal_helper()`)

### 4. Phase Numbering (0-13)
- Always use new numbering in file names
- Phase 0: Taxonomy & Definitions
- Phase 1: Setup
- Phase 2: Indicators
- Phase 3: Landscape
- Phase 4: Supply Chain
- Phase 5: Institutions
- Phase 6: Funding
- Phase 7: Links
- Phase 8: Risk
- Phase 9: PRC/MCF
- Phase 10: Red Team
- Phase 11: Foresight
- Phase 12: Extended
- Phase 13: Closeout

## Implementation Priority

### Immediate Actions (Priority 1)
1. Move Python scripts from root to appropriate directories
2. Move documentation files to `docs/` subdirectories
3. Create `.gitignore` to exclude temp files and `.docx` from root
4. Archive old/unused files

### Short-term (Priority 2)
1. Create `scripts/`, `tools/`, and `artifacts/` directories
2. Reorganize existing scripts into categories
3. Update imports in Python files
4. Create `__init__.py` files for packages

### Medium-term (Priority 3)
1. Set up testing framework
2. Create notebooks for exploratory work
3. Implement automated organization checks
4. Document all conventions in team wiki

## Git Ignore Recommendations

Add to `.gitignore`:
```
# Temporary files
~$*
*.tmp
*.bak
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDE
.vscode/
.idea/
*.swp
*.swo

# Output files in root (should be in out/)
/*.docx
/*.xlsx
/*.pptx

# Local config
.env
.env.local
*.local

# BigQuery credentials
*credentials*.json
*service-account*.json

# Large data files
*.csv
!metric_catalog.csv
!procurement_signals.csv
```

## Benefits of This Organization

1. **Clarity**: Clear separation of concerns
2. **Scalability**: Easy to add new countries/phases
3. **Maintainability**: Logical structure for team collaboration
4. **Reproducibility**: Clear data flow from raw → processed → artifacts → reports
5. **Version Control**: Better git history with organized files
6. **Testing**: Dedicated test structure
7. **Documentation**: Centralized, categorized docs
8. **Automation**: Scripts organized by purpose

## Migration Checklist

- [ ] Backup current state
- [ ] Create new directory structure
- [ ] Move Python analysis scripts to `scripts/analysis/`
- [ ] Move setup/config scripts to `scripts/setup/`
- [ ] Move BigQuery tools to `tools/data_loaders/`
- [ ] Move documentation to appropriate `docs/` subdirectories
- [ ] Update all import statements
- [ ] Update Makefile paths
- [ ] Test all scripts still work
- [ ] Update README with new structure
- [ ] Commit with clear message about reorganization
- [ ] Tag version before and after reorganization

## Continuous Improvement

1. **Weekly**: Review root directory for misplaced files
2. **Monthly**: Audit naming conventions
3. **Quarterly**: Review architecture for improvements
4. **Per Phase**: Ensure outputs follow structure
5. **Per Country**: Validate consistent organization
