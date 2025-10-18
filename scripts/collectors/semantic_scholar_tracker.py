"""
Semantic Scholar Researcher Tracker
Free API for tracking researcher movements and collaborations
No API key required - 200M+ papers, 50M+ authors
Better coverage than ORCID public API
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import pandas as pd
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class ResearchField(object):
    """Research fields with China sensitivity levels"""
    CRITICAL = {
        "quantum computing", "quantum information", "quantum cryptography",
        "artificial intelligence", "machine learning", "deep learning",
        "hypersonics", "scramjet", "hypersonic vehicle",
        "semiconductor", "photonics", "integrated circuits",
        "nuclear fusion", "nuclear physics", "particle physics",
        "biotechnology", "synthetic biology", "gene editing",
        "nanotechnology", "metamaterials", "graphene"
    }

    SENSITIVE = {
        "robotics", "autonomous systems", "computer vision",
        "5G", "6G", "wireless communication",
        "cybersecurity", "cryptography", "network security",
        "aerospace", "satellite", "space technology",
        "energy storage", "battery technology", "fuel cells",
        "advanced materials", "composites", "ceramics"
    }

class SemanticScholarTracker:
    """
    Track researcher movements and collaborations using Semantic Scholar
    Completely free, no authentication required
    """

    def __init__(self, country_iso3: str):
        self.country = country_iso3
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.output_dir = Path(f"artifacts/{country_iso3}/phase08_talent")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Map country codes to names for search
        self.country_names = {
            "ITA": "Italy",
            "USA": "United States",
            "CHN": "China",
            "GBR": "United Kingdom",
            "DEU": "Germany",
            "FRA": "France"
        }

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OSINT-Foresight/1.0 (research purposes)"
        })

        # Rate limiting - Semantic Scholar allows 100 requests/second
        self.last_request_time = 0
        self.min_request_interval = 0.01  # 100 requests/second

    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def search_authors(self, query: str, limit: int = 100) -> List[Dict]:
        """
        Search for authors by name or affiliation

        Args:
            query: Search query (name or institution)
            limit: Maximum results

        Returns:
            List of author records
        """
        self._rate_limit()

        try:
            url = f"{self.base_url}/author/search"
            params = {
                "query": query,
                "limit": limit,
                "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex"
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching authors: {e}")
            return []

    def get_author_details(self, author_id: str) -> Optional[Dict]:
        """
        Get detailed author information including papers

        Args:
            author_id: Semantic Scholar author ID

        Returns:
            Author details with recent papers
        """
        self._rate_limit()

        try:
            url = f"{self.base_url}/author/{author_id}"
            params = {
                "fields": "authorId,name,aliases,affiliations,homepage,paperCount,citationCount,hIndex,papers.title,papers.year,papers.venue,papers.authors,papers.fieldsOfStudy,papers.citationCount"
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching author {author_id}: {e}")
            return None

    def track_author_movement(self, author_id: str) -> Dict:
        """
        Track an author's institutional movements based on paper affiliations

        Args:
            author_id: Semantic Scholar author ID

        Returns:
            Movement history with China collaboration flags
        """
        author_data = self.get_author_details(author_id)
        if not author_data:
            return {}

        movements = {
            "author_id": author_id,
            "name": author_data.get('name'),
            "current_affiliations": author_data.get('affiliations', []),
            "total_papers": author_data.get('paperCount', 0),
            "citations": author_data.get('citationCount', 0),
            "h_index": author_data.get('hIndex', 0),
            "timeline": [],
            "china_collaborations": [],
            "sensitive_research": [],
            "risk_indicators": []
        }

        # Analyze papers for affiliation changes and collaborations
        papers = author_data.get('papers', [])
        affiliation_timeline = defaultdict(list)

        for paper in papers:
            year = paper.get('year')
            if not year:
                continue

            # Check for Chinese co-authors
            has_chinese_coauthor = False
            chinese_institutions = []

            for coauthor in paper.get('authors', []):
                # Check if co-author has Chinese affiliation
                for affiliation in coauthor.get('affiliations', []):
                    if any(cn in affiliation.lower() for cn in ['china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'tsinghua', 'peking']):
                        has_chinese_coauthor = True
                        chinese_institutions.append(affiliation)

            if has_chinese_coauthor:
                movements['china_collaborations'].append({
                    "year": year,
                    "title": paper.get('title'),
                    "chinese_institutions": list(set(chinese_institutions)),
                    "citation_count": paper.get('citationCount', 0)
                })

            # Check for sensitive research areas
            fields = paper.get('fieldsOfStudy', [])
            for field in fields:
                field_lower = field.lower()
                if any(critical in field_lower for critical in ResearchField.CRITICAL):
                    movements['sensitive_research'].append({
                        "year": year,
                        "field": field,
                        "sensitivity": "CRITICAL",
                        "title": paper.get('title'),
                        "has_chinese_coauthor": has_chinese_coauthor
                    })
                elif any(sensitive in field_lower for sensitive in ResearchField.SENSITIVE):
                    movements['sensitive_research'].append({
                        "year": year,
                        "field": field,
                        "sensitivity": "SENSITIVE",
                        "title": paper.get('title'),
                        "has_chinese_coauthor": has_chinese_coauthor
                    })

        # Assess risk indicators
        if movements['china_collaborations']:
            movements['risk_indicators'].append(f"Chinese collaborations: {len(movements['china_collaborations'])} papers")

        critical_with_china = [s for s in movements['sensitive_research']
                              if s['sensitivity'] == 'CRITICAL' and s['has_chinese_coauthor']]
        if critical_with_china:
            movements['risk_indicators'].append(f"CRITICAL: {len(critical_with_china)} sensitive papers with Chinese co-authors")

        return movements

    def analyze_institution_talent_flow(self, institution: str, years: int = 5) -> Dict:
        """
        Analyze talent flows for an institution

        Args:
            institution: Institution name
            years: Years to analyze

        Returns:
            Talent flow analysis
        """
        # Search for authors at this institution
        authors = self.search_authors(institution, limit=100)

        analysis = {
            "institution": institution,
            "period": f"{datetime.now().year - years}-{datetime.now().year}",
            "total_researchers": len(authors),
            "talent_flows": {
                "to_china": [],
                "from_china": [],
                "internal_moves": []
            },
            "collaboration_metrics": {
                "china_collaborators": [],
                "high_impact_china_papers": [],
                "sensitive_field_overlaps": []
            }
        }

        # Sample analysis of top researchers
        for author in authors[:20]:  # Analyze top 20 by citations
            author_id = author.get('authorId')
            if not author_id:
                continue

            logger.info(f"Analyzing researcher: {author.get('name')}")
            movement = self.track_author_movement(author_id)

            # Identify concerning patterns
            if movement.get('china_collaborations'):
                analysis['collaboration_metrics']['china_collaborators'].append({
                    "name": movement['name'],
                    "papers_with_china": len(movement['china_collaborations']),
                    "sensitive_overlaps": len([s for s in movement.get('sensitive_research', [])
                                              if s.get('has_chinese_coauthor')])
                })

            # High-impact China collaborations
            high_impact = [c for c in movement.get('china_collaborations', [])
                          if c.get('citation_count', 0) > 100]
            if high_impact:
                analysis['collaboration_metrics']['high_impact_china_papers'].extend(high_impact)

        return analysis

    def find_china_linked_researchers(self, institution: str, field: Optional[str] = None) -> List[Dict]:
        """
        Find researchers at an institution with China links

        Args:
            institution: Institution name
            field: Optional field filter

        Returns:
            List of researchers with China connections
        """
        query = institution
        if field:
            query += f" {field}"

        authors = self.search_authors(query, limit=50)
        china_linked = []

        for author in authors:
            author_id = author.get('authorId')
            if not author_id:
                continue

            # Get recent papers
            author_details = self.get_author_details(author_id)
            if not author_details:
                continue

            papers = author_details.get('papers', [])[:10]  # Check recent 10 papers

            china_papers = []
            for paper in papers:
                # Check for Chinese co-authors or venues
                for coauthor in paper.get('authors', []):
                    affiliations = coauthor.get('affiliations', [])
                    if any('china' in aff.lower() or 'chinese' in aff.lower() for aff in affiliations):
                        china_papers.append({
                            "title": paper.get('title'),
                            "year": paper.get('year'),
                            "venue": paper.get('venue')
                        })
                        break

            if china_papers:
                china_linked.append({
                    "name": author_details.get('name'),
                    "author_id": author_id,
                    "affiliations": author_details.get('affiliations', []),
                    "total_papers": author_details.get('paperCount'),
                    "china_papers": china_papers,
                    "china_collaboration_rate": len(china_papers) / len(papers) * 100
                })

        return china_linked

    def detect_talent_program_participants(self, authors: List[str]) -> List[Dict]:
        """
        Detect potential talent program participants based on patterns

        Args:
            authors: List of author names or IDs

        Returns:
            Suspicious patterns indicating talent program participation
        """
        suspects = []

        for author_query in authors:
            # Search for the author
            search_results = self.search_authors(author_query, limit=5)
            if not search_results:
                continue

            author_id = search_results[0].get('authorId')
            movement = self.track_author_movement(author_id)

            suspicious_patterns = []

            # Pattern 1: Sudden increase in China collaborations
            china_collab_years = [c['year'] for c in movement.get('china_collaborations', [])]
            if china_collab_years:
                china_collab_years.sort()
                if len(china_collab_years) >= 3:
                    recent_rate = len([y for y in china_collab_years if y >= datetime.now().year - 2])
                    if recent_rate >= len(china_collab_years) * 0.6:
                        suspicious_patterns.append("Sudden increase in China collaborations")

            # Pattern 2: Sensitive research with China
            sensitive_with_china = [s for s in movement.get('sensitive_research', [])
                                   if s.get('has_chinese_coauthor') and s.get('sensitivity') == 'CRITICAL']
            if sensitive_with_china:
                suspicious_patterns.append(f"Critical research with China: {len(sensitive_with_china)} papers")

            # Pattern 3: Dual affiliations
            affiliations = movement.get('current_affiliations', [])
            if any('china' in aff.lower() for aff in affiliations) and len(affiliations) > 1:
                suspicious_patterns.append("Dual affiliations including China")

            if suspicious_patterns:
                suspects.append({
                    "name": movement.get('name'),
                    "author_id": author_id,
                    "patterns": suspicious_patterns,
                    "risk_score": len(suspicious_patterns) * 10,  # Simple scoring
                    "china_papers": len(movement.get('china_collaborations', [])),
                    "sensitive_papers": len(movement.get('sensitive_research', []))
                })

        return suspects

    def generate_talent_risk_report(self, institutions: List[str]) -> Dict:
        """
        Generate comprehensive talent risk report for country

        Args:
            institutions: List of institutions to analyze

        Returns:
            Talent risk assessment report
        """
        timestamp = datetime.now().isoformat()

        report = {
            "generated_at": timestamp,
            "country": self.country,
            "institutions_analyzed": len(institutions),
            "institution_reports": {},
            "aggregate_risks": {
                "high_risk_researchers": [],
                "talent_program_suspects": [],
                "sensitive_collaborations": []
            },
            "recommendations": []
        }

        for institution in institutions:
            logger.info(f"Analyzing talent risks for {institution}")

            # Find China-linked researchers
            china_linked = self.find_china_linked_researchers(institution)

            # Analyze talent flows
            talent_flow = self.analyze_institution_talent_flow(institution, years=3)

            report['institution_reports'][institution] = {
                "china_linked_researchers": len(china_linked),
                "high_collaboration_rate": [r for r in china_linked
                                           if r.get('china_collaboration_rate', 0) > 30],
                "talent_flow_summary": talent_flow.get('collaboration_metrics', {})
            }

            # Aggregate high-risk individuals
            for researcher in china_linked:
                if researcher.get('china_collaboration_rate', 0) > 50:
                    report['aggregate_risks']['high_risk_researchers'].append({
                        "name": researcher['name'],
                        "institution": institution,
                        "china_collaboration_rate": researcher['china_collaboration_rate'],
                        "china_papers": len(researcher.get('china_papers', []))
                    })

        # Generate recommendations
        if report['aggregate_risks']['high_risk_researchers']:
            report['recommendations'].append(
                f"URGENT: {len(report['aggregate_risks']['high_risk_researchers'])} researchers "
                f"with >50% China collaboration rate require security review"
            )

        total_china_linked = sum(
            inst_report.get('china_linked_researchers', 0)
            for inst_report in report['institution_reports'].values()
        )

        if total_china_linked > 10:
            report['recommendations'].append(
                f"Monitor {total_china_linked} researchers with established China connections"
            )

        # Save report
        output_file = self.output_dir / "talent_risk_assessment.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Talent risk report saved to {output_file}")

        return report

def main():
    """Test Semantic Scholar talent tracking"""
    import sys

    country = sys.argv[1] if len(sys.argv) > 1 else "ITA"

    # Italian institutions to analyze
    test_institutions = [
        "Politecnico di Milano",
        "University of Bologna",
        "Sapienza University of Rome"
    ]

    tracker = SemanticScholarTracker(country)

    print(f"\n=== Semantic Scholar Talent Analysis for {country} ===\n")

    # Test single institution
    if test_institutions:
        institution = test_institutions[0]
        print(f"Analyzing: {institution}")

        # Find China-linked researchers
        print("\nSearching for China-linked researchers...")
        china_linked = tracker.find_china_linked_researchers(institution, field="artificial intelligence")

        if china_linked:
            print(f"Found {len(china_linked)} researchers with China connections:")
            for researcher in china_linked[:3]:  # Show top 3
                print(f"\n  {researcher['name']}:")
                print(f"    - Total papers: {researcher['total_papers']}")
                print(f"    - China collaboration rate: {researcher['china_collaboration_rate']:.1f}%")
                print(f"    - Recent China papers: {len(researcher['china_papers'])}")

        # Test talent flow analysis
        print(f"\n\nAnalyzing talent flows for {institution}...")
        flow_analysis = tracker.analyze_institution_talent_flow(institution, years=3)

        if flow_analysis['collaboration_metrics']['china_collaborators']:
            print(f"China collaborators: {len(flow_analysis['collaboration_metrics']['china_collaborators'])}")
            for collab in flow_analysis['collaboration_metrics']['china_collaborators'][:3]:
                print(f"  - {collab['name']}: {collab['papers_with_china']} papers")
                if collab.get('sensitive_overlaps'):
                    print(f"    ⚠️  {collab['sensitive_overlaps']} in sensitive fields!")

    # Generate full report
    if len(test_institutions) > 1:
        print("\n\nGenerating comprehensive talent risk report...")
        report = tracker.generate_talent_risk_report(test_institutions[:2])  # Limit for testing

        print(f"\nReport Summary:")
        print(f"Institutions analyzed: {report['institutions_analyzed']}")
        print(f"High-risk researchers: {len(report['aggregate_risks']['high_risk_researchers'])}")

        if report['recommendations']:
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
