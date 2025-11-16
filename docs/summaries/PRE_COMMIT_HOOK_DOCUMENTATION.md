# Pre-Commit Hook: SQL Injection Prevention

**Issue**: #31 - SQL Injection Vulnerability
**Date Deployed**: 2025-11-04
**Status**: ✅ Active
**Location**: `.git/hooks/pre-commit`

## Overview

The pre-commit hook automatically scans all staged Python files for SQL injection vulnerabilities before allowing commits. It blocks commits containing unsafe SQL patterns while allowing validated secure patterns.

## What It Blocks

The hook detects and blocks:

```python
# BLOCKED: Unvalidated variable in SQL
table_name = user_input
cur.execute(f"SELECT * FROM {table_name}")  # ❌ BLOCKED
```

## What It Allows

The hook permits these safe patterns:

### 1. Validated Variables (safe_ prefix)

```python
# ALLOWED: Validated with whitelist
ALLOWED_TABLES = {'entities', 'patents', 'collaborations'}

def validate_table_name(name):
    if name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {name}")
    return name

safe_table = validate_table_name(table)  # Validation enforced
cur.execute(f"SELECT * FROM {safe_table}")  # ✅ ALLOWED
```

### 2. Parameterized Queries

```python
# ALLOWED: Using ? placeholders
cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))  # ✅ ALLOWED
```

### 3. F-strings Without Variable Interpolation

```python
# ALLOWED: F-string for multi-line formatting only, no {variables}
cur.execute(f"""
    SELECT sql FROM sqlite_master
    WHERE type='table' AND name=?
""", (table_name,))  # ✅ ALLOWED
```

## Detection Logic

The hook performs these checks:

1. **Initial Scan**: Finds all `execute(f"...` patterns
2. **Validation Check**: For each match:
   - Has `{safe_*}` variables? → ✅ ALLOW (validated)
   - Has no `{variables}` at all? → ✅ ALLOW (f-string for formatting only)
   - Has `{unvalidated}` variables? → ❌ BLOCK (vulnerability)

## Testing Results

```bash
# Test 1: Safe file (merge_osint_databases.py)
Raw matches found: 8
✅ WOULD ALLOW - All uses are safe (safe_ prefix or no variables)

# Test 2: Unsafe file (test_sql_injection_hook.py)
Raw matches found: 1
✅ WOULD BLOCK - Vulnerability detected correctly
```

## If Your Commit Is Blocked

When the hook blocks your commit, you'll see:

```
❌ SQL INJECTION VULNERABILITY DETECTED!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File: scripts/example.py
Vulnerable lines:
  42:    cur.execute(f"SELECT * FROM {table}")

🛑 COMMIT BLOCKED: SQL injection patterns found
```

### Fix Options

**Option 1: Whitelist Validation** (for hardcoded lists)
```python
ALLOWED_TABLES = {'entities', 'patents', 'collaborations'}

def validate_table_name(name):
    if name not in ALLOWED_TABLES:
        raise ValueError(f'Invalid table: {name}')
    return name

safe_table = validate_table_name(table)
execute(f"SELECT * FROM {safe_table}")
```

**Option 2: Parameterized Queries** (for user input)
```python
# Replace this:
execute(f"SELECT * FROM users WHERE id = {user_id}")

# With this:
execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Option 3: Schema Validation** (for dynamic columns)
```python
cur.execute("PRAGMA table_info(table_name)")
valid_columns = {col[1] for col in cur.fetchall()}

def validate_column_name(col, valid_cols):
    if col not in valid_cols:
        raise ValueError(f'Invalid column: {col}')
    return col

safe_col = validate_column_name(column, valid_columns)
execute(f'SELECT * FROM table WHERE "{safe_col}" IS NULL')
```

## Bypassing the Hook

**NOT RECOMMENDED**: You can bypass with `git commit --no-verify`

Only use this for:
- Emergency hotfixes that will be fixed immediately after
- False positives (report these to the security team)

## Implementation Details

**File**: `.git/hooks/pre-commit`
**Pattern**: `execute\s*\(\s*f["\047]`
**Language**: Bash (portable)
**Performance**: < 1 second for typical commits

## References

- **Progress Report**: `SQL_INJECTION_REMEDIATION_PROGRESS.md`
- **Example Fixes**:
  - `scripts/merge_osint_databases.py` (whitelist pattern)
  - `scripts/qa_qc_audit_comprehensive.py` (schema pattern)
- **Master Audit**: `PHASE10_MASTER_FINDINGS_REPORT.md` (Issue #31)

## Maintenance

The hook runs automatically on every commit. No manual action required.

If the hook needs updates:
1. Edit `.git/hooks/pre-commit`
2. Test with `bash .git/hooks/pre-commit` (after staging test files)
3. Document changes in this file

## Status

✅ **Deployed**: 2025-11-04
✅ **Tested**: Blocks unsafe code, allows safe code
✅ **Active**: Protecting all future commits

This hook is part of **Week 1 Critical Security** fixes in the 8-week remediation roadmap.
