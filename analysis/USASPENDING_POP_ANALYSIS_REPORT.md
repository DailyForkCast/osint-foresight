# USAspending Place of Performance (POP) Analysis Report

**Generated:** 2025-10-25 20:03:02

---

## Executive Summary

This report addresses a critical data quality issue in USAspending data:

**Finding:** The `recipient_country_code` field in USAspending often reflects where contract work is performed (Place of Performance), not where the company is legally based.

**Impact:** This causes significant false positives when trying to identify contracts with Chinese entities.

**Solution:** We've added POP analysis flags to help users filter based on their specific needs.

---

## Categories Explained

**1. VERIFIED_POP_MATCH**
   - Recipient country code matches place of performance
   - Example: Chinese entity (CHN) with work in China (CHN)
   - **Highest confidence** these are actual entities from origin country

**2. ENTITY_FROM_ORIGIN_WORK_IN_USA**
   - Recipient coded as from origin country, work performed in USA
   - **Likely false positives** due to USAspending data quality issues
   - Example: ZACHRY CADDELL JV (coded CHN but work in USA)

**3. ENTITY_FROM_ORIGIN_WORK_ELSEWHERE**
   - Recipient from origin country, work in third country
   - Example: Chinese entity doing work in Switzerland
   - **Mixed confidence** - could be legitimate global operations

**4. POP_UNKNOWN**
   - Place of performance not specified in contract data
   - Requires manual review

---

## Recommendations for Analysis

**For identifying actual Chinese entities:**
```sql
SELECT * FROM usaspending_china_374_v2
WHERE pop_analysis_category = 'VERIFIED_POP_MATCH'
```

**For identifying Chinese entities operating in USA:**
```sql
SELECT * FROM usaspending_china_374_v2
WHERE pop_analysis_category IN ('VERIFIED_POP_MATCH', 'ENTITY_FROM_ORIGIN_WORK_ELSEWHERE')
-- Excludes likely false positives from work-in-USA coding
```

**For conservative analysis (highest confidence only):**
```sql
SELECT * FROM usaspending_china_374_v2
WHERE pop_matches_origin = 1
```

