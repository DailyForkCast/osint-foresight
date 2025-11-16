# Option A: Rebuild TED Entity Table with Validation & Null Protocols
**Date:** October 20, 2025
**Strategy:** Complete rebuild with quality controls from day one
**Status:** Planning Phase

---

## Executive Summary

We will completely rebuild the `ted_procurement_chinese_entities_found` table using:
1. **Proper Chinese entity detection** (Chinese characters, country codes, company patterns)
2. **Multi-stage validation framework** (European exclusions, confidence scoring)
3. **Null protocols** (comprehensive null handling to prevent data loss)
4. **Quality gates** (70% source precision, 90% match precision)

---

## Phase 1: Clear Contaminated Data

### Step 1.1: Backup Current State
```sql
-- Create backup of contaminated table for forensics
CREATE TABLE ted_procurement_chinese_entities_found_CONTAMINATED_20251020
AS SELECT * FROM ted_procurement_chinese_entities_found;
```

### Step 1.2: Clear Entity Table
```sql
-- Remove all contaminated entities
DELETE FROM ted_procurement_chinese_entities_found;

-- Verify empty
SELECT COUNT(*) FROM ted_procurement_chinese_entities_found;
-- Expected: 0
```

### Step 1.3: Reset is_chinese_related Flags
```sql
-- Clear all flags to baseline state
UPDATE ted_contracts_production
SET is_chinese_related = 0
WHERE is_chinese_related = 1;

-- Keep the original 295 that were manually verified
-- (We'll need to restore these if they're legitimate)
```

**Deliverables:**
- ✅ Contaminated table backed up
- ✅ Entity table cleared (0 rows)
- ✅ Contract flags reset to clean state

---

## Phase 2: Implement Chinese Entity Detection with Null Protocols

### Detection Criteria (Multi-Factor Scoring)

**Primary Indicators (High Confidence):**
1. **Chinese Characters Present** (+35 points)
   - Unicode range: \u4e00-\u9fff
   - Null protocol: Check for NULL before regex

2. **Chinese Country Code** (+40 points)
   - Valid codes: CN, CHN, HK, HKG, MO, MAC
   - Null protocol: If NULL, check alternative country fields

3. **Chinese Address** (+20 points)
   - Contains Chinese characters
   - Contains Chinese city names (Beijing, Shanghai, etc.)
   - Null protocol: Check contractor_address, winner_address, all address fields

**Secondary Indicators (Moderate Confidence):**
4. **Chinese Company Suffix** (+15 points)
   - "Co., Ltd.", "Limited", "有限公司", "股份有限公司"
   - Null protocol: Check for NULL before pattern matching

5. **Chinese Name Patterns** (+10 points)
   - "China", "Chinese", "Huawei", "ZTE", etc.
   - Null protocol: Case-insensitive, handle NULL

**Exclusions (Automatic Rejection):**
6. **European Legal Suffixes** (-100 points, instant rejection)
   - GmbH, S.L., s.r.o., SpA, B.V., etc.
   - Null protocol: N/A (presence-based)

7. **Non-Chinese Country Code** (-30 points)
   - Any valid ISO code that's not Chinese
   - Null protocol: Only penalize if code is present and confirmed non-Chinese

**Confidence Threshold:**
- Minimum 70 points required to flag as Chinese entity
- Must have either Chinese characters OR Chinese country code

---

## Phase 3: Create Detection Script with Null Protocols

### Script: `rebuild_ted_chinese_entities.py`

**Key Features:**
1. **Null Protocol Integration**
   - Check ALL relevant fields before assuming NULL means "no data"
   - contractor_name, winner_name, operator_name
   - contractor_country, winner_country, iso_country_code
   - contractor_address, winner_address, performance_country
   - contractor_nuts, winner_nuts

2. **Multi-Field Aggregation**
   - Aggregate data from all contractor/winner/operator fields
   - Score based on combined evidence
   - Never miss a Chinese entity due to NULL in one field

3. **Validation Framework**
   - Use `TEDEntityValidator` class
   - European suffix detection
   - Confidence scoring (0-100 scale)
   - Country code validation

4. **Incremental Processing**
   - Process contracts in batches (10,000 at a time)
   - Checkpoint every batch
   - Resume capability if interrupted

