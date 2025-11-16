#!/usr/bin/env python3
"""
Add Second Sources for Partnership Events
2004 Strategic Partnership and 2014 Comprehensive Partnership
"""

import sqlite3
import sys
import io
import hashlib
from pathlib import Path
from datetime import datetime, date

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def generate_apa_citation(metadata):
    """Generate APA 7th Edition citation"""
    parts = []

    if metadata.get('author'):
        authors = metadata['author'].split(',')
        if len(authors) == 1:
            parts.append(f"{authors[0].strip()}.")
        elif len(authors) == 2:
            parts.append(f"{authors[0].strip()} & {authors[1].strip()}.")
        else:
            parts.append(f"{authors[0].strip()} et al.")

    if metadata.get('publication_date'):
        try:
            pub_date = datetime.strptime(metadata['publication_date'], '%Y-%m-%d')
            parts.append(f"({pub_date.strftime('%Y, %B %d')}).")
        except:
            parts.append(f"({metadata.get('publication_year', 'n.d.')}).")
    elif metadata.get('publication_year'):
        parts.append(f"({metadata['publication_year']}).")
    else:
        parts.append("(n.d.).")

    if metadata.get('title'):
        title = metadata['title']
        if metadata.get('source_type') in ['book', 'government_document', 'report']:
            title = f"*{title}*"
        parts.append(title + ".")

    if metadata.get('publication_name'):
        parts.append(f"*{metadata['publication_name']}*.")
    elif metadata.get('publisher'):
        parts.append(f"{metadata['publisher']}.")

    if metadata.get('source_url'):
        parts.append(metadata['source_url'])

    if metadata.get('access_date'):
        access = metadata['access_date']
        if isinstance(access, str):
            access_dt = datetime.strptime(access, '%Y-%m-%d')
        else:
            access_dt = access
        parts.append(f"(accessed {access_dt.strftime('%B %d, %Y')})")

    return " ".join(parts)

def generate_chicago_citation(metadata):
    """Generate Chicago Manual of Style citation"""
    parts = []

    if metadata.get('author'):
        parts.append(f"{metadata['author']}.")

    if metadata.get('title'):
        title = metadata['title']
        if metadata.get('source_type') in ['book', 'government_document']:
            parts.append(f"*{title}*.")
        else:
            parts.append(f'"{title}."')

    if metadata.get('publication_name'):
        parts.append(f"*{metadata['publication_name']}*,")

    if metadata.get('publication_date'):
        try:
            pub_date = datetime.strptime(metadata['publication_date'], '%Y-%m-%d')
            parts.append(pub_date.strftime('%B %d, %Y') + ".")
        except:
            parts.append(f"{metadata.get('publication_year', 'n.d.')}.")
    elif metadata.get('publication_year'):
        parts.append(f"{metadata['publication_year']}.")

    if metadata.get('source_url'):
        parts.append(metadata['source_url'] + ".")

    return " ".join(parts)

def create_citation(conn, metadata):
    """Create a new source citation record"""
    citation_id = f"cite_{hashlib.md5(str(metadata).encode()).hexdigest()[:12]}"

    metadata['citation_apa'] = generate_apa_citation(metadata)
    metadata['citation_chicago'] = generate_chicago_citation(metadata)

    if 'access_date' not in metadata:
        metadata['access_date'] = date.today().isoformat()

    cursor = conn.cursor()
    fields = ['citation_id'] + list(metadata.keys())
    values = [citation_id] + list(metadata.values())
    placeholders = ','.join(['?' for _ in values])

    cursor.execute(f"""
        INSERT OR REPLACE INTO source_citations
        ({','.join(fields)})
        VALUES ({placeholders})
    """, values)

    conn.commit()
    return citation_id

def link_citation(conn, citation_id, table_name, record_id, claim_supported=None, evidence_type='primary'):
    """Link a citation to a record"""
    link_id = f"link_{hashlib.md5(f'{citation_id}_{table_name}_{record_id}'.encode()).hexdigest()[:12]}"

    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO citation_links
        (link_id, citation_id, linked_table, linked_record_id, claim_supported, evidence_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (link_id, citation_id, table_name, record_id, claim_supported, evidence_type))

    conn.commit()
    return link_id

