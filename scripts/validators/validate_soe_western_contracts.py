#!/usr/bin/env python3
"""
SOE Western Contract Cross-Reference Validator

Validates claims in the Historical SOE Database against actual contract data
from USAspending and TED databases.

Purpose:
- Verify US contract claims against USAspending database
- Verify EU contract claims against TED database
- Generate validation report with evidence/discrepancies

Author: OSINT Foresight Team
Date: 2025-10-22
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

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


class SOEContractValidator:
    """Cross-reference SOE contract claims with actual databases"""

    def __init__(self):
        """Initialize validator"""
        self.historical_data = None
        self.master_conn = None
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'entities_checked': 0,
            'us_claims_verified': 0,
            'us_claims_failed': 0,
            'eu_claims_verified': 0,
            'eu_claims_failed': 0,
            'detailed_findings': []
        }

    def load_historical_database(self):
        """Load historical SOE database"""
        logger.info(f"Loading historical database: {HISTORICAL_DB_PATH}")

        with open(HISTORICAL_DB_PATH, 'r', encoding='utf-8') as f:
            self.historical_data = json.load(f)

        logger.info(f"  [OK] Loaded {len(self.historical_data['entities'])} entities")

    def connect_master_database(self):
        """Connect to master warehouse database"""
        logger.info(f"Connecting to master database: {MASTER_DB_PATH}")

        if not MASTER_DB_PATH.exists():
            logger.error(f"  [ERROR] Master database not found at {MASTER_DB_PATH}")
            return False

        self.master_conn = sqlite3.connect(MASTER_DB_PATH)
        self.master_conn.row_factory = sqlite3.Row
        logger.info("  [OK] Connected to master database")
        return True

    def validate_us_contracts(self, entity: Dict) -> Dict:
        """Validate US contract claims for an entity"""
        entity_name = entity['common_name']
        logger.info(f"\n=== Validating US contracts for {entity_name} ===")

        western = entity.get('western_contracting', {})
        has_us_contracts = western.get('us_contracts', False)

        result = {
            'entity_id': entity['entity_id'],
            'entity_name': entity_name,
            'claim': 'has_us_contracts' if has_us_contracts else 'no_us_contracts',
            'verified': False,
            'actual_count': 0,
            'evidence': [],
            'discrepancy': None
        }

        if not has_us_contracts:
            logger.info("  [SKIP] No US contract claims to validate")
            return result

        # Search USAspending database for this entity
        cursor = self.master_conn.cursor()

        # Verify table exists and has data
        cursor.execute("""
            SELECT COUNT(*) FROM usaspending_china_comprehensive
        """)
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            logger.warning("  [WARNING] USAspending table is empty")
            result['discrepancy'] = "USAspending table has no data"
            return result

        logger.info(f"  [INFO] Searching USAspending ({row_count:,} total records)")

        # Search by common name and all aliases
        search_terms = [entity_name] + entity.get('aliases', [])

        for search_term in search_terms:
            # Clean Chinese characters from search
            if any('\u4e00' <= char <= '\u9fff' for char in search_term):
                continue

            cursor.execute("""
                SELECT
                    recipient_name,
                    COUNT(*) as contract_count,
                    SUM(CAST(federal_action_obligation AS REAL)) as total_value
                FROM usaspending_china_comprehensive
                WHERE recipient_name LIKE ?
                GROUP BY recipient_name
            """, (f'%{search_term}%',))

            rows = cursor.fetchall()
            for row in rows:
                result['actual_count'] += row['contract_count']
                result['evidence'].append({
                    'contractor_name': row['recipient_name'],
                    'contract_count': row['contract_count'],
                    'total_value': row['total_value'],
                    'matched_on': search_term,
                    'source_table': 'usaspending_china_comprehensive'
                })

        # Verify claim
        if result['actual_count'] > 0:
            result['verified'] = True
            logger.info(f"  [VERIFIED] Found {result['actual_count']} US contracts")
        else:
            result['verified'] = False
            result['discrepancy'] = f"Claimed US contracts but found 0 in USAspending database"
            logger.warning(f"  [FAILED] Claimed contracts but found none")

        return result

    def validate_eu_contracts(self, entity: Dict) -> Dict:
        """Validate EU contract claims for an entity"""
        entity_name = entity['common_name']
        logger.info(f"\n=== Validating EU contracts for {entity_name} ===")

        western = entity.get('western_contracting', {})
        has_eu_contracts = western.get('eu_contracts', False)

        result = {
            'entity_id': entity['entity_id'],
            'entity_name': entity_name,
            'claim': 'has_eu_contracts' if has_eu_contracts else 'no_eu_contracts',
            'verified': False,
            'actual_count': 0,
            'evidence': [],
            'discrepancy': None
        }

        if not has_eu_contracts:
            logger.info("  [SKIP] No EU contract claims to validate")
            return result

        # Search TED database for this entity
        cursor = self.master_conn.cursor()

        # Check if TED table exists and has data
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='ted_china_contracts_fixed'
        """)

        if not cursor.fetchone():
            logger.warning("  [WARNING] TED database table not found")
            result['discrepancy'] = "TED database table not found"
            return result

        # Verify table has data
        cursor.execute("SELECT COUNT(*) FROM ted_china_contracts_fixed")
        row_count = cursor.fetchone()[0]
        if row_count == 0:
            logger.warning("  [WARNING] TED table is empty")
            result['discrepancy'] = "TED table has no data"
            return result

        logger.info(f"  [INFO] Searching TED table ({row_count:,} total records)")

        # Search by common name and all aliases
        search_terms = [entity_name] + entity.get('aliases', [])

        for search_term in search_terms:
            # Clean Chinese characters from search
            if any('\u4e00' <= char <= '\u9fff' for char in search_term):
                continue

            # Search both supplier and buyer fields
            cursor.execute("""
                SELECT
                    supplier_name,
                    COUNT(*) as contract_count
                FROM ted_china_contracts_fixed
                WHERE (supplier_name LIKE ? OR buyer_name LIKE ?)
                  AND supplier_name IS NOT NULL
                GROUP BY supplier_name
            """, (f'%{search_term}%', f'%{search_term}%'))

            rows = cursor.fetchall()
            for row in rows:
                result['actual_count'] += row['contract_count']
                result['evidence'].append({
                    'contractor_name': row['supplier_name'],
                    'contract_count': row['contract_count'],
                    'matched_on': search_term,
                    'source_table': 'ted_china_contracts_fixed'
                })

        # Verify claim
        if result['actual_count'] > 0:
            result['verified'] = True
            logger.info(f"  [VERIFIED] Found {result['actual_count']} EU contracts")
        else:
            result['verified'] = False
            result['discrepancy'] = f"Claimed EU contracts but found 0 in TED database"
            logger.warning(f"  [FAILED] Claimed contracts but found none")

        return result

    def validate_all_entities(self):
        """Validate contract claims for all entities"""
        logger.info("\n" + "="*80)
        logger.info("VALIDATING SOE WESTERN CONTRACT CLAIMS")
        logger.info("="*80)

        if not self.connect_master_database():
            logger.error("Cannot proceed without master database")
            return

        for entity in self.historical_data['entities']:
            self.validation_results['entities_checked'] += 1

            # Validate US contracts
            us_result = self.validate_us_contracts(entity)
            if us_result['claim'] == 'has_us_contracts':
                if us_result['verified']:
                    self.validation_results['us_claims_verified'] += 1
                else:
                    self.validation_results['us_claims_failed'] += 1

            # Validate EU contracts
            eu_result = self.validate_eu_contracts(entity)
            if eu_result['claim'] == 'has_eu_contracts':
                if eu_result['verified']:
                    self.validation_results['eu_claims_verified'] += 1
                else:
                    self.validation_results['eu_claims_failed'] += 1

            # Store detailed findings
            self.validation_results['detailed_findings'].append({
                'entity_id': entity['entity_id'],
                'entity_name': entity['common_name'],
                'us_validation': us_result,
                'eu_validation': eu_result
            })

    def generate_report(self) -> str:
        """Generate validation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = ANALYSIS_DIR / f"soe_contract_validation_{timestamp}.json"

        logger.info(f"\n{'='*80}")
        logger.info("VALIDATION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Entities Checked: {self.validation_results['entities_checked']}")
        logger.info(f"\nUS Contracts:")
        logger.info(f"  Verified: {self.validation_results['us_claims_verified']}")
        logger.info(f"  Failed: {self.validation_results['us_claims_failed']}")
        logger.info(f"\nEU Contracts:")
        logger.info(f"  Verified: {self.validation_results['eu_claims_verified']}")
        logger.info(f"  Failed: {self.validation_results['eu_claims_failed']}")

        # Calculate verification rate
        total_claims = (
            self.validation_results['us_claims_verified'] +
            self.validation_results['us_claims_failed'] +
            self.validation_results['eu_claims_verified'] +
            self.validation_results['eu_claims_failed']
        )
        total_verified = (
            self.validation_results['us_claims_verified'] +
            self.validation_results['eu_claims_verified']
        )

        if total_claims > 0:
            verification_rate = (total_verified / total_claims) * 100
            logger.info(f"\nOverall Verification Rate: {verification_rate:.1f}%")

        # Write detailed report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)

        logger.info(f"\n  [OK] Detailed report saved: {report_path}")
        return str(report_path)

    def run_validation(self):
        """Run complete validation process"""
        self.load_historical_database()
        self.validate_all_entities()
        report_path = self.generate_report()

        if self.master_conn:
            self.master_conn.close()

        return report_path


def main():
    """Main execution"""
    validator = SOEContractValidator()
    report_path = validator.run_validation()

    print(f"\n{'='*80}")
    print("SOE WESTERN CONTRACT VALIDATION COMPLETE")
    print(f"{'='*80}")
    print(f"Report: {report_path}")
    print("\nNext steps:")
    print("1. Review detailed findings in the JSON report")
    print("2. Investigate any failed verifications")
    print("3. Update historical database with verified data")
    print("4. Add source provenance for verified contracts")


if __name__ == "__main__":
    main()
