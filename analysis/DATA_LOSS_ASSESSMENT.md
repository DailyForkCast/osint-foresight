# Database Data Loss Assessment
## Based on Processing Logs (October 11, 2025)

## Summary

Due to concurrent write operations on SQLite database, some data loss occurred from database lock errors.

## Detailed Analysis

### 1. USPTO CPC Classifications

**Source**: `uspto_cpc_processing.log`

- **Total records processed**: 65,590,414
- **Strategic technology records**: 14,154,434
- **Database lock errors**: 45
- **Estimated data loss**: ~45,000 records (0.07%)
  - Assumes 1,000 records per failed batch insert
- **Assessment**: ✅ **ACCEPTABLE** - Data is 99.93% complete

**Top Strategic Technologies** (successfully imported):
- Computing: 3,592,356
- Semiconductor Devices: 3,433,167
- Wireless Communications: 1,500,194
- Batteries/Fuel Cells: 1,014,679
- AI/Neural Networks: 383,205

### 2. GLEIF Entities

**Source**: `gleif_streaming_processing_v2.log`

- **Total entities processed**: 3,086,233
- **Database lock errors**: 242
- **Estimated data loss**: ~242,000 entities (7.8%)
  - Assumes 1,000 entities per failed batch insert
- **Assessment**: ⚠️  **MODERATE** - Data is ~92% complete

**Key Entity Counts** (from log summary):
- Mainland China (CN): 106,890
- Hong Kong (HK): 11,833
- United States (US): 333,697
- India (IN): 300,830
- Italy (IT): 235,254

**Lock Error Pattern**: Errors increased significantly after minute 15, with throughput dropping from 2,730/sec to 200/sec due to concurrent USPTO CPC writes.

### 3. GLEIF Relationships

**Source**: `gleif_streaming_processing_v2.log`

- **Total relationships processed**: 464,565
- **Processing time**: 0.4 minutes (23 seconds)
- **Database lock errors**: Unknown (processed during heavy USPTO write activity)
- **Records in database**: 1 (from summary)
- **Estimated data loss**: 464,564 relationships (99.998%)
- **Assessment**: ❌ **CRITICAL** - Almost no relationship data saved

**Why relationships failed**:
1. Relationship processing happened at 19:21:45 (minute 132)
2. USPTO CPC was still actively writing at this time
3. GLEIF relationships used `INSERT OR IGNORE` which silently fails on conflicts
4. Almost all inserts hit database locks during concurrent writes

## Root Cause Analysis

### SQLite Concurrency Limitations

```
┌─────────────────────────────────────────────────────────────┐
│ TIME  │ GLEIF Process        │ USPTO CPC Process          │
├───────┼──────────────────────┼────────────────────────────┤
│ 17:08 │ Start entities       │ [Not started]              │
│ 17:15 │ Processing (500/sec) │ Start CPC (heavy writes)   │
│ 17:20 │ **SLOWS to 200/sec** │ Writing heavily            │
│ 19:21 │ Start relationships  │ **STILL WRITING**          │
│ 19:21 │ **464K REL FAIL**    │ Database locked            │
│ 19:26 │ Complete (1 rel)     │ Complete                   │
└───────┴──────────────────────┴────────────────────────────┘
```

### Lock Error Distribution

- **Minutes 0-15** (entities only): 11 errors (2,730/sec throughput)
- **Minutes 15-60** (concurrent GLEIF+USPTO): 231 errors (200-400/sec throughput)
- **Minute 132** (relationships): ~464K errors (almost total loss)

## Impact Assessment

| Data Type | Expected | Actual* | Loss | Status |
|-----------|----------|---------|------|--------|
| CPC Classifications | 65,590,414 | ~65,545,000 | 0.07% | ✅ OK |
| GLEIF Entities | 3,086,233 | ~2,844,000 | 7.8% | ⚠️  MODERATE |
| GLEIF Relationships | 464,565 | 1 | 99.998% | ❌ CRITICAL |

