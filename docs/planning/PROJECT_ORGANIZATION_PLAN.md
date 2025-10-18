# Project Organization Plan - OSINT Foresight

## Current Issues Identified
- **189 loose files** in root directory (needs major cleanup)
- Multiple terminal summary files scattered in root
- China analysis files mixed with other documents in root
- Test/diagnostic scripts mixed with production scripts
- Archived content from 2025-09-19 needs proper integration

## Proposed Directory Structure

```
OSINT-Foresight/
│
├── 📂 analysis/                    # Analysis outputs and reports
│   ├── china_footprint/           # China-specific analysis
│   ├── country_reports/           # Per-country analysis
│   └── terminal_summaries/        # Terminal A-F summaries
│
├── 📂 artifacts/                   # Country-specific processed data
│   ├── Italy/
│   ├── Germany/
│   └── [other countries]/
│
├── 📂 config/                      # Configuration files
│   ├── china_sources.json
│   ├── canonical_fields.json
│   └── provenance_tracking.json
│
├── 📂 data/                        # Raw and processed data
│   ├── processed/                 # Processed datasets
│   ├── raw/                       # Raw data files
│   └── test_harvest/              # Test data
│
├── 📂 database/                    # Database files and SQL
│   ├── schemas/
│   ├── queries/
│   └── osint_research.db
│
├── 📂 docs/                        # Documentation
│   ├── prompts/                   # Prompt templates
│   │   ├── active/master/         # Active master prompts
│   │   └── china_footprint_analysis.md
│   ├── guides/                    # User guides
│   ├── reports/                   # Project reports
│   └── standards/                 # Standards documentation
│
├── 📂 scripts/                     # Python scripts
│   ├── collectors/                # Data collection scripts
│   ├── analysis/                  # Analysis scripts
│   ├── processing/                # Data processing scripts
│   ├── utils/                     # Utility scripts
│   └── tests/                     # Test scripts
│
├── 📂 outputs/                     # Analysis outputs
│   └── [dated folders]/
│
├── 📂 archive/                     # Archived content
│   └── 2025-09-19/               # Previous analysis
│
└── README.md                       # Main documentation
```

## Files to Move (Priority Actions)

### 1. China Analysis Files → analysis/china_footprint/
- `china_analysis_*.sql`
- `china_analysis_*.json`
- `CHINA_ANALYSIS_SUMMARY.md`
- `china_collaboration_timeline.csv`

### 2. Terminal Summaries → analysis/terminal_summaries/
- `TERMINAL_*_SUMMARY.md` (all variants)
- `TERMINAL_*_STARTUP_GUIDE.md`
- `TERMINAL_*_REPORT.md`

### 3. Configuration Files → config/
- `canonical_fields.json`
- `access_controls.json`
- `provenance_fields_enhanced.json`

### 4. Test/Diagnostic Scripts → scripts/tests/
- `check_*.py`
- `diagnostic_*.py`
- `*_test.py`

### 5. Documentation → docs/reports/
- `DATA_COLLECTION_STATUS_REPORT.md`
- `MCF_*_REPORT.md`
- `OPENAIRE_*.md`
- `PROJECT_KNOWLEDGE_BASE_PROPOSAL.md`

### 6. SQL Files → database/queries/
- All `.sql` files in root

### 7. Backup Files → archive/backups/
- `README*.backup`
- `README_old.md`
- `*_backup.md`

## Cleanup Actions

### Files to Delete/Archive
1. Redundant README backups
2. Old terminal conversation logs
3. Duplicate analysis files
4. Temporary test outputs
5. `nul` file (appears to be an error)

### Files to Keep in Root
- `README.md` (main)
- `.gitignore`
- `.env.local`
- `requirements.txt` (if exists)
- `setup.py` (if exists)

## Implementation Priority

1. **High Priority**: Move China analysis files (current focus)
2. **High Priority**: Organize terminal summaries
3. **Medium Priority**: Clean up root directory files
4. **Medium Priority**: Organize scripts into subdirectories
5. **Low Priority**: Archive old analyses properly
6. **Low Priority**: Update all file references

## Benefits of Reorganization

✅ **Cleaner root directory** - from 189 files to ~5-10
✅ **Better discoverability** - logical grouping of related files
✅ **Easier maintenance** - clear separation of concerns
✅ **Improved collaboration** - team members can find files easily
✅ **Version control** - better git history with organized structure
✅ **Automated workflows** - scripts can rely on consistent paths

## Next Steps

1. Create missing directories
2. Move files according to plan
3. Update README with new structure
4. Update scripts to use new paths
5. Test all functionality
6. Commit changes with clear message
