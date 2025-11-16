#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract TED Chinese entities for user review
"""

import sqlite3
import json

db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for Chinese entity tables
tables_to_check = [
    'ted_procurement_chinese_entities_found',
    'ted_china_contracts_fixed',
    'ted_contractors'
]

results = {}

for table in tables_to_check:
    try:
        # Get count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        if count > 0:
            results[table] = {
                'total_records': count,
                'entities': []
            }

            # Get schema
            cursor.execute(f"PRAGMA table_info({table})")
            schema = cursor.fetchall()
            columns = [col[1] for col in schema]
            results[table]['columns'] = columns

            # For ted_contractors, filter for Chinese only
            if table == 'ted_contractors':
                cursor.execute(f"""
                    SELECT contractor_name, COUNT(*) as count, contractor_country
                    FROM {table}
                    WHERE is_chinese = 1
                    GROUP BY contractor_name, contractor_country
                    ORDER BY count DESC
                """)
            else:
                # For other tables, get all unique entities
                name_col = 'contractor_name' if 'contractor_name' in columns else columns[0]
                cursor.execute(f"""
                    SELECT {name_col}, COUNT(*) as count
                    FROM {table}
                    GROUP BY {name_col}
                    ORDER BY count DESC
                """)

            entities = cursor.fetchall()
            results[table]['unique_entities'] = len(entities)
            results[table]['entities'] = entities

    except sqlite3.OperationalError:
        continue

conn.close()

# Write results to file
output = {
    'summary': {
        table: {
            'total_records': data['total_records'],
            'unique_entities': data['unique_entities'],
            'columns': data['columns']
        } for table, data in results.items()
    },
    'entities_by_table': {}
}

for table, data in results.items():
    output['entities_by_table'][table] = [
        {
            'name': ent[0] if ent[0] else '[NULL]',
            'contract_count': ent[1],
            'country': ent[2] if len(ent) > 2 else None
        } for ent in data['entities']
    ]

# Save JSON
with open('analysis/ted_chinese_entities_current.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Save CSV for review
with open('analysis/ted_chinese_entities_for_review.csv', 'w', encoding='utf-8', newline='') as f:
    f.write('table,entity_name,contract_count,country,decision,notes\n')

    for table, data in results.items():
        for ent in data['entities']:
            name = str(ent[0]).replace('"', '""') if ent[0] else '[NULL]'
            count = ent[1]
            country = str(ent[2]) if len(ent) > 2 and ent[2] else ''
            f.write(f'"{table}","{name}",{count},"{country}",,\n')

print("Files created:")
print("  - analysis/ted_chinese_entities_current.json")
print("  - analysis/ted_chinese_entities_for_review.csv")
print("\nSummary:")
for table, data in results.items():
    print(f"  {table}: {data['total_records']:,} records, {data['unique_entities']} unique entities")
