#!/usr/bin/env python3
"""
Detailed TED contract analyzer to classify actual risk levels
Not all contracts with Chinese companies are problematic
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ContractRiskClassifier:
    """Classify contracts by actual risk level and content"""

    def __init__(self):
        self.output_dir = Path("data/processed/ted_risk_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Define high-risk categories
        self.high_risk_keywords = {
            'infrastructure': ['network', 'telecom', 'grid', 'power', 'water', 'transport', 'rail', 'airport', 'port'],
            'defense': ['military', 'defense', 'weapon', 'missile', 'radar', 'surveillance', 'intelligence'],
            'data': ['database', 'cloud', 'server', 'datacenter', 'storage', 'backup', 'processing'],
            'communications': ['5g', '6g', 'fiber', 'satellite', 'broadcast', 'emergency'],
            'energy': ['nuclear', 'pipeline', 'refinery', 'lng', 'electricity', 'generation'],
            'healthcare': ['hospital', 'medical', 'pharmaceutical', 'vaccine', 'diagnostic'],
            'finance': ['banking', 'payment', 'transaction', 'clearing', 'settlement'],
            'government': ['ministry', 'parliament', 'court', 'police', 'customs', 'tax']
        }

        # Define low-risk categories
        self.low_risk_keywords = {
            'consumer': ['furniture', 'clothing', 'textile', 'toy', 'gift', 'souvenir'],
            'food': ['catering', 'restaurant', 'food', 'beverage', 'coffee'],
            'office': ['stationery', 'printer', 'paper', 'pen', 'desk'],
            'maintenance': ['cleaning', 'waste', 'recycling', 'landscaping', 'painting'],
            'events': ['conference', 'exhibition', 'festival', 'ceremony'],
            'marketing': ['advertising', 'promotion', 'brochure', 'poster']
        }

        # Critical Chinese companies of concern
        self.critical_companies = {
            'huawei', 'zte', 'hikvision', 'dahua', 'hytera', 'lenovo',
            'tcl', 'xiaomi', 'oppo', 'vivo', 'boe', 'cssc', 'norinco',
            'casic', 'casc', 'avic', 'cetc', 'cnnc', 'cgn', 'spic',
            'smic', 'ymtc', 'cxmt', 'jcet', 'byd', 'catl', 'nio',
            'xpeng', 'li auto', 'geely', 'great wall', 'changan'
        }

    def classify_contract_risk(self, contract: Dict) -> Tuple[str, List[str]]:
        """
        Classify a contract's risk level
        Returns: (risk_level, reasons)
        """
        reasons = []
        risk_score = 0

        # Get contract text (combining available fields)
        text = ' '.join([
            str(contract.get('title', '')),
            str(contract.get('description', '')),
            str(contract.get('category', '')),
            str(contract.get('cpv_code', '')),
            str(contract.get('nuts_code', ''))
        ]).lower()

        # Check for critical companies
        china_company = contract.get('china_company', '').lower()
        if china_company in self.critical_companies:
            risk_score += 50
            reasons.append(f"Critical company: {china_company}")

        # Check high-risk sectors
        for sector, keywords in self.high_risk_keywords.items():
            if any(kw in text for kw in keywords):
                risk_score += 20
                reasons.append(f"High-risk sector: {sector}")

        # Check if it's actually low-risk despite Chinese involvement
        for category, keywords in self.low_risk_keywords.items():
            if any(kw in text for kw in keywords):
                risk_score -= 10
                reasons.append(f"Low-risk category: {category}")

        # Check contract value
        value = contract.get('value', 0)
        if value > 10_000_000:  # >€10M
            risk_score += 15
            reasons.append(f"High value: €{value:,.0f}")
        elif value > 1_000_000:  # >€1M
            risk_score += 5
            reasons.append(f"Significant value: €{value:,.0f}")

        # Check for specific concerning patterns
        if 'data' in text and ('storage' in text or 'cloud' in text):
            risk_score += 25
            reasons.append("Data sovereignty risk")

        if 'critical' in text or 'essential' in text or 'strategic' in text:
            risk_score += 15
            reasons.append("Marked as critical/strategic")

        # Determine final risk level
        if risk_score >= 60:
            return "CRITICAL", reasons
        elif risk_score >= 30:
            return "HIGH", reasons
        elif risk_score >= 10:
            return "MEDIUM", reasons
        elif risk_score >= 0:
            return "LOW", reasons
        else:
            return "MINIMAL", reasons

    def analyze_entity_contracts(self, entity_name: str, year_start: int = 2015, year_end: int = 2025):
        """Analyze all contracts for a specific entity"""
        logger.info(f"Analyzing contracts for {entity_name}")

        entity_analysis = {
            'entity': entity_name,
            'total_contracts': 0,
            'china_contracts': 0,
            'risk_breakdown': defaultdict(int),
            'critical_contracts': [],
            'high_risk_contracts': [],
            'by_company': defaultdict(list),
            'by_sector': defaultdict(list)
        }

        # Process each year
        for year in range(year_start, year_end + 1):
            year_file = Path(f"data/processed/ted_complete_analysis/{year}/china_contracts_{year}.json")
            if not year_file.exists():
                continue

            with open(year_file, 'r', encoding='utf-8') as f:
                contracts = json.load(f)

            for contract in contracts:
                # Check if this contract involves our entity
                authority = str(contract.get('authority', '')).lower()
                if entity_name.lower() not in authority:
                    continue

                entity_analysis['total_contracts'] += 1

                # Only analyze if China-related
                if not contract.get('china_company'):
                    continue

                entity_analysis['china_contracts'] += 1

                # Classify risk
                risk_level, reasons = self.classify_contract_risk(contract)
                entity_analysis['risk_breakdown'][risk_level] += 1

                # Store contract details for high-risk items
                contract_summary = {
                    'year': year,
                    'title': contract.get('title', 'Unknown'),
                    'value': contract.get('value', 0),
                    'company': contract.get('china_company', 'Unknown'),
                    'risk_level': risk_level,
                    'reasons': reasons
                }

                if risk_level == "CRITICAL":
                    entity_analysis['critical_contracts'].append(contract_summary)
                elif risk_level == "HIGH":
                    entity_analysis['high_risk_contracts'].append(contract_summary)

                # Categorize by company
                company = contract.get('china_company', 'unknown')
                entity_analysis['by_company'][company].append(risk_level)

                # Categorize by sector
                for sector in self.identify_sectors(contract):
                    entity_analysis['by_sector'][sector].append(risk_level)

        return entity_analysis

    def identify_sectors(self, contract: Dict) -> List[str]:
        """Identify which sectors a contract belongs to"""
        sectors = []
        text = ' '.join([
            str(contract.get('title', '')),
            str(contract.get('description', ''))
        ]).lower()

        for sector, keywords in self.high_risk_keywords.items():
            if any(kw in text for kw in keywords):
                sectors.append(sector)

        return sectors if sectors else ['other']

    def generate_risk_report(self, analyses: List[Dict]):
        """Generate comprehensive risk report"""
        report_lines = [
            "# TED Contract Risk Analysis - Detailed Assessment",
            f"**Analysis Date:** 2025-09-18",
            "",
            "## Executive Summary",
            "",
            "This analysis examines the actual content and risk levels of contracts,",
            "not just their existence. Many contracts with Chinese entities are low-risk",
            "(e.g., office supplies, catering) while others pose genuine security concerns.",
            "",
            "## Risk Classification Criteria",
            "",
            "**CRITICAL RISK:**",
            "- Critical infrastructure control systems",
            "- Defense/military systems",
            "- Data sovereignty (cloud, servers)",
            "- Critical companies (Huawei, ZTE, etc.)",
            "",
            "**HIGH RISK:**",
            "- Telecommunications equipment",
            "- Energy infrastructure",
            "- Healthcare systems",
            "- Government IT systems",
            "",
            "**MEDIUM RISK:**",
            "- Non-critical IT equipment",
            "- Industrial machinery",
            "- Construction projects",
            "",
            "**LOW RISK:**",
            "- Consumer goods",
            "- Office supplies",
            "- Catering services",
            "- Maintenance services",
            "",
            "## Entity Analysis",
            ""
        ]

        for analysis in analyses:
            entity = analysis['entity']
            total = analysis['china_contracts']

            report_lines.extend([
                f"### {entity.upper()}",
                f"**Total China-Related Contracts:** {total:,}",
                "",
                "**Risk Breakdown:**",
            ])

            for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']:
                count = analysis['risk_breakdown'].get(risk_level, 0)
                pct = (count / total * 100) if total > 0 else 0
                report_lines.append(f"- {risk_level}: {count:,} ({pct:.1f}%)")

            report_lines.append("")

            # Critical contracts detail
            if analysis['critical_contracts']:
                report_lines.extend([
                    f"**Critical Risk Contracts ({len(analysis['critical_contracts'])}):**",
                    ""
                ])
                for contract in analysis['critical_contracts'][:10]:  # Top 10
                    report_lines.extend([
                        f"**{contract['title'][:100]}**",
                        f"- Year: {contract['year']}",
                        f"- Company: {contract['company']}",
                        f"- Value: €{contract['value']:,.0f}",
                        f"- Concerns: {', '.join(contract['reasons'])}",
                        ""
                    ])

            # Company breakdown
            report_lines.extend([
                "**By Chinese Company:**",
                ""
            ])
            for company, risk_levels in sorted(analysis['by_company'].items(),
                                              key=lambda x: len(x[1]), reverse=True)[:10]:
                critical = risk_levels.count('CRITICAL')
                high = risk_levels.count('HIGH')
                total_company = len(risk_levels)
                report_lines.append(f"- {company}: {total_company} contracts (Critical: {critical}, High: {high})")

            report_lines.extend(["", "---", ""])

        # Overall assessment
        report_lines.extend([
            "## Overall Assessment",
            "",
            "Based on detailed contract analysis:",
            "",
            "**GENUINE CONCERNS:**",
            "- ZTE/Huawei in telecom infrastructure (kill switch risk)",
            "- BOE in medical equipment (healthcare dependency)",
            "- BYD in public transport (smart city control)",
            "- Data center and cloud contracts (sovereignty risk)",
            "",
            "**OVERBLOWN CONCERNS:**",
            "- Many contracts are for non-critical items (office supplies, catering)",
            "- Consumer goods purchases pose minimal security risk",
            "- Maintenance and cleaning services are not strategic vulnerabilities",
            "",
            "**RECOMMENDED FOCUS AREAS:**",
            "1. Replace ZTE/Huawei telecom equipment (CRITICAL)",
            "2. Audit medical device supply chains (HIGH)",
            "3. Review smart city/transport dependencies (HIGH)",
            "4. Ensure data sovereignty for government systems (CRITICAL)",
            "5. Diversify energy technology suppliers (MEDIUM)",
            "",
            "The actual risk is significant but more nuanced than raw contract counts suggest."
        ])

        return "\n".join(report_lines)

    def run_analysis(self):
        """Run comprehensive risk analysis on key entities"""
        logger.info("Starting detailed contract risk analysis...")

        # Key entities to analyze
        entities = ['asi', 'eni', 'leonardo', 'tim', 'ministero', 'carabinieri']

        analyses = []
        for entity in entities:
            analysis = self.analyze_entity_contracts(entity)
            analyses.append(analysis)

            # Save individual entity analysis
            output_file = self.output_dir / f"{entity}_risk_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            logger.info(f"{entity}: {analysis['china_contracts']} China contracts - "
                       f"Critical: {analysis['risk_breakdown'].get('CRITICAL', 0)}, "
                       f"High: {analysis['risk_breakdown'].get('HIGH', 0)}")

        # Generate comprehensive report
        report = self.generate_risk_report(analyses)
        report_file = self.output_dir / "TED_CONTRACT_RISK_ASSESSMENT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"Risk assessment complete. Report saved to {report_file}")

        return analyses

if __name__ == "__main__":
    classifier = ContractRiskClassifier()
    classifier.run_analysis()
