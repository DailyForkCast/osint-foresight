#!/usr/bin/env python3
"""
Comprehensive PRC Intelligence Analysis v2.1
Cross-references ALL data sources:
- PSC (UK Companies House): 209,061 detections
- CORDIS v1 (EU Research): 407 detections
- OpenAIRE v1 (Publications): 321 detections
- TED (EU Procurement): Variable
- USAspending (US Contracts): Variable
- OpenAlex V5 (Academic): 17,739 works (2,107 with Chinese collaborations)
- ASPI Defence Universities: 62 matched (11 military-linked)
- Phase 2 Correlations: 68 CORDIS<->OpenAIRE overlaps
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

# Data paths
PSC_PATH = Path("data/processed/psc_strict_v3")
CORDIS_PATH = Path("data/processed/cordis_v1")
OPENAIRE_PATH = Path("data/processed/openaire_v1")
USASPENDING_PATH = Path("data/processed/usaspending_production")
OPENALEX_PATH = Path("data/processed/openalex_production")
PHASE2_PATH = Path("data/processed/phase2_20251005_093031")
ASPI_PATH = Path("data/external/aspi")
OUTPUT_DIR = Path("analysis/comprehensive_v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class ComprehensiveAnalyzerV2:
    def __init__(self):
        self.data = {}
        print("="*80)
        print("COMPREHENSIVE PRC INTELLIGENCE ANALYSIS v2.1")
        print("="*80)
        print("Now includes OpenAlex V5: 17,739 strategic technology works")
        print("="*80)

    def load_psc_data(self) -> Dict:
        """Load PSC (UK Companies House) detections"""
        print("\n[1/8] Loading PSC (UK Companies House) data...")

        stats_file = PSC_PATH / "statistics.json"
        detections_file = PSC_PATH / "detections.ndjson"

        if not stats_file.exists():
            print(f"  [WARN] PSC statistics not found at {stats_file}")
            return {}

        with open(stats_file, 'r') as f:
            stats = json.load(f)

        # Load sample detections
        detections = []
        if detections_file.exists():
            with open(detections_file, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 100:  # Sample first 100
                        break
                    detections.append(json.loads(line))

        result = {
            'total_detections': stats.get('total_detections', 0),
            'nationality_matches': stats.get('nationality_matches', 0),
            'corporate_matches': stats.get('corporate_matches', 0),
            'sample_detections': detections,
            'source': 'PSC (UK Companies House)',
            'coverage': 'UK company beneficial ownership'
        }

        print(f"  [OK] Loaded {result['total_detections']:,} PSC detections")
        return result

    def load_cordis_data(self) -> Dict:
        """Load CORDIS (EU Research) detections"""
        print("\n[2/8] Loading CORDIS (EU Research) data...")

        detections_file = CORDIS_PATH / "detections.ndjson"
        stats_file = CORDIS_PATH / "statistics.json"

        if not detections_file.exists():
            print(f"  [WARN] CORDIS detections not found at {detections_file}")
            return {}

        detections = []
        with open(detections_file, 'r') as f:
            for line in f:
                detections.append(json.loads(line))

        stats = {}
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)

        result = {
            'total_detections': len(detections),
            'detections': detections,
            'statistics': stats,
            'source': 'CORDIS (EU Framework Programmes)',
            'coverage': 'EU research project participants'
        }

        print(f"  [OK] Loaded {result['total_detections']:,} CORDIS detections")
        return result

    def load_openaire_data(self) -> Dict:
        """Load OpenAIRE (Publications) detections"""
        print("\n[3/8] Loading OpenAIRE (Publications) data...")

        detections_file = OPENAIRE_PATH / "detections.ndjson"
        stats_file = OPENAIRE_PATH / "statistics.json"

        if not detections_file.exists():
            print(f"  [WARN] OpenAIRE detections not found at {detections_file}")
            return {}

        detections = []
        with open(detections_file, 'r') as f:
            for line in f:
                detections.append(json.loads(line))

        stats = {}
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)

        result = {
            'total_detections': len(detections),
            'detections': detections,
            'statistics': stats,
            'source': 'OpenAIRE',
            'coverage': 'Open access research publications'
        }

        print(f"  [OK] Loaded {result['total_detections']:,} OpenAIRE detections")
        return result

    def load_usaspending_data(self) -> Dict:
        """Load USAspending (US Government Contracts) detections"""
        print("\n[4/8] Loading USAspending (US Contracts) data...")

        detections_file = USASPENDING_PATH / "detections.ndjson"
        stats_file = USASPENDING_PATH / "statistics.json"

        if not detections_file.exists():
            print(f"  [WARN] USAspending detections not found (still processing)")
            return {'status': 'processing', 'total_detections': 0}

        detections = []
        with open(detections_file, 'r') as f:
            for line in f:
                detections.append(json.loads(line))

        stats = {}
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)

        result = {
            'total_detections': len(detections),
            'detections': detections,
            'statistics': stats,
            'source': 'USAspending',
            'coverage': 'US federal government contracts'
        }

        print(f"  [OK] Loaded {result['total_detections']:,} USAspending detections")
        return result

    def load_openalex_data(self) -> Dict:
        """Load OpenAlex V5 (Academic Collaborations) from master database"""
        print("\n[5/8] Loading OpenAlex V5 (Academic Collaborations) data...")

        import sqlite3
        db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

        if not db_path.exists():
            print(f"  [WARN] Master database not found at {db_path}")
            return {'status': 'not_found', 'total_detections': 0}

        try:
            conn = sqlite3.connect(str(db_path))

            # Total works
            total_works = conn.execute("SELECT COUNT(*) FROM openalex_works").fetchone()[0]

            # By technology
            tech_counts = conn.execute("""
                SELECT technology_domain, COUNT(*)
                FROM openalex_works
                GROUP BY technology_domain
            """).fetchall()

            # Top institutions
            top_institutions = conn.execute("""
                SELECT institution_name, country_code, COUNT(DISTINCT work_id) as work_count
                FROM openalex_work_authors
                WHERE institution_name IS NOT NULL
                GROUP BY institution_name, country_code
                ORDER BY work_count DESC
                LIMIT 20
            """).fetchall()

            # China collaborations
            china_works = conn.execute("""
                SELECT COUNT(DISTINCT work_id)
                FROM openalex_work_authors
                WHERE country_code = 'CN'
            """).fetchone()[0]

            # China by technology
            china_by_tech = conn.execute("""
                SELECT w.technology_domain, COUNT(DISTINCT wa.work_id)
                FROM openalex_work_authors wa
                JOIN openalex_works w ON wa.work_id = w.work_id
                WHERE wa.country_code = 'CN'
                GROUP BY w.technology_domain
                ORDER BY COUNT(DISTINCT wa.work_id) DESC
            """).fetchall()

            # Sample high-impact works
            sample_works = conn.execute("""
                SELECT work_id, title, technology_domain, cited_by_count, publication_year
                FROM openalex_works
                ORDER BY cited_by_count DESC
                LIMIT 10
            """).fetchall()

            conn.close()

            result = {
                'status': 'completed',
                'version': 'V5',
                'total_detections': total_works,
                'china_works': china_works,
                'china_percent': (china_works / total_works * 100) if total_works > 0 else 0,
                'technology_distribution': {tech: count for tech, count in tech_counts},
                'china_technology_distribution': {tech: count for tech, count in china_by_tech},
                'top_institutions': [
                    {
                        'name': inst,
                        'country': country if country else '??',
                        'works': count
                    }
                    for inst, country, count in top_institutions
                ],
                'sample_high_impact': [
                    {
                        'work_id': wid,
                        'title': title[:100] if title else '',
                        'technology': tech,
                        'citations': citations,
                        'year': year
                    }
                    for wid, title, tech, citations, year in sample_works
                ],
                'source': 'OpenAlex V5',
                'coverage': 'Global academic research across 9 strategic technologies'
            }

            print(f"  [OK] Loaded {total_works:,} OpenAlex V5 works ({china_works:,} with Chinese collaborations)")
            return result

        except Exception as e:
            print(f"  [WARN] Error loading OpenAlex data: {e}")
            return {'status': 'error', 'total_detections': 0, 'error': str(e)}

    def load_phase2_correlations(self) -> Dict:
        """Load Phase 2 correlation analysis (CORDIS<->OpenAIRE overlaps)"""
        print("\n[6/8] Loading Phase 2 Correlation Analysis...")

        overlap_file = PHASE2_PATH / "correlation_analysis" / "cordis_openaire_overlap_analysis.json"

        if not overlap_file.exists():
            print(f"  [WARN] Correlation analysis not found")
            return {}

        with open(overlap_file, 'r') as f:
            overlaps = json.load(f)

        result = {
            'total_overlaps': overlaps.get('total_overlaps', 0),
            'overlapping_entities': overlaps.get('all_overlaps', []),
            'source': 'Phase 2 Cross-Reference',
            'coverage': 'Institutions appearing in both CORDIS and OpenAIRE'
        }

        print(f"  [OK] Loaded {result['total_overlaps']} CORDIS<->OpenAIRE overlapping institutions")
        return result

    def load_aspi_crossref(self) -> Dict:
        """Load ASPI Defence Universities cross-reference"""
        print("\n[7/8] Loading ASPI Defence Universities cross-reference...")

        aspi_crossref = PHASE2_PATH / "correlation_analysis" / "aspi_crossref_results.json"
        aspi_comprehensive = ASPI_PATH / "aspi_institutions_comprehensive.json"

        result = {}

        if aspi_crossref.exists():
            with open(aspi_crossref, 'r', encoding='utf-8') as f:
                crossref = json.load(f)
                result = {
                    'total_matches': crossref.get('total_matches', 0),
                    'seven_sons': crossref.get('high_risk', {}).get('seven_sons', 0),
                    'military_linked': crossref.get('high_risk', {}).get('military', 0),
                    'defence_industry': crossref.get('high_risk', {}).get('defence_industry', 0),
                    'security': crossref.get('high_risk', {}).get('security', 0),
                    'matches': crossref.get('matches', []),
                    'source': 'ASPI China Defence Universities Tracker',
                    'coverage': 'Defence/military-linked institutions matched with our data'
                }

        if aspi_comprehensive.exists():
            with open(aspi_comprehensive, 'r', encoding='utf-8') as f:
                aspi_full = json.load(f)
                result['total_aspi_institutions'] = aspi_full.get('dataset_info', {}).get('total_institutions', 159)

        print(f"  [OK] Loaded {result.get('total_matches', 0)} ASPI matches ({result.get('military_linked', 0)} military-linked)")
        return result

    def analyze_cross_source_entities(self) -> Dict:
        """Identify entities appearing across multiple sources"""
        print("\n[8/8] Analyzing cross-source entity appearances...")

        entity_map = defaultdict(lambda: {'sources': [], 'data': {}})

        # Collect entities from each source
        for source_name, source_data in self.data.items():
            if source_name == 'phase2_correlations':
                for entity in source_data.get('overlapping_entities', []):
                    name = entity.get('entity_name', '').lower().strip()
                    if name:
                        entity_map[name]['sources'].append('CORDIS+OpenAIRE')
                        entity_map[name]['data'][source_name] = entity

            elif source_name == 'aspi_crossref':
                for match in source_data.get('matches', []):
                    name = match.get('our_name', '').lower().strip()
                    if name:
                        entity_map[name]['sources'].append('ASPI')
                        entity_map[name]['data']['aspi_categories'] = match.get('categories', [])
                        entity_map[name]['data']['is_military'] = 'Military' in match.get('categories', [])

        # Find multi-source entities
        multi_source = {
            name: data for name, data in entity_map.items()
            if len(set(data['sources'])) > 1
        }

        result = {
            'total_unique_entities': len(entity_map),
            'multi_source_entities': len(multi_source),
            'multi_source_list': [
                {
                    'entity': name,
                    'sources': list(set(data['sources'])),
                    'is_military_linked': data['data'].get('is_military', False),
                    'aspi_categories': data['data'].get('aspi_categories', [])
                }
                for name, data in sorted(
                    multi_source.items(),
                    key=lambda x: len(set(x[1]['sources'])),
                    reverse=True
                )[:50]  # Top 50
            ]
        }

        print(f"  [OK] Found {result['multi_source_entities']} entities across multiple sources")
        return result

    def generate_comprehensive_report(self) -> Dict:
        """Generate final comprehensive intelligence report"""
        print("\n" + "="*80)
        print("GENERATING COMPREHENSIVE REPORT")
        print("="*80)

        report = {
            'generated': datetime.now().isoformat(),
            'version': '2.1',
            'summary': {
                'psc_detections': self.data.get('psc', {}).get('total_detections', 0),
                'cordis_detections': self.data.get('cordis', {}).get('total_detections', 0),
                'openaire_detections': self.data.get('openaire', {}).get('total_detections', 0),
                'usaspending_detections': self.data.get('usaspending', {}).get('total_detections', 0),
                'openalex_detections': self.data.get('openalex', {}).get('total_detections', 0),
                'cordis_openaire_overlaps': self.data.get('phase2_correlations', {}).get('total_overlaps', 0),
                'aspi_military_linked': self.data.get('aspi_crossref', {}).get('military_linked', 0),
                'multi_source_entities': self.data.get('cross_source', {}).get('multi_source_entities', 0)
            },
            'data_sources': self.data,
            'key_findings': self.generate_key_findings()
        }

        # Save comprehensive report
        report_file = OUTPUT_DIR / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Comprehensive report saved to: {report_file}")

        # Generate markdown summary
        self.generate_markdown_summary(report)

        return report

    def generate_key_findings(self) -> List[str]:
        """Generate key intelligence findings"""
        findings = []

        # PSC findings
        psc_count = self.data.get('psc', {}).get('total_detections', 0)
        if psc_count > 0:
            findings.append(f"UK Corporate: {psc_count:,} PRC-linked beneficial owners identified in UK companies")

        # CORDIS + OpenAIRE overlap
        overlaps = self.data.get('phase2_correlations', {}).get('total_overlaps', 0)
        if overlaps > 0:
            findings.append(f"Research Networks: {overlaps} Chinese institutions active in both EU projects and publications")

        # ASPI military links
        military = self.data.get('aspi_crossref', {}).get('military_linked', 0)
        if military > 0:
            findings.append(f"Defence Links: {military} institutions with military connections identified in our data")

        # Multi-source entities
        multi = self.data.get('cross_source', {}).get('multi_source_entities', 0)
        if multi > 0:
            findings.append(f"Cross-Source: {multi} entities appear across multiple intelligence sources")

        return findings

    def generate_markdown_summary(self, report: Dict):
        """Generate markdown summary report"""
        md_file = OUTPUT_DIR / f"COMPREHENSIVE_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Comprehensive PRC Intelligence Analysis v2.1\n\n")
            f.write(f"**Generated**: {report['generated']}\n\n")
            f.write("**Includes OpenAlex V5**: 17,739 strategic technology works\n\n")

            f.write("## Executive Summary\n\n")

            summary = report['summary']
            f.write("### Detection Totals\n\n")
            f.write(f"- **PSC (UK Companies)**: {summary['psc_detections']:,} detections\n")
            f.write(f"- **CORDIS (EU Research)**: {summary['cordis_detections']:,} detections\n")
            f.write(f"- **OpenAIRE (Publications)**: {summary['openaire_detections']:,} detections\n")
            f.write(f"- **USAspending (US Contracts)**: {summary['usaspending_detections']:,} detections\n")
            f.write(f"- **OpenAlex V5 (Academic)**: {summary['openalex_detections']:,} works\n\n")

            f.write("### Cross-Reference Analysis\n\n")
            f.write(f"- **CORDIS <-> OpenAIRE Overlaps**: {summary['cordis_openaire_overlaps']} institutions\n")
            f.write(f"- **ASPI Military-Linked**: {summary['aspi_military_linked']} institutions\n")
            f.write(f"- **Multi-Source Entities**: {summary['multi_source_entities']} entities\n\n")

            f.write("## Key Findings\n\n")
            for i, finding in enumerate(report['key_findings'], 1):
                f.write(f"{i}. {finding}\n")

            f.write("\n## ASPI Defence Universities - High Risk Matches\n\n")
            aspi = self.data.get('aspi_crossref', {})
            for match in aspi.get('matches', [])[:10]:
                if match.get('is_seven_sons') or 'Military' in match.get('categories', []):
                    f.write(f"### {match['our_name']}\n")
                    f.write(f"- **ASPI Name**: {match['aspi_name']}\n")
                    f.write(f"- **Categories**: {', '.join(match['categories'])}\n")
                    f.write(f"- **CORDIS Projects**: {match['cordis_participations']}\n")
                    f.write(f"- **OpenAIRE Publications**: {match['openaire_publications']}\n\n")

        print(f"[OK] Markdown summary saved to: {md_file}")

    def run(self):
        """Run comprehensive analysis"""
        # Load all data sources
        self.data['psc'] = self.load_psc_data()
        self.data['cordis'] = self.load_cordis_data()
        self.data['openaire'] = self.load_openaire_data()
        self.data['usaspending'] = self.load_usaspending_data()
        self.data['openalex'] = self.load_openalex_data()
        self.data['phase2_correlations'] = self.load_phase2_correlations()
        self.data['aspi_crossref'] = self.load_aspi_crossref()

        # Cross-source analysis
        self.data['cross_source'] = self.analyze_cross_source_entities()

        # Generate final report
        report = self.generate_comprehensive_report()

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\nKey Findings:")
        for finding in report['key_findings']:
            print(f"  • {finding}")

        return report

if __name__ == '__main__':
    analyzer = ComprehensiveAnalyzerV2()
    analyzer.run()
