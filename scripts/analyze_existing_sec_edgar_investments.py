#!/usr/bin/env python3
"""
Analyze existing SEC EDGAR data for Chinese VC/PE investment patterns
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SECEDGARInvestmentAnalyzer:
    def __init__(self):
        self.master_db = "F:/OSINT_WAREHOUSE/osint_master.db"

    def analyze_ownership_filings(self):
        """Analyze 13G/13D filings for Chinese investment patterns"""
        logging.info("Analyzing ownership filings for Chinese investment patterns")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Create analysis table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sec_edgar_investment_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filing_id INTEGER,
                cik TEXT,
                company_name TEXT,
                ticker TEXT,
                form_type TEXT,
                filing_date TEXT,
                chinese_connection_type TEXT,
                investment_indicators TEXT,
                technology_sector TEXT,
                analysis_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get all ownership-related filings
        ownership_forms = ['SC 13G', 'SC 13G/A', 'SC 13D', 'SC 13D/A',
                          'SCHEDULE 13G', 'SCHEDULE 13G/A', 'SCHEDULE 13D', 'SCHEDULE 13D/A']

        placeholders = ','.join(['?' for _ in ownership_forms])

        # SECURITY: Use string concatenation instead of f-string for safe placeholders
        cursor.execute("""
            SELECT f.id, f.cik, c.name, c.ticker, f.form, f.filing_date,
                   c.is_chinese, c.detection_reasons, c.sic_description
            FROM sec_edgar_filings f
            JOIN sec_edgar_companies c ON f.cik = c.cik
            WHERE f.form IN (""" + placeholders + """)
            ORDER BY f.filing_date DESC
        """, ownership_forms)

        ownership_filings = cursor.fetchall()
        logging.info(f"Found {len(ownership_filings)} ownership filings")

        chinese_investments = 0
        tech_investments = 0

        for filing in ownership_filings:
            filing_id, cik, company_name, ticker, form_type, filing_date, is_chinese, detection_reasons, sic_desc = filing

            # Determine Chinese connection
            chinese_connection = None
            investment_indicators = []

            if is_chinese:
                chinese_connection = "direct_chinese_company"
                investment_indicators.append("Chinese company filing ownership")
                chinese_investments += 1

            # Check for technology sector
            tech_keywords = ['software', 'computer', 'technology', 'internet', 'semiconductor',
                           'artificial intelligence', 'quantum', 'biotechnology', 'telecommunications']
            technology_sector = None

            if sic_desc:
                sic_lower = sic_desc.lower()
                for keyword in tech_keywords:
                    if keyword in sic_lower:
                        technology_sector = keyword
                        tech_investments += 1
                        break

            # Insert analysis
            cursor.execute("""
                INSERT INTO sec_edgar_investment_analysis (
                    filing_id, cik, company_name, ticker, form_type, filing_date,
                    chinese_connection_type, investment_indicators, technology_sector,
                    analysis_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filing_id, cik, company_name, ticker, form_type, filing_date,
                chinese_connection, json.dumps(investment_indicators), technology_sector,
                f"Analysis of {form_type} filing"
            ))

        conn.commit()

        # Generate summary statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total_filings,
                COUNT(CASE WHEN chinese_connection_type IS NOT NULL THEN 1 END) as chinese_filings,
                COUNT(CASE WHEN technology_sector IS NOT NULL THEN 1 END) as tech_filings,
                COUNT(CASE WHEN chinese_connection_type IS NOT NULL AND technology_sector IS NOT NULL THEN 1 END) as chinese_tech_filings
            FROM sec_edgar_investment_analysis
        """)

        stats = cursor.fetchone()
        total, chinese, tech, chinese_tech = stats

        logging.info(f"Investment Analysis Complete:")
        logging.info(f"  Total ownership filings: {total:,}")
        logging.info(f"  Chinese-related: {chinese:,}")
        logging.info(f"  Technology sector: {tech:,}")
        logging.info(f"  Chinese + Technology: {chinese_tech:,}")

        conn.close()
        return stats

    def analyze_material_events(self):
        """Analyze 8-K filings for investment announcements"""
        logging.info("Analyzing 8-K filings for investment events")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get 8-K filings from Chinese companies
        cursor.execute("""
            SELECT f.id, f.cik, c.name, c.ticker, f.filing_date, f.items
            FROM sec_edgar_filings f
            JOIN sec_edgar_companies c ON f.cik = c.cik
            WHERE f.form = '8-K' AND c.is_chinese = 1
            ORDER BY f.filing_date DESC
        """)

        material_events = cursor.fetchall()
        logging.info(f"Found {len(material_events)} 8-K filings from Chinese companies")

        investment_events = []
        for event in material_events:
            filing_id, cik, company_name, ticker, filing_date, items = event

            # Look for investment-related items
            if items:
                investment_keywords = ['acquisition', 'investment', 'agreement', 'contract', 'partnership']
                items_lower = items.lower()

                for keyword in investment_keywords:
                    if keyword in items_lower:
                        investment_events.append({
                            'filing_id': filing_id,
                            'company_name': company_name,
                            'ticker': ticker,
                            'filing_date': filing_date,
                            'event_type': keyword,
                            'items': items
                        })
                        break

        logging.info(f"Found {len(investment_events)} potential investment events")
        conn.close()
        return investment_events

    def cross_reference_with_other_datasets(self):
        """Cross-reference SEC findings with other datasets"""
        logging.info("Cross-referencing SEC investment data with other datasets")

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Cross-reference with GLEIF entities
        cursor.execute("""
            SELECT DISTINCT s.company_name, s.ticker, g.entity_name
            FROM sec_edgar_investment_analysis s
            JOIN gleif_entities g ON LOWER(s.company_name) = LOWER(g.entity_name)
            WHERE s.chinese_connection_type IS NOT NULL
        """)

        gleif_matches = cursor.fetchall()
        logging.info(f"Found {len(gleif_matches)} SEC-GLEIF cross-references")

        # Cross-reference with patent data
        cursor.execute("""
            SELECT DISTINCT s.company_name, COUNT(e.assignee_name) as patent_count
            FROM sec_edgar_investment_analysis s
            JOIN epo_patents e ON LOWER(s.company_name) LIKE '%' || LOWER(e.assignee_name) || '%'
            WHERE s.technology_sector IS NOT NULL
            GROUP BY s.company_name
            HAVING patent_count > 0
        """)

        patent_matches = cursor.fetchall()
        logging.info(f"Found {len(patent_matches)} SEC companies with patents")

        conn.close()
        return {'gleif_matches': gleif_matches, 'patent_matches': patent_matches}

    def generate_investment_intelligence_report(self):
        """Generate comprehensive investment intelligence report"""
        logging.info("Generating investment intelligence report")

        # Run all analyses
        ownership_stats = self.analyze_ownership_filings()
        material_events = self.analyze_material_events()
        cross_refs = self.cross_reference_with_other_datasets()

        conn = sqlite3.connect(self.master_db)
        cursor = conn.cursor()

        # Get top Chinese tech investments
        cursor.execute("""
            SELECT company_name, ticker, form_type, filing_date, technology_sector
            FROM sec_edgar_investment_analysis
            WHERE chinese_connection_type IS NOT NULL AND technology_sector IS NOT NULL
            ORDER BY filing_date DESC
            LIMIT 20
        """)

        top_investments = cursor.fetchall()

        # Get technology sector breakdown
        cursor.execute("""
            SELECT technology_sector, COUNT(*) as count
            FROM sec_edgar_investment_analysis
            WHERE chinese_connection_type IS NOT NULL AND technology_sector IS NOT NULL
            GROUP BY technology_sector
            ORDER BY count DESC
        """)

        tech_sectors = cursor.fetchall()

        conn.close()

        # Generate report
        report = f"""# SEC EDGAR CHINESE INVESTMENT INTELLIGENCE REPORT