5. **Quality Metrics**
   - Track precision at each batch
   - Alert if precision drops below 70%
   - Generate detailed quality reports

---

## Phase 4: Null Protocol Implementation Details

### Contractor Name Null Protocol
```python
def get_contractor_name_with_null_protocol(row):
    """
    Get contractor name with null protocol - check all fields.
    """
    # Primary field
    if row['contractor_name'] and row['contractor_name'].strip():
        return row['contractor_name'].strip()

    # Fallback to winner_name
    if row['winner_name'] and row['winner_name'].strip():
        return row['winner_name'].strip()

    # Fallback to operator_name
    if row['operator_name'] and row['operator_name'].strip():
        return row['operator_name'].strip()

    # No valid name found
    return None
```

### Country Code Null Protocol
```python
def get_country_code_with_null_protocol(row):
    """
    Get country code with null protocol - check all country fields.
    """
    # Try contractor_country
    if row['contractor_country'] and len(row['contractor_country'].strip()) == 2:
        return row['contractor_country'].strip().upper()

    # Try winner_country
    if row['winner_country'] and len(row['winner_country'].strip()) == 2:
        return row['winner_country'].strip().upper()

    # Try iso_country_code
    if row['iso_country_code'] and len(row['iso_country_code'].strip()) == 2:
        return row['iso_country_code'].strip().upper()

    # Try performance_country
    if row['performance_country'] and len(row['performance_country'].strip()) == 2:
        return row['performance_country'].strip().upper()

    # Extract from NUTS code (first 2 chars)
    if row['contractor_nuts'] and len(row['contractor_nuts']) >= 2:
        return row['contractor_nuts'][:2].upper()

    if row['winner_nuts'] and len(row['winner_nuts']) >= 2:
        return row['winner_nuts'][:2].upper()

    # No valid country code found
    return None
```

### Address Null Protocol
```python
def get_address_with_null_protocol(row):
    """
    Get address with null protocol - check all address fields.
    """
    # Try contractor_address
    if row['contractor_address'] and row['contractor_address'].strip():
        return row['contractor_address'].strip()

    # Try winner_address
    if row['winner_address'] and row['winner_address'].strip():
        return row['winner_address'].strip()

    # Combine available location data
    location_parts = []
    if row['contractor_town']:
        location_parts.append(row['contractor_town'])
    if row['contractor_postal_code']:
        location_parts.append(row['contractor_postal_code'])
    if row['performance_country']:
        location_parts.append(row['performance_country'])

    if location_parts:
        return ', '.join(location_parts)

    # No valid address found
    return None
```

---

## Phase 5: Processing Algorithm

### High-Level Flow

```
1. For each contract in ted_contracts_production:

   2. Apply Null Protocol to extract contractor data:
      - name = get_contractor_name_with_null_protocol(contract)
      - country = get_country_code_with_null_protocol(contract)
      - address = get_address_with_null_protocol(contract)

   3. If name is NULL, skip (no entity to detect)

   4. Apply Chinese Entity Detection:
      - confidence, indicators = calculate_chinese_confidence(name, country, address)

   5. Apply Validation Framework:
      - is_valid = validate_entity(name, country, address, min_confidence=70.0)

   6. If is_valid:
      - Add to ted_procurement_chinese_entities_found
      - Increment contracts_count for this entity
      - Update first_seen, last_seen
      - Track countries_active

   7. Batch checkpoint every 10,000 contracts

   8. Generate quality metrics every 50,000 contracts
```

### Quality Gates During Processing

**Gate 1: Source Precision** (every 50,000 contracts)
- Sample 100 random entities added so far
- Validate with full framework
- Required precision: ≥ 70%
- If below threshold: ALERT and pause for review

**Gate 2: European Contamination** (every 50,000 contracts)
- Check for European legal suffixes in new entities
- Maximum allowed: 5%
- If above threshold: ALERT and investigate detection logic

**Gate 3: Null Handling** (every 50,000 contracts)
- Track NULL field statistics
- Ensure null protocols are capturing data
- Alert if >20% of entities have all-NULL fields

---

## Phase 6: Entity Table Schema Updates

### Add Quality Tracking Columns

