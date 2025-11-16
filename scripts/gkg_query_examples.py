#!/usr/bin/env python3
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier


"""
GKG Query Examples - Demonstrating keyword search on 5.1M China-related records
Using themes discovered from data exploration

Database: F:/OSINT_WAREHOUSE/osint_master.db
Records: 5,165,311 China-related GKG records from 100 high-value dates (2020-2025)
Cost: $0.00
"""

import sqlite3
from collections import Counter

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

#--------------------------------------------------------------------------#
# Query 1: Technology & Innovation Coverage
#--------------------------------------------------------------------------#
def query_technology_innovation():
    """
    Find articles mentioning technology and innovation
    Real themes: WB_376_INNOVATION_TECHNOLOGY_AND_ENTREPRENEURSHIP
                 SOC_EMERGINGTECH
                 SOC_INNOVATION
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = '''
    SELECT
        SUBSTR(CAST(publish_date AS TEXT), 1, 8) as date,
        themes,
        organizations,
        tone,
        document_identifier
    FROM gdelt_gkg
    WHERE (themes LIKE '%INNOVATION%'
        OR themes LIKE '%EMERGINGTECH%'
        OR themes LIKE '%WB_133_INFORMATION_AND_COMMUNICATION_TECHNOLOGIES%')
    ORDER BY publish_date DESC
    LIMIT 20
    '''

    cursor.execute(query)
    results = cursor.fetchall()

    print("="*80)
    print(f"QUERY 1: Technology & Innovation Coverage")
    print(f"Found: {len(results)} results (showing top 20)")
    print("="*80)

    for i, (date, themes, orgs, tone, url) in enumerate(results, 1):
        # Extract innovation themes
        theme_list = [t for t in themes.split(';') if t and 'INNOV' in t.upper()][:2]
        # Extract organizations
        org_list = [o.split(',')[0] for o in orgs.split(';') if o][:2]

        print(f"\n{i}. Date: {date}, Tone: {tone:.1f}")
        if theme_list:
            print(f"   Themes: {theme_list}")
        if org_list:
            print(f"   Orgs: {org_list}")
        print(f"   URL: {url[:70]}...")

    conn.close()
    print()

#--------------------------------------------------------------------------#
# Query 2: Research & University Collaboration
#--------------------------------------------------------------------------#
def query_research_universities():
    """
    Find research and university activities
    Real themes: SOC_POINTSOFINTEREST_UNIVERSITY
                 TAX_FNCACT_RESEARCHER
                 SCIENCE
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = '''
    SELECT
        SUBSTR(CAST(publish_date AS TEXT), 1, 8) as date,
        themes,
        organizations,
        persons,
        tone
    FROM gdelt_gkg
    WHERE (themes LIKE '%UNIVERSITY%'
        OR themes LIKE '%RESEARCHER%'
        OR themes LIKE '%SCIENCE%')
    AND organizations LIKE '%UNIVERSITY%'
    ORDER BY publish_date DESC
    LIMIT 15
    '''

    cursor.execute(query)
    results = cursor.fetchall()

    print("="*80)
    print(f"QUERY 2: Research & University Collaboration")
    print(f"Found: {len(results)} results (showing top 15)")
    print("="*80)

    for i, (date, themes, orgs, persons, tone) in enumerate(results, 1):
        # Extract universities
        univ_list = [o for o in orgs.split(';') if o and 'UNIVERSITY' in o.upper()][:2]
        # Extract researchers
        person_list = [p.split(',')[0] for p in persons.split(';') if p][:2]

        print(f"\n{i}. Date: {date}, Tone: {tone:.1f}")
        if univ_list:
            print(f"   Universities: {univ_list}")
        if person_list:
            print(f"   Persons: {person_list}")

    conn.close()
    print()

