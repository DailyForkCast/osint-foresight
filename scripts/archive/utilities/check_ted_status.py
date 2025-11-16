import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

# Get total records
cursor.execute('SELECT COUNT(*) FROM ted_contracts_production')
total = cursor.fetchone()[0]

# Get Chinese contracts
cursor.execute('SELECT COUNT(*) FROM ted_contracts_production WHERE is_chinese_related = 1')
chinese = cursor.fetchone()[0]

# Get format breakdown
cursor.execute('SELECT form_type, COUNT(*) as count FROM ted_contracts_production GROUP BY form_type')
format_breakdown = cursor.fetchall()

# Get recent records
cursor.execute('SELECT COUNT(*) FROM ted_contracts_production WHERE source_archive LIKE "%2024%" OR source_archive LIKE "%2025%"')
recent = cursor.fetchone()[0]

print(f'Total records: {total:,}')
print(f'Chinese contracts: {chinese:,}')
print(f'Era 3 (2024-2025) records: {recent:,}')
print(f'\nFormat breakdown:')
for ft, cnt in format_breakdown:
    if ft:
        print(f'  {ft}: {cnt:,}')
    else:
        print(f'  (no format): {cnt:,}')

conn.close()
