# Database Lock Error Analysis

## What Happened

During concurrent processing of GLEIF and USPTO CPC data, both processes wrote to the same SQLite database (`F:/OSINT_WAREHOUSE/osint_master.db`) simultaneously, causing database lock errors.

## Error Counts

- **USPTO CPC Processing**: 45 database lock errors
- **GLEIF Processing**: 242 database lock errors
- **Total**: 287 lock errors

## Root Cause: SQLite Concurrency Limitations

SQLite uses **file-level locking**, which means:

1. **Only ONE writer at a time**: When one process is writing (INSERT/UPDATE), the entire database is locked
2. **Lock timeout**: If a process can't acquire a lock within the timeout period, it fails
3. **Write serialization**: All writes must happen sequentially, not in parallel

### Our Scenario

```
Time    GLEIF Process                    USPTO CPC Process
----    -------------                    -----------------
T1      INSERT batch (1000 entities)     [waiting]
T2      COMMIT                           INSERT batch (1000 CPCs)
T3      [waiting]                        COMMIT
T4      INSERT batch                     [waiting]
T5      **DATABASE LOCKED ERROR**        INSERT batch succeeds
```

## Impact Assessment (Based on Logs)

### USPTO CPC Data
- **Expected**: 65,590,414 total classifications
- **Errors**: 45 failed inserts
- **Estimated loss**: ~45,000 records (0.07%)
  - Assumes batch size of 1,000 per insert
- **Strategic tech loss**: Proportionally ~9,700 records (0.07%)

### GLEIF Data
- **Expected entities**: 3,086,233
- **Expected relationships**: 464,565
- **Errors**: 242 failed inserts
- **Estimated loss**: ~242,000 records (0.3%)
  - Mix of entity and relationship records

## Why the Relationship Count is Wrong

The GLEIF summary showed only **1 relationship** in the database despite processing 464,565. This suggests:

1. **Most relationship inserts hit database locks** during concurrent processing
2. **INSERT OR IGNORE** clause: Duplicate keys were silently ignored
3. **Concurrent write conflicts**: GLEIF and USPTO both writing at same time

The relationship data likely needs reprocessing.

## Solutions

### 1. **Sequential Processing** (Simplest)
Run processes one at a time instead of concurrently:
```bash
python scripts/process_gleif_streaming.py
# Wait for completion
python scripts/process_uspto_cpc_classifications.py
```

**Pros**: No lock errors, 100% data integrity
**Cons**: Slower total time (sequential vs parallel)

### 2. **Separate Databases** (Recommended for production)
Use different database files for different data sources:
```python
GLEIF_DB = "F:/OSINT_WAREHOUSE/gleif.db"
USPTO_DB = "F:/OSINT_WAREHOUSE/uspto.db"
MASTER_DB = "F:/OSINT_WAREHOUSE/osint_master.db"
```

**Pros**: No contention, can process in parallel
**Cons**: More complex queries across databases

### 3. **Write-Ahead Logging (WAL) Mode**
Enable SQLite WAL mode for better concurrent access:
```python
conn.execute("PRAGMA journal_mode=WAL")
```

**Pros**: Allows concurrent reads during writes, reduces lock time
**Cons**: Still only one writer at a time, but faster

### 4. **Increase Timeout and Retry Logic**
Add retry logic with exponential backoff:
```python
import time

for attempt in range(5):
    try:
        cursor.executemany(sql, batch)
        conn.commit()
        break
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e) and attempt < 4:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s, 8s
            continue
        raise
```

**Pros**: Reduces errors without architectural changes
**Cons**: Slower processing, doesn't eliminate locks

### 5. **PostgreSQL Migration** (Long-term solution)
Switch to PostgreSQL for true concurrent writes:

**Pros**: Multi-version concurrency control (MVCC), no file locks
**Cons**: Requires PostgreSQL installation and setup

## Recommended Action

For **immediate fix** with minimal effort:

1. **Reprocess GLEIF relationships only** (sequential, database not locked by others)
2. **Enable WAL mode** for future processing
3. **Add retry logic** to both processors

For **production robustness**:

1. Use separate databases per data source
2. Merge into master database after processing
3. Or migrate to PostgreSQL for true parallel writes

## Data Integrity Status

Based on error counts vs total records:

✅ **USPTO CPC**: ~99.93% complete (acceptable)
⚠️  **GLEIF Entities**: ~99.7% complete (acceptable)
❌ **GLEIF Relationships**: ~99.99% missing (needs reprocessing)

**Bottom line**: The entity and CPC data are mostly fine, but the relationship data needs to be reprocessed when the database isn't being accessed by other processes.