#--------------------------------------------------------------------------#
# Query 3: Temporal Analysis - Innovation Trends
#--------------------------------------------------------------------------#
def query_temporal_innovation():
    """
    Track innovation mentions over time
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = '''
    SELECT
        SUBSTR(CAST(publish_date AS TEXT), 1, 8) as date,
        COUNT(*) as articles,
        AVG(tone) as avg_tone,
        AVG(positive_score) as avg_positive,
        AVG(negative_score) as avg_negative
    FROM gdelt_gkg
    WHERE themes LIKE '%INNOVATION%'
    GROUP BY SUBSTR(CAST(publish_date AS TEXT), 1, 8)
    ORDER BY date DESC
    LIMIT 20
    '''

    cursor.execute(query)
    results = cursor.fetchall()

    print("="*80)
    print(f"QUERY 3: Innovation Coverage Over Time")
    print("="*80)
    print(f"{'Date':10} {'Articles':>8} {'Tone':>8} {'Positive':>8} {'Negative':>8}")
    print("-"*50)

    for date, count, tone, pos, neg in results:
        print(f"{date:10} {count:8,} {tone:8.1f} {pos:8.1f} {neg:8.1f}")

    conn.close()
    print()

#--------------------------------------------------------------------------#
# Query 4: Specific Organizations (Huawei, Tencent, Alibaba)
#--------------------------------------------------------------------------#
def query_tech_companies():
    """
    Find mentions of major Chinese tech companies
    """
    conn = connect_db()
    cursor = conn.cursor()

    companies = ['HUAWEI', 'TENCENT', 'ALIBABA', 'BAIDU', 'XIAOMI']

    print("="*80)
    print(f"QUERY 4: Major Chinese Tech Company Mentions")
    print("="*80)

    for company in companies:
        # SECURITY: Use parameterized query to prevent SQL injection
        cursor.execute('''
            SELECT COUNT(*)
            FROM gdelt_gkg
            WHERE organizations LIKE ?
        ''', (f'%{company}%',))
        count = cursor.fetchone()[0]
        print(f"{company:15} {count:6,} mentions")

    # Get sample articles for most mentioned company
    cursor.execute('''
        SELECT
            SUBSTR(CAST(publish_date AS TEXT), 1, 8) as date,
            themes,
            tone,
            document_identifier
        FROM gdelt_gkg
        WHERE organizations LIKE '%HUAWEI%'
        OR organizations LIKE '%TENCENT%'
        OR organizations LIKE '%ALIBABA%'
        ORDER BY publish_date DESC
        LIMIT 5
    ''')

    results = cursor.fetchall()
    print(f"\nSample articles mentioning these companies:")
    print("-"*80)
    for i, (date, themes, tone, url) in enumerate(results, 1):
        theme_list = [t.split(',')[0] for t in themes.split(';') if t][:2]
        print(f"{i}. {date} | Tone: {tone:5.1f} | {theme_list}")
        print(f"   {url[:70]}...")

    conn.close()
    print()

#--------------------------------------------------------------------------#
# Query 5: Location-Based Analysis
#--------------------------------------------------------------------------#
def query_location_analysis():
    """
    Analyze coverage by location
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = '''
    SELECT locations
    FROM gdelt_gkg
    WHERE locations != ''
    LIMIT 2000
    '''

    cursor.execute(query)

    all_countries = []
    for row in cursor.fetchall():
        locs = row[0].split(';')
        for loc in locs:
            if loc:
                # Extract country from location string
                parts = loc.split('#')
                if len(parts) > 1:
                    country = parts[1] if len(parts) > 1 else loc
                    all_countries.append(country)

    country_counts = Counter(all_countries)

    print("="*80)
    print(f"QUERY 5: Top 20 Locations in China-related GKG Records")
    print("="*80)

    for country, count in country_counts.most_common(20):
        print(f"{country:40} {count:6,} mentions")

    conn.close()
    print()

#--------------------------------------------------------------------------#
# Query 6: Sentiment Analysis by Theme
#--------------------------------------------------------------------------#
def query_sentiment_by_theme():
    """
    Compare sentiment across different theme categories
    """
    conn = connect_db()
    cursor = conn.cursor()

    theme_categories = [
        ('Innovation', '%INNOVATION%'),
        ('Security', '%SECURITY%'),
        ('Education', '%EDUCATION%'),
        ('Health/Medical', '%MEDICAL%'),
        ('Government', '%GOVERNMENT%')
    ]

    print("="*80)
    print(f"QUERY 6: Average Sentiment by Theme Category")
    print("="*80)
    print(f"{'Category':20} {'Articles':>10} {'Avg Tone':>10} {'Positive':>10} {'Negative':>10}")
    print("-"*70)

    for category, pattern in theme_categories:
        # SECURITY: Use parameterized query to prevent SQL injection
        cursor.execute('''
            SELECT
                COUNT(*) as count,
                AVG(tone) as avg_tone,
                AVG(positive_score) as avg_pos,
                AVG(negative_score) as avg_neg
            FROM gdelt_gkg
            WHERE themes LIKE ?
        ''', (pattern,))

        count, tone, pos, neg = cursor.fetchone()
        if count:
            print(f"{category:20} {count:10,} {tone:10.2f} {pos:10.2f} {neg:10.2f}")

    conn.close()
    print()

#--------------------------------------------------------------------------#
# Query 7: Most Common Themes
#--------------------------------------------------------------------------#
def query_theme_distribution():
    """
    Show most common themes in the dataset
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT themes
        FROM gdelt_gkg
        WHERE themes != ''
        LIMIT 3000
    ''')

    all_themes = []
    for row in cursor.fetchall():
        themes = row[0].split(';')
        for theme in themes:
            if theme and not theme.startswith('TAX_WORLDLANGUAGES'):
                theme_name = theme.split(',')[0]
                all_themes.append(theme_name)

    theme_counts = Counter(all_themes)

    print("="*80)
    print(f"QUERY 7: Top 30 Themes in China-related GKG Records")
    print("="*80)

    for theme, count in theme_counts.most_common(30):
        print(f"{theme:60} {count:5,}")

    conn.close()
    print()

#--------------------------------------------------------------------------#
# Main Execution
#--------------------------------------------------------------------------#
if __name__ == "__main__":
    print()
    print("#" * 80)
    print("# GKG KEYWORD SEARCH DEMONSTRATION")
    print("# Database: 5.1M China-related records from 100 high-value dates")
    print("# Coverage: 2020-2025")
    print("# Cost: $0.00")
    print("#" * 80)
    print()

    # Run all queries
    query_technology_innovation()
    input("Press Enter to continue to next query...")

    query_research_universities()
    input("Press Enter to continue to next query...")

    query_temporal_innovation()
    input("Press Enter to continue to next query...")

    query_tech_companies()
    input("Press Enter to continue to next query...")

    query_location_analysis()
    input("Press Enter to continue to next query...")

    query_sentiment_by_theme()
    input("Press Enter to continue to next query...")

    query_theme_distribution()

    print()
    print("="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print()
    print("All queries executed successfully on 5.1M GKG records.")
    print("These examples demonstrate the keyword search capability you now have.")
    print()
