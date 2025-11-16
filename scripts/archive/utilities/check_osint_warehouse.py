import sqlite3
from pathlib import Path

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

if not Path(db_path).exists():
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Connecting to {db_path}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
print(f"\nAvailable tables ({len(tables)}):")
for table in tables:
    print(f"  - {table}")

# Check for quantum-related data
print("\n" + "="*80)
print("Checking for quantum research data...")
print("="*80)

# Try different possible table structures
for table in tables[:10]:  # Check first 10 tables
    try:
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        cols = [description[0] for description in cursor.description]
        print(f"\n{table}: {len(cols)} columns")
        print(f"  Columns: {', '.join(cols[:10])}")

        # Check if has title/abstract for quantum search
        if 'title' in cols or 'abstract' in cols:
            print(f"  -> Has text fields, checking for quantum research...")

            where_clauses = []
            if 'title' in cols:
                where_clauses.append("title LIKE '%quantum%'")
            if 'abstract' in cols:
                where_clauses.append("abstract LIKE '%quantum%'")

            query = f"SELECT COUNT(*) FROM {table} WHERE {' OR '.join(where_clauses)}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"  -> Quantum records: {count:,}")

    except Exception as e:
        print(f"\n{table}: Error - {e}")

conn.close()
