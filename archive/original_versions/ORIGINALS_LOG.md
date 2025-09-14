# Original Versions Log

## Purpose
This directory contains the original versions of documents before temporal compliance fixes or other major updates. These are preserved for reference and rollback capability.

## Files

### Italy Executive Brief
**File**: `Italy/ITALY_EXECUTIVE_BRIEF_ORIGINAL.md`
**Date Archived**: 2025-09-14
**Reason**: Temporal non-compliance - contained 2024-2025 recommendations

**Issues Found**:
1. "Immediate (2024-2025)" - past tense timeline
2. "Target: 1.55% GDP by 2025" - too soon (only 3.5 months)
3. "65% compliance by 2025" - unrealistic timeline
4. "Medium-term (2025-2030)" - starts too early
5. "Scenario Outlook (2025-2033)" - should start from 2026
6. "Next Review: Q4 2025" - only weeks away

**Fixed Version Location**: `artifacts/Italy/_national/ITALY_EXECUTIVE_BRIEF.md`

## Version Control

| Document | Original Date | Archive Date | Issue Type | Fixed |
|----------|--------------|--------------|------------|-------|
| Italy Executive Brief | 2025-09-13 | 2025-09-14 | Temporal | ✅ |

## Recovery Instructions

If you need to restore an original version:

```bash
# To view differences
diff original_versions/Italy/ITALY_EXECUTIVE_BRIEF_ORIGINAL.md \
     ../artifacts/Italy/_national/ITALY_EXECUTIVE_BRIEF.md

# To restore (NOT RECOMMENDED without review)
cp original_versions/Italy/ITALY_EXECUTIVE_BRIEF_ORIGINAL.md \
   ../artifacts/Italy/_national/ITALY_EXECUTIVE_BRIEF.md
```

## Compliance Notes

All originals in this folder failed temporal compliance checks for one or more of these reasons:
- References to past dates (2024, early 2025)
- Unrealistic immediate timelines (< 8 months)
- Budget cycle misunderstanding (FY2025/2026 changes)
- Missing implementation delays

## Archive Policy

1. **Never modify** files in this directory
2. **Always document** why a file was archived
3. **Keep the fixed version** reference updated
4. **Add new entries** to this log when archiving

---

*Log Started: September 14, 2025*
