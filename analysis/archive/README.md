# Analysis Archive

**Purpose**: Long-term storage for outdated or superseded analysis reports and temporary outputs

## Directory Structure

Files are organized by archival date (YYYY-MM format) and data source:
```
archive/
├── 2025-09/
│   ├── openalex/
│   ├── ted/
│   ├── uspto/
│   ├── usaspending/
│   └── cross-source/
├── 2025-10/
├── 2025-11/
└── [future months]
```

## What Gets Archived Here

**Auto-archived after 90 days (from last modification):**
- Temporary test outputs (*_TEST_*, *_SAMPLE_*, *_DEBUG_*)
- Processing checkpoint files (*.json state files)
- Superseded analysis reports (when newer version exists)
- One-off analysis results
- Validation reports (after findings incorporated)

**Manual review before archiving:**
- Comprehensive analysis reports (COMPLETE_*, FINAL_*)
- Cross-source intelligence reports
- Data quality assessments
- Strategic analysis summaries

**NEVER archived:**
- Current status reports (DATABASE_CURRENT_STATUS.md, etc.)
- Active processing checkpoints
- Leonardo Standard validation results (current)
- Master analysis summaries

## Data Source Categories

- **openalex/**: OpenAlex research collaboration analysis
- **ted/**: TED EU procurement analysis
- **uspto/**: USPTO patent analysis
- **usaspending/**: USAspending federal contract analysis
- **cross-source/**: Multi-source intelligence fusion reports

## Retention Policy

- **0-90 days**: Active (in parent analysis/ directory)
- **90-180 days**: Archived here (in YYYY-MM/source subdirectories)
- **180-365 days**: Compressed (tar.gz by data source)
- **>365 days**: Review for deletion or deep archive

## Accessing Archived Files

Each month's subdirectory contains an ARCHIVE_INDEX.md with details about archived files.

## Manual Archival

To manually archive a file before 90 days:
1. Move to appropriate YYYY-MM/[source] subdirectory
2. Update ARCHIVE_INDEX.md
3. Document reason and superseding file (if applicable)

---

**Last Updated**: 2025-10-17
**Managed By**: archive_old_docs.py (automated script)
