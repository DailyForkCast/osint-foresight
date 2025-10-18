# Documentation Archival Policy
**Version**: 1.0
**Effective Date**: October 17, 2025
**Last Updated**: October 17, 2025
**Managed By**: archive_old_docs.py (automated script)

---

## Purpose

This policy establishes systematic archival procedures for OSINT Foresight project documentation to:
- Maintain clean, navigable active documentation directories
- Preserve historical analysis and session records
- Prevent accidental loss of valuable insights
- Enable efficient retrieval of archived materials
- Establish clear retention tiers for different document types

---

## Scope

### Files Covered by This Policy
This archival policy applies to **documentation files only**:
- `.md` (Markdown documentation)
- `.json` (Analysis results, reports, checkpoints)
- `.txt` (Text reports, logs, summaries)

### Files NEVER Archived
The following are **permanently excluded** from archival:
- **Python scripts** (`.py` files) - Code is never archived, only documented
- **Batch files** (`.bat` files) - Operational scripts remain active
- **Configuration files** (`.json` in `config/` directory)
- **Database files** (`.db`, `.sqlite`)
- **Data files** (`.csv`, `.tsv`, `.parquet`, `.gz`)
- **Binary files** (executables, images, etc.)

---

## Archival Criteria

### Age-Based Archival
Files are evaluated for archival based on **time since last modification** (not creation date).

**Rationale**: A file last modified 3 months ago is stale regardless of when it was created. Active files that are regularly updated remain current.

### Automatic Archival After 90 Days
Files meeting ALL of the following criteria are automatically archived:
1. **Age**: Last modified >90 days ago
2. **File Type**: One of `.md`, `.json`, `.txt`
3. **Not Protected**: Not in protected categories (see below)
4. **Location**: In `analysis/` or `KNOWLEDGE_BASE/` directories

### Protected File Categories
The following files are **NEVER archived**, regardless of age:

#### Tier 1: Critical Documentation
- `README.md` (root)
- `docs/prompts/active/master/CLAUDE_CODE_MASTER_V9.8_COMPLETE.md`
- `docs/UNIFIED_DATA_INFRASTRUCTURE_INVENTORY_MULTICOUNTRY.md`
- `docs/SCRIPTS_INVENTORY.md`

#### Tier 2: Architecture Documentation
- All files in `KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/`
- Current master prompts in `docs/prompts/active/`

#### Active Status Files
Files with "CURRENT" or "STATUS" in name, modified within 30 days:
- `analysis/DATABASE_CURRENT_STATUS.md`
- `data/processing_status.json`
- `data/ted_production_checkpoint.json`
- Any `*_CHECKPOINT.json` actively being updated

#### Active Validation Results
- Leonardo Standard validation results modified within 30 days
- Current cross-reference validation reports

---

## Retention Tiers

### Tier 1: Active (0-90 days)
**Location**: Parent directories (`analysis/`, `KNOWLEDGE_BASE/`)
**Status**: Fully active, no restrictions
**Action**: None required

### Tier 2: Archived (90-180 days)
**Location**: Archive subdirectories (`analysis/archive/`, `KNOWLEDGE_BASE/archive/`)
**Organization**: By archival date (YYYY-MM format) and data source
**Status**: Read-only, preserved for reference
**Action**: Moved to archive by `archive_old_docs.py`

### Tier 3: Compressed (180-365 days)
**Location**: Same archive subdirectories
**Organization**: Compressed by data source into `.tar.gz` archives
**Status**: Compressed but locally accessible
**Action**: Automated compression by `compress_archives.py` (future)

### Tier 4: Deep Archive (>365 days)
**Location**: To be determined (external storage or deletion)
**Organization**: Annual reviews
**Status**: Reviewed for deletion or long-term storage
**Action**: Manual review process

---

## Archive Organization

### KNOWLEDGE_BASE Archive Structure
```
KNOWLEDGE_BASE/archive/
├── 2025-09/
│   ├── ARCHIVE_INDEX.md
│   └── [archived .md files from September 2025]
├── 2025-10/
│   ├── ARCHIVE_INDEX.md
│   └── [archived .md files from October 2025]
└── [future months]/
```

**Files Archived Here**:
- Session summaries (SESSION_SUMMARY_*.md)
- Temporary documentation (*_TEMP_*, *_DRAFT_*)
- Superseded guides/documentation
- Old lesson learned reports (after consolidation into master)

### Analysis Archive Structure
```
analysis/archive/
├── 2025-09/
│   ├── ARCHIVE_INDEX.md
│   ├── openalex/
│   ├── ted/
│   ├── uspto/
│   ├── usaspending/
│   └── cross-source/
├── 2025-10/
│   ├── [same structure]
└── [future months]/
```

