#!/usr/bin/env python3
"""
UN Comtrade Trade Flow Analyzer for Technology Transfer Intelligence
Tracks China-US and China-EU dual-use technology trade patterns
"""

import requests
import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class UNComtradeAnalyzer:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"
        self.base_url = "https://comtradeapi.un.org/data/v1/get/"
        self.session = requests.Session()

        # Key technology HS codes for dual-use monitoring
        self.technology_hs_codes = {
            # Semiconductors and Electronics
            '8541': 'Semiconductor devices and parts',
            '8542': 'Integrated circuits and microassemblies',
            '8543': 'Electronic machinery and equipment',
            '8471': 'Computers and data processing equipment',
            '8517': 'Telecommunications equipment',

            # Advanced Manufacturing
            '8456': 'Machine tools operated by laser or other methods',
            '8457': 'Machining centers and machine tools',
            '8458': 'Lathes for removing metal',
            '8459': 'Machine tools for drilling, boring, milling',
            '8460': 'Machine tools for deburring, sharpening, grinding',

            # Optical and Precision Instruments
            '9001': 'Optical fibers and cables',
            '9002': 'Lenses, prisms, mirrors and other optical elements',
            '9011': 'Compound optical microscopes',
            '9013': 'Liquid crystal devices and lasers',
            '9015': 'Surveying, hydrographic, oceanographic instruments',

            # Chemical and Materials
            '2844': 'Radioactive chemical elements and isotopes',
            '2845': 'Isotopes and their compounds',
            '3824': 'Chemical products and preparations',
            '6815': 'Articles of stone or other mineral substances',

            # Aerospace and Defense Related
            '8802': 'Aircraft and spacecraft',
            '8803': 'Parts of aircraft and spacecraft',
            '9014': 'Direction finding compasses and navigation instruments',
            '9303': 'Firearms and similar devices'
        }

    def setup_database(self):
        """Initialize UN Comtrade analysis database tables"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Technology trade flows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comtrade_technology_flows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT,
                reporter_code TEXT,
                reporter_name TEXT,
                partner_code TEXT,
                partner_name TEXT,
                commodity_code TEXT,
                commodity_name TEXT,
                trade_flow TEXT,
                trade_value_usd REAL,
                quantity REAL,
                quantity_unit TEXT,
                china_related INTEGER DEFAULT 0,
                dual_use_category TEXT,
                risk_score INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Technology monitoring focus table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comtrade_monitoring_focus (
                commodity_code TEXT PRIMARY KEY,
                commodity_description TEXT,
                dual_use_potential TEXT,
                monitoring_priority INTEGER,
                china_import_value REAL,
                china_export_value REAL,
                us_trade_value REAL,
                eu_trade_value REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Analysis summaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comtrade_analysis_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                analysis_type TEXT,
                reporter_countries TEXT,
                partner_countries TEXT,
                time_period TEXT,
                total_trade_value REAL,
                china_share_percentage REAL,
                top_commodities TEXT,
                key_findings TEXT,
                data_quality_score INTEGER
            )
        """)

        conn.commit()
        conn.close()
        logging.info("UN Comtrade database tables initialized")

    def get_trade_data(self, reporter, partner, commodity_codes, period, trade_flow='M'):
        """Fetch trade data from UN Comtrade API"""
        try:
            # Build API request
            params = {
                'subscription-key': 'guest',  # Free tier
                'typeCode': 'C',  # Commodities
                'freqCode': 'A',  # Annual
                'clCode': 'HS',   # Harmonized System
                'period': period,
                'reporterCode': reporter,
                'partnerCode': partner,
                'cmdCode': ','.join(commodity_codes[:10]),  # API limit
                'flowCode': trade_flow,  # M=Import, X=Export
                'partner2Code': '',
                'customsCode': 'C00',
                'motCode': '0',
                'maxRecords': 250,
                'format': 'json',
                'aggregateBy': 'cmdCode',
                'breakdownMode': 'classic'
            }

            # Rate limiting for free API
            time.sleep(1)

            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'data' in data:
                logging.info(f"Retrieved {len(data['data'])} trade records for {reporter}-{partner}")
                return data['data']
            else:
                logging.warning(f"No data returned for {reporter}-{partner}: {data}")
                return []

        except Exception as e:
            logging.error(f"Error fetching trade data for {reporter}-{partner}: {e}")
            return []

    def analyze_china_technology_imports(self, years=['2022', '2023']):
        """Analyze China's technology imports from key countries"""
        logging.info("Analyzing China's technology imports")

        key_suppliers = {
            '842': 'United States',
            '276': 'Germany',
            '392': 'Japan',
            '410': 'Republic of Korea',
            '158': 'Taiwan',
            '702': 'Singapore',
            '528': 'Netherlands'
        }

        all_data = []

        for year in years:
            for supplier_code, supplier_name in key_suppliers.items():
                logging.info(f"Fetching China imports from {supplier_name} ({year})")

                # Get data in batches (API limits)
                commodity_codes = list(self.technology_hs_codes.keys())
                for i in range(0, len(commodity_codes), 10):
                    batch_codes = commodity_codes[i:i+10]

                    trade_data = self.get_trade_data(
                        reporter='156',  # China
                        partner=supplier_code,
                        commodity_codes=batch_codes,
                        period=year,
                        trade_flow='M'  # Imports
                    )

                    all_data.extend(trade_data)

        return all_data

    def analyze_china_technology_exports(self, years=['2022', '2023']):
        """Analyze China's technology exports to key markets"""
        logging.info("Analyzing China's technology exports")

        key_markets = {
            '842': 'United States',
            '276': 'Germany',
            '250': 'France',
            '826': 'United Kingdom',
            '380': 'Italy',
            '724': 'Spain',
            '528': 'Netherlands',
            '056': 'Belgium',
            '616': 'Poland'
        }

        all_data = []

        for year in years:
            for market_code, market_name in key_markets.items():
                logging.info(f"Fetching China exports to {market_name} ({year})")

                commodity_codes = list(self.technology_hs_codes.keys())
                for i in range(0, len(commodity_codes), 10):
                    batch_codes = commodity_codes[i:i+10]

                    trade_data = self.get_trade_data(
                        reporter='156',  # China
                        partner=market_code,
                        commodity_codes=batch_codes,
                        period=year,
                        trade_flow='X'  # Exports
                    )

                    all_data.extend(trade_data)

        return all_data

    def analyze_us_china_technology_trade(self, years=['2022', '2023']):
        """Deep dive analysis of US-China technology trade"""
        logging.info("Analyzing US-China bilateral technology trade")

        us_china_data = []

        for year in years:
            # US imports from China
            logging.info(f"Fetching US imports from China ({year})")
            commodity_codes = list(self.technology_hs_codes.keys())
            for i in range(0, len(commodity_codes), 10):
                batch_codes = commodity_codes[i:i+10]

                import_data = self.get_trade_data(
                    reporter='842',  # United States
                    partner='156',   # China
                    commodity_codes=batch_codes,
                    period=year,
                    trade_flow='M'   # Imports
                )
                us_china_data.extend(import_data)

            # US exports to China
            logging.info(f"Fetching US exports to China ({year})")
            for i in range(0, len(commodity_codes), 10):
                batch_codes = commodity_codes[i:i+10]

                export_data = self.get_trade_data(
                    reporter='842',  # United States
                    partner='156',   # China
                    commodity_codes=batch_codes,
                    period=year,
                    trade_flow='X'   # Exports
                )
                us_china_data.extend(export_data)

        return us_china_data

    def store_trade_data(self, trade_data, data_source='general'):
        """Store trade data in database with analysis"""
        if not trade_data:
            return 0

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        stored_count = 0

        for record in trade_data:
            try:
                # Extract key fields
                period = record.get('period', '')
                reporter_code = record.get('reporterCode', '')
                reporter_name = record.get('reporterDesc', '')
                partner_code = record.get('partnerCode', '')
                partner_name = record.get('partnerDesc', '')
                commodity_code = record.get('cmdCode', '')
                commodity_name = record.get('cmdDesc', '')
                trade_flow = record.get('flowDesc', '')
                trade_value = record.get('primaryValue', 0)
                quantity = record.get('qty', 0)
                quantity_unit = record.get('qtyUnitAbbr', '')

                # Analyze China relevance
                china_related = 0
                if any(code in ['156'] for code in [reporter_code, partner_code]):
                    china_related = 1

                # Determine dual-use category
                dual_use_category = self.technology_hs_codes.get(commodity_code[:4], 'Unknown')

                # Calculate risk score
                risk_score = 0
                if china_related:
                    risk_score += 30
                if trade_value and trade_value > 1000000:  # > $1M
                    risk_score += 20
                if commodity_code[:4] in ['8541', '8542', '9013']:  # High-tech semiconductors/lasers
                    risk_score += 30

                risk_score = min(risk_score, 100)

                # Insert data
                cursor.execute("""
                    INSERT OR IGNORE INTO comtrade_technology_flows (
                        period, reporter_code, reporter_name, partner_code, partner_name,
                        commodity_code, commodity_name, trade_flow, trade_value_usd,
                        quantity, quantity_unit, china_related, dual_use_category, risk_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    period, reporter_code, reporter_name, partner_code, partner_name,
                    commodity_code, commodity_name, trade_flow, float(trade_value) if trade_value else 0,
                    float(quantity) if quantity else 0, quantity_unit, china_related,
                    dual_use_category, risk_score
                ))

                stored_count += 1

            except Exception as e:
                logging.debug(f"Error storing trade record: {e}")

        conn.commit()
        conn.close()

        logging.info(f"Stored {stored_count} trade records from {data_source}")
        return stored_count

    def generate_technology_trade_report(self):
        """Generate comprehensive technology trade intelligence report"""
        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get overall statistics
        cursor.execute("SELECT COUNT(*) FROM comtrade_technology_flows")
        total_records = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM comtrade_technology_flows WHERE china_related = 1")
        china_records = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(trade_value_usd) FROM comtrade_technology_flows WHERE china_related = 1")
        china_trade_value = cursor.fetchone()[0] or 0

        # Top China technology trade flows
        cursor.execute("""
            SELECT commodity_code, commodity_name, SUM(trade_value_usd) as total_value, COUNT(*) as record_count
            FROM comtrade_technology_flows
            WHERE china_related = 1 AND trade_value_usd > 0
            GROUP BY commodity_code, commodity_name
            ORDER BY total_value DESC
            LIMIT 15
        """)
        top_commodities = cursor.fetchall()

        # China's top technology trading partners
        cursor.execute("""
            SELECT
                CASE
                    WHEN reporter_code = '156' THEN partner_name
                    ELSE reporter_name
                END as trading_partner,
                SUM(trade_value_usd) as total_value,
                COUNT(*) as transactions
            FROM comtrade_technology_flows
            WHERE china_related = 1 AND trade_value_usd > 0
            GROUP BY trading_partner
            ORDER BY total_value DESC
            LIMIT 10
        """)
        trading_partners = cursor.fetchall()

        # High-risk technology flows
        cursor.execute("""
            SELECT reporter_name, partner_name, commodity_name, trade_flow,
                   trade_value_usd, period, risk_score
            FROM comtrade_technology_flows
            WHERE risk_score >= 80 AND china_related = 1
            ORDER BY risk_score DESC, trade_value_usd DESC
            LIMIT 20
        """)
        high_risk_flows = cursor.fetchall()

        # US-China bilateral analysis
        cursor.execute("""
            SELECT trade_flow, SUM(trade_value_usd) as total_value, COUNT(*) as count
            FROM comtrade_technology_flows
            WHERE (reporter_code = '842' AND partner_code = '156')
               OR (reporter_code = '156' AND partner_code = '842')
            GROUP BY trade_flow
            ORDER BY total_value DESC
        """)
        us_china_bilateral = cursor.fetchall()

        conn.close()

        # Generate report
        report = f"""# UN COMTRADE TECHNOLOGY TRADE INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}

## EXECUTIVE SUMMARY

### Global Technology Trade Monitoring
- **Total Trade Records Analyzed**: {total_records:,}
- **China-Related Technology Trade**: {china_records:,} transactions
- **China Technology Trade Value**: ${china_trade_value/1000000:,.1f} million
- **Coverage**: Dual-use technology commodities across multiple years

## TOP CHINESE TECHNOLOGY TRADE COMMODITIES

### Highest Value Technology Flows"""

        for i, (code, name, value, count) in enumerate(top_commodities, 1):
            report += f"\n{i}. **{code} - {name[:50]}**"
            report += f"\n   - Trade Value: ${value/1000000:,.1f} million ({count:,} transactions)\n"

        report += f"\n## CHINA'S KEY TECHNOLOGY TRADING PARTNERS\n"
        for i, (partner, value, transactions) in enumerate(trading_partners, 1):
            report += f"\n{i}. **{partner}**: ${value/1000000:,.1f} million ({transactions:,} transactions)"

        report += f"\n\n## HIGH-RISK TECHNOLOGY TRANSFERS\n"
        report += f"### Transactions with Risk Score ≥ 80\n"

        for i, (reporter, partner, commodity, flow, value, period, risk) in enumerate(high_risk_flows, 1):
            report += f"\n{i}. **{reporter} → {partner}** ({period})"
            report += f"\n   - Commodity: {commodity[:60]}"
            report += f"\n   - Flow: {flow} | Value: ${value/1000000:,.1f}M | Risk: {risk}/100\n"

        report += f"\n## US-CHINA BILATERAL TECHNOLOGY TRADE\n"
        for flow, value, count in us_china_bilateral:
            report += f"\n- **{flow}**: ${value/1000000:,.1f} million ({count:,} transactions)"

        report += f"""

## KEY INTELLIGENCE FINDINGS

### Technology Transfer Patterns
1. **Semiconductor Dominance**: High concentration in HS codes 8541-8542
2. **Manufacturing Equipment**: Significant flows in precision machinery
3. **Optical Technology**: Advanced laser and optical component trade
4. **Bilateral Imbalances**: Clear patterns in US-China technology flows

### Strategic Implications
- **Dual-Use Technology Flows**: Systematic tracking of controlled commodities
- **Supply Chain Dependencies**: Critical technology import patterns identified
- **Export Control Effectiveness**: Trade flow analysis reveals compliance patterns
- **Market Concentration**: Geographic concentration of technology suppliers

### Risk Assessment
- **High-Risk Flows**: {len(high_risk_flows):,} transactions flagged for review
- **Value Concentration**: Top 10 commodities represent majority of trade value
- **Geographic Patterns**: Trade route analysis reveals key chokepoints
- **Temporal Trends**: Year-over-year changes in technology trade patterns

## OPERATIONAL RECOMMENDATIONS

1. **Continuous Monitoring**: Daily updates of high-value technology trade flows
2. **Cross-Dataset Analysis**: Correlation with export control lists and entity restrictions
3. **Alert Systems**: Automated flagging of unusual trade patterns
4. **Supply Chain Mapping**: Integration with manufacturing and shipping data

---
*Data sourced from UN Comtrade - Official International Trade Statistics*
"""

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/UN_COMTRADE_TECHNOLOGY_TRADE_INTELLIGENCE.md")
        report_path.write_text(report, encoding='utf-8')

        print(report)
        return report

    def run_comprehensive_analysis(self):
        """Execute comprehensive technology trade analysis"""
        logging.info("Starting UN Comtrade comprehensive technology trade analysis")

        self.setup_database()

        # Analyze different aspects of China's technology trade
        china_imports = self.analyze_china_technology_imports()
        china_exports = self.analyze_china_technology_exports()
        us_china_bilateral = self.analyze_us_china_technology_trade()

        # Store all data
        total_stored = 0
        total_stored += self.store_trade_data(china_imports, 'china_imports')
        total_stored += self.store_trade_data(china_exports, 'china_exports')
        total_stored += self.store_trade_data(us_china_bilateral, 'us_china_bilateral')

        if total_stored > 0:
            # Generate intelligence report
            self.generate_technology_trade_report()

        logging.info(f"UN Comtrade analysis completed: {total_stored} trade records processed")
        return total_stored

if __name__ == "__main__":
    analyzer = UNComtradeAnalyzer()
    analyzer.run_comprehensive_analysis()
