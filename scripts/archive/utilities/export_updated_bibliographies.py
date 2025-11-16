#!/usr/bin/env python3
"""
Export Updated Bibliographies After Adding Secondary Sources
"""

import sqlite3
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_DIR = Path("C:/Projects/OSINT - Foresight/analysis")

def export_bibliography(conn, format='apa'):
    """Export bibliography in specified format"""
    cursor = conn.cursor()

    # Get all citations ordered by publication date
    cursor.execute("""
        SELECT * FROM source_citations
        ORDER BY publication_date DESC, title
    """)

    citations = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]

    bibliography = []
    for row in citations:
        citation_dict = dict(zip(cols, row))
        if format == 'apa':
            bib_entry = citation_dict.get('citation_apa', 'Citation not generated')
        elif format == 'chicago':
            bib_entry = citation_dict.get('citation_chicago', 'Citation not generated')
        else:
            bib_entry = citation_dict.get('citation_apa', 'Citation not generated')

        bibliography.append(bib_entry)

    return "\n\n".join(bibliography)

def main():
    print("="*80)
    print("EXPORTING UPDATED BIBLIOGRAPHIES")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        conn = sqlite3.connect(str(DB_PATH))
        print(f"✓ Connected to {DB_PATH}\n")

        # Export APA bibliography
        print("1. Generating APA bibliography...")
        apa_bib = export_bibliography(conn, 'apa')
        apa_path = OUTPUT_DIR / "GERMANY_BIBLIOGRAPHY_APA.md"

        with open(apa_path, 'w', encoding='utf-8') as f:
            f.write(f"# Bibliography - APA\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(apa_bib)

        print(f"  ✓ APA bibliography exported to: {apa_path}")

        # Export Chicago bibliography
        print("\n2. Generating Chicago bibliography...")
        chicago_bib = export_bibliography(conn, 'chicago')
        chicago_path = OUTPUT_DIR / "GERMANY_BIBLIOGRAPHY_CHICAGO.md"

        with open(chicago_path, 'w', encoding='utf-8') as f:
            f.write(f"# Bibliography - CHICAGO\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(chicago_bib)

        print(f"  ✓ Chicago bibliography exported to: {chicago_path}")

        # Count citations
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM source_citations")
        total = cursor.fetchone()[0]

        print(f"\n{'='*80}")
        print(f"✓ BIBLIOGRAPHIES UPDATED")
        print("="*80)
        print(f"\nTotal citations exported: {total}")
        print(f"\nFiles created:")
        print(f"  - {apa_path}")
        print(f"  - {chicago_path}")

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
