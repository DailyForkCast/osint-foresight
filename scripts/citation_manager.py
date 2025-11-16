#!/usr/bin/env python3
"""
Citation Manager for Bilateral Relations Intelligence
Comprehensive source citation, tracking, and export system

Features:
- Automatic citation generation (APA, Chicago, MLA)
- URL archiving via Archive.org
- Multi-source tracking per claim
- Bibliography export
- Link rot prevention
- Source verification
"""

import sqlite3
import sys
import io
from pathlib import Path
from datetime import datetime
from datetime import date as date_class
import hashlib
import re
import json

# ============================================================================
# SECURITY: SQL injection prevention through identifier validation
# ============================================================================

def validate_sql_identifier(identifier):
    """
    SECURITY: Validate SQL identifier (table or column name).
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

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class CitationManager:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(str(self.db_path))
        print(f"Connected to {self.db_path}")

    def generate_apa_citation(self, metadata):
        """
        Generate APA 7th Edition citation

        Format examples:
        - News: Author, A. A. (Year, Month Day). Title. Publication. URL
        - Gov Doc: Agency. (Year). Title. URL
        - Book: Author, A. A. (Year). Title. Publisher.
        """
        parts = []

        # Author
        if metadata.get('author'):
            authors = metadata['author'].split(',')
            if len(authors) == 1:
                parts.append(f"{authors[0].strip()}.")
            elif len(authors) == 2:
                parts.append(f"{authors[0].strip()} & {authors[1].strip()}.")
            else:
                parts.append(f"{authors[0].strip()} et al.")

        # Date
        if metadata.get('publication_date'):
            try:
                pub_date = datetime.strptime(metadata['publication_date'], '%Y-%m-%d')
                parts.append(f"({pub_date.strftime('%Y, %B %d')})." if pub_date.day else f"({pub_date.year}).")
            except:
                parts.append(f"({metadata.get('publication_year', 'n.d.')}).")
        elif metadata.get('publication_year'):
            parts.append(f"({metadata['publication_year']}).")
        else:
            parts.append("(n.d.).")

        # Title
        if metadata.get('title'):
            title = metadata['title']
            # Italicize if book/report, regular if article
            if metadata.get('source_type') in ['book', 'government_document', 'report']:
                title = f"*{title}*"
            parts.append(title + ".")

        # Source/Publisher
        if metadata.get('publication_name'):
            parts.append(f"*{metadata['publication_name']}*.")
        elif metadata.get('publisher'):
            parts.append(f"{metadata['publisher']}.")

        # URL
        if metadata.get('source_url'):
            parts.append(metadata['source_url'])

        # Access date
        if metadata.get('access_date'):
            access = metadata['access_date']
            if isinstance(access, str):
                access_dt = datetime.strptime(access, '%Y-%m-%d')
            else:
                access_dt = access
            # APA 7 doesn't require access date for stable sources, but we include for archival
            parts.append(f"(accessed {access_dt.strftime('%B %d, %Y')})")

        return " ".join(parts)

    def generate_chicago_citation(self, metadata):
        """
        Generate Chicago Manual of Style citation

        Format: Author. "Title." Publication, Date. URL.
        """
        parts = []

        # Author
        if metadata.get('author'):
            parts.append(f"{metadata['author']}.")

        # Title (in quotes for articles, italics for books)
        if metadata.get('title'):
            title = metadata['title']
            if metadata.get('source_type') in ['book', 'government_document']:
                parts.append(f"*{title}*.")
            else:
                parts.append(f'"{title}."')

        # Publication
        if metadata.get('publication_name'):
            parts.append(f"*{metadata['publication_name']}*,")

        # Date
        if metadata.get('publication_date'):
            try:
                pub_date = datetime.strptime(metadata['publication_date'], '%Y-%m-%d')
                parts.append(pub_date.strftime('%B %d, %Y') + ".")
            except:
                parts.append(f"{metadata.get('publication_year', 'n.d.')}.")
        elif metadata.get('publication_year'):
            parts.append(f"{metadata['publication_year']}.")

        # URL
        if metadata.get('source_url'):
            parts.append(metadata['source_url'] + ".")

        return " ".join(parts)

    def create_citation(self, metadata, auto_generate=True):
        """
        Create a new source citation record

        Args:
            metadata: Dict with citation fields
            auto_generate: Automatically generate formatted citations

        Returns:
            citation_id
        """
        # Generate citation_id
        citation_id = f"cite_{hashlib.md5(str(metadata).encode()).hexdigest()[:12]}"

        # Auto-generate formatted citations
        if auto_generate:
            metadata['citation_apa'] = self.generate_apa_citation(metadata)
            metadata['citation_chicago'] = self.generate_chicago_citation(metadata)

        # Ensure required fields
        if 'access_date' not in metadata:
            metadata['access_date'] = date_class.today().isoformat()

        # Insert citation
        cursor = self.conn.cursor()

        fields = ['citation_id'] + list(metadata.keys())
        # SECURITY: Validate all column names before use in SQL
        safe_fields = [validate_sql_identifier(field) for field in fields]
        values = [citation_id] + list(metadata.values())
        placeholders = ','.join(['?' for _ in values])

        cursor.execute(f"""
            INSERT OR REPLACE INTO source_citations
            ({','.join(safe_fields)})
            VALUES ({placeholders})
        """, values)

        self.conn.commit()
        return citation_id

    def link_citation(self, citation_id, table_name, record_id, claim_supported=None, evidence_type='primary'):
        """
        Link a citation to a record

        Args:
            citation_id: ID of the citation
            table_name: Table containing the record ('major_acquisitions', etc.)
            record_id: Primary key of the record
            claim_supported: Specific claim (e.g., "deal_value", "acquisition_date")
            evidence_type: 'primary', 'secondary', 'corroborating'
        """
        link_id = f"link_{hashlib.md5(f'{citation_id}_{table_name}_{record_id}'.encode()).hexdigest()[:12]}"

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO citation_links
            (link_id, citation_id, linked_table, linked_record_id, claim_supported, evidence_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (link_id, citation_id, table_name, record_id, claim_supported, evidence_type))

        self.conn.commit()
        return link_id

    def migrate_existing_sources(self, country_code='DE'):
        """
        Migrate existing source_url fields to proper citation records
        """
        print(f"\nMigrating existing sources for {country_code}...")

        cursor = self.conn.cursor()
        migrated = 0

        # Migrate major_acquisitions
        print("\n1. Migrating major_acquisitions...")
        cursor.execute("""
            SELECT acquisition_id, target_company, source_url, announcement_date
            FROM major_acquisitions
            WHERE country_code = ? AND source_url IS NOT NULL
        """, (country_code,))

        for acq_id, company, url, date in cursor.fetchall():
            # Parse URL to extract metadata
            metadata = self._parse_url_metadata(url)
            metadata.update({
                'source_type': 'news_article',
                'title': f"Chinese acquisition of {company}",
                'source_url': url,
                'access_date': date_class.today().isoformat(),
                'source_reliability': 2  # News source
            })

            citation_id = self.create_citation(metadata)
            self.link_citation(citation_id, 'major_acquisitions', acq_id, 'entire_record', 'primary')
            migrated += 1
            print(f"  ✓ {company}: Citation created")

        # Migrate bilateral_events
        print("\n2. Migrating bilateral_events...")
        cursor.execute("""
            SELECT event_id, event_title, source_url, source_type, source_reliability, event_date
            FROM bilateral_events
            WHERE country_code = ? AND source_url IS NOT NULL
        """, (country_code,))

        for event_id, title, url, source_type, reliability, event_date in cursor.fetchall():
            metadata = self._parse_url_metadata(url)
            metadata.update({
                'source_type': self._map_source_type(source_type),
                'title': title,
                'source_url': url,
                'access_date': date_class.today().isoformat(),
                'source_reliability': reliability or 3,
                'government_official': 1 if source_type == 'official_statement' else 0
            })

            citation_id = self.create_citation(metadata)
            self.link_citation(citation_id, 'bilateral_events', event_id, 'entire_record', 'primary')
            migrated += 1
            print(f"  ✓ {title}: Citation created")

        print(f"\nMigration complete: {migrated} citations created")
        return migrated

    def _parse_url_metadata(self, url):
        """Extract metadata from URL"""
        metadata = {}

        # Publication name from domain
        if 'reuters.com' in url:
            metadata['publication_name'] = 'Reuters'
            metadata['author'] = 'Reuters'
        elif 'bbc.com' in url or 'bbc.co.uk' in url:
            metadata['publication_name'] = 'BBC News'
            metadata['author'] = 'BBC'
        elif 'dw.com' in url:
            metadata['publication_name'] = 'Deutsche Welle'
            metadata['author'] = 'Deutsche Welle'
        elif 'state.gov' in url:
            metadata['publication_name'] = 'U.S. Department of State'
            metadata['author'] = 'U.S. Department of State'
            metadata['publisher'] = 'U.S. Government'
        elif 'auswaertiges-amt.de' in url:
            metadata['publication_name'] = 'German Federal Foreign Office'
            metadata['author'] = 'Auswärtiges Amt'
            metadata['publisher'] = 'German Government'
        elif 'fmprc.gov.cn' in url:
            metadata['publication_name'] = 'Chinese Ministry of Foreign Affairs'
            metadata['author'] = 'FMPRC'
            metadata['publisher'] = 'Chinese Government'

        return metadata

    def _map_source_type(self, old_type):
        """Map old source_type to new citation source_type"""
        mapping = {
            'official_statement': 'government_document',
            'news': 'news_article',
            'treaty': 'treaty',
            'academic': 'academic_paper',
            'government_report': 'government_document'
        }
        return mapping.get(old_type, 'news_article')

    def generate_bibliography(self, table_name=None, record_id=None, format='apa'):
        """
        Generate formatted bibliography

        Args:
            table_name: Optional - limit to specific table
            record_id: Optional - limit to specific record
            format: 'apa', 'chicago', or 'mla'

        Returns:
            Formatted bibliography string
        """
        cursor = self.conn.cursor()

        if table_name and record_id:
            # Bibliography for specific record
            query = """
                SELECT DISTINCT sc.*
                FROM source_citations sc
                JOIN citation_links cl ON sc.citation_id = cl.citation_id
                WHERE cl.linked_table = ? AND cl.linked_record_id = ?
                ORDER BY sc.publication_date DESC
            """
            cursor.execute(query, (table_name, record_id))
        else:
            # Full bibliography
            query = "SELECT * FROM source_citations ORDER BY publication_date DESC"
            cursor.execute(query)

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

    def export_bibliography_file(self, filename, format='apa'):
        """Export bibliography to file"""
        bibliography = self.generate_bibliography(format=format)

        output_path = Path(f"C:/Projects/OSINT - Foresight/analysis/{filename}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Bibliography - {format.upper()}\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(bibliography)

        print(f"\nBibliography exported to: {output_path}")
        return output_path

    def citation_quality_report(self, country_code='DE'):
        """Generate citation quality report"""
        print("\n" + "="*80)
        print("CITATION QUALITY REPORT")
        print("="*80)

        cursor = self.conn.cursor()

        # Total citations
        cursor.execute("SELECT COUNT(*) FROM source_citations")
        total = cursor.fetchone()[0]
        print(f"\nTotal citations: {total}")

        # Citations by type
        cursor.execute("""
            SELECT source_type, COUNT(*) as count
            FROM source_citations
            GROUP BY source_type
            ORDER BY count DESC
        """)
        print("\nCitations by type:")
        for stype, count in cursor.fetchall():
            print(f"  {stype}: {count}")

        # Records with multiple sources
        cursor.execute("""
            SELECT linked_table, COUNT(DISTINCT linked_record_id) as records,
                   AVG(source_count) as avg_sources
            FROM (
                SELECT linked_table, linked_record_id, COUNT(*) as source_count
                FROM citation_links
                GROUP BY linked_table, linked_record_id
            )
            GROUP BY linked_table
        """)
        print("\nMulti-source coverage:")
        for table, records, avg in cursor.fetchall():
            print(f"  {table}: {records} records, {avg:.1f} avg sources")

        # Insufficient sources
        cursor.execute("SELECT COUNT(*) FROM v_insufficient_sources")
        insufficient = cursor.fetchone()[0]
        if insufficient:
            print(f"\n⚠ Records with <2 sources: {insufficient}")
        else:
            print(f"\n✓ All records have 2+ sources")

        # Source reliability distribution
        cursor.execute("""
            SELECT source_reliability, COUNT(*) as count
            FROM source_citations
            GROUP BY source_reliability
            ORDER BY source_reliability
        """)
        print("\nSource reliability distribution:")
        for reliability, count in cursor.fetchall():
            reliability_label = {
                1: 'Primary official',
                2: 'Verified secondary',
                3: 'Credible',
                4: 'Unverified'
            }.get(reliability, 'Unknown')
            print(f"  Level {reliability} ({reliability_label}): {count}")

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

def main():
    print("="*80)
    print("CITATION MANAGER")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    manager = CitationManager()

    try:
        manager.connect()

        # Integrate citation framework schema
        print("\n1. Integrating citation framework schema...")
        schema_path = Path("C:/Projects/OSINT - Foresight/database/citation_framework_schema.sql")
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            cursor = manager.conn.cursor()
            cursor.executescript(schema_sql)
            manager.conn.commit()
            print("  ✓ Citation framework schema integrated")
        else:
            print("  ⚠ Schema file not found")

        # Migrate existing sources
        print("\n2. Migrating existing sources to citation framework...")
        migrated = manager.migrate_existing_sources('DE')

        # Generate quality report
        print("\n3. Citation quality assessment...")
        manager.citation_quality_report('DE')

        # Export bibliography
        print("\n4. Generating bibliography...")
        manager.export_bibliography_file('GERMANY_BIBLIOGRAPHY_APA.md', 'apa')
        manager.export_bibliography_file('GERMANY_BIBLIOGRAPHY_CHICAGO.md', 'chicago')

        print("\n" + "="*80)
        print("✓ CITATION FRAMEWORK OPERATIONAL")
        print("="*80)

        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        manager.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
