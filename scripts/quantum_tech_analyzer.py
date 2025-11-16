"""
Quantum Technology Foresight Analyzer
NO FABRICATION - Only report verified data with sources
"""

import gzip
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

class QuantumAnalyzer:
    def __init__(self):
        self.openalex_path = Path("F:/OSINT_Backups/openalex/data/works")
        self.quantum_keywords = [
            'quantum computing', 'quantum computer', 'quantum algorithm',
            'quantum sensing', 'quantum sensor', 'quantum metrology',
            'quantum communication', 'quantum cryptography', 'quantum key distribution',
            'quantum network', 'qubit', 'qubits', 'quantum entanglement',
            'quantum supremacy', 'quantum advantage', 'quantum error correction',
            'superconducting qubit', 'topological qubit', 'ion trap',
            'quantum annealing', 'quantum simulation', 'quantum machine learning',
            'dilution refrigerator', 'cryogenic', 'quantum material',
            'photonic quantum', 'quantum dot', 'quantum well'
        ]

        self.results = {
            'publications': [],
            'institutions': defaultdict(int),
            'countries': defaultdict(int),
            'funding_sources': defaultdict(int),
            'topics': defaultdict(int),
            'collaborations': [],
            'sources': []
        }

    def is_quantum_related(self, text):
        """Check if text contains quantum keywords"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.quantum_keywords)

    def extract_date_from_path(self, path_str):
        """Extract date from OpenAlex file path"""
        match = re.search(r'updated_date=(\d{4}-\d{2}-\d{2})', str(path_str))
        if match:
            return match.group(1)
        return None

    def process_work(self, work, source_file):
        """Process a single OpenAlex work record"""
        try:
            # Check title and abstract for quantum keywords
            title = work.get('title', '')
            abstract = work.get('abstract_inverted_index', {})

            # Reconstruct abstract from inverted index
            abstract_text = ''
            if abstract:
                words_positions = []
                for word, positions in abstract.items():
                    for pos in positions:
                        words_positions.append((pos, word))
                words_positions.sort()
                abstract_text = ' '.join([word for _, word in words_positions])

            combined_text = f"{title} {abstract_text}"

            if not self.is_quantum_related(combined_text):
                return False

            # Extract publication date
            pub_date = work.get('publication_date', '')
            pub_year = work.get('publication_year', 0)

            # Only include recent publications (2023-2025)
            if pub_year < 2023:
                return False

            # Extract institutions and countries
            authorships = work.get('authorships', [])
            institutions_list = []
            countries_list = []

            for authorship in authorships:
                for institution in authorship.get('institutions', []):
                    inst_name = institution.get('display_name', '')
                    inst_country = institution.get('country_code', '')

                    if inst_name:
                        institutions_list.append(inst_name)
                        self.results['institutions'][inst_name] += 1

                    if inst_country:
                        countries_list.append(inst_country)
                        self.results['countries'][inst_country] += 1

            # Extract funding information
            grants = work.get('grants', [])
            for grant in grants:
                funder = grant.get('funder_display_name', '')
                if funder:
                    self.results['funding_sources'][funder] += 1

            # Extract topics/concepts
            concepts = work.get('concepts', [])
            for concept in concepts[:5]:  # Top 5 concepts
                concept_name = concept.get('display_name', '')
                if concept_name:
                    self.results['topics'][concept_name] += 1

            # Store publication details
            pub_record = {
                'id': work.get('id', ''),
                'title': title,
                'year': pub_year,
                'date': pub_date,
                'doi': work.get('doi', ''),
                'institutions': institutions_list,
                'countries': list(set(countries_list)),
                'funders': [g.get('funder_display_name', '') for g in grants],
                'cited_by_count': work.get('cited_by_count', 0),
                'source_file': str(source_file)
            }

            self.results['publications'].append(pub_record)

            # Track international collaborations
            unique_countries = list(set(countries_list))
            if len(unique_countries) > 1:
                self.results['collaborations'].append({
                    'title': title,
                    'countries': unique_countries,
                    'year': pub_year
                })

            return True

        except Exception as e:
            print(f"Error processing work: {e}")
            return False

    def search_openalex_files(self, year_filter=None, max_files=100):
        """Search through OpenAlex compressed files for quantum research"""
        print(f"[{datetime.now()}] Starting OpenAlex quantum search...")
        print(f"Base path: {self.openalex_path}")

        # Find all .gz files, filter by year if specified
        all_files = list(self.openalex_path.rglob("*.gz"))
        print(f"Found {len(all_files)} total files")

        # Filter to 2023+ files
        target_files = []
        for f in all_files:
            date_str = self.extract_date_from_path(f)
            if date_str and date_str >= '2023-01-01':
                target_files.append(f)

        target_files.sort(reverse=True)  # Most recent first
        target_files = target_files[:max_files]

        print(f"Processing {len(target_files)} files from 2023-2025...")

        processed_files = 0
        quantum_papers_found = 0

        for file_path in target_files:
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        try:
                            work = json.loads(line.strip())
                            if self.process_work(work, file_path):
                                quantum_papers_found += 1
                        except json.JSONDecodeError:
                            continue

                processed_files += 1
                if processed_files % 10 == 0:
                    print(f"Processed {processed_files}/{len(target_files)} files, found {quantum_papers_found} quantum papers")

            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

        print(f"\n[{datetime.now()}] Search complete!")
        print(f"Files processed: {processed_files}")
        print(f"Quantum papers found: {quantum_papers_found}")

        # Record sources
        self.results['sources'].append({
            'source': 'OpenAlex',
            'path': str(self.openalex_path),
            'files_processed': processed_files,
            'date_range': '2023-2025',
            'search_date': datetime.now().isoformat(),
            'papers_found': quantum_papers_found
        })

    def generate_report(self, output_path):
        """Generate JSON report of findings"""

        # Sort results
        top_institutions = sorted(self.results['institutions'].items(),
                                 key=lambda x: x[1], reverse=True)[:50]
        top_countries = sorted(self.results['countries'].items(),
                              key=lambda x: x[1], reverse=True)[:30]
        top_funders = sorted(self.results['funding_sources'].items(),
                            key=lambda x: x[1], reverse=True)[:30]
        top_topics = sorted(self.results['topics'].items(),
                           key=lambda x: x[1], reverse=True)[:50]

        report = {
            'search_metadata': {
                'date': datetime.now().isoformat(),
                'total_publications_found': len(self.results['publications']),
                'keywords_searched': self.quantum_keywords,
                'data_sources': self.results['sources']
            },
            'publications_summary': {
                'total': len(self.results['publications']),
                'most_cited': sorted(self.results['publications'],
                                    key=lambda x: x['cited_by_count'],
                                    reverse=True)[:20],
                'by_year': self._count_by_year()
            },
            'leading_institutions': [
                {'name': name, 'publications': count}
                for name, count in top_institutions
            ],
            'countries': [
                {'code': code, 'publications': count}
                for code, count in top_countries
            ],
            'major_funders': [
                {'name': name, 'funded_publications': count}
                for name, count in top_funders
            ],
            'top_topics': [
                {'topic': topic, 'occurrences': count}
                for topic, count in top_topics
            ],
            'international_collaborations': {
                'total': len(self.results['collaborations']),
                'examples': self.results['collaborations'][:50]
            },
            'all_publications': self.results['publications']
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to: {output_path}")
        return report

    def _count_by_year(self):
        """Count publications by year"""
        by_year = defaultdict(int)
        for pub in self.results['publications']:
            by_year[pub['year']] += 1
        return dict(sorted(by_year.items()))

if __name__ == '__main__':
    analyzer = QuantumAnalyzer()

    # Search through recent OpenAlex files (limit to 100 files for performance)
    analyzer.search_openalex_files(max_files=100)

    # Generate report
    output_path = "C:/Projects/OSINT - Foresight/analysis/quantum_tech/openalex_quantum_analysis.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    report = analyzer.generate_report(output_path)

    print("\n=== SUMMARY ===")
    print(f"Total quantum publications found: {report['search_metadata']['total_publications_found']}")
    print(f"Top 5 institutions:")
    for inst in report['leading_institutions'][:5]:
        print(f"  - {inst['name']}: {inst['publications']} papers")
    print(f"\nTop 5 countries:")
    for country in report['countries'][:5]:
        print(f"  - {country['code']}: {country['publications']} papers")
    print(f"\nTop 5 funders:")
    for funder in report['major_funders'][:5]:
        print(f"  - {funder['name']}: {funder['funded_publications']} papers")
