# KNOWLEDGE_BASE Archive

**Purpose**: Long-term storage for outdated or superseded KNOWLEDGE_BASE documentation

## Directory Structure

Files are organized by archival date (YYYY-MM format):
```
archive/
├── 2025-09/
├── 2025-10/
├── 2025-11/
└── [future months]
```

## What Gets Archived Here

**Auto-archived after 90 days (from last modification):**
- Session summaries (SESSION_SUMMARY_*.md)
- Temporary documentation (*_TEMP_*, *_DRAFT_*)
- Superseded guides/documentation (when newer version exists)
- Old lesson learned reports (after consolidation)

**NEVER archived:**
- Current architecture documentation
- Active master prompts
- Critical project documentation (Tier 1+2 files)
- SCRIPTS_INVENTORY.md
- Current status reports

## Retention Policy

- **0-90 days**: Active (in parent KNOWLEDGE_BASE/ directory)
- **90-180 days**: Archived here (in YYYY-MM subdirectories)
- **180-365 days**: Compressed (tar.gz)
- **>365 days**: Review for deletion

## Accessing Archived Files

Each month's subdirectory contains an ARCHIVE_INDEX.md with details about archived files.

## Manual Archival

To manually archive a file before 90 days:
1. Move to appropriate YYYY-MM subdirectory
2. Update ARCHIVE_INDEX.md
3. Document reason in index

---

**Last Updated**: 2025-10-17
**Managed By**: archive_old_docs.py (automated script)
