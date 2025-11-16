#!/usr/bin/env python3
"""
Investigate why 98.2% of documents have no content
"""

import sqlite3
import json
from pathlib import Path

def investigate_content_issue():
    """Deep dive into the content extraction problem"""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("INVESTIGATING DOCUMENT CONTENT ISSUE")
    print("="*80)

    # 1. Sample documents WITH content
    print("\n[DOCUMENTS WITH CONTENT - Sample 5]")
    cursor.execute("""
        SELECT id, title, publisher_org, content_length,
               SUBSTR(content_text, 1, 200) as content_preview
        FROM documents
        WHERE content_text IS NOT NULL
          AND LENGTH(content_text) > 100
        LIMIT 5
    """)

    for row in cursor.fetchall():
        try:
            print(f"\nDoc ID: {row['id']}")
            print(f"  Title: {row['title'][:80] if row['title'] else 'None'}...")
            print(f"  Publisher: {row['publisher_org'][:60] if row['publisher_org'] else 'None'}")
            print(f"  Content Length: {row['content_length']:,} chars")
            print(f"  Preview: {row['content_preview'][:150] if row['content_preview'] else 'None'}...")
        except:
            print(f"\nDoc ID: {row['id']} [unicode content - cannot display]")

    # 2. Sample documents WITHOUT content
    print("\n\n[DOCUMENTS WITHOUT CONTENT - Sample 10]")
    cursor.execute("""
        SELECT id, title, publisher_org, content_length, content_text,
               saved_path, hash_sha256
        FROM documents
        WHERE content_text IS NULL
           OR LENGTH(content_text) <= 100
        LIMIT 10
    """)

    for row in cursor.fetchall():
        try:
            print(f"\nDoc ID: {row['id']}")
            print(f"  Title: {row['title'][:80] if row['title'] else 'None'}...")
            print(f"  Publisher: {row['publisher_org'][:60] if row['publisher_org'] else 'None'}")
            print(f"  Content Length: {row['content_length']} chars")
            print(f"  Content Text: '{row['content_text']}'")
            print(f"  Saved Path: {row['saved_path']}")
            print(f"  Hash: {row['hash_sha256'][:16] if row['hash_sha256'] else 'None'}...")
        except:
            print(f"\nDoc ID: {row['id']} [unicode - cannot display fully]")
            print(f"  Content Length: {row['content_length']} chars")
            print(f"  Saved Path: {row['saved_path']}")

    # 3. Check if there's a pattern by publisher
    print("\n\n[CONTENT AVAILABILITY BY PUBLISHER]")
    cursor.execute("""
        SELECT
            publisher_org,
            COUNT(*) as total_docs,
            COUNT(CASE WHEN LENGTH(content_text) > 100 THEN 1 END) as with_content,
            COUNT(CASE WHEN LENGTH(content_text) <= 100 OR content_text IS NULL THEN 1 END) as without_content
        FROM documents
        WHERE publisher_org IS NOT NULL
        GROUP BY publisher_org
        ORDER BY total_docs DESC
        LIMIT 10
    """)

    print(f"{'Publisher':<60} {'Total':<8} {'With':<8} {'Without':<8} {'%With':<8}")
    print(f"{'-'*60} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for row in cursor.fetchall():
        pct = (row['with_content'] / row['total_docs'] * 100) if row['total_docs'] > 0 else 0
        pub = row['publisher_org'][:60] if row['publisher_org'] else 'Unknown'
        try:
            print(f"{pub:<60} {row['total_docs']:<8} {row['with_content']:<8} {row['without_content']:<8} {pct:<8.1f}")
        except:
            print(f"[unicode publisher] {row['total_docs']:<8} {row['with_content']:<8} {row['without_content']:<8} {pct:<8.1f}")

    # 4. Check the documents table schema for content-related fields
    print("\n\n[DOCUMENTS TABLE SCHEMA - Content Fields]")
    cursor.execute("PRAGMA table_info(documents)")
    content_fields = []
    for row in cursor.fetchall():
        col_name = row[1]
        if any(keyword in col_name.lower() for keyword in ['content', 'text', 'body', 'html', 'extract']):
            content_fields.append((row[1], row[2]))  # name, type

    print("Content-related columns:")
    for name, dtype in content_fields:
        print(f"  - {name} ({dtype})")

    # 5. Check if saved_path points to actual files
    print("\n\n[SAVED PATH VALIDATION - Sample 5]")
    cursor.execute("""
        SELECT id, title, saved_path
        FROM documents
        WHERE saved_path IS NOT NULL
        LIMIT 5
    """)

    for row in cursor.fetchall():
        file_path = row['saved_path']
        exists = Path(file_path).exists() if file_path else False
        print(f"\nDoc ID: {row['id']}")
        print(f"  Saved Path: {file_path}")
        print(f"  Exists: {exists}")

        if exists and file_path:
            p = Path(file_path)
            print(f"  Size: {p.stat().st_size:,} bytes")

            # Try to read if it's a JSON file
            if p.suffix == '.json':
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"  JSON keys: {list(data.keys())[:10]}")

                        # Check for content fields
                        content_keys = [k for k in data.keys() if any(word in k.lower() for word in ['content', 'text', 'body', 'html'])]
                        print(f"  Content keys: {content_keys}")

                        if content_keys:
                            for key in content_keys[:2]:
                                val = data[key]
                                if isinstance(val, str):
                                    print(f"    {key}: {len(val)} chars - '{val[:100]}...'")
                except Exception as e:
                    print(f"  Error reading JSON: {e}")

    conn.close()

if __name__ == "__main__":
    investigate_content_issue()
