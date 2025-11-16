"""
Monitor OpenAlex V2 Production Progress
"""
import sqlite3
import time
from datetime import datetime

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def monitor_progress():
    """Monitor and display production progress"""

    print("=" * 80)
    print("OPENALEX V2 PRODUCTION MONITOR")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    conn = sqlite3.connect(DB_PATH)

    # Total works
    total = conn.execute("SELECT COUNT(*) FROM openalex_works WHERE validation_keyword IS NOT NULL").fetchone()[0]
    print(f"Total V2 works: {total:,}")
    print()

    # Works by technology
    print("Works by technology:")
    print("-" * 60)
    for row in conn.execute("""
        SELECT technology_domain, COUNT(*)
        FROM openalex_works
        WHERE validation_keyword IS NOT NULL
        GROUP BY technology_domain
        ORDER BY technology_domain
    """):
        tech, count = row
        pct = (count / 10000) * 100
        bar_length = int(pct / 2)  # 50 chars max
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {tech:20s}: {count:6,} / 10,000 ({pct:5.1f}%) {bar}")

    print()

    # Top countries
    print("Top 10 countries:")
    print("-" * 60)
    for row in conn.execute("""
        SELECT country_code, COUNT(DISTINCT work_id) as works
        FROM openalex_work_authors
        WHERE country_code IS NOT NULL
        GROUP BY country_code
        ORDER BY works DESC
        LIMIT 10
    """):
        country, count = row
        print(f"  {country}: {count:,} works")

    print()

    # Authors and institutions
    authors = conn.execute("SELECT COUNT(DISTINCT author_id) FROM openalex_work_authors").fetchone()[0]
    institutions = conn.execute("SELECT COUNT(DISTINCT institution_id) FROM openalex_work_authors WHERE institution_id IS NOT NULL").fetchone()[0]
    funders = conn.execute("SELECT COUNT(DISTINCT funder_id) FROM openalex_work_funders").fetchone()[0]

    print(f"Unique authors: {authors:,}")
    print(f"Unique institutions: {institutions:,}")
    print(f"Unique funders: {funders:,}")

    conn.close()

    print()
    print("=" * 80)
    print(f"[Refreshed at {datetime.now().strftime('%H:%M:%S')}]")
    print("Press Ctrl+C to exit")

if __name__ == "__main__":
    try:
        while True:
            monitor_progress()
            time.sleep(30)  # Refresh every 30 seconds
            print("\n" * 2)  # Clear space
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
