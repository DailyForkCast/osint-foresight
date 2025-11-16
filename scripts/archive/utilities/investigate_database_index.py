#!/usr/bin/env python3
"""
Investigate Database Index Issues
Diagnose why database queries are taking 3+ hours instead of ~22 seconds
"""

import sqlite3
import time
from pathlib import Path

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

print("="*80)
print("DATABASE INDEX INVESTIGATION")
print("="*80)
print(f"Database: {DB_PATH}")
print()

# Check database file size
db_size = Path(DB_PATH).stat().st_size / (1024**3)
print(f"Database size: {db_size:.2f} GB")

# Check for WAL/SHM files
wal_path = Path(str(DB_PATH) + "-wal")
shm_path = Path(str(DB_PATH) + "-shm")
if wal_path.exists():
    wal_size = wal_path.stat().st_size / (1024**2)
    print(f"WAL file: {wal_size:.2f} MB")
if shm_path.exists():
    shm_size = shm_path.stat().st_size / (1024**2)
    print(f"SHM file: {shm_size:.2f} MB")

print()
print("-"*80)
print("PHASE 1: Database Integrity Check")
print("-"*80)

conn = sqlite3.connect(DB_PATH, timeout=300)
cursor = conn.cursor()

print("Running PRAGMA integrity_check...")
start = time.time()
cursor.execute("PRAGMA integrity_check")
result = cursor.fetchone()
elapsed = time.time() - start
print(f"Result: {result[0]}")
print(f"Time: {elapsed:.2f} seconds")
print()

print("-"*80)
print("PHASE 2: Index Status")
print("-"*80)

print("Listing all indexes on gdelt_gkg table...")
cursor.execute("""
    SELECT name, sql FROM sqlite_master
    WHERE type='index' AND tbl_name='gdelt_gkg'
    ORDER BY name
""")
indexes = cursor.fetchall()

for idx_name, idx_sql in indexes:
    print(f"\nIndex: {idx_name}")
    if idx_sql:
        print(f"  SQL: {idx_sql}")
    else:
        print(f"  (auto-created primary key)")

print()
print("-"*80)
print("PHASE 3: Index Analysis")
print("-"*80)

for idx_name, _ in indexes:
    print(f"\nAnalyzing index: {idx_name}")
    start = time.time()
    cursor.execute(f"ANALYZE {idx_name}")
    conn.commit()
    elapsed = time.time() - start
    print(f"  Analysis time: {elapsed:.2f} seconds")

print()
print("-"*80)
print("PHASE 4: Query Performance Test")
print("-"*80)

# Test the problematic query
print("\nTesting date prefix query (the slow one)...")
query = "SELECT DISTINCT SUBSTR(CAST(publish_date AS TEXT), 1, 8) FROM gdelt_gkg"

print(f"Query: {query}")
print("Running...")
start = time.time()
cursor.execute(query)
results = cursor.fetchall()
elapsed = time.time() - start

print(f"Results: {len(results)} unique dates")
print(f"Time: {elapsed:.2f} seconds")
print()

# Check if query used the index
print("Checking query plan (EXPLAIN QUERY PLAN)...")
cursor.execute(f"EXPLAIN QUERY PLAN {query}")
plan = cursor.fetchall()
for row in plan:
    print(f"  {row}")
print()

print("-"*80)
print("PHASE 5: Index Statistics")
print("-"*80)

# Get index stats
cursor.execute("""
    SELECT name, idx FROM sqlite_stat1
    WHERE tbl = 'gdelt_gkg'
""")
stats = cursor.fetchall()

if stats:
    print("\nIndex statistics (sqlite_stat1):")
    for name, idx_stats in stats:
        print(f"  {name}: {idx_stats}")
else:
    print("\nNo statistics found - indexes may not be analyzed!")
    print("Recommendation: Run ANALYZE command")

print()
print("-"*80)
print("PHASE 6: Table Statistics")
print("-"*80)

# Total records
print("\nCounting total records...")
start = time.time()
cursor.execute("SELECT COUNT(*) FROM gdelt_gkg")
total = cursor.fetchone()[0]
elapsed = time.time() - start
print(f"Total records: {total:,}")
print(f"Time: {elapsed:.2f} seconds")

# Count unique dates (using index)
print("\nCounting unique dates...")
start = time.time()
cursor.execute("SELECT COUNT(DISTINCT SUBSTR(CAST(publish_date AS TEXT), 1, 8)) FROM gdelt_gkg")
unique_dates = cursor.fetchone()[0]
elapsed = time.time() - start
print(f"Unique dates: {unique_dates:,}")
print(f"Time: {elapsed:.2f} seconds")

conn.close()

print()
print("="*80)
print("INVESTIGATION COMPLETE")
print("="*80)
print()
print("Summary:")
print(f"  Database: {db_size:.2f} GB")
print(f"  Records: {total:,}")
print(f"  Unique dates: {unique_dates:,}")
print(f"  Indexes: {len(indexes)}")
print()
print("If query time was > 30 seconds, index may need rebuilding.")
print("Check query plan to see if index was used.")
