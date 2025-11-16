import sqlite3
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cur = conn.cursor()

cur.execute("""
    SELECT e.event_id, e.event_title, e.event_date, e.country_code,
           COUNT(DISTINCT c.citation_id) as citation_count
    FROM bilateral_events e
    LEFT JOIN citation_links cl ON e.event_id = cl.linked_record_id AND cl.linked_table = 'bilateral_events'
    LEFT JOIN source_citations c ON cl.citation_id = c.citation_id
    GROUP BY e.event_id
    HAVING citation_count < 2
    ORDER BY e.event_date DESC
""")

print("Events needing second source:")
print("="*80)
single_source_events = []
for row in cur.fetchall():
    event_id, title, date, country, count = row
    print(f"{event_id} ({country}, {date}): {title}")
    print(f"  Current sources: {count}")
    single_source_events.append(event_id)
    print()

print(f"\nTotal events needing second source: {len(single_source_events)}")

conn.close()
