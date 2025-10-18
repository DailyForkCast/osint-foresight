#!/usr/bin/env python3
"""
Existing Data Processor
Processes all downloaded Italy data for comprehensive China analysis
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExistingDataProcessor:
    def __init__(self):
        self.collected_path = Path("data/collected")
        self.processed_path = Path("data/processed")
        self.output_path = Path("data/processed/comprehensive_analysis")
        self.output_path.mkdir(parents=True, exist_ok=True)

        # China detection patterns
        self.china_patterns = [
            r'\bchina\b', r'\bchinese\b', r'\bbeijing\b', r'\bshanghai\b',
            r'\bhuawei\b', r'\bzte\b', r'\balibaba\b', r'\btencent\b',
            r'\bbaidu\b', r'\bxiaomi\b', r'\blenovo\b', r'\bdji\b',
            r'\bsinochem\b', r'\bavic\b', r'\bcomac\b', r'\bcrrc\b',
            r'\bchinese academy\b', r'\btsinghua\b', r'\bpeking university\b'
        ]

        # Dual-use technology patterns
        self.dual_use_patterns = [
            r'\bquantum\b', r'\bcryptograph\b', r'\bencryption\b',
            r'\bsemiconductor\b', r'\bmicrochip\b', r'\bai\b', r'\bmachine learning\b',
            r'\bartificial intelligence\b', r'\b5g\b', r'\b6g\b',
            r'\bradar\b', r'\bsatellite\b', r'\bdrone\b', r'\buav\b',
            r'\bhypersonic\b', r'\bmissile\b', r'\bnuclear\b', r'\blaser\b',
            r'\bbiotechnology\b', r'\bsynthetic biology\b', r'\bgenome\b'
        ]

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'sources_processed': [],
            'china_connections': [],
            'dual_use_findings': [],
            'leonardo_analysis': {},
            'contract_patterns': [],
            'research_collaborations': [],
            'statistics': defaultdict(int)
        }

    def process_leonardo_patents(self):
        """Process Leonardo patent data from EPO"""
        logger.info("Processing Leonardo patent data...")

        epo_files = list(self.collected_path.glob("epo/leonardo_patents_*.json"))

        leonardo_data = {
            'total_patents': 0,
            'china_related': 0,
            'dual_use': 0,
            'patent_details': []
        }

        for file_path in epo_files:
            try:
                with open(file_path, 'r') as f:
                    patents = json.load(f)

                    if isinstance(patents, list):
                        leonardo_data['total_patents'] += len(patents)

                        for patent in patents:
                            patent_text = self._extract_patent_text(patent)

                            china_score = self._calculate_china_score(patent_text)
                            dual_use_keywords = self._check_dual_use(patent_text)

                            if china_score > 0 or dual_use_keywords:
                                patent_analysis = {
                                    'patent_id': patent.get('id', 'Unknown'),
                                    'title': patent.get('title', ''),
                                    'date': patent.get('date', ''),
                                    'china_score': china_score,
                                    'dual_use_keywords': dual_use_keywords,
                                    'risk_level': self._assess_patent_risk(china_score, dual_use_keywords)
                                }

                                leonardo_data['patent_details'].append(patent_analysis)

                                if china_score > 0:
                                    leonardo_data['china_related'] += 1
                                    self.results['china_connections'].append({
                                        'source': 'EPO_Leonardo',
                                        'type': 'patent',
                                        'details': patent_analysis
                                    })

                                if dual_use_keywords:
                                    leonardo_data['dual_use'] += 1
                                    self.results['dual_use_findings'].append({
                                        'source': 'EPO_Leonardo',
                                        'type': 'patent',
                                        'keywords': dual_use_keywords,
                                        'details': patent_analysis
                                    })

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

        self.results['leonardo_analysis'] = leonardo_data
        self.results['statistics']['leonardo_patents'] = leonardo_data['total_patents']
        self.results['statistics']['leonardo_china'] = leonardo_data['china_related']

        logger.info(f"Leonardo patents: {leonardo_data['total_patents']} total, "
                   f"{leonardo_data['china_related']} China-related, "
                   f"{leonardo_data['dual_use']} dual-use")

        return leonardo_data

    def process_sec_edgar_data(self):
        """Process SEC EDGAR filings"""
        logger.info("Processing SEC EDGAR data...")

        sec_files = list(self.collected_path.glob("sec_edgar/*.json"))

        sec_analysis = {
            'files_processed': len(sec_files),
            'china_mentions': 0,
            'risk_disclosures': [],
            'supply_chain_references': []
        }

        for file_path in sec_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    # Process different SEC data formats
                    if isinstance(data, dict):
                        sec_text = self._extract_sec_text(data)

                        china_score = self._calculate_china_score(sec_text)
                        dual_use_keywords = self._check_dual_use(sec_text)

                        if china_score > 0:
                            sec_analysis['china_mentions'] += china_score
                            self.results['china_connections'].append({
                                'source': 'SEC_EDGAR',
                                'file': file_path.name,
                                'china_score': china_score,
                                'context': 'financial_filing'
                            })

                        # Look for risk disclosures
                        risk_indicators = self._extract_risk_disclosures(sec_text)
                        if risk_indicators:
                            sec_analysis['risk_disclosures'].extend(risk_indicators)

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

        self.results['statistics']['sec_files'] = sec_analysis['files_processed']
        self.results['statistics']['sec_china_mentions'] = sec_analysis['china_mentions']

        logger.info(f"SEC EDGAR: {sec_analysis['files_processed']} files, "
                   f"{sec_analysis['china_mentions']} China mentions")

        return sec_analysis

    def process_contract_data(self):
        """Process US contract data (FPDS)"""
        logger.info("Processing US contract data...")

        contract_files = list(self.collected_path.glob("italy_us/fpds_contracts/*.csv"))

        contract_analysis = {
            'files_processed': len(contract_files),
            'total_contracts': 0,
            'total_value': 0,
            'china_related': 0,
            'dual_use': 0,
            'contract_details': []
        }

        for file_path in contract_files:
            try:
                df = pd.read_csv(file_path)
                contract_analysis['total_contracts'] += len(df)

                # Process each contract
                for _, row in df.iterrows():
                    contract_text = ' '.join([str(val) for val in row.values if pd.notna(val)])

                    china_score = self._calculate_china_score(contract_text)
                    dual_use_keywords = self._check_dual_use(contract_text)

                    # Extract contract value if available
                    value = self._extract_contract_value(row)
                    if value:
                        contract_analysis['total_value'] += value

                    if china_score > 0 or dual_use_keywords:
                        contract_detail = {
                            'file': file_path.name,
                            'contractor': row.get('contractor_name', 'Unknown'),
                            'description': row.get('description', ''),
                            'value': value,
                            'china_score': china_score,
                            'dual_use_keywords': dual_use_keywords
                        }

                        contract_analysis['contract_details'].append(contract_detail)
                        self.results['contract_patterns'].append(contract_detail)

                        if china_score > 0:
                            contract_analysis['china_related'] += 1
                        if dual_use_keywords:
                            contract_analysis['dual_use'] += 1

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

        self.results['statistics']['contract_files'] = contract_analysis['files_processed']
        self.results['statistics']['total_contracts'] = contract_analysis['total_contracts']
        self.results['statistics']['contract_value'] = contract_analysis['total_value']

        logger.info(f"Contracts: {contract_analysis['total_contracts']} total, "
                   f"${contract_analysis['total_value']:,.0f} value, "
                   f"{contract_analysis['china_related']} China-related")

        return contract_analysis

    def process_research_data(self):
        """Process research collaboration data"""
        logger.info("Processing research collaboration data...")

        research_files = [
            self.collected_path / "openaire/italy_china_research_analysis.json",
            *list(self.processed_path.glob("openalex_bulk/*.json")),
            *list(self.processed_path.glob("italy_cordis/*.json"))
        ]

        research_analysis = {
            'files_processed': 0,
            'collaborations': 0,
            'institutions': set(),
            'dual_use_research': 0
        }

        for file_path in research_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        research_analysis['files_processed'] += 1

                        # Process different research data formats
                        collaborations = self._extract_research_collaborations(data)
                        research_analysis['collaborations'] += len(collaborations)

                        for collab in collaborations:
                            if collab.get('chinese_institutions'):
                                self.results['research_collaborations'].append({
                                    'source': file_path.name,
                                    'title': collab.get('title', ''),
                                    'institutions': collab.get('institutions', []),
                                    'chinese_partners': collab.get('chinese_institutions', []),
                                    'dual_use': collab.get('dual_use', False)
                                })

                                if collab.get('dual_use'):
                                    research_analysis['dual_use_research'] += 1

                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

        self.results['statistics']['research_files'] = research_analysis['files_processed']
        self.results['statistics']['research_collaborations'] = research_analysis['collaborations']

        logger.info(f"Research: {research_analysis['files_processed']} files, "
                   f"{research_analysis['collaborations']} collaborations")

        return research_analysis

    def _extract_patent_text(self, patent: dict) -> str:
        """Extract searchable text from patent data"""
        text_fields = ['title', 'abstract', 'description', 'inventors', 'assignees']
        text = ''

        for field in text_fields:
            value = patent.get(field, '')
            if isinstance(value, list):
                text += ' ' + ' '.join([str(v) for v in value])
            elif value:
                text += ' ' + str(value)

        return text.lower()

    def _extract_sec_text(self, data: dict) -> str:
        """Extract searchable text from SEC filing"""
        text_fields = ['business_description', 'risk_factors', 'md_a', 'notes']
        text = ''

        for field in text_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    text += ' ' + value
                elif isinstance(value, list):
                    text += ' ' + ' '.join([str(v) for v in value])

        return text.lower()

    def _calculate_china_score(self, text: str) -> int:
        """Calculate China relevance score"""
        score = 0
        for pattern in self.china_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches
        return score

    def _check_dual_use(self, text: str) -> list:
        """Check for dual-use technology keywords"""
        found_keywords = []
        for pattern in self.dual_use_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Extract the actual matched word
                matches = re.findall(pattern, text, re.IGNORECASE)
                found_keywords.extend(matches)
        return list(set(found_keywords))

    def _assess_patent_risk(self, china_score: int, dual_use_keywords: list) -> str:
        """Assess risk level of patent"""
        if china_score > 0 and dual_use_keywords:
            return 'HIGH'
        elif china_score > 2 or len(dual_use_keywords) > 2:
            return 'MEDIUM'
        elif china_score > 0 or dual_use_keywords:
            return 'LOW'
        else:
            return 'NONE'

    def _extract_contract_value(self, row) -> float:
        """Extract contract value from row"""
        value_fields = ['total_value', 'contract_value', 'amount', 'value']
        for field in value_fields:
            if field in row and pd.notna(row[field]):
                try:
                    # Handle string values with currency symbols
                    value_str = str(row[field]).replace('$', '').replace(',', '')
                    return float(value_str)
                except:
                    continue
        return 0.0

    def _extract_risk_disclosures(self, text: str) -> list:
        """Extract risk disclosures from SEC text"""
        risk_patterns = [
            r'risk.{0,50}china',
            r'china.{0,50}risk',
            r'supply chain.{0,50}risk',
            r'geopolitical.{0,50}risk',
            r'trade.{0,50}war',
            r'tariff.{0,50}impact'
        ]

        disclosures = []
        for pattern in risk_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            disclosures.extend(matches)

        return disclosures

    def _extract_research_collaborations(self, data: dict) -> list:
        """Extract research collaborations from data"""
        collaborations = []

        # Handle different data formats
        if 'works' in data:
            for work in data['works']:
                collab = {
                    'title': work.get('title', ''),
                    'institutions': [inst.get('display_name', '')
                                   for inst in work.get('institutions', [])],
                    'chinese_institutions': [inst.get('display_name', '')
                                           for inst in work.get('institutions', [])
                                           if inst.get('country_code') == 'CN'],
                    'dual_use': len(self._check_dual_use(work.get('title', ''))) > 0
                }
                collaborations.append(collab)

        elif 'collaborations' in data:
            collaborations.extend(data['collaborations'])

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'title' in item:
                    collab = {
                        'title': item.get('title', ''),
                        'institutions': item.get('institutions', []),
                        'chinese_institutions': [inst for inst in item.get('institutions', [])
                                               if any(cn in inst.lower() for cn in ['china', 'chinese', 'beijing'])],
                        'dual_use': len(self._check_dual_use(item.get('title', ''))) > 0
                    }
                    collaborations.append(collab)

        return collaborations

    def generate_comprehensive_report(self) -> dict:
        """Generate comprehensive analysis report"""
        # Calculate summary statistics
        total_china_indicators = (
            self.results['statistics'].get('leonardo_china', 0) +
            self.results['statistics'].get('sec_china_mentions', 0) +
            len([c for c in self.results['contract_patterns'] if c.get('china_score', 0) > 0])
        )

        total_dual_use = (
            self.results['leonardo_analysis'].get('dual_use', 0) +
            len([f for f in self.results['dual_use_findings']]) +
            len([c for c in self.results['contract_patterns'] if c.get('dual_use_keywords')])
        )

        # Assess risk level
        risk_level = 'LOW'
        if total_china_indicators > 10:
            risk_level = 'MEDIUM'
        if total_china_indicators > 50 or total_dual_use > 20:
            risk_level = 'HIGH'
        if total_china_indicators > 100 and total_dual_use > 50:
            risk_level = 'CRITICAL'

        report = {
            'generated_at': datetime.now().isoformat(),
            'data_sources_processed': len(self.results['sources_processed']),
            'summary_statistics': {
                'total_china_indicators': total_china_indicators,
                'total_dual_use_findings': total_dual_use,
                'leonardo_patents_analyzed': self.results['statistics'].get('leonardo_patents', 0),
                'contracts_analyzed': self.results['statistics'].get('total_contracts', 0),
                'contract_value_analyzed': self.results['statistics'].get('contract_value', 0),
                'research_collaborations': self.results['statistics'].get('research_collaborations', 0)
            },
            'risk_assessment': {
                'overall_risk_level': risk_level,
                'china_exposure': total_china_indicators,
                'dual_use_exposure': total_dual_use,
                'confidence': 0.8
            },
            'detailed_findings': {
                'leonardo_analysis': self.results['leonardo_analysis'],
                'china_connections': self.results['china_connections'],
                'dual_use_findings': self.results['dual_use_findings'],
                'contract_patterns': self.results['contract_patterns'],
                'research_collaborations': self.results['research_collaborations']
            },
            'recommendations': self._generate_recommendations(total_china_indicators, total_dual_use)
        }

        return report

    def _generate_recommendations(self, china_indicators: int, dual_use: int) -> list:
        """Generate actionable recommendations"""
        recommendations = []

        if china_indicators > 50:
            recommendations.append("CRITICAL: Comprehensive review of all China connections required")

        if dual_use > 20:
            recommendations.append("HIGH PRIORITY: Audit dual-use technology exposure")

        if self.results['leonardo_analysis'].get('china_related', 0) > 5:
            recommendations.append("INVESTIGATE: Leonardo China patent relationships need detailed review")

        if len(self.results['contract_patterns']) > 10:
            recommendations.append("REVIEW: Significant contract patterns identified")

        recommendations.extend([
            "EXPAND: Process additional data sources for complete picture",
            "MONITOR: Establish ongoing surveillance of identified patterns",
            "VALIDATE: Cross-reference with classified intelligence sources"
        ])

        return recommendations

    def process_all_data(self):
        """Process all available downloaded data"""
        logger.info("="*60)
        logger.info("EXISTING DATA COMPREHENSIVE PROCESSING")
        logger.info("="*60)

        # Process each data source
        leonardo_data = self.process_leonardo_patents()
        sec_data = self.process_sec_edgar_data()
        contract_data = self.process_contract_data()
        research_data = self.process_research_data()

        # Generate comprehensive report
        report = self.generate_comprehensive_report()

        # Save results
        output_file = self.output_path / f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Display summary
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE ANALYSIS RESULTS")
        logger.info("="*60)

        stats = report['summary_statistics']
        logger.info(f"\nData Processed:")
        logger.info(f"  Leonardo Patents: {stats['leonardo_patents_analyzed']}")
        logger.info(f"  US Contracts: {stats['contracts_analyzed']}")
        logger.info(f"  Contract Value: ${stats['contract_value_analyzed']:,.0f}")
        logger.info(f"  Research Collaborations: {stats['research_collaborations']}")

        logger.info(f"\nKey Findings:")
        logger.info(f"  Total China Indicators: {stats['total_china_indicators']}")
        logger.info(f"  Total Dual-Use Findings: {stats['total_dual_use_findings']}")

        logger.info(f"\nRisk Assessment:")
        risk = report['risk_assessment']
        logger.info(f"  Overall Risk Level: {risk['overall_risk_level']}")
        logger.info(f"  China Exposure: {risk['china_exposure']}")
        logger.info(f"  Dual-Use Exposure: {risk['dual_use_exposure']}")

        logger.info(f"\nTop Recommendations:")
        for rec in report['recommendations'][:3]:
            logger.info(f"  • {rec}")

        logger.info(f"\nFull results saved to: {output_file}")

        return report

def main():
    processor = ExistingDataProcessor()
    return processor.process_all_data()

if __name__ == "__main__":
    main()
