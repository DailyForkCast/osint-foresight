# Phase 4: Automation & Prevention Setup Guide
**Version**: 1.0
**Date**: October 17, 2025
**Purpose**: Complete setup instructions for documentation automation

---

## Overview

Phase 4 implements automated systems to prevent future documentation drift and maintain documentation quality. This includes:
1. Git hooks for pre-commit validation
2. Weekly automated audits
3. Validation framework
4. Monitoring and reporting

---

## Components Created

### 1. Documentation Validation System
**File**: `validate_documentation.py`
**Purpose**: Validates documentation for outdated statistics and quality issues

**Capabilities**:
- Detects old database statistics (3.6 GB, 132 tables, 16.8M records)
- Verifies Tier 1+2 files contain current statistics
- Validates archive structure
- Can be used standalone or as git hook

**Usage**:
```bash
# Validate all documentation
python validate_documentation.py

# Validate only Tier 1 files
python validate_documentation.py --tier 1

# Run as git pre-commit hook (exit 1 on failure)
python validate_documentation.py --hook
```

### 2. Git Hooks Setup
**File**: `setup_git_hooks.py`
**Purpose**: Installs git hooks for automated validation

**Hooks Installed**:
- **pre-commit**: Validates documentation before allowing commit
- **pre-push**: Comprehensive validation before push

**Setup**:
```bash
# Install git hooks
python setup_git_hooks.py

# Test without installing
python setup_git_hooks.py --test

# Remove hooks
python setup_git_hooks.py --remove
```

**Bypass** (not recommended):
```bash
git commit --no-verify
git push --no-verify
```

### 3. Weekly Audit Script
**File**: `run_weekly_documentation_audit.bat`
**Purpose**: Runs automated weekly audits and archival

**Tasks Performed**:
1. Documentation validation
2. Archival preview (dry-run)
3. Database audit
4. Saves logs to `logs/` directory

### 4. Archival Automation
**File**: `archive_old_docs.py`
**Purpose**: Archives documentation >90 days old

**Usage**:
```bash
# Preview what would be archived (dry-run)
python archive_old_docs.py --dry-run

# Execute archival
python archive_old_docs.py

# Archive files older than 60 days
python archive_old_docs.py --age 60
```

---

## Setup Instructions

### Step 1: Install Git Hooks

**Purpose**: Prevent commits with outdated documentation

**Installation**:
```bash
cd "C:\Projects\OSINT - Foresight"
python setup_git_hooks.py
```

**Expected Output**:
```
Installing git hooks...

  ✅ Installed pre-commit
  ✅ Installed pre-push

============================================================
✅ Git hooks successfully installed!
============================================================

Installed hooks:
  - pre-commit: Validates documentation before commit
  - pre-push: Comprehensive validation before push
```

**Verification**:
```bash
# Check hooks exist
ls .git/hooks/pre-commit
ls .git/hooks/pre-push

# Test validation
python validate_documentation.py
```

### Step 2: Create Logs Directory

**Purpose**: Store weekly audit logs

**Setup**:
```bash
mkdir logs
echo "# Weekly Documentation Audit Logs" > logs/README.md
```

**Directory Structure**:
```
logs/
├── README.md
├── doc_validation_YYYYMMDD.log
├── archive_preview_YYYYMMDD.log
└── database_audit_YYYYMMDD.log
```

### Step 3: Schedule Weekly Audit

**Purpose**: Automated weekly validation and archival preview

**Windows Task Scheduler Setup**:

1. **Open Task Scheduler**:
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create New Task**:
   - Click "Create Basic Task..."
   - Name: "OSINT Documentation Weekly Audit"
   - Description: "Weekly documentation validation and archival preview"

3. **Set Trigger**:
   - Trigger: Weekly
   - Start: [Choose Sunday at 9:00 AM]
   - Recur every: 1 week

4. **Set Action**:
   - Action: Start a program
   - Program/script: `C:\Projects\OSINT - Foresight\run_weekly_documentation_audit.bat`
   - Start in: `C:\Projects\OSINT - Foresight`

5. **Set Conditions**:
   - ✓ Start only if computer is on AC power
   - ✓ Wake the computer to run this task
   - ✓ Start the task only if the computer is idle for: 10 minutes

6. **Set Settings**:
   - ✓ Allow task to be run on demand
   - ✓ Run task as soon as possible after scheduled start is missed
   - If task fails, restart every: 1 hour
   - Attempt to restart up to: 3 times

**Command-Line Setup** (alternative):
```bash
schtasks /create /tn "OSINT_Documentation_Weekly_Audit" ^
  /tr "C:\Projects\OSINT - Foresight\run_weekly_documentation_audit.bat" ^
  /sc WEEKLY /d SUN /st 09:00 /rl HIGHEST /f
```

