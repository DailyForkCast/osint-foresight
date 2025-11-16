#!/usr/bin/env python3
import re

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
    Only allows alphanumeric characters and underscores.
    Prevents SQL injection from dynamic SQL construction.
    """
    if not identifier:
        raise ValueError("Identifier cannot be empty")

    # Check for valid characters only (alphanumeric + underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', identifier):
        raise ValueError(f"Invalid identifier: {identifier}. Contains illegal characters.")

    # Check length (SQLite limit is 1024, we use 100 for safety)
    if len(identifier) > 100:
        raise ValueError(f"Identifier too long: {identifier}")

    # Blacklist dangerous SQL keywords
    dangerous_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                         'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';', '/*', '*/'}
    if identifier.upper() in dangerous_keywords:
        raise ValueError(f"Identifier contains SQL keyword: {identifier}")

    return identifier


"""
Analyze USPTO Patent Database for PRC Involvement
2.8M assignees, 12.7M case files - identify Chinese patents and technology transfer
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = "F:/OSINT_WAREHOUSE/osint_master.db"
OUTPUT_DIR = Path("C:/Projects/OSINT - Foresight/analysis/patents")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load PRC SOE database
with open('C:/Projects/OSINT - Foresight/data/prc_soe_database.json') as f:
    soe_db = json.load(f)

# Load Chinese locations
with open('C:/Projects/OSINT - Foresight/data/chinese_locations.json') as f:
    locations = json.load(f)

class USPTOPRCAnalyzer:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()

        # Build SOE list
        self.soe_names = set()
        for category, companies in soe_db['central_soes'].items():
            self.soe_names.update([c.lower() for c in companies])

        # Build location list
        self.chinese_locations = []
        for key in ['tier1_cities', 'provincial_capitals', 'provinces']:
            if key in locations:
                self.chinese_locations.extend([loc.lower() for loc in locations[key]])

        print("="*80)
        print("USPTO PRC PATENT ANALYSIS")
        print("="*80)

    def analyze_assignee_table(self):
        """Analyze uspto_assignee table for Chinese assignees"""
        print("\n" + "=" * 80)
        print("ANALYZING 2.8M USPTO ASSIGNEES")
        print("=" * 80)

        # Get table schema
        self.cur.execute("PRAGMA table_info(uspto_assignee)")
        columns = [row[1] for row in self.cur.fetchall()]
        print(f"\nColumns: {columns}")

        # Sample data
        print("\nSample assignees:")
        self.cur.execute("SELECT * FROM uspto_assignee LIMIT 5")
        for row in self.cur.fetchall():
            print(f"  {row}")

        # Search for Chinese assignees
        print("\nSearching for Chinese assignees...")

        chinese_assignees = []

        # Search by country codes
        for col in columns:
            if 'country' in col.lower():
                print(f"\nSearching {col} column for CN/HK...")
                # SECURITY: Validate column name before use in SQL
                safe_col = validate_sql_identifier(col)
                self.cur.execute(f"SELECT COUNT(*) FROM uspto_assignee WHERE LOWER({safe_col}) IN ('cn', 'hk', 'china', 'hong kong')")
                count = self.cur.fetchone()[0]
                print(f"  Found {count:,} Chinese assignees in {col}")

                if count > 0:
                    # Get samples
                    # SECURITY: Validate column name before use in SQL
                    self.cur.execute(f"SELECT * FROM uspto_assignee WHERE LOWER({safe_col}) IN ('cn', 'hk') LIMIT 10")
                    for row in self.cur.fetchall():
                        chinese_assignees.append(dict(zip(columns, row)))

        print(f"\nTotal Chinese assignees found: {len(chinese_assignees)}")

        # Search by organization name
        if chinese_assignees:
            print("\nSample Chinese assignees:")
            for assignee in chinese_assignees[:10]:
                print(f"  {assignee}")

        return chinese_assignees

    def analyze_case_file_table(self):
        """Analyze uspto_case_file table for Chinese patents"""
        print("\n" + "=" * 80)
        print("ANALYZING 12.7M USPTO CASE FILES")
        print("=" * 80)

        # Get table schema
        self.cur.execute("PRAGMA table_info(uspto_case_file)")
        columns = [row[1] for row in self.cur.fetchall()]
        print(f"\nColumns ({len(columns)} total): {columns[:15]}...")

        # Sample data
        print("\nSample case files:")
        self.cur.execute("SELECT * FROM uspto_case_file LIMIT 3")
        for row in self.cur.fetchall():
            # Print first 10 fields only
            print(f"  {row[:10]}...")

        return {'columns': columns}

    def search_soe_patents(self):
        """Search for SOE-related patents"""
        print("\n" + "=" * 80)
        print("SEARCHING FOR PRC SOE PATENTS")
        print("=" * 80)

        soe_patents = defaultdict(list)

        # Search assignee table for SOEs
        self.cur.execute("PRAGMA table_info(uspto_assignee)")
        columns = [row[1] for row in self.cur.fetchall()]

        name_cols = [c for c in columns if 'name' in c.lower() or 'organization' in c.lower()]

        if name_cols:
            name_col = name_cols[0]
            print(f"\nSearching {name_col} for SOEs...")

            for soe in ['huawei', 'zte', 'lenovo', 'nuctech', 'hikvision', 'dahua']:
                # SECURITY: Validate column name and use parameterized query for value
                safe_name_col = validate_sql_identifier(name_col)
                self.cur.execute(f"SELECT * FROM uspto_assignee WHERE LOWER({safe_name_col}) LIKE ? LIMIT 100", (f'%{soe}%',))
                results = self.cur.fetchall()

                if results:
                    print(f"  {soe.upper()}: {len(results)} assignees")
                    soe_patents[soe] = [dict(zip(columns, row)) for row in results]

        return dict(soe_patents)

    def generate_report(self, all_data):
        """Generate final patent analysis report"""
        print("\n" + "=" * 80)
        print("GENERATING PATENT REPORT")
        print("=" * 80)

        report = {
            'generated': datetime.now().isoformat(),
            'total_assignees': 2_800_000,
            'total_case_files': 12_691_942,
            'chinese_assignees': all_data.get('assignees', []),
            'soe_patents': all_data.get('soe_patents', {}),
            'case_file_schema': all_data.get('case_file', {})
        }

        report_file = OUTPUT_DIR / "uspto_prc_patent_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to: {report_file}")

        return report

    def run(self):
        """Run complete USPTO PRC analysis"""
        all_data = {}

        all_data['assignees'] = self.analyze_assignee_table()
        all_data['case_file'] = self.analyze_case_file_table()
        all_data['soe_patents'] = self.search_soe_patents()

        report = self.generate_report(all_data)

        self.conn.close()

        print("\n" + "=" * 80)
        print("USPTO ANALYSIS COMPLETE")
        print("=" * 80)

        return report

if __name__ == '__main__':
    analyzer = USPTOPRCAnalyzer()
    analyzer.run()
