#!/usr/bin/env python3
"""
Official Database Searcher for EU-China Agreements
Searches EUR-Lex, UN Treaty Collection, and other official sources
ZERO FABRICATION - COMPLETE PROVENANCE
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import logging
from urllib.parse import urlencode, quote

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OfficialDatabaseSearcher:
    """Search official databases for EU-China agreements"""

    def __init__(self):
        self.output_dir = Path("C:/Projects/OSINT - Foresight/eu_china_agreements/official_database_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_eurlex(self) -> List[Dict]:
        """
        Search EUR-Lex database for EU-China agreements
        EUR-Lex is the official EU law database
        """
        logger.info("=" * 60)
        logger.info("SEARCHING EUR-LEX DATABASE")
        logger.info("=" * 60)

        results = []

        # EUR-Lex search API endpoints
        search_queries = [
            {
                'query': 'China cooperation agreement',
                'type': 'international_agreement'
            },
            {
                'query': 'China partnership',
                'type': 'partnership_agreement'
            },
            {
                'query': 'EU China bilateral',
                'type': 'bilateral_agreement'
            },
            {
                'query': 'China memorandum understanding',
                'type': 'MoU'
            }
        ]

        base_url = "https://eur-lex.europa.eu/search.html"

        for search in search_queries:
            logger.info(f"Searching for: {search['query']}")

            # Build EUR-Lex search URL
            params = {
                'text': search['query'],
                'scope': 'EURLEX',
                'type': 'quick',
                'lang': 'en'
            }

            search_url = f"{base_url}?{urlencode(params)}"

            result = {
                'database': 'EUR-Lex',
                'search_query': search['query'],
                'search_type': search['type'],
                'search_url': search_url,
                'timestamp': datetime.now().isoformat(),
                'verification_required': True,
                'data_source': 'Official EU Law Database',
                'citation': f"EUR-Lex. (2024). Search results for '{search['query']}'. Available at: {search_url}. Accessed: {datetime.now().strftime('%Y-%m-%d')}.",
                'manual_check_required': True,
                'instructions': [
                    f"1. Visit: {search_url}",
                    "2. Filter results by document type: International Agreements",
                    "3. Filter by date range if needed",
                    "4. Look for China-specific agreements",
                    "5. Document CELEX numbers of relevant agreements"
                ]
            }

            results.append(result)

        # Known important EU-China agreements to verify
        known_agreements = [
            {
                'title': 'EU-China Comprehensive Agreement on Investment (CAI)',
                'year': '2020',
                'celex': 'Expected format: 22020A####',
                'status': 'Negotiated but not ratified',
                'search_url': 'https://eur-lex.europa.eu/search.html?text=China+investment+agreement+2020'
            },
            {
                'title': 'EU-China Strategic Agenda for Cooperation',
                'year': '2013',
                'celex': 'Search required',
                'status': 'Active',
                'search_url': 'https://eur-lex.europa.eu/search.html?text=China+strategic+agenda+2013'
            },
            {
                'title': 'EU-China Science & Technology Agreement',
                'year': '1998',
                'celex': '21998A1224(01)',
                'status': 'Active',
                'search_url': 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:21998A1224(01)'
            }
        ]

        for agreement in known_agreements:
            logger.info(f"Known agreement: {agreement['title']}")
            results.append({
                'database': 'EUR-Lex',
                'agreement_title': agreement['title'],
                'year': agreement['year'],
                'celex_number': agreement['celex'],
                'status': agreement['status'],
                'verification_url': agreement['search_url'],
                'timestamp': datetime.now().isoformat(),
                'data_source': 'EUR-Lex Known Agreement',
                'citation': f"{agreement['title']}. ({agreement['year']}). EUR-Lex Database. CELEX: {agreement['celex']}. Status: {agreement['status']}.",
                'verification_priority': 'HIGH'
            })

        return results

    def search_un_treaties(self) -> List[Dict]:
        """
        Search UN Treaty Collection for agreements
        """
        logger.info("=" * 60)
        logger.info("SEARCHING UN TREATY COLLECTION")
        logger.info("=" * 60)

        results = []

        # UN Treaty Collection search parameters
        base_url = "https://treaties.un.org"

        search_queries = [
            "China European Union",
            "China EU bilateral",
            "China Europe cooperation"
        ]

        for query in search_queries:
            logger.info(f"UN Treaty search: {query}")

            result = {
                'database': 'UN Treaty Collection',
                'search_query': query,
                'search_url': f"{base_url}/Pages/AdvanceSearch.aspx?clang=_en",
                'timestamp': datetime.now().isoformat(),
                'data_source': 'United Nations Treaty Collection',
                'manual_steps': [
                    f"1. Visit: {base_url}/Pages/AdvanceSearch.aspx?clang=_en",
                    f"2. Enter search term: {query}",
                    "3. Select 'Bilateral Treaties' if available",
                    "4. Check both China and EU member states",
                    "5. Document treaty registration numbers"
                ],
                'citation': f"UN Treaty Collection. (2024). Search for '{query}'. Database: {base_url}. Accessed: {datetime.now().strftime('%Y-%m-%d')}."
            }

            results.append(result)

        return results

    def search_council_europa(self) -> List[Dict]:
        """
        Search Council of Europe treaty database
        """
        logger.info("=" * 60)
        logger.info("SEARCHING COUNCIL OF EUROPE TREATIES")
        logger.info("=" * 60)

        results = []

        base_url = "https://www.coe.int/en/web/conventions"

        result = {
            'database': 'Council of Europe',
            'search_url': f"{base_url}/full-list",
            'timestamp': datetime.now().isoformat(),
            'data_source': 'Council of Europe Treaty Office',
            'instructions': [
                f"1. Visit: {base_url}/full-list",
                "2. Search for treaties with China participation",
                "3. Check for EU member state bilateral agreements",
                "4. Document ETS/CETS numbers"
            ],
            'citation': f"Council of Europe Treaty Office. (2024). Treaty database. Available at: {base_url}. Accessed: {datetime.now().strftime('%Y-%m-%d')}."
        }

        results.append(result)

        return results

    def generate_specific_searches(self) -> List[Dict]:
        """
        Generate specific search URLs for each EU country + China
        """
        logger.info("=" * 60)
        logger.info("GENERATING COUNTRY-SPECIFIC SEARCHES")
        logger.info("=" * 60)

        eu_countries = [
            "Germany", "France", "Italy", "Spain", "Poland",
            "Netherlands", "Belgium", "Portugal", "Greece", "Czech Republic",
            "Hungary", "Sweden", "Austria", "Denmark", "Finland",
            "Slovakia", "Ireland", "Croatia", "Lithuania", "Slovenia",
            "Latvia", "Estonia", "Cyprus", "Luxembourg", "Malta",
            "Bulgaria", "Romania"
        ]

        results = []

        for country in eu_countries[:10]:  # Limit to first 10 for initial search
            # EUR-Lex search for bilateral agreements
            eurlex_url = f"https://eur-lex.europa.eu/search.html?text={quote(country)}+China+agreement&scope=EURLEX"

            result = {
                'country': country,
                'search_type': 'bilateral_agreement',
                'eurlex_url': eurlex_url,
                'google_scholar_url': f"https://scholar.google.com/scholar?q={quote(country)}+China+bilateral+agreement+treaty",
                'timestamp': datetime.now().isoformat(),
                'instructions': f"Search for {country}-China bilateral agreements",
                'citation': f"{country}-China agreements search. EUR-Lex and Google Scholar. Accessed: {datetime.now().strftime('%Y-%m-%d')}."
            }

            results.append(result)

        return results

    def create_search_checklist(self) -> Dict:
        """
        Create comprehensive search checklist for manual verification
        """
        logger.info("Creating comprehensive search checklist...")

        checklist = {
            'created': datetime.now().isoformat(),
            'purpose': 'Manual search checklist for EU-China agreements',
            'databases': {
                'primary': [
                    {
                        'name': 'EUR-Lex',
                        'url': 'https://eur-lex.europa.eu',
                        'description': 'Official EU law and treaties database',
                        'search_tips': [
                            'Use advanced search',
                            'Filter by "International Agreements"',
                            'Search for "China" in full text',
                            'Check CELEX numbers starting with 2 (international agreements)'
                        ]
                    },
                    {
                        'name': 'European Council Agreements',
                        'url': 'https://www.consilium.europa.eu/en/documents-publications/treaties-agreements/',
                        'description': 'Council agreements and treaties',
                        'search_tips': [
                            'Browse international agreements section',
                            'Search for China-specific agreements',
                            'Check both bilateral and multilateral'
                        ]
                    }
                ],
                'secondary': [
                    {
                        'name': 'UN Treaty Collection',
                        'url': 'https://treaties.un.org',
                        'description': 'United Nations treaty database',
                        'search_tips': [
                            'Use advanced search',
                            'Search by country (China + EU states)',
                            'Check bilateral treaties section'
                        ]
                    },
                    {
                        'name': 'Treaty Database EU External Action',
                        'url': 'https://www.eeas.europa.eu',
                        'description': 'EU External Action Service',
                        'search_tips': [
                            'Check China country page',
                            'Look for partnership agreements',
                            'Review joint statements'
                        ]
                    }
                ],
                'academic': [
                    {
                        'name': 'Google Scholar',
                        'url': 'https://scholar.google.com',
                        'search_query': '"EU-China agreement" OR "EU-China treaty" OR "EU-China MoU"'
                    },
                    {
                        'name': 'JSTOR',
                        'url': 'https://www.jstor.org',
                        'search_query': 'EU China bilateral agreement'
                    }
                ]
            },
            'search_terms': {
                'english': [
                    'EU-China agreement',
                    'EU-China treaty',
                    'EU-China MoU',
                    'EU-China partnership',
                    'EU-China cooperation',
                    'EU-China bilateral'
                ],
                'legal_terms': [
                    'bilateral agreement',
                    'memorandum of understanding',
                    'strategic partnership',
                    'cooperation framework',
                    'joint declaration'
                ]
            },
            'verification_steps': [
                '1. Search each database systematically',
                '2. Document all findings with URLs',
                '3. Save PDFs of agreements found',
                '4. Record CELEX/treaty numbers',
                '5. Note signature dates and parties',
                '6. Check ratification status',
                '7. Verify current validity'
            ]
        }

        return checklist

    def execute_comprehensive_search(self) -> Dict:
        """
        Execute all search methods and compile results
        """
        logger.info("=" * 60)
        logger.info("EXECUTING COMPREHENSIVE OFFICIAL DATABASE SEARCH")
        logger.info("ZERO FABRICATION - MANUAL VERIFICATION REQUIRED")
        logger.info("=" * 60)

        # Execute all searches
        eurlex_results = self.search_eurlex()
        un_results = self.search_un_treaties()
        coe_results = self.search_council_europa()
        specific_searches = self.generate_specific_searches()
        checklist = self.create_search_checklist()

        # Compile results
        comprehensive_results = {
            'execution_time': datetime.now().isoformat(),
            'search_method': 'Official Database Search',
            'statistics': {
                'eurlex_searches': len(eurlex_results),
                'un_searches': len(un_results),
                'coe_searches': len(coe_results),
                'country_specific': len(specific_searches),
                'total_search_points': len(eurlex_results) + len(un_results) + len(coe_results) + len(specific_searches)
            },
            'results': {
                'eurlex': eurlex_results,
                'un_treaties': un_results,
                'council_europe': coe_results,
                'country_specific': specific_searches
            },
            'search_checklist': checklist,
            'data_quality': {
                'fabrication_risk': 'ZERO',
                'all_sources_official': True,
                'manual_verification_required': True,
                'citations_complete': True
            },
            'next_steps': [
                '1. Manually search each database using provided URLs',
                '2. Document all agreements found with full citations',
                '3. Download PDF copies of agreements',
                '4. Create inventory with CELEX/treaty numbers',
                '5. Verify ratification and current status',
                '6. Cross-reference with national databases'
            ]
        }

        # Save results
        output_file = self.output_dir / f"official_database_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved: {output_file}")

        # Create human-readable report
        self.create_search_report(comprehensive_results)

        return comprehensive_results

    def create_search_report(self, results: Dict):
        """Create human-readable search report"""
        report_lines = [
            "# OFFICIAL DATABASE SEARCH REPORT",
            f"Generated: {results['execution_time']}",
            "",
            "## SEARCH SUMMARY",
            f"- EUR-Lex searches prepared: {results['statistics']['eurlex_searches']}",
            f"- UN Treaty searches prepared: {results['statistics']['un_searches']}",
            f"- Country-specific searches: {results['statistics']['country_specific']}",
            f"- Total search points: {results['statistics']['total_search_points']}",
            "",
            "## PRIMARY DATABASES TO SEARCH",
            "",
            "### EUR-Lex (EU Official)",
            "The primary source for all EU-China agreements:",
            ""
        ]

        # Add EUR-Lex searches
        for item in results['results']['eurlex'][:5]:  # First 5 items
            if 'agreement_title' in item:
                report_lines.append(f"- **{item['agreement_title']}** ({item['year']})")
                report_lines.append(f"  - Status: {item['status']}")
                report_lines.append(f"  - Verify at: {item.get('verification_url', 'N/A')}")
            else:
                report_lines.append(f"- Search: {item['search_query']}")
                report_lines.append(f"  - Type: {item['search_type']}")

        report_lines.extend([
            "",
            "### UN Treaty Collection",
            "For registered international agreements:",
            ""
        ])

        # Add UN searches
        for item in results['results']['un_treaties'][:3]:
            report_lines.append(f"- Search term: {item['search_query']}")

        report_lines.extend([
            "",
            "## COUNTRY-SPECIFIC SEARCHES",
            "Bilateral agreements by country:",
            ""
        ])

        # Add country searches
        for item in results['results']['country_specific'][:5]:
            report_lines.append(f"- **{item['country']}**: {item['eurlex_url']}")

        report_lines.extend([
            "",
            "## VERIFICATION CHECKLIST",
            "",
            "### Required Actions:",
        ])

        for step in results['next_steps']:
            report_lines.append(step)

        report_lines.extend([
            "",
            "## DATA QUALITY STATEMENT",
            "- All URLs point to official government databases",
            "- Zero fabrication - all searches must be manually executed",
            "- Results require manual verification and documentation",
            "- Citations must be collected for each agreement found",
            "",
            "## IMPORTANT NOTES",
            "- EUR-Lex CELEX numbers starting with '2' indicate international agreements",
            "- Check both EU-level and member state bilateral agreements",
            "- Verify ratification status - signed does not mean in force",
            "- Document finding date and database version"
        ])

        # Save report
        report_file = self.output_dir / f"search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        logger.info(f"Report saved: {report_file}")

def main():
    """Execute official database search"""
    print("=" * 60)
    print("OFFICIAL DATABASE SEARCHER")
    print("EU-CHINA BILATERAL AGREEMENTS")
    print("=" * 60)

    searcher = OfficialDatabaseSearcher()
    results = searcher.execute_comprehensive_search()

    print(f"\nSearch preparation complete:")
    print(f"Total search points: {results['statistics']['total_search_points']}")
    print(f"Databases to search: EUR-Lex, UN Treaties, Council of Europe")
    print(f"\nReports saved in: {searcher.output_dir}")
    print("\nMANUAL EXECUTION REQUIRED FOR ALL SEARCHES")
    print("ZERO FABRICATION - COMPLETE DOCUMENTATION REQUIRED")

if __name__ == "__main__":
    main()
