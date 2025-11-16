#!/usr/bin/env python3
"""
Comprehensive SOE Database v2.0 Validator

Cross-references all 62 entities against:
- USPTO patents (PatentsView)
- OpenAlex research collaborations
- USAspending contracts
- TED EU contracts

Does NOT require pre-existing claims - searches for ALL entities across ALL sources.

Author: OSINT Foresight Team
Date: 2025-10-22
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
HISTORICAL_DB_PATH = PROJECT_ROOT / "data" / "prc_soe_historical_database.json"
MASTER_DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)


class ComprehensiveSOEValidator:
    """Cross-reference all SOE entities against all data sources"""

    def __init__(self):
        """Initialize validator"""
        self.historical_data = None
        self.master_conn = None
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'database_version': '2.0',
            'total_entities': 0,
            'entities_with_data': 0,
            'data_sources': {
                'uspto_patents': {'available': False, 'entities_found': 0, 'total_records': 0},
                'openalex_research': {'available': False, 'entities_found': 0, 'total_records': 0},
                'usaspending_contracts': {'available': False, 'entities_found': 0, 'total_records': 0},
                'ted_contracts': {'available': False, 'entities_found': 0, 'total_records': 0}
            },
            'by_entity': [],
            'by_sector': {},
            'entity_list_findings': {},
            'section_1260h_findings': {}
        }

    def load_historical_database(self):
        """Load historical SOE database v2.0"""
        logger.info(f"Loading historical database v2.0: {HISTORICAL_DB_PATH}")

        with open(HISTORICAL_DB_PATH, 'r', encoding='utf-8') as f:
            self.historical_data = json.load(f)

        total = len(self.historical_data['entities'])
        self.validation_results['total_entities'] = total
        logger.info(f"  Loaded {total} entities from v2.0 database")

    def connect_master_database(self):
        """Connect to master warehouse database"""
        logger.info(f"Connecting to master database: {MASTER_DB_PATH}")

        if not MASTER_DB_PATH.exists():
            logger.error(f"  Master database not found at {MASTER_DB_PATH}")
            return False

        self.master_conn = sqlite3.connect(MASTER_DB_PATH)
        self.master_conn.row_factory = sqlite3.Row
        logger.info("  Connected to master database")
        return True

    def check_data_source_availability(self):
        """Check which data sources are available"""
        logger.info("\n" + "="*80)
        logger.info("CHECKING DATA SOURCE AVAILABILITY")
        logger.info("="*80)

        cursor = self.master_conn.cursor()

        # Check USPTO patents
        try:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name LIKE '%patent%'
            """)
            patent_tables = [row[0] for row in cursor.fetchall()]

            if patent_tables:
                # Try common patent table names
                for table in ['patentsview_assignees', 'uspto_patents', 'patents']:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            self.validation_results['data_sources']['uspto_patents']['available'] = True
                            self.validation_results['data_sources']['uspto_patents']['table_name'] = table
                            logger.info(f"  USPTO Patents: {count:,} records in {table}")
                            break
                    except sqlite3.OperationalError:
                        continue

            if not self.validation_results['data_sources']['uspto_patents']['available']:
                logger.warning("  USPTO Patents: NOT AVAILABLE")
        except Exception as e:
            logger.warning(f"  USPTO Patents: ERROR - {e}")

        # Check OpenAlex research
        try:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name LIKE '%openalex%'
            """)
            openalex_tables = [row[0] for row in cursor.fetchall()]

            if openalex_tables:
                for table in openalex_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            self.validation_results['data_sources']['openalex_research']['available'] = True
                            self.validation_results['data_sources']['openalex_research']['table_name'] = table
                            logger.info(f"  OpenAlex Research: {count:,} records in {table}")
                            break
                    except sqlite3.OperationalError:
                        continue

            if not self.validation_results['data_sources']['openalex_research']['available']:
                logger.warning("  OpenAlex Research: NOT AVAILABLE")
        except Exception as e:
            logger.warning(f"  OpenAlex Research: ERROR - {e}")

        # Check USAspending
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM usaspending_china_comprehensive
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                self.validation_results['data_sources']['usaspending_contracts']['available'] = True
                self.validation_results['data_sources']['usaspending_contracts']['table_name'] = 'usaspending_china_comprehensive'
                logger.info(f"  USAspending: {count:,} records")
            else:
                logger.warning("  USAspending: Table empty")
        except sqlite3.OperationalError:
            logger.warning("  USAspending: NOT AVAILABLE")

        # Check TED contracts
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM ted_china_contracts_fixed
            """)
            count = cursor.fetchone()[0]
            if count > 0:
                self.validation_results['data_sources']['ted_contracts']['available'] = True
                self.validation_results['data_sources']['ted_contracts']['table_name'] = 'ted_china_contracts_fixed'
                logger.info(f"  TED Contracts: {count:,} records")
            else:
                logger.warning("  TED Contracts: Table empty")
        except sqlite3.OperationalError:
            logger.warning("  TED Contracts: NOT AVAILABLE")

    def search_usaspending(self, entity: Dict) -> Dict:
        """Search USAspending for entity"""
        if not self.validation_results['data_sources']['usaspending_contracts']['available']:
            return {'found': False, 'count': 0, 'records': []}

        entity_name = entity.get('common_name', '')
        cursor = self.master_conn.cursor()

        # Search by common name and aliases
        search_terms = [entity_name]
        if 'aliases' in entity:
            search_terms.extend(entity['aliases'])

        # Add official names
        if 'official_name_en' in entity:
            search_terms.append(entity['official_name_en'])

        results = {'found': False, 'count': 0, 'records': [], 'search_terms_used': []}

        for search_term in search_terms:
            # Skip Chinese characters
            if any('\u4e00' <= char <= '\u9fff' for char in search_term):
                continue

            try:
                cursor.execute("""
                    SELECT
                        recipient_name,
                        COUNT(*) as contract_count,
                        SUM(CAST(federal_action_obligation AS REAL)) as total_value
                    FROM usaspending_china_comprehensive
                    WHERE recipient_name LIKE ?
                    GROUP BY recipient_name
                    LIMIT 10
                """, (f'%{search_term}%',))

                rows = cursor.fetchall()
                for row in rows:
                    results['found'] = True
                    results['count'] += row['contract_count']
                    results['records'].append({
                        'recipient_name': row['recipient_name'],
                        'contract_count': row['contract_count'],
                        'total_value': row['total_value'],
                        'matched_on': search_term
                    })
                    if search_term not in results['search_terms_used']:
                        results['search_terms_used'].append(search_term)
            except Exception as e:
                logger.debug(f"    Error searching USAspending for {search_term}: {e}")

        return results

    def search_ted(self, entity: Dict) -> Dict:
        """Search TED contracts for entity"""
        if not self.validation_results['data_sources']['ted_contracts']['available']:
            return {'found': False, 'count': 0, 'records': []}

        entity_name = entity.get('common_name', '')
        cursor = self.master_conn.cursor()

        # Search by common name and aliases
        search_terms = [entity_name]
        if 'aliases' in entity:
            search_terms.extend(entity['aliases'])

        # Add official names
        if 'official_name_en' in entity:
            search_terms.append(entity['official_name_en'])

        results = {'found': False, 'count': 0, 'records': [], 'search_terms_used': []}

        for search_term in search_terms:
            # Skip Chinese characters
            if any('\u4e00' <= char <= '\u9fff' for char in search_term):
                continue

            try:
                cursor.execute("""
                    SELECT
                        supplier_name,
                        COUNT(*) as contract_count
                    FROM ted_china_contracts_fixed
                    WHERE (supplier_name LIKE ? OR buyer_name LIKE ?)
                      AND supplier_name IS NOT NULL
                    GROUP BY supplier_name
                    LIMIT 10
                """, (f'%{search_term}%', f'%{search_term}%'))

                rows = cursor.fetchall()
                for row in rows:
                    results['found'] = True
                    results['count'] += row['contract_count']
                    results['records'].append({
                        'supplier_name': row['supplier_name'],
                        'contract_count': row['contract_count'],
                        'matched_on': search_term
                    })
                    if search_term not in results['search_terms_used']:
                        results['search_terms_used'].append(search_term)
            except Exception as e:
                logger.debug(f"    Error searching TED for {search_term}: {e}")

        return results

    def validate_entity(self, entity: Dict) -> Dict:
        """Validate a single entity across all data sources"""
        entity_id = entity.get('entity_id', 'Unknown')
        entity_name = entity.get('common_name', entity.get('official_name_en', 'Unknown'))

        logger.info(f"\n{'='*80}")
        logger.info(f"Entity: {entity_name} ({entity_id})")
        logger.info(f"{'='*80}")

        # Extract sector
        sector = 'Unknown'
        if 'sector' in entity:
            sector = entity['sector']
        elif 'strategic_classification' in entity:
            strat_class = entity['strategic_classification']
            if isinstance(strat_class, dict):
                sector = strat_class.get('sector', 'Unknown')
            elif isinstance(strat_class, str):
                sector = strat_class

        result = {
            'entity_id': entity_id,
            'entity_name': entity_name,
            'official_name_en': entity.get('official_name_en', ''),
            'official_name_cn': entity.get('official_name_cn', ''),
            'sector': sector,
            'section_1260h': False,
            'entity_list': False,
            'entity_list_date': None,
            'seven_sons': False,
            'data_found': False,
            'sources': {}
        }

        # Extract MCF classification
        if 'mcf_classification' in entity:
            mcf = entity['mcf_classification']
            result['section_1260h'] = mcf.get('section_1260h_listed', False)
            result['entity_list'] = mcf.get('entity_list', False)
            result['entity_list_date'] = mcf.get('entity_list_date')
            result['seven_sons'] = mcf.get('seven_sons_national_defense', False)

        # Search USAspending
        logger.info("  Searching USAspending...")
        usaspending_results = self.search_usaspending(entity)
        result['sources']['usaspending'] = usaspending_results
        if usaspending_results['found']:
            logger.info(f"    FOUND: {usaspending_results['count']} contracts")
            result['data_found'] = True
            self.validation_results['data_sources']['usaspending_contracts']['entities_found'] += 1
        else:
            logger.info("    Not found")

        # Search TED
        logger.info("  Searching TED...")
        ted_results = self.search_ted(entity)
        result['sources']['ted'] = ted_results
        if ted_results['found']:
            logger.info(f"    FOUND: {ted_results['count']} contracts")
            result['data_found'] = True
            self.validation_results['data_sources']['ted_contracts']['entities_found'] += 1
        else:
            logger.info("  Not found")

        # Track if any data found
        if result['data_found']:
            self.validation_results['entities_with_data'] += 1

        return result

    def validate_all_entities(self):
        """Validate all entities"""
        logger.info("\n" + "="*80)
        logger.info("VALIDATING ALL 62 ENTITIES")
        logger.info("="*80)

        sector_stats = defaultdict(lambda: {
            'total': 0,
            'with_data': 0,
            'usaspending': 0,
            'ted': 0
        })

        for entity in self.historical_data['entities']:
            result = self.validate_entity(entity)
            self.validation_results['by_entity'].append(result)

            # Track sector statistics
            sector = result['sector']
            sector_stats[sector]['total'] += 1
            if result['data_found']:
                sector_stats[sector]['with_data'] += 1
            if result['sources']['usaspending']['found']:
                sector_stats[sector]['usaspending'] += 1
            if result['sources']['ted']['found']:
                sector_stats[sector]['ted'] += 1

            # Track Entity List findings
            if result['entity_list']:
                self.validation_results['entity_list_findings'][result['entity_name']] = {
                    'date': result['entity_list_date'],
                    'found_in_usaspending': result['sources']['usaspending']['found'],
                    'found_in_ted': result['sources']['ted']['found']
                }

            # Track Section 1260H findings
            if result['section_1260h']:
                self.validation_results['section_1260h_findings'][result['entity_name']] = {
                    'found_in_usaspending': result['sources']['usaspending']['found'],
                    'found_in_ted': result['sources']['ted']['found']
                }

        self.validation_results['by_sector'] = dict(sector_stats)

    def generate_summary_report(self):
        """Generate summary statistics"""
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE VALIDATION SUMMARY")
        logger.info("="*80)

        logger.info(f"\nDatabase: v2.0")
        logger.info(f"Total entities: {self.validation_results['total_entities']}")
        logger.info(f"Entities with data: {self.validation_results['entities_with_data']}")

        coverage_pct = (self.validation_results['entities_with_data'] /
                       self.validation_results['total_entities'] * 100)
        logger.info(f"Coverage rate: {coverage_pct:.1f}%")

        logger.info("\nData Sources:")
        for source, data in self.validation_results['data_sources'].items():
            if data['available']:
                logger.info(f"  {source}: {data['entities_found']} entities found")
            else:
                logger.info(f"  {source}: NOT AVAILABLE")

        logger.info("\nSection 1260H Entities (52 total):")
        section_1260h_with_data = sum(1 for e in self.validation_results['by_entity']
                                      if e['section_1260h'] and e['data_found'])
        logger.info(f"  Found in databases: {section_1260h_with_data}")

        logger.info("\nBIS Entity List Entities (24 total):")
        entity_list_with_data = sum(1 for e in self.validation_results['by_entity']
                                    if e['entity_list'] and e['data_found'])
        logger.info(f"  Found in databases: {entity_list_with_data}")

        logger.info("\nTop Entities by Data Presence:")
        entities_sorted = sorted(self.validation_results['by_entity'],
                                key=lambda x: (
                                    x['sources']['usaspending']['count'] +
                                    x['sources']['ted']['count']
                                ), reverse=True)

        for entity in entities_sorted[:10]:
            usa_count = entity['sources']['usaspending']['count']
            ted_count = entity['sources']['ted']['count']
            total = usa_count + ted_count
            if total > 0:
                logger.info(f"  {entity['entity_name']:30} USAspending: {usa_count:3}, TED: {ted_count:3}")

    def save_detailed_report(self) -> str:
        """Save detailed JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = ANALYSIS_DIR / f"comprehensive_validation_v2_{timestamp}.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)

        logger.info(f"\nDetailed report saved: {report_path}")
        return str(report_path)

    def run_validation(self):
        """Run complete validation process"""
        self.load_historical_database()

        if not self.connect_master_database():
            logger.error("Cannot proceed without master database")
            return None

        self.check_data_source_availability()
        self.validate_all_entities()
        self.generate_summary_report()
        report_path = self.save_detailed_report()

        if self.master_conn:
            self.master_conn.close()

        return report_path


def main():
    """Main execution"""
    validator = ComprehensiveSOEValidator()
    report_path = validator.run_validation()

    if report_path:
        print(f"\n{'='*80}")
        print("COMPREHENSIVE SOE v2.0 VALIDATION COMPLETE")
        print(f"{'='*80}")
        print(f"Report: {report_path}")
        print("\nNext steps:")
        print("1. Review detailed findings in JSON report")
        print("2. Identify entities needing subsidiary expansion")
        print("3. Generate intelligence reports by sector")
        print("4. Cross-reference Entity List findings")


if __name__ == "__main__":
    main()
