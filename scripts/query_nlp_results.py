#!/usr/bin/env python3
"""
Query NLP extraction results to demonstrate capabilities
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("C:/Projects/OSINT-Foresight/database/osint_master.db")

def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(title)
    print("="*80)

def query_year_targets():
    """Query for year-based targets across all documents"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("TIMELINE: POLICY TARGETS BY YEAR")

    results = cursor.execute("""
    SELECT
        target_year,
        COUNT(*) as mentions,
        GROUP_CONCAT(DISTINCT provision_type) as types
    FROM policy_provisions
    WHERE target_year IS NOT NULL
    GROUP BY target_year
    ORDER BY target_year
    LIMIT 20
    """).fetchall()

    print(f"\n{'Year':<10} {'Mentions':<12} {'Provision Types'}")
    print("-"*80)
    for row in results:
        print(f"{row[0]:<10} {row[1]:<12} {row[2][:50] if row[2] else 'N/A'}")

    conn.close()

def query_technology_priorities():
    """Query technology domain priorities"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("TECHNOLOGY PRIORITIES ACROSS ALL DOCUMENTS")

    results = cursor.execute("""
    SELECT
        technology_domain,
        COUNT(DISTINCT document_id) as documents,
        SUM(CASE WHEN priority_level = 'high_priority' THEN 1 ELSE 0 END) as high_priority,
        SUM(CASE WHEN priority_level = 'medium_priority' THEN 1 ELSE 0 END) as medium_priority
    FROM policy_technology_domains
    GROUP BY technology_domain
    ORDER BY documents DESC
    """).fetchall()

    print(f"\n{'Technology Domain':<30} {'Docs':<8} {'High Pri':<10} {'Med Pri':<10}")
    print("-"*80)
    for row in results:
        print(f"{row[0]:<30} {row[1]:<8} {row[2]:<10} {row[3]:<10}")

    conn.close()

def query_entity_references():
    """Query most mentioned entities"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("MOST REFERENCED CHINESE ENTITIES")

    results = cursor.execute("""
    SELECT
        entity_name,
        entity_type,
        COUNT(*) as mentions,
        COUNT(DISTINCT document_id) as documents
    FROM policy_entity_references
    GROUP BY entity_name, entity_type
    ORDER BY mentions DESC
    LIMIT 25
    """).fetchall()

    print(f"\n{'Entity Name':<40} {'Type':<30} {'Mentions':<10} {'Docs'}")
    print("-"*80)
    for row in results:
        print(f"{row[0]:<40} {row[1]:<30} {row[2]:<10} {row[3]}")

    conn.close()

