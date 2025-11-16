# TED Flagged Contracts Re-validation Report

**Generated:** 2025-10-24 20:39:24
**Total Contracts Reviewed:** 295
**Updated Detection:** Word boundaries + Nuctech + 10 additional companies

---

## Executive Summary

After applying word boundary fixes and updated Chinese company patterns, the 295 originally flagged TED contracts were re-validated.

### Results

| Category | Count | Percentage |
|----------|-------|------------|
| **True Chinese** | 151 | 51.2% |
| **False Positives** | 2 | 0.7% |
| **Uncertain (Needs Review)** | 142 | 48.1% |

### Precision Metrics

- **Actual Precision:** 51.19% (confirmed Chinese only)
- **Conservative Precision:** 99.32% (Chinese + uncertain)
- **False Positive Rate:** 0.68%

---

## True Chinese Contracts (151)

### Detection Methods

- **Known Chinese Company**: 135 contracts
- **CN/HK Country Code**: 15 contracts
- **Chinese Characters**: 1 contracts


### Sample True Chinese Contracts (First 10)

| Notice | Contractor | Country | Company | Reason |
|--------|------------|---------|---------|--------|
| ORG-0001 | N/A | None | Lenovo | Known company: Lenovo |
| ORG-0001 | N/A | None | Huawei | Known company: Huawei |
| ORG-0001 | N/A | None | Lenovo | Known company: Lenovo |
| ORG-0001 | N/A | None | Lenovo | Known company: Lenovo |
| ORG-0001 | N/A | None | Huawei | Known company: Huawei |
| ORG-0001 | N/A | None | Lenovo | Known company: Lenovo |
| ORG-0001 | N/A | None | Huawei | Known company: Huawei |
| ORG-0001 | N/A | None | Nuctech | Known company: Nuctech |
| RES-0001 | HOPSCOTCH HONGKONG LIMITED | HKG |  | CN/HK country code |
| RES-0001 | Eclat International Limited | HKG |  | CN/HK country code |


---

## False Positives (2)

### Common False Positive Patterns

- **European company: ltd**: 2 contracts


### Sample False Positives (First 10)

| Notice | Contractor | Country | Reason |
|--------|------------|---------|--------|
| RES-0001 | Ribcern International Ltd | NGA | European company: ltd |
| RES-0001 | Study Options Ltd | KEN | European company: ltd |


---

## Uncertain Contracts (142)

These contracts require manual review to confirm classification.

### Sample Uncertain Contracts (First 10)

| Notice | Contractor | Patterns Matched | Reason |
|--------|------------|------------------|--------|
| ORG-0001 | N/A | china | Only 'china' keyword: 1 pattern matches: china |
| ORG-0001 | N/A | china | Only 'china' keyword: 1 pattern matches: china |
| ORG-0001 | N/A | china | Only 'china' keyword: 1 pattern matches: china |
| RES-0001 | N/A | shenzhen | 1 pattern matches: shenzhen |
| ORG-0001 | N/A | hong kong | 1 pattern matches: hong kong |
| ORG-0001 | N/A | china | Only 'china' keyword: 1 pattern matches: china |
| ORG-0001 | N/A | china | Only 'china' keyword: 1 pattern matches: china |
| RES-0000 | N/A | hong kong | 1 pattern matches: hong kong |
| RES-0001 | N/A | chinese | 1 pattern matches: chinese |
| ORG-0001 | N/A | china | Only 'china' keyword: 1 pattern matches: china |


---

## Recommendations

### Immediate Actions

1. **Remove 2 False Positives**
   - Clear is_chinese_related flag for these contracts
   - Archive for audit trail

2. **Manual Review 142 Uncertain Contracts**
   - Export to Excel for manual classification
   - Focus on contracts with only 'china' keyword matches

3. **Update Precision Metrics**
   - Current actual precision: 51.19%
   - After cleanup: 151/293 = 51.5% minimum

### Database Updates Needed

```sql
-- Clear false positives
UPDATE ted_contracts_production
SET is_chinese_related = 0,
    chinese_confidence = 0.0,
    detection_rationale = 'False positive - removed in re-validation 20251024_203924'
WHERE id IN (
    -- List of 2 false positive IDs
);
```

---

## Files Generated

1. **Detailed Results:** `analysis/ted_revalidation_detailed_20251024_203924.json`
2. **Summary Report:** `analysis/ted_revalidation_summary_20251024_203924.json`
3. **This Report:** `analysis/TED_REVALIDATION_REPORT_20251024_203924.md`

---

**Re-validation Complete**
**Status:** Ready for database cleanup
**Next Step:** Manual review of 142 uncertain contracts
