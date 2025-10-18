#!/usr/bin/env python3
"""
EU-China Comprehensive Procurement Relationship Analyzer
Analyzes all EU countries' procurement relationships with Chinese entities
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import sys
sys.path.append('C:/Projects/OSINT - Foresight/scripts')
from hybrid_chinese_detector import HybridChineseDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EUChinaProcurementAnalyzer:
    """Comprehensive analyzer for EU-China procurement relationships"""

    # EU member states (27 countries)
    EU_COUNTRIES = [
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
        'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL',
        'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'
    ]

    # Critical technology sectors
    CRITICAL_SECTORS = {
        '32': 'Radio, television, communication',
        '30': 'Office machinery and computers',
        '31': 'Electrical machinery',
        '33': 'Medical and precision instruments',
        '34': 'Motor vehicles',
        '35': 'Other transport equipment',
        '45': 'Construction work',
        '48': 'Software and information systems',
        '50': 'Repair and maintenance',
        '64': 'Telecommunications',
        '71': 'Architectural and engineering',
        '72': 'IT services',
        '73': 'Research and development',
        '79': 'Security services'
    }

    # Chinese company patterns to search for
    CHINESE_COMPANIES = [
        'Huawei', 'ZTE', 'Hikvision', 'Dahua', 'DJI', 'Lenovo',
        'Alibaba', 'Tencent', 'Baidu', 'ByteDance', 'Xiaomi',
        'BYD', 'CRRC', 'SMIC', 'China Mobile', 'China Telecom',
        'China Unicom', 'Sinopec', 'PetroChina', 'State Grid',
        'COSCO', 'China National', 'China State', 'CNOOC',
        'AVIC', 'COMAC', 'NORINCO', 'CETC', 'CASIC'
    ]

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.detector = HybridChineseDetector()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'eu_countries_analyzed': 0,
            'total_contracts': 0,
            'chinese_contracts': 0,
            'by_country': {},
            'by_sector': {},
            'by_year': {},
            'critical_findings': [],
            'technology_transfers': [],
            'high_risk_contracts': []
        }

    def analyze_all_eu_countries(self):
        """Main analysis function for all EU countries"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        logger.info("Starting comprehensive EU-China procurement analysis")

        # Get total contracts
        cur.execute('SELECT COUNT(*) FROM ted_china_contracts')
        self.results['total_contracts'] = cur.fetchone()[0]

        # Analyze each EU country
        for country_code in self.EU_COUNTRIES:
            logger.info(f"Analyzing {country_code}...")
            self.analyze_country(cur, country_code)
            self.results['eu_countries_analyzed'] += 1

        # Analyze Chinese contractors across all EU
        self.analyze_chinese_contractors(cur)

        # Analyze critical sectors
        self.analyze_critical_sectors(cur)

        # Analyze temporal patterns
        self.analyze_temporal_patterns(cur)

        # Identify high-risk contracts
        self.identify_high_risk_contracts(cur)

        conn.close()

        return self.results

    def analyze_country(self, cursor, country_code: str):
        """Analyze a specific EU country's relationship with China"""

        country_results = {
            'total_contracts': 0,
            'chinese_contracts': 0,
            'chinese_contractors': [],
            'sectors_exposed': {},
            'total_value_to_china': 0,
            'critical_dependencies': []
        }

        # Get all contracts for this country
        cursor.execute('''
            SELECT COUNT(*) FROM ted_china_contracts
            WHERE country = ? OR contracting_authority_country = ?
        ''', (country_code, country_code))
        country_results['total_contracts'] = cursor.fetchone()[0]

        # Find Chinese contractors in this country
        cursor.execute('''
            SELECT contractor_name, contractor_country,
                   contract_title, cpv_codes, contract_value_eur,
                   contracting_authority, contract_id
            FROM ted_china_contracts
            WHERE (country = ? OR contracting_authority_country = ?)
            AND contractor_name IS NOT NULL
        ''', (country_code, country_code))

        for row in cursor.fetchall():
            contractor, contractor_country, title, cpv, value, authority, contract_id = row

            # Check if contractor is Chinese
            result = self.detector.detect_chinese_entity(
                contractor, contractor_country, authority, title or ""
            )

            if result.confidence_score > 0.5:  # Medium confidence or higher
                country_results['chinese_contracts'] += 1

                # Track the contractor
                contractor_info = {
                    'name': contractor[:100] if contractor else 'Unknown',
                    'confidence': result.confidence_score,
                    'evidence': result.recommendation,
                    'contract_id': contract_id,
                    'cpv_code': cpv,
                    'value': value
                }
                country_results['chinese_contractors'].append(contractor_info)

                # Track sector exposure
                if cpv:
                    sector = cpv[:2] if len(cpv) >= 2 else 'Unknown'
                    if sector not in country_results['sectors_exposed']:
                        country_results['sectors_exposed'][sector] = 0
                    country_results['sectors_exposed'][sector] += 1

                # Track value
                if value:
                    try:
                        country_results['total_value_to_china'] += float(value)
                    except:
                        pass

                # Check for critical dependencies
                if cpv and any(cpv.startswith(critical) for critical in self.CRITICAL_SECTORS):
                    country_results['critical_dependencies'].append({
                        'contractor': contractor[:100],
                        'sector': self.CRITICAL_SECTORS.get(cpv[:2], 'Critical sector'),
                        'authority': authority[:100] if authority else 'Unknown'
                    })

        self.results['by_country'][country_code] = country_results
        self.results['chinese_contracts'] += country_results['chinese_contracts']

    def analyze_chinese_contractors(self, cursor):
        """Identify and analyze all Chinese contractors across EU"""

        logger.info("Analyzing Chinese contractors across all EU...")

        # Search for known Chinese companies
        for company in self.CHINESE_COMPANIES:
            cursor.execute('''
                SELECT contractor_name, COUNT(*) as contract_count,
                       GROUP_CONCAT(DISTINCT country) as countries,
                       SUM(CAST(contract_value_eur AS REAL)) as total_value
                FROM ted_china_contracts
                WHERE contractor_name LIKE ?
                GROUP BY contractor_name
                ORDER BY contract_count DESC
            ''', (f'%{company}%',))

            for row in cursor.fetchall():
                if row[0]:  # If contractor name exists
                    self.results['critical_findings'].append({
                        'type': 'Known Chinese Company',
                        'company': row[0][:100],
                        'pattern_matched': company,
                        'contracts': row[1],
                        'countries': row[2],
                        'total_value': row[3] if row[3] else 0
                    })

        # Find contractors with Chinese country codes
        cursor.execute('''
            SELECT contractor_name, contractor_country,
                   COUNT(*) as contract_count,
                   GROUP_CONCAT(DISTINCT country) as eu_countries
            FROM ted_china_contracts
            WHERE contractor_country IN ('CN', 'CHN', 'HK', 'MO')
            AND contractor_name IS NOT NULL
            GROUP BY contractor_name, contractor_country
            ORDER BY contract_count DESC
        ''')

        for row in cursor.fetchall():
            self.results['critical_findings'].append({
                'type': 'Chinese Country Code',
                'company': row[0][:100],
                'country_code': row[1],
                'contracts': row[2],
                'eu_countries': row[3]
            })

    def analyze_critical_sectors(self, cursor):
        """Analyze Chinese involvement in critical sectors"""

        logger.info("Analyzing critical sector exposure...")

        for cpv_prefix, sector_name in self.CRITICAL_SECTORS.items():
            cursor.execute('''
                SELECT COUNT(*) as total_contracts,
                       COUNT(DISTINCT contractor_name) as unique_contractors
                FROM ted_china_contracts
                WHERE cpv_codes LIKE ?
            ''', (f'{cpv_prefix}%',))

            total, unique = cursor.fetchone()

            # Now check for Chinese involvement
            chinese_count = 0
            chinese_contractors = []

            cursor.execute('''
                SELECT DISTINCT contractor_name, contractor_country, contracting_authority
                FROM ted_china_contracts
                WHERE cpv_codes LIKE ?
                AND contractor_name IS NOT NULL
            ''', (f'{cpv_prefix}%',))

            for contractor, country, authority in cursor.fetchall():
                result = self.detector.detect_chinese_entity(contractor, country, authority)
                if result.confidence_score > 0.5:
                    chinese_count += 1
                    chinese_contractors.append(contractor[:100])

            if chinese_count > 0:
                self.results['by_sector'][sector_name] = {
                    'cpv_prefix': cpv_prefix,
                    'total_contracts': total,
                    'chinese_contracts': chinese_count,
                    'chinese_contractors': chinese_contractors[:5],  # Top 5
                    'exposure_rate': chinese_count / total if total > 0 else 0
                }

    def analyze_temporal_patterns(self, cursor):
        """Analyze Chinese procurement patterns over time"""

        logger.info("Analyzing temporal patterns...")

        cursor.execute('''
            SELECT SUBSTR(publication_date, 1, 4) as year, COUNT(*) as count
            FROM ted_china_contracts
            WHERE publication_date IS NOT NULL
            GROUP BY year
            ORDER BY year
        ''')

        for year, total in cursor.fetchall():
            if year and year.isdigit():
                # Count Chinese contracts for this year
                cursor.execute('''
                    SELECT COUNT(*) FROM ted_china_contracts
                    WHERE SUBSTR(publication_date, 1, 4) = ?
                    AND refined_china_linked = 1
                ''', (year,))

                chinese_count = cursor.fetchone()[0]

                self.results['by_year'][year] = {
                    'total_contracts': total,
                    'chinese_contracts': chinese_count,
                    'penetration_rate': chinese_count / total if total > 0 else 0
                }

    def identify_high_risk_contracts(self, cursor):
        """Identify high-risk contracts with Chinese entities"""

        logger.info("Identifying high-risk contracts...")

        # Focus on critical sectors with Chinese involvement
        critical_cpv = "','".join(self.CRITICAL_SECTORS.keys())

        cursor.execute(f'''
            SELECT contractor_name, contractor_country, contract_title,
                   cpv_codes, contract_value_eur, contracting_authority,
                   country, contract_id
            FROM ted_china_contracts
            WHERE contractor_name IS NOT NULL
            AND (
                SUBSTR(cpv_codes, 1, 2) IN ('{critical_cpv}')
                OR contract_title LIKE '%5G%'
                OR contract_title LIKE '%AI%'
                OR contract_title LIKE '%artificial intelligence%'
                OR contract_title LIKE '%surveillance%'
                OR contract_title LIKE '%security%'
                OR contract_title LIKE '%defense%'
                OR contract_title LIKE '%military%'
                OR contract_title LIKE '%critical infrastructure%'
            )
            LIMIT 10000
        ''')

        for row in cursor.fetchall():
            contractor, contractor_country, title, cpv, value, authority, eu_country, contract_id = row

            # Check Chinese connection
            result = self.detector.detect_chinese_entity(
                contractor, contractor_country, authority, title or ""
            )

            if result.confidence_score > 0.7:  # High confidence
                risk_level = self.assess_risk_level(title, cpv, value)

                if risk_level >= 7:  # High risk threshold
                    self.results['high_risk_contracts'].append({
                        'contractor': contractor[:100],
                        'title': title[:200] if title else 'N/A',
                        'sector': self.CRITICAL_SECTORS.get(cpv[:2], 'Unknown') if cpv else 'Unknown',
                        'eu_country': eu_country,
                        'authority': authority[:100] if authority else 'Unknown',
                        'value': value,
                        'risk_score': risk_level,
                        'chinese_confidence': result.confidence_score,
                        'contract_id': contract_id
                    })

    def assess_risk_level(self, title: str, cpv: str, value) -> int:
        """Assess risk level of a contract (0-10 scale)"""
        risk_score = 5  # Base score

        # Check for critical keywords
        critical_keywords = [
            ('5G', 3), ('AI', 2), ('surveillance', 3), ('security', 2),
            ('defense', 3), ('military', 3), ('infrastructure', 2),
            ('telecom', 2), ('network', 2), ('data', 1)
        ]

        if title:
            title_lower = title.lower()
            for keyword, weight in critical_keywords:
                if keyword.lower() in title_lower:
                    risk_score += weight

        # Check CPV code criticality
        if cpv and cpv[:2] in ['32', '33', '64', '72', '79']:  # Most critical sectors
            risk_score += 2

        # Check value
        try:
            if value and float(value) > 1000000:  # Over €1M
                risk_score += 1
            if value and float(value) > 10000000:  # Over €10M
                risk_score += 1
        except:
            pass

        return min(risk_score, 10)  # Cap at 10

    def generate_report(self):
        """Generate comprehensive analysis report"""

        report_path = Path("C:/Projects/OSINT - Foresight/analysis/eu_china_procurement_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Generate summary statistics
        print("\n" + "="*80)
        print("EU-CHINA PROCUREMENT RELATIONSHIP ANALYSIS")
        print("="*80)
        print(f"\nAnalysis Timestamp: {self.results['timestamp']}")
        print(f"EU Countries Analyzed: {self.results['eu_countries_analyzed']}")
        print(f"Total Contracts: {self.results['total_contracts']:,}")
        print(f"Chinese Contracts Identified: {self.results['chinese_contracts']}")

        if self.results['chinese_contracts'] > 0:
            penetration = (self.results['chinese_contracts'] / self.results['total_contracts']) * 100
            print(f"Chinese Penetration Rate: {penetration:.4f}%")

        # Country rankings
        print("\n" + "="*50)
        print("TOP 5 EU COUNTRIES BY CHINESE CONTRACT EXPOSURE")
        print("="*50)

        sorted_countries = sorted(
            self.results['by_country'].items(),
            key=lambda x: x[1]['chinese_contracts'],
            reverse=True
        )[:5]

        for country, data in sorted_countries:
            if data['chinese_contracts'] > 0:
                print(f"\n{country}:")
                print(f"  Chinese Contracts: {data['chinese_contracts']}")
                print(f"  Total Value to China: €{data['total_value_to_china']:,.2f}")
                print(f"  Critical Dependencies: {len(data['critical_dependencies'])}")

        # Sector analysis
        print("\n" + "="*50)
        print("CRITICAL SECTORS WITH CHINESE INVOLVEMENT")
        print("="*50)

        for sector, data in self.results['by_sector'].items():
            print(f"\n{sector}:")
            print(f"  Chinese Contracts: {data['chinese_contracts']}")
            print(f"  Exposure Rate: {data['exposure_rate']:.2%}")
            if data['chinese_contractors']:
                print(f"  Key Contractors: {', '.join(data['chinese_contractors'][:3])}")

        # High risk contracts
        print("\n" + "="*50)
        print(f"HIGH-RISK CONTRACTS IDENTIFIED: {len(self.results['high_risk_contracts'])}")
        print("="*50)

        for contract in self.results['high_risk_contracts'][:5]:
            print(f"\nRisk Score: {contract['risk_score']}/10")
            print(f"  Contractor: {contract['contractor']}")
            print(f"  Title: {contract['title']}")
            print(f"  Country: {contract['eu_country']}")
            print(f"  Sector: {contract['sector']}")
            print(f"  Value: €{contract['value']:,}" if contract['value'] else "  Value: N/A")

        print(f"\n\nFull report saved to: {report_path}")

        return self.results


def main():
    """Main execution function"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    analyzer = EUChinaProcurementAnalyzer(db_path)
    results = analyzer.analyze_all_eu_countries()
    analyzer.generate_report()

    # Save key findings summary
    summary = {
        'executive_summary': {
            'total_eu_contracts': results['total_contracts'],
            'chinese_involvement': results['chinese_contracts'],
            'penetration_rate': (results['chinese_contracts'] / results['total_contracts'] * 100) if results['total_contracts'] > 0 else 0,
            'high_risk_contracts': len(results['high_risk_contracts']),
            'critical_findings': len(results['critical_findings']),
            'most_exposed_countries': list(sorted(
                results['by_country'].items(),
                key=lambda x: x[1]['chinese_contracts'],
                reverse=True
            ))[:3]
        }
    }

    with open("C:/Projects/OSINT - Foresight/analysis/eu_china_executive_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    return results


if __name__ == "__main__":
    main()
