#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive PRC Intelligence Analysis v3.0
Cross-references ALL data sources:
- PSC (UK Companies House): 209,061 detections
- CORDIS v1 (EU Research): 407 detections
- OpenAIRE v1 (Publications): 321 detections
- TED (EU Procurement): Variable
- USAspending (US Contracts): Variable
- OpenAlex (Academic): In progress
- ASPI Defence Universities: 62 matched (11 military-linked)
- Phase 2 Correlations: 68 CORDIS↔OpenAIRE overlaps
- SEC Edgar (US Corporate Filings): 944 Chinese companies
- OpenSanctions (Global Sanctions): OFAC + consolidated lists
- GLEIF (Legal Entity Identifiers): Global LEI registry
- USPTO (US Patents): Technology risk analysis
- EPO (EU Patents): European patent filings
- Sanctions (Consolidated): Multi-source sanctions data
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

# Force UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Data paths
PSC_PATH = Path("data/processed/psc_strict_v3")
CORDIS_PATH = Path("data/processed/cordis_v1")
OPENAIRE_PATH = Path("data/processed/openaire_v1")
USASPENDING_PATH = Path("data/processed/usaspending_production")
OPENALEX_PATH = Path("data/processed/openalex_production")
PHASE2_PATH = Path("data/processed/phase2_20251005_093031")
ASPI_PATH = Path("data/external/aspi")
SEC_EDGAR_PATH = Path("data/processed/sec_edgar_comprehensive")
SANCTIONS_PATH = Path("F:/OSINT_DATA/SANCTIONS")
USPTO_PATH = Path("F:/OSINT_DATA/USPTO_Patents")
EPO_PATH = Path("F:/OSINT_DATA/EPO_PATENTS")
TED_PATH = Path("data/processed/ted_china")
OUTPUT_DIR = Path("analysis/comprehensive_v3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class ComprehensiveAnalyzerV3:
    def __init__(self):
        self.data = {}
        print("="*80)
        print("COMPREHENSIVE PRC INTELLIGENCE ANALYSIS v3.0")
        print("="*80)

    def load_psc_data(self) -> Dict:
        """Load PSC (UK Companies House) detections"""
        print("\n[1/14] Loading PSC (UK Companies House) data...")

        stats_file = PSC_PATH / "statistics.json"
        detections_file = PSC_PATH / "detections.ndjson"

        if not stats_file.exists():
            print(f"  ⚠ PSC statistics not found at {stats_file}")
            return {}

        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        # Load sample detections
        detections = []
        if detections_file.exists():
            with open(detections_file, 'r', encoding='utf-8') as f:
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

        print(f"  ✓ Loaded {result['total_detections']:,} PSC detections")
        return result

    def load_cordis_data(self) -> Dict:
        """Load CORDIS (EU Research) detections"""
        print("\n[2/14] Loading CORDIS (EU Research) data...")

        detections_file = CORDIS_PATH / "detections.ndjson"
        stats_file = CORDIS_PATH / "statistics.json"

        if not detections_file.exists():
            print(f"  ⚠ CORDIS detections not found at {detections_file}")
            return {}

        detections = []
        with open(detections_file, 'r', encoding='utf-8') as f:
            for line in f:
                detections.append(json.loads(line))

        stats = {}
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)

        result = {
            'total_detections': len(detections),
            'detections': detections,
            'statistics': stats,
            'source': 'CORDIS (EU Framework Programmes)',
            'coverage': 'EU research project participants'
        }

        print(f"  ✓ Loaded {result['total_detections']:,} CORDIS detections")
        return result

    def load_openaire_data(self) -> Dict:
        """Load OpenAIRE (Publications) detections"""
        print("\n[3/14] Loading OpenAIRE (Publications) data...")

        detections_file = OPENAIRE_PATH / "detections.ndjson"
        stats_file = OPENAIRE_PATH / "statistics.json"

        if not detections_file.exists():
            print(f"  ⚠ OpenAIRE detections not found at {detections_file}")
            return {}

        detections = []
        with open(detections_file, 'r', encoding='utf-8') as f:
            for line in f:
                detections.append(json.loads(line))

        stats = {}
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)

        result = {
            'total_detections': len(detections),
            'detections': detections,
            'statistics': stats,
            'source': 'OpenAIRE',
            'coverage': 'Open access research publications'
        }

        print(f"  ✓ Loaded {result['total_detections']:,} OpenAIRE detections")
        return result

    def load_usaspending_data(self) -> Dict:
        """Load USAspending (US Government Contracts) detections"""
        print("\n[4/14] Loading USAspending (US Contracts) data...")

        detections_file = USASPENDING_PATH / "detections.ndjson"
        stats_file = USASPENDING_PATH / "statistics.json"

        if not detections_file.exists():
            print(f"  ⚠ USAspending detections not found (still processing)")
            return {'status': 'processing', 'total_detections': 0}

        detections = []
        with open(detections_file, 'r', encoding='utf-8') as f:
            for line in f:
                detections.append(json.loads(line))

        stats = {}
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)

        result = {
            'total_detections': len(detections),
            'detections': detections,
            'statistics': stats,
            'source': 'USAspending',
            'coverage': 'US federal government contracts'
        }

        print(f"  ✓ Loaded {result['total_detections']:,} USAspending detections")
        return result

    def load_openalex_data(self) -> Dict:
        """Load OpenAlex (Academic Collaborations) detections"""
        print("\n[5/14] Loading OpenAlex (Academic Collaborations) data...")

        detections_file = OPENALEX_PATH / "detections.ndjson"
        checkpoint_file = OPENALEX_PATH / "checkpoint.json"

        result = {'status': 'processing', 'total_detections': 0}

        if checkpoint_file.exists():
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                result['progress'] = checkpoint.get('progress', 'unknown')
                result['last_processed'] = checkpoint.get('last_processed_date', 'unknown')

        if detections_file.exists():
            count = sum(1 for _ in open(detections_file, 'r'))
            result['total_detections'] = count
            result['source'] = 'OpenAlex'
            result['coverage'] = 'Global academic collaborations'
            print(f"  ⏳ OpenAlex: {count:,} detections so far (still processing)")
        else:
            print(f"  ⚠ OpenAlex still processing...")

        return result

    def load_phase2_correlations(self) -> Dict:
        """Load Phase 2 correlation analysis (CORDIS↔OpenAIRE overlaps)"""
        print("\n[6/14] Loading Phase 2 Correlation Analysis...")

        overlap_file = PHASE2_PATH / "correlation_analysis" / "cordis_openaire_overlap_analysis.json"

        if not overlap_file.exists():
            print(f"  ⚠ Correlation analysis not found")
            return {}

        with open(overlap_file, 'r', encoding='utf-8') as f:
            overlaps = json.load(f)

        result = {
            'total_overlaps': overlaps.get('total_overlaps', 0),
            'overlapping_entities': overlaps.get('all_overlaps', []),
            'source': 'Phase 2 Cross-Reference',
            'coverage': 'Institutions appearing in both CORDIS and OpenAIRE'
        }

        print(f"  ✓ Loaded {result['total_overlaps']} CORDIS↔OpenAIRE overlapping institutions")
        return result

    def load_aspi_crossref(self) -> Dict:
        """Load ASPI Defence Universities cross-reference"""
        print("\n[7/14] Loading ASPI Defence Universities cross-reference...")

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

        print(f"  ✓ Loaded {result.get('total_matches', 0)} ASPI matches ({result.get('military_linked', 0)} military-linked)")
        return result

    def load_sec_edgar_data(self) -> Dict:
        """Load SEC Edgar (US Corporate Filings) data"""
        print("\n[8/14] Loading SEC Edgar (US Corporate Filings) data...")

        chinese_dir = SEC_EDGAR_PATH / "chinese"
        companies_list = SEC_EDGAR_PATH / "chinese_companies_list.json"

        result = {'total_companies': 0, 'companies': [], 'source': 'SEC Edgar', 'coverage': 'Chinese companies listed in US markets'}

        if companies_list.exists():
            with open(companies_list, 'r', encoding='utf-8') as f:
                companies = json.load(f)
                result['total_companies'] = len(companies)
                result['companies'] = companies[:50]  # Sample first 50

        elif chinese_dir.exists():
            # Count JSON files in chinese directory
            json_files = list(chinese_dir.glob("*.json"))
            result['total_companies'] = len(json_files)
            result['companies'] = [f.stem for f in json_files[:50]]

        print(f"  ✓ Loaded {result['total_companies']:,} SEC Edgar Chinese companies")
        return result

    def load_opensanctions_data(self) -> Dict:
        """Load OpenSanctions (Global Sanctions) data"""
        print("\n[9/14] Loading OpenSanctions (Global Sanctions) data...")

        ofac_file = SANCTIONS_PATH / "OFAC_consolidated_xml_20250917.xml"

        result = {'source': 'OpenSanctions/OFAC', 'coverage': 'Consolidated sanctions lists', 'data_available': False}

        if ofac_file.exists():
            result['data_available'] = True
            result['ofac_file'] = str(ofac_file)
            result['file_size_mb'] = ofac_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ OFAC sanctions data available ({result['file_size_mb']:.1f} MB)")
        else:
            print(f"  ⚠ OpenSanctions/OFAC data not found")

        return result

    def load_gleif_data(self) -> Dict:
        """Load GLEIF (Legal Entity Identifiers) data"""
        print("\n[10/14] Loading GLEIF (Legal Entity Identifiers) data...")

        # GLEIF data would be in F:/OSINT_DATA or data/external if we had it
        result = {'source': 'GLEIF', 'coverage': 'Global Legal Entity Identifiers', 'status': 'not_yet_integrated'}

        print(f"  ⚠ GLEIF data not yet integrated (future enhancement)")
        return result

    def load_uspto_data(self) -> Dict:
        """Load USPTO (US Patents) data"""
        print("\n[11/14] Loading USPTO (US Patents) data...")

        result = {'source': 'USPTO', 'coverage': 'US patent filings', 'analyses': []}

        # Check for analysis reports
        if USPTO_PATH.exists():
            json_files = list(USPTO_PATH.glob("*.json"))
            result['analyses'] = [f.name for f in json_files]
            result['total_analyses'] = len(json_files)

            # Load summary if available
            for analysis_file in json_files:
                if 'summary' in analysis_file.name.lower():
                    with open(analysis_file, 'r', encoding='utf-8') as f:
                        summary = json.load(f)
                        result['summary'] = summary
                        break

            print(f"  ✓ Loaded {result['total_analyses']} USPTO analysis files")
        else:
            print(f"  ⚠ USPTO data not found")
            result['total_analyses'] = 0

        return result

    def load_epo_data(self) -> Dict:
        """Load EPO (European Patent Office) data"""
        print("\n[12/14] Loading EPO (European Patent Office) data...")

        result = {'source': 'EPO', 'coverage': 'European patent filings', 'data_available': False}

        if EPO_PATH.exists():
            subdirs = [d for d in EPO_PATH.iterdir() if d.is_dir()]
            result['data_available'] = True
            result['subdirectories'] = [d.name for d in subdirs]
            result['total_subdirs'] = len(subdirs)
            print(f"  ✓ EPO data available ({result['total_subdirs']} subdirectories)")
        else:
            print(f"  ⚠ EPO data not found")

        return result

    def load_sanctions_consolidated(self) -> Dict:
        """Load consolidated sanctions data"""
        print("\n[13/15] Loading Consolidated Sanctions data...")

        result = {'source': 'Sanctions (Consolidated)', 'coverage': 'Multi-source sanctions data', 'files': []}

        if SANCTIONS_PATH.exists():
            sanction_files = list(SANCTIONS_PATH.glob("*"))
            result['files'] = [f.name for f in sanction_files]
            result['total_files'] = len(sanction_files)
            print(f"  ✓ Loaded {result['total_files']} sanctions files")
        else:
            print(f"  ⚠ Sanctions data not found")
            result['total_files'] = 0

        return result

    def load_ted_data(self) -> Dict:
        """Load TED (EU Procurement) data"""
        print("\n[14/15] Loading TED (EU Procurement) data...")

        ted_comprehensive = TED_PATH / "ted_china_comprehensive_20250928_165336.json"

        result = {'source': 'TED (Tenders Electronic Daily)', 'coverage': 'EU public procurement', 'total_contracts': 0, 'total_suppliers': 0}

        if ted_comprehensive.exists():
            with open(ted_comprehensive, 'r', encoding='utf-8') as f:
                ted_data = json.load(f)
                result['total_contracts'] = len(ted_data.get('china_contracts', []))
                result['total_suppliers'] = len(ted_data.get('chinese_suppliers', []))
                result['yearly_statistics'] = ted_data.get('yearly_statistics', [])
                result['contracts'] = ted_data.get('china_contracts', [])[:50]  # Sample first 50

            print(f"  ✓ Loaded {result['total_contracts']:,} TED contracts, {result['total_suppliers']:,} suppliers")
        else:
            print(f"  ⚠ TED data not found at {ted_comprehensive}")

        return result

    def analyze_cross_source_entities(self) -> Dict:
        """Identify entities appearing across multiple sources"""
        print("\n[15/15] Analyzing cross-source entity appearances...")

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

        print(f"  ✓ Found {result['multi_source_entities']} entities across multiple sources")
        return result

    def generate_comprehensive_report(self) -> Dict:
        """Generate final comprehensive intelligence report"""
        print("\n" + "="*80)
        print("GENERATING COMPREHENSIVE REPORT")
        print("="*80)

        report = {
            'generated': datetime.now().isoformat(),
            'version': '3.0',
            'summary': {
                'psc_detections': self.data.get('psc', {}).get('total_detections', 0),
                'cordis_detections': self.data.get('cordis', {}).get('total_detections', 0),
                'openaire_detections': self.data.get('openaire', {}).get('total_detections', 0),
                'usaspending_detections': self.data.get('usaspending', {}).get('total_detections', 0),
                'openalex_detections': self.data.get('openalex', {}).get('total_detections', 0),
                'cordis_openaire_overlaps': self.data.get('phase2_correlations', {}).get('total_overlaps', 0),
                'aspi_military_linked': self.data.get('aspi_crossref', {}).get('military_linked', 0),
                'sec_edgar_companies': self.data.get('sec_edgar', {}).get('total_companies', 0),
                'opensanctions_available': self.data.get('opensanctions', {}).get('data_available', False),
                'gleif_status': self.data.get('gleif', {}).get('status', 'unknown'),
                'uspto_analyses': self.data.get('uspto', {}).get('total_analyses', 0),
                'epo_available': self.data.get('epo', {}).get('data_available', False),
                'sanctions_files': self.data.get('sanctions', {}).get('total_files', 0),
                'ted_contracts': self.data.get('ted', {}).get('total_contracts', 0),
                'ted_suppliers': self.data.get('ted', {}).get('total_suppliers', 0),
                'multi_source_entities': self.data.get('cross_source', {}).get('multi_source_entities', 0)
            },
            'data_sources': self.data,
            'key_findings': self.generate_key_findings()
        }

        # Save comprehensive report
        report_file = OUTPUT_DIR / f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Comprehensive report saved to: {report_file}")

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
            f.write("# Comprehensive PRC Intelligence Analysis v3.0\n\n")
            f.write(f"**Generated**: {report['generated']}\n\n")

            f.write("## Executive Summary\n\n")

            summary = report['summary']
            f.write("### Detection Totals\n\n")
            f.write(f"- **PSC (UK Companies)**: {summary['psc_detections']:,} detections\n")
            f.write(f"- **CORDIS (EU Research)**: {summary['cordis_detections']:,} detections\n")
            f.write(f"- **OpenAIRE (Publications)**: {summary['openaire_detections']:,} detections\n")
            f.write(f"- **USAspending (US Contracts)**: {summary['usaspending_detections']:,} detections\n")
            f.write(f"- **OpenAlex (Academic)**: {summary['openalex_detections']:,} detections (in progress)\n")
            f.write(f"- **SEC Edgar (US Filings)**: {summary['sec_edgar_companies']:,} Chinese companies\n")
            f.write(f"- **USPTO (US Patents)**: {summary['uspto_analyses']:,} analysis files\n")
            f.write(f"- **TED (EU Procurement)**: {summary['ted_contracts']:,} contracts, {summary['ted_suppliers']:,} suppliers\n\n")

            f.write("### Cross-Reference Analysis\n\n")
            f.write(f"- **CORDIS ↔ OpenAIRE Overlaps**: {summary['cordis_openaire_overlaps']} institutions\n")
            f.write(f"- **ASPI Military-Linked**: {summary['aspi_military_linked']} institutions\n")
            f.write(f"- **Multi-Source Entities**: {summary['multi_source_entities']} entities\n\n")

            f.write("### Additional Data Sources\n\n")
            f.write(f"- **OpenSanctions/OFAC**: {'Available' if summary['opensanctions_available'] else 'Not found'}\n")
            f.write(f"- **GLEIF**: {summary['gleif_status']}\n")
            f.write(f"- **EPO Patents**: {'Available' if summary['epo_available'] else 'Not found'}\n")
            f.write(f"- **Sanctions Files**: {summary['sanctions_files']} files\n\n")

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

        print(f"✓ Markdown summary saved to: {md_file}")

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
        self.data['sec_edgar'] = self.load_sec_edgar_data()
        self.data['opensanctions'] = self.load_opensanctions_data()
        self.data['gleif'] = self.load_gleif_data()
        self.data['uspto'] = self.load_uspto_data()
        self.data['epo'] = self.load_epo_data()
        self.data['sanctions'] = self.load_sanctions_consolidated()
        self.data['ted'] = self.load_ted_data()

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
    analyzer = ComprehensiveAnalyzerV3()
    analyzer.run()
