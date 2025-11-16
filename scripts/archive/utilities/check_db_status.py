#!/usr/bin/env python3
import sqlite3
from pathlib import Path

def check_database_status():
    db_dir = Path("F:/OSINT_WAREHOUSE")

    databases = {
        'google_patents_china.db': 'patent_searches',
        'leonardo_scoring.db': 'technology_assessments',
        'master_intelligence.db': 'intelligence_fusion',
        'predictive_indicators.db': 'indicator_measurements',
        'rss_intelligence.db': 'feed_items',
        'entity_graph.db': 'entities'
    }

    print("DATABASE STATUS REPORT")
    print("=" * 50)

    for db_file, table in databases.items():
        db_path = db_dir / db_file
        if db_path.exists():
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()

                # Get table list
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cur.fetchall()]

                # Get record count from main table
                if table in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cur.fetchone()[0]
                    print(f"{db_file}: {count} records in {table}")
                else:
                    print(f"{db_file}: Table '{table}' not found. Tables: {tables}")

                conn.close()
            except Exception as e:
                print(f"{db_file}: Error - {e}")
        else:
            print(f"{db_file}: File not found")

    print("\nRecent database activity:")
    import os
    import time
    for db_file in databases.keys():
        db_path = db_dir / db_file
        if db_path.exists():
            mtime = os.path.getmtime(db_path)
            mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            print(f"{db_file}: Last modified {mtime_str}")

if __name__ == "__main__":
    check_database_status()
