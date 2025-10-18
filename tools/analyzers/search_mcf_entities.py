#!/usr/bin/env python3
"""
Search for specific Military-Civil Fusion (MCF) entities in USASpending data
These are known Chinese companies with military ties
"""

import re
from pathlib import Path
from datetime import datetime
import json

def search_mcf_entities():
    print("=" * 80)
    print("SEARCHING FOR MILITARY-CIVIL FUSION (MCF) ENTITIES")
    print(f"Start time: {datetime.now()}")
    print("=" * 80)

    # Known MCF entities (companies with PLA/military ties)
    mcf_entities = {
        'huawei': {
            'patterns': [r'\bhuawei\b', r'\bhisilicon\b', r'\bfuturewei\b'],
            'risk': 'CRITICAL',
            'category': 'Telecommunications/5G'
        },
        'zte': {
            'patterns': [r'\bzte\b', r'\bzhongxing\b'],
            'risk': 'CRITICAL',
            'category': 'Telecommunications'
        },
        'hikvision': {
            'patterns': [r'\bhikvision\b', r'\bhangzhou hikvision\b'],
            'risk': 'HIGH',
            'category': 'Surveillance'
        },
        'dahua': {
            'patterns': [r'\bdahua\b', r'\bzhejiang dahua\b'],
            'risk': 'HIGH',
            'category': 'Surveillance'
        },
        'dji': {
            'patterns': [r'\bdji\b', r'\bda-?jiang\b', r'\bsz dji\b'],
            'risk': 'HIGH',
            'category': 'Drones/UAV'
        },
        'smic': {
            'patterns': [r'\bsmic\b', r'\bsemiconductor manufacturing international\b'],
            'risk': 'CRITICAL',
            'category': 'Semiconductors'
        },
        'bgi': {
            'patterns': [r'\bbgi\b', r'\bbeijing genomics\b', r'\bmgi\b'],
            'risk': 'HIGH',
            'category': 'Biotechnology/Genomics'
        },
        'lenovo': {
            'patterns': [r'\blenovo\b', r'\blegend holdings\b'],
            'risk': 'MEDIUM',
            'category': 'Computing/Hardware'
        },
        'alibaba': {
            'patterns': [r'\balibaba\b', r'\baltaba\b', r'\btaobao\b'],
            'risk': 'MEDIUM',
            'category': 'Cloud/E-commerce'
        },
        'tencent': {
            'patterns': [r'\btencent\b', r'\bwechat\b', r'\bweixin\b'],
            'risk': 'MEDIUM',
            'category': 'Software/Gaming'
        },
        'baidu': {
            'patterns': [r'\bbaidu\b'],
            'risk': 'MEDIUM',
            'category': 'AI/Search'
        },
        'bytedance': {
            'patterns': [r'\bbytedance\b', r'\btiktok\b', r'\bdouyin\b'],
            'risk': 'HIGH',
            'category': 'Social Media/AI'
        },
        'nuctech': {
            'patterns': [r'\bnuctech\b', r'\bnuclear technology\b'],
            'risk': 'CRITICAL',
            'category': 'Security Scanning'
        },
        'hytera': {
            'patterns': [r'\bhytera\b'],
            'risk': 'HIGH',
            'category': 'Communications'
        },
        'inspur': {
            'patterns': [r'\binspur\b'],
            'risk': 'HIGH',
            'category': 'Servers/Computing'
        },
        'sugon': {
            'patterns': [r'\bsugon\b', r'\bdawning\b'],
            'risk': 'CRITICAL',
            'category': 'Supercomputing'
        },
        'iflytek': {
            'patterns': [r'\biflytek\b', r'\bkeda\b'],
            'risk': 'HIGH',
            'category': 'AI/Voice Recognition'
        },
        'sensetime': {
            'patterns': [r'\bsensetime\b'],
            'risk': 'HIGH',
            'category': 'AI/Facial Recognition'
        },
        'megvii': {
            'patterns': [r'\bmegvii\b', r'\bface\+\+\b'],
            'risk': 'HIGH',
            'category': 'AI/Facial Recognition'
        },
        'yitu': {
            'patterns': [r'\byitu\b'],
            'risk': 'HIGH',
            'category': 'AI/Surveillance'
        }
    }

    # Defense contractors and state-owned enterprises
    defense_entities = {
        'norinco': {
            'patterns': [r'\bnorinco\b', r'\bnorth industries\b'],
            'risk': 'CRITICAL',
            'category': 'Defense/Weapons'
        },
        'avic': {
            'patterns': [r'\bavic\b', r'\baviation industry corporation\b'],
            'risk': 'CRITICAL',
            'category': 'Aerospace/Defense'
        },
        'casic': {
            'patterns': [r'\bcasic\b', r'\baerospace science\b'],
            'risk': 'CRITICAL',
            'category': 'Missiles/Space'
        },
        'casc': {
            'patterns': [r'\bcasc\b', r'\bchina aerospace\b'],
            'risk': 'CRITICAL',
            'category': 'Space/Satellites'
        },
        'cetc': {
            'patterns': [r'\bcetc\b', r'\bchina electronics technology\b'],
            'risk': 'CRITICAL',
            'category': 'Defense Electronics'
        },
        'cssc': {
            'patterns': [r'\bcssc\b', r'\bshipbuilding corporation\b'],
            'risk': 'CRITICAL',
            'category': 'Naval/Shipbuilding'
        },
        'csic': {
            'patterns': [r'\bcsic\b', r'\bshipbuilding industry\b'],
            'risk': 'CRITICAL',
            'category': 'Naval/Defense'
        }
    }

    # Combine all entities
    all_entities = {**mcf_entities, **defense_entities}

    # Compile patterns
    for entity_name, entity_info in all_entities.items():
        entity_info['compiled'] = [re.compile(p, re.IGNORECASE) for p in entity_info['patterns']]

    # Files to search
    data_files = [
        "5836.dat",  # 124.72 GB
        "5847.dat",  # 126.50 GB
        "5848.dat",  # 222.45 GB - The main target
        "5862.dat"   # 52.05 GB
    ]

    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")

    # Results storage
    findings = {}
    critical_findings = []
    total_mcf_mentions = 0

    for file_name in data_files:
        file_path = base_path / file_name

        if not file_path.exists():
            print(f"Skipping {file_name} - not found")
            continue

        file_size_gb = file_path.stat().st_size / 1e9
        print(f"\nSearching {file_name} ({file_size_gb:.2f} GB)...")
        print("-" * 40)

        file_findings = {}
        lines_checked = 0
        sample_size = 5000000  # Check first 5M lines per file

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    lines_checked += 1

                    if lines_checked % 500000 == 0:
                        print(f"  Checked {lines_checked:,} lines...")

                    line_lower = line.lower()

                    # Check each MCF entity
                    for entity_name, entity_info in all_entities.items():
                        for pattern in entity_info['compiled']:
                            if pattern.search(line_lower):
                                total_mcf_mentions += 1

                                if entity_name not in file_findings:
                                    file_findings[entity_name] = {
                                        'count': 0,
                                        'risk': entity_info['risk'],
                                        'category': entity_info['category'],
                                        'examples': []
                                    }

                                file_findings[entity_name]['count'] += 1

                                # Save examples for critical risks
                                if entity_info['risk'] == 'CRITICAL' and len(file_findings[entity_name]['examples']) < 3:
                                    file_findings[entity_name]['examples'].append({
                                        'line_number': line_num,
                                        'text': line[:300]
                                    })

                                    critical_findings.append({
                                        'entity': entity_name,
                                        'file': file_name,
                                        'line': line_num,
                                        'risk': entity_info['risk'],
                                        'category': entity_info['category']
                                    })

                                break  # Found match, move to next entity

                    if lines_checked >= sample_size:
                        break

        except Exception as e:
            print(f"  Error processing {file_name}: {e}")

        findings[file_name] = file_findings

        # Report file results
        if file_findings:
            print(f"\n  MCF ENTITIES FOUND IN {file_name}:")
            for entity, info in sorted(file_findings.items(), key=lambda x: x[1]['count'], reverse=True):
                print(f"    {entity}: {info['count']} mentions [{info['risk']}] - {info['category']}")

    # Summary report
    print("\n" + "=" * 80)
    print("MCF ENTITY SEARCH SUMMARY")
    print("=" * 80)

    print(f"\nTotal MCF entity mentions found: {total_mcf_mentions:,}")
    print(f"Critical risk findings: {len(critical_findings):,}")

    # Aggregate by entity
    entity_totals = {}
    for file_name, file_findings in findings.items():
        for entity, info in file_findings.items():
            if entity not in entity_totals:
                entity_totals[entity] = {
                    'total': 0,
                    'risk': info['risk'],
                    'category': info['category'],
                    'files': []
                }
            entity_totals[entity]['total'] += info['count']
            entity_totals[entity]['files'].append(file_name)

    # Report top MCF entities
    if entity_totals:
        print("\nTOP MCF ENTITIES BY TOTAL MENTIONS:")
        print("-" * 40)
        sorted_entities = sorted(entity_totals.items(), key=lambda x: x[1]['total'], reverse=True)
        for entity, info in sorted_entities[:20]:
            print(f"  {entity}: {info['total']:,} total")
            print(f"    Risk: {info['risk']} | Category: {info['category']}")
            print(f"    Found in: {', '.join(info['files'])}")

    # Critical risks
    if critical_findings:
        print("\nCRITICAL RISK ENTITIES DETECTED:")
        print("-" * 40)
        critical_entities = set(f['entity'] for f in critical_findings)
        for entity in critical_entities:
            entity_criticals = [f for f in critical_findings if f['entity'] == entity]
            print(f"  {entity}: {len(entity_criticals)} critical mentions")
            print(f"    Category: {entity_criticals[0]['category']}")

    # Save results
    output_file = Path("mcf_entity_search_results.json")
    results = {
        'summary': {
            'total_mcf_mentions': total_mcf_mentions,
            'critical_findings_count': len(critical_findings),
            'entities_found': len(entity_totals)
        },
        'entity_totals': entity_totals,
        'file_details': findings,
        'critical_findings': critical_findings[:100]  # First 100 critical
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    print("\n" + "=" * 80)
    print(f"End time: {datetime.now()}")

    return results

if __name__ == "__main__":
    search_mcf_entities()
