"""
Quantum Research Institution Enrichment Tool
Systematically enriches quantum research reports with comprehensive institution data.

This script addresses the "No institution data available" problem by:
1. Extracting institution information from OpenAlex quantum analysis
2. Computing institution-level metrics (publications, citations, collaborations)
3. Identifying China collaboration patterns at the institution level
4. Generating risk assessments for each institution
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class QuantumInstitutionEnricher:
    def __init__(self):
        self.base_path = Path("C:/Projects/OSINT - Foresight")
        self.quantum_data_path = self.base_path / "analysis/quantum_tech/openalex_quantum_analysis.json"
        self.output_path = self.base_path / "analysis/QUANTUM_INSTITUTIONS_ENRICHED.json"

        # European country codes
        self.european_countries = {
            'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE',
            'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT',
            'RO', 'SK', 'SI', 'ES', 'SE', 'GB', 'NO', 'CH', 'IS'
        }

        # China country codes
        self.china_codes = {'CN', 'CHN'}

        # Institution-level data structures
        self.institutions = defaultdict(lambda: {
            'name': '',
            'countries': set(),
            'publications': [],
            'total_citations': 0,
            'china_collaborations': 0,
            'total_collaborations': 0,
            'collaboration_partners': defaultdict(int),
            'years_active': set(),
            'topics': defaultdict(int)
        })

    def load_quantum_data(self):
        """Load existing quantum research data"""
        print(f"Loading quantum data from: {self.quantum_data_path}")

        if not self.quantum_data_path.exists():
            raise FileNotFoundError(f"Quantum data file not found: {self.quantum_data_path}")

        with open(self.quantum_data_path, 'r', encoding='utf-8') as f:
            self.quantum_data = json.load(f)

        print(f"Loaded {len(self.quantum_data.get('all_publications', []))} quantum publications")

    def extract_institution_data(self):
        """Extract and aggregate institution-level data from publications"""
        print("\nExtracting institution data from publications...")

        publications = self.quantum_data.get('all_publications', [])

        for pub in publications:
            pub_institutions = pub.get('institutions', [])
            pub_countries = pub.get('countries', [])
            pub_citations = pub.get('cited_by_count', 0)
            pub_year = pub.get('year', 0)

            # Check if this is a China collaboration
            has_china = any(c in self.china_codes for c in pub_countries)

            # Process each institution in the publication
            for inst_name in pub_institutions:
                if not inst_name:
                    continue

                # Initialize or update institution record
                inst = self.institutions[inst_name]
                inst['name'] = inst_name

                # Add countries (institutions can appear in multiple countries)
                inst['countries'].update(pub_countries)

                # Track publication
                inst['publications'].append({
                    'title': pub.get('title', ''),
                    'year': pub_year,
                    'doi': pub.get('doi', ''),
                    'citations': pub_citations,
                    'has_china': has_china,
                    'countries': pub_countries
                })

                # Aggregate metrics
                inst['total_citations'] += pub_citations
                inst['years_active'].add(pub_year)

                # Track collaborations
                if len(pub_countries) > 1:
                    inst['total_collaborations'] += 1
                    if has_china:
                        inst['china_collaborations'] += 1

                    # Track specific collaboration partners
                    for country in pub_countries:
                        inst['collaboration_partners'][country] += 1

        print(f"Extracted data for {len(self.institutions)} unique institutions")

    def compute_institution_metrics(self):
        """Compute derived metrics for each institution"""
        print("\nComputing institution metrics...")

        enriched_institutions = []

        for inst_name, inst_data in self.institutions.items():
            num_pubs = len(inst_data['publications'])

            # Determine primary country (most common)
            country_counts = defaultdict(int)
            for pub in inst_data['publications']:
                for country in pub['countries']:
                    country_counts[country] += 1

            primary_country = max(country_counts.items(), key=lambda x: x[1])[0] if country_counts else 'UNKNOWN'

            # Calculate collaboration rate
            collab_rate = (inst_data['china_collaborations'] / num_pubs * 100) if num_pubs > 0 else 0

            # Determine if European institution
            is_european = primary_country in self.european_countries

            # Calculate risk score
            risk_score = self._calculate_risk_score(
                collab_rate,
                inst_data['china_collaborations'],
                num_pubs,
                is_european
            )

            # Calculate average citations
            avg_citations = inst_data['total_citations'] / num_pubs if num_pubs > 0 else 0

            # Build enriched record
            enriched = {
                'institution_name': inst_name,
                'primary_country': primary_country,
                'is_european': is_european,
                'total_publications': num_pubs,
                'total_citations': inst_data['total_citations'],
                'average_citations': round(avg_citations, 2),
                'china_collaborations': inst_data['china_collaborations'],
                'total_collaborations': inst_data['total_collaborations'],
                'china_collaboration_rate': round(collab_rate, 2),
                'risk_score': risk_score,
                'risk_level': self._get_risk_level(risk_score),
                'years_active': sorted(list(inst_data['years_active'])),
                'year_range': f"{min(inst_data['years_active'])}-{max(inst_data['years_active'])}" if inst_data['years_active'] else '',
                'collaboration_partners': dict(sorted(
                    inst_data['collaboration_partners'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),  # Top 10 partners
                'top_publications': sorted(
                    inst_data['publications'],
                    key=lambda x: x['citations'],
                    reverse=True
                )[:5]  # Top 5 most cited
            }

            enriched_institutions.append(enriched)

        # Sort by publication count
        enriched_institutions.sort(key=lambda x: x['total_publications'], reverse=True)

        return enriched_institutions

    def _calculate_risk_score(self, collab_rate, china_collabs, total_pubs, is_european):
        """
        Calculate risk score (0-100) based on:
        - China collaboration rate (0-40 points)
        - Absolute number of China collaborations (0-30 points)
        - Volume of quantum research (0-20 points)
        - European location (0-10 points bonus risk)
        """
        score = 0

        # Collaboration rate contribution (0-40)
        score += min(collab_rate, 40)

        # Absolute collaboration count (0-30)
        if china_collabs >= 50:
            score += 30
        elif china_collabs >= 20:
            score += 20
        elif china_collabs >= 10:
            score += 15
        elif china_collabs >= 5:
            score += 10
        elif china_collabs >= 1:
            score += 5

        # Research volume indicator (0-20)
        if total_pubs >= 100:
            score += 20
        elif total_pubs >= 50:
            score += 15
        elif total_pubs >= 20:
            score += 10
        elif total_pubs >= 10:
            score += 5

        # European institution bonus (higher strategic concern)
        if is_european and china_collabs > 0:
            score += 10

        return min(score, 100)

    def _get_risk_level(self, risk_score):
        """Convert numeric risk score to categorical level"""
        if risk_score >= 70:
            return 'CRITICAL'
        elif risk_score >= 50:
            return 'HIGH'
        elif risk_score >= 30:
            return 'MEDIUM'
        elif risk_score >= 10:
            return 'LOW'
        else:
            return 'MINIMAL'

    def generate_summary_statistics(self, institutions):
        """Generate summary statistics across all institutions"""
        european_insts = [i for i in institutions if i['is_european']]
        european_with_china = [i for i in european_insts if i['china_collaborations'] > 0]

        china_collabs = [i for i in institutions if i['china_collaborations'] > 0]

        return {
            'total_institutions': len(institutions),
            'european_institutions': len(european_insts),
            'european_with_china_collabs': len(european_with_china),
            'institutions_with_china': len(china_collabs),
            'total_quantum_publications': sum(i['total_publications'] for i in institutions),
            'total_citations': sum(i['total_citations'] for i in institutions),
            'total_china_collaborations': sum(i['china_collaborations'] for i in institutions),
            'top_10_institutions': [
                {
                    'name': i['institution_name'],
                    'country': i['primary_country'],
                    'publications': i['total_publications'],
                    'china_collabs': i['china_collaborations']
                }
                for i in institutions[:10]
            ],
            'top_10_european': [
                {
                    'name': i['institution_name'],
                    'country': i['primary_country'],
                    'publications': i['total_publications'],
                    'china_collabs': i['china_collaborations'],
                    'risk_level': i['risk_level']
                }
                for i in european_insts[:10]
            ],
            'highest_risk_institutions': sorted(
                institutions,
                key=lambda x: x['risk_score'],
                reverse=True
            )[:20]
        }

    def save_enriched_data(self, institutions, summary):
        """Save enriched institution data to JSON"""
        output = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'source_file': str(self.quantum_data_path),
                'total_publications_analyzed': len(self.quantum_data.get('all_publications', [])),
                'methodology': {
                    'risk_scoring': 'Weighted scoring based on collaboration rate (40%), absolute collaborations (30%), research volume (20%), and European location bonus (10%)',
                    'institution_identification': 'Extracted from OpenAlex authorship data',
                    'country_assignment': 'Primary country determined by most frequent appearance in publications'
                }
            },
            'summary_statistics': summary,
            'institutions': institutions
        }

        print(f"\nSaving enriched data to: {self.output_path}")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Successfully saved data for {len(institutions)} institutions")

        return output

    def run(self):
        """Execute full enrichment pipeline"""
        print("="*80)
        print("QUANTUM INSTITUTION ENRICHMENT PIPELINE")
        print("="*80)

        # Load source data
        self.load_quantum_data()

        # Extract institution data
        self.extract_institution_data()

        # Compute metrics
        institutions = self.compute_institution_metrics()

        # Generate summary
        summary = self.generate_summary_statistics(institutions)

        # Save enriched data
        output = self.save_enriched_data(institutions, summary)

        # Print summary
        print("\n" + "="*80)
        print("ENRICHMENT SUMMARY")
        print("="*80)
        print(f"Total institutions: {summary['total_institutions']}")
        print(f"European institutions: {summary['european_institutions']}")
        print(f"Institutions with China collaborations: {summary['institutions_with_china']}")
        print(f"European institutions with China: {summary['european_with_china_collabs']}")
        print(f"\nTop 5 Institutions by Publication Volume:")
        for i, inst in enumerate(summary['top_10_institutions'][:5], 1):
            print(f"  {i}. {inst['name']} ({inst['country']}): {inst['publications']} pubs, {inst['china_collabs']} China collabs")

        print(f"\nTop 5 European Institutions:")
        for i, inst in enumerate(summary['top_10_european'][:5], 1):
            print(f"  {i}. {inst['name']} ({inst['country']}): {inst['publications']} pubs, Risk: {inst['risk_level']}")

        print(f"\nTop 5 Highest Risk Institutions:")
        for i, inst in enumerate(summary['highest_risk_institutions'][:5], 1):
            print(f"  {i}. {inst['institution_name']} ({inst['primary_country']})")
            print(f"      Risk: {inst['risk_level']} (Score: {inst['risk_score']})")
            print(f"      China collabs: {inst['china_collaborations']}/{inst['total_publications']} ({inst['china_collaboration_rate']}%)")

        print("\n" + "="*80)
        print(f"OUTPUT: {self.output_path}")
        print("="*80)

        return output


if __name__ == '__main__':
    enricher = QuantumInstitutionEnricher()
    enricher.run()
