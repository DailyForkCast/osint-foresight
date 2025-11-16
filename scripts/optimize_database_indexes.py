#!/usr/bin/env python3
"""
Database Index Optimization Script
Analyzes current indexes and adds optimizations for Phase 1, 2, 5 bottlenecks
"""

import sqlite3
import re
from pathlib import Path
import time
from datetime import datetime
import json

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table, column, or index name).
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


class DatabaseIndexOptimizer:
    """Optimizes database indexes for query performance"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.optimization_log = []

    def analyze_current_indexes(self):
        """Analyze existing indexes in the database"""
        print("="*80)
        print("ANALYZING CURRENT DATABASE INDEXES")
        print("="*80)

        # Get all tables
        self.cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in self.cur.fetchall()]

        index_summary = {}

        for table in tables:
            # SECURITY: Validate table name before use in SQL
            safe_table = validate_sql_identifier(table)

            # Get indexes for this table
            self.cur.execute(f"PRAGMA index_list('{safe_table}')")
            indexes = self.cur.fetchall()

            if indexes:
                index_summary[table] = []
                print(f"\n{table}:")
                for idx in indexes:
                    idx_name = idx[1]
                    # SECURITY: Validate index name before use in SQL
                    safe_idx_name = validate_sql_identifier(idx_name)
                    # Get index details
                    self.cur.execute(f"PRAGMA index_info('{safe_idx_name}')")
                    columns = [col[2] for col in self.cur.fetchall()]
                    index_summary[table].append({
                        'name': idx_name,
                        'columns': columns
                    })
                    print(f"  - {idx_name}: {', '.join(columns)}")

        return index_summary

    def add_phase1_indexes(self):
        """Add indexes to optimize Phase 1 (Data Validation) queries"""
        print("\n" + "="*80)
        print("ADDING PHASE 1 OPTIMIZATION INDEXES")
        print("="*80)

        indexes_to_add = [
            ('ted_china_contracts_fixed', 'country_iso', 'idx_ted_country'),
            ('sec_edgar_chinese_investors', 'country', 'idx_sec_edgar_country'),
            ('openaire_china_collaborations', 'country', 'idx_openaire_country'),
            ('cordis_chinese_orgs', 'country', 'idx_cordis_country'),
        ]

        for table, column, index_name in indexes_to_add:
            self._add_index_safe(table, column, index_name, 'Phase 1')

    def add_phase2_indexes(self):
        """Add indexes to optimize Phase 2 (Technology Landscape) queries"""
        print("\n" + "="*80)
        print("ADDING PHASE 2 OPTIMIZATION INDEXES")
        print("="*80)

        indexes_to_add = [
            ('uspto_patent_chinese_2011_2025', 'assignee_country', 'idx_uspto_country'),
            ('uspto_patent_chinese_2011_2025', 'cpc_section', 'idx_uspto_cpc_section'),
            ('epo_patents', 'applicant_country', 'idx_epo_country'),
            ('openalex_works', 'country', 'idx_openalex_works_country'),
        ]

        for table, column, index_name in indexes_to_add:
            self._add_index_safe(table, column, index_name, 'Phase 2')

    def add_phase5_indexes(self):
        """Add indexes to optimize Phase 5 (Funding Flows) queries"""
        print("\n" + "="*80)
        print("ADDING PHASE 5 OPTIMIZATION INDEXES")
        print("="*80)

        indexes_to_add = [
            ('cordis_projects', 'project_id', 'idx_cordis_project_id'),
            ('cordis_organizations', 'country', 'idx_cordis_org_country'),
            ('usaspending_contracts', 'recipient_country', 'idx_usaspending_country'),
        ]

        for table, column, index_name in indexes_to_add:
            self._add_index_safe(table, column, index_name, 'Phase 5')

    def _add_index_safe(self, table, column, index_name, phase):
        """Safely add an index with error handling"""
        # SECURITY: Validate identifiers before use in SQL
        safe_table = validate_sql_identifier(table)
        safe_column = validate_sql_identifier(column)
        safe_index_name = validate_sql_identifier(index_name)

        # Check if table exists
        self.cur.execute(f"""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table,))

        if not self.cur.fetchone():
            print(f"  [SKIP] {table}.{column}: Table doesn't exist")
            self.optimization_log.append({
                'phase': phase,
                'table': table,
                'column': column,
                'index_name': index_name,
                'status': 'skipped',
                'reason': 'table_not_found'
            })
            return

        # Check if column exists
        self.cur.execute(f"PRAGMA table_info('{safe_table}')")
        columns = [row[1] for row in self.cur.fetchall()]
        if column not in columns:
            print(f"  [SKIP] {table}.{column}: Column doesn't exist")
            self.optimization_log.append({
                'phase': phase,
                'table': table,
                'column': column,
                'index_name': index_name,
                'status': 'skipped',
                'reason': 'column_not_found'
            })
            return

        # Check if index already exists
        self.cur.execute(f"PRAGMA index_list('{safe_table}')")
        existing_indexes = [row[1] for row in self.cur.fetchall()]

        if index_name in existing_indexes:
            print(f"  [EXISTS] {table}.{column}: Index already exists")
            self.optimization_log.append({
                'phase': phase,
                'table': table,
                'column': column,
                'index_name': index_name,
                'status': 'already_exists'
            })
            return

        # Create index
        start_time = time.time()
        try:
            print(f"  + Creating index on {table}.{column}...", end=" ")
            self.cur.execute(f"""
                CREATE INDEX IF NOT EXISTS {safe_index_name}
                ON {safe_table}({safe_column})
            """)
            self.conn.commit()
            elapsed = time.time() - start_time
            print(f"[OK] ({elapsed:.2f}s)")

            self.optimization_log.append({
                'phase': phase,
                'table': table,
                'column': column,
                'index_name': index_name,
                'status': 'created',
                'time_seconds': round(elapsed, 2)
            })

        except Exception as e:
            print(f"[ERROR] {e}")
            self.optimization_log.append({
                'phase': phase,
                'table': table,
                'column': column,
                'index_name': index_name,
                'status': 'error',
                'error': str(e)
            })

    def analyze_table_sizes(self):
        """Analyze table sizes to understand impact"""
        print("\n" + "="*80)
        print("TABLE SIZE ANALYSIS")
        print("="*80)

        tables_of_interest = [
            'ted_china_contracts_fixed',
            'sec_edgar_chinese_investors',
            'uspto_patent_chinese_2011_2025',
            'cordis_projects',
            'cordis_organizations',
            'openaire_china_collaborations',
            'openalex_works'
        ]

        for table in tables_of_interest:
            try:
                # SECURITY: Validate table name before use in SQL
                safe_table = validate_sql_identifier(table)
                self.cur.execute(f"SELECT COUNT(*) FROM {safe_table}")
                count = self.cur.fetchone()[0]
                print(f"  {table}: {count:,} rows")
            except:
                print(f"  {table}: Table not found")

    def generate_report(self):
        """Generate optimization report"""
        print("\n" + "="*80)
        print("OPTIMIZATION SUMMARY")
        print("="*80)

        created = [log for log in self.optimization_log if log['status'] == 'created']
        skipped = [log for log in self.optimization_log if log['status'] == 'skipped']
        already_exists = [log for log in self.optimization_log if log['status'] == 'already_exists']
        errors = [log for log in self.optimization_log if log['status'] == 'error']

        print(f"\nIndexes created: {len(created)}")
        print(f"Indexes already existed: {len(already_exists)}")
        print(f"Indexes skipped: {len(skipped)}")
        print(f"Errors: {len(errors)}")

        if created:
            total_time = sum(log.get('time_seconds', 0) for log in created)
            print(f"\nTotal index creation time: {total_time:.2f}s")

        if errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"  - {error['table']}.{error['column']}: {error['error']}")

        # Save detailed log
        report_path = Path("analysis/database_optimization_log.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            'timestamp': datetime.now().isoformat(),
            'database': str(self.db_path),
            'summary': {
                'created': len(created),
                'already_exists': len(already_exists),
                'skipped': len(skipped),
                'errors': len(errors)
            },
            'details': self.optimization_log
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed log saved to: {report_path}")

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return

    print("="*80)
    print("DATABASE INDEX OPTIMIZATION")
    print("="*80)
    print(f"Database: {db_path}")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80)

    optimizer = DatabaseIndexOptimizer(db_path)

    # Step 1: Analyze current state
    optimizer.analyze_current_indexes()
    optimizer.analyze_table_sizes()

    # Step 2: Add optimizations
    optimizer.add_phase1_indexes()
    optimizer.add_phase2_indexes()
    optimizer.add_phase5_indexes()

    # Step 3: Generate report
    optimizer.generate_report()

    # Cleanup
    optimizer.close()

    print("\n" + "="*80)
    print("OPTIMIZATION COMPLETE")
    print("="*80)
    print("\nNext step: Run performance profiler to measure impact")
    print("Command: python scripts/performance_profiler.py")
    print("="*80)


if __name__ == "__main__":
    main()
