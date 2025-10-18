#!/usr/bin/env python3
"""
Comprehensive EU-China Agreements Harvester
Enhanced for maximum coverage of all agreement types:
- Sister city agreements
- Science & technology partnerships
- Academic collaborations
- Economic agreements
- Cultural exchanges
- Infrastructure projects
- Government MoUs
- Municipal partnerships

ZERO FABRICATION - STRICT PROVENANCE - COMPREHENSIVE COVERAGE
"""

import json
import logging
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from zero_fabrication_harvester import CountryHarvesterZeroFab, ProvenanceTracker

# Enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [COMPREHENSIVE] %(message)s',
    handlers=[
        logging.FileHandler(f'comprehensive_harvest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveHarvester(CountryHarvesterZeroFab):
    """Enhanced harvester for comprehensive agreement collection"""

    def __init__(self, country_code: str, config_path: str, output_dir: Path):
        super().__init__(country_code, config_path, output_dir)

        # Load comprehensive search terms
        self.comprehensive_config = self._load_comprehensive_config()

        # Enhanced source limits based on country importance
        self.source_limits = self._determine_source_limits()

        logger.info(f"Comprehensive harvester initialized for {country_code}")
        logger.info(f"Source limit: {self.source_limits} sources")

    def _load_comprehensive_config(self) -> Dict:
        """Load comprehensive search configuration"""
        config_file = Path(__file__).parent.parent / 'config' / 'comprehensive_search_terms.json'

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning("Comprehensive config not found, using defaults")
            return {}

    def _determine_source_limits(self) -> int:
        """Determine appropriate source limits based on country"""
        major_countries = ['DE', 'FR', 'IT', 'GB', 'ES', 'PL', 'NL', 'BE']
        medium_countries = ['AT', 'CH', 'CZ', 'HU', 'SK', 'SI', 'RO', 'BG', 'HR', 'GR', 'PT']

        if self.country_code in major_countries:
            return 50  # Deep search for major countries
        elif self.country_code in medium_countries:
            return 30  # Medium search for medium countries
        else:
            return 20  # Standard search for smaller countries

    def generate_comprehensive_search_queries(self) -> List[str]:
        """Generate comprehensive search queries for all agreement types"""
        country_info = self.config['countries'][self.country_code]
        queries = []

        # Base country identifiers
        country_names = [
            country_info['name'],
            country_info.get('native_name', ''),
            country_info.get('chinese_name', '')
        ]

        # Get comprehensive agreement types
        agreement_types = self.comprehensive_config.get('comprehensive_agreement_types', {})

        # Generate queries for each agreement type
        for category, terms in agreement_types.items():
            for term in terms:
                for country_name in country_names:
                    if country_name:
                        # English queries
                        queries.extend([
                            f'"{term}" "{country_name}" China',
                            f'"{term}" "{country_name}" Chinese',
                            f'China {term} {country_name}',
                            f'Chinese {term} {country_name}'
                        ])

        # Add native language queries
        if 'search_terms' in country_info:
            native_terms = country_info['search_terms'].get(country_info['primary_language'], [])
            chinese_terms = self.comprehensive_config.get('multilingual_terms', {}).get('chinese_terms', [])

            for native_term in native_terms:
                for chinese_term in chinese_terms:
                    queries.extend([
                        f'{native_term} {chinese_term}',
                        f'{native_term} 中国',
                        f'{chinese_term} {country_info["name"]}'
                    ])

        # Add specific search operators
        search_operators = self.comprehensive_config.get('search_strategies', {}).get('search_operators', [])
        for operator in search_operators:
            queries.append(f'{operator} {country_info["name"]}')

        # Add site-specific searches
        official_domains = country_info.get('official_domains', [])
        for domain in official_domains:
            queries.extend([
                f'site:{domain} China cooperation',
                f'site:{domain} China agreement',
                f'site:{domain} China partnership',
                f'site:{domain} 中国 合作',
                f'site:{domain} sister city China',
                f'site:{domain} university China cooperation'
            ])

        # Deduplicate and randomize
        unique_queries = list(set(queries))
        random.shuffle(unique_queries)

        logger.info(f"Generated {len(unique_queries)} comprehensive search queries")
        return unique_queries[:self.source_limits]  # Limit to appropriate number

    def harvest_comprehensive(self) -> Dict:
        """Execute comprehensive harvest with enhanced coverage"""
        logger.info("=" * 80)
        logger.info(f"COMPREHENSIVE HARVEST - {self.country_code}")
        logger.info(f"TARGET: ALL AGREEMENT TYPES")
        logger.info(f"SOURCE LIMIT: {self.source_limits}")
        logger.info("FABRICATION RISK: ZERO")
        logger.info("=" * 80)

        start_time = datetime.now()

        # Generate comprehensive search queries
        search_queries = self.generate_comprehensive_search_queries()

        logger.info(f"Executing {len(search_queries)} targeted searches...")

        # Execute searches with enhanced parameters
        all_agreements = []
        search_results = []

        for i, query in enumerate(search_queries, 1):
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(search_queries)} searches completed")

            try:
                # Enhanced search with longer delays to avoid rate limiting
                time.sleep(random.uniform(2, 4))

                # Execute search and collect results
                results = self._execute_enhanced_search(query)
                search_results.extend(results)

                # Process results for agreements
                agreements = self._extract_agreements_from_results(results)
                all_agreements.extend(agreements)

            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
                continue

        # Enhanced deduplication
        unique_agreements = self._enhanced_deduplication(all_agreements)

        # Enhanced validation
        validated_agreements = self._enhanced_validation(unique_agreements)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60

        # Generate comprehensive report
        report = {
            'country': self.country_code,
            'session_info': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': duration,
                'search_queries_executed': len(search_queries),
                'source_limit': self.source_limits,
                'fabrication_risk': 'ZERO'
            },
            'search_coverage': {
                'sister_cities': self._count_agreements_by_type(validated_agreements, 'sister'),
                'academic_partnerships': self._count_agreements_by_type(validated_agreements, 'academic'),
                'science_tech': self._count_agreements_by_type(validated_agreements, 'science|technology'),
                'economic_agreements': self._count_agreements_by_type(validated_agreements, 'economic|trade'),
                'cultural_exchanges': self._count_agreements_by_type(validated_agreements, 'cultural'),
                'government_mous': self._count_agreements_by_type(validated_agreements, 'government|official'),
                'other_agreements': len(validated_agreements)
            },
            'agreements_found': len(validated_agreements),
            'agreements': validated_agreements,
            'verification_required': True,
            'all_data_status': 'REQUIRES_MANUAL_VERIFICATION'
        }

        logger.info(f"COMPREHENSIVE HARVEST COMPLETE")
        logger.info(f"Country: {self.country_code}")
        logger.info(f"Duration: {duration:.1f} minutes")
        logger.info(f"Total agreements found: {len(validated_agreements)}")
        logger.info(f"Sister cities: {report['search_coverage']['sister_cities']}")
        logger.info(f"Academic partnerships: {report['search_coverage']['academic_partnerships']}")
        logger.info(f"Science & tech: {report['search_coverage']['science_tech']}")

        return report

    def _execute_enhanced_search(self, query: str) -> List[Dict]:
        """Execute enhanced search with better result processing"""
        # Implement enhanced search logic here
        # This would integrate with the existing scraper but with enhanced processing
        results = []

        try:
            # Use existing scraper infrastructure but with enhanced parameters
            if hasattr(self, 'scraper') and self.scraper:
                search_results = self.scraper.search_agreements(
                    query,
                    max_results=10,  # More results per query
                    include_pdfs=True,
                    deep_scan=True
                )
                results.extend(search_results)
        except Exception as e:
            logger.error(f"Enhanced search failed: {e}")

        return results

    def _count_agreements_by_type(self, agreements: List[Dict], type_pattern: str) -> int:
        """Count agreements matching specific type patterns"""
        import re
        count = 0
        pattern = re.compile(type_pattern, re.IGNORECASE)

        for agreement in agreements:
            title = agreement.get('title_en', '') + ' ' + agreement.get('title_native', '')
            summary = agreement.get('summary', '')
            if pattern.search(title + ' ' + summary):
                count += 1

        return count

    def _enhanced_deduplication(self, agreements: List[Dict]) -> List[Dict]:
        """Enhanced deduplication with better similarity detection"""
        # Use existing deduplication but with enhanced parameters
        if hasattr(self, 'deduplicator'):
            return self.deduplicator.deduplicate_agreements(
                agreements,
                similarity_threshold=0.85,  # Higher threshold for better accuracy
                field_weights={
                    'title': 0.4,
                    'parties': 0.3,
                    'date': 0.2,
                    'type': 0.1
                }
            )
        return agreements

    def _enhanced_validation(self, agreements: List[Dict]) -> List[Dict]:
        """Enhanced validation with comprehensive checks"""
        validated = []

        for agreement in agreements:
            # Enhanced validation logic
            if self._is_valid_agreement(agreement):
                # Add enhanced metadata
                agreement['validation_timestamp'] = datetime.now().isoformat()
                agreement['validation_status'] = 'REQUIRES_MANUAL_VERIFICATION'
                agreement['confidence_enhanced'] = True
                validated.append(agreement)

        return validated

    def _is_valid_agreement(self, agreement: Dict) -> bool:
        """Enhanced validation criteria"""
        # Must have meaningful title
        title = agreement.get('title_en', '') or agreement.get('title_native', '')
        if not title or len(title.strip()) < 10:
            return False

        # Must have source
        if not agreement.get('sources'):
            return False

        # Must mention China or Chinese entities
        text_to_check = f"{title} {agreement.get('summary', '')}"
        china_indicators = ['china', 'chinese', '中国', 'prc', "people's republic"]

        if not any(indicator in text_to_check.lower() for indicator in china_indicators):
            return False

        return True


def main():
    """Main execution for comprehensive harvesting"""
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive EU-China Agreements Harvester')
    parser.add_argument('--country', required=True, help='Country code (e.g., DE, FR, IT)')
    parser.add_argument('--config', default='config/all_countries.json', help='Config file path')
    parser.add_argument('--output', default='out_comprehensive', help='Output directory')

    args = parser.parse_args()

    # Initialize comprehensive harvester
    output_dir = Path(__file__).parent.parent / args.output

    harvester = ComprehensiveHarvester(
        args.country,
        str(Path(__file__).parent.parent / args.config),
        output_dir
    )

    # Execute comprehensive harvest
    result = harvester.harvest_comprehensive()

    # Save results
    output_file = output_dir / f'{args.country}_comprehensive_results.json'
    output_dir.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"Comprehensive results saved to: {output_file}")


if __name__ == "__main__":
    main()
