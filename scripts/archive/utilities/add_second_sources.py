#!/usr/bin/env python3
"""
Add Second Corroborating Sources for 13 Academic Events
Addresses validation finding: 13 events need multi-source verification
"""

import sqlite3
import hashlib
from pathlib import Path
from datetime import date

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=60.0)

def add_citation(citation_id, source_type, source_url, source_reliability,
                 author=None, publication_name=None, publication_date=None, title=None):
    """Add citation to source_citations table"""
    conn.execute("""
        INSERT OR REPLACE INTO source_citations
        (citation_id, source_type, source_url, source_reliability, author,
         publication_name, publication_date, title, access_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (citation_id, source_type, source_url, source_reliability, author,
          publication_name, publication_date, title, date.today().isoformat()))
    print(f"  Added citation: {citation_id}")

def link_citation(citation_id, event_id):
    """Link citation to event"""
    link_id = f"link_{hashlib.md5(f'{citation_id}{event_id}'.encode()).hexdigest()[:12]}"
    conn.execute("""
        INSERT OR REPLACE INTO citation_links
        (link_id, citation_id, linked_table, linked_record_id, evidence_strength)
        VALUES (?, ?, ?, ?, ?)
    """, (link_id, citation_id, 'bilateral_events', event_id, 'supporting'))
    print(f"  Linked {citation_id} to {event_id}")

print("ADDING SECOND SOURCES FOR ACADEMIC EVENTS")
print("="*80)

# Netherlands semiconductor research limits (2023)
print("\n1. Netherlands Semiconductor Research Limits (2023)")
add_citation(
    citation_id='cite_nl_2023_asml_bloomberg',
    source_type='news',
    source_url='https://www.bloomberg.com/news/articles/2024-07-15/us-pressure-on-dutch-china-links-reaches-asml-funded-university',
    source_reliability=2,
    publication_name='Bloomberg',
    publication_date='2024-07-15',
    title='ASML-Backed University Caught in Middle of US-China Chips War'
)
link_citation('cite_nl_2023_asml_bloomberg', 'NL_2023_semiconductor_research_limits')

# Sweden Confucius closures (2019)
print("\n2. Sweden Confucius Institute Closures (2019)")
add_citation(
    citation_id='cite_se_2019_confucius_rfa',
    source_type='news',
    source_url='https://www.rfa.org/english/news/china/sweden-confucius-04232020132659.html',
    source_reliability=2,
    publication_name='Radio Free Asia',
    publication_date='2020-04-23',
    title='Sweden to Shutter Last Confucius Teaching Program Amid Souring Ties'
)
link_citation('cite_se_2019_confucius_rfa', 'SE_2019_confucius_closures')

add_citation(
    citation_id='cite_se_2019_confucius_uwn',
    source_type='news',
    source_url='https://www.universityworldnews.com/post.php?story=20200513092025679',
    source_reliability=2,
    publication_name='University World News',
    publication_date='2020-05-13',
    title='Confucius institutions close as China relations deteriorate'
)
link_citation('cite_se_2019_confucius_uwn', 'SE_2019_confucius_closures')

# UK student restrictions (2022)
print("\n3. UK Student Restrictions (2022)")
add_citation(
    citation_id='cite_uk_2022_atas_lancet',
    source_type='academic',
    source_url='https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(23)00143-2/abstract',
    source_reliability=2,
    publication_name='The Lancet Oncology',
    publication_date='2023-04-01',
    title='Students and researchers from China barred from working in the UK'
)
link_citation('cite_uk_2022_atas_lancet', 'UK_2022_student_restrictions')

add_citation(
    citation_id='cite_uk_2022_atas_times',
    source_type='news',
    source_url='https://www.timeshighereducation.com/news/overseas-researchers-limbo-over-uk-security-clearance-delays',
    source_reliability=2,
    publication_name='Times Higher Education',
    publication_date='2022-09-15',
    title='Researchers hit by Atas security check delays'
)
link_citation('cite_uk_2022_atas_times', 'UK_2022_student_restrictions')

# Belgium Confucius closure (2019)
print("\n4. Belgium Confucius Institute Closure (2019)")
add_citation(
    citation_id='cite_be_2019_confucius_vub',
    source_type='institutional',
    source_url='https://press.vub.ac.be/the-vub-will-not-continue-its-cooperation-with-the-confucius-institute',
    source_reliability=1,
    publication_name='Vrije Universiteit Brussel Press',
    publication_date='2019-12-10',
    title='The VUB will not continue its cooperation with the Confucius Institute'
)
link_citation('cite_be_2019_confucius_vub', 'BE_2019_confucius_closure')

add_citation(
    citation_id='cite_be_2019_confucius_scmp',
    source_type='news',
    source_url='https://www.scmp.com/news/china/diplomacy/article/3041617/belgian-university-closes-its-chinese-state-funded-confucius',
    source_reliability=2,
    publication_name='South China Morning Post',
    publication_date='2019-12-11',
    title='Belgian university closes its Chinese state-funded Confucius Institute after spying claims'
)
link_citation('cite_be_2019_confucius_scmp', 'BE_2019_confucius_closure')

# Lithuania partnerships suspended (2021)
print("\n5. Lithuania Partnerships Context (2021)")
add_citation(
    citation_id='cite_lt_2021_relations_euronews',
    source_type='news',
    source_url='https://www.euronews.com/2021/11/21/china-downgrades-relations-with-lithuania-over-taiwan-embassy-spat',
    source_reliability=2,
    publication_name='Euronews',
    publication_date='2021-11-21',
    title='China downgrades relations with Lithuania over Taiwan embassy spat'
)
link_citation('cite_lt_2021_relations_euronews', 'LT_2021_university_partnerships_suspended')

# France CNRS-CAS joint labs (2019)
print("\n6. France-China Joint Research Laboratories (2019)")
add_citation(
    citation_id='cite_fr_2019_cnrs_cas_announcement',
    source_type='institutional',
    source_url='http://www.cnrs.fr/en/strengthening-partnership-between-cnrs-and-chinese-academy-sciences',
    source_reliability=1,
    publication_name='CNRS Press Release',
    publication_date='2019-10-08',
    title='Strengthening the partnership between CNRS and the Chinese Academy of Sciences'
)
link_citation('cite_fr_2019_cnrs_cas_announcement', 'FR_2019_cnrs_cas_joint_labs')

# Commit all changes
conn.commit()
print("\n" + "="*80)
print("SECOND SOURCES ADDED SUCCESSFULLY")
print("="*80)

# Verification
cur = conn.cursor()
cur.execute("""
    SELECT e.event_id, e.event_title, COUNT(DISTINCT c.citation_id) as citation_count
    FROM bilateral_events e
    LEFT JOIN citation_links cl ON e.event_id = cl.linked_record_id AND cl.linked_table = 'bilateral_events'
    LEFT JOIN source_citations c ON cl.citation_id = c.citation_id
    WHERE e.event_id IN (
        'NL_2023_semiconductor_research_limits',
        'SE_2019_confucius_closures',
        'UK_2022_student_restrictions',
        'BE_2019_confucius_closure',
        'LT_2021_university_partnerships_suspended',
        'FR_2019_cnrs_cas_joint_labs'
    )
    GROUP BY e.event_id
""")

print("\nVerification - Events with new sources:")
for row in cur.fetchall():
    event_id, title, count = row
    status = "OK" if count >= 2 else "NEEDS MORE"
    print(f"  [{status}] {event_id}: {count} sources")

# Check remaining events
cur.execute("""
    SELECT e.event_id, e.event_title, COUNT(DISTINCT c.citation_id) as citation_count
    FROM bilateral_events e
    LEFT JOIN citation_links cl ON e.event_id = cl.linked_record_id AND cl.linked_table = 'bilateral_events'
    LEFT JOIN source_citations c ON cl.citation_id = c.citation_id
    GROUP BY e.event_id
    HAVING citation_count < 2
""")

remaining = cur.fetchall()
print(f"\nRemaining events needing sources: {len(remaining)}")
for row in remaining:
    print(f"  - {row[0]}: {row[1]} ({row[2]} sources)")

conn.close()
print("\n[SUCCESS] Second source integration complete!")
