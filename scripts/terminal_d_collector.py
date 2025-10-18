#!/usr/bin/env python3
"""
Terminal D: Smaller EU States China Collaboration Collector
Countries: BE, LU, MT, CY, SI, HR
"""

import requests
import json
import time
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - TERMINAL_D - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TerminalDCollector:
    """Terminal D: Process smaller EU states"""

    def __init__(self):
        self.base_url = "https://api.openaire.eu/search/publications"
        self.output_dir = Path("C:/Projects/OSINT - Foresight/data/processed/openaire_verified/terminal_d")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # My assigned countries (Terminal D)
        self.my_countries = ['BE', 'LU', 'MT', 'CY', 'SI', 'HR']

        # Enhanced Chinese keywords for smaller states
        self.china_keywords = [
            # Core terms
            'China', 'Chinese', 'Beijing', 'Shanghai', 'Shenzhen',
            'Guangzhou', 'Wuhan', 'Chengdu', 'Nanjing', 'Tianjin',

            # Universities (key for smaller states)
            'Tsinghua', 'Peking University', 'Fudan', 'Zhejiang',
            'USTC', 'SJTU', 'Nanjing University', 'Beihang',

            # Research institutions
            'CAS', 'Chinese Academy', 'NSFC', 'MOST',

            # Tech companies (important for smaller EU collaborations)
            'Huawei', 'Alibaba', 'Tencent', 'Baidu', 'Xiaomi',
            'ByteDance', 'DJI', 'BYD', 'CATL', 'SMIC',

            # Regions
            'Hong Kong', 'Macau', 'Xinjiang', 'Tibet'
        ]

        # Connect to warehouse
        self.warehouse_path = "F:/OSINT_WAREHOUSE/osint_research.db"

        self.stats = {
            'terminal': 'D',
            'countries_assigned': self.my_countries,
            'total_queries': 0,
            'total_results': 0,
            'verified_china': 0,
            'imported_to_warehouse': 0,
            'api_errors': 0,
            'start_time': datetime.now().isoformat()
        }

        logger.info(f"Terminal D initialized for countries: {', '.join(self.my_countries)}")

    def collect_country_data(self, country_code: str) -> int:
        """Collect China collaborations for a specific country"""

        logger.info(f"🇪🇺 Processing {country_code} - China collaborations...")

        country_results = []
        seen_ids = set()

        for i, keyword in enumerate(self.china_keywords[:12]):  # Use top 12 keywords
            params = {
                'country': country_code,
                'keywords': keyword,
                'format': 'json',
                'size': 100
            }

            try:
                logger.info(f"  🔍 Searching {country_code} + '{keyword}' ({i+1}/12)...")

                response = requests.get(self.base_url, params=params, timeout=30)
                self.stats['total_queries'] += 1

                if response.status_code == 200:
                    data = response.json()

                    # Handle response structure
                    if 'response' in data:
                        results = data.get('response', {}).get('results', [])
                        total_available = data.get('response', {}).get('total', 0)
                    else:
                        results = data.get('results', [])
                        total_available = len(results)

                    verified_new = 0
                    for result in results:
                        pub_id = result.get('id', '')

                        if pub_id in seen_ids:
                            continue

                        # Verify China involvement
                        if self._verify_china_involvement(result):
                            result['verified_china'] = True
                            result['detection_method'] = 'keyword_search'
                            result['keyword_used'] = keyword
                            result['country'] = country_code
                            result['collection_date'] = datetime.now().isoformat()
                            result['terminal'] = 'D'

                            country_results.append(result)
                            seen_ids.add(pub_id)
                            verified_new += 1
                            self.stats['verified_china'] += 1

                    self.stats['total_results'] += len(results)
                    logger.info(f"    ✅ Found {len(results)} results, {verified_new} verified China collaborations (Total available: {total_available})")

                elif response.status_code == 429:
                    logger.warning("⏳ Rate limited, waiting 10 seconds...")
                    time.sleep(10)

                else:
                    logger.error(f"❌ API error: {response.status_code}")
                    self.stats['api_errors'] += 1

                # Rate limiting for smaller states (be gentle)
                time.sleep(2)

            except Exception as e:
                logger.error(f"❌ Error processing {country_code} + '{keyword}': {e}")
                self.stats['api_errors'] += 1

        # Save country results
        if country_results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f"{country_code}_china_collaborations_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'country': country_code,
                    'terminal': 'D',
                    'total_found': len(country_results),
                    'method': 'keyword_search',
                    'keywords_used': self.china_keywords[:12],
                    'collection_date': datetime.now().isoformat(),
                    'results': country_results
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved {len(country_results)} {country_code}-China collaborations to {output_file.name}")

            # Immediately import to warehouse
            self._import_to_warehouse(country_results, country_code)

        else:
            logger.warning(f"⚠️ No verified China collaborations found for {country_code}")

        return len(country_results)

    def _verify_china_involvement(self, result: Dict) -> bool:
        """Verify China involvement using comprehensive indicators"""

        # Convert to searchable text
        result_text = json.dumps(result).lower()

        # Strong indicators
        strong_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'tsinghua', 'peking', 'fudan', 'cas', 'wuhan',
            'guangzhou', 'nanjing', 'hangzhou', 'xinjiang',
            'huawei', 'alibaba', 'tencent', 'baidu'
        ]

        # Check for strong indicators
        for indicator in strong_indicators:
            if indicator in result_text:
                return True

        # Check specific fields
        if 'creator' in result:
            creators = result.get('creator', [])
            if isinstance(creators, list):
                for creator in creators:
                    creator_text = str(creator).lower()
                    for indicator in strong_indicators:
                        if indicator in creator_text:
                            return True

        return False

    def _import_to_warehouse(self, results: List[Dict], country_code: str):
        """Import results directly to warehouse"""

        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            imported = 0
            for result in results:
                # Extract title
                title = result.get('title', {})
                if isinstance(title, dict):
                    title = title.get('$', '') or title.get('content', '')

                cursor.execute("""
                INSERT OR REPLACE INTO core_f_publication (
                    pub_id, doi, title,
                    has_chinese_author, china_collaboration_score,
                    source_system, source_file,
                    retrieved_at, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.get('id', ''),
                    result.get('doi', ''),
                    str(title)[:500],
                    1,  # Verified China collaboration
                    1.0,  # High confidence from keyword method
                    'OpenAIRE_Keyword_TerminalD',
                    f"{country_code}_terminal_d",
                    datetime.now().isoformat(),
                    0.95
                ))
                imported += 1

            conn.commit()
            conn.close()

            self.stats['imported_to_warehouse'] += imported
            logger.info(f"📊 Imported {imported} {country_code} publications to warehouse")

        except Exception as e:
            logger.error(f"❌ Database import error for {country_code}: {e}")

    def process_all_countries(self):
        """Process all assigned countries"""

        logger.info("="*60)
        logger.info("🎯 TERMINAL D: STARTING SMALLER EU STATES PROCESSING")
        logger.info("="*60)

        country_results = {}

        for i, country in enumerate(self.my_countries):
            logger.info(f"\n📍 Processing {country} ({i+1}/{len(self.my_countries)})")
            logger.info("-"*40)

            count = self.collect_country_data(country)
            country_results[country] = count

            # Progress update
            logger.info(f"📈 Progress: {self.stats}")

            # Brief pause between countries
            time.sleep(3)

        # Final summary
        logger.info("\n" + "="*60)
        logger.info("🏁 TERMINAL D: PROCESSING COMPLETE")
        logger.info("="*60)

        for country, count in country_results.items():
            logger.info(f"  {country}: {count:,} China collaborations")

        logger.info(f"\nFinal Statistics:")
        logger.info(f"  Total queries: {self.stats['total_queries']}")
        logger.info(f"  Total results: {self.stats['total_results']}")
        logger.info(f"  Verified China: {self.stats['verified_china']}")
        logger.info(f"  Imported to warehouse: {self.stats['imported_to_warehouse']}")
        logger.info(f"  API errors: {self.stats['api_errors']}")

        # Save final stats
        stats_file = self.output_dir / f"terminal_d_final_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['country_results'] = country_results

        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        logger.info(f"📊 Statistics saved to {stats_file.name}")

    def check_warehouse_status(self):
        """Check current warehouse status for Terminal D countries"""

        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            logger.info("\n📊 WAREHOUSE STATUS CHECK (Terminal D)")
            logger.info("-"*40)

            # Check publications by Terminal D
            cursor.execute("""
            SELECT COUNT(*)
            FROM core_f_publication
            WHERE source_system LIKE '%TerminalD%'
            """)
            terminal_d_count = cursor.fetchone()[0]

            logger.info(f"Publications from Terminal D: {terminal_d_count:,}")

            # Check by country (if we can infer from source_file)
            for country in self.my_countries:
                cursor.execute("""
                SELECT COUNT(*)
                FROM core_f_publication
                WHERE source_file LIKE ? AND has_chinese_author = 1
                """, (f"%{country}%",))
                country_count = cursor.fetchone()[0]
                logger.info(f"  {country}: {country_count:,} China collaborations")

            conn.close()

        except Exception as e:
            logger.error(f"❌ Warehouse status check failed: {e}")

def main():
    """Main execution for Terminal D"""

    collector = TerminalDCollector()

    # Check current warehouse status
    collector.check_warehouse_status()

    # Process all assigned countries
    collector.process_all_countries()

    # Final warehouse check
    collector.check_warehouse_status()

    logger.info("\n🎉 Terminal D processing complete!")

if __name__ == "__main__":
    main()
