import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()

cur.execute('PRAGMA table_info(ted_contracts_production)')
existing = {row[1] for row in cur.fetchall()}

cols = {
    'document_type': 'TEXT', 'form_type': 'TEXT', 'ca_official_name': 'TEXT',
    'ca_address': 'TEXT', 'ca_city': 'TEXT', 'ca_postal_code': 'TEXT',
    'ca_country': 'TEXT', 'ca_type': 'TEXT', 'ca_main_activity': 'TEXT',
    'contract_description': 'TEXT', 'contract_type': 'TEXT', 'cpv_main': 'TEXT',
    'cpv_additional': 'TEXT', 'nuts_code': 'TEXT', 'place_of_performance': 'TEXT',
    'value_estimated': 'REAL', 'value_total': 'REAL', 'currency': 'TEXT',
    'award_date': 'TEXT', 'number_tenders_received': 'INTEGER',
    'contractor_official_name': 'TEXT', 'contractor_city': 'TEXT',
    'contractor_postal_code': 'TEXT', 'contractor_sme': 'BOOLEAN',
    'additional_contractors': 'TEXT', 'subcontractors': 'TEXT',
    'procedure_type': 'TEXT', 'award_criteria': 'TEXT', 'submission_deadline': 'TEXT',
    'framework_agreement': 'BOOLEAN', 'gpa_covered': 'BOOLEAN',
    'chinese_entities': 'TEXT', 'validator_version': 'TEXT'
}

missing = {c: t for c, t in cols.items() if c not in existing}
print(f'Adding {len(missing)} columns...')

for col, dtype in missing.items():
    try:
        cur.execute(f'ALTER TABLE ted_contracts_production ADD COLUMN {col} {dtype}')
        print(f'  {col}')
    except Exception as e:
        print(f'  SKIP {col}: {e}')

conn.commit()
cur.execute('SELECT COUNT(*) FROM ted_contracts_production')
print(f'\nDone. Records: {cur.fetchone()[0]:,}')
conn.close()