**Verification**:
```bash
# Check scheduled task exists
schtasks /query /tn "OSINT_Documentation_Weekly_Audit"

# Run manually to test
schtasks /run /tn "OSINT_Documentation_Weekly_Audit"
```

### Step 4: Test the System

**Test Git Hooks**:
```bash
# Make a trivial change to test file
echo "test" > test_commit.txt
git add test_commit.txt
git commit -m "Test commit"

# Should see validation run
# If documentation has issues, commit will be blocked
```

**Test Validation**:
```bash
# Run standalone validation
python validate_documentation.py

# Should output:
# ============================================================
# Validating Tier 1 (Critical) Documentation
# ============================================================
#   ✅ PASSED: README.md
#   ✅ PASSED: CLAUDE_CODE_MASTER_V9.8_COMPLETE.md
#   ...
```

**Test Archival (Dry-Run)**:
```bash
# Preview what would be archived
python archive_old_docs.py --dry-run

# Should output files >90 days old
# No files will be moved in dry-run mode
```

**Test Weekly Audit**:
```bash
# Run manually
run_weekly_documentation_audit.bat

# Check logs created
dir logs\
```

---

## Monitoring and Maintenance

### Weekly Review Checklist

Every week, review the automated audit logs:

1. **Check Validation Log**:
   - Location: `logs/doc_validation_YYYYMMDD.log`
   - Look for: Errors or warnings
   - Action: Fix any issues found

2. **Check Archival Preview**:
   - Location: `logs/archive_preview_YYYYMMDD.log`
   - Look for: Files ready for archival
   - Action: Review and execute archival if appropriate

3. **Check Database Audit**:
   - Location: `logs/database_audit_YYYYMMDD.log`
   - Look for: Database statistics changes
   - Action: Update documentation if significant changes

### Monthly Tasks

**First Week of Month**:
1. Run archival (not dry-run):
   ```bash
   python archive_old_docs.py
   ```

2. Review archived files:
   ```bash
   # Check current month's archive
   ls analysis/archive/YYYY-MM/
   ls KNOWLEDGE_BASE/archive/YYYY-MM/
   ```

3. Verify ARCHIVE_INDEX.md created:
   ```bash
   cat analysis/archive/YYYY-MM/ARCHIVE_INDEX.md
   cat KNOWLEDGE_BASE/archive/YYYY-MM/ARCHIVE_INDEX.md
   ```

**Quarterly (Every 3 Months)**:
1. Review ARCHIVAL_POLICY.md effectiveness
2. Update protected files list if needed
3. Review archive retention thresholds
4. Update DOCUMENTATION_INDEX.md with new major documents

**Annually (Every 12 Months)**:
1. Comprehensive documentation audit
2. Review Tier 4 archives (>365 days old)
3. Decide: Keep, compress further, or delete
4. Update automation scripts if needed

---

## Troubleshooting

### Git Hook Issues

**Problem**: Hook not executing
```bash
# Check hook file exists and is executable
ls -la .git/hooks/pre-commit

# Reinstall hooks
python setup_git_hooks.py --remove
python setup_git_hooks.py
```

**Problem**: Hook blocking valid commits
```bash
# Review validation errors
python validate_documentation.py

# If errors are false positives, update protected patterns in validate_documentation.py
# Or bypass once (not recommended):
git commit --no-verify
```

### Validation Issues

**Problem**: False positive on old values
```bash
# Check what triggered the error
python validate_documentation.py --tier 1

# If legitimate historical reference, add to protected patterns
# Edit: validate_documentation.py
```

**Problem**: Missing current values warning
```bash
# Verify current statistics
python audit_database.py

# Update Tier 1+2 files with current values
```

### Scheduler Issues

**Problem**: Scheduled task not running
```bash
# Check task status
schtasks /query /tn "OSINT_Documentation_Weekly_Audit" /v

# Check task history in Task Scheduler GUI
# Action Center → Task Scheduler Library → History
```

**Problem**: Logs not being created
```bash
# Verify logs directory exists
mkdir logs

# Run batch file manually
run_weekly_documentation_audit.bat

# Check for errors in output
```

### Archival Issues

**Problem**: Protected files being flagged for archival
```bash
# Review protected files list in archive_old_docs.py
# Add missing files to PROTECTED_FILES or PROTECTED_PATTERNS
```

**Problem**: Archive structure missing
```bash
# Recreate archive directories
mkdir analysis\archive
mkdir KNOWLEDGE_BASE\archive

# Run archival to create month directories
python archive_old_docs.py --dry-run
```

---

## Configuration Reference

### Files Modified by Automation

**By Git Hooks**: None (read-only validation)

**By Weekly Audit**:
- `logs/doc_validation_*.log` (created)
- `logs/archive_preview_*.log` (created)
- `logs/database_audit_*.log` (created)

