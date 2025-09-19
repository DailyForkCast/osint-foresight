#!/usr/bin/env python3
"""
Extract specific China-related contracts from TED data
Very focused, fast extraction
"""

import tarfile
import json
import re
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_china_contracts():
    """Quick extraction of China-related Italian contracts"""

    ted_path = Path("F:/TED_Data/monthly")
    output_dir = Path("data/processed/ted_china_contracts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Very specific China company names to find
    china_companies = [
        'huawei', 'zte', 'lenovo', 'xiaomi', 'oppo', 'vivo',
        'alibaba', 'tencent', 'baidu', 'bytedance', 'jd.com',
        'china telecom', 'china mobile', 'china unicom',
        'haier', 'hisense', 'tcl', 'boe technology',
        'smic', 'catl', 'byd', 'geely', 'great wall',
        'sinopharm', 'sinovac', 'fosun', 'wanda',
        'state grid', 'cnpc', 'sinopec', 'cnooc'
    ]

    critical_items = [
        'semiconductor', 'microchip', 'processor', 'integrated circuit',
        '5g equipment', 'telecom', 'network infrastructure',
        'solar panel', 'wind turbine', 'battery', 'lithium',
        'rare earth', 'medical equipment', 'ventilator', 'ppe',
        'surveillance', 'camera', 'facial recognition'
    ]

    found_contracts = []

    # Just scan 2023-2024 for recent patterns
    target_files = [
        "2024/TED_monthly_2024_01.tar.gz",
        "2024/TED_monthly_2024_04.tar.gz",
        "2023/TED_monthly_2023_01.tar.gz",
        "2023/TED_monthly_2023_06.tar.gz",
        "2022/TED_monthly_2022_01.tar.gz"
    ]

    for file_path in target_files:
        full_path = ted_path / file_path
        if not full_path.exists():
            continue

        logger.info(f"Scanning {file_path}")

        try:
            with tarfile.open(full_path, 'r:gz') as tar:
                # Just check first 1000 files for speed
                members = tar.getmembers()[:1000]

                for member in members:
                    if not member.name.endswith('.xml'):
                        continue

                    try:
                        f = tar.extractfile(member)
                        if f:
                            content = f.read().decode('utf-8', errors='ignore')

                            # Quick Italy check
                            if 'IT' not in content[:5000] and 'Italy' not in content[:5000]:
                                continue

                            content_lower = content.lower()

                            # Check for China companies
                            china_found = None
                            for company in china_companies:
                                if company in content_lower:
                                    china_found = company
                                    break

                            # Check for critical items
                            critical_found = None
                            for item in critical_items:
                                if item in content_lower:
                                    critical_found = item
                                    break

                            if china_found or critical_found:
                                # Extract key details
                                contract = {
                                    'file': member.name,
                                    'date': file_path,
                                    'china_company': china_found,
                                    'critical_item': critical_found
                                }

                                # Try to extract title
                                title_match = re.search(r'<TITLE[^>]*>([^<]+)</TITLE>', content)
                                if title_match:
                                    contract['title'] = title_match.group(1)[:200]

                                # Try to extract authority
                                auth_match = re.search(r'<OFFICIALNAME>([^<]+)</OFFICIALNAME>', content)
                                if auth_match:
                                    contract['authority'] = auth_match.group(1)[:200]

                                # Try to extract value
                                value_match = re.search(r'VALUE["\s]+CURRENCY[^>]*>([0-9.]+)', content)
                                if value_match:
                                    contract['value'] = value_match.group(1)

                                found_contracts.append(contract)
                                logger.info(f"Found: {china_found or critical_found} - {contract.get('title', 'Unknown')[:50]}")

                    except Exception as e:
                        continue

        except Exception as e:
            logger.error(f"Error with {file_path}: {e}")

    # Save results
    if found_contracts:
        output_file = output_dir / 'china_contracts_found.json'
        with open(output_file, 'w') as f:
            json.dump(found_contracts, f, indent=2)

        # Create summary
        summary_file = output_dir / 'CHINA_CONTRACTS_SUMMARY.md'
        with open(summary_file, 'w') as f:
            f.write(f"""# China-Related Contracts in Italian Procurement
**Date:** {datetime.now().isoformat()}
**Contracts Found:** {len(found_contracts)}

## Key Findings

### By Chinese Company
""")
            company_counts = {}
            for c in found_contracts:
                if c.get('china_company'):
                    company_counts[c['china_company']] = company_counts.get(c['china_company'], 0) + 1

            for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {company}: {count} contracts\n")

            f.write("\n### By Critical Item\n")
            item_counts = {}
            for c in found_contracts:
                if c.get('critical_item'):
                    item_counts[c['critical_item']] = item_counts.get(c['critical_item'], 0) + 1

            for item, count in sorted(item_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {item}: {count} contracts\n")

            f.write("\n### Sample Contracts\n")
            for c in found_contracts[:10]:
                f.write(f"\n**{c.get('title', 'Unknown')[:100]}**\n")
                f.write(f"- Authority: {c.get('authority', 'Unknown')[:100]}\n")
                f.write(f"- China: {c.get('china_company', 'N/A')}\n")
                f.write(f"- Critical: {c.get('critical_item', 'N/A')}\n")
                f.write(f"- Value: €{c.get('value', 'Unknown')}\n")

    return found_contracts


if __name__ == "__main__":
    print("Extracting China-related contracts from TED data...")
    contracts = extract_china_contracts()
    print(f"\nFound {len(contracts)} China-related contracts")

    if contracts:
        print("\nTop findings:")
        china_companies = set(c.get('china_company') for c in contracts if c.get('china_company'))
        critical_items = set(c.get('critical_item') for c in contracts if c.get('critical_item'))

        print(f"Chinese companies: {', '.join(list(china_companies)[:5])}")
        print(f"Critical items: {', '.join(list(critical_items)[:5])}")
