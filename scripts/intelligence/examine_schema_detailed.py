#!/usr/bin/env python3
"""
Examine database schema in detail for intelligence analysis adaptation
"""

import sqlite3
import json
from collections import defaultdict

def examine_schema():
    """Examine database schema to understand available tables and columns"""

    db_path = 'F:/OSINT_WAREHOUSE/osint_master.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("="*80)
        print("DATABASE SCHEMA EXAMINATION FOR INTELLIGENCE ANALYSIS")
        print("="*80)

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\nTotal tables: {len(tables)}")

        # Focus on tables relevant for intelligence analysis
        relevant_keywords = [
            'document', 'entity', 'report', 'mcf', 'thinktank',
            'arxiv', 'patent', 'ted', 'usaspending'
        ]

        relevant_tables = [t for t in tables
                          if any(keyword in t.lower() for keyword in relevant_keywords)]

        print(f"\nRelevant tables for analysis: {len(relevant_tables)}")

        schema_info = {}

        for table in relevant_tables:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
            except:
                row_count = -1

            # Store schema info
            schema_info[table] = {
                'columns': [(col[1], col[2]) for col in columns],  # (name, type)
                'row_count': row_count
            }

            print(f"\n{table} ({row_count:,} rows):")
            print("  Columns:")
            for col_name, col_type in schema_info[table]['columns']:
                print(f"    - {col_name} ({col_type})")

        # Check for specific tables needed by intelligence prompts
        print("\n" + "="*80)
        print("CHECKING REQUIRED TABLES FOR INTELLIGENCE ANALYSES")
        print("="*80)

        required_checks = {
            'documents': ['id', 'content', 'content_text', 'title', 'source', 'created_date', 'saved_path'],
            'document_entities': ['entity_name', 'entity_text', 'entity_type', 'document_id'],
            'report_entities': ['entity_name', 'entity_type', 'report_id'],
            'mcf_documents': ['id', 'title', 'content', 'published_date'],
            'mcf_entities': ['entity_text', 'entity_type', 'document_id'],
            'thinktank_reports': ['id', 'title', 'source', 'published_date']
        }

        for table, expected_columns in required_checks.items():
            if table in schema_info:
                actual_columns = [col[0] for col in schema_info[table]['columns']]
                missing = [col for col in expected_columns if col not in actual_columns]
                present = [col for col in expected_columns if col in actual_columns]

                print(f"\n{table}:")
                print(f"  ✓ Table exists ({schema_info[table]['row_count']:,} rows)")
                print(f"  ✓ Has columns: {', '.join(present)}")
                if missing:
                    print(f"  ✗ Missing: {', '.join(missing)}")
                    # Find similar columns
                    similar = [col for col in actual_columns
                              if any(m.lower() in col.lower() for m in missing)]
                    if similar:
                        print(f"  → Similar columns available: {', '.join(similar)}")
            else:
                print(f"\n{table}:")
                print(f"  ✗ Table does not exist")
                # Look for similar tables
                similar_tables = [t for t in tables if table[:5] in t.lower()]
                if similar_tables:
                    print(f"  → Similar tables: {', '.join(similar_tables)}")

        # Check for Chinese content
        print("\n" + "="*80)
        print("CHECKING CHINESE CONTENT")
        print("="*80)

        if 'documents' in schema_info:
            cursor.execute("""
                SELECT COUNT(*) FROM documents
                WHERE content_text LIKE '%中%'
                   OR content_text LIKE '%国%'
            """)
            chinese_docs = cursor.fetchone()[0]
            print(f"\nDocuments with Chinese characters: {chinese_docs:,}")

        # Check entity coverage
        print("\n" + "="*80)
        print("CHECKING ENTITY COVERAGE")
        print("="*80)

        entity_tables = [t for t in schema_info.keys() if 'entit' in t.lower()]

        for table in entity_tables:
            print(f"\n{table}:")

            # Check entity types
            entity_col = None
            type_col = None

            for col, _ in schema_info[table]['columns']:
                if 'entity' in col.lower() and 'type' not in col.lower():
                    entity_col = col
                if 'type' in col.lower():
                    type_col = col

            if type_col:
                cursor.execute(f"""
                    SELECT {type_col}, COUNT(*) as count
                    FROM {table}
                    WHERE {type_col} IS NOT NULL
                    GROUP BY {type_col}
                    ORDER BY count DESC
                    LIMIT 10
                """)
                types = cursor.fetchall()
                print(f"  Entity types:")
                for entity_type, count in types:
                    print(f"    - {entity_type}: {count:,}")

        # Save schema to JSON for reference
        output = {
            'total_tables': len(tables),
            'relevant_tables': len(relevant_tables),
            'schema_details': schema_info,
            'table_availability': {
                table: table in schema_info
                for table in required_checks.keys()
            }
        }

        with open('analysis/intelligence_schema_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("\n" + "="*80)
        print("Schema details saved to: analysis/intelligence_schema_mapping.json")
        print("="*80)

        conn.close()

        return schema_info

    except Exception as e:
        print(f"\nError examining schema: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    schema = examine_schema()
