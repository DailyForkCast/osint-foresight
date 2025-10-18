#!/usr/bin/env python3
"""
Improved Collaboration Analyzer
Better search methods for accurate collaboration rate measurement
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImprovedCollaborationAnalyzer:
    """Multiple methods to accurately measure research collaboration"""

    def __init__(self):
        self.output_dir = Path("reports/country=IT/improved_collaboration")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            'analysis_date': datetime.now().isoformat(),
            'methods': {},
            'reconciliation': {},
            'best_estimate': {}
        }

    # METHOD 1: Crossref with Affiliation Analysis
    def method1_crossref_affiliation_analysis(self, country1: str = "Italy", country2: str = "China") -> Dict:
        """
        Use Crossref but analyze actual author affiliations in the results
        """
        logger.info(f"Method 1: Crossref with affiliation verification for {country1}-{country2}")

        # First, get a sample of papers mentioning both countries
        params = {
            'query': f'{country1} {country2}',
            'filter': 'from-pub-date:2020-01-01,until-pub-date:2024-12-31',
            'rows': 100,  # Get larger sample for analysis
            'select': 'DOI,title,author,published,container-title'
        }

        try:
            response = requests.get(
                "https://api.crossref.org/works",
                params=params,
                headers={'User-Agent': 'Academic Research Project'}
            )

            if response.status_code == 200:
                data = response.json()
                total_found = data['message']['total-results']
                items = data['message']['items']

                # Now verify actual collaborations by checking affiliations
                verified_collabs = 0
                collaboration_patterns = {
                    'both_in_affiliation': 0,
                    'both_in_authors': 0,
                    'mixed_affiliations': 0,
                    'unclear': 0
                }

                for item in items:
                    authors = item.get('author', [])
                    has_country1 = False
                    has_country2 = False

                    # Check each author's affiliations
                    for author in authors:
                        affiliations = author.get('affiliation', [])
                        for aff in affiliations:
                            aff_name = aff.get('name', '').lower()
                            if country1.lower() in aff_name or 'milan' in aff_name or 'rome' in aff_name or 'bologna' in aff_name:
                                has_country1 = True
                            if country2.lower() in aff_name or 'beijing' in aff_name or 'shanghai' in aff_name or 'chinese academy' in aff_name:
                                has_country2 = True

                    if has_country1 and has_country2:
                        verified_collabs += 1
                        collaboration_patterns['both_in_affiliation'] += 1
                    elif has_country1 or has_country2:
                        collaboration_patterns['mixed_affiliations'] += 1
                    else:
                        collaboration_patterns['unclear'] += 1

                # Estimate true collaboration rate
                verification_rate = verified_collabs / len(items) if items else 0
                estimated_true_collabs = int(total_found * verification_rate)

                return {
                    'method': 'Crossref with affiliation verification',
                    'raw_results': total_found,
                    'sample_size': len(items),
                    'verified_collaborations': verified_collabs,
                    'verification_rate': round(verification_rate * 100, 2),
                    'estimated_true_collaborations': estimated_true_collabs,
                    'patterns': collaboration_patterns
                }

        except Exception as e:
            logger.error(f"Method 1 error: {e}")
            return {'error': str(e)}

    # METHOD 2: OpenAlex API with Precise Filters
    def method2_openalex_precise(self, country1: str = "Italy", country2: str = "China") -> Dict:
        """
        Use OpenAlex API with precise institution and author affiliation filters
        """
        logger.info(f"Method 2: OpenAlex with precise filters for {country1}-{country2}")

        # OpenAlex API endpoint
        base_url = "https://api.openalex.org/works"

        # Build precise query
        params = {
            'filter': f'institutions.country_code:IT,institutions.country_code:CN,from_publication_date:2020-01-01',
            'group_by': 'publication_year',
            'per_page': 200
        }

        try:
            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Also get total Italy papers for rate calculation
                italy_params = {
                    'filter': 'institutions.country_code:IT,from_publication_date:2020-01-01',
                    'group_by': 'publication_year'
                }
                italy_response = requests.get(base_url, params=italy_params)
                italy_data = italy_response.json() if italy_response.status_code == 200 else {}

                italy_total = italy_data.get('meta', {}).get('count', 100000)
                collab_total = data.get('meta', {}).get('count', 0)

                collaboration_rate = (collab_total / italy_total * 100) if italy_total > 0 else 0

                return {
                    'method': 'OpenAlex with precise institutional filters',
                    'italy_total_papers': italy_total,
                    'collaboration_papers': collab_total,
                    'collaboration_rate': round(collaboration_rate, 2),
                    'years_covered': '2020-2024',
                    'confidence': 'HIGH - Uses institutional country codes'
                }

        except Exception as e:
            logger.error(f"Method 2 error: {e}")
            return {'error': str(e)}

    # METHOD 3: Semantic Scholar with Author Analysis
    def method3_semantic_scholar(self, country1: str = "Italy", country2: str = "China") -> Dict:
        """
        Use Semantic Scholar API to analyze papers with detailed author information
        """
        logger.info(f"Method 3: Semantic Scholar analysis for {country1}-{country2}")

        base_url = "http://api.semanticscholar.org/graph/v1/paper/search"

        # Search for papers with both countries in author affiliations
        params = {
            'query': f'"{country1}" AND "{country2}"',
            'fields': 'title,authors,year,citationCount,venue',
            'limit': 100,
            'year': '2020-2024'
        }

        try:
            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])

                # Analyze author patterns
                collaboration_types = {
                    'high_citation': 0,  # >10 citations
                    'recent': 0,  # 2023-2024
                    'venue_quality': {}  # Track venues
                }

                for paper in papers:
                    if paper.get('citationCount', 0) > 10:
                        collaboration_types['high_citation'] += 1
                    if paper.get('year', 0) >= 2023:
                        collaboration_types['recent'] += 1
                    venue = paper.get('venue', 'Unknown')
                    if venue:
                        collaboration_types['venue_quality'][venue] = collaboration_types['venue_quality'].get(venue, 0) + 1

                return {
                    'method': 'Semantic Scholar with author analysis',
                    'papers_analyzed': len(papers),
                    'high_impact_collaborations': collaboration_types['high_citation'],
                    'recent_collaborations': collaboration_types['recent'],
                    'top_venues': dict(sorted(collaboration_types['venue_quality'].items(),
                                             key=lambda x: x[1],
                                             reverse=True)[:5]),
                    'quality_indicator': 'Focus on citation impact'
                }

        except Exception as e:
            logger.error(f"Method 3 error: {e}")
            return {'error': str(e)}

    # METHOD 4: ArXiv Direct Analysis
    def method4_arxiv_detailed(self, country1: str = "Italy", country2: str = "China") -> Dict:
        """
        Detailed ArXiv analysis with multiple search strategies
        """
        logger.info(f"Method 4: ArXiv detailed analysis for {country1}-{country2}")

        try:
            import arxiv

            # Strategy 1: Search by author affiliations
            strategies = [
                f'au:"{country1}" AND au:"{country2}"',  # Authors from both
                f'ti:"{country1}" AND ti:"{country2}"',  # Title mentions both
                f'abs:"{country1}" AND abs:"{country2}" AND cat:cs.*'  # CS papers mentioning both
            ]

            results = {}
            for strategy in strategies:
                search = arxiv.Search(
                    query=strategy,
                    max_results=50,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                papers = list(search.results())
                results[strategy[:20]] = len(papers)

            # Get Italy baseline for comparison
            italy_search = arxiv.Search(
                query=f'au:"{country1}"',
                max_results=1
            )
            italy_papers = list(italy_search.results())

            return {
                'method': 'ArXiv multi-strategy analysis',
                'search_strategies': results,
                'primary_estimate': results.get(f'au:"{country1}" AND au:', 0),
                'field_specific': 'Primarily CS/Physics/Math',
                'limitation': 'Preprints only, not all published papers'
            }

        except Exception as e:
            logger.error(f"Method 4 error: {e}")
            return {'error': str(e)}

    # METHOD 5: DOI Resolution and Publisher APIs
    def method5_doi_sampling(self, sample_size: int = 100) -> Dict:
        """
        Sample DOIs and check publisher metadata directly
        """
        logger.info(f"Method 5: DOI sampling and verification")

        # Get sample of Italy papers from Crossref
        params = {
            'query.affiliation': 'Italy',
            'filter': 'from-pub-date:2023-01-01',
            'rows': sample_size,
            'select': 'DOI,author'
        }

        try:
            response = requests.get(
                "https://api.crossref.org/works",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                items = data['message']['items']

                china_collabs = 0
                usa_collabs = 0
                germany_collabs = 0

                for item in items:
                    authors = item.get('author', [])
                    affiliations_text = ' '.join([
                        ' '.join([aff.get('name', '') for aff in author.get('affiliation', [])])
                        for author in authors
                    ]).lower()

                    if 'china' in affiliations_text or 'beijing' in affiliations_text or 'shanghai' in affiliations_text:
                        china_collabs += 1
                    if 'usa' in affiliations_text or 'united states' in affiliations_text or 'america' in affiliations_text:
                        usa_collabs += 1
                    if 'germany' in affiliations_text or 'deutschland' in affiliations_text or 'berlin' in affiliations_text:
                        germany_collabs += 1

                return {
                    'method': 'DOI sampling with direct verification',
                    'sample_size': len(items),
                    'china_collaboration_rate': round(china_collabs / len(items) * 100, 2) if items else 0,
                    'usa_collaboration_rate': round(usa_collabs / len(items) * 100, 2) if items else 0,
                    'germany_collaboration_rate': round(germany_collabs / len(items) * 100, 2) if items else 0,
                    'confidence': 'MEDIUM - Based on sample'
                }

        except Exception as e:
            logger.error(f"Method 5 error: {e}")
            return {'error': str(e)}

    def reconcile_results(self, all_results: Dict) -> Dict:
        """
        Reconcile different methods to get best estimate
        """
        logger.info("Reconciling results from all methods")

        # Extract collaboration rates where available
        rates = []
        high_confidence_rates = []

        for method, result in all_results.items():
            if 'collaboration_rate' in result:
                rates.append(result['collaboration_rate'])
                if result.get('confidence', '').startswith('HIGH'):
                    high_confidence_rates.append(result['collaboration_rate'])
            elif 'china_collaboration_rate' in result:
                rates.append(result['china_collaboration_rate'])

        if high_confidence_rates:
            best_estimate = sum(high_confidence_rates) / len(high_confidence_rates)
        elif rates:
            best_estimate = sum(rates) / len(rates)
        else:
            best_estimate = None

        return {
            'all_rates': rates,
            'high_confidence_rates': high_confidence_rates,
            'best_estimate': round(best_estimate, 2) if best_estimate else None,
            'range': f"{min(rates):.1f}% - {max(rates):.1f}%" if rates else "Unknown",
            'recommendation': 'Use OpenAlex institutional filter as most reliable'
        }

    def run_all_methods(self) -> Dict:
        """
        Run all methods and generate comprehensive report
        """
        logger.info("Running all improved collaboration analysis methods")

        # Run each method
        self.results['methods']['crossref_verified'] = self.method1_crossref_affiliation_analysis()
        time.sleep(2)

        self.results['methods']['openalex_precise'] = self.method2_openalex_precise()
        time.sleep(2)

        self.results['methods']['semantic_scholar'] = self.method3_semantic_scholar()
        time.sleep(2)

        self.results['methods']['arxiv_detailed'] = self.method4_arxiv_detailed()
        time.sleep(2)

        self.results['methods']['doi_sampling'] = self.method5_doi_sampling()

        # Reconcile results
        self.results['reconciliation'] = self.reconcile_results(self.results['methods'])

        # Save results
        output_file = self.output_dir / 'improved_collaboration_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to {output_file}")

        # Generate summary
        self.generate_summary_report()

        return self.results

    def generate_summary_report(self):
        """
        Generate markdown summary of improved analysis
        """
        summary_file = self.output_dir / 'improved_methods_summary.md'

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Improved Collaboration Analysis Methods\n\n")
            f.write(f"**Date:** {self.results['analysis_date']}\n\n")

            f.write("## Method Comparison\n\n")
            f.write("| Method | Italy-China Rate | Confidence | Notes |\n")
            f.write("|--------|-----------------|------------|-------|\n")

            for method_name, result in self.results['methods'].items():
                if 'error' not in result:
                    rate = result.get('collaboration_rate', result.get('china_collaboration_rate', 'N/A'))
                    confidence = result.get('confidence', 'Unknown')
                    method = result.get('method', method_name)
                    f.write(f"| {method} | {rate}% | {confidence} | |\n")

            f.write("\n## Best Estimate\n\n")
            recon = self.results['reconciliation']
            f.write(f"- **Recommended Rate:** {recon.get('best_estimate', 'Unknown')}%\n")
            f.write(f"- **Range:** {recon.get('range', 'Unknown')}\n")
            f.write(f"- **Recommendation:** {recon.get('recommendation', '')}\n")

        logger.info(f"Summary saved to {summary_file}")

def main():
    analyzer = ImprovedCollaborationAnalyzer()
    results = analyzer.run_all_methods()

    print("\n=== IMPROVED COLLABORATION ANALYSIS ===")
    print(f"Date: {results['analysis_date']}\n")

    print("Results by Method:")
    for method_name, result in results['methods'].items():
        if 'error' not in result:
            rate = result.get('collaboration_rate', result.get('china_collaboration_rate', 'N/A'))
            print(f"  {method_name}: {rate}%")

    print(f"\nBest Estimate: {results['reconciliation'].get('best_estimate', 'Unknown')}%")
    print(f"Range: {results['reconciliation'].get('range', 'Unknown')}")

if __name__ == "__main__":
    main()