**Data Source Categories**:
- **openalex/**: OpenAlex research collaboration analysis
- **ted/**: TED EU procurement analysis
- **uspto/**: USPTO patent analysis
- **usaspending/**: USAspending federal contract analysis
- **cross-source/**: Multi-source intelligence fusion reports

**Files Archived Here**:
- Temporary test outputs (*_TEST_*, *_SAMPLE_*, *_DEBUG_*)
- Processing checkpoint files (superseded state files)
- Superseded analysis reports (when newer version exists)
- One-off analysis results
- Validation reports (after findings incorporated into master)

---

## Archival Procedures

### Automated Archival (Recommended)

**Tool**: `archive_old_docs.py`
**Schedule**: Weekly (recommended) or monthly
**Execution**:
```bash
python archive_old_docs.py --dry-run  # Preview what would be archived
python archive_old_docs.py             # Execute archival
```

**Process**:
1. Scans `analysis/` and `KNOWLEDGE_BASE/` directories
2. Identifies files >90 days old (by last modification)
3. Excludes protected files (Tier 1+2, active checkpoints)
4. Creates YYYY-MM subdirectories as needed
5. Moves files to appropriate archive location
6. Updates ARCHIVE_INDEX.md in each month's directory
7. Generates archival summary report

### Manual Archival (Exception Cases)

To manually archive a file before 90 days:

#### For KNOWLEDGE_BASE files:
1. Move file to `KNOWLEDGE_BASE/archive/YYYY-MM/`
2. Update `KNOWLEDGE_BASE/archive/YYYY-MM/ARCHIVE_INDEX.md`
3. Document reason for early archival
4. Note superseding file if applicable

#### For analysis files:
1. Determine appropriate data source category
2. Move file to `analysis/archive/YYYY-MM/[source]/`
3. Update `analysis/archive/YYYY-MM/ARCHIVE_INDEX.md`
4. Document reason and superseding file

**Common reasons for manual archival**:
- File superseded by comprehensive report
- Test/debug file no longer relevant
- Duplicate analysis consolidated elsewhere
- Temporary investigation complete

---

## ARCHIVE_INDEX.md Format

Each month's archive directory must contain an `ARCHIVE_INDEX.md` with:

```markdown
# Archive Index - [Month Year]

**Archive Date**: YYYY-MM
**Files Archived**: [count]
**Total Size**: [size]

## Archived Files

| File Name | Original Location | Archive Date | Reason | Superseded By |
|-----------|-------------------|--------------|--------|---------------|
| [filename] | [path] | YYYY-MM-DD | [reason] | [new file or N/A] |

## Data Source Breakdown (analysis only)

- **openalex**: [count] files
- **ted**: [count] files
- **uspto**: [count] files
- **usaspending**: [count] files
- **cross-source**: [count] files

## Notes

[Any special notes about this month's archival]
```

---

## Retrieval Procedures

### Finding Archived Files

1. **Check README.md** in archive root directory
2. **Review ARCHIVE_INDEX.md** for specific month
3. **Search by approximate date**: Files organized by archival month
4. **Search by data source**: In `analysis/archive/YYYY-MM/[source]/`

### Accessing Compressed Archives (Tier 3)

```bash
# List contents without extracting
tar -tzf analysis/archive/2024-09/openalex_archive.tar.gz

# Extract specific file
tar -xzf analysis/archive/2024-09/openalex_archive.tar.gz [filename]

# Extract entire archive
tar -xzf analysis/archive/2024-09/openalex_archive.tar.gz -C [destination]
```

### Restoring Archived Files

To restore an archived file to active status:

1. **Verify file is still relevant**: Review content
2. **Check for superseding files**: Ensure no newer version exists
3. **Copy (don't move)** from archive to active directory
4. **Update ARCHIVE_INDEX.md**: Note file was restored
5. **Document restoration**: Add note in restoration location

**WARNING**: Never move files out of archives (always copy). Archives serve as historical record.

---

## Special Cases

### Session Summaries
- **Active Period**: 90 days from creation
- **Archival**: Move to `KNOWLEDGE_BASE/archive/YYYY-MM/`
- **Exception**: Major milestone summaries may be protected longer
- **Consolidation**: May be consolidated into quarterly summaries

### Checkpoint Files
- **Active**: While processing is ongoing or <30 days since completion
- **Archival**: 90 days after processing completion
- **Exception**: Keep most recent checkpoint for each data source indefinitely
- **Example**: Keep `ted_production_checkpoint.json` active even if >90 days old

### Validation Reports
- **Active**: Until findings incorporated into codebase or documentation
- **Archival**: 90 days after incorporation
- **Exception**: Leonardo Standard validation results kept for 180 days
- **Consolidation**: Major validation findings consolidated into master reports

### Test and Debug Files
- **Immediate Archival**: May be archived immediately after test completion
- **Retention**: 90-180 days in archive, then delete
- **Exception**: Test results demonstrating major bugs kept longer
- **Identification**: Files with *_TEST_*, *_SAMPLE_*, *_DEBUG_* patterns

### Comprehensive Reports
- **Protected Period**: 180 days minimum
- **Manual Review**: Required before archival
- **Criteria**: Must verify no unique insights would be lost
- **Examples**: COMPLETE_*, FINAL_*, COMPREHENSIVE_* files

---

## Integration with Scripts

### archive_old_docs.py
Primary automation script that implements this policy:
- Scans directories for archival candidates
- Applies all protection rules
- Creates archive structure
- Generates ARCHIVE_INDEX.md
- Produces archival report

### compress_archives.py (Future)
Automated compression for Tier 3 archival:
- Identifies archives >180 days old
- Compresses by data source into .tar.gz
- Preserves ARCHIVE_INDEX.md
- Updates archive README.md

### validate_documentation.py (Future)
Validation script for documentation health:
- Verifies all Tier 1+2 files present
- Checks for documentation drift
- Validates archive structure
- Reports missing ARCHIVE_INDEX.md files

---

## Policy Maintenance

### Quarterly Review
Every 3 months, review this policy for:
- Effectiveness of 90-day threshold
- Protected file list accuracy
- Archive organization structure
- Compression/deletion thresholds

### Annual Audit
Every 12 months:
- Review all Tier 4 archives (>365 days)
- Decide: Keep, compress further, or delete
- Update retention policies if needed
- Document lessons learned

### Policy Updates
When updating this policy:
1. Increment version number
2. Update "Last Updated" date
3. Document changes in CHANGELOG section (below)
4. Notify team of policy changes
5. Update `archive_old_docs.py` if automation affected

---

## Exemptions and Exceptions

### Project-Wide Exemptions
Files that should remain active indefinitely:
- All Tier 1+2 critical documentation
- SCRIPTS_INVENTORY.md
- Current architecture documentation
- Active processing checkpoints

### Temporary Exemptions
To temporarily exempt a file from archival:
1. Add `.noarchive` suffix to filename (e.g., `report.md.noarchive`)
2. Document reason in file header
3. Set review date for exemption
4. Remove suffix when archival appropriate

### Data Source Exemptions
Certain data sources may have different retention:
- **OpenAlex**: Processing reports kept 180 days (dataset is massive)
- **TED**: Detection method analysis kept 180 days (format evolution tracking)
- **USPTO**: Patent classification reports kept 180 days (strategic tech tracking)

---

## Compliance and Quality Metrics

### Archive Health Metrics
Monitor these indicators monthly:
- **Archive Growth Rate**: Size of archives per month
- **Retrieval Frequency**: How often archived files accessed
- **Restoration Rate**: How many files moved back to active
- **Coverage**: % of eligible files successfully archived

### Quality Indicators
- All archive months have ARCHIVE_INDEX.md
- No files >90 days in active directories (except protected)
- Archive structure consistent across months
- Compressed archives follow naming convention

---

## Troubleshooting

### Problem: File archived too early
**Solution**: Copy (don't move) from archive back to active directory. Update ARCHIVE_INDEX.md with note.

### Problem: Protected file was archived
**Solution**: Immediately restore to original location. Update protected file list. Fix `archive_old_docs.py` if automation error.

### Problem: Archive month directory missing
**Solution**: Create directory with proper structure. Add ARCHIVE_INDEX.md. Populate with any files from that month found elsewhere.

### Problem: ARCHIVE_INDEX.md out of sync
**Solution**: Run `validate_archives.py` (future script) to regenerate index from actual files.

---

## CHANGELOG

### Version 1.0 (2025-10-17)
- Initial policy creation
- Established 90-day archival threshold
- Defined 4-tier retention structure
- Protected Tier 1+2 critical documentation
- Created archive organization by date and data source

---

## References

- **DOCUMENTATION_REMEDIATION_COMPLETION_REPORT.md**: Phase 1+2 completion report
- **SCRIPTS_INVENTORY.md**: Comprehensive scripts documentation
- **archive/README.md**: Archive directory documentation
- **archive_old_docs.py**: Automation script implementing this policy

---

## Contact and Questions

For questions about this policy or archival procedures:
1. Review this policy document
2. Check archive README.md files
3. Review ARCHIVE_INDEX.md for specific months
4. Consult DOCUMENTATION_REMEDIATION_COMPLETION_REPORT.md

---

**Policy Status**: ✅ ACTIVE
**Next Review**: January 2026
**Automation**: archive_old_docs.py (to be implemented)

---

*This policy ensures systematic, reversible, and well-documented archival of OSINT Foresight project documentation while protecting critical files and maintaining accessibility of historical materials.*
