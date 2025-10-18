#!/usr/bin/env python3
"""
TED Batch Processor for Italy-China Analysis
Processes multiple TED archives efficiently
"""

import json
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import logging
import re
from collections import defaultdict
import concurrent.futures
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TEDBatchProcessor:
    def __init__(self):
        self.base_path = Path("F:/TED_Data/monthly")
        self.output_path = Path("data/processed/ted_italy_analysis")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Simplified patterns for faster processing
        self.italy_pattern = re.compile(r'\b(ital|rome|milan|turin|naples|bologna|leonardo|fincantieri|stmicro)', re.IGNORECASE)
        self.china_pattern = re.compile(r'\b(china|chinese|beijing|shanghai|huawei|zte|alibaba|tencent)', re.IGNORECASE)
        self.dual_use_pattern = re.compile(r'\b(quantum|crypto|semiconductor|artificial intelligence|5g|6g|radar|satellite|drone|nuclear)', re.IGNORECASE)

        self.results = {
            'processed_files': 0,
            'italy_contracts': [],
            'china_mentions': [],
            'dual_use_contracts': [],
            'high_risk': []
        }

    def process_single_file(self, file_content: bytes, filename: str) -> dict:
        """Process a single XML file from archive"""
        try:
            # Quick text search first (faster than full XML parsing)
            text = file_content.decode('utf-8', errors='ignore')

            italy_match = self.italy_pattern.search(text)
            if not italy_match:
                return None

            china_match = self.china_pattern.search(text)
            dual_use_match = self.dual_use_pattern.search(text)

            result = {
                'file': filename,
                'italy': True,
                'china': bool(china_match),
                'dual_use': bool(dual_use_match),
                'high_risk': bool(china_match and dual_use_match)
            }

            # Extract key fields if high interest
            if result['china'] or result['dual_use']:
                try:
                    root = ET.fromstring(file_content)

                    # Extract basic contract info
                    result['details'] = {
                        'title': self._extract_text(root, './/TITLE_CONTRACT', text),
                        'authority': self._extract_text(root, './/NAME_ADDRESSES_CONTACT_CONTRACT_AUTHORITY', text),
                        'value': self._extract_text(root, './/VALUE_COST', text),
                        'cpv': self._extract_text(root, './/CPV_MAIN', text),
                        'date': self._extract_text(root, './/DT_DISPATCH', text)
                    }
                except:
                    # If XML parsing fails, use regex extraction
                    result['details'] = self._extract_with_regex(text)

            return result

        except Exception as e:
            return None

    def _extract_text(self, root, xpath, fallback_text):
        """Extract text from XML with fallback"""
        try:
            elem = root.find(xpath)
            if elem is not None and elem.text:
                return elem.text[:200]  # Limit length
        except:
            pass
        return ""

    def _extract_with_regex(self, text):
        """Fallback regex extraction"""
        details = {}

        # Try to extract title
        title_match = re.search(r'<TITLE[^>]*>([^<]+)</TITLE>', text)
        if title_match:
            details['title'] = title_match.group(1)[:200]

        # Try to extract value
        value_match = re.search(r'<VALUE[^>]*>([^<]+)</VALUE>', text)
        if value_match:
            details['value'] = value_match.group(1)

        return details

    def process_archive(self, archive_path: Path) -> dict:
        """Process a single monthly archive"""
        logger.info(f"Processing {archive_path.name}")

        month_stats = {
            'archive': archive_path.name,
            'total_files': 0,
            'italy_contracts': 0,
            'china_mentions': 0,
            'dual_use': 0,
            'high_risk': 0,
            'contracts': []
        }

        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                members = tar.getmembers()

                # Process in batches
                batch_size = 100
                for i in range(0, len(members), batch_size):
                    batch = members[i:i+batch_size]

                    for member in batch:
                        if member.isfile() and member.name.endswith('.xml'):
                            try:
                                f = tar.extractfile(member)
                                if f:
                                    content = f.read()
                                    result = self.process_single_file(content, member.name)

                                    if result:
                                        month_stats['total_files'] += 1
                                        month_stats['italy_contracts'] += 1

                                        if result['china']:
                                            month_stats['china_mentions'] += 1
                                            self.results['china_mentions'].append(result)

                                        if result['dual_use']:
                                            month_stats['dual_use'] += 1
                                            self.results['dual_use_contracts'].append(result)

                                        if result['high_risk']:
                                            month_stats['high_risk'] += 1
                                            self.results['high_risk'].append(result)
                                            month_stats['contracts'].append(result)
                            except:
                                continue

                    # Log progress
                    if (i + batch_size) % 1000 == 0:
                        logger.info(f"  Processed {i + batch_size}/{len(members)} files")

        except Exception as e:
            logger.error(f"Error processing {archive_path}: {e}")

        logger.info(f"  Found: {month_stats['italy_contracts']} IT contracts, "
                   f"{month_stats['china_mentions']} CN mentions, "
                   f"{month_stats['high_risk']} high risk")

        return month_stats

    def process_year(self, year: int, months: list = None):
        """Process multiple months of TED data"""
        year_path = self.base_path / str(year)

        if not year_path.exists():
            logger.error(f"Year path not found: {year_path}")
            return

        if months is None:
            months = range(1, 13)

        all_results = []

        for month in months:
            archive_name = f"TED_monthly_{year}_{month:02d}.tar.gz"
            archive_path = year_path / archive_name

            if archive_path.exists():
                month_stats = self.process_archive(archive_path)
                all_results.append(month_stats)

                # Save intermediate results
                self.save_month_results(year, month, month_stats)
            else:
                logger.warning(f"Archive not found: {archive_path}")

        # Save consolidated results
        self.save_year_results(year, all_results)

        return all_results

    def save_month_results(self, year: int, month: int, stats: dict):
        """Save results for a single month"""
        output_file = self.output_path / f"ted_{year}_{month:02d}_results.json"

        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info(f"Saved results to {output_file}")

    def save_year_results(self, year: int, all_results: list):
        """Save consolidated year results"""
        summary = {
            'year': year,
            'months_processed': len(all_results),
            'total_italy_contracts': sum(r['italy_contracts'] for r in all_results),
            'total_china_mentions': sum(r['china_mentions'] for r in all_results),
            'total_dual_use': sum(r['dual_use'] for r in all_results),
            'total_high_risk': sum(r['high_risk'] for r in all_results),
            'monthly_breakdown': all_results
        }

        output_file = self.output_path / f"ted_{year}_summary.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Save high-risk contracts separately
        if self.results['high_risk']:
            high_risk_file = self.output_path / f"ted_{year}_high_risk_contracts.json"
            with open(high_risk_file, 'w') as f:
                json.dump(self.results['high_risk'], f, indent=2)

        logger.info(f"\nYear {year} Summary:")
        logger.info(f"  Total Italy Contracts: {summary['total_italy_contracts']:,}")
        logger.info(f"  China Mentions: {summary['total_china_mentions']}")
        logger.info(f"  Dual-Use Contracts: {summary['total_dual_use']}")
        logger.info(f"  High-Risk Contracts: {summary['total_high_risk']}")

def main():
    processor = TEDBatchProcessor()

    # Process 2024 Q3-Q4 (most recent data)
    logger.info("="*60)
    logger.info("TED BATCH PROCESSING - ITALY-CHINA ANALYSIS")
    logger.info("="*60)

    # Start with recent months that are complete
    logger.info("\nProcessing 2024 Q3 (July-September)...")
    results_2024 = processor.process_year(2024, months=[7, 8, 9])

    # If successful, process more
    if results_2024:
        logger.info("\nProcessing 2024 Q2 (April-June)...")
        processor.process_year(2024, months=[4, 5, 6])

    logger.info("\n" + "="*60)
    logger.info("PROCESSING COMPLETE")
    logger.info(f"Results saved to: {processor.output_path}")
    logger.info("="*60)

if __name__ == "__main__":
    main()
