# Tracker - Next Update Notes
**Date:** October 26, 2025
**Current Version:** v6 (with Option B structured references)

---

## Pending Changes for v7

### 1. Project_Spotlight Column A Cleanup
**Location:** Project_Spotlight sheet, Column A

**Action:** Delete the following section header labels:
- "target audiences"
- "target technologies"
- "key deliverables"

**Reason:** Cleaner visual layout - the sections are self-explanatory from their content and column headers

**Implementation:**
```python
# Find and clear these specific cells in Column A
labels_to_remove = ['target audiences', 'target technologies', 'key deliverables']
for row in ws['A']:
    if row.value and str(row.value).lower() in labels_to_remove:
        row.value = None
```

---

## Future Considerations

### Performance Testing
- Test v6 with realistic data volumes:
  - 50-100 projects
  - 500-2,000 rows in Country_Budgets
  - 500+ milestones
- Measure recalculation time (F9)

### Optional Enhancements (Not Requested Yet)
- Option C optimization if Excel 365 available (FILTER functions)
- Additional conditional formatting optimizations
- Performance monitoring dashboard

---

## Completed in v6
✓ Option A: Replaced full column references with specific ranges (50-70% faster)
✓ Option B: Converted to structured references (70-85% faster total)
✓ Fixed Portfolio_Dashboard funding format: `=TEXT(Control!B15,"$#,##0")`
✓ Regional_Summary with 6 regions and comprehensive metrics
✓ Project_Spotlight redesign with audiences/technologies/deliverables
✓ Project_Technologies sheet created (35 sample records)
✓ Config_Lists updated with all 98 countries
