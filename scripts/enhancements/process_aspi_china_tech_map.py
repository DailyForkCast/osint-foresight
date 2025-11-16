#!/usr/bin/env python3
"""
ASPI China Tech Map Processor
Imports ASPI's China Tech Map data into the OSINT framework
Source: https://chinatechmap.aspi.org.au/#/data/
"""

import csv
import sqlite3
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ASPIChinaTechMapProcessor:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
        self.csv_path = Path("C:/Users/mrear/Downloads/data.csv")

    def create_tables(self):
        """Create ASPI China Tech Map tables"""
        logger.info("Creating ASPI tables...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main infrastructure table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aspi_infrastructure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aspi_infrastructure_id TEXT UNIQUE,
                company_id TEXT,
                company_name TEXT,
                infrastructure_type_id TEXT,
                infrastructure_type TEXT,
                secondary_infrastructure_type_id TEXT,
                secondary_infrastructure_type TEXT,
                country_id TEXT,
                country_name TEXT,
                city TEXT,
                latitude REAL,
                longitude REAL,
                label TEXT,
                year_commenced TEXT,
                year_ended TEXT,
                primary_topic TEXT,
                secondary_topic TEXT,
                third_topic TEXT,
                description TEXT,
                cable_id TEXT,
                highlight TEXT,
                cable_owner TEXT,
                ownership_type TEXT,
                is_soe INTEGER,
                street_address TEXT,
                created_date DATETIME,
                data_hash TEXT
            )
        """)

        # Companies extracted from ASPI
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aspi_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id TEXT UNIQUE,
                company_name TEXT,
                ownership_type TEXT,
                is_soe INTEGER,
                total_infrastructure_count INTEGER,
                countries_count INTEGER,
                created_date DATETIME
            )
        """)

        # Infrastructure types
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aspi_infrastructure_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_id TEXT UNIQUE,
                type_name TEXT,
                infrastructure_count INTEGER
            )
        """)

        # Topics/Technologies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aspi_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                infrastructure_id TEXT,
                topic_level TEXT,
                topic_name TEXT,
                created_date DATETIME,
                FOREIGN KEY(infrastructure_id) REFERENCES aspi_infrastructure(aspi_infrastructure_id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aspi_company ON aspi_infrastructure(company_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aspi_country ON aspi_infrastructure(country_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aspi_type ON aspi_infrastructure(infrastructure_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aspi_year ON aspi_infrastructure(year_commenced)")

        conn.commit()
        conn.close()

        logger.info("ASPI tables created successfully")

    def parse_id_field(self, field: str) -> tuple:
        """Parse ID fields like '1 | Huawei' into (id, name)"""
        if not field or field.strip() == '':
            return None, None

        parts = field.split('|')
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return None, field.strip()

    def clean_html(self, html_text: str) -> str:
        """Remove HTML tags and extract plain text"""
        if not html_text:
            return ''

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&rsquo;', "'")
        text = text.replace('&ldquo;', '"')
        text = text.replace('&rdquo;', '"')
        text = text.replace('&mdash;', '—')
        text = text.replace('&ndash;', '–')
        text = text.replace('&pound;', '£')

        # Clean up whitespace
        text = ' '.join(text.split())

        return text

    def is_soe(self, ownership_type: str) -> bool:
        """Determine if company is state-owned"""
        if not ownership_type:
            return False

        soe_indicators = ['state-owned', 'state owned', 'soe', 'government']
        ownership_lower = ownership_type.lower()

        return any(indicator in ownership_lower for indicator in soe_indicators)

    def process_csv(self):
        """Process ASPI CSV and import data"""
        logger.info(f"Processing CSV: {self.csv_path}")

        if not self.csv_path.exists():
            logger.error(f"CSV file not found: {self.csv_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM aspi_infrastructure")
        cursor.execute("DELETE FROM aspi_companies")
        cursor.execute("DELETE FROM aspi_infrastructure_types")
        cursor.execute("DELETE FROM aspi_topics")

        companies = {}
        infrastructure_types = {}

        imported = 0
        skipped = 0

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Parse ID fields
                    company_id, company_name = self.parse_id_field(row.get('company_id', ''))
                    infra_type_id, infra_type_name = self.parse_id_field(row.get('infrastructure_type_id', ''))
                    sec_infra_type_id, sec_infra_type_name = self.parse_id_field(row.get('secondary_infrastructure_type_id', ''))
                    country_id, country_name = self.parse_id_field(row.get('country_id', ''))

                    # Skip if no company or infrastructure type
                    if not company_name or not infra_type_name:
                        skipped += 1
                        continue

                    # Clean description
                    description = self.clean_html(row.get('text', ''))

                    # Parse ownership
                    ownership_type_id, ownership_type = self.parse_id_field(row.get('type_of_company_id_ref', ''))
                    is_soe_flag = 1 if self.is_soe(ownership_type) else 0

                    # Parse coordinates
                    try:
                        lat = float(row.get('overseas_infrastructure_lat', '') or 0)
                        lng = float(row.get('overseas_infrastructure_lng', '') or 0)
                    except:
                        lat, lng = 0.0, 0.0

                    # Create hash
                    hash_input = f"{company_name}:{infra_type_name}:{country_name}:{row.get('label', '')}"
                    data_hash = hashlib.md5(hash_input.encode()).hexdigest()

                    # Insert infrastructure record
                    cursor.execute("""
                        INSERT OR IGNORE INTO aspi_infrastructure (
                            aspi_infrastructure_id, company_id, company_name,
                            infrastructure_type_id, infrastructure_type,
                            secondary_infrastructure_type_id, secondary_infrastructure_type,
                            country_id, country_name, city, latitude, longitude,
                            label, year_commenced, year_ended,
                            primary_topic, secondary_topic, third_topic,
                            description, cable_id, highlight, cable_owner,
                            ownership_type, is_soe, street_address,
                            created_date, data_hash
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row.get('company_overseas_infrastructure_id'),
                        company_id, company_name,
                        infra_type_id, infra_type_name,
                        sec_infra_type_id, sec_infra_type_name,
                        country_id, country_name,
                        row.get('city', ''),
                        lat, lng,
                        row.get('label', ''),
                        row.get('year_commenced', ''),
                        row.get('year_ended', ''),
                        row.get('Primary topic', ''),
                        row.get('Secondary (if needed)', ''),
                        row.get('Third topic', ''),
                        description,
                        row.get('cable_id', ''),
                        row.get('highlight', ''),
                        row.get('cable_owner', ''),
                        ownership_type,
                        is_soe_flag,
                        row.get('street address', ''),
                        datetime.now().isoformat(),
                        data_hash
                    ))

                    # Track companies
                    if company_name:
                        if company_name not in companies:
                            companies[company_name] = {
                                'company_id': company_id,
                                'ownership_type': ownership_type,
                                'is_soe': is_soe_flag,
                                'count': 0,
                                'countries': set()
                            }
                        companies[company_name]['count'] += 1
                        if country_name:
                            companies[company_name]['countries'].add(country_name)

                    # Track infrastructure types
                    if infra_type_name:
                        if infra_type_name not in infrastructure_types:
                            infrastructure_types[infra_type_name] = {
                                'type_id': infra_type_id,
                                'count': 0
                            }
                        infrastructure_types[infra_type_name]['count'] += 1

                    # Insert topics
                    for topic_level, topic_name in [
                        ('primary', row.get('Primary topic', '')),
                        ('secondary', row.get('Secondary (if needed)', '')),
                        ('third', row.get('Third topic', ''))
                    ]:
                        if topic_name and topic_name.strip():
                            cursor.execute("""
                                INSERT INTO aspi_topics (infrastructure_id, topic_level, topic_name, created_date)
                                VALUES (?, ?, ?, ?)
                            """, (
                                row.get('company_overseas_infrastructure_id'),
                                topic_level,
                                topic_name.strip(),
                                datetime.now().isoformat()
                            ))

                    imported += 1

                    if imported % 500 == 0:
                        logger.info(f"Imported {imported} records...")
                        conn.commit()

                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    skipped += 1

        # Insert company summaries
        for company_name, data in companies.items():
            cursor.execute("""
                INSERT INTO aspi_companies (
                    company_id, company_name, ownership_type, is_soe,
                    total_infrastructure_count, countries_count, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data['company_id'],
                company_name,
                data['ownership_type'],
                data['is_soe'],
                data['count'],
                len(data['countries']),
                datetime.now().isoformat()
            ))

        # Insert infrastructure type summaries
        for type_name, data in infrastructure_types.items():
            cursor.execute("""
                INSERT INTO aspi_infrastructure_types (
                    type_id, type_name, infrastructure_count
                ) VALUES (?, ?, ?)
            """, (
                data['type_id'],
                type_name,
                data['count']
            ))

        conn.commit()
        conn.close()

        logger.info(f"\n{'='*80}")
        logger.info(f"ASPI China Tech Map Import Complete")
        logger.info(f"{'='*80}")
        logger.info(f"Infrastructure records imported: {imported:,}")
        logger.info(f"Records skipped: {skipped:,}")
        logger.info(f"Companies tracked: {len(companies):,}")
        logger.info(f"Infrastructure types: {len(infrastructure_types):,}")
        logger.info(f"{'='*80}")

        return imported

    def generate_summary(self):
        """Generate summary statistics"""
        logger.info("Generating summary statistics...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Company statistics
        companies = conn.execute("""
            SELECT company_name, ownership_type, is_soe,
                   total_infrastructure_count, countries_count
            FROM aspi_companies
            ORDER BY total_infrastructure_count DESC
            LIMIT 10
        """).fetchall()

        # Infrastructure type statistics
        types = conn.execute("""
            SELECT type_name, infrastructure_count
            FROM aspi_infrastructure_types
            ORDER BY infrastructure_count DESC
        """).fetchall()

        # Country statistics
        countries = conn.execute("""
            SELECT country_name, COUNT(*) as count
            FROM aspi_infrastructure
            WHERE country_name IS NOT NULL AND country_name != ''
            GROUP BY country_name
            ORDER BY count DESC
            LIMIT 20
        """).fetchall()

        # Topic statistics
        topics = conn.execute("""
            SELECT topic_name, COUNT(*) as count
            FROM aspi_topics
            WHERE topic_name IS NOT NULL AND topic_name != ''
            GROUP BY topic_name
            ORDER BY count DESC
            LIMIT 15
        """).fetchall()

        # SOE vs Private
        soe_stats = conn.execute("""
            SELECT
                SUM(CASE WHEN is_soe = 1 THEN 1 ELSE 0 END) as soe_count,
                SUM(CASE WHEN is_soe = 0 THEN 1 ELSE 0 END) as private_count
            FROM aspi_companies
        """).fetchone()

        # Get totals before closing connection
        total_infrastructure = conn.execute('SELECT COUNT(*) FROM aspi_infrastructure').fetchone()[0]
        total_companies = conn.execute('SELECT COUNT(*) FROM aspi_companies').fetchone()[0]

        conn.close()

        # Generate report
        report = f"""# ASPI China Tech Map - Import Summary
**Generated:** {datetime.now().isoformat()}

## Overview

- **Total Infrastructure Records:** {total_infrastructure:,}
- **Total Companies:** {total_companies:,}
- **SOEs:** {soe_stats['soe_count']:,} ({soe_stats['soe_count']/(soe_stats['soe_count']+soe_stats['private_count'])*100:.1f}%)
- **Private Companies:** {soe_stats['private_count']:,} ({soe_stats['private_count']/(soe_stats['soe_count']+soe_stats['private_count'])*100:.1f}%)
- **Countries Covered:** {len(countries):,}
- **Infrastructure Types:** {len(types):,}

## Top 10 Companies by Infrastructure Count

| Company | Ownership | Infrastructure Count | Countries |
|---------|-----------|---------------------|-----------|
"""

        for company in companies:
            ownership = "SOE" if company['is_soe'] else "Private"
            report += f"| {company['company_name']} | {ownership} | {company['total_infrastructure_count']:,} | {company['countries_count']:,} |\n"

        report += f"""\n## Infrastructure Types

| Type | Count |
|------|-------|
"""

        for itype in types:
            report += f"| {itype['type_name']} | {itype['infrastructure_count']:,} |\n"

        report += f"""\n## Top 20 Countries by Infrastructure Presence

| Country | Infrastructure Count |
|---------|---------------------|
"""

        for country in countries:
            report += f"| {country['country_name']} | {country['count']:,} |\n"

        report += f"""\n## Top 15 Technology Topics

| Topic | Mentions |
|-------|----------|
"""

        for topic in topics:
            report += f"| {topic['topic_name']} | {topic['count']:,} |\n"

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ASPI_CHINA_TECH_MAP_SUMMARY.md")
        report_path.write_text(report, encoding='utf-8')

        logger.info(f"Summary report saved to: {report_path}")

        return report

    def cross_reference_entities(self):
        """Cross-reference ASPI companies with existing entities"""
        logger.info("Cross-referencing ASPI entities...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Find ASPI companies in BIS Entity List
        bis_matches = conn.execute("""
            SELECT DISTINCT a.company_name, a.is_soe, a.total_infrastructure_count
            FROM aspi_companies a
            JOIN bis_entity_list_fixed b ON UPPER(b.entity_name) LIKE '%' || UPPER(a.company_name) || '%'
            ORDER BY a.total_infrastructure_count DESC
        """).fetchall()

        # Find ASPI companies in Report entities
        report_matches = conn.execute("""
            SELECT DISTINCT a.company_name, a.is_soe, a.total_infrastructure_count
            FROM aspi_companies a
            JOIN report_entities r ON UPPER(r.entity_name) = UPPER(a.company_name)
            ORDER BY a.total_infrastructure_count DESC
        """).fetchall()

        # Find ASPI companies in GLEIF
        gleif_matches = conn.execute("""
            SELECT DISTINCT a.company_name, a.is_soe, a.total_infrastructure_count
            FROM aspi_companies a
            JOIN gleif_entities g ON UPPER(g.legal_name) LIKE '%' || UPPER(a.company_name) || '%'
            ORDER BY a.total_infrastructure_count DESC
        """).fetchall()

        conn.close()

        logger.info(f"\n{'='*80}")
        logger.info(f"ASPI Cross-Reference Results")
        logger.info(f"{'='*80}")
        logger.info(f"ASPI companies in BIS Entity List: {len(bis_matches)}")
        logger.info(f"ASPI companies in Intelligence Reports: {len(report_matches)}")
        logger.info(f"ASPI companies in GLEIF: {len(gleif_matches)}")
        logger.info(f"{'='*80}")

        if bis_matches:
            logger.info("\nASPI companies on BIS Entity List (HIGH RISK):")
            for match in bis_matches[:10]:
                logger.info(f"  - {match['company_name']} ({match['total_infrastructure_count']} infrastructure projects)")

        return {
            'bis_matches': len(bis_matches),
            'report_matches': len(report_matches),
            'gleif_matches': len(gleif_matches)
        }

    def run(self):
        """Execute full ASPI processing pipeline"""
        logger.info("Starting ASPI China Tech Map processing...")

        # Create tables
        self.create_tables()

        # Process CSV
        imported = self.process_csv()

        # Generate summary
        self.generate_summary()

        # Cross-reference
        cross_ref_results = self.cross_reference_entities()

        logger.info("\n✅ ASPI China Tech Map processing complete!")

        return imported


if __name__ == "__main__":
    processor = ASPIChinaTechMapProcessor()
    processor.run()
