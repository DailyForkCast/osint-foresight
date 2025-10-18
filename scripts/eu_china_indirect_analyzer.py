#!/usr/bin/env python3
"""
EU-China Indirect Relationship Analyzer
Identifies indirect Chinese involvement through:
- Subcontractors
- Joint ventures
- Technology dependencies
- Supply chain relationships
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IndirectChineseAnalyzer:
    """Analyzer for indirect Chinese involvement in EU procurement"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'direct_chinese': 0,
            'indirect_indicators': 0,
            'technology_dependencies': [],
            'suspicious_patterns': [],
            'joint_ventures': [],
            'supply_chain_risks': [],
            'recommendations': []
        }

    def analyze_indirect_relationships(self):
        """Main analysis for indirect Chinese relationships"""

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        logger.info("Starting indirect Chinese relationship analysis...")

        # 1. Check for technology dependencies
        self.check_technology_dependencies(cur)

        # 2. Look for joint ventures and consortiums
        self.find_joint_ventures(cur)

        # 3. Analyze supply chain indicators
        self.analyze_supply_chain(cur)

        # 4. Check for Chinese technology products
        self.check_chinese_products(cur)

        # 5. Analyze telecommunication contracts
        self.analyze_telecom_contracts(cur)

        # 6. Look for infrastructure projects
        self.analyze_infrastructure(cur)

        conn.close()

        return self.results

    def check_technology_dependencies(self, cursor):
        """Check for dependencies on Chinese technology"""

        logger.info("Checking technology dependencies...")

        # Chinese technology products and standards
        chinese_tech = [
            ('5G', ['Huawei', 'ZTE']),
            ('surveillance', ['Hikvision', 'Dahua']),
            ('drone', ['DJI']),
            ('telecom equipment', ['Huawei', 'ZTE']),
            ('network equipment', ['Huawei', 'H3C', 'TP-Link']),
            ('solar panel', ['Jinko', 'Trina', 'LONGi']),
            ('battery', ['CATL', 'BYD']),
            ('electric bus', ['BYD', 'Yutong']),
            ('train', ['CRRC']),
            ('port equipment', ['ZPMC'])
        ]

        for tech_type, companies in chinese_tech:
            # Search for the technology type
            cursor.execute('''
                SELECT contract_id, contractor_name, contract_title,
                       contract_description, contracting_authority, country
                FROM ted_china_contracts
                WHERE (contract_title LIKE ? OR contract_description LIKE ?)
                AND contractor_name IS NOT NULL
                LIMIT 100
            ''', (f'%{tech_type}%', f'%{tech_type}%'))

            for row in cursor.fetchall():
                contract_id, contractor, title, description, authority, country = row

                # Check if any Chinese companies might be involved
                text_to_check = f"{contractor or ''} {title or ''} {description or ''}"

                for company in companies:
                    if company.lower() in text_to_check.lower():
                        self.results['technology_dependencies'].append({
                            'type': 'Direct Chinese Technology',
                            'technology': tech_type,
                            'chinese_company': company,
                            'contractor': contractor[:100] if contractor else 'N/A',
                            'country': country,
                            'contract_id': contract_id
                        })

                # Even if not directly mentioned, flag as potential dependency
                if tech_type in ['5G', 'telecom equipment', 'network equipment']:
                    self.results['technology_dependencies'].append({
                        'type': 'Potential Chinese Technology Dependency',
                        'technology': tech_type,
                        'contractor': contractor[:100] if contractor else 'N/A',
                        'title': title[:200] if title else 'N/A',
                        'country': country,
                        'note': f'May involve Chinese {tech_type} suppliers'
                    })

    def find_joint_ventures(self, cursor):
        """Find joint ventures and consortiums that might include Chinese partners"""

        logger.info("Looking for joint ventures and consortiums...")

        # Keywords indicating joint ventures or consortiums
        jv_keywords = ['consortium', 'joint venture', 'JV', 'partnership', 'cooperation']

        for keyword in jv_keywords:
            cursor.execute('''
                SELECT contractor_name, contract_title, country, contract_id
                FROM ted_china_contracts
                WHERE contractor_name LIKE ?
                LIMIT 50
            ''', (f'%{keyword}%',))

            for contractor, title, country, contract_id in cursor.fetchall():
                if contractor:
                    self.results['joint_ventures'].append({
                        'contractor': contractor[:150],
                        'title': title[:150] if title else 'N/A',
                        'country': country,
                        'type': keyword,
                        'contract_id': contract_id,
                        'note': 'Potential for Chinese partner involvement'
                    })

    def analyze_supply_chain(self, cursor):
        """Analyze supply chain risks and dependencies"""

        logger.info("Analyzing supply chain indicators...")

        # Critical supply chain sectors
        supply_chain_cpv = {
            '30': 'IT equipment (often Chinese manufactured)',
            '31': 'Electrical machinery',
            '32': 'Telecommunications equipment',
            '34': 'Transport equipment',
            '38': 'Laboratory equipment',
            '44': 'Construction materials',
            '48': 'Software packages'
        }

        for cpv_code, description in supply_chain_cpv.items():
            cursor.execute('''
                SELECT COUNT(*) as count,
                       COUNT(DISTINCT contractor_name) as contractors
                FROM ted_china_contracts
                WHERE cpv_codes LIKE ?
            ''', (f'{cpv_code}%',))

            count, contractors = cursor.fetchone()

            if count > 0:
                # Get sample contracts
                cursor.execute('''
                    SELECT contractor_name, contract_title, country
                    FROM ted_china_contracts
                    WHERE cpv_codes LIKE ?
                    AND contractor_name IS NOT NULL
                    LIMIT 5
                ''', (f'{cpv_code}%',))

                samples = []
                for name, title, country in cursor.fetchall():
                    samples.append({
                        'contractor': name[:100] if name else 'N/A',
                        'title': title[:100] if title else 'N/A',
                        'country': country
                    })

                self.results['supply_chain_risks'].append({
                    'sector': description,
                    'cpv_prefix': cpv_code,
                    'total_contracts': count,
                    'unique_contractors': contractors,
                    'risk': 'High likelihood of Chinese components in supply chain',
                    'sample_contracts': samples
                })

    def check_chinese_products(self, cursor):
        """Check for specific Chinese products being procured"""

        logger.info("Checking for Chinese products...")

        # Known Chinese brands and products
        chinese_brands = [
            'Lenovo', 'Xiaomi', 'Oppo', 'Vivo', 'OnePlus', 'Realme',
            'TCL', 'Hisense', 'Haier', 'Midea', 'Gree',
            'Great Wall', 'Geely', 'BYD', 'NIO', 'Xpeng',
            'Alibaba Cloud', 'Tencent Cloud', 'Baidu Cloud',
            'WeChat', 'TikTok', 'DJI', 'Hikvision', 'Dahua'
        ]

        for brand in chinese_brands:
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM ted_china_contracts
                WHERE contract_title LIKE ? OR contract_description LIKE ?
            ''', (f'%{brand}%', f'%{brand}%'))

            count = cursor.fetchone()[0]

            if count > 0:
                # Get examples
                cursor.execute('''
                    SELECT contractor_name, contract_title, country
                    FROM ted_china_contracts
                    WHERE contract_title LIKE ? OR contract_description LIKE ?
                    LIMIT 3
                ''', (f'%{brand}%', f'%{brand}%'))

                for contractor, title, country in cursor.fetchall():
                    self.results['suspicious_patterns'].append({
                        'type': 'Chinese Brand Mentioned',
                        'brand': brand,
                        'contractor': contractor[:100] if contractor else 'N/A',
                        'title': title[:150] if title else 'N/A',
                        'country': country
                    })

    def analyze_telecom_contracts(self, cursor):
        """Special analysis for telecommunications contracts"""

        logger.info("Analyzing telecommunications contracts...")

        # Telecom CPV codes
        cursor.execute('''
            SELECT contractor_name, contract_title, country,
                   contract_description, cpv_codes
            FROM ted_china_contracts
            WHERE (cpv_codes LIKE '32%' OR cpv_codes LIKE '64%'
                   OR contract_title LIKE '%telecom%'
                   OR contract_title LIKE '%5G%'
                   OR contract_title LIKE '%network%')
            AND contractor_name IS NOT NULL
            LIMIT 200
        ''')

        telecom_risks = []
        for contractor, title, country, description, cpv in cursor.fetchall():
            risk_score = 0
            risk_factors = []

            # Check for risk indicators
            text = f"{contractor or ''} {title or ''} {description or ''}".lower()

            if '5g' in text:
                risk_score += 3
                risk_factors.append('5G technology')
            if 'network' in text:
                risk_score += 1
                risk_factors.append('Network infrastructure')
            if 'core' in text:
                risk_score += 2
                risk_factors.append('Core network')
            if any(word in text for word in ['radio', 'antenna', 'base station']):
                risk_score += 2
                risk_factors.append('Radio access network')

            if risk_score >= 3:
                telecom_risks.append({
                    'contractor': contractor[:100] if contractor else 'N/A',
                    'title': title[:150] if title else 'N/A',
                    'country': country,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'note': 'High probability of Chinese equipment in telecom infrastructure'
                })

        # Add top risks to results
        telecom_risks.sort(key=lambda x: x['risk_score'], reverse=True)
        self.results['technology_dependencies'].extend(telecom_risks[:10])

    def analyze_infrastructure(self, cursor):
        """Analyze infrastructure projects for Chinese involvement"""

        logger.info("Analyzing infrastructure projects...")

        # Infrastructure keywords
        infrastructure_keywords = [
            'port', 'railway', 'highway', 'bridge', 'tunnel',
            'airport', 'power plant', 'solar farm', 'wind farm',
            'smart city', 'metro', 'subway'
        ]

        for keyword in infrastructure_keywords:
            cursor.execute('''
                SELECT contractor_name, contract_title, country, contract_value_eur
                FROM ted_china_contracts
                WHERE (contract_title LIKE ? OR contract_description LIKE ?)
                AND contract_value_eur > 1000000
                LIMIT 20
            ''', (f'%{keyword}%', f'%{keyword}%'))

            for contractor, title, country, value in cursor.fetchall():
                if contractor:
                    self.results['suspicious_patterns'].append({
                        'type': 'Major Infrastructure Project',
                        'keyword': keyword,
                        'contractor': contractor[:100],
                        'title': title[:150] if title else 'N/A',
                        'country': country,
                        'value': value,
                        'note': f'Belt and Road Initiative potential - {keyword} project'
                    })

    def generate_report(self):
        """Generate analysis report"""

        # Calculate statistics
        total_indicators = (
            len(self.results['technology_dependencies']) +
            len(self.results['joint_ventures']) +
            len(self.results['supply_chain_risks']) +
            len(self.results['suspicious_patterns'])
        )

        print("\n" + "="*80)
        print("EU-CHINA INDIRECT RELATIONSHIP ANALYSIS")
        print("="*80)
        print(f"\nAnalysis Timestamp: {self.results['timestamp']}")
        print(f"Total Indirect Indicators Found: {total_indicators}")

        # Technology dependencies
        if self.results['technology_dependencies']:
            print("\n" + "="*50)
            print("TECHNOLOGY DEPENDENCIES")
            print("="*50)

            # Group by technology type
            tech_groups = {}
            for dep in self.results['technology_dependencies']:
                tech = dep.get('technology', 'Unknown')
                if tech not in tech_groups:
                    tech_groups[tech] = []
                tech_groups[tech].append(dep)

            for tech, deps in tech_groups.items():
                print(f"\n{tech}: {len(deps)} instances")
                for dep in deps[:2]:  # Show first 2
                    print(f"  - {dep.get('contractor', 'N/A')} ({dep.get('country', 'N/A')})")

        # Supply chain risks
        if self.results['supply_chain_risks']:
            print("\n" + "="*50)
            print("SUPPLY CHAIN RISKS")
            print("="*50)

            for risk in self.results['supply_chain_risks'][:5]:
                print(f"\n{risk['sector']}:")
                print(f"  Total Contracts: {risk['total_contracts']}")
                print(f"  Risk: {risk['risk']}")

        # Joint ventures
        if self.results['joint_ventures']:
            print("\n" + "="*50)
            print(f"JOINT VENTURES/CONSORTIUMS: {len(self.results['joint_ventures'])}")
            print("="*50)
            print("Potential for hidden Chinese partnerships")

            for jv in self.results['joint_ventures'][:3]:
                print(f"\n  - {jv['contractor']}")
                print(f"    Country: {jv['country']}, Type: {jv['type']}")

        # Recommendations
        self.results['recommendations'] = [
            "1. Implement mandatory disclosure of all subcontractors and suppliers",
            "2. Require country-of-origin labeling for all technology components",
            "3. Conduct supply chain audits for critical infrastructure projects",
            "4. Establish a registry of Chinese technology dependencies",
            "5. Develop alternative non-Chinese suppliers for critical sectors",
            "6. Monitor joint ventures and consortiums for hidden Chinese partners"
        ]

        print("\n" + "="*50)
        print("RECOMMENDATIONS")
        print("="*50)
        for rec in self.results['recommendations']:
            print(f"{rec}")

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/eu_china_indirect_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n\nFull report saved to: {report_path}")

        return self.results


def main():
    """Main execution"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    analyzer = IndirectChineseAnalyzer(db_path)
    results = analyzer.analyze_indirect_relationships()
    analyzer.generate_report()

    return results


if __name__ == "__main__":
    main()
