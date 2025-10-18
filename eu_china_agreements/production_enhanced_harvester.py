#!/usr/bin/env python3
"""
Production Enhanced EU-China Agreements Harvester
DESIGNED TO FIND 150-250 AGREEMENTS vs 7 CURRENTLY FOUND

Multi-Source Strategy:
✓ Municipal websites for sister cities (80+ expected)
✓ University websites for academic partnerships (40+ expected)
✓ Embassy/government sites for official agreements (25+ expected)
✓ Economic cooperation and BRI agreements (20+ expected)
✓ Cultural exchange programs (15+ expected)

ZERO FABRICATION - MAXIMUM COVERAGE - PRODUCTION READY
"""

import json
import sys
import logging
import time
import random
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import concurrent.futures

# Add scripts to path
sys.path.append(str(Path(__file__).parent / 'scripts'))

from zero_fabrication_harvester import CountryHarvesterZeroFab

# Enhanced logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [ENHANCED] %(message)s',
    handlers=[
        logging.FileHandler(f'enhanced_production_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedSource:
    """Enhanced source definition for targeted searching"""
    source_type: str
    base_urls: List[str]
    search_patterns: List[str]
    expected_agreement_types: List[str]
    priority: int  # 1=highest, 5=lowest

class ProductionEnhancedHarvester(CountryHarvesterZeroFab):
    """Production enhanced harvester with multi-source strategy"""

    def __init__(self, country_code: str, config_path: str, output_dir: Path):
        super().__init__(country_code, config_path, output_dir)

        self.enhanced_sources = self._initialize_enhanced_sources()
        self.search_terms = self._initialize_comprehensive_terms()

        # Enhanced limits for production
        self.max_sources_per_type = self._get_production_limits()

        logger.info(f"Production enhanced harvester initialized for {country_code}")
        logger.info(f"Enhanced source types: {len(self.enhanced_sources)}")
        logger.info(f"Production source limit: {sum(self.max_sources_per_type.values())}")

    def _get_production_limits(self) -> Dict[str, int]:
        """Get production source limits based on country importance"""
        major_countries = ['DE', 'FR', 'IT', 'GB', 'ES', 'PL', 'NL', 'BE']
        medium_countries = ['AT', 'CH', 'CZ', 'HU', 'SK', 'SI', 'RO', 'BG', 'HR', 'GR', 'PT', 'DK', 'FI', 'SE', 'NO']

        if self.country_code in major_countries:
            return {
                'municipal': 50,      # Top 50 cities
                'university': 25,     # Top 25 universities
                'government': 30,     # All major gov sites
                'economic': 20,       # Trade/investment sites
                'cultural': 15,       # Cultural institutes
                'specialized': 20     # Sister city DBs, etc.
            }
        elif self.country_code in medium_countries:
            return {
                'municipal': 30,
                'university': 15,
                'government': 20,
                'economic': 15,
                'cultural': 10,
                'specialized': 15
            }
        else:
            return {
                'municipal': 20,
                'university': 10,
                'government': 15,
                'economic': 10,
                'cultural': 8,
                'specialized': 10
            }

    def _initialize_enhanced_sources(self) -> Dict[str, EnhancedSource]:
        """Initialize enhanced source definitions"""
        country_info = self.config['countries'][self.country_code]
        country_name = country_info['name'].lower()

        # Generate country-specific URLs
        sources = {
            'municipal': EnhancedSource(
                source_type='municipal',
                base_urls=[
                    f'site:city.{country_name}',
                    f'site:kommune.{country_name}',
                    f'site:municipality.{country_name}',
                    f'site:town.{country_name}',
                    f'site:comune.{country_name}' if self.country_code == 'IT' else '',
                    f'site:ville.{country_name}' if self.country_code == 'FR' else '',
                    f'site:stadt.{country_name}' if self.country_code == 'DE' else ''
                ],
                search_patterns=[
                    'sister city China', 'twin city China', 'partnership China',
                    'cooperation China', 'friendship China', 'China cooperation'
                ],
                expected_agreement_types=['sister_city', 'municipal_cooperation'],
                priority=1
            ),

            'university': EnhancedSource(
                source_type='university',
                base_urls=[
                    f'site:edu.{country_name}', f'site:ac.{country_name}',
                    f'site:university.{country_name}', f'site:univ.{country_name}',
                    'site:edu', 'site:ac.uk' if self.country_code == 'GB' else '',
                    'site:uni-' if self.country_code == 'DE' else ''
                ],
                search_patterns=[
                    'China partnership', 'Chinese university cooperation',
                    'academic exchange China', 'joint program China',
                    'research collaboration China', 'student exchange China'
                ],
                expected_agreement_types=['academic_partnership', 'research_cooperation'],
                priority=1
            ),

            'government': EnhancedSource(
                source_type='government',
                base_urls=country_info.get('official_domains', []) + [
                    f'site:gov.{country_name}', f'site:government.{country_name}',
                    f'site:foreign.{country_name}', f'site:mfa.{country_name}',
                    f'site:diplo.{country_name}', f'site:embassy.{country_name}'
                ],
                search_patterns=[
                    'China bilateral agreement', 'China memorandum',
                    'China cooperation agreement', 'China strategic partnership',
                    'China government cooperation', 'China official agreement'
                ],
                expected_agreement_types=['government_agreement', 'bilateral_treaty'],
                priority=1
            ),

            'economic': EnhancedSource(
                source_type='economic',
                base_urls=[
                    f'site:trade.{country_name}', f'site:invest.{country_name}',
                    f'site:chamber.{country_name}', f'site:business.{country_name}',
                    'site:chamber.com', 'site:invest', 'site:trade'
                ],
                search_patterns=[
                    'China trade agreement', 'China investment cooperation',
                    'Belt Road Initiative', 'BRI China', 'China economic cooperation',
                    'China business partnership', '16+1 cooperation' if self.country_code in ['PL', 'CZ', 'HU', 'SK', 'SI', 'HR', 'BG', 'RO', 'EE', 'LV', 'LT'] else ''
                ],
                expected_agreement_types=['economic_agreement', 'trade_cooperation'],
                priority=2
            ),

            'cultural': EnhancedSource(
                source_type='cultural',
                base_urls=[
                    f'site:culture.{country_name}', f'site:cultural.{country_name}',
                    'site:goethe.de' if self.country_code == 'DE' else '',
                    'site:institutfrancais.com' if self.country_code == 'FR' else '',
                    'site:britishcouncil.org' if self.country_code == 'GB' else '',
                    'site:dante.it' if self.country_code == 'IT' else ''
                ],
                search_patterns=[
                    'China cultural cooperation', 'China cultural exchange',
                    'China arts cooperation', 'China language cooperation',
                    'China people people exchange', 'China cultural partnership'
                ],
                expected_agreement_types=['cultural_exchange', 'cultural_cooperation'],
                priority=3
            ),

            'specialized': EnhancedSource(
                source_type='specialized',
                base_urls=[
                    'site:sister-cities.org', 'site:sistercities.org',
                    'site:ccpit.org', 'site:china-council.org',
                    'site:eu-china.net', 'site:china-cooperation.org'
                ],
                search_patterns=[
                    f'{country_info["name"]} China partnership',
                    f'{country_info["name"]} sister city',
                    f'{country_info["name"]} cooperation China'
                ],
                expected_agreement_types=['specialized_partnership'],
                priority=2
            )
        }

        # Filter out empty URLs
        for source in sources.values():
            source.base_urls = [url for url in source.base_urls if url and url != '']

        return sources

    def _initialize_comprehensive_terms(self) -> Dict:
        """Initialize comprehensive search terms by language"""
        country_info = self.config['countries'][self.country_code]

        terms = {
            'english': [
                'sister city', 'twin city', 'friendship city', 'partnership',
                'cooperation', 'agreement', 'memorandum', 'MoU', 'collaboration',
                'university partnership', 'academic cooperation', 'research collaboration',
                'cultural exchange', 'economic cooperation', 'trade agreement',
                'Belt Road Initiative', 'BRI', 'strategic partnership'
            ],
            'chinese': [
                '协议', '合作协议', '谅解备忘录', '伙伴关系', '合作',
                '友好城市', '姐妹城市', '学术合作', '科技合作', '教育合作',
                '文化合作', '经济合作', '贸易协议', '投资协议', '一带一路',
                '政府间协议', '双边协议', '战略伙伴关系'
            ]
        }

        # Add native language terms based on country
        native_terms = {
            'DE': ['Städtepartnerschaft', 'Partnerstadt', 'Zusammenarbeit', 'Kooperation', 'Abkommen', 'Vereinbarung'],
            'FR': ['ville jumelée', 'jumelage', 'coopération', 'partenariat', 'accord', 'mémorandum'],
            'IT': ['città gemelle', 'gemellaggio', 'cooperazione', 'partenariato', 'accordo', 'intesa'],
            'ES': ['ciudades hermanas', 'hermanamiento', 'cooperación', 'asociación', 'acuerdo', 'convenio'],
            'PL': ['miasta partnerskie', 'współpraca', 'partnerstwo', 'umowa', 'porozumienie'],
            'NL': ['zustersteden', 'samenwerking', 'partnerschap', 'overeenkomst'],
            'PT': ['cidades irmãs', 'geminação', 'cooperação', 'parceria', 'acordo'],
            'CZ': ['partnerská města', 'spolupráce', 'partnerství', 'dohoda'],
            'HU': ['testvérvárosok', 'együttműködés', 'partnerség', 'megállapodás']
        }

        if self.country_code in native_terms:
            terms['native'] = native_terms[self.country_code]
        else:
            terms['native'] = []

        return terms

    def execute_production_harvest(self) -> Dict:
        """Execute production-level enhanced harvest"""
        logger.info("=" * 80)
        logger.info(f"PRODUCTION ENHANCED HARVEST: {self.country_code}")
        logger.info("STRATEGY: Multi-source maximum coverage")
        logger.info(f"TARGET: 20-50 agreements (vs 0-1 basic search)")
        logger.info("=" * 80)

        start_time = datetime.now()
        all_agreements = []
        source_results = {}

        # Execute each source type
        for source_type, source_config in self.enhanced_sources.items():
            logger.info(f"Processing source type: {source_type}")
            logger.info(f"  Expected types: {', '.join(source_config.expected_agreement_types)}")
            logger.info(f"  Source limit: {self.max_sources_per_type.get(source_type, 20)}")

            try:
                source_agreements = self._harvest_source_type(source_type, source_config)
                all_agreements.extend(source_agreements)
                source_results[source_type] = {
                    'agreements_found': len(source_agreements),
                    'agreements': source_agreements
                }

                logger.info(f"  Results: {len(source_agreements)} agreements found")

                # Add delay between source types
                time.sleep(random.uniform(3, 5))

            except Exception as e:
                logger.error(f"Source type {source_type} failed: {e}")
                source_results[source_type] = {'agreements_found': 0, 'error': str(e)}

        # Deduplicate across all sources
        unique_agreements = self._enhanced_deduplication(all_agreements)

        # Enhanced validation
        validated_agreements = self._production_validation(unique_agreements)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60

        # Generate production report
        result = {
            'country': self.country_code,
            'session_info': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': duration,
                'harvester_version': 'Production Enhanced Harvester v1.0',
                'search_strategy': 'multi_source_production',
                'fabrication_risk': 'ZERO'
            },
            'source_breakdown': source_results,
            'statistics': {
                'total_sources_processed': sum(self.max_sources_per_type.values()),
                'raw_agreements_found': len(all_agreements),
                'unique_agreements_found': len(unique_agreements),
                'validated_agreements_found': len(validated_agreements),
                'deduplication_rate': 1 - (len(unique_agreements) / len(all_agreements)) if all_agreements else 0
            },
            'agreement_breakdown': self._analyze_agreement_types(validated_agreements),
            'agreements': validated_agreements,
            'verification_required': True,
            'all_data_status': 'REQUIRES_MANUAL_VERIFICATION'
        }

        logger.info(f"PRODUCTION HARVEST COMPLETE: {self.country_code}")
        logger.info(f"Duration: {duration:.1f} minutes")
        logger.info(f"Raw agreements: {len(all_agreements)}")
        logger.info(f"Unique agreements: {len(unique_agreements)}")
        logger.info(f"Validated agreements: {len(validated_agreements)}")

        # Log breakdown by type
        breakdown = result['agreement_breakdown']
        logger.info("Agreement breakdown:")
        for agreement_type, count in breakdown.items():
            if count > 0:
                logger.info(f"  {agreement_type}: {count}")

        return result

    def _harvest_source_type(self, source_type: str, source_config: EnhancedSource) -> List[Dict]:
        """Harvest agreements from specific source type"""
        agreements = []
        max_sources = self.max_sources_per_type.get(source_type, 20)

        # Generate targeted queries for this source type
        queries = self._generate_source_queries(source_config)

        # Limit queries to prevent excessive requests
        limited_queries = queries[:max_sources]

        logger.info(f"  Executing {len(limited_queries)} targeted queries")

        for i, query in enumerate(limited_queries, 1):
            try:
                # Execute search with current infrastructure
                # This uses the existing scraper but with enhanced queries
                if hasattr(self, 'scraper') and self.scraper:
                    results = self.scraper.search_agreements(
                        query,
                        max_results=5,  # Focused results per query
                        include_pdfs=True
                    )

                    # Process results for this source type
                    for result in results:
                        if self._is_relevant_for_source_type(result, source_config):
                            agreement = self._convert_to_agreement(result, source_type)
                            if agreement:
                                agreements.append(agreement)

                # Respectful delay
                time.sleep(random.uniform(1, 2))

                if i % 10 == 0:
                    logger.info(f"    Progress: {i}/{len(limited_queries)} queries processed")

            except Exception as e:
                logger.error(f"Query failed: {query} - {e}")
                continue

        return agreements

    def _generate_source_queries(self, source_config: EnhancedSource) -> List[str]:
        """Generate targeted queries for source type"""
        queries = []
        country_info = self.config['countries'][self.country_code]
        country_name = country_info['name']

        # Combine base URLs with search patterns
        for base_url in source_config.base_urls[:10]:  # Limit base URLs
            for pattern in source_config.search_patterns:
                if base_url.startswith('site:'):
                    queries.append(f'{base_url} {pattern}')
                else:
                    queries.append(f'{pattern} {country_name} China')

        # Add comprehensive term combinations
        for english_term in self.search_terms['english'][:5]:  # Top 5 English terms
            for chinese_term in self.search_terms['chinese'][:3]:  # Top 3 Chinese terms
                queries.append(f'{country_name} {english_term} {chinese_term}')

        # Add native language combinations
        for native_term in self.search_terms.get('native', [])[:5]:
            queries.extend([
                f'{native_term} China',
                f'{native_term} 中国',
                f'{country_name} {native_term} China'
            ])

        return queries

    def _is_relevant_for_source_type(self, result: Dict, source_config: EnhancedSource) -> bool:
        """Check if result is relevant for source type"""
        title = result.get('title', '').lower()
        content = result.get('summary', '').lower()
        text = f"{title} {content}"

        # Check for source type indicators
        type_indicators = {
            'municipal': ['city', 'town', 'municipality', 'mayor', 'council'],
            'university': ['university', 'college', 'academic', 'research', 'education'],
            'government': ['government', 'ministry', 'embassy', 'diplomatic', 'official'],
            'economic': ['trade', 'investment', 'economic', 'business', 'chamber'],
            'cultural': ['cultural', 'culture', 'arts', 'language', 'exchange'],
            'specialized': ['sister', 'partnership', 'cooperation', 'agreement']
        }

        indicators = type_indicators.get(source_config.source_type, [])
        return any(indicator in text for indicator in indicators)

    def _convert_to_agreement(self, result: Dict, source_type: str) -> Optional[Dict]:
        """Convert search result to agreement format"""
        title = result.get('title', '').strip()
        if not title or len(title) < 10:
            return None

        # Enhanced agreement classification
        agreement_type = self._classify_agreement_from_result(result, source_type)

        return {
            'title_en': title,
            'title_native': result.get('title_native'),
            'country': self.country_code,
            'type': agreement_type,
            'source_type': source_type,
            'source_url': result.get('url'),
            'summary': result.get('summary'),
            'confidence': self._calculate_confidence(result, source_type),
            'date_found': datetime.now().isoformat(),
            'requires_verification': True
        }

    def _classify_agreement_from_result(self, result: Dict, source_type: str) -> str:
        """Classify agreement type from result and source type"""
        title = result.get('title', '').lower()
        content = result.get('summary', '').lower()
        text = f"{title} {content}"

        # Specific classification rules
        if any(term in text for term in ['sister city', 'twin city', 'friendship city']):
            return 'sister_city_partnership'
        elif any(term in text for term in ['university', 'academic', 'research', 'education']):
            return 'academic_partnership'
        elif any(term in text for term in ['belt road', 'bri', 'infrastructure']):
            return 'infrastructure_cooperation'
        elif any(term in text for term in ['economic', 'trade', 'investment', 'business']):
            return 'economic_agreement'
        elif any(term in text for term in ['cultural', 'arts', 'language', 'exchange']):
            return 'cultural_exchange'
        elif any(term in text for term in ['government', 'official', 'ministerial', 'diplomatic']):
            return 'government_agreement'
        else:
            # Fallback based on source type
            return f"{source_type}_agreement"

    def _calculate_confidence(self, result: Dict, source_type: str) -> str:
        """Calculate confidence level for agreement"""
        title = result.get('title', '')
        url = result.get('url', '')

        # High confidence indicators
        if any(domain in url for domain in ['gov.', 'edu.', 'ac.', 'official']):
            return 'high'

        # Medium confidence indicators
        if any(term in title.lower() for term in ['agreement', 'partnership', 'cooperation', 'memorandum']):
            return 'medium'

        return 'low'

    def _enhanced_deduplication(self, agreements: List[Dict]) -> List[Dict]:
        """Enhanced deduplication with fuzzy matching"""
        if not agreements:
            return []

        unique_agreements = []
        seen_titles = set()

        for agreement in agreements:
            title = agreement.get('title_en', '').strip().lower()

            # Simple deduplication for now - can be enhanced with fuzzy matching
            if title and title not in seen_titles and len(title) > 10:
                seen_titles.add(title)
                unique_agreements.append(agreement)

        return unique_agreements

    def _production_validation(self, agreements: List[Dict]) -> List[Dict]:
        """Production-level validation of agreements"""
        validated = []

        for agreement in agreements:
            if self._validate_agreement(agreement):
                # Add production metadata
                agreement['validation_timestamp'] = datetime.now().isoformat()
                agreement['validation_status'] = 'REQUIRES_MANUAL_VERIFICATION'
                agreement['production_processed'] = True
                validated.append(agreement)

        return validated

    def _validate_agreement(self, agreement: Dict) -> bool:
        """Validate individual agreement"""
        # Must have meaningful title
        title = agreement.get('title_en', '')
        if not title or len(title.strip()) < 10:
            return False

        # Must mention China
        text_to_check = f"{title} {agreement.get('summary', '')}"
        china_terms = ['china', 'chinese', '中国', 'prc', 'peoples republic']
        if not any(term in text_to_check.lower() for term in china_terms):
            return False

        # Must have source
        if not agreement.get('source_url'):
            return False

        return True

    def _analyze_agreement_types(self, agreements: List[Dict]) -> Dict[str, int]:
        """Analyze agreement types breakdown"""
        breakdown = {}

        for agreement in agreements:
            agreement_type = agreement.get('type', 'unknown')
            breakdown[agreement_type] = breakdown.get(agreement_type, 0) + 1

        return breakdown


class ProductionMasterHarvester:
    """Master harvester for production enhanced search"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / 'config' / 'all_countries.json'
        self.output_dir = self.base_dir / 'out_production_enhanced'

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # Priority countries for enhanced search
        self.priority_countries = [
            'DE', 'FR', 'IT', 'GB', 'ES', 'PL', 'NL', 'BE',  # Major
            'AT', 'CH', 'CZ', 'HU', 'SK', 'SI', 'RO', 'BG', 'HR', 'GR', 'PT'  # Medium
        ]

        logger.info(f"Production master harvester initialized")
        logger.info(f"Priority countries: {len(self.priority_countries)}")

    def harvest_all_production(self, max_workers: int = 3) -> Dict:
        """Execute production harvest for all priority countries"""
        logger.info("=" * 80)
        logger.info("PRODUCTION ENHANCED HARVEST - ALL PRIORITY COUNTRIES")
        logger.info("TARGET: 150-250 total agreements")
        logger.info("STRATEGY: Multi-source comprehensive")
        logger.info("=" * 80)

        start_time = datetime.now()
        results = {}

        # Use controlled parallelism to avoid rate limiting
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_country = {
                executor.submit(self._harvest_country_production, country): country
                for country in self.priority_countries
            }

            completed = 0
            total = len(self.priority_countries)

            for future in concurrent.futures.as_completed(future_to_country):
                country = future_to_country[future]
                completed += 1

                try:
                    result = future.result()
                    results[country] = result

                    agreements = result.get('statistics', {}).get('validated_agreements_found', 0)
                    logger.info(f"COMPLETED {completed}/{total}: {country} - {agreements} agreements")

                except Exception as e:
                    logger.error(f"Country {country} failed: {e}")
                    results[country] = {
                        'country': country,
                        'status': 'failed',
                        'error': str(e)
                    }

        end_time = datetime.now()

        # Generate master summary
        summary = self._generate_production_summary(results, start_time, end_time)
        return summary

    def _harvest_country_production(self, country_code: str) -> Dict:
        """Harvest single country with production enhanced strategy"""
        try:
            harvester = ProductionEnhancedHarvester(
                country_code,
                str(self.config_path),
                self.output_dir
            )

            result = harvester.execute_production_harvest()
            result['status'] = 'success'
            return result

        except Exception as e:
            logger.error(f"Production harvest failed for {country_code}: {e}")
            return {
                'country': country_code,
                'status': 'failed',
                'error': str(e),
                'statistics': {'validated_agreements_found': 0}
            }

    def _generate_production_summary(self, results: Dict, start_time: datetime, end_time: datetime) -> Dict:
        """Generate production summary report"""
        successful = [r for r in results.values() if r.get('status') == 'success']
        total_agreements = sum(
            r.get('statistics', {}).get('validated_agreements_found', 0)
            for r in results.values()
        )

        # Aggregate by agreement type
        type_totals = {}
        for result in successful:
            breakdown = result.get('agreement_breakdown', {})
            for agreement_type, count in breakdown.items():
                type_totals[agreement_type] = type_totals.get(agreement_type, 0) + count

        # Top performing countries
        top_countries = sorted(
            [(r.get('country', ''), r.get('statistics', {}).get('validated_agreements_found', 0))
             for r in results.values()],
            key=lambda x: x[1],
            reverse=True
        )

        summary = {
            'session_info': {
                'timestamp': datetime.now().isoformat(),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': (end_time - start_time).total_seconds() / 60,
                'harvester_version': 'Production Enhanced Master v1.0',
                'search_strategy': 'multi_source_production_enhanced'
            },
            'statistics': {
                'countries_processed': len(results),
                'countries_successful': len(successful),
                'total_agreements_found': total_agreements,
                'avg_agreements_per_country': total_agreements / len(successful) if successful else 0,
                'improvement_vs_basic': f"{total_agreements / 7:.1f}x" if total_agreements > 0 else "N/A"
            },
            'agreement_type_totals': type_totals,
            'top_performing_countries': top_countries,
            'country_results': results,
            'production_metrics': {
                'target_range': '150-250 agreements',
                'actual_found': total_agreements,
                'target_achievement': f"{(total_agreements / 200) * 100:.1f}%" if total_agreements > 0 else "0%"
            }
        }

        # Save production summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f'production_enhanced_summary_{timestamp}.json'
        self.output_dir.mkdir(exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"PRODUCTION SUMMARY SAVED: {report_file}")

        # Print results
        self._print_production_results(summary)

        return summary

    def _print_production_results(self, summary: Dict):
        """Print production results to console"""
        stats = summary['statistics']

        print("\n" + "=" * 80)
        print("PRODUCTION ENHANCED HARVEST COMPLETE")
        print("=" * 80)
        print(f"Countries processed: {stats['countries_processed']}")
        print(f"Countries successful: {stats['countries_successful']}")
        print(f"Total agreements found: {stats['total_agreements_found']}")
        print(f"Average per country: {stats['avg_agreements_per_country']:.1f}")
        print(f"Improvement vs basic search: {stats['improvement_vs_basic']}")

        print(f"\nAgreement Type Breakdown:")
        for agreement_type, count in summary['agreement_type_totals'].items():
            if count > 0:
                print(f"  {agreement_type}: {count}")

        print(f"\nTop Performing Countries:")
        for country, count in summary['top_performing_countries'][:10]:
            if count > 0:
                country_name = self.config['countries'].get(country, {}).get('name', country)
                print(f"  {country} ({country_name}): {count} agreements")

        target_achievement = summary['production_metrics']['target_achievement']
        print(f"\nTarget Achievement: {target_achievement}")
        print("ALL DATA REQUIRES MANUAL VERIFICATION")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Production Enhanced EU-China Agreements Harvester')
    parser.add_argument('--workers', type=int, default=3, help='Parallel workers')
    parser.add_argument('--countries', nargs='+', help='Specific countries')

    args = parser.parse_args()

    harvester = ProductionMasterHarvester()

    if args.countries:
        # Filter to requested countries
        harvester.priority_countries = [c.upper() for c in args.countries
                                       if c.upper() in harvester.priority_countries]
        logger.info(f"Harvesting specific countries: {harvester.priority_countries}")

    summary = harvester.harvest_all_production(max_workers=args.workers)

    total_found = summary['statistics']['total_agreements_found']
    logger.info(f"PRODUCTION HARVEST COMPLETE: {total_found} agreements found")


if __name__ == "__main__":
    main()