```sql
ALTER TABLE ted_procurement_chinese_entities_found
ADD COLUMN detection_confidence REAL;

ALTER TABLE ted_procurement_chinese_entities_found
ADD COLUMN has_chinese_characters INTEGER;

ALTER TABLE ted_procurement_chinese_entities_found
ADD COLUMN validated_country_code TEXT;

ALTER TABLE ted_procurement_chinese_entities_found
ADD COLUMN detection_method TEXT;  -- 'chinese_chars', 'country_code', 'both'

ALTER TABLE ted_procurement_chinese_entities_found
ADD COLUMN null_fields_used TEXT;  -- JSON list of fields that were NULL but recovered
```

---

## Phase 7: Validation & Quality Assurance

### Post-Processing Validation

1. **Sample 1,000 random entities** from rebuilt table
2. **Manual review** by domain expert
3. **Calculate precision** (true positives / total)
4. **Target:** ≥ 90% precision

### Quality Metrics to Track

```
- Total entities detected: X
- With Chinese characters: X (%)
- With Chinese country code: X (%)
- With both: X (%)
- Average confidence score: XX.X
- European entities (should be 0): 0
- Null fields recovered: X instances
- Contracts flagged: X (compared to 295 baseline)
```

---

## Phase 8: Sync to Production

### Only After Validation Passes

1. Run improved sync script with quality gates:
   ```bash
   python ted_improved_sync_with_validation.py
   ```

2. Quality Gate 1 should pass (≥70% source precision)
3. Quality Gate 2 should pass (≥90% match precision)
4. Flag contracts in `ted_contracts_production`

---

## Phase 9: Continuous Monitoring

### Automated Quality Checks (Weekly)

1. **Sample validation** (100 random entities)
2. **Precision tracking** (trend over time)
3. **European contamination check** (should remain 0%)
4. **Null protocol effectiveness** (% of data recovered)

---

## Implementation Timeline

| Phase | Task | Duration | Dependencies |
|-------|------|----------|--------------|
| 1 | Clear contaminated data | 1 hour | Backup created |
| 2 | Design detection criteria | 2 hours | Requirements clear |
| 3 | Implement detection script | 4 hours | Validation framework ready |
| 4 | Implement null protocols | 3 hours | Schema understood |
| 5 | Process TED contracts | 6-8 hours | Detection script tested |
| 6 | Update entity schema | 1 hour | Processing complete |
| 7 | Validation & QA | 3 hours | Domain expert available |
| 8 | Sync to production | 1 hour | Validation passed |
| 9 | Setup monitoring | 2 hours | Production sync complete |

**Total Estimated Time:** 23-25 hours (3-4 working days)

---

## Success Criteria

✅ **Entity Table Quality**
- Precision ≥ 90%
- European contamination = 0%
- Confidence scores averaged ≥ 75

✅ **Null Protocol Effectiveness**
- ≥ 95% of contracts with Chinese entities captured
- Null fields recovered in ≥ 30% of detections

✅ **Quality Gates**
- Quality Gate 1 passes (≥70% source precision)
- Quality Gate 2 passes (≥90% match precision)

✅ **Production Sync**
- Contracts flagged: reasonable number (estimate 1,000-5,000)
- False positive rate: <10%
- Database integrity: maintained

---

## Risk Mitigation

**Risk 1: Processing Time**
- Mitigation: Batch processing with checkpoints
- Fallback: Process in parallel by year/country

**Risk 2: Quality Below Threshold**
- Mitigation: Quality gates will catch issues early
- Fallback: Adjust confidence thresholds, add more validation

**Risk 3: Null Protocols Miss Data**
- Mitigation: Comprehensive field checking
- Fallback: Add more fields to null protocol chain

**Risk 4: European Contamination Recurs**
- Mitigation: European suffix exclusion built into validation
- Fallback: Add more European suffixes to exclusion list

---

## Next Steps

1. ✅ Create backup of contaminated table
2. ✅ Clear entity table
3. ⏳ Implement detection script with null protocols
4. ⏳ Test on 10,000 contract sample
5. ⏳ Run full processing on all contracts
6. ⏳ Validate results
7. ⏳ Sync to production with quality gates

---

**Approval Required to Proceed**
**Date:** October 20, 2025
**Approved by:** [Pending]
