#!/usr/bin/env python3
"""
Query project databases for MCF/NQPF enrichment data
Focus on high-priority slides: 6, 10, 11, 14
"""

import sqlite3
import json
from pathlib import Path
from collections import Counter
import re

print("="*80)
print("ENRICHMENT DATA QUERY - HIGH PRIORITY SLIDES")
print("="*80)

# Check which databases exist
db_paths = {
    'master': 'data/osint_master.db',
    'kaggle_arxiv': 'data/kaggle_arxiv_processing.db',
    'warehouse': 'F:/OSINT_WAREHOUSE/osint_warehouse.db'
}

available_dbs = {}
for name, path in db_paths.items():
    if Path(path).exists():
        available_dbs[name] = path
        print(f"[OK] Found: {name} at {path}")
    else:
        print(f"[X] Not found: {name} at {path}")

print("\n" + "="*80)

# ========== SLIDE 6: MCF/NQPF KEYWORD TRENDS ==========
print("\n[SLIDE 6] MCF/NQPF KEYWORD TRENDS")
print("-"*80)

mcf_keywords = ['military-civil fusion', 'MCF', 'civil-military integration',
                'jun-min ronghe', 'junmin ronghe']
nqpf_keywords = ['new quality productive forces', 'NQPF', 'xin zhi sheng chan li',
                 'new-type productive forces']

# Try to find keyword trends in OpenAlex/arXiv data
if 'kaggle_arxiv' in available_dbs:
    print("\nQuerying Kaggle arXiv database for MCF/NQPF keywords...")
    conn = sqlite3.connect(available_dbs['kaggle_arxiv'])
    cursor = conn.cursor()

    # Check schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")

    # Try to get schema of main table
    if tables:
        table_name = tables[0][0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\nColumns in {table_name}:")
        for col in columns[:10]:  # First 10 columns
            print(f"  - {col[1]} ({col[2]})")

        # Try to query for papers with China affiliation and MCF-related keywords
        # Check if we have year/date field
        col_names = [col[1] for col in columns]

        if 'update_date' in col_names or 'published_date' in col_names:
            date_field = 'update_date' if 'update_date' in col_names else 'published_date'

            # Query for MCF keywords by year
            print(f"\nSearching for MCF keywords in abstracts...")
            query = f"""
            SELECT
                substr({date_field}, 1, 4) as year,
                COUNT(*) as papers
            FROM {table_name}
            WHERE (abstract LIKE '%military%' AND abstract LIKE '%civil%')
               OR abstract LIKE '%dual%use%'
               OR abstract LIKE '%defense%innovation%'
            GROUP BY year
            ORDER BY year DESC
            LIMIT 10
            """
            cursor.execute(query)
            results = cursor.fetchall()

            if results:
                print("\nMCF-related papers by year:")
                for row in results:
                    print(f"  {row[0]}: {row[1]} papers")
            else:
                print("  No results found")

    conn.close()

# Check master database for entity detections with Chinese institutions
if 'master' in available_dbs:
    print("\n\nQuerying master database for Chinese entity patterns...")
    conn = sqlite3.connect(available_dbs['master'])
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")

    # Look for detection or entity tables
    detection_tables = [t[0] for t in tables if 'detection' in t[0].lower() or
                       'entity' in t[0].lower() or 'openalex' in t[0].lower()]

    if detection_tables:
        print(f"\nRelevant tables: {detection_tables}")

        for table in detection_tables[:3]:  # Check first 3 tables
            print(f"\n  Checking {table}...")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]

            # Try to get sample data
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count}")

            if count > 0 and count < 100000:  # Only query if reasonable size
                # Try to find year patterns
                if 'year' in col_names or 'date' in col_names:
                    year_field = 'year' if 'year' in col_names else 'date'
                    cursor.execute(f"""
                    SELECT {year_field}, COUNT(*)
                    FROM {table}
                    GROUP BY {year_field}
                    ORDER BY {year_field} DESC
                    LIMIT 10
                    """)
                    year_results = cursor.fetchall()
                    if year_results:
                        print(f"    Year distribution:")
                        for row in year_results[:5]:
                            print(f"      {row[0]}: {row[1]}")

    conn.close()

print("\n" + "="*80)
print("\n[SLIDE 10] HIT/NPU COLLABORATION CASES")
print("-"*80)

# Look for Harbin Institute of Technology (HIT) and Northwestern Polytechnical University (NPU)
# in collaboration data

target_institutions = [
    'Harbin Institute of Technology',
    'Northwestern Polytechnical University',
    'HIT',
    'NPU',
    'Harbin',
    'Northwestern Poly'
]

