#!/usr/bin/env python3
"""
TED China Supplier Analysis - Enhanced procurement analysis for Chinese supplier detection
"""

import json
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TEDChinaSupplierAnalyzer:
    def __init__(self):
        self.ted_path = Path("F:/TED_Data/monthly")
        self.output_path = Path("reports/country=IT/ted_china_supplier_analysis.json")

        # Chinese company indicators
        self.chinese_indicators = {
            'company_suffixes': [
                'Ltd.', 'Limited', 'Co., Ltd.', 'Corporation', 'Corp.',
                'Technology Co.', 'Tech Co.', 'Electronic Co.', 'Electronics Co.',
                'Industrial Co.', 'Trading Co.', 'Import Export Co.'
            ],
            'chinese_cities': [
                'Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou', 'Hangzhou',
                'Nanjing', 'Tianjin', 'Wuhan', 'Chengdu', 'Xi\'an',
                'Suzhou', 'Dongguan', 'Foshan', 'Ningbo', 'Qingdao'
            ],
            'chinese_keywords': [
                'China', 'Chinese', 'Sino-', 'Asia Pacific', 'Far East',
                'Huawei', 'ZTE', 'Xiaomi', 'BYD', 'DJI', 'Lenovo',
                'Alibaba', 'Tencent', 'Baidu'
            ]
        }

        # Technology keywords (focused)
        self.tech_keywords = {
            'semiconductors': ['semiconductor', 'microchip', 'chip', 'processor', 'integrated circuit'],
            'telecommunications': ['5G', '6G', 'telecom', 'network equipment', 'base station'],
            'ai_ml': ['artificial intelligence', 'machine learning', 'AI', 'neural network'],
            'aerospace': ['aerospace', 'satellite', 'drone', 'UAV', 'aircraft'],
            'cybersecurity': ['cybersecurity', 'cyber security', 'firewall', 'encryption'],
            'defense': ['defense', 'defence', 'military', 'weapon', 'radar']
        }

        self.results = {
            'analysis_date': datetime.now().isoformat(),
            'data_coverage': [],
            'summary': {
                'total_procurements': 0,
                'italian_procurements': 0,
                'tech_procurements': 0,
                'china_linked_procurements': 0
            },
            'china_suppliers': [],
            'tech_by_category': {},
            'risk_indicators': []
        }

    def is_italian_procurement(self, root):
        """Enhanced Italian procurement detection"""
        # Check country codes
        for country in root.findall('.//COUNTRY'):
            if country.get('VALUE') == 'IT':
                return True

        # Check address elements
        for address in root.findall('.//ADDRESS'):
            addr_text = ET.tostring(address, encoding='unicode', method='text').lower()
            if any(indicator in addr_text for indicator in
                   ['italia', 'italy', 'roma', 'milan', 'torino', 'napoli', 'bologna']):
                return True

        # Check contracting body names
        for org in root.findall('.//OFFICIALNAME'):
            org_text = org.text or ''
            if any(indicator in org_text.lower() for indicator in
                   ['italia', 'italian', 'ministero', 'comune', 'regione', 'agenzia']):
                return True

        return False

    def extract_procurement_details(self, root):
        """Extract detailed procurement information"""
        details = {
            'title': 'Unknown',
            'authority': 'Unknown',
            'supplier': 'Unknown',
            'value': 0,
            'cpv_codes': [],
            'description': ''
        }

        # Title extraction (multiple approaches)
        title_elements = [
            './/TITLE_TEXT',
            './/SHORT_DESCR',
            './/TITLE',
            './/OBJECT_CONTRACT/TITLE'
        ]
        for elem in title_elements:
            title = root.findtext(elem)
            if title and title.strip() and title.strip() != 'No title':
                details['title'] = title.strip()[:200]
                break

        # Authority extraction
        authority_elements = [
            './/OFFICIALNAME',
            './/NAME_ADDRESSES_CONTACT/OFFICIALNAME',
            './/CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY/OFFICIALNAME'
        ]
        for elem in authority_elements:
            authority = root.findtext(elem)
            if authority and authority.strip():
                details['authority'] = authority.strip()[:100]
                break

        # Supplier extraction (from awards)
        supplier_elements = [
            './/AWARDED_CONTRACT/CONTRACTOR/ADDRESS_CONTRACTOR/OFFICIALNAME',
            './/CONTRACTOR/OFFICIALNAME',
            './/AWARDED_TO/OFFICIALNAME'
        ]
        for elem in supplier_elements:
            supplier = root.findtext(elem)
            if supplier and supplier.strip():
                details['supplier'] = supplier.strip()[:100]
                break

        # Value extraction
        value_elements = [
            './/VAL_TOTAL',
            './/VALUE',
            './/INITIAL_VALUE',
            './/VAL_ESTIMATED_TOTAL'
        ]
        for elem in value_elements:
            val_elem = root.find(elem)
            if val_elem is not None:
                try:
                    value_text = val_elem.text or val_elem.get('VALUE', '0')
                    # Clean numeric value
                    value_clean = re.sub(r'[^\d.]', '', value_text)
                    if value_clean:
                        details['value'] = float(value_clean)
                        break
                except:
                    continue

        # CPV codes
        for cpv in root.findall('.//CPV_CODE'):
            code = cpv.get('CODE')
            if code:
                details['cpv_codes'].append(code)

        # Description
        desc_elements = ['.//SHORT_DESCR', './/DESCRIPTION']
        for elem in desc_elements:
            desc = root.findtext(elem)
            if desc and desc.strip():
                details['description'] = desc.strip()[:500]
                break

        return details

    def detect_chinese_supplier(self, supplier_name, full_text):
        """Detect if supplier appears to be Chinese"""
        if not supplier_name or supplier_name == 'Unknown':
            return False, []

        indicators_found = []
        supplier_lower = supplier_name.lower()
        text_lower = full_text.lower()

        # Check for Chinese cities
        for city in self.chinese_indicators['chinese_cities']:
            if city.lower() in text_lower:
                indicators_found.append(f"Chinese city: {city}")

        # Check for Chinese keywords
        for keyword in self.chinese_indicators['chinese_keywords']:
            if keyword.lower() in supplier_lower or keyword.lower() in text_lower:
                indicators_found.append(f"Chinese keyword: {keyword}")

        # Check for Chinese company patterns
        if any(suffix in supplier_name for suffix in ['(China)', 'China Ltd', 'Beijing', 'Shanghai']):
            indicators_found.append("Chinese company pattern")

        return len(indicators_found) > 0, indicators_found

    def identify_technologies(self, title, description):
        """Identify technology categories"""
        text = f"{title} {description}".lower()
        found_techs = []

        for tech_cat, keywords in self.tech_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                found_techs.append(tech_cat)

        return found_techs

    def analyze_procurement(self, root):
        """Analyze single procurement for China links and technology"""
        self.results['summary']['total_procurements'] += 1

        if not self.is_italian_procurement(root):
            return

        self.results['summary']['italian_procurements'] += 1

        # Extract details
        details = self.extract_procurement_details(root)

        # Identify technologies
        technologies = self.identify_technologies(details['title'], details['description'])

        if technologies:
            self.results['summary']['tech_procurements'] += 1
            for tech in technologies:
                self.results['tech_by_category'][tech] = self.results['tech_by_category'].get(tech, 0) + 1

            # Check for Chinese suppliers
            full_text = ET.tostring(root, encoding='unicode', method='text')
            is_chinese, indicators = self.detect_chinese_supplier(details['supplier'], full_text)

            if is_chinese:
                self.results['summary']['china_linked_procurements'] += 1

                china_procurement = {
                    'title': details['title'],
                    'authority': details['authority'],
                    'supplier': details['supplier'],
                    'value': details['value'],
                    'technologies': technologies,
                    'chinese_indicators': indicators,
                    'risk_level': self.assess_risk_level(technologies, details['value'])
                }

                self.results['china_suppliers'].append(china_procurement)
                logger.info(f"CHINA LINK FOUND: {details['supplier']} - {technologies}")

    def assess_risk_level(self, technologies, value):
        """Assess risk level of Chinese procurement"""
        high_risk_techs = ['defense', 'cybersecurity', 'semiconductors', 'telecommunications']

        if any(tech in high_risk_techs for tech in technologies):
            if value > 1000000:  # High value
                return 'CRITICAL'
            else:
                return 'HIGH'
        elif technologies:  # Any technology
            return 'MEDIUM'
        else:
            return 'LOW'

    def process_multiple_months(self, max_months=6):
        """Process multiple recent months for comprehensive analysis"""

        # Get recent months across years
        month_files = []
        for year_dir in sorted(self.ted_path.iterdir(), reverse=True):
            if year_dir.is_dir() and year_dir.name.isdigit():
                year_files = list(year_dir.glob("TED_monthly_*.tar.gz"))
                for file in sorted(year_files, reverse=True):
                    month_files.append((year_dir.name, file))
                    if len(month_files) >= max_months:
                        break
            if len(month_files) >= max_months:
                break

        logger.info(f"Processing {len(month_files)} months of TED data")

        for year, tar_file in month_files[:max_months]:
            month_name = f"{year}/{tar_file.name}"
            self.results['data_coverage'].append(month_name)
            logger.info(f"Processing {month_name}")

            try:
                with tarfile.open(tar_file, 'r:gz') as outer_tar:
                    processed_files = 0
                    for member in outer_tar.getmembers():
                        if member.name.endswith('.tar.gz'):
                            inner_tar_file = outer_tar.extractfile(member)
                            if inner_tar_file:
                                try:
                                    with tarfile.open(fileobj=inner_tar_file, mode='r:gz') as inner_tar:
                                        for inner_member in inner_tar.getmembers():
                                            if inner_member.name.endswith('.xml'):
                                                xml_file = inner_tar.extractfile(inner_member)
                                                if xml_file:
                                                    try:
                                                        content = xml_file.read()
                                                        root = ET.fromstring(content)
                                                        self.analyze_procurement(root)
                                                        processed_files += 1

                                                        # Limit per month for performance
                                                        if processed_files >= 500:
                                                            break
                                                    except Exception as e:
                                                        continue
                                            if processed_files >= 500:
                                                break
                                except Exception as e:
                                    logger.warning(f"Error with inner archive: {e}")
                                    continue

                logger.info(f"Completed {month_name}: {processed_files} files processed")

            except Exception as e:
                logger.error(f"Error processing {tar_file}: {e}")

    def generate_final_report(self):
        """Generate comprehensive China supplier risk report"""

        # Calculate risk metrics
        if self.results['summary']['tech_procurements'] > 0:
            china_penetration = (self.results['summary']['china_linked_procurements'] /
                               self.results['summary']['tech_procurements']) * 100
        else:
            china_penetration = 0

        # Risk indicators
        self.results['risk_indicators'] = [
            f"Chinese suppliers found in {self.results['summary']['china_linked_procurements']} technology procurements",
            f"China penetration rate: {china_penetration:.1f}% of Italian tech procurements",
            f"Primary risk areas: {list(self.results['tech_by_category'].keys())}",
            f"Data coverage: {len(self.results['data_coverage'])} months analyzed"
        ]

        # Save comprehensive report
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"China supplier analysis saved to {self.output_path}")
        return self.results

def main():
    analyzer = TEDChinaSupplierAnalyzer()
    analyzer.process_multiple_months(max_months=6)  # Last 6 months
    report = analyzer.generate_final_report()

    print(f"\n=== TED China Supplier Analysis Results ===")
    print(f"Data coverage: {len(report['data_coverage'])} months")
    print(f"Total procurements: {report['summary']['total_procurements']}")
    print(f"Italian tech procurements: {report['summary']['tech_procurements']}")
    print(f"China-linked procurements: {report['summary']['china_linked_procurements']}")

    if report['summary']['tech_procurements'] > 0:
        penetration = (report['summary']['china_linked_procurements'] /
                      report['summary']['tech_procurements']) * 100
        print(f"China penetration rate: {penetration:.1f}%")

    print(f"\nTechnology categories found:")
    for tech, count in report['tech_by_category'].items():
        print(f"  {tech}: {count}")

if __name__ == "__main__":
    main()