**By Monthly Archival**:
- Files moved to `analysis/archive/YYYY-MM/`
- Files moved to `KNOWLEDGE_BASE/archive/YYYY-MM/`
- `ARCHIVE_INDEX.md` created/updated in each month

### Protected Files (Never Modified by Automation)

**Tier 1**:
- README.md
- docs/prompts/active/master/CLAUDE_CODE_MASTER_V9.8_COMPLETE.md
- docs/UNIFIED_DATA_INFRASTRUCTURE_INVENTORY_MULTICOUNTRY.md
- docs/SCRIPTS_INVENTORY.md

**Tier 2**:
- All files in KNOWLEDGE_BASE/04_PROJECT_ARCHITECTURE/
- ARCHIVAL_POLICY.md
- DOCUMENTATION_REMEDIATION_COMPLETION_REPORT.md

**Active Status Files**:
- analysis/DATABASE_CURRENT_STATUS.md
- data/processing_status.json
- Active checkpoint files (<30 days old)

### Customization Options

**Change Archival Age Threshold**:
```bash
# Archive files older than 60 days instead of 90
python archive_old_docs.py --age 60
```

**Modify Protected Files**:
Edit `archive_old_docs.py` and `validate_documentation.py`:
```python
PROTECTED_FILES = [
    # Add your files here
    "YOUR_PROTECTED_FILE.md"
]

PROTECTED_PATTERNS = [
    # Add patterns here
    "IMPORTANT",
    "CRITICAL"
]
```

**Change Weekly Audit Schedule**:
```bash
# Modify scheduled task to run daily instead of weekly
schtasks /change /tn "OSINT_Documentation_Weekly_Audit" /sc DAILY /st 09:00
```

---

## Success Metrics

### Documentation Health Indicators

**Green (Healthy)**:
- ✅ All Tier 1+2 validation passes
- ✅ No files >90 days in active directories (except protected)
- ✅ Archive structure consistent
- ✅ ARCHIVE_INDEX.md exists for all archive months
- ✅ Weekly audit logs show no errors

**Yellow (Needs Attention)**:
- ⚠️ Validation warnings present
- ⚠️ Some files >90 days not yet archived
- ⚠️ Missing ARCHIVE_INDEX.md for recent months
- ⚠️ Scheduled task missed runs

**Red (Action Required)**:
- ❌ Tier 1+2 validation errors
- ❌ Protected files contain old values
- ❌ Archive structure broken
- ❌ Scheduled task failing consistently
- ❌ Documentation drift detected

### Monthly Report Template

```
OSINT Documentation Health Report - [Month YYYY]

Validation Status: [Green/Yellow/Red]
- Tier 1 Files: [Pass/Fail]
- Tier 2 Files: [Pass/Fail]
- Archive Structure: [Valid/Issues]

Archival Activity:
- Files Archived: [count]
- Total Archive Size: [MB]
- Oldest Active File: [days]

Issues Found:
- [List any issues]

Actions Taken:
- [List remediation actions]

Next Month Focus:
- [Planned improvements]
```

---

## Phase 4 Completion Checklist

- [x] Created validate_documentation.py
- [x] Created setup_git_hooks.py
- [x] Created run_weekly_documentation_audit.bat
- [x] Documented setup procedures
- [ ] **MANUAL STEP**: Install git hooks (run setup_git_hooks.py)
- [ ] **MANUAL STEP**: Create logs directory
- [ ] **MANUAL STEP**: Schedule weekly audit in Task Scheduler
- [ ] **MANUAL STEP**: Test all automation systems
- [ ] **MANUAL STEP**: Run first weekly audit manually

---

## Related Documentation

- **ARCHIVAL_POLICY.md**: Complete archival policy
- **DOCUMENTATION_INDEX.md**: Master documentation navigation
- **DOCUMENTATION_REMEDIATION_COMPLETION_REPORT.md**: Phases 1+2 results
- **archive_old_docs.py**: Archival automation script

---

## Next Steps

1. **Install git hooks**:
   ```bash
   python setup_git_hooks.py
   ```

2. **Create logs directory**:
   ```bash
   mkdir logs
   ```

3. **Schedule weekly audit**: Follow Step 3 above

4. **Test system**:
   ```bash
   python validate_documentation.py
   python archive_old_docs.py --dry-run
   run_weekly_documentation_audit.bat
   ```

5. **Monitor for one month**: Review logs weekly, adjust as needed

6. **Document lessons learned**: Update this guide with any issues encountered

---

**Status**: ✅ AUTOMATION SCRIPTS COMPLETE
**Manual Steps**: 4 setup tasks required (see checklist above)
**Estimated Setup Time**: 15-20 minutes
**Next Review**: Weekly for first month, then monthly

---

*This guide documents the complete Phase 4 automation setup for preventing future documentation drift in the OSINT Foresight project.*
