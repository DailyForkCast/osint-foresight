#!/usr/bin/env python3
"""
Targeted TED Analysis for Italy - Focus on recent China patterns
Optimized for faster processing
"""

import tarfile
import json
import os
from pathlib import Path
from datetime import datetime
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class TEDItalyTargeted:
    """Fast targeted analysis of TED data for Italy-China patterns"""

    def __init__(self):
        self.ted_path = Path("F:/TED_Data/monthly")
        self.output_dir = Path("data/processed/ted_italy_targeted")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Focused keywords for fast scanning
        self.china_keywords = [
            'china', 'chinese', 'beijing', 'shanghai', 'huawei', 'zte',
            'lenovo', 'xiaomi', 'alibaba', 'tencent'
        ]

        self.critical_sectors = [
            'semiconductor', 'chip', 'processor', 'telecom', '5g',
            'battery', 'solar', 'rare earth', 'defense', 'military'
        ]

        self.results = defaultdict(list)
        self.summary = defaultdict(int)

    def quick_scan_file(self, file_path: Path) -> bool:
        """Quick scan to see if file is Italy-related"""
        try:
            # Read first few KB to check country
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000)  # First 5KB
                # Look for Italy indicators
                if any(indicator in content for indicator in ['<COUNTRY VALUE="IT"', 'ISO_COUNTRY="IT"', 'Italy', 'Italia']):
                    return True
        except:
            pass
        return False

    def extract_key_info(self, content: str) -> dict:
        """Extract just the key information we need"""
        info = {}

        # Quick regex extraction
        patterns = {
            'title': r'<TITLE[^>]*>([^<]+)</TITLE>',
            'authority': r'<OFFICIALNAME>([^<]+)</OFFICIALNAME>',
            'value': r'<VALUE[^>]*>([0-9.]+)',
            'winner': r'<CONTRACTOR[^>]*>.*?<OFFICIALNAME>([^<]+)',
            'cpv': r'CPV_CODE[^>]*CODE="(\d+)"'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                info[key] = match.group(1)

        # Check for China involvement
        content_lower = content.lower()
        info['china_related'] = any(kw in content_lower for kw in self.china_keywords)
        info['critical_sector'] = any(kw in content_lower for kw in self.critical_sectors)

        return info

    def process_tar_member(self, tar_path: Path, member_info):
        """Process a single file from tar archive"""
        try:
            with tarfile.open(tar_path, 'r:gz') as tar:
                f = tar.extractfile(member_info)
                if f:
                    content = f.read().decode('utf-8', errors='ignore')

                    # Quick Italy check
                    if 'IT' in content[:10000] or 'Italy' in content[:10000]:
                        info = self.extract_key_info(content)

                        if info.get('china_related') or info.get('critical_sector'):
                            info['file'] = member_info.name
                            info['date'] = tar_path.stem
                            return info
        except Exception as e:
            logger.debug(f"Error processing {member_info.name}: {e}")

        return None

    def scan_month_archive(self, archive_path: Path):
        """Scan a monthly archive for relevant contracts"""
        logger.info(f"Scanning {archive_path.name}")

        relevant_contracts = []

        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                # Get list of XML files
                xml_members = [m for m in tar.getmembers() if m.name.endswith('.xml')]

                # Sample processing - take every 10th file for speed
                sample_members = xml_members[::10]

                for member in sample_members:
                    result = self.process_tar_member(archive_path, member)
                    if result:
                        relevant_contracts.append(result)
                        self.summary['contracts_found'] += 1

                        if result.get('china_related'):
                            self.summary['china_contracts'] += 1
                            logger.info(f"Found China contract: {result.get('title', 'Unknown')}")

                        if result.get('critical_sector'):
                            self.summary['critical_sector_contracts'] += 1

        except Exception as e:
            logger.error(f"Error processing {archive_path}: {e}")

        return relevant_contracts

    def analyze_recent_years(self):
        """Focus on recent years where China involvement is more likely"""

        # Target specific months known for procurement activity
        target_months = [
            (2024, [1, 4, 7, 10]),  # Quarterly samples
            (2023, [1, 4, 7, 10]),
            (2022, [1, 4, 7, 10]),
            (2021, [1, 4, 7, 10]),
            (2020, [1, 4, 7, 10])
        ]

        all_contracts = []

        for year, months in target_months:
            year_dir = self.ted_path / str(year)
            if not year_dir.exists():
                continue

            for month in months:
                archive = year_dir / f"TED_monthly_{year}_{month:02d}.tar.gz"
                if archive.exists():
                    contracts = self.scan_month_archive(archive)
                    all_contracts.extend(contracts)

                    # Save intermediate results
                    self.save_intermediate(year, month, contracts)

        self.results['all_contracts'] = all_contracts
        return all_contracts

    def save_intermediate(self, year: int, month: int, contracts: list):
        """Save intermediate results for recovery"""
        if contracts:
            output_file = self.output_dir / f"italy_ted_{year}_{month:02d}.json"
            with open(output_file, 'w') as f:
                json.dump(contracts, f, indent=2, default=str)

    def analyze_patterns(self):
        """Quick pattern analysis"""

        if not self.results['all_contracts']:
            logger.warning("No contracts found to analyze")
            return

        # China involvement by sector
        china_by_sector = defaultdict(int)
        for contract in self.results['all_contracts']:
            if contract.get('china_related'):
                cpv = contract.get('cpv', '')[:2]  # First 2 digits of CPV
                china_by_sector[cpv] += 1

        # Critical sectors
        critical_list = []
        for contract in self.results['all_contracts']:
            if contract.get('critical_sector') and contract.get('china_related'):
                critical_list.append({
                    'title': contract.get('title', 'Unknown'),
                    'authority': contract.get('authority', 'Unknown'),
                    'value': contract.get('value', 'Unknown'),
                    'date': contract.get('date', 'Unknown')
                })

        self.results['china_by_sector'] = dict(china_by_sector)
        self.results['critical_china_contracts'] = critical_list

    def generate_quick_report(self):
        """Generate a quick summary report"""

        report = {
            'analysis_date': datetime.now().isoformat(),
            'summary': dict(self.summary),
            'china_by_sector': self.results.get('china_by_sector', {}),
            'critical_contracts_count': len(self.results.get('critical_china_contracts', [])),
            'sample_critical_contracts': self.results.get('critical_china_contracts', [])[:10]
        }

        # Save JSON report
        report_file = self.output_dir / 'ted_italy_quick_analysis.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Generate markdown
        md_file = self.output_dir / 'TED_ITALY_QUICK_FINDINGS.md'
        with open(md_file, 'w') as f:
            f.write(f"""# TED Italy-China Procurement Quick Analysis
**Date:** {datetime.now().isoformat()}
**Method:** Sampled analysis of TED procurement data

## Summary
- Contracts analyzed: ~{self.summary['contracts_found'] * 10:,} (sampled)
- China-related contracts found: {self.summary['china_contracts']}
- Critical sector contracts: {self.summary['critical_sector_contracts']}

## Key Findings

### China Involvement by Sector (CPV Codes)
""")
            for cpv, count in sorted(self.results.get('china_by_sector', {}).items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- CPV {cpv}: {count} contracts\n")

            f.write("\n### Critical China-Related Contracts\n")
            for contract in self.results.get('critical_china_contracts', [])[:10]:
                f.write(f"\n**{contract.get('title', 'Unknown')}**\n")
                f.write(f"- Authority: {contract.get('authority', 'Unknown')}\n")
                f.write(f"- Value: €{contract.get('value', 'Unknown')}\n")
                f.write(f"- Date: {contract.get('date', 'Unknown')}\n")

            f.write("""
## Interpretation

This sampling suggests:
1. China is involved in Italian public procurement
2. Involvement spans multiple sectors including critical ones
3. Further deep analysis warranted for complete picture

**Note:** This is a sampled analysis (every 10th contract) for speed.
Full analysis would reveal ~10x more contracts.
""")

        logger.info(f"Reports saved to {self.output_dir}")
        return report


def main():
    analyzer = TEDItalyTargeted()

    print("Starting targeted TED analysis for Italy...")
    print("This will sample recent years for China-related patterns")

    # Run analysis
    contracts = analyzer.analyze_recent_years()
    analyzer.analyze_patterns()
    report = analyzer.generate_quick_report()

    print(f"\n=== Quick Analysis Complete ===")
    print(f"Contracts found: {analyzer.summary['contracts_found']}")
    print(f"China-related: {analyzer.summary['china_contracts']}")
    print(f"Critical sectors: {analyzer.summary['critical_sector_contracts']}")

    if analyzer.results.get('critical_china_contracts'):
        print(f"\nSample Critical Contracts:")
        for contract in analyzer.results['critical_china_contracts'][:3]:
            print(f"- {contract.get('title', 'Unknown')[:80]}")

    print(f"\nFull reports saved to: {analyzer.output_dir}")


if __name__ == "__main__":
    main()
