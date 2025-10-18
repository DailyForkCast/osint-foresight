#!/usr/bin/env python3
"""
FIXED OpenAIRE collector - corrects the API parsing issue
All terminals should use this version
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FixedOpenAIRECollector:
    """Fixed OpenAIRE collector with correct API parsing"""

    def __init__(self, terminal_id: str = "FIXED"):
        self.base_url = "https://api.openaire.eu/search/publications"
        self.output_dir = Path(f"C:/Projects/OSINT - Foresight/data/processed/openaire_verified/terminal_{terminal_id.lower()}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Enhanced Chinese keywords
        self.china_keywords = [
            'China', 'Chinese', 'Beijing', 'Shanghai', 'Shenzhen',
            'Guangzhou', 'Wuhan', 'Chengdu', 'Nanjing', 'Tianjin',
            'Tsinghua', 'Peking University', 'Fudan', 'Zhejiang',
            'USTC', 'SJTU', 'CAS', 'Chinese Academy',
            'Huawei', 'Alibaba', 'Tencent', 'Baidu', 'Xiaomi'
        ]

        # Warehouse connection
        self.warehouse_path = "F:/OSINT_WAREHOUSE/osint_research.db"

        self.terminal_id = terminal_id
        self.stats = {
            'terminal': terminal_id,
            'total_queries': 0,
            'total_results': 0,
            'verified_china': 0,
            'imported_to_warehouse': 0,
            'api_errors': 0,
            'start_time': datetime.now().isoformat()
        }

        logger.info(f"Fixed OpenAIRE Collector initialized (Terminal {terminal_id})")

    def collect_country_data(self, country_code: str, max_keywords: int = 8) -> int:
        """Collect China collaborations for a country with FIXED parsing"""

        logger.info(f"🔧 FIXED: Processing {country_code} - China collaborations...")

        country_results = []
        seen_ids = set()

        for i, keyword in enumerate(self.china_keywords[:max_keywords]):
            params = {
                'country': country_code,
                'keywords': keyword,
                'format': 'json',
                'size': 50  # Reasonable size for testing
            }

            try:
                logger.info(f"  🔍 Searching {country_code} + '{keyword}' ({i+1}/{max_keywords})...")

                response = requests.get(self.base_url, params=params, timeout=30)
                self.stats['total_queries'] += 1

                if response.status_code == 200:
                    data = response.json()

                    # FIXED: Correct OpenAIRE structure parsing
                    try:
                        if 'response' in data and 'results' in data['response']:
                            results_container = data['response']['results']

                            # OpenAIRE returns results in 'result' key (singular)
                            if isinstance(results_container, dict) and 'result' in results_container:
                                results = results_container['result']
                            else:
                                results = []

                        else:
                            results = []

                        logger.info(f"    ✅ API returned {len(results)} results")

                        verified_new = 0
                        for result in results:
                            if not isinstance(result, dict):
                                continue

                            # Get publication ID
                            pub_id = self._extract_id(result)

                            if not pub_id or pub_id in seen_ids:
                                continue

                            # Verify China involvement
                            if self._verify_china_involvement(result):
                                result['verified_china'] = True
                                result['detection_method'] = 'keyword_search_fixed'
                                result['keyword_used'] = keyword
                                result['country'] = country_code
                                result['collection_date'] = datetime.now().isoformat()
                                result['terminal'] = self.terminal_id

                                country_results.append(result)
                                seen_ids.add(pub_id)
                                verified_new += 1
                                self.stats['verified_china'] += 1

                        self.stats['total_results'] += len(results)
                        logger.info(f"    🎯 {verified_new} verified China collaborations found")

                    except Exception as parse_error:
                        logger.error(f"❌ Parsing error for {country_code} + '{keyword}': {parse_error}")
                        self.stats['api_errors'] += 1

                elif response.status_code == 429:
                    logger.warning("⏳ Rate limited, waiting 10 seconds...")
                    time.sleep(10)
                else:
                    logger.error(f"❌ API error: {response.status_code}")
                    self.stats['api_errors'] += 1

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                logger.error(f"❌ Request error for {country_code} + '{keyword}': {e}")
                self.stats['api_errors'] += 1

        # Save and import results
        if country_results:
            self._save_results(country_results, country_code)
            self._import_to_warehouse(country_results, country_code)
        else:
            logger.warning(f"⚠️ No verified China collaborations found for {country_code}")

        return len(country_results)

    def _extract_id(self, result: Dict) -> str:
        """Extract publication ID from OpenAIRE result"""

        # Try different ID fields in OpenAIRE
        id_fields = ['id', 'objIdentifier', 'originalId']

        for field in id_fields:
            if field in result:
                return str(result[field])

        # Try nested header
        if 'header' in result:
            header = result['header']
            for field in id_fields:
                if field in header:
                    return str(header[field])

        # Fallback to a hash of the content
        return str(hash(json.dumps(result, sort_keys=True)))[:16]

    def _verify_china_involvement(self, result: Dict) -> bool:
        """Verify China involvement in publication"""

        # Convert entire result to text for searching
        result_text = json.dumps(result).lower()

        # Strong indicators
        strong_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
            'tsinghua', 'peking', 'fudan', 'cas', 'wuhan',
            'guangzhou', 'nanjing', 'hangzhou', 'xinjiang',
            'huawei', 'alibaba', 'tencent', 'baidu'
        ]

        # Check for any strong indicator
        for indicator in strong_indicators:
            if indicator in result_text:
                return True

        # Additional check in metadata if available
        if 'metadata' in result:
            metadata_text = json.dumps(result['metadata']).lower()
            for indicator in strong_indicators:
                if indicator in metadata_text:
                    return True

        return False

    def _save_results(self, results: List[Dict], country_code: str):
        """Save results to JSON file"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"{country_code}_china_collaborations_FIXED_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'country': country_code,
                'terminal': self.terminal_id,
                'total_found': len(results),
                'method': 'keyword_search_fixed',
                'fix_applied': 'openaire_structure_parsing',
                'keywords_used': self.china_keywords[:8],
                'collection_date': datetime.now().isoformat(),
                'results': results
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Saved {len(results)} {country_code}-China collaborations to {output_file.name}")

    def _import_to_warehouse(self, results: List[Dict], country_code: str):
        """Import verified results to warehouse"""

        try:
            conn = sqlite3.connect(self.warehouse_path)
            cursor = conn.cursor()

            imported = 0
            for result in results:
                # Extract title from metadata
                title = self._extract_title(result)

                cursor.execute("""
                INSERT OR REPLACE INTO core_f_publication (
                    pub_id, title, has_chinese_author,
                    china_collaboration_score, source_system,
                    retrieved_at, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    self._extract_id(result),
                    title[:500],
                    1,  # Verified China collaboration
                    1.0,  # High confidence from keyword + verification
                    f'OpenAIRE_FIXED_{self.terminal_id}',
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

    def _extract_title(self, result: Dict) -> str:
        """Extract title from OpenAIRE result"""

        # Try metadata first
        if 'metadata' in result:
            metadata = result['metadata']

            # Different title fields in OpenAIRE
            title_fields = ['title', 'maintitle', 'originalTitle']

            for field in title_fields:
                if field in metadata:
                    title = metadata[field]

                    # Handle different title formats
                    if isinstance(title, dict):
                        return title.get('$', '') or title.get('content', 'Unknown Title')
                    elif isinstance(title, str):
                        return title
                    elif isinstance(title, list) and title:
                        first_title = title[0]
                        if isinstance(first_title, dict):
                            return first_title.get('$', '') or first_title.get('content', 'Unknown Title')
                        return str(first_title)

        # Fallback
        return "Unknown Publication Title"

    def test_single_country(self, country_code: str = "IT"):
        """Test the fix with a single country"""

        logger.info(f"🧪 Testing fixed parser with {country_code}")
        results = self.collect_country_data(country_code, max_keywords=3)
        logger.info(f"✅ Test complete: {results} China collaborations found")

        return results

def main():
    """Main execution - test the fix"""

    collector = FixedOpenAIRECollector("TEST")

    # Test with a few countries
    test_countries = ['IT', 'BE', 'DE']

    logger.info("🔧 Testing FIXED OpenAIRE Collector")
    logger.info("="*50)

    total_found = 0
    for country in test_countries:
        found = collector.test_single_country(country)
        total_found += found
        time.sleep(5)  # Pause between countries

    logger.info(f"\n🎉 FIXED COLLECTOR TEST COMPLETE")
    logger.info(f"Total China collaborations found: {total_found}")
    logger.info(f"Final stats: {collector.stats}")

if __name__ == "__main__":
    main()