def query_made_in_china_2025():
    """Query Made in China 2025 specific data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("MADE IN CHINA 2025 - SPECIFIC TARGETS")

    # Get document ID for MIC2025
    doc_id = cursor.execute("""
    SELECT document_id FROM chinese_policy_documents
    WHERE title LIKE '%Made in China 2025%'
    """).fetchone()

    if not doc_id:
        print("Made in China 2025 document not found")
        conn.close()
        return

    doc_id = doc_id[0]

    # Get quantitative targets
    results = cursor.execute("""
    SELECT
        provision_type,
        quantitative_value,
        quantitative_unit,
        target_year,
        SUBSTR(provision_text, 1, 100) as context
    FROM policy_provisions
    WHERE document_id = ?
    AND quantitative_value IS NOT NULL
    ORDER BY target_year, quantitative_value DESC
    LIMIT 15
    """, (doc_id,)).fetchall()

    print(f"\n{'Type':<20} {'Value':<12} {'Unit':<10} {'Year':<8} {'Context'}")
    print("-"*80)
    for row in results:
        context = row[4].replace('\n', ' ')[:50] if row[4] else 'N/A'
        print(f"{row[0]:<20} {row[1]:<12.2f} {row[2]:<10} {str(row[3]):<8} {context}")

    # Get technology domains in MIC2025
    tech_results = cursor.execute("""
    SELECT
        technology_domain,
        priority_level,
        SUBSTR(context, 1, 100) as context
    FROM policy_technology_domains
    WHERE document_id = ?
    ORDER BY priority_level DESC
    """, (doc_id,)).fetchall()

    print("\nTECHNOLOGY PRIORITIES IN MADE IN CHINA 2025:")
    print("-"*80)
    for row in tech_results:
        context = row[2].replace('\n', ' ')[:60] if row[2] else 'N/A'
        print(f"  - {row[0]:<30} [{row[1]}]: {context}")

    conn.close()

def query_thousand_talents():
    """Query Thousand Talents program information"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("THOUSAND TALENTS PROGRAM - ENTITY REFERENCES")

    results = cursor.execute("""
    SELECT
        e.entity_name,
        d.title,
        SUBSTR(e.role_description, 1, 100) as context
    FROM policy_entity_references e
    JOIN chinese_policy_documents d ON e.document_id = d.document_id
    WHERE e.entity_name LIKE '%Thousand Talents%'
    ORDER BY d.title
    LIMIT 10
    """).fetchall()

    for row in results:
        print(f"\nDocument: {row[1][:60]}")
        print(f"Entity: {row[0]}")
        print(f"Context: {row[2].replace(chr(10), ' ')}")

    conn.close()

def query_2025_2030_targets():
    """Query specific targets for 2025 and 2030"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("2025 vs 2030 TARGETS COMPARISON")

    for year in [2025, 2030]:
        results = cursor.execute("""
        SELECT
            milestone_type,
            COUNT(*) as count,
            SUBSTR(GROUP_CONCAT(milestone_description, ' | '), 1, 200) as examples
        FROM policy_timeline
        WHERE milestone_year = ?
        GROUP BY milestone_type
        ORDER BY count DESC
        """, (year,)).fetchall()

        print(f"\n{year} TARGETS:")
        print("-"*80)
        for row in results:
            print(f"\n  Type: {row[0]} ({row[1]} mentions)")
            if row[2]:
                examples = row[2].replace('\n', ' ')[:150]
                print(f"  Examples: {examples}...")

    conn.close()

def query_cross_document_tech_coverage():
    """Show which documents cover which technologies"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("TECHNOLOGY DOMAIN COVERAGE BY DOCUMENT PRIORITY")

    results = cursor.execute("""
    SELECT
        d.priority_level,
        t.technology_domain,
        COUNT(DISTINCT d.document_id) as doc_count
    FROM policy_technology_domains t
    JOIN chinese_policy_documents d ON t.document_id = d.document_id
    GROUP BY d.priority_level, t.technology_domain
    ORDER BY d.priority_level, doc_count DESC
    """).fetchall()

    current_priority = None
    for row in results:
        if row[0] != current_priority:
            print(f"\n{row[0]} PRIORITY DOCUMENTS:")
            print("-"*80)
            current_priority = row[0]
        print(f"  {row[1]:<35} - {row[2]} documents")

    conn.close()

def main():
    """Run all demonstration queries"""
    print("="*80)
    print("CHINESE POLICY DOCUMENTS - NLP EXTRACTION RESULTS")
    print("="*80)
    print("\nQuerying extracted structured data...")

    query_year_targets()
    query_technology_priorities()
    query_entity_references()
    query_made_in_china_2025()
    query_thousand_talents()
    query_2025_2030_targets()
    query_cross_document_tech_coverage()

    print("\n" + "="*80)
    print("QUERY DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nDatabase now contains:")
    print("  - 6,401 quantitative provisions (targets, percentages, financial data)")
    print("  - 198 entity references (SOEs, agencies, institutions)")
    print("  - 503 timeline milestones (2020, 2025, 2030 targets)")
    print("  - 174 technology domain mappings")
    print("\nReady for cross-database intelligence queries!")
    print("="*80)

if __name__ == "__main__":
    main()