if 'master' in available_dbs:
    print("\nSearching for HIT/NPU collaborations...")
    conn = sqlite3.connect(available_dbs['master'])
    cursor = conn.cursor()

    # Find tables with institution or affiliation data
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    collab_tables = [t[0] for t in tables if 'collab' in t[0].lower() or
                    'author' in t[0].lower() or 'institution' in t[0].lower()]

    if collab_tables:
        print(f"Collaboration tables: {collab_tables}")

        for table in collab_tables[:2]:
            print(f"\n  Checking {table}...")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            print(f"    Columns: {col_names[:10]}")

            # Look for institution fields
            inst_fields = [c for c in col_names if 'institution' in c.lower() or
                          'affiliation' in c.lower() or 'org' in c.lower()]

            if inst_fields:
                print(f"    Institution fields: {inst_fields}")

                # Try to search for HIT/NPU
                inst_field = inst_fields[0]
                for target in ['Harbin', 'Northwestern Poly']:
                    try:
                        cursor.execute(f"""
                        SELECT COUNT(*)
                        FROM {table}
                        WHERE {inst_field} LIKE '%{target}%'
                        LIMIT 10
                        """)
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"    Found {count} records with '{target}'")
                    except Exception as e:
                        print(f"    Error querying: {e}")

    conn.close()

print("\n" + "="*80)
print("\n[SLIDE 11] GLOBAL EXAMPLES - TED PROCUREMENT")
print("-"*80)

# Look for TED (Tenders Electronic Daily) procurement data with Chinese contractors

if 'master' in available_dbs:
    print("\nSearching for TED procurement data with Chinese entities...")
    conn = sqlite3.connect(available_dbs['master'])
    cursor = conn.cursor()

    # Find TED tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    ted_tables = [t[0] for t in tables if 'ted' in t[0].lower()]

    if ted_tables:
        print(f"TED tables: {ted_tables}")

        for table in ted_tables[:2]:
            print(f"\n  Checking {table}...")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]

            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"    Total records: {count}")

            # Look for contractor or company fields
            company_fields = [c for c in col_names if 'contractor' in c.lower() or
                            'company' in c.lower() or 'winner' in c.lower() or
                            'supplier' in c.lower()]

            if company_fields:
                print(f"    Company fields: {company_fields}")

                # Search for Huawei, ZTE, Chinese companies
                chinese_companies = ['Huawei', 'ZTE', 'China']

                for company in chinese_companies:
                    for field in company_fields[:2]:
                        try:
                            cursor.execute(f"""
                            SELECT COUNT(*)
                            FROM {table}
                            WHERE {field} LIKE '%{company}%'
                            LIMIT 1
                            """)
                            result = cursor.fetchone()
                            if result and result[0] > 0:
                                print(f"    Found {result[0]} records with '{company}' in {field}")

                                # Get sample records
                                cursor.execute(f"""
                                SELECT {field},
                                       {'country' if 'country' in col_names else '""'} as country
                                FROM {table}
                                WHERE {field} LIKE '%{company}%'
                                LIMIT 5
                                """)
                                samples = cursor.fetchall()
                                if samples:
                                    print(f"      Sample records:")
                                    for s in samples[:3]:
                                        print(f"        {s}")
                        except Exception as e:
                            pass

    conn.close()

print("\n" + "="*80)
print("\n[SLIDE 14] ILLICIT ACQUISITION CASES")
print("-"*80)

# Look for cyber incident, APT, or enforcement action data

if 'master' in available_dbs:
    print("\nSearching for cyber incident or enforcement data...")
    conn = sqlite3.connect(available_dbs['master'])
    cursor = conn.cursor()

    # Find relevant tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    incident_tables = [t[0] for t in tables if 'cyber' in t[0].lower() or
                      'apt' in t[0].lower() or 'incident' in t[0].lower() or
                      'enforcement' in t[0].lower() or 'violation' in t[0].lower()]

    if incident_tables:
        print(f"Incident tables: {incident_tables}")

        for table in incident_tables:
            print(f"\n  {table}:")
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"    Records: {count}")
    else:
        print("  No dedicated incident tables found")

        # Check if any tables have incident-related fields
        all_tables = [t[0] for t in tables]
        for table in all_tables[:10]:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_names = [col[1].lower() for col in columns]

            if any(keyword in ' '.join(col_names) for keyword in
                   ['threat', 'apt', 'cyber', 'hack', 'intrusion', 'violation']):
                print(f"\n  {table} may have incident data:")
                print(f"    Columns: {[col[1] for col in columns][:10]}")

    conn.close()

# Check for any analysis reports that might have case studies
print("\n\nChecking analysis reports for case studies...")
analysis_files = [
    'analysis/USASPENDING_VALIDATION_FINAL_SUMMARY.md',
    'analysis/USPTO_CRITICAL_FINDINGS_20251006.md',
    'analysis/TED_CHINESE_CONTRACTOR_ANALYSIS.md',
    'analysis/CHINA_EUROPE_INTERACTIONS.md'
]

for filepath in analysis_files:
    path = Path(filepath)
    if path.exists():
        print(f"\n[OK] Found: {filepath}")
        # Read first 100 lines to see if it has relevant data
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()[:50]
            # Look for specific company/case mentions
            text = ''.join(lines).lower()
            if 'huawei' in text or 'zte' in text or 'harbin' in text:
                print(f"  Contains relevant company mentions")
                # Extract some context
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in
                          ['huawei', 'zte', 'harbin', 'northwestern', 'case', 'example']):
                        print(f"  Line {i+1}: {line.strip()[:80]}...")
    else:
        print(f"[X] Not found: {filepath}")

print("\n" + "="*80)
print("QUERY COMPLETE")
print("="*80)
