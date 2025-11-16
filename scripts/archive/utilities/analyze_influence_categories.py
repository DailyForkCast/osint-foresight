#!/usr/bin/env python3
"""
Deep Dive Analysis: Chinese Influence Categories in TED
Analyze 17+1 Initiative, China Cooperation, Trade Events, and INTPA contracts
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("\n" + "="*80)
print("CHINESE INFLUENCE CATEGORIES - DEEP DIVE ANALYSIS")
print("="*80)
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all influence contracts (excluding BRI which we know is now 0)
influence_contracts = cursor.execute("""
    SELECT
        id, notice_number, publication_date,
        ca_name, ca_country,
        contractor_name, contractor_country,
        contract_title,
        SUBSTR(contract_description, 1, 1000) as description,
        value_total, currency,
        influence_category, influence_priority, influence_patterns
    FROM ted_contracts_production
    WHERE influence_category IS NOT NULL
    AND influence_category != 'BRI_RELATED'
    ORDER BY influence_category, publication_date DESC
""").fetchall()

print(f"Total influence contracts found: {len(influence_contracts)}")
print()

# Organize by category
by_category = defaultdict(list)
for row in influence_contracts:
    contract_id, notice, pub_date, ca_name, ca_country, contractor, contractor_country, \
        title, description, value, currency, category, priority, patterns = row

    by_category[category].append({
        'id': contract_id,
        'notice': notice,
        'date': pub_date,
        'ca_name': ca_name,
        'ca_country': ca_country,
        'contractor': contractor,
        'contractor_country': contractor_country,
        'title': title,
        'description': description,
        'value': value,
        'currency': currency,
        'priority': priority,
        'patterns': patterns
    })

# Analysis by category
print("="*80)
print("BREAKDOWN BY INFLUENCE CATEGORY")
print("="*80)
for category, contracts in sorted(by_category.items()):
    print(f"\n{category}: {len(contracts)} contracts")

print()

# Detailed analysis of each category
categories_to_analyze = ['17PLUS1_INITIATIVE', 'CHINA_COOPERATION', 'TRADE_EVENT', 'INTPA_RADAR']

full_report = {
    'timestamp': datetime.now().isoformat(),
    'total_contracts': len(influence_contracts),
    'categories': {}
}

for category_name in categories_to_analyze:
    contracts = by_category.get(category_name, [])

    if not contracts:
        print(f"\n{'='*80}")
        print(f"{category_name}: NO CONTRACTS FOUND")
        print(f"{'='*80}\n")
        continue

    print(f"\n{'='*80}")
    print(f"{category_name}: {len(contracts)} CONTRACTS")
    print(f"{'='*80}\n")

    # Geographic analysis
    by_country = Counter(c['ca_country'] for c in contracts if c['ca_country'])
    print(f"Geographic Distribution:")
    for country, count in by_country.most_common():
        print(f"  {country}: {count} contracts ({count/len(contracts)*100:.1f}%)")
    print()

    # Temporal analysis
    by_year = Counter()
    for c in contracts:
        if c['date']:
            year = c['date'][:4]
            by_year[year] += 1

    if by_year:
        print(f"Temporal Distribution:")
        for year in sorted(by_year.keys()):
            print(f"  {year}: {by_year[year]} contracts")
        print()

    # Value analysis
    valued_contracts = [c for c in contracts if c['value'] and c['value'] > 0]
    if valued_contracts:
        total_eur = sum(c['value'] for c in valued_contracts if c['currency'] == 'EUR')
        print(f"Value Analysis:")
        print(f"  Contracts with value: {len(valued_contracts)}/{len(contracts)}")
        print(f"  Total EUR value: €{total_eur:,.0f}")
        print()

    # Top contracting authorities
    ca_counts = Counter(c['ca_name'] for c in contracts if c['ca_name'])
    if ca_counts:
        print(f"Top Contracting Authorities:")
        for ca, count in ca_counts.most_common(5):
            ca_safe = ca[:60].encode('ascii', errors='replace').decode('ascii')
            print(f"  {ca_safe}: {count}")
        print()

    # Individual contract details
    print(f"Individual Contracts:")
    print(f"{'-'*80}")

    for i, contract in enumerate(contracts[:10], 1):  # Show up to 10
        title_safe = (contract['title'][:70] or '').encode('ascii', errors='replace').decode('ascii')
        print(f"\n[{i}] {title_safe}")
        print(f"    ID: {contract['id']}")
        print(f"    Date: {contract['date']}")
        ca_safe = (contract['ca_name'] or 'N/A')[:60].encode('ascii', errors='replace').decode('ascii')
        print(f"    CA: {ca_safe} ({contract['ca_country']})")
        contractor_safe = (contract['contractor'] or 'N/A')[:50].encode('ascii', errors='replace').decode('ascii')
        print(f"    Contractor: {contractor_safe}")
        if contract['contractor_country']:
            print(f"    Contractor Country: {contract['contractor_country']}")
        if contract['value']:
            print(f"    Value: {contract['value']:,.0f} {contract['currency'] or 'N/A'}")
        print(f"    Priority: {contract['priority']}")

        # Show description snippet
        if contract['description']:
            desc = (contract['description'].replace('\n', ' ')[:200]).encode('ascii', errors='replace').decode('ascii')
            print(f"    Description: {desc}...")

    if len(contracts) > 10:
        print(f"\n    ... and {len(contracts) - 10} more contracts")

    print()

    # Save to report
    full_report['categories'][category_name] = {
        'count': len(contracts),
        'countries': dict(by_country),
        'years': dict(by_year),
        'valued_contracts': len(valued_contracts) if valued_contracts else 0,
        'total_eur_value': total_eur if valued_contracts else 0,
        'top_cas': [(ca, count) for ca, count in ca_counts.most_common(5)],
        'contracts': [{
            'id': c['id'],
            'date': c['date'],
            'ca_name': c['ca_name'],
            'ca_country': c['ca_country'],
            'contractor': c['contractor'],
            'title': c['title'],
            'value': c['value'],
            'currency': c['currency']
        } for c in contracts]
    }

# Strategic Assessment
print("\n" + "="*80)
print("STRATEGIC ASSESSMENT")
print("="*80)
print()

print("17+1 Initiative (China-CEEC):")
if '17PLUS1_INITIATIVE' in by_category:
    contracts = by_category['17PLUS1_INITIATIVE']
    ceec_countries = {'BG', 'HR', 'CZ', 'EE', 'GR', 'HU', 'LV', 'LT', 'PL', 'RO', 'SK', 'SI', 'AL', 'BA', 'ME', 'MK', 'RS'}
    ceec_contracts = [c for c in contracts if c['ca_country'] in ceec_countries]
    print(f"  Total contracts: {len(contracts)}")
    print(f"  In CEEC countries: {len(ceec_contracts)} ({len(ceec_contracts)/len(contracts)*100:.1f}%)")
    print(f"  Assessment: {'Aligned with 17+1 geography' if len(ceec_contracts) > len(contracts)*0.5 else 'Geographic mismatch - review needed'}")
else:
    print("  No contracts found")
print()

print("China Cooperation Programs:")
if 'CHINA_COOPERATION' in by_category:
    contracts = by_category['CHINA_COOPERATION']
    print(f"  Total contracts: {len(contracts)}")
    print(f"  Assessment: Direct EU-China cooperation initiatives")
else:
    print("  No contracts found")
print()

print("Trade Events:")
if 'TRADE_EVENT' in by_category:
    contracts = by_category['TRADE_EVENT']
    print(f"  Total contracts: {len(contracts)}")
    print(f"  Assessment: China-focused trade promotion activities")
else:
    print("  No contracts found")
print()

print("INTPA Radar:")
if 'INTPA_RADAR' in by_category:
    contracts = by_category['INTPA_RADAR']
    print(f"  Total contracts: {len(contracts)}")
    print(f"  Assessment: European Commission International Partnerships contracts")
    print(f"  Note: Not necessarily China-focused, but worth monitoring for China mentions")
else:
    print("  No contracts found")

# Save report
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_file = Path(f"analysis/influence_categories_deep_dive_{timestamp}.json")

with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(full_report, f, indent=2, default=str)

print()
print(f"\nFull report saved to: {report_file}")

conn.close()

print()
print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
