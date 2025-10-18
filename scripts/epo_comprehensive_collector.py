#!/usr/bin/env python3
"""
EPO Comprehensive Patent Collector
Systematic collection of all patents using segmentation strategies
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EPOComprehensiveCollector:
    """Collect comprehensive patent data using segmentation"""

    def __init__(self):
        # Load authentication
        self.auth_config_path = Path("C:/Projects/OSINT - Foresight/config/patent_auth.json")
        self.refresh_token()

        # Output directory
        self.output_dir = Path("F:/OSINT_DATA/epo_comprehensive_collection")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Coverage tracking
        self.coverage_file = self.output_dir / "coverage_tracking.json"
        self.coverage = self.load_coverage()

    def refresh_token(self):
        """Refresh EPO authentication token"""
        import subprocess
        result = subprocess.run(
            ["python", "scripts/epo_auth_from_config.py"],
            capture_output=True,
            text=True,
            cwd="C:/Projects/OSINT - Foresight"
        )

        # Reload token
        with open(self.auth_config_path, 'r') as f:
            config = json.load(f)

        self.access_token = config['epo_ops']['access_token']

        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'User-Agent': 'OSINT-Research-System/1.0'
        })

        self.search_url = "https://ops.epo.org/3.2/rest-services/published-data/search"

    def load_coverage(self) -> Dict:
        """Load coverage tracking data"""
        if self.coverage_file.exists():
            with open(self.coverage_file, 'r') as f:
                return json.load(f)
        return {
            'queries_completed': [],
            'segments_processed': {},
            'total_patents_collected': 0,
            'last_updated': None
        }

    def save_coverage(self):
        """Save coverage tracking data"""
        self.coverage['last_updated'] = datetime.now().isoformat()
        with open(self.coverage_file, 'w') as f:
            json.dump(self.coverage, f, indent=2)

    def execute_query(self, query: str, range_str: str = "1-100") -> Tuple[int, List[Dict]]:
        """Execute a single EPO query and return count and results"""
        try:
            params = {
                'q': query,
                'Range': range_str
            }

            response = self.session.get(self.search_url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                total_count = 0
                patents = []

                if 'ops:world-patent-data' in data:
                    world_data = data['ops:world-patent-data']
                    if 'ops:biblio-search' in world_data:
                        biblio_search = world_data['ops:biblio-search']

                        if '@total-result-count' in biblio_search:
                            total_count = int(biblio_search['@total-result-count'])

                        if 'ops:search-result' in biblio_search:
                            search_results = biblio_search['ops:search-result']
                            if isinstance(search_results, list):
                                patents = search_results
                            elif search_results:
                                patents = [search_results]

                return total_count, patents

            elif response.status_code == 400 and 'invalid_access_token' in response.text:
                logger.info("Token expired, refreshing...")
                self.refresh_token()
                time.sleep(2)
                return self.execute_query(query, range_str)  # Retry

            else:
                logger.error(f"Query failed with status {response.status_code}")
                return 0, []

        except Exception as e:
            logger.error(f"Query exception: {e}")
            return 0, []

    def collect_segmented(self, base_query: str, description: str, max_per_segment: int = 2000):
        """Collect patents using date segmentation for large result sets"""

        print(f"\n{'='*60}")
        print(f"Collecting: {description}")
        print(f"Base query: {base_query}")
        print(f"{'='*60}")

        # First check total count
        total_count, _ = self.execute_query(base_query, "1-1")
        print(f"Total patents found: {total_count:,}")

        if total_count == 0:
            return []

        all_patents = []
        segment_key = f"{base_query}"

        # If already processed, skip
        if segment_key in self.coverage['segments_processed']:
            print(f"Already processed (found in coverage tracking)")
            return []

        # Strategy based on count
        if total_count <= max_per_segment:
            # Can get all in one query (or series of range queries)
            print(f"Retrieving all {total_count} patents...")

            for start in range(1, min(total_count + 1, max_per_segment), 100):
                end = min(start + 99, total_count, max_per_segment)
                range_str = f"{start}-{end}"

                _, patents = self.execute_query(base_query, range_str)
                all_patents.extend(patents)

                print(f"  Retrieved {start}-{end}: {len(patents)} patents")
                time.sleep(1)  # Rate limiting

        else:
            # Need to segment by date
            print(f"Segmenting by date (exceeds {max_per_segment} limit)...")

            # Try yearly segments first
            current_year = 2024
            for year in range(current_year, 2014, -1):  # Last 10 years
                year_query = f"{base_query} AND pd={year}"
                year_count, _ = self.execute_query(year_query, "1-1")

                print(f"\n  Year {year}: {year_count:,} patents")

                if year_count == 0:
                    continue
                elif year_count <= max_per_segment:
                    # Get all for this year
                    for start in range(1, min(year_count + 1, max_per_segment), 100):
                        end = min(start + 99, year_count, max_per_segment)
                        range_str = f"{start}-{end}"

                        _, patents = self.execute_query(year_query, range_str)
                        all_patents.extend(patents)

                        print(f"    Retrieved {start}-{end}: {len(patents)} patents")
                        time.sleep(1)

                else:
                    # Need monthly segments for this year
                    print(f"    Breaking {year} into months...")
                    for month in range(1, 13):
                        month_str = f"{year}{month:02d}"
                        month_query = f"{base_query} AND pd={month_str}"
                        month_count, _ = self.execute_query(month_query, "1-1")

                        if month_count > 0:
                            print(f"      {month_str}: {month_count:,} patents")

                            for start in range(1, min(month_count + 1, max_per_segment), 100):
                                end = min(start + 99, month_count, max_per_segment)
                                range_str = f"{start}-{end}"

                                _, patents = self.execute_query(month_query, range_str)
                                all_patents.extend(patents)
                                time.sleep(1)

        # Save results
        if all_patents:
            filename = f"{description.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.output_dir / filename

            result_data = {
                'description': description,
                'base_query': base_query,
                'total_count_reported': total_count,
                'patents_collected': len(all_patents),
                'collection_time': datetime.now().isoformat(),
                'patents': all_patents
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)

            print(f"\n✓ Collected {len(all_patents)} patents")
            print(f"✓ Saved to: {filepath}")

            # Update coverage
            self.coverage['segments_processed'][segment_key] = {
                'description': description,
                'total_count': total_count,
                'collected': len(all_patents),
                'timestamp': datetime.now().isoformat()
            }
            self.coverage['total_patents_collected'] += len(all_patents)
            self.save_coverage()

        return all_patents

    def run_priority_collection(self):
        """Run collection for priority queries"""

        print("="*60)
        print("EPO Comprehensive Patent Collection")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Priority collection targets
        priority_queries = [
            # Critical Chinese companies (segmented by year)
            ("pa=huawei AND pd=2024", "Huawei 2024"),
            ("pa=huawei AND pd=2023", "Huawei 2023"),
            ("pa=xiaomi AND pd=2024", "Xiaomi 2024"),
            ("pa=xiaomi AND pd=2023", "Xiaomi 2023"),

            # Critical technologies with China
            ("txt=5G AND pa=china AND pd=2023", "5G China 2023"),
            ("txt=quantum AND pa=china AND pd>=2022", "Quantum China Recent"),
            ("txt=semiconductor AND pa=china AND pd=2023", "Semiconductor China 2023"),

            # EU-China joint patents (these are small enough to get all)
            ("pa=china AND pa=germany", "China-Germany Joint"),
            ("pa=china AND pa=france", "China-France Joint"),
            ("pa=china AND pa=italy", "China-Italy Joint"),
            ("pa=huawei AND pa=siemens", "Huawei-Siemens Joint"),
            ("pa=huawei AND pa=nokia", "Huawei-Nokia Joint"),

            # Specific technology areas
            ("txt=\"brain computer interface\" AND pd>=2020", "BCI Recent"),
            ("txt=\"low earth orbit\" AND pa=china", "LEO China"),
            ("txt=CRISPR AND pa=china AND pd>=2022", "CRISPR China Recent"),
        ]

        collection_summary = {
            'start_time': datetime.now().isoformat(),
            'queries_processed': 0,
            'total_patents_collected': 0,
            'segments': []
        }

        for query, description in priority_queries:
            try:
                patents = self.collect_segmented(query, description)

                collection_summary['queries_processed'] += 1
                collection_summary['total_patents_collected'] += len(patents)
                collection_summary['segments'].append({
                    'description': description,
                    'query': query,
                    'patents_collected': len(patents)
                })

                # Rate limiting between major queries
                time.sleep(2)

            except Exception as e:
                logger.error(f"Failed to collect {description}: {e}")
                continue

        # Save summary
        collection_summary['end_time'] = datetime.now().isoformat()

        summary_file = self.output_dir / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(collection_summary, f, indent=2)

        print("\n" + "="*60)
        print("COLLECTION COMPLETE")
        print("="*60)
        print(f"Queries processed: {collection_summary['queries_processed']}")
        print(f"Total patents collected: {collection_summary['total_patents_collected']:,}")
        print(f"Coverage tracking: {self.coverage_file}")
        print(f"Summary saved: {summary_file}")

        return collection_summary

def main():
    collector = EPOComprehensiveCollector()
    collector.run_priority_collection()

if __name__ == "__main__":
    main()
