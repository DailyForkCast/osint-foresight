#!/usr/bin/env python3
"""
Query OSINT Database for Intelligence
Execute queries and generate reports from SQL database
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

def query_database():
    """Query the OSINT database and generate intelligence reports"""

    db_path = Path("F:/OSINT_DATA/osint_intelligence.db")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("="*60)
    print("OSINT DATABASE INTELLIGENCE QUERIES")
    print(f"Database: {db_path}")
    print("="*60)

    # 1. Patent Overview
    print("\n1. PATENT OVERVIEW")
    print("-"*40)
    cursor.execute("""
    SELECT
        category,
        COUNT(*) as count,
        COUNT(DISTINCT country_code) as countries
    FROM patents
    GROUP BY category
    ORDER BY count DESC
    """)

    for category, count, countries in cursor.fetchall():
        print(f"  {category}: {count} patents from {countries} countries")

    # 2. Organization Analysis
    print("\n2. TOP ORGANIZATIONS BY PATENTS")
    print("-"*40)
    cursor.execute("""
    SELECT
        applicant_name,
        applicant_country,
        COUNT(DISTINCT patent_id) as patent_count
    FROM patent_applicants
    WHERE applicant_name != ''
    GROUP BY applicant_name
    ORDER BY patent_count DESC
    LIMIT 10
    """)

    for name, country, count in cursor.fetchall():
        # Handle unicode in organization names
        safe_name = name.encode('ascii', 'ignore').decode('ascii')[:50] if name else 'Unknown'
        print(f"  {safe_name}: {count} patents ({country})")

    # 3. Technology Areas
    print("\n3. TECHNOLOGY DISTRIBUTION")
    print("-"*40)
    cursor.execute("""
    SELECT
        technology_area,
        COUNT(*) as classification_count,
        COUNT(DISTINCT patent_id) as patent_count
    FROM patent_classifications
    GROUP BY technology_area
    ORDER BY classification_count DESC
    """)

    for tech, class_count, patent_count in cursor.fetchall():
        print(f"  {tech}: {class_count} classifications in {patent_count} patents")

    # 4. Cross-border patterns
    print("\n4. CROSS-BORDER PATENT APPLICATIONS")
    print("-"*40)
    cursor.execute("""
    SELECT
        p.patent_id,
        p.title,
        GROUP_CONCAT(DISTINCT pa.applicant_country) as countries,
        COUNT(DISTINCT pa.applicant_country) as country_count
    FROM patents p
    JOIN patent_applicants pa ON p.patent_id = pa.patent_id
    GROUP BY p.patent_id
    HAVING COUNT(DISTINCT pa.applicant_country) > 1
    """)

    cross_border = cursor.fetchall()
    if cross_border:
        for patent_id, title, countries, count in cross_border:
            print(f"  {patent_id}: {title[:40]}...")
            print(f"    Countries: {countries}")
    else:
        print("  No cross-border collaborations detected in current dataset")

    # 5. Chinese involvement
    print("\n5. CHINESE ENTITY INVOLVEMENT")
    print("-"*40)
    cursor.execute("""
    SELECT
        applicant_name,
        COUNT(DISTINCT patent_id) as patent_count
    FROM patent_applicants
    WHERE applicant_country = 'CN' OR applicant_name LIKE '%CHINA%'
       OR applicant_name LIKE '%CHINESE%' OR applicant_name LIKE '%HUAWEI%'
    GROUP BY applicant_name
    """)

    chinese_entities = cursor.fetchall()
    if chinese_entities:
        for name, count in chinese_entities:
            safe_name = name.encode('ascii', 'ignore').decode('ascii') if name else 'Unknown'
            print(f"  {safe_name}: {count} patents")
    else:
        print("  Analyzing entity names for Chinese involvement...")

        # Alternative check
        cursor.execute("""
        SELECT DISTINCT applicant_name
        FROM patent_applicants
        WHERE applicant_name LIKE '%CN%' OR applicant_name LIKE '%LTD%'
        """)

        potential = cursor.fetchall()
        for (name,) in potential[:5]:
            print(f"    Potential: {name}")

    # 6. Critical technology focus
    print("\n6. CRITICAL TECHNOLOGY AREAS")
    print("-"*40)
    critical_techs = ['5G/Telecommunications', 'Computing/AI', 'Electronic Components']

    for tech in critical_techs:
        cursor.execute("""
        SELECT COUNT(DISTINCT p.patent_id)
        FROM patents p
        JOIN patent_classifications pc ON p.patent_id = pc.patent_id
        WHERE pc.technology_area = ?
        """, (tech,))

        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  {tech}: {count} patents")

    # 7. Export intelligence summary
    print("\n7. GENERATING INTELLIGENCE SUMMARY")
    print("-"*40)

    summary = {
        'generated': datetime.now().isoformat(),
        'database': str(db_path),
        'statistics': {},
        'key_findings': []
    }

    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM patents")
    summary['statistics']['total_patents'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT applicant_name) FROM patent_applicants")
    summary['statistics']['unique_organizations'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT technology_area) FROM patent_classifications")
    summary['statistics']['technology_areas'] = cursor.fetchone()[0]

    # Key findings
    cursor.execute("""
    SELECT category, COUNT(*) as c
    FROM patents
    GROUP BY category
    ORDER BY c DESC
    LIMIT 1
    """)
    top_category = cursor.fetchone()
    if top_category:
        summary['key_findings'].append({
            'finding': 'Top patent category',
            'value': top_category[0],
            'count': top_category[1]
        })

    # Save summary
    summary_file = Path("F:/OSINT_DATA/database_intelligence_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"  Summary saved to: {summary_file}")

    conn.close()

    print("\n" + "="*60)
    print("INTELLIGENCE EXTRACTION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    query_database()
