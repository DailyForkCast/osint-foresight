#!/usr/bin/env python3
"""
Phase 4: Database Integrity Audit
Systematic checks for data quality issues
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class DatabaseIntegrityAuditor:
    """Check database for integrity issues"""

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.findings = []

    def check_table_integrity(self, table_name):
        """Run integrity checks on a single table"""
        issues = {
            'table': table_name,
            'checks': []
        }

        # Get table info
        self.cur.execute(f"PRAGMA table_info({table_name})")
        columns = self.cur.fetchall()
        column_names = [col[1] for col in columns]

        # Get record count
        self.cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        record_count = self.cur.fetchone()[0]

        if record_count == 0:
            issues['checks'].append({
                'type': 'empty_table',
                'severity': 'INFO',
                'message': f'Table is empty (0 records)'
            })
            return issues

        # Check 1: NULL values in all columns
        for col_name in column_names:
            try:
                self.cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
                null_count = self.cur.fetchone()[0]
                if null_count > 0:
                    null_pct = (null_count / record_count) * 100
                    if null_pct > 50:
                        issues['checks'].append({
                            'type': 'high_null_rate',
                            'severity': 'MEDIUM',
                            'column': col_name,
                            'message': f'{null_pct:.1f}% NULL values in {col_name}'
                        })
            except:
                pass

        # Check 2: Duplicate records (if table has id column)
        if 'id' in column_names:
            try:
                self.cur.execute(f"""
                    SELECT COUNT(*) FROM (
                        SELECT id, COUNT(*) as cnt
                        FROM {table_name}
                        GROUP BY id
                        HAVING cnt > 1
                    )
                """)
                dup_count = self.cur.fetchone()[0]
                if dup_count > 0:
                    issues['checks'].append({
                        'type': 'duplicate_ids',
                        'severity': 'HIGH',
                        'message': f'{dup_count} duplicate IDs found'
                    })
            except:
                pass

        # Check 3: Future dates (if date columns exist)
        date_columns = [col for col in column_names if 'date' in col.lower() or 'time' in col.lower()]
        for date_col in date_columns:
            try:
                # Check for dates in future
                self.cur.execute(f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE {date_col} > datetime('now')
                """)
                future_count = self.cur.fetchone()[0]
                if future_count > 0:
                    issues['checks'].append({
                        'type': 'future_dates',
                        'severity': 'MEDIUM',
                        'column': date_col,
                        'message': f'{future_count} records with future dates in {date_col}'
                    })
            except:
                pass

        # Check 4: Invalid dates (year < 1900 or > 2100)
        for date_col in date_columns:
            try:
                self.cur.execute(f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE {date_col} < '1900-01-01' OR {date_col} > '2100-01-01'
                """)
                invalid_count = self.cur.fetchone()[0]
                if invalid_count > 0:
                    issues['checks'].append({
                        'type': 'invalid_dates',
                        'severity': 'MEDIUM',
                        'column': date_col,
                        'message': f'{invalid_count} records with invalid dates in {date_col}'
                    })
            except:
                pass

        # Check 5: Empty strings vs NULL
        text_columns = [col for col in column_names if any(x in col.lower() for x in ['name', 'title', 'description', 'text'])]
        for text_col in text_columns[:5]:  # Limit to first 5 text columns
            try:
                self.cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {text_col} = ''")
                empty_count = self.cur.fetchone()[0]
                if empty_count > 0:
                    empty_pct = (empty_count / record_count) * 100
                    if empty_pct > 10:
                        issues['checks'].append({
                            'type': 'empty_strings',
                            'severity': 'LOW',
                            'column': text_col,
                            'message': f'{empty_pct:.1f}% empty strings in {text_col} (should be NULL?)'
                        })
            except:
                pass

        return issues

    def audit_sample(self, tables_to_check):
        """Audit a sample of tables"""
        results = []

        print("="*80)
        print("PHASE 4: DATABASE INTEGRITY AUDIT")
        print("="*80)
        print(f"\nDatabase: {self.db_path}")
        print(f"Tables to check: {len(tables_to_check)}")
        print()

        for i, table_name in enumerate(tables_to_check, 1):
            print(f"[{i}/{len(tables_to_check)}] Checking {table_name}...")
            issues = self.check_table_integrity(table_name)

            if issues['checks']:
                print(f"  Found {len(issues['checks'])} issues")
                results.append(issues)
            else:
                print(f"  ✓ No issues found")

        return results

    def close(self):
        self.conn.close()

def main():
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return

    auditor = DatabaseIntegrityAuditor(db_path)

    # Get all tables
    auditor.cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [row[0] for row in auditor.cur.fetchall()]

    # Strategy: Check key tables from each data source
    priority_tables = [
        # USAspending
        'usaspending_china_374_v2',
        'usaspending_contracts',

        # TED
        'ted_contracts_production',
        'ted_china_contracts_fixed',

        # USPTO
        'uspto_cpc_classifications',
        'uspto_patents_chinese',

        # OpenAlex
        'openalex_works',
        'openalex_work_authors',

        # ArXiv
        'arxiv_papers',
        'arxiv_authors',

        # GDELT
        'gdelt_events',
        'gdelt_mentions',

        # GLEIF
        'gleif_entities',

        # European
        'european_institutions',

        # Bilateral
        'bilateral_countries',
        'bilateral_events',

        # Chinese entities
        'chinese_entities',
        'china_entities',
    ]

    # Filter to tables that actually exist
    tables_to_check = [t for t in priority_tables if t in all_tables]

    print(f"\nPriority tables found: {len(tables_to_check)}/{len(priority_tables)}")
    print(f"Missing tables: {set(priority_tables) - set(tables_to_check)}")
    print()

    # Run audit
    results = auditor.audit_sample(tables_to_check)

    # Save results
    output_file = Path("PHASE4_DATABASE_INTEGRITY_RESULTS.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Generate summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    total_issues = sum(len(r['checks']) for r in results)
    by_severity = defaultdict(int)
    by_type = defaultdict(int)

    for result in results:
        for check in result['checks']:
            by_severity[check['severity']] += 1
            by_type[check['type']] += 1

    print(f"\nTables checked: {len(tables_to_check)}")
    print(f"Tables with issues: {len(results)}")
    print(f"Total issues found: {total_issues}")
    print()
    print("By Severity:")
    for sev in ['HIGH', 'MEDIUM', 'LOW', 'INFO']:
        if by_severity[sev] > 0:
            print(f"  {sev:10} {by_severity[sev]:3} issues")
    print()
    print("By Type:")
    for issue_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type:20} {count:3} occurrences")

    print(f"\nDetailed results saved to: {output_file}")

    auditor.close()

if __name__ == "__main__":
    main()
