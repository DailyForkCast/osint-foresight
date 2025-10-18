#!/usr/bin/env python3
"""
SEC EDGAR SQL Database Query Tool
Provides useful queries for the SEC EDGAR data in SQL database
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

class SECEdgarSQLQuery:
    """Query SEC EDGAR data from SQL database"""

    def __init__(self, db_path: str = "database/osint_master.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

    def database_summary(self):
        """Get database summary statistics"""
        print("\n" + "="*60)
        print("SEC EDGAR DATABASE SUMMARY")
        print("="*60)

        # Total companies
        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_companies")
        total = self.cursor.fetchone()[0]
        print(f"Total Companies: {total}")

        # Chinese companies
        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_companies WHERE is_chinese = 1")
        chinese = self.cursor.fetchone()[0]
        print(f"Chinese Companies: {chinese}")

        # Total filings
        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_filings")
        filings = self.cursor.fetchone()[0]
        print(f"Total Filings: {filings}")

        # Total addresses
        self.cursor.execute("SELECT COUNT(*) FROM sec_edgar_addresses")
        addresses = self.cursor.fetchone()[0]
        print(f"Total Addresses: {addresses}")

        print("="*60)

    def top_chinese_companies(self, limit: int = 20):
        """Get top Chinese companies by filing count"""
        print(f"\nTop {limit} Chinese Companies:")
        print("-" * 60)

        query = """
        SELECT
            c.ticker,
            c.name,
            c.sic_description,
            c.state_of_incorporation,
            COUNT(DISTINCT f.id) as filing_count
        FROM sec_edgar_companies c
        LEFT JOIN sec_edgar_filings f ON c.cik = f.cik
        WHERE c.is_chinese = 1 AND c.ticker IS NOT NULL
        GROUP BY c.cik
        ORDER BY filing_count DESC
        LIMIT ?
        """

        results = self.cursor.execute(query, (limit,)).fetchall()

        for ticker, name, sic_desc, state, count in results:
            print(f"{ticker:6} | {name[:30]:30} | {sic_desc[:25] if sic_desc else 'N/A':25} | State: {state:3} | Filings: {count}")

    def chinese_companies_by_industry(self):
        """Group Chinese companies by industry"""
        print("\nChinese Companies by Industry:")
        print("-" * 60)

        query = """
        SELECT
            COALESCE(sic_description, 'Unclassified') as industry,
            COUNT(*) as count
        FROM sec_edgar_companies
        WHERE is_chinese = 1
        GROUP BY sic_description
        ORDER BY count DESC
        LIMIT 15
        """

        results = self.cursor.execute(query).fetchall()

        for industry, count in results:
            print(f"{industry[:40]:40} | {count:4} companies")

    def chinese_companies_by_state(self):
        """Group Chinese companies by state of incorporation"""
        print("\nChinese Companies by State of Incorporation:")
        print("-" * 60)

        query = """
        SELECT
            state_of_incorporation,
            CASE state_of_incorporation
                WHEN 'E9' THEN 'Cayman Islands'
                WHEN 'D0' THEN 'Bermuda'
                WHEN 'F4' THEN 'British Virgin Islands'
                WHEN 'L3' THEN 'Hong Kong'
                WHEN 'K3' THEN 'Hong Kong'
                ELSE state_of_incorporation
            END as location,
            COUNT(*) as count
        FROM sec_edgar_companies
        WHERE is_chinese = 1
        GROUP BY state_of_incorporation
        ORDER BY count DESC
        LIMIT 10
        """

        results = self.cursor.execute(query).fetchall()

        for state, location, count in results:
            print(f"{state:3} | {location:25} | {count:4} companies")

    def search_chinese_companies(self, keyword: str):
        """Search for Chinese companies by keyword"""
        print(f"\nSearching for Chinese companies with '{keyword}':")
        print("-" * 60)

        query = """
        SELECT ticker, cik, name, sic_description
        FROM sec_edgar_companies
        WHERE is_chinese = 1
        AND (name LIKE ? OR ticker LIKE ? OR sic_description LIKE ?)
        ORDER BY name
        LIMIT 20
        """

        search_term = f"%{keyword}%"
        results = self.cursor.execute(query, (search_term, search_term, search_term)).fetchall()

        for ticker, cik, name, sic_desc in results:
            print(f"{ticker:6} | {cik} | {name[:35]:35} | {sic_desc[:25] if sic_desc else 'N/A'}")

        if not results:
            print("No matching companies found.")

    def recent_filings(self, days: int = 30):
        """Get recent filings from Chinese companies"""
        print(f"\nRecent Filings from Chinese Companies (last {days} days):")
        print("-" * 60)

        query = """
        SELECT
            c.ticker,
            c.name,
            f.form,
            f.filing_date,
            f.accession_number
        FROM sec_edgar_filings f
        JOIN sec_edgar_companies c ON f.cik = c.cik
        WHERE c.is_chinese = 1
        AND f.filing_date >= date('now', '-' || ? || ' days')
        ORDER BY f.filing_date DESC
        LIMIT 20
        """

        results = self.cursor.execute(query, (days,)).fetchall()

        for ticker, name, form, date, accession in results:
            print(f"{date} | {ticker:6} | {form:6} | {name[:30]:30} | {accession}")

        if not results:
            print("No recent filings found.")

    def export_chinese_companies_csv(self, filename: str = "chinese_companies.csv"):
        """Export Chinese companies to CSV"""
        query = """
        SELECT
            cik,
            ticker,
            name,
            sic,
            sic_description,
            state_of_incorporation,
            phone,
            website,
            detection_reasons
        FROM sec_edgar_companies
        WHERE is_chinese = 1
        ORDER BY name
        """

        df = pd.read_sql_query(query, self.conn)
        df.to_csv(filename, index=False)
        print(f"\nExported {len(df)} Chinese companies to {filename}")

    def detection_statistics(self):
        """Show detection method statistics"""
        print("\nChinese Company Detection Statistics:")
        print("-" * 60)

        query = """
        SELECT
            indicator_type,
            COUNT(DISTINCT cik) as company_count,
            COUNT(*) as total_indicators
        FROM sec_edgar_chinese_indicators
        GROUP BY indicator_type
        ORDER BY company_count DESC
        """

        results = self.cursor.execute(query).fetchall()

        for indicator, companies, total in results:
            print(f"{indicator:15} | {companies:4} companies | {total:4} total matches")

    def run_all_reports(self):
        """Run all standard reports"""
        self.database_summary()
        self.top_chinese_companies()
        self.chinese_companies_by_industry()
        self.chinese_companies_by_state()
        self.detection_statistics()

    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main execution function with menu"""
    query_tool = SECEdgarSQLQuery()

    print("\n" + "="*60)
    print("SEC EDGAR SQL DATABASE QUERY TOOL")
    print("="*60)

    while True:
        print("\nOptions:")
        print("1. Database Summary")
        print("2. Top Chinese Companies")
        print("3. Companies by Industry")
        print("4. Companies by State of Incorporation")
        print("5. Search Companies")
        print("6. Recent Filings")
        print("7. Detection Statistics")
        print("8. Export Chinese Companies to CSV")
        print("9. Run All Reports")
        print("0. Exit")

        choice = input("\nSelect option (0-9): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            query_tool.database_summary()
        elif choice == "2":
            query_tool.top_chinese_companies()
        elif choice == "3":
            query_tool.chinese_companies_by_industry()
        elif choice == "4":
            query_tool.chinese_companies_by_state()
        elif choice == "5":
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                query_tool.search_chinese_companies(keyword)
        elif choice == "6":
            days = input("Enter number of days (default 30): ").strip()
            days = int(days) if days.isdigit() else 30
            query_tool.recent_filings(days)
        elif choice == "7":
            query_tool.detection_statistics()
        elif choice == "8":
            query_tool.export_chinese_companies_csv()
        elif choice == "9":
            query_tool.run_all_reports()
        else:
            print("Invalid option. Please try again.")

    query_tool.close()
    print("\nGoodbye!")

if __name__ == "__main__":
    # Run in non-interactive mode for immediate results
    query_tool = SECEdgarSQLQuery()
    query_tool.run_all_reports()
    query_tool.close()
