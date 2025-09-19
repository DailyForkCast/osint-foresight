#!/usr/bin/env python3
"""
TED Procurement Deep Analysis for Italy
Processes 40GB+ of EU procurement data to find:
1. Italian contracts with Chinese suppliers
2. Technology/defense procurements
3. Hidden supply chain dependencies
"""

import tarfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List
import logging
import gzip
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TEDItalyAnalyzer:
    """Deep analysis of TED procurement data for Italy"""

    def __init__(self):
        self.ted_path = Path("F:/TED_Data/monthly")
        self.output_dir = Path("data/processed/ted_italy_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Keywords indicating Chinese involvement
        self.china_indicators = [
            'china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou',
            'huawei', 'zte', 'lenovo', 'alibaba', 'tencent', 'baidu',
            'sinochem', 'sinopec', 'cnpc', 'cnooc', 'cosco', 'sinosteel',
            'china telecom', 'china mobile', 'china unicom',
            'bank of china', 'icbc', 'ccb', 'agricultural bank of china'
        ]

        # Technology/defense keywords
        self.tech_keywords = [
            'semiconductor', 'microchip', 'processor', 'integrated circuit',
            'radar', 'satellite', 'drone', 'uav', 'military', 'defense', 'defence',
            'aerospace', 'avionics', 'missile', 'submarine', 'frigate',
            'artificial intelligence', 'ai', 'machine learning', 'quantum',
            '5g', 'telecom', 'network equipment', 'cybersecurity',
            'battery', 'lithium', 'rare earth', 'solar panel', 'wind turbine'
        ]

        # Italian contracting authorities of interest
        self.italian_entities = [
            'leonardo', 'fincantieri', 'ministero della difesa',
            'ministry of defence', 'italian navy', 'aeronautica militare',
            'esercito italiano', 'carabinieri', 'polizia di stato',
            'agenzia spaziale italiana', 'asi', 'enea', 'cnr',
            'politecnico di milano', 'politecnico di torino',
            'università di bologna', 'sapienza',
            'enel', 'eni', 'terna', 'snam', 'italgas',
            'telecom italia', 'tim', 'vodafone italia'
        ]

        self.results = {
            'total_contracts': 0,
            'italian_contracts': 0,
            'china_related': [],
            'tech_defense': [],
            'supply_chain_risks': [],
            'timeline': {},
            'value_analysis': {},
            'entity_patterns': {}
        }

    def extract_and_analyze_year(self, year: int):
        """Extract and analyze all months for a given year"""

        year_dir = self.ted_path / str(year)
        if not year_dir.exists():
            logger.warning(f"Year directory {year} not found")
            return

        logger.info(f"Processing year {year}")

        for month in range(1, 13):
            month_file = year_dir / f"TED_monthly_{year}_{month:02d}.tar.gz"
            if month_file.exists():
                self.process_month_archive(month_file, year, month)

    def process_month_archive(self, archive_path: Path, year: int, month: int):
        """Process a monthly TED archive"""

        logger.info(f"Processing {year}-{month:02d}")
        temp_dir = self.output_dir / f"temp_{year}_{month:02d}"
        temp_dir.mkdir(exist_ok=True)

        try:
            # Extract archive
            with tarfile.open(archive_path, 'r:gz') as tar:
                # Extract only XML files related to Italy
                for member in tar.getmembers():
                    if member.name.endswith('.xml'):
                        # Extract to temp
                        tar.extract(member, path=temp_dir)

                        # Process the XML
                        xml_path = temp_dir / member.name
                        self.process_contract_xml(xml_path, year, month)

                        # Clean up to save space
                        xml_path.unlink()

        except Exception as e:
            logger.error(f"Error processing {archive_path}: {e}")

        finally:
            # Clean up temp directory
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)

    def process_contract_xml(self, xml_path: Path, year: int, month: int):
        """Process individual contract XML file"""

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Check if Italian contract
            country = self.extract_country(root)
            if country != 'IT':
                return

            self.results['italian_contracts'] += 1

            # Extract contract details
            contract = {
                'year': year,
                'month': month,
                'contract_id': self.extract_contract_id(root),
                'authority': self.extract_authority(root),
                'title': self.extract_title(root),
                'description': self.extract_description(root),
                'cpv_codes': self.extract_cpv_codes(root),
                'value': self.extract_value(root),
                'winner': self.extract_winner(root),
                'winner_country': self.extract_winner_country(root)
            }

            # Check for Chinese involvement
            if self.check_china_involvement(contract):
                self.results['china_related'].append(contract)
                logger.info(f"Found China-related contract: {contract['contract_id']}")

            # Check for tech/defense relevance
            if self.check_tech_defense(contract):
                self.results['tech_defense'].append(contract)

            # Update timeline
            period_key = f"{year}-{month:02d}"
            if period_key not in self.results['timeline']:
                self.results['timeline'][period_key] = {
                    'total': 0,
                    'china_related': 0,
                    'tech_defense': 0,
                    'total_value': 0
                }

            self.results['timeline'][period_key]['total'] += 1
            if contract['value']:
                self.results['timeline'][period_key]['total_value'] += contract['value']

        except Exception as e:
            logger.debug(f"Error processing XML {xml_path}: {e}")

    def extract_country(self, root) -> str:
        """Extract country code from XML"""
        # Try multiple possible paths for country code
        paths = [
            ".//ISO_COUNTRY",
            ".//CONTRACTING_BODY//ADDRESS_CONTRACTING_BODY//COUNTRY",
            ".//CONTRACTING_AUTHORITY//POSTAL_ADDRESS//COUNTRY",
            ".//COUNTRY_CODE"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                return elem.get('VALUE', elem.text)

        return None

    def extract_authority(self, root) -> str:
        """Extract contracting authority name"""
        paths = [
            ".//CONTRACTING_BODY//CA_CE//ORGANISATION//OFFICIALNAME",
            ".//CONTRACTING_AUTHORITY//NAME_ADDRESSES_CONTACT//CA_CE//ORGANISATION//OFFICIALNAME",
            ".//AUTH_NAME"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                return elem.text

        return "Unknown"

    def extract_title(self, root) -> str:
        """Extract contract title"""
        paths = [
            ".//OBJECT_CONTRACT//TITLE",
            ".//CONTRACT//TITLE",
            ".//TI_TEXT"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                return elem.text

        return ""

    def extract_description(self, root) -> str:
        """Extract contract description"""
        paths = [
            ".//OBJECT_CONTRACT//SHORT_DESCR",
            ".//CONTRACT//SHORT_CONTRACT_DESCRIPTION",
            ".//SHORT_DESCR"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                return elem.text

        return ""

    def extract_cpv_codes(self, root) -> List[str]:
        """Extract CPV classification codes"""
        codes = []
        for elem in root.findall(".//CPV_CODE"):
            code = elem.get('CODE', elem.text)
            if code:
                codes.append(code)
        return codes

    def extract_value(self, root) -> float:
        """Extract contract value"""
        paths = [
            ".//VALUE",
            ".//VAL_TOTAL",
            ".//TOTAL_FINAL_VALUE"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                try:
                    # Handle both VALUE attribute and text
                    value_str = elem.get('VALUE', elem.text)
                    if value_str:
                        # Remove currency symbols and convert
                        value_str = re.sub(r'[^\d.]', '', value_str)
                        return float(value_str)
                except:
                    pass

        return None

    def extract_winner(self, root) -> str:
        """Extract winning bidder name"""
        paths = [
            ".//AWARDED_CONTRACT//CONTRACTORS//CONTRACTOR//ADDRESS_CONTRACTOR//ORGANISATION//OFFICIALNAME",
            ".//ECONOMIC_OPERATOR_NAME_ADDRESS//ORGANISATION//OFFICIALNAME",
            ".//WINNER_NAME"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                return elem.text

        return None

    def extract_winner_country(self, root) -> str:
        """Extract winning bidder country"""
        paths = [
            ".//AWARDED_CONTRACT//CONTRACTORS//CONTRACTOR//ADDRESS_CONTRACTOR//COUNTRY",
            ".//ECONOMIC_OPERATOR_NAME_ADDRESS//COUNTRY",
            ".//WINNER_COUNTRY"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                return elem.get('VALUE', elem.text)

        return None

    def extract_contract_id(self, root) -> str:
        """Extract contract identifier"""
        paths = [
            ".//NOTICE_DATA//NO_DOC_OJS",
            ".//TED_EXPORT//DOC_ID",
            ".//CONTRACT_NUMBER"
        ]

        for path in paths:
            elem = root.find(path)
            if elem is not None:
                return elem.text

        return f"unknown_{datetime.now().timestamp()}"

    def check_china_involvement(self, contract: Dict) -> bool:
        """Check if contract involves Chinese entities"""

        # Check winner country
        if contract['winner_country'] == 'CN':
            return True

        # Check text fields for Chinese indicators
        text_to_check = ' '.join([
            contract.get('winner', ''),
            contract.get('title', ''),
            contract.get('description', '')
        ]).lower()

        for indicator in self.china_indicators:
            if indicator in text_to_check:
                return True

        return False

    def check_tech_defense(self, contract: Dict) -> bool:
        """Check if contract is tech/defense related"""

        # Check authority
        authority = contract.get('authority', '').lower()
        for entity in self.italian_entities:
            if entity in authority:
                # Check if also has tech keywords
                text_to_check = ' '.join([
                    contract.get('title', ''),
                    contract.get('description', '')
                ]).lower()

                for keyword in self.tech_keywords:
                    if keyword in text_to_check:
                        return True

        # Check CPV codes for technology categories
        tech_cpv_prefixes = [
            '30',  # Office and computing machinery
            '32',  # Radio, TV, communication
            '35',  # Security, fire-fighting, military
            '38',  # Laboratory, optical, precision equipment
            '48',  # Software
            '72'   # IT services
        ]

        for code in contract.get('cpv_codes', []):
            if any(code.startswith(prefix) for prefix in tech_cpv_prefixes):
                return True

        return False

    def analyze_patterns(self):
        """Analyze patterns in the collected data"""

        logger.info("Analyzing patterns...")

        # China involvement trends
        if self.results['china_related']:
            df_china = pd.DataFrame(self.results['china_related'])

            # Group by year
            china_by_year = df_china.groupby('year').agg({
                'contract_id': 'count',
                'value': 'sum'
            }).rename(columns={'contract_id': 'count'})

            self.results['china_trends'] = china_by_year.to_dict()

            # Top Chinese suppliers
            if 'winner' in df_china.columns:
                top_suppliers = df_china['winner'].value_counts().head(20)
                self.results['top_chinese_suppliers'] = top_suppliers.to_dict()

            # Sectors involved (by CPV)
            all_cpvs = []
            for cpvs in df_china['cpv_codes']:
                if cpvs:
                    all_cpvs.extend(cpvs)

            cpv_analysis = pd.Series(all_cpvs).value_counts().head(20)
            self.results['china_cpv_analysis'] = cpv_analysis.to_dict()

        # Technology procurement patterns
        if self.results['tech_defense']:
            df_tech = pd.DataFrame(self.results['tech_defense'])

            # Authorities procuring tech
            if 'authority' in df_tech.columns:
                top_authorities = df_tech['authority'].value_counts().head(20)
                self.results['tech_authorities'] = top_authorities.to_dict()

            # Tech procurement value over time
            tech_by_year = df_tech.groupby('year').agg({
                'contract_id': 'count',
                'value': 'sum'
            }).rename(columns={'contract_id': 'count'})

            self.results['tech_trends'] = tech_by_year.to_dict()

    def identify_supply_chain_risks(self):
        """Identify specific supply chain vulnerabilities"""

        logger.info("Identifying supply chain risks...")

        # Critical components from China
        critical_contracts = []

        for contract in self.results['china_related']:
            # Check if critical sector
            if self.check_tech_defense(contract):
                risk_score = self.calculate_risk_score(contract)

                if risk_score > 5:  # High risk threshold
                    critical_contracts.append({
                        'contract': contract,
                        'risk_score': risk_score,
                        'risk_factors': self.identify_risk_factors(contract)
                    })

        self.results['critical_dependencies'] = sorted(
            critical_contracts,
            key=lambda x: x['risk_score'],
            reverse=True
        )[:50]  # Top 50 risks

    def calculate_risk_score(self, contract: Dict) -> float:
        """Calculate risk score for a contract"""

        score = 0

        # Value factor
        if contract.get('value'):
            if contract['value'] > 10_000_000:
                score += 3
            elif contract['value'] > 1_000_000:
                score += 2
            else:
                score += 1

        # Authority criticality
        authority = contract.get('authority', '').lower()
        if any(term in authority for term in ['defense', 'difesa', 'military', 'militare']):
            score += 3
        elif any(term in authority for term in ['leonardo', 'fincantieri']):
            score += 2

        # Technology criticality
        text = (contract.get('title', '') + ' ' + contract.get('description', '')).lower()
        if any(term in text for term in ['semiconductor', 'chip', 'processor']):
            score += 3
        if any(term in text for term in ['5g', 'network', 'telecom']):
            score += 2
        if any(term in text for term in ['battery', 'lithium', 'rare earth']):
            score += 2

        return score

    def identify_risk_factors(self, contract: Dict) -> List[str]:
        """Identify specific risk factors in a contract"""

        factors = []

        if contract.get('winner_country') == 'CN':
            factors.append("Direct Chinese supplier")

        authority = contract.get('authority', '').lower()
        if 'defense' in authority or 'difesa' in authority:
            factors.append("Defense sector procurement")

        if 'leonardo' in authority:
            factors.append("Leonardo SpA involvement")

        text = (contract.get('title', '') + ' ' + contract.get('description', '')).lower()
        if 'semiconductor' in text or 'chip' in text:
            factors.append("Semiconductor dependency")

        if '5g' in text or 'telecom' in text:
            factors.append("Telecommunications infrastructure")

        if contract.get('value', 0) > 10_000_000:
            factors.append(f"High value: €{contract['value']:,.0f}")

        return factors

    def generate_report(self):
        """Generate comprehensive analysis report"""

        # Save raw data
        if self.results['china_related']:
            china_df = pd.DataFrame(self.results['china_related'])
            china_df.to_csv(self.output_dir / 'italy_china_contracts.csv', index=False)

        if self.results['tech_defense']:
            tech_df = pd.DataFrame(self.results['tech_defense'])
            tech_df.to_csv(self.output_dir / 'italy_tech_defense_contracts.csv', index=False)

        # Save analysis results
        with open(self.output_dir / 'ted_italy_analysis.json', 'w') as f:
            # Convert complex objects for JSON serialization
            results_json = {
                'summary': {
                    'total_italian_contracts': self.results['italian_contracts'],
                    'china_related_count': len(self.results['china_related']),
                    'tech_defense_count': len(self.results['tech_defense']),
                    'analysis_date': datetime.now().isoformat()
                },
                'china_trends': self.results.get('china_trends', {}),
                'tech_trends': self.results.get('tech_trends', {}),
                'top_chinese_suppliers': self.results.get('top_chinese_suppliers', {}),
                'tech_authorities': self.results.get('tech_authorities', {}),
                'timeline': self.results['timeline']
            }

            json.dump(results_json, f, indent=2, default=str)

        # Generate markdown report
        self.write_markdown_report()

        return self.results

    def write_markdown_report(self):
        """Write detailed markdown report"""

        report_path = self.output_dir / 'TED_ITALY_PROCUREMENT_ANALYSIS.md'

        with open(report_path, 'w') as f:
            f.write(f"""# Italy TED Procurement Analysis
**Generated:** {datetime.now().isoformat()}
**Data Period:** 2015-2025

## Executive Summary

- **Total Italian Contracts Analyzed:** {self.results['italian_contracts']:,}
- **China-Related Contracts:** {len(self.results['china_related'])}
- **Tech/Defense Contracts:** {len(self.results['tech_defense'])}

## Key Findings

### China Involvement
""")

            if self.results.get('top_chinese_suppliers'):
                f.write("\n**Top Chinese Suppliers:**\n")
                for supplier, count in list(self.results['top_chinese_suppliers'].items())[:10]:
                    f.write(f"- {supplier}: {count} contracts\n")

            if self.results.get('china_trends'):
                f.write("\n**China Contract Trends by Year:**\n")
                f.write("| Year | Contracts | Total Value (€) |\n")
                f.write("|------|-----------|----------------|\n")
                for year, data in self.results['china_trends'].items():
                    f.write(f"| {year} | {data.get('count', 0)} | {data.get('value', 0):,.0f} |\n")

            f.write("\n### Critical Dependencies\n")
            if self.results.get('critical_dependencies'):
                for item in self.results['critical_dependencies'][:10]:
                    contract = item['contract']
                    f.write(f"\n**{contract['contract_id']}**\n")
                    f.write(f"- Authority: {contract['authority']}\n")
                    f.write(f"- Title: {contract['title']}\n")
                    f.write(f"- Winner: {contract.get('winner', 'Unknown')}\n")
                    f.write(f"- Risk Score: {item['risk_score']}\n")
                    f.write(f"- Risk Factors: {', '.join(item['risk_factors'])}\n")

            f.write("\n## Recommendations\n\n")
            f.write("1. Review high-risk contracts for alternative suppliers\n")
            f.write("2. Map critical component dependencies\n")
            f.write("3. Develop contingency plans for Chinese supplier disruption\n")
            f.write("4. Increase supply chain transparency requirements\n")

        logger.info(f"Report saved to {report_path}")


def main():
    analyzer = TEDItalyAnalyzer()

    # Process recent years with likely China involvement
    for year in [2020, 2021, 2022, 2023, 2024]:
        analyzer.extract_and_analyze_year(year)

    # Analyze patterns
    analyzer.analyze_patterns()
    analyzer.identify_supply_chain_risks()

    # Generate report
    results = analyzer.generate_report()

    print(f"\n=== TED Italy Analysis Complete ===")
    print(f"Italian contracts analyzed: {results['italian_contracts']:,}")
    print(f"China-related contracts: {len(results['china_related'])}")
    print(f"Tech/Defense contracts: {len(results['tech_defense'])}")

    if results.get('critical_dependencies'):
        print(f"\nTop Critical Dependencies:")
        for item in results['critical_dependencies'][:5]:
            print(f"- {item['contract']['authority']}: Risk Score {item['risk_score']}")


if __name__ == "__main__":
    main()
