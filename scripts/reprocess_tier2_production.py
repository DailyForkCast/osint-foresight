#!/usr/bin/env python3
"""
reprocess_tier2_production.py - Full TIER_2 Reprocessing (Production)

Reprocesses all 166,557 USAspending records with improved TIER_2 logic:
- Word boundary enforcement (fixes Kachina, Facchina)
- Porcelain/tableware false positives
- Country code validation
- Product origin detection
- Biotech/pharma/laser tier upgrades
- Supply chain separation

IMPORTANT: Creates backups before modifying data.

Usage:
    python reprocess_tier2_production.py --execute

Estimated time: 8-10 hours for 166K records
"""

import sqlite3
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
import time

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

class Tier2ProductionReprocessor:
    """Production TIER_2 reprocessing with all improvements"""

    # Copy logic from test script
    FALSE_POSITIVE_PATTERNS = {
        'substring_china': [
            r'\bkachina\b',
            r'\bcatalina\s+china\b',
            r'\bfacchina\b',
        ],
        'porcelain_tableware': [
            r'\bchina\s+porcelain\b', r'\bfine\s+china\b', r'\bbone\s+china\b',
            r'\bchina\s+dinnerware\b', r'\bchina\s+dishes\b', r'\bchina\s+plates\b',
            r'\bchina\s+cabinet\b', r'\bchina\s+glassware\b', r'\bchina\s+tableware\b',
            r'\broyal\s+china\b', r'\blenox\s+china\b', r'\bwedgwood\s+china\b',
            r'\bmikasa\s+china\b', r'\bnoritake\s+china\b',
        ],
        'us_locations': [r'\bchina\s+grove\b', r'\bchina\s+lake\b', r'\bchina\s+spring\b'],
        'casino_hotel': [r'\bcasino\b', r'\bresort\b', r'\bhotel\b', r'\bgaming\s+corporation\b', r'\bharrahs\b', r'\bboyd\s+gaming\b'],
        'insurance': [r'\binsurance\s+company\b', r'\blife\s+insurance\b'],
        'italian_companies': [r'\bsoc\s+coop\s+livornese\b', r'\bfacchinaggi\b'],
        'recreational': [r'\bskydive\b'],
        'us_consulting': [r'\bmsd\s+biztech\b', r'\brushinov\b'],
    }

    BIOTECH_PHARMA_INDICATORS = [
        'pharmaron', 'chempartner', 'wuxi', 'biologics', 'pharma',
        'drug development', 'medicine technology', 'clinical research',
        'cro', 'cdmo', 'pharmaceutical', 'therapeutics'
    ]

    LASER_OPTICS_INDICATORS = [
        'laser', 'optics', 'photonics', 'optical', 'electro-optical',
        'infrared', 'lidar', 'fiber optic'
    ]

    SEVEN_SONS_UNIVERSITIES = [
        r'beijing institute of technology', r'beihang', r'beijing university of aeronautics',
        r'harbin engineering university', r'harbin institute of technology',
        r'nanjing.*aeronautics', r'nanjing.*science.*technology',
        r'northwestern polytechnical', r'national university of defense'
    ]

    SUPPLY_CHAIN_ENTITIES = [
        'lenovo', 'huawei technologies usa', 'zte corporation',
        'tp-link', 'haier', 'hisense', 'tcl', 'xiaomi'
    ]

    def __init__(self, db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'total_records': 0,
            'tier2_original': 0,
            'false_positives_removed': 0,
            'tier_upgrades': 0,
            'supply_chain_moved': 0,
            'tier2_final': 0,
            'processing_time': 0
        }
        self.changes_log = []

    def connect_db(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"[OK] Connected to: {self.db_path}")

    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")

    def backup_table(self, table_name):
        """Create backup of table before modification"""
        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)

        backup_name = f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        safe_backup = validate_sql_identifier(backup_name)

        cursor = self.conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {safe_backup}")
        cursor.execute(f"CREATE TABLE {safe_backup} AS SELECT * FROM {safe_table}")
        self.conn.commit()

        # Get record count
        cursor.execute(f"SELECT COUNT(*) FROM {safe_backup}")
        count = cursor.fetchone()[0]

        print(f"[OK] Backup created: {backup_name} ({count:,} records)")
        return backup_name

    def is_false_positive(self, entity_name, vendor_name, description):
        """Check false positive patterns"""
        text = f"{entity_name} {vendor_name} {description}".lower()
        for category, patterns in self.FALSE_POSITIVE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True, category
        return False, None

    def is_product_origin_only(self, description):
        """Check if product origin, not entity"""
        if not description or pd.isna(description):
            return False
        text = str(description).lower()
        origin_patterns = [
            r'(made|manufactured|produced|fabricated|assembled)\s+(in|from)\s+china',
            r'(shipped|sent|delivered)\s+(from|out of)\s+china',
            r'(import|imported)\s+(from|out of)\s+china',
            r'country\s+of\s+origin:\s*china',
            r'product\s+of\s+china',
        ]
        return any(re.search(p, text, re.I) for p in origin_patterns)

    def check_tier_upgrade(self, entity_name, description):
        """Check tier upgrade to TIER_1"""
        text = f"{entity_name} {description}".lower()

        if any(ind in text for ind in self.BIOTECH_PHARMA_INDICATORS):
            return 'TIER_1', 'BIOTECH_PHARMA'
        if any(ind in text for ind in self.LASER_OPTICS_INDICATORS):
            return 'TIER_1', 'LASER_OPTICS'
        if any(re.search(uni, text, re.I) for uni in self.SEVEN_SONS_UNIVERSITIES):
            return 'TIER_1', 'SEVEN_SONS'
        return None, None

    def is_supply_chain(self, entity_name):
        """Check supply chain entity"""
        return any(s in str(entity_name).lower() for s in self.SUPPLY_CHAIN_ENTITIES)

    def validate_country_code(self, entity_name, country_code):
        """Validate country code matches entity"""
        if country_code not in ['CHN', 'HKG']:
            return True
        indicators = [
            r'\bbeijing\b', r'\bshanghai\b', r'\bshenzhen\b', r'\bguangzhou\b',
            r'\bhong\s*kong\b', r'\bchina\b', r'\bchinese\b', r'\bprc\b'
        ]
        return any(re.search(ind, str(entity_name), re.I) for ind in indicators)

    def reprocess_table(self, table_name, recipient_col, vendor_col, description_col, country_col):
        """Reprocess a single table"""
        print(f"\n{'='*60}")
        print(f"REPROCESSING: {table_name}")
        print(f"{'='*60}")

        # SECURITY: Validate table name before use in SQL
        safe_table = validate_sql_identifier(table_name)

        # Create backup
        backup_name = self.backup_table(table_name)

        # Get current TIER_2 records
        query = f"""
        SELECT * FROM {safe_table}
        WHERE importance_tier = 'TIER_2'
        """

        df = pd.read_sql(query, self.conn)
        original_tier2_count = len(df)
        self.stats['tier2_original'] += original_tier2_count

        print(f"[OK] Found {original_tier2_count:,} TIER_2 records")

        # Process each record
        cursor = self.conn.cursor()
        batch_size = 1000
        processed = 0
        removed_ids = []
        upgraded_ids = []
        supply_chain_ids = []

        start_time = time.time()

        for idx, row in df.iterrows():
            entity_name = str(row.get(recipient_col, ''))
            vendor_name = str(row.get(vendor_col, ''))
            description = str(row.get(description_col, ''))
            country_code = str(row.get(country_col, ''))
            record_id = row.get('id') or row.get('transaction_id')

            # Check false positive
            is_fp, fp_category = self.is_false_positive(entity_name, vendor_name, description)
            if is_fp:
                removed_ids.append((record_id, fp_category))
                self.stats['false_positives_removed'] += 1
                continue

            # Check product origin only
            if self.is_product_origin_only(description):
                if not re.search(r'\bchina\b', entity_name, re.I):
                    removed_ids.append((record_id, 'product_origin'))
                    self.stats['false_positives_removed'] += 1
                    continue

            # Check country code validation
            if not self.validate_country_code(entity_name, country_code):
                removed_ids.append((record_id, 'country_mismatch'))
                self.stats['false_positives_removed'] += 1
                continue

            # Check tier upgrade
            new_tier, upgrade_cat = self.check_tier_upgrade(entity_name, description)
            if new_tier == 'TIER_1':
                upgraded_ids.append((record_id, upgrade_cat))
                self.stats['tier_upgrades'] += 1
                continue

            # Check supply chain
            if self.is_supply_chain(entity_name):
                supply_chain_ids.append(record_id)
                self.stats['supply_chain_moved'] += 1
                continue

            processed += 1
            if processed % batch_size == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed
                remaining = (original_tier2_count - processed) / rate if rate > 0 else 0
                print(f"  Progress: {processed:,}/{original_tier2_count:,} ({processed/original_tier2_count*100:.1f}%) | {rate:.0f} rec/sec | ETA: {remaining/60:.0f}min")

        # Apply changes to database
        print(f"\n[OK] Processing complete. Applying changes...")

        # Delete false positives
        if removed_ids:
            ids_to_remove = [str(r[0]) for r in removed_ids]
            placeholders = ','.join(['?' for _ in ids_to_remove])
            id_field = 'id' if 'id' in df.columns else 'transaction_id'
            # SECURITY: Validate column name before use in SQL
            safe_id_field = validate_sql_identifier(id_field)
            cursor.execute(f"DELETE FROM {safe_table} WHERE {safe_id_field} IN ({placeholders})", ids_to_remove)
            print(f"[OK] Removed {len(removed_ids):,} false positives")

        # Upgrade to TIER_1
        if upgraded_ids:
            for record_id, category in upgraded_ids:
                id_field = 'id' if 'id' in df.columns else 'transaction_id'
                # SECURITY: Validate column name before use in SQL
                safe_id_field = validate_sql_identifier(id_field)
                cursor.execute(f"""
                    UPDATE {safe_table}
                    SET importance_tier = 'TIER_1',
                        importance_score = 0.9,
                        commodity_type = ?
                    WHERE {safe_id_field} = ?
                """, (category, record_id))
            print(f"[OK] Upgraded {len(upgraded_ids):,} records to TIER_1")

        # Move to supply chain (mark for now, can extract later)
        if supply_chain_ids:
            id_field = 'id' if 'id' in df.columns else 'transaction_id'
            # SECURITY: Validate column name before use in SQL
            safe_id_field = validate_sql_identifier(id_field)
            placeholders = ','.join(['?' for _ in supply_chain_ids])
            cursor.execute(f"""
                UPDATE {safe_table}
                SET commodity_type = 'SUPPLY_CHAIN'
                WHERE {safe_id_field} IN ({placeholders})
            """, supply_chain_ids)
            print(f"[OK] Marked {len(supply_chain_ids):,} as supply chain")

        self.conn.commit()

        # Final stats for this table
        cursor.execute(f"SELECT COUNT(*) FROM {safe_table} WHERE importance_tier = 'TIER_2'")
        final_tier2 = cursor.fetchone()[0]
        self.stats['tier2_final'] += final_tier2

        print(f"\n[RESULTS]")
        print(f"  Original TIER_2: {original_tier2_count:,}")
        print(f"  Removed: {len(removed_ids):,}")
        print(f"  Upgraded: {len(upgraded_ids):,}")
        print(f"  Supply Chain: {len(supply_chain_ids):,}")
        print(f"  Final TIER_2: {final_tier2:,}")
        print(f"  Reduction: {original_tier2_count - final_tier2:,} ({(original_tier2_count-final_tier2)/original_tier2_count*100:.1f}%)")

        return {
            'table': table_name,
            'original_tier2': original_tier2_count,
            'removed': len(removed_ids),
            'upgraded': len(upgraded_ids),
            'supply_chain': len(supply_chain_ids),
            'final_tier2': final_tier2,
            'backup': backup_name
        }

    def reprocess_all_tables(self):
        """Reprocess all three USAspending tables"""
        print("\n" + "="*60)
        print("TIER_2 PRODUCTION REPROCESSING - FULL DATASET")
        print("="*60)
        print(f"Database: {self.db_path}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = time.time()

        results = []

        # Table 1: 305-column (159,513 records - 95.8%)
        print("\n[1/3] Processing 305-column table...")
        r1 = self.reprocess_table(
            'usaspending_china_305',
            'recipient_name',
            'vendor_name',
            'award_description',
            'pop_country_code'
        )
        results.append(r1)

        # Table 2: 101-column (5,108 records - 3.1%)
        print("\n[2/3] Processing 101-column table...")
        r2 = self.reprocess_table(
            'usaspending_china_101',
            'recipient_name',
            'vendor_name',
            'award_description',
            'place_of_performance_country_code'
        )
        results.append(r2)

        # Table 3: comprehensive (1,936 records - 1.2%)
        print("\n[3/3] Processing comprehensive table...")
        r3 = self.reprocess_table(
            'usaspending_china_comprehensive',
            'recipient_name',
            'vendor_name',
            'award_description',
            'pop_country_code'
        )
        results.append(r3)

        self.stats['processing_time'] = time.time() - start_time

        return results

    def generate_final_report(self, table_results, output_dir="analysis"):
        """Generate comprehensive final report"""
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Compile full report
        report = {
            'timestamp': timestamp,
            'database': self.db_path,
            'statistics': self.stats,
            'table_results': table_results
        }

        # Save JSON
        json_path = Path(output_dir) / f"tier2_production_reprocessing_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "="*60)
        print("TIER_2 REPROCESSING - FINAL REPORT")
        print("="*60)

        print(f"\nProcessing Time: {self.stats['processing_time']/3600:.2f} hours")
        print(f"\nOverall Statistics:")
        print(f"  Original TIER_2: {self.stats['tier2_original']:,}")
        print(f"  False Positives Removed: {self.stats['false_positives_removed']:,} ({self.stats['false_positives_removed']/self.stats['tier2_original']*100:.1f}%)")
        print(f"  Upgraded to TIER_1: {self.stats['tier_upgrades']:,} ({self.stats['tier_upgrades']/self.stats['tier2_original']*100:.1f}%)")
        print(f"  Moved to Supply Chain: {self.stats['supply_chain_moved']:,} ({self.stats['supply_chain_moved']/self.stats['tier2_original']*100:.1f}%)")
        print(f"  Final TIER_2: {self.stats['tier2_final']:,} ({self.stats['tier2_final']/self.stats['tier2_original']*100:.1f}%)")

        print(f"\nBy Table:")
        for r in table_results:
            print(f"\n  {r['table']}:")
            print(f"    Original: {r['original_tier2']:,}")
            print(f"    Removed: {r['removed']:,}")
            print(f"    Upgraded: {r['upgraded']:,}")
            print(f"    Supply Chain: {r['supply_chain']:,}")
            print(f"    Final: {r['final_tier2']:,}")
            print(f"    Backup: {r['backup']}")

        print("\n" + "="*60)
        print(f"[SUCCESS] Report saved: {json_path}")
        print("="*60)

        return json_path

def main():
    import argparse

    parser = argparse.ArgumentParser(description='TIER_2 Production Reprocessing')
    parser.add_argument('--execute', action='store_true',
                       help='Execute reprocessing (required for safety)')
    parser.add_argument('--db',
                       default='F:/OSINT_WAREHOUSE/osint_master.db',
                       help='Database path')

    args = parser.parse_args()

    if not args.execute:
        print("ERROR: Must specify --execute flag to run production reprocessing")
        print("This is a safety check to prevent accidental execution.")
        print("\nUsage: python reprocess_tier2_production.py --execute")
        return

    print("="*60)
    print("TIER_2 PRODUCTION REPROCESSING")
    print("="*60)
    print("\nModifying production database...")
    print("Backups will be created automatically.")
    print("\nEstimated time: 8-10 hours for 166K records")
    print("\nStarting reprocessing...")

    reprocessor = Tier2ProductionReprocessor(db_path=args.db)
    reprocessor.connect_db()

    try:
        results = reprocessor.reprocess_all_tables()
        reprocessor.generate_final_report(results)
    finally:
        reprocessor.close_db()

    print("\n[SUCCESS] TIER_2 reprocessing complete!")

if __name__ == "__main__":
    main()
