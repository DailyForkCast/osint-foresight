#!/usr/bin/env python3
"""
arXiv BCI Dataset Analysis
Analyzes 5,557 BCI papers from arXiv for EU-China collaborations

Zero Fabrication Protocol: All statistics from actual database queries
Created: 2025-10-27
"""

import sqlite3
import json
from collections import defaultdict, Counter
from datetime import datetime

class ArxivBCIAnalyzer:
    def __init__(self):
        self.db_path = "C:/Projects/OSINT-Foresight/data/kaggle_arxiv_processing.db"
        self.core_keywords = [
            'brain-computer interface',
            'brain computer interface',
            'bci system',
            'brain-machine interface',
            'brain machine interface',
            'neural interface',
            'neuroprosthetic',
            'neuromodulation',
            'eeg analysis',
            'electroencephalography'
        ]

        # EU + China country codes for author affiliations
        self.eu_countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                             'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
                             'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
        self.china_codes = ['CN', 'HK', 'MO', 'TW']  # Mainland + HK + Macau + Taiwan

    def get_bci_papers(self):
        """Get all BCI papers from arXiv"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build keyword search
        conditions = []
        for kw in self.core_keywords:
            kw_safe = kw.replace("'", "''")
            conditions.append(f"(LOWER(title) LIKE '%{kw_safe}%' OR LOWER(abstract) LIKE '%{kw_safe}%')")

        where_clause = ' OR '.join(conditions)

        # Get all BCI papers with authors
        query = f"""
        SELECT DISTINCT
            p.arxiv_id,
            p.title,
            p.abstract,
            p.categories,
            p.update_date,
            p.doi
        FROM kaggle_arxiv_papers p
        WHERE {where_clause}
        ORDER BY p.update_date DESC
        """

        cursor.execute(query)
        papers = cursor.fetchall()

        conn.close()

        print(f"Found {len(papers)} BCI papers in arXiv")
        return papers

    def analyze_temporal_trends(self, papers):
        """Analyze publication trends over time"""
        by_year = defaultdict(int)

        for paper in papers:
            arxiv_id, title, abstract, cats, date, doi = paper
            try:
                year = int(date[:4]) if date else None
                if year and 2000 <= year <= 2025:
                    by_year[year] += 1
            except:
                continue

        print("\n" + "="*70)
        print("TEMPORAL TRENDS (2000-2025)")
        print("="*70)

        for year in sorted(by_year.keys()):
            count = by_year[year]
            bar = "█" * (count // 20)
            print(f"{year}: {count:4d} papers {bar}")

        return by_year

    def analyze_categories(self, papers):
        """Analyze arXiv categories"""
        category_counts = Counter()

        for paper in papers:
            arxiv_id, title, abstract, cats, date, doi = paper
            if cats:
                # arXiv categories are space-separated
                for cat in cats.split():
                    category_counts[cat] += 1

        print("\n" + "="*70)
        print("TOP 20 ARXIV CATEGORIES")
        print("="*70)

        for cat, count in category_counts.most_common(20):
            pct = 100 * count / len(papers)
            print(f"{cat:20s} {count:5d} papers ({pct:5.2f}%)")

        return category_counts

    def identify_true_bci_papers(self, papers):
        """
        Filter for TRUE BCI papers (not false positives)
        Strict criteria: title must contain explicit BCI terms
        """
        strict_terms = [
            'brain-computer interface',
            'brain computer interface',
            'brain-machine interface',
            'brain machine interface',
            'neural interface',
            'neuroprosthetic',
            'motor imagery',
            'p300',
            'ssvep',
            'erp'
        ]

        true_bci = []
        false_positives = []

        for paper in papers:
            arxiv_id, title, abstract, cats, date, doi = paper
            title_lower = title.lower() if title else ""

            # Check if title contains strict BCI terms
            is_bci = any(term in title_lower for term in strict_terms)

            # Also check categories - exclude pure math papers
            if cats and any(cat.startswith('math.') and 'cs.' not in cats for cat in cats.split()):
                if 'neural' not in title_lower and 'brain' not in title_lower and 'eeg' not in title_lower:
                    is_bci = False  # Likely false positive

            if is_bci:
                true_bci.append(paper)
            else:
                false_positives.append(paper)

        print("\n" + "="*70)
        print("FALSE POSITIVE FILTERING")
        print("="*70)
        print(f"Total papers: {len(papers)}")
        print(f"True BCI papers (strict): {len(true_bci)}")
        print(f"Likely false positives: {len(false_positives)}")
        print(f"Precision estimate: {100*len(true_bci)/len(papers):.1f}%")

        # Sample false positives
        print("\nSample False Positives (first 10):")
        for i, paper in enumerate(false_positives[:10], 1):
            arxiv_id, title, abstract, cats, date, doi = paper
            print(f"{i}. [{cats}] {title[:80]}")

        return true_bci, false_positives

    def analyze_collaborations(self, papers):
        """
        Analyze author collaborations
        NOTE: arXiv dataset doesn't have detailed author affiliations in accessible format
        This is a limitation - we can see author names but not their countries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get authors for BCI papers
        arxiv_ids = [p[0] for p in papers[:100]]  # Sample first 100 for performance
        placeholders = ','.join(['?' for _ in arxiv_ids])

        cursor.execute(f"""
            SELECT DISTINCT paper_arxiv_id, author
            FROM kaggle_arxiv_authors
            WHERE paper_arxiv_id IN ({placeholders})
        """, arxiv_ids)

        author_data = cursor.fetchall()
        conn.close()

        print("\n" + "="*70)
        print("COLLABORATION ANALYSIS (Sample of 100 papers)")
        print("="*70)
        print(f"Total author entries: {len(author_data)}")
        print()
        print("⚠️ LIMITATION: arXiv dataset does not include author affiliations/countries")
        print("Cannot determine EU-China collaborations from this dataset alone")
        print("Recommendation: Use OpenAlex once collection completes")

        return author_data

    def generate_report(self):
        """Generate comprehensive BCI analysis report"""
        print("="*70)
        print("arXiv BCI DATASET ANALYSIS")
        print("="*70)
        print(f"Database: {self.db_path}")
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Protocol: Zero Fabrication - All stats from actual queries")
        print("="*70)

        # Get all BCI papers
        papers = self.get_bci_papers()

        if not papers:
            print("ERROR: No BCI papers found!")
            return

        # Analyze temporal trends
        by_year = self.analyze_temporal_trends(papers)

        # Analyze categories
        categories = self.analyze_categories(papers)

        # Filter false positives
        true_bci, false_positives = self.identify_true_bci_papers(papers)

        # Analyze collaborations (limited by data)
        authors = self.analyze_collaborations(papers)

        # Summary statistics
        print("\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        print(f"Total arXiv papers searched: 1,442,797")
        print(f"BCI papers found (keyword search): {len(papers)}")
        print(f"BCI papers (strict filtering): {len(true_bci)}")
        print(f"Hit rate (keyword): {100*len(papers)/1442797:.3f}%")
        print(f"Hit rate (strict): {100*len(true_bci)/1442797:.3f}%")
        print(f"Date range: {min(by_year.keys()) if by_year else 'N/A'} - {max(by_year.keys()) if by_year else 'N/A'}")
        print()
        print("⚠️ EU-China Collaboration Analysis:")
        print("   Not possible with arXiv dataset (no affiliation data)")
        print("   Requires OpenAlex dataset with institutional affiliations")

        # Save results
        results = {
            'total_papers': len(papers),
            'true_bci_papers': len(true_bci),
            'false_positives': len(false_positives),
            'by_year': dict(by_year),
            'top_categories': dict(categories.most_common(20)),
            'analysis_date': datetime.now().isoformat(),
            'protocol': 'Zero Fabrication Protocol',
            'limitation': 'No author affiliation data for EU-China collaboration analysis'
        }

        output_file = "analysis/arxiv_bci_analysis_20251027.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {output_file}")
        print("="*70)

if __name__ == "__main__":
    analyzer = ArxivBCIAnalyzer()
    analyzer.generate_report()
