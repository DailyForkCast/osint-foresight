#!/usr/bin/env python3
"""
Entity Cross-Reference System
Finds entities that appear in multiple data sources (GLEIF, TED, USPTO, BIS, SEC_EDGAR, Reports)
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityCrossReference:
    def __init__(self):
        self.db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

    def find_cross_referenced_entities(self):
        """Find entities appearing in multiple data sources"""
        logger.info("Finding cross-referenced entities...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Data sources to check
        sources = {
            'GLEIF': 'gleif_entities',
            'TED': 'ted_china_entities',
            'USPTO': 'uspto_patents_chinese',
            'BIS_Entity': 'bis_entity_list_fixed',
            'BIS_Denied': 'bis_denied_persons',
            'SEC_EDGAR': 'sec_edgar_chinese_investors',
            'Reports': 'report_entities'
        }

        # Get entity names from each source
        entity_sources = {}

        # GLEIF entities
        logger.info("Extracting GLEIF entities...")
        gleif_entities = conn.execute('SELECT legal_name FROM gleif_entities WHERE legal_name IS NOT NULL').fetchall()
        for row in gleif_entities:
            name = row['legal_name'].strip()
            if name not in entity_sources:
                entity_sources[name] = set()
            entity_sources[name].add('GLEIF')

        # TED entities
        logger.info("Extracting TED entities...")
        ted_entities = conn.execute('SELECT entity_name FROM ted_china_entities WHERE entity_name IS NOT NULL').fetchall()
        for row in ted_entities:
            name = row['entity_name'].strip()
            if name not in entity_sources:
                entity_sources[name] = set()
            entity_sources[name].add('TED')

        # USPTO assignees
        logger.info("Extracting USPTO assignees...")
        uspto_entities = conn.execute('SELECT DISTINCT assignee_name FROM uspto_patents_chinese WHERE assignee_name IS NOT NULL').fetchall()
        for row in uspto_entities:
            name = row['assignee_name'].strip()
            if name not in entity_sources:
                entity_sources[name] = set()
            entity_sources[name].add('USPTO')

        # BIS Entity List
        logger.info("Extracting BIS entities...")
        bis_entities = conn.execute('SELECT entity_name FROM bis_entity_list_fixed WHERE entity_name IS NOT NULL').fetchall()
        for row in bis_entities:
            name = row['entity_name'].strip()
            if name not in entity_sources:
                entity_sources[name] = set()
            entity_sources[name].add('BIS_Entity')

        # BIS Denied Persons
        logger.info("Extracting BIS denied persons...")
        bis_denied = conn.execute('SELECT name FROM bis_denied_persons WHERE name IS NOT NULL').fetchall()
        for row in bis_denied:
            name = row['name'].strip()
            if name not in entity_sources:
                entity_sources[name] = set()
            entity_sources[name].add('BIS_Denied')

        # SEC EDGAR
        logger.info("Extracting SEC EDGAR entities...")
        sec_entities = conn.execute('SELECT DISTINCT investor_name FROM sec_edgar_chinese_investors WHERE investor_name IS NOT NULL').fetchall()
        for row in sec_entities:
            name = row['investor_name'].strip()
            if name not in entity_sources:
                entity_sources[name] = set()
            entity_sources[name].add('SEC_EDGAR')

        # Report entities
        logger.info("Extracting Report entities...")
        report_entities = conn.execute('SELECT DISTINCT entity_name FROM report_entities WHERE entity_name IS NOT NULL').fetchall()
        for row in report_entities:
            name = row['entity_name'].strip()
            if name not in entity_sources:
                entity_sources[name] = set()
            entity_sources[name].add('Reports')

        conn.close()

        # Find entities in multiple sources
        cross_referenced = {}
        for entity, sources_set in entity_sources.items():
            if len(sources_set) > 1:
                cross_referenced[entity] = list(sources_set)

        logger.info(f"Found {len(cross_referenced)} entities in multiple sources")
        return cross_referenced

    def find_fuzzy_matches(self):
        """Find potential matches using fuzzy matching (simplified version)"""
        logger.info("Finding fuzzy matches...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Get normalized names from all sources
        all_entities = {}

        # GLEIF
        gleif = conn.execute('SELECT legal_name FROM gleif_entities WHERE legal_name IS NOT NULL LIMIT 1000').fetchall()
        for row in gleif:
            normalized = self._normalize_name(row['legal_name'])
            if normalized:
                if normalized not in all_entities:
                    all_entities[normalized] = {'original': row['legal_name'], 'sources': set()}
                all_entities[normalized]['sources'].add('GLEIF')

        # TED
        ted = conn.execute('SELECT entity_name FROM ted_china_entities WHERE entity_name IS NOT NULL LIMIT 1000').fetchall()
        for row in ted:
            normalized = self._normalize_name(row['entity_name'])
            if normalized:
                if normalized not in all_entities:
                    all_entities[normalized] = {'original': row['entity_name'], 'sources': set()}
                all_entities[normalized]['sources'].add('TED')

        # USPTO
        uspto = conn.execute('SELECT DISTINCT assignee_name FROM uspto_patents_chinese WHERE assignee_name IS NOT NULL LIMIT 1000').fetchall()
        for row in uspto:
            normalized = self._normalize_name(row['assignee_name'])
            if normalized:
                if normalized not in all_entities:
                    all_entities[normalized] = {'original': row['assignee_name'], 'sources': set()}
                all_entities[normalized]['sources'].add('USPTO')

        conn.close()

        # Find matches
        fuzzy_matches = {}
        for normalized, data in all_entities.items():
            if len(data['sources']) > 1:
                fuzzy_matches[data['original']] = list(data['sources'])

        logger.info(f"Found {len(fuzzy_matches)} fuzzy matches")
        return fuzzy_matches

    def _normalize_name(self, name):
        """Normalize entity name for fuzzy matching"""
        if not name:
            return None

        # Convert to uppercase
        normalized = name.upper()

        # Remove common suffixes
        suffixes = [
            ' LTD', ' LIMITED', ' INC', ' INCORPORATED', ' CORP', ' CORPORATION',
            ' CO', ' COMPANY', ' LLC', ' LP', ' PLC', ' AG', ' SA', ' NV', ' BV',
            ' TECHNOLOGIES', ' TECHNOLOGY', ' GROUP', ' HOLDINGS'
        ]

        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()

        # Remove punctuation
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())

        # Remove extra spaces
        normalized = ' '.join(normalized.split())

        return normalized if len(normalized) > 2 else None

    def create_cross_reference_table(self, cross_referenced, fuzzy_matches):
        """Create entity_cross_references table"""
        logger.info("Creating entity_cross_references table...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table if doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_cross_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                normalized_name TEXT,
                source_count INTEGER,
                sources TEXT,
                match_type TEXT,
                risk_level TEXT,
                created_date DATETIME
            )
        """)

        # Clear existing data
        cursor.execute('DELETE FROM entity_cross_references')

        # Insert exact matches
        inserted = 0
        for entity, sources in cross_referenced.items():
            normalized = self._normalize_name(entity)
            risk_level = self._assess_cross_reference_risk(sources)

            cursor.execute("""
                INSERT INTO entity_cross_references (
                    entity_name, normalized_name, source_count, sources,
                    match_type, risk_level, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entity,
                normalized,
                len(sources),
                ', '.join(sources),
                'EXACT',
                risk_level,
                datetime.now().isoformat()
            ))
            inserted += 1

        # Insert fuzzy matches
        for entity, sources in fuzzy_matches.items():
            normalized = self._normalize_name(entity)

            # Skip if already in exact matches
            if entity in cross_referenced:
                continue

            risk_level = self._assess_cross_reference_risk(sources)

            cursor.execute("""
                INSERT INTO entity_cross_references (
                    entity_name, normalized_name, source_count, sources,
                    match_type, risk_level, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entity,
                normalized,
                len(sources),
                ', '.join(sources),
                'FUZZY',
                risk_level,
                datetime.now().isoformat()
            ))
            inserted += 1

        conn.commit()
        conn.close()

        logger.info(f"Inserted {inserted} cross-referenced entities")
        return inserted

    def _assess_cross_reference_risk(self, sources):
        """Assess risk level based on source combination"""
        # High risk if in BIS list
        if 'BIS_Entity' in sources or 'BIS_Denied' in sources:
            return 'CRITICAL'

        # High risk if in 4+ sources
        if len(sources) >= 4:
            return 'HIGH'

        # Medium risk if in 3 sources
        if len(sources) == 3:
            return 'MEDIUM'

        # Low risk if in 2 sources
        return 'LOW'

    def generate_summary_report(self):
        """Generate summary report of cross-referenced entities"""
        logger.info("Generating summary report...")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        # Get statistics
        total = conn.execute('SELECT COUNT(*) FROM entity_cross_references').fetchone()[0]

        # By match type
        exact = conn.execute("SELECT COUNT(*) FROM entity_cross_references WHERE match_type = 'EXACT'").fetchone()[0]
        fuzzy = conn.execute("SELECT COUNT(*) FROM entity_cross_references WHERE match_type = 'FUZZY'").fetchone()[0]

        # By risk level
        critical = conn.execute("SELECT COUNT(*) FROM entity_cross_references WHERE risk_level = 'CRITICAL'").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM entity_cross_references WHERE risk_level = 'HIGH'").fetchone()[0]
        medium = conn.execute("SELECT COUNT(*) FROM entity_cross_references WHERE risk_level = 'MEDIUM'").fetchone()[0]
        low = conn.execute("SELECT COUNT(*) FROM entity_cross_references WHERE risk_level = 'LOW'").fetchone()[0]

        # By source count
        by_source_count = conn.execute("""
            SELECT source_count, COUNT(*) as count
            FROM entity_cross_references
            GROUP BY source_count
            ORDER BY source_count DESC
        """).fetchall()

        # Top entities
        top_entities = conn.execute("""
            SELECT entity_name, source_count, sources, risk_level
            FROM entity_cross_references
            ORDER BY source_count DESC, risk_level DESC
            LIMIT 20
        """).fetchall()

        conn.close()

        # Generate report
        report = f"""# Entity Cross-Reference Summary
**Generated:** {datetime.now().isoformat()}

## Overview

- **Total Cross-Referenced Entities:** {total:,}
- **Exact Matches:** {exact:,} ({exact/total*100 if total > 0 else 0:.1f}%)
- **Fuzzy Matches:** {fuzzy:,} ({fuzzy/total*100 if total > 0 else 0:.1f}%)

## Risk Distribution

| Risk Level | Count | Percentage |
|------------|-------|------------|
| CRITICAL | {critical:,} | {critical/total*100 if total > 0 else 0:.1f}% |
| HIGH | {high:,} | {high/total*100 if total > 0 else 0:.1f}% |
| MEDIUM | {medium:,} | {medium/total*100 if total > 0 else 0:.1f}% |
| LOW | {low:,} | {low/total*100 if total > 0 else 0:.1f}% |

## Source Count Distribution

| Sources | Entities |
|---------|----------|
"""

        for row in by_source_count:
            report += f"| {row['source_count']} | {row['count']:,} |\n"

        report += f"""
## Top 20 Cross-Referenced Entities

| Entity | Sources (#) | Source List | Risk |
|--------|-------------|-------------|------|
"""

        for entity in top_entities:
            report += f"| {entity['entity_name']} | {entity['source_count']} | {entity['sources']} | {entity['risk_level']} |\n"

        # Save report
        report_path = Path("C:/Projects/OSINT - Foresight/analysis/ENTITY_CROSS_REFERENCE_REPORT.md")
        report_path.write_text(report, encoding='utf-8')

        logger.info(f"Report saved to: {report_path}")
        return report

    def run(self):
        """Execute the cross-reference analysis"""
        logger.info("Starting entity cross-reference analysis...")

        # Find exact matches
        cross_referenced = self.find_cross_referenced_entities()

        # Find fuzzy matches
        fuzzy_matches = self.find_fuzzy_matches()

        # Create cross-reference table
        inserted = self.create_cross_reference_table(cross_referenced, fuzzy_matches)

        # Generate summary report
        report = self.generate_summary_report()

        logger.info(f"\n{'='*80}")
        logger.info(f"Entity Cross-Reference Analysis Complete")
        logger.info(f"{'='*80}")
        logger.info(f"Total cross-referenced entities: {inserted:,}")
        logger.info(f"Exact matches: {len(cross_referenced):,}")
        logger.info(f"Fuzzy matches: {len(fuzzy_matches):,}")
        logger.info(f"{'='*80}")

        return inserted


if __name__ == "__main__":
    cross_ref = EntityCrossReference()
    cross_ref.run()
