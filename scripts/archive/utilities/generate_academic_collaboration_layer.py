#!/usr/bin/env python3
"""
Generate Academic Collaboration Layer for Bilateral Relations
Integrates OpenAlex research collaboration data with bilateral framework
"""

import sqlite3
import sys
import io
import json
from pathlib import Path
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

conn = sqlite3.connect(str(DB_PATH))
cur = conn.cursor()

print("="*80)
print("ACADEMIC COLLABORATION INTEGRATION - EU-CHINA RESEARCH")
print("="*80 + "\n")

# Get our 28 bilateral countries
bilateral_countries = ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE','GB']

country_names = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'HR': 'Croatia', 'CY': 'Cyprus',
    'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia', 'FI': 'Finland', 'FR': 'France',
    'DE': 'Germany', 'GR': 'Greece', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy',
    'LV': 'Latvia', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'MT': 'Malta', 'NL': 'Netherlands',
    'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SK': 'Slovakia', 'SI': 'Slovenia',
    'ES': 'Spain', 'SE': 'Sweden', 'GB': 'United Kingdom'
}

# Get collaboration statistics by country
cur.execute(f'''
    SELECT country_code, COUNT(*) as institutions,
           SUM(works_count) as total_works,
           ROUND(AVG(works_count), 1) as avg_works,
           SUM(cited_by_count) as total_citations,
           ROUND(AVG(h_index), 1) as avg_h_index
    FROM openalex_entities
    WHERE country_code IN ({','.join(['?' for _ in bilateral_countries])})
      AND entity_type = 'institution'
    GROUP BY country_code
    ORDER BY total_works DESC
''', bilateral_countries)

collaboration_stats = []
for row in cur.fetchall():
    collaboration_stats.append({
        'country_code': row[0],
        'country_name': country_names.get(row[0], row[0]),
        'institutions': row[1],
        'total_works': row[2],
        'avg_works_per_institution': row[3],
        'total_citations': row[4],
        'avg_h_index': row[5]
    })

print(f"Total Countries with Data: {len(collaboration_stats)}/28")
print(f"Total Institutions: {sum(c['institutions'] for c in collaboration_stats):,}")
print(f"Total Collaborative Works: {sum(c['total_works'] for c in collaboration_stats):,}")
print(f"Total Citations: {sum(c['total_citations'] for c in collaboration_stats):,}\n")

# Top collaborating institutions by country
print("="*80)
print("TOP RESEARCH INSTITUTIONS BY COUNTRY (China Collaborations)")
print("="*80 + "\n")

for country_stat in collaboration_stats[:10]:  # Top 10 countries
    cc = country_stat['country_code']
    print(f"\n{country_stat['country_name']} ({cc}):")
    print(f"  Total: {country_stat['institutions']:,} institutions, {country_stat['total_works']:,} works")

    # Get top institutions for this country
    cur.execute('''
        SELECT name, works_count, cited_by_count, h_index, city
        FROM openalex_entities
        WHERE country_code = ? AND entity_type = 'institution'
        ORDER BY works_count DESC
        LIMIT 5
    ''', (cc,))

    print(f"  Top Institutions:")
    for inst in cur.fetchall():
        city_str = f", {inst[4]}" if inst[4] else ""
        print(f"    • {inst[0]}{city_str}")
        print(f"      Works: {inst[1]:,}, Citations: {inst[2]:,}, H-Index: {inst[3]}")

# Check if we have topic/technology domain data
print("\n" + "="*80)
print("RESEARCH FOCUS AREAS")
print("="*80 + "\n")

cur.execute('''
    SELECT technology_domain, COUNT(*) as works
    FROM openalex_works
    WHERE technology_domain IS NOT NULL
    GROUP BY technology_domain
    ORDER BY works DESC
    LIMIT 10
''')

tech_domains = cur.fetchall()
if tech_domains:
    print("Top Technology Domains:")
    for domain, count in tech_domains:
        print(f"  • {domain}: {count:,} works")
else:
    print("  (Technology domain classification not available)")

# Generate summary report
print("\n" + "="*80)
print("ACADEMIC COLLABORATION SUMMARY BY COUNTRY")
print("="*80 + "\n")

print(f"{'Country':<25} {'Institutions':<12} {'Works':<12} {'Citations':<12} {'Avg H-Index':<12}")
print("-" * 85)

for stat in sorted(collaboration_stats, key=lambda x: x['total_works'], reverse=True):
    print(f"{stat['country_name']:<25} {stat['institutions']:<12,} {stat['total_works']:<12,} "
          f"{stat['total_citations']:<12,} {stat['avg_h_index']:<12}")