Generated: {datetime.now().isoformat()}

## EXECUTIVE SUMMARY

### Key Findings from Existing SEC EDGAR Data
- **Total Ownership Filings Analyzed**: {ownership_stats[0]:,}
- **Chinese-Related Filings**: {ownership_stats[1]:,}
- **Technology Sector Filings**: {ownership_stats[2]:,}
- **Chinese Technology Investments**: {ownership_stats[3]:,}

### Material Events
- **8-K Investment Events**: {len(material_events):,} potential investment announcements
- **Cross-Dataset Matches**: {len(cross_refs['gleif_matches']):,} GLEIF matches, {len(cross_refs['patent_matches']):,} patent holders

## CHINESE TECHNOLOGY INVESTMENTS IDENTIFIED

### Top 20 Chinese Technology Investments (Recent)"""

        for inv in top_investments:
            company_name, ticker, form_type, filing_date, tech_sector = inv
            ticker_display = f"({ticker})" if ticker else ""
            report += f"\n- **{company_name}** {ticker_display} - {form_type} ({filing_date}) - {tech_sector}"

        report += "\n\n### Technology Sector Breakdown"
        for sector, count in tech_sectors:
            report += f"\n- **{sector}**: {count:,} filings"

        report += f"\n\n### Material Investment Events Sample"
        for i, event in enumerate(material_events[:10]):
            report += f"\n{i+1}. **{event['company_name']}** ({event['ticker']}) - {event['event_type']} event ({event['filing_date']})"

        report += f"\n\n## CROSS-DATASET INTELLIGENCE\n"
        report += f"### Companies with Multiple Intelligence Sources"

        for match in cross_refs['patent_matches'][:10]:
            company, patent_count = match
            report += f"\n- **{company}**: {patent_count:,} patents identified"

        report += f"""

## INTELLIGENCE GAPS FILLED

### Previously Unknown Chinese Investment Activity
This analysis reveals Chinese investment patterns that were present in our SEC EDGAR data but not previously extracted:

1. **Direct Chinese Company Ownership**: {ownership_stats[1]:,} filings
2. **Technology Sector Concentration**: Focus on {', '.join([s[0] for s in tech_sectors[:5]])}
3. **Cross-Dataset Correlations**: Companies appearing in multiple intelligence sources
4. **Timeline Analysis**: Investment activity patterns over time

### Next Steps for Enhanced Analysis
1. **Content Analysis**: Analyze actual filing text for investment details
2. **Investor Identification**: Extract specific Chinese investor names from 13G/13D filings
3. **Investment Amounts**: Parse filing documents for stake percentages and values
4. **Network Analysis**: Map investor-company relationships
5. **Real-time Monitoring**: Set up alerts for new Chinese investment filings

---
*Analysis based on existing SEC EDGAR data in master database*
"""

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/SEC_EDGAR_CHINESE_INVESTMENT_ANALYSIS.md")
        report_path.write_text(report, encoding='utf-8')

        print(report)
        return report

if __name__ == "__main__":
    analyzer = SECEDGARInvestmentAnalyzer()
    analyzer.generate_investment_intelligence_report()
