# GLEIF REPEX Data Validation Safeguards

## Overview
V5 of the GLEIF REPEX processor implements comprehensive data quality validation to ensure **no garbage data enters the database**.

## Critical Safeguards Implemented

### 1. LEI Format Validation ✓
**Purpose:** Ensure only valid Legal Entity Identifiers are stored

**Validation Rules:**
- Must be exactly 20 characters
- Must be alphanumeric only (A-Z, 0-9)
- Pattern: `^[A-Z0-9]{20}$`

**Action on Failure:**
- Record is REJECTED (not inserted)
- Logged with reason
- Counted in statistics

**Example Valid LEI:** `001GPB6A9XPE8XJICC14`
**Example Invalid:** `123` (too short), `ABC-123-456` (contains hyphens)

---

### 2. Exception Category Validation ✓
**Purpose:** Only accept known GLEIF exception categories

**Valid Categories** (from GLEIF specification):
```
- DIRECT_ACCOUNTING_CONSOLIDATION_PARENT
- ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT
- NO_LEI
- NATURAL_PERSONS
- NON_CONSOLIDATING
- BINDING_LEGAL_COMMITMENTS
```

**Action on Failure:**
- Record is REJECTED
- Unknown categories logged
- Helps detect GLEIF format changes

---

### 3. Exception Reason Validation ✓
**Purpose:** Validate reasons against known GLEIF codes

**Valid Reasons:**
```
- NON_CONSOLIDATING
- NO_KNOWN_PERSON
- NATURAL_PERSONS
- NO_LEI
- BINDING_LEGAL_COMMITMENTS
- CONSENT_NOT_OBTAINED
- DETRIMENT_NOT_EXCLUDED
- LEGAL_OBSTACLES
- DISCLOSURE_DETRIMENTAL
```

**Special Handling:**
- Allows freeform text reasons >100 chars (GLEIF permits descriptive text)
- Validates each reason in comma-separated lists
- Non-critical: Logs warning but doesn't reject record

---

### 4. Data Structure Validation ✓
**Purpose:** Detect format changes in GLEIF JSON structure

**Checks:**
- Verifies GLEIF's `{"$": "value"}` wrapper format
- Logs warnings when unexpected dict structures found
- Tracks type mismatches (e.g., receiving array when expecting string)

**Examples Caught:**
```python
Expected:  {"$": "value"}
Caught:    {"value": "xyz"}  # Missing "$" key
Caught:    "plain string"     # Missing wrapper entirely
Caught:    [array]            # Wrong type
```

---

### 5. Empty/Null Field Detection ✓
**Purpose:** Track data completeness

**Monitored Fields:**
- LEI (critical - record rejected if missing)
- ExceptionCategory (critical - record rejected if missing)
- ExceptionReason (logged, not rejected)
- ExceptionReference (logged)
- RegistrationStatus (logged)
- LastUpdateDate (logged)

**Statistics Tracked:**
```
- Missing LEI count
- Missing category count
- Empty reason count
- Unexpected structure count
```

---

### 6. Sample Data Verification ✓
**Purpose:** Early detection of systemic issues

**Implementation:**
- First 100 records logged in detail
- Sample records saved for inspection
- First 20 rejections logged with full details
- First 50 validation warnings logged

**Catches:**
- Batch-level format changes
- Systematic data quality issues
- Encoding problems

---

### 7. Comprehensive Statistics ✓
**Purpose:** Audit trail and quality metrics

**Metrics Collected:**
```
Total Records Processed:     X
Valid Records Inserted:      X (Y%)
Rejected Records:            X

Validation Issues:
  - Invalid LEI format:      X
  - Missing LEI:             X
  - Missing category:        X
  - Unknown category:        X
  - Unknown reason:          X
  - Empty reason:            X
  - Unexpected structure:    X

Top Categories (frequency)
Top Reasons (frequency)
```

---

