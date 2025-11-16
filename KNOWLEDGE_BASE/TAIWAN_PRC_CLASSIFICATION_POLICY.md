# Taiwan/PRC Entity Classification Policy

**Effective Date:** October 22, 2025
**Policy Version:** 1.0
**Status:** ✅ APPROVED FOR IMPLEMENTATION

---

## Executive Summary

This policy establishes **mandatory separation** of Taiwan (Republic of China, ROC) entities from People's Republic of China (PRC) entities in all OSINT Foresight data processing, analysis, and reporting.

**Key Principle:** Taiwan is NOT part of the People's Republic of China and must be classified separately.

---

## Policy Statement

### 1. Core Classification Principle

**Taiwan and the PRC are SEPARATE jurisdictions** for all analytical purposes.

**Four Distinct Classifications Required:**
1. **PRC (People's Republic of China)** - Mainland China
2. **Taiwan (Republic of China, ROC)** - Taiwan
3. **Hong Kong SAR** - Special Administrative Region of PRC (since 1997)
4. **Macao SAR** - Special Administrative Region of PRC (since 1999)

### 2. Mandatory Separation

**PROHIBITED:**
- ❌ Aggregating Taiwan entities with PRC entities without explicit disclosure
- ❌ Using "China" or "Chinese" to refer ambiguously to both PRC and Taiwan
- ❌ Classifying Taiwan companies as "Chinese companies"
- ❌ Labeling Taiwan research institutions as "Chinese institutions"

**REQUIRED:**
- ✅ Separate country_of_origin field: 'CN' (PRC), 'TW' (Taiwan), 'HK' (Hong Kong), 'MO' (Macao)
- ✅ Explicit labeling in reports: "Taiwan (separate from PRC)"
- ✅ User choice to aggregate or keep separate based on research question
- ✅ Clear documentation when combining for specific analyses

### 3. Geographic Codes

**ISO 3166-1 alpha-2 Country Codes (MANDATORY):**

| Entity | Code | Full Name | Status |
|--------|------|-----------|--------|
| PRC | CN | People's Republic of China | Sovereign state |
| Taiwan | TW | Taiwan (Republic of China) | Separate jurisdiction |
| Hong Kong | HK | Hong Kong SAR | PRC Special Administrative Region (1997+) |
| Macao | MO | Macao SAR | PRC Special Administrative Region (1999+) |

**NEVER use:**
- "CHN" for Taiwan
- "ROC" as primary code (use TW)
- "Greater China" without explicit breakdown
- Ambiguous "China" without qualifier

### 4. Hong Kong & Macao Treatment

**Special Status Recognition:**

**Hong Kong:**
- **Pre-1997:** British territory (separate from PRC and Taiwan)
- **Post-1997:** PRC Special Administrative Region
- **Classification:** Code as 'HK', note SAR status
- **Analysis:** User decides whether to include with PRC based on research question
- **Default:** Report separately with notation "Hong Kong SAR (PRC since 1997)"

**Macao:**
- **Pre-1999:** Portuguese territory (separate from PRC and Taiwan)
- **Post-1999:** PRC Special Administrative Region
- **Classification:** Code as 'MO', note SAR status
- **Default:** Report separately with notation "Macao SAR (PRC since 1999)"

**Analytical Flexibility:**
- Researchers MAY aggregate HK/MO with PRC if justified by research question
- MUST explicitly state aggregation in methodology
- MUST report breakdowns separately before aggregation

---

## Implementation Requirements

### 5. Database Schema Changes

**All entity tables MUST include:**

```sql
ALTER TABLE usaspending_china_374
ADD COLUMN entity_country_of_origin TEXT CHECK (entity_country_of_origin IN ('CN', 'TW', 'HK', 'MO', 'OTHER'));

ALTER TABLE uspto_patents_chinese
ADD COLUMN assignee_country_of_origin TEXT CHECK (assignee_country_of_origin IN ('CN', 'TW', 'HK', 'MO', 'OTHER'));

ALTER TABLE ted_contractors
ADD COLUMN contractor_country_of_origin TEXT CHECK (contractor_country_of_origin IN ('CN', 'TW', 'HK', 'MO', 'OTHER'));
```

**Populate from existing data:**
- Use recipient_country_code, contractor_country, assignee_country fields
- Manual verification for ambiguous cases
- Document classification decisions

### 6. Detection Algorithm Updates

**CRITICAL: Add country code verification to ALL detection pipelines**

**Before (INCORRECT):**
```python
# BAD: Detects based on name only
if 'chinese' in entity_name.lower() or 'china' in entity_name.lower():
    is_chinese = True
```

**After (CORRECT):**
```python
# GOOD: Verifies country of origin
if country_code == 'CN':
    entity_origin = 'PRC'
elif country_code == 'TW':
    entity_origin = 'Taiwan'
elif country_code == 'HK':
    entity_origin = 'Hong Kong SAR'
elif country_code == 'MO':
    entity_origin = 'Macao SAR'
else:
    # Name-based detection as fallback only
    if 'chinese' in entity_name.lower():
        entity_origin = 'PRC (name-based, verify manually)'
```

**Verification hierarchy:**
1. **Primary:** Country code field (recipient_country_code, assignee_country, etc.)
2. **Secondary:** Legal entity registry (GLEIF, OpenCorporates)
3. **Tertiary:** Name-based patterns (MUST flag for manual verification)
4. **Manual:** High-value entities (>$10M) require analyst verification

### 7. Known Taiwan Entities (Exclusion List)

**Major Taiwan Companies (DO NOT classify as PRC):**

**Technology:**
- Hon Hai Precision Industry (Foxconn) - Taiwan
- Taiwan Semiconductor Manufacturing (TSMC) - Taiwan
- MediaTek Inc. - Taiwan
- ASUSTeK Computer - Taiwan
- Acer Inc. - Taiwan
- HTC Corporation - Taiwan
- Realtek Semiconductor - Taiwan
- Novatek Microelectronics - Taiwan

**Others:**
- Evergreen Marine - Taiwan
- Formosa Plastics - Taiwan
- Cathay Pacific (historical Taiwan ties, now HK-based)

**Research Institutions:**
- Academia Sinica - Taiwan (NOT Chinese Academy of Sciences)
- National Taiwan University - Taiwan
- National Tsing Hua University (Taiwan) - Taiwan
- Industrial Technology Research Institute (ITRI) - Taiwan

**Verification:** If entity name matches above + country code is TW → Taiwan, NOT PRC

### 8. Reporting Requirements

**ALL reports MUST include:**

**Methodology Section:**
```
GEOGRAPHIC CLASSIFICATION POLICY:

This analysis follows the Taiwan/PRC Separation Policy (v1.0):
- PRC (CN): People's Republic of China (mainland)
- Taiwan (TW): Taiwan, separate jurisdiction
- Hong Kong (HK): SAR of PRC since 1997
- Macao (MO): SAR of PRC since 1999

Taiwan entities are NOT included in PRC figures unless explicitly stated.
Hong Kong/Macao entities are reported separately with SAR notation.
```

**Data Tables:**
```
| Geographic Entity | Count | Value |
|------------------|-------|-------|
| PRC (mainland)   | XXX   | $XXX  |
| Taiwan           | XXX   | $XXX  |
| Hong Kong SAR    | XXX   | $XXX  |
| Macao SAR        | XXX   | $XXX  |
| TOTAL (all 4)    | XXX   | $XXX  |
```

**Visualizations:**
- Use separate colors/categories for PRC vs Taiwan
- Label clearly: "Taiwan (separate from PRC)"
- If aggregated, use label: "PRC + Taiwan (combined)" with breakdown in notes

---

## Specific Use Case Guidance

### 9. Research Questions That May Aggregate

**Scenarios where combining PRC + Taiwan MAY be justified:**
1. "East Asian technology landscape" (cultural/geographic region)
2. "Chinese-language research output" (linguistic analysis)
3. Historical analyses (pre-1949 or cross-strait comparisons)
4. Supply chain analyses (when both are in same chain)

**REQUIRED when aggregating:**
- Explicit statement: "This analysis combines PRC and Taiwan for [reason]"
- Separate breakdown provided in appendix
- Researcher acknowledges political sensitivity
- Note: "Taiwan and PRC are separate jurisdictions"

### 10. Research Questions Requiring Separation

**Scenarios where PRC and Taiwan MUST be separate:**
1. **National security analysis** - Different threat models
2. **Procurement policy** - Different legal frameworks
3. **Technology transfer investigations** - Different export control regimes
4. **Patent landscape** - Different patent offices (USPTO vs CNIPA vs TIPO)
5. **Geopolitical analysis** - Distinct political entities
6. **Most intelligence analyses** - Default is separate

---

## False Positive Prevention

### 11. Common Misclassification Patterns

**Pattern 1: Name-based detection without country verification**
- ❌ BAD: "DJI" in name → Chinese
- ✅ GOOD: "DJI" in name + country_code='USA' → US entity (false positive)

**Pattern 2: "Chinese" in entity name**
- ❌ BAD: "Chinese University of Hong Kong" → PRC
- ✅ GOOD: Check country code → HK (Hong Kong SAR, report separately)

**Pattern 3: Taiwan company with "China" in name**
- Example: "China Steel Corporation" → Taiwan company despite name
- ✅ CORRECT: country_code='TW' → Taiwan, NOT PRC

**Pattern 4: Headquarters vs. operations**
- Example: Foxconn (Taiwan HQ) with China operations
- ✅ CORRECT: Classify by legal headquarters (Taiwan)
- Note: Can track operations separately if needed

### 12. Validation Checklist

**Before finalizing any entity classification:**

- [ ] Country code verified from official source
- [ ] Entity not on Taiwan exclusion list
- [ ] High-value entities (>$10M) manually verified
- [ ] Ambiguous cases flagged for analyst review
- [ ] Hong Kong/Macao SAR status noted
- [ ] Classification documented in entity record

---

## Policy Enforcement

### 13. Automated Validation

**All processing scripts MUST include:**

```python
# Validation function
def validate_entity_classification(entity_name, country_code, value):
    """
    Validates entity classification against policy.
    Raises warning for policy violations.
    """
    taiwan_indicators = ['taiwan', 'taipei', 'formosa', 'roc']

    # Check 1: Taiwan name with China classification
    if any(indicator in entity_name.lower() for indicator in taiwan_indicators):
        if country_code == 'CN':
            raise ValueError(f"POLICY VIOLATION: Taiwan entity classified as CN: {entity_name}")

    # Check 2: Known Taiwan companies
    taiwan_companies = ['hon hai', 'foxconn', 'tsmc', 'mediatek', 'asus', 'acer']
    if any(company in entity_name.lower() for company in taiwan_companies):
        if country_code != 'TW':
            raise Warning(f"Verify classification: Known Taiwan company: {entity_name}")

    # Check 3: High-value entities need manual verification
    if value > 10_000_000:
        if classification_confidence != 'VERIFIED':
            raise Warning(f"Manual verification required: High-value entity: {entity_name} (${value:,.0f})")

    return True
```

### 14. Manual Review Required

**Triggers for manual verification:**
1. Entity value >$10M
2. Country code missing or ambiguous
3. Entity name contains both "Taiwan" and "China"
4. Conflicting indicators (name suggests one country, code suggests another)
5. New entity not in known company database

**Review Process:**
1. Analyst checks official corporate registry
2. Verifies with GLEIF LEI if available
3. Cross-references with OpenCorporates
4. Documents decision in entity record
5. Adds to approved/exclusion lists

### 15. Quality Assurance

**Quarterly Audit:**
- Sample 100 random entity classifications
- Verify country_of_origin accuracy
- Check for Taiwan/PRC mixing
- Review high-value entity classifications
- Update exclusion lists

**Metrics to Track:**
- Taiwan entities misclassified as PRC: Target <1%
- PRC entities misclassified as Taiwan: Target <1%
- High-value entities verified: Target 100%
- Hong Kong/Macao properly noted: Target 100%

---

## Policy Rationale

### 16. Why This Matters

**Analytical Accuracy:**
- Different legal frameworks (PRC law vs ROC law)
- Different patent systems (CNIPA vs TIPO)
- Different regulatory environments
- Different political risks

**Political Sensitivity:**
- Recognizing Taiwan's separate status
- Avoiding offense to stakeholders
- Accurate geopolitical assessment
- Professional intelligence standards

**Legal Compliance:**
- Export control regulations differ (US, EU)
- Sanctions may differ
- Procurement rules differ
- Due diligence requirements differ

**Research Integrity:**
- Factual accuracy paramount
- Transparent methodology
- Reproducible results
- Defensible conclusions

### 17. Escalation Procedures

**If classification is unclear:**
1. Flag entity for manual review
2. Consult Taiwan exclusion list
3. Check official corporate registries
4. Document uncertainty in entity record
5. If still unclear, classify as "UNKNOWN (verify manually)"

**If policy violation detected:**
1. Immediate alert to analyst
2. Halt processing if automated
3. Review classification criteria
4. Update exclusion lists if needed
5. Document correction

---

## Version History

**v1.0 (October 22, 2025):**
- Initial policy approved
- Established 4-way classification (CN, TW, HK, MO)
- Created Taiwan exclusion list
- Defined validation requirements
- Implemented country code verification mandate

**Future Revisions:**
- As new edge cases emerge
- When new major entities are identified
- Quarterly review and update
- User feedback incorporation

---

## Quick Reference Card

### For Analysts:

**When you see "Chinese" entity, ask:**
1. What's the country code? (CN, TW, HK, MO?)
2. Is it on Taiwan exclusion list?
3. If >$10M, is it manually verified?
4. Am I reporting PRC and Taiwan separately?

**Always state in reports:**
- "Taiwan entities reported separately from PRC"
- "Hong Kong SAR (PRC since 1997)"
- Geographic breakdown before any aggregation

### For Developers:

**Every detection script must:**
1. Check country_code FIRST
2. Use Taiwan exclusion list
3. Validate high-value entities
4. Add country_of_origin field
5. Never aggregate Taiwan + PRC by default

**Required fields:**
```sql
entity_country_of_origin TEXT CHECK (entity_country_of_origin IN ('CN', 'TW', 'HK', 'MO', 'OTHER'))
classification_confidence TEXT CHECK (classification_confidence IN ('VERIFIED', 'AUTOMATED', 'NEEDS_REVIEW'))
manual_verification_date DATE
```

---

## Policy Owner

**Responsible:** Project Lead
**Review Frequency:** Quarterly
**Next Review:** January 22, 2026
**Exceptions:** Require written justification and approval

---

**POLICY STATUS:** ✅ APPROVED AND EFFECTIVE IMMEDIATELY

**All existing data must be reclassified according to this policy within 30 days.**

**All new processing must comply immediately.**
