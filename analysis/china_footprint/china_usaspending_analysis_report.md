# China Analysis: USASpending Data

Generated: 2025-09-25T15:10:51.739093

## Executive Summary

- **Records Analyzed**: 9,397,541
- **China-Related Findings**: 0
- **Risk Indicators**: 2

## Temporal Analysis

| Year | Records |
|------|--------|
| 1979 | 1 |
| 1980 | 5 |
| 1987 | 1 |
| 1990 | 1 |
| 2007 | 1 |
| 2008 | 1 |
| 2011 | 5 |
| 2014 | 8 |
| 2015 | 2 |
| 2016 | 16 |
| 2017 | 12 |
| 2018 | 51 |
| 2019 | 27 |
| 2020 | 51 |
| 2021 | 28 |
| 2023 | 9 |
| 2024 | 7 |
| 2025 | 31 |

## Database Structure Analysis

- **Vendor Tables**: 2
- **Contract Tables**: 1
- **Award Tables**: 7
- **Geographic Columns**: 115

## Risk Indicators

### Recent Activity
- **Severity**: LOW
- **Description**: Activity detected in recent years: 2020, 2021, 2024, 2025, 2023
- **Recommendation**: Analyze trend over time

### Large Dataset
- **Severity**: INFO
- **Description**: Dataset contains 9,397,541 records
- **Recommendation**: Consider sampling or distributed processing for detailed analysis

## Recommendations

### Priority: HIGH
**Action**: Extract and analyze vendor tables

**Reason**: Vendor data can reveal foreign entity participation

**Tables to analyze**:
- rpt.recipient_lookup
- rpt.recipient_profile

### Priority: HIGH
**Action**: Analyze contract data for China-related terms

**Reason**: Contracts may reference Chinese entities or technology

**Tables to analyze**:
- raw.source_procurement_transaction

### Priority: MEDIUM
**Action**: Set up PostgreSQL and restore full database

**Reason**: Enable SQL queries for comprehensive analysis

### Priority: LOW
**Action**: Process large compressed files

**Reason**: May contain additional procurement or financial data

## Next Steps

1. **Immediate**: Review identified China-related entities
2. **Short-term**: Set up PostgreSQL for full database access
3. **Medium-term**: Implement automated scanning for China patterns
4. **Long-term**: Build comprehensive foreign entity tracking system