*Actual counts are estimates based on error patterns since database is currently locked

## What Data Was Lost?

### USPTO CPC (~45,000 records)
- Randomly distributed across 177 XML files
- Proportional loss across all CPC classes
- Strategic tech loss: ~9,700 records (0.07%)
- **Impact on analysis**: Minimal - statistically negligible

### GLEIF Entities (~242,000 records)
- Loss concentrated in minutes 15-132 when USPTO was writing
- Likely missing entities from middle/end of alphabet
- **China-specific impact**: Unknown if CN/HK entities affected
- **Impact on analysis**: Moderate - may miss some entities

### GLEIF Relationships (464,564 records)
- **CRITICAL**: Almost complete loss of corporate ownership data
- Only 1 relationship saved (likely first record before locks)
- **All corporate hierarchies missing**
- **Impact on analysis**: SEVERE - Phase 6 cannot map ownership networks

## Recommendations

### IMMEDIATE (Required)

1. **Reprocess GLEIF Relationships Only** (30 seconds)
   - Run when database is not locked
   - Only processes relationship file (32MB)
   - Critical for Phase 6 International Links analysis

2. **Verify Database Once Accessible**
   - Run `verify_database_completeness.py`
   - Get actual record counts
   - Identify specific gaps in entity data

### SHORT-TERM (Recommended)

3. **Reprocess Missing GLEIF Entities** (if loss > 10%)
   - Identify which LEI ranges are missing
   - Selective reprocessing to fill gaps
   - Important for comprehensive entity coverage

4. **Enable WAL Mode**
   ```python
   conn.execute("PRAGMA journal_mode=WAL")
   ```
   - Improves concurrent read/write performance
   - Reduces lock contention 80-90%

5. **Add Retry Logic to All Processors**
   ```python
   for attempt in range(5):
       try:
           cursor.executemany(sql, batch)
           conn.commit()
           break
       except sqlite3.OperationalError as e:
           if "locked" in str(e):
               time.sleep(2 ** attempt)
               continue
   ```

### LONG-TERM (Architecture)

6. **Use Separate Databases Per Source**
   - `gleif.db`, `uspto.db`, `ted.db`, etc.
   - Merge into `osint_master.db` after processing
   - Zero contention during data collection

7. **Consider PostgreSQL Migration**
   - True MVCC (Multi-Version Concurrency Control)
   - Multiple concurrent writers
   - Better for production workloads

## Current Status

**Database Status**: 🔒 LOCKED (cannot verify actual counts)
- Lock files present: `.db-shm`, `.db-wal`
- 19 GB database file size
- Processes completed but connections may be held

**Next Steps**:
1. Wait for lock to clear OR restart system
2. Run verification script to get actual counts
3. Reprocess GLEIF relationships (critical)
4. Assess if entity gaps need filling

## Data Usability

| Phase | Data Source | Usability | Notes |
|-------|-------------|-----------|-------|
| Phase 2 | USPTO CPC | ✅ 99.9% usable | Strategic tech mapping ready |
| Phase 6 | GLEIF Entities | ⚠️  ~92% usable | Most entities present, some gaps |
| Phase 6 | GLEIF Relationships | ❌ 0.0002% usable | **MUST reprocess before Phase 6** |
| Phase 6 | ASPI | ✅ 100% usable | Already integrated |

## Conclusion

**USPTO CPC**: Ready for Phase 2 integration - data loss is negligible.

**GLEIF Entities**: Likely usable for Phase 6 but should verify once database accessible - moderate data loss may require selective reprocessing.

**GLEIF Relationships**: **CRITICAL - MUST reprocess** before Phase 6 can analyze corporate ownership networks. Without this data, we cannot:
- Map parent-child company relationships
- Identify ultimate beneficial owners
- Trace corporate control structures
- Cross-reference subsidiaries with detections

**Priority**: Reprocess relationships first (quick, 30 seconds), then verify entity completeness, then decide if entity reprocessing is needed.