### 8. Record Rejection Policy ✓
**Purpose:** Maintain database integrity

**Rejection Criteria:**
A record is REJECTED if:
- LEI is missing OR invalid format
- ExceptionCategory is missing OR unknown

**Rationale:**
- LEI is the primary key - must be valid
- Category is core business data - must be recognized
- Other fields can be empty/unknown (logged for review)

---

### 9. Error Handling ✓
**Purpose:** Fail safely, not silently

**Safety Limits:**
- Max 1,000 rejections before halting (prevents processing garbage data)
- All errors logged with full exception traces
- Database transaction rollback on critical errors

**Prevents:**
- Silent data corruption
- Processing completely invalid files
- Database left in inconsistent state

---

### 10. Audit Logging ✓
**Purpose:** Full traceability

**What's Logged:**
- Every validation warning (first N occurrences)
- Every rejected record (first 20)
- Every unexpected data structure
- Complete statistics summary
- Sample records for manual review

**Log Locations:**
- `gleif_repex_v5_processing.log` - All events
- Console output - Progress and summary

---

## Comparison: V4 vs V5

| Feature | V4 (Basic) | V5 (Validated) |
|---------|-----------|----------------|
| LEI Validation | ❌ None | ✅ Format check |
| Category Validation | ❌ None | ✅ Whitelist check |
| Reason Validation | ❌ None | ✅ Known codes |
| Structure Validation | ❌ None | ✅ Full checks |
| Record Rejection | ❌ None | ✅ Invalid records rejected |
| Statistics | ❌ Basic count | ✅ Comprehensive metrics |
| Sample Verification | ❌ None | ✅ First 100 logged |
| Audit Trail | ❌ Minimal | ✅ Complete |

---

## Recommended Usage

**For Production:** Use V5 (validated)
- First run: Review logs and statistics
- Verify rejection count is reasonable (<1% of total)
- Check sample records match expectations
- Review unknown categories/reasons

**For Emergency:** Use V4 (fast)
- When V5 validation is too strict
- When speed is critical
- When you trust the data source completely

---

## Post-Processing Verification

After running V5, verify:
```sql
-- Check record count is reasonable
SELECT COUNT(*) FROM gleif_repex;

-- Verify LEI format
SELECT COUNT(*) FROM gleif_repex
WHERE length(lei) != 20;  -- Should be 0

-- Check category distribution
SELECT exception_category, COUNT(*)
FROM gleif_repex
GROUP BY exception_category
ORDER BY COUNT(*) DESC;

-- Look for unexpected values
SELECT DISTINCT exception_category
FROM gleif_repex
WHERE exception_category NOT IN (
  'DIRECT_ACCOUNTING_CONSOLIDATION_PARENT',
  'ULTIMATE_ACCOUNTING_CONSOLIDATION_PARENT',
  'NO_LEI', 'NATURAL_PERSONS', 'NON_CONSOLIDATING',
  'BINDING_LEGAL_COMMITMENTS'
);
```

---

## What Could Still Go Wrong?

**Edge Cases Not Fully Covered:**
1. **LEI checksum validation** - We validate format but not the check digit
2. **Date format validation** - Accepts any string in LastUpdateDate
3. **Character encoding issues** - Assumes UTF-8, could have mojibake
4. **Duplicate LEIs** - INSERT OR REPLACE keeps latest, older data lost

**Mitigation:**
- GLEIF data is highly standardized (reduces risk)
- Statistics will show anomalies
- Periodic manual spot checks recommended

---

## Emergency Rollback

If V5 rejects too many records:

1. Check rejection reasons in log
2. If rejections are false positives:
   - Adjust validation rules
   - Add new categories/reasons to whitelist
3. If rejections are valid:
   - Report to GLEIF data quality team
   - Use rejected records for separate analysis

**Rollback command:**
```bash
# Restore from V4 data (if needed)
python scripts/process_gleif_repex_v4_ROBUST.py
```
