# OSINT Foresight Project Structure

## Directory Organization

```
osint-foresight/
│
├── artifacts/          # Generated analysis artifacts by country
│   └── {Country}/      # Country-specific outputs (e.g., Italy/)
│       └── _national/  # National-level analysis JSONs
│
├── config/             # Configuration files
│   ├── indicators/     # Country-specific indicator configurations
│   ├── models.yaml     # Model configurations
│   ├── env.example     # Environment variable template
│   └── *.yaml          # Various config files
│
├── data/              # Data pipeline directories
│   ├── raw/           # Original data sources
│   ├── interim/       # Intermediate processing
│   └── processed/     # Final processed data
│       └── country={CODE}/  # Country-specific processed data
│
├── docs/              # Documentation
│   ├── prompts/       # Prompt templates and masters
│   │   └── archive/   # Archived/deprecated prompts
│   ├── reports/       # Analysis reports
│   └── *.md           # Documentation files
│
├── evidence/          # Evidence and validation data
│   ├── citations/     # Citation tracking
│   └── screenshots/   # Visual evidence (not in Git)
│
├── queries/           # Search queries and keywords
│   └── keywords/      # Country-specific keyword sets
│       └── country={CODE}/
│
├── reports/           # Generated analysis reports
│   ├── archive/       # Archived reports
│   └── country={CODE}/ # Country-specific reports
│
├── scripts/           # Utility and automation scripts
│   ├── archive/       # Archived/deprecated scripts
│   └── *.py           # Active Python scripts
│
├── src/               # Source code
│   ├── analysis/      # Analysis modules
│   └── utils/         # Utility modules
│
├── tests/             # Test files
│   └── test_*.py      # Unit and integration tests
│
├── tools/             # External tools and utilities
│
└── Root Files:
    ├── .gitignore     # Git ignore rules
    ├── .pre-commit-config.yaml  # Pre-commit hooks
    ├── Makefile       # Build automation
    ├── README.md      # Project documentation
    ├── pyproject.toml # Python project config
    └── requirements.txt # Python dependencies
```

## Key Principles

1. **Country Data Organization**: Use `country={CODE}` pattern for consistency
2. **Separation of Concerns**: Keep raw, interim, and processed data separate
3. **Archive Strategy**: Move deprecated files to `archive/` subdirectories
4. **Configuration Centralization**: All configs in `config/` directory
5. **Documentation Focus**: Comprehensive docs in `docs/` directory

## File Naming Conventions

- **Reports**: `phase-{N}_{name}.md` (e.g., `phase-1_indicators.md`)
- **Data**: Use lowercase with underscores (e.g., `supply_chain_map.json`)
- **Scripts**: Descriptive names with underscores (e.g., `process_cordis_data.py`)
- **Configs**: Purpose-based naming (e.g., `temporal_awareness_requirements.yaml`)

## Data Flow

```
raw/ → interim/ → processed/ → artifacts/ → reports/
         ↓           ↓            ↓           ↓
     [scripts/]  [src/analysis/] [queries/] [docs/]
```

## Important Notes

- Large datasets (CORDIS, OpenAlex, etc.) should be stored externally, not in Git
- Use `.gitignore` to exclude generated files and large datasets
- Archive old versions rather than deleting them
- Maintain consistent country code usage (ISO 3166-1 alpha-2)
