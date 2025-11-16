# TED Database Insert Error Analysis

## Error
```
ERROR:__main__:Database insert error: Error binding parameter 26 - probably unsupported type.
```

## Root Cause

The error is in `ted_complete_production_processor.py` in the `validate_china_involvement()` method.

### Bug Location: Line 191

```python
# CHINESE_CONFIRMED path
return {
    'is_chinese_related': True,
    'chinese_confidence': 1.0,
    'chinese_indicators': quality_assessment.positive_signals,  # BUG: Not JSON encoded!
    'chinese_entities': json.dumps([contract.get('contractor_name', 'Unknown')]),
    'data_quality_flag': quality_assessment.data_quality_flag,
    'fields_with_data_count': quality_assessment.fields_with_data_count,
    'negative_signals': json.dumps(quality_assessment.negative_signals),  # Correctly encoded
    'positive_signals': json.dumps(quality_assessment.positive_signals),  # Correctly encoded
    'detection_rationale': quality_assessment.rationale
}
```

### Problem

`chinese_indicators` is being set to `quality_assessment.positive_signals` which is a **Python list**, not a JSON string.

SQLite cannot store Python list objects directly - they must be JSON-encoded strings.

### Comparison

- Line 191: `'chinese_indicators': quality_assessment.positive_signals` ❌ (Python list)
- Line 195: `'negative_signals': json.dumps(quality_assessment.negative_signals)` ✅ (JSON string)
- Line 247: `'chinese_indicators': json.dumps(matches)` ✅ (JSON string in pattern match path)

### Why It's Intermittent

The error only occurs when:
1. A contract is detected as `CHINESE_CONFIRMED` by the Data Quality Assessor
2. The `positive_signals` field contains data (not empty)
3. The insert tries to bind the Python list to the SQL parameter

Most contracts go through the pattern matching path (line 247) which correctly JSON-encodes, so only a subset hit this bug.

## Fix

Change line 191 from:
```python
'chinese_indicators': quality_assessment.positive_signals,
```

To:
```python
'chinese_indicators': json.dumps(quality_assessment.positive_signals) if quality_assessment.positive_signals else None,
```

## Estimated Impact

- Total errors so far: 8 (as of line 541 in logs)
- Total Chinese contracts found: 25
- Error rate: ~32% of Chinese detections hitting the bug
- **Data loss**: 8 Chinese contracts NOT saved to database due to this bug

## Priority

**HIGH** - We're losing Chinese contract data. Should fix and re-process affected records.
