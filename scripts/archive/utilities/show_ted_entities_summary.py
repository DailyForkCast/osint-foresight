#!/usr/bin/env python3
"""Show summary of TED Chinese entities"""
import json

with open('analysis/ted_chinese_entities_current.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("="*80)
print("TED CHINESE ENTITIES - SUMMARY")
print("="*80)

if 'ted_contractors' in data['entities_by_table']:
    entities = data['entities_by_table']['ted_contractors']
    print(f"\nTotal unique Chinese contractors: {len(entities)}")
    print(f"\nTop 50 by contract count:\n")

    for i, ent in enumerate(entities[:50], 1):
        name = ent['name']
        count = ent['contract_count']
        country = ent.get('country', '')
        print(f"{i:3}. {name:<60} ({count:3} contracts) [{country}]")

    print(f"\n... and {len(entities) - 50} more entities")

    # Show distribution
    print("\n" + "="*80)
    print("DISTRIBUTION BY CONTRACT COUNT")
    print("="*80)

    counts = {}
    for ent in entities:
        c = ent['contract_count']
        if c >= 100:
            key = '100+'
        elif c >= 50:
            key = '50-99'
        elif c >= 20:
            key = '20-49'
        elif c >= 10:
            key = '10-19'
        elif c >= 5:
            key = '5-9'
        else:
            key = '1-4'
        counts[key] = counts.get(key, 0) + 1

    for key in ['100+', '50-99', '20-49', '10-19', '5-9', '1-4']:
        if key in counts:
            print(f"  {key:>10} contracts: {counts[key]:4} entities")

print("\nFull list saved to: analysis/ted_chinese_entities_for_review.csv")
print("  - Column 'decision': KEEP, REMOVE, VERIFY, or leave blank")
print("  - Column 'notes': Add any notes about why")