print("-" * 85)
total_inst = sum(c['institutions'] for c in collaboration_stats)
total_works = sum(c['total_works'] for c in collaboration_stats)
total_cites = sum(c['total_citations'] for c in collaboration_stats)
avg_h = sum(c['avg_h_index'] * c['institutions'] for c in collaboration_stats) / total_inst if total_inst > 0 else 0

print(f"{'TOTAL':<25} {total_inst:<12,} {total_works:<12,} {total_cites:<12,} {avg_h:<12.1f}")

# Save detailed report
report = {
    'generated_date': date.today().isoformat(),
    'total_countries': len(collaboration_stats),
    'total_institutions': total_inst,
    'total_collaborative_works': total_works,
    'total_citations': total_cites,
    'countries_covered': len(collaboration_stats),
    'countries_total': 28,
    'coverage_percentage': round(len(collaboration_stats) / 28 * 100, 1),
    'country_statistics': collaboration_stats,
    'top_institutions_by_works': [],
    'top_institutions_by_citations': [],
    'top_institutions_by_h_index': []
}

# Top institutions overall
cur.execute('''
    SELECT country_code, name, city, works_count, cited_by_count, h_index
    FROM openalex_entities
    WHERE entity_type = 'institution'
    ORDER BY works_count DESC
    LIMIT 20
''')

for row in cur.fetchall():
    report['top_institutions_by_works'].append({
        'country': row[0],
        'name': row[1],
        'city': row[2],
        'works': row[3],
        'citations': row[4],
        'h_index': row[5]
    })

# Save JSON report
output_path = Path('analysis/academic_collaboration_summary.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✓ Detailed report saved to: {output_path}")

# Check for high-risk collaborations
print("\n" + "="*80)
print("HIGH-RISK COLLABORATION ASSESSMENT")
print("="*80 + "\n")

cur.execute('''
    SELECT COUNT(*) FROM openalex_china_high_risk
''')
high_risk_count = cur.fetchone()[0]

if high_risk_count > 0:
    print(f"High-risk collaborations flagged: {high_risk_count:,}")

    cur.execute('''
        SELECT country_code, COUNT(*) as count
        FROM openalex_entities
        WHERE risk_score > 50
        GROUP BY country_code
        ORDER BY count DESC
        LIMIT 10
    ''')

    risk_by_country = cur.fetchall()
    if risk_by_country:
        print("\nCountries with high-risk institutions:")
        for cc, count in risk_by_country:
            print(f"  {country_names.get(cc, cc)}: {count:,} institutions")
else:
    print("(Risk assessment data not available)")

print("\n" + "="*80)
print("INTEGRATION RECOMMENDATIONS")
print("="*80 + "\n")

print("Next steps to integrate academic collaboration into bilateral framework:")
print()
print("1. CREATE ACADEMIC_COLLABORATION_EVENTS table:")
print("   - Link research partnerships to bilateral_events")
print("   - Add major collaborative projects (Horizon Europe, bilateral programs)")
print("   - Track university partnership agreements")
print()
print("2. ADD SISTER CITY RELATIONSHIPS:")
print("   - Create sister_cities table")
print("   - Link to bilateral_events timeline")
print("   - Document cultural exchange programs")
print()
print("3. DOCUMENT JOINT FUNDING PROGRAMS:")
print("   - Horizon Europe projects with Chinese partners")
print("   - National bilateral research funds")
print("   - Industry-academia collaboration programs")
print()
print("4. CREATE COMPREHENSIVE UNIVERSITY PARTNERSHIPS:")
print("   - Student exchange agreements")
print("   - Joint degree programs")
print("   - Confucius Institutes (and closures)")
print("   - Faculty exchange programs")
print()
print("5. INTEGRATE WITH BILATERAL EVENTS TIMELINE:")
print("   - Add academic milestones to event timeline")
print("   - Cross-reference with technology restrictions")
print("   - Identify academic collaboration gaps after diplomatic incidents")
print()

print("=" * 80)
print("✓ ACADEMIC COLLABORATION ANALYSIS COMPLETE")
print("=" * 80)
print(f"\n{len(collaboration_stats)}/28 countries have China research collaborations")
print(f"{total_inst:,} European institutions involved")
print(f"{total_works:,} collaborative research works")
print(f"{total_cites:,} total citations")
print("\nReady to integrate into bilateral relations framework!")

conn.close()