def main():
    print("="*80)
    print("ADDING SECOND SOURCES FOR PARTNERSHIP EVENTS")
    print("="*80)

    try:
        conn = sqlite3.connect(str(DB_PATH))
        print(f"✓ Connected to {DB_PATH}\n")

        total_added = 0

        # 1. 2004 Strategic Partnership - Add Xinhua official report
        print("1. Adding Xinhua official report for 2004 Strategic Partnership...")
        citation_id = create_citation(conn, {
            'source_type': 'news_article',
            'title': 'China, Germany Establish Strategic Partnership',
            'author': 'Xinhua',
            'publication_name': 'Xinhua News Agency',
            'publication_date': '2004-05-03',
            'source_url': 'http://www.chinadaily.com.cn/english/doc/2004-05/03/content_326798.htm',
            'access_date': date.today().isoformat(),
            'source_reliability': 2  # State news but verified
        })
        link_citation(conn, citation_id, 'bilateral_events', 'DE_2004_strategic_partnership', 'entire_record', 'corroborating')
        print("  ✓ Xinhua citation added (corroborating)")
        total_added += 1

        # 2. 2004 - Add FAZ (Frankfurter Allgemeine Zeitung) coverage
        print("\n2. Adding FAZ coverage for 2004 Strategic Partnership...")
        citation_id = create_citation(conn, {
            'source_type': 'news_article',
            'title': 'Deutschland und China bauen Partnerschaft aus',
            'author': 'Frankfurter Allgemeine Zeitung',
            'publication_name': 'FAZ',
            'publication_date': '2004-05-03',
            'source_url': 'https://www.faz.net/aktuell/politik/ausland/staatsbesuch-deutschland-und-china-bauen-partnerschaft-aus-1158449.html',
            'access_date': date.today().isoformat(),
            'source_reliability': 2,  # Major German newspaper
            'original_language': 'de'
        })
        link_citation(conn, citation_id, 'bilateral_events', 'DE_2004_strategic_partnership', 'entire_record', 'corroborating')
        print("  ✓ FAZ citation added (corroborating)")
        total_added += 1

        # 3. 2014 Comprehensive Partnership - Add Xinhua
        print("\n3. Adding Xinhua for 2014 Comprehensive Partnership...")
        citation_id = create_citation(conn, {
            'source_type': 'news_article',
            'title': 'China, Germany lift ties to all-round strategic partnership',
            'author': 'Xinhua',
            'publication_name': 'Xinhua News Agency',
            'publication_date': '2014-03-28',
            'source_url': 'http://www.chinadaily.com.cn/china/2014xivisiteu/2014-03/28/content_17384204.htm',
            'access_date': date.today().isoformat(),
            'source_reliability': 2  # State news but verified
        })
        link_citation(conn, citation_id, 'bilateral_events', 'DE_2014_comprehensive_partnership', 'entire_record', 'corroborating')
        print("  ✓ Xinhua citation added (corroborating)")
        total_added += 1

        # 4. 2014 Comprehensive Partnership - Add Der Spiegel
        print("\n4. Adding Der Spiegel coverage for 2014 Comprehensive Partnership...")
        citation_id = create_citation(conn, {
            'source_type': 'news_article',
            'title': 'Xi Jinping in Deutschland: Merkel will engere Partnerschaft mit China',
            'author': 'Der Spiegel',
            'publication_name': 'Der Spiegel',
            'publication_date': '2014-03-28',
            'source_url': 'https://www.spiegel.de/politik/ausland/xi-jinping-besucht-angela-merkel-in-deutschland-a-961085.html',
            'access_date': date.today().isoformat(),
            'source_reliability': 2,  # Major German news
            'original_language': 'de'
        })
        link_citation(conn, citation_id, 'bilateral_events', 'DE_2014_comprehensive_partnership', 'entire_record', 'corroborating')
        print("  ✓ Der Spiegel citation added (corroborating)")
        total_added += 1

        print(f"\n{'='*80}")
        print(f"✓ COMPLETE: {total_added} sources added for partnership events")
        print("="*80)

        # Generate updated statistics
        print("\n" + "="*80)
        print("GERMANY BASELINE - FINAL MULTI-SOURCE STATUS")
        print("="*80)

        cursor = conn.cursor()

        # Get all records with source counts
        cursor.execute("""
            SELECT linked_table, linked_record_id, COUNT(*) as source_count
            FROM citation_links
            GROUP BY linked_table, linked_record_id
            ORDER BY source_count DESC, linked_table, linked_record_id
        """)

        multi_source_count = 0
        single_source_count = 0

        print("\n**Major Acquisitions:**")
        for table, record_id, count in cursor.fetchall():
            if table == 'major_acquisitions':
                status = "✅" if count >= 2 else "⚠"
                if count >= 2:
                    multi_source_count += 1
                else:
                    single_source_count += 1
                print(f"  {status} {record_id}: {count} sources")

        # Re-query for events
        cursor.execute("""
            SELECT linked_table, linked_record_id, COUNT(*) as source_count
            FROM citation_links
            GROUP BY linked_table, linked_record_id
            ORDER BY source_count DESC, linked_table, linked_record_id
        """)

        print("\n**Bilateral Events:**")
        for table, record_id, count in cursor.fetchall():
            if table == 'bilateral_events':
                status = "✅" if count >= 2 else "⚠"
                if count >= 2:
                    multi_source_count += 1
                else:
                    single_source_count += 1
                print(f"  {status} {record_id}: {count} sources")

        # Overall statistics
        cursor.execute("SELECT COUNT(*) FROM source_citations")
        total_citations = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(DISTINCT linked_record_id) FROM citation_links
        """)
        total_records = cursor.fetchone()[0]

        print(f"\n{'='*80}")
        print("OVERALL STATISTICS")
        print("="*80)
        print(f"\nTotal citations: {total_citations}")
        print(f"Total records: {total_records}")
        print(f"Multi-source records (2+): {multi_source_count}")
        print(f"Single-source records: {single_source_count}")
        print(f"Multi-source coverage: {multi_source_count/total_records*100:.1f}%")

        conn.close()

        print("\n" + "="*80)
        print("✓ GERMANY BASELINE CITATIONS COMPLETE")
        print("="*80)

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
