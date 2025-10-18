#!/usr/bin/env python3
"""
Update TED Database with Refined Chinese Detection
Fixes the false positive problem in the original database
"""

import sqlite3
import json
from pathlib import Path
import time
from refined_chinese_detector import RefinedChineseDetector
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_ted_database():
    """Update TED database with refined Chinese detection"""
    detector = RefinedChineseDetector()
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add new columns for refined detection
    try:
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN refined_china_linked BOOLEAN DEFAULT 0')
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN refined_china_confidence REAL DEFAULT 0.0')
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN refined_china_evidence TEXT')
        cursor.execute('ALTER TABLE ted_china_contracts ADD COLUMN refined_detection_method TEXT')
        logger.info("Added new columns for refined detection")
    except sqlite3.OperationalError:
        logger.info("Columns already exist, continuing...")

    # Get all contracts that were previously marked as Chinese
    cursor.execute('''
        SELECT contract_id, contractor_name, contractor_country, contracting_authority
        FROM ted_china_contracts
        WHERE china_linked = 1
    ''')

    contracts = cursor.fetchall()
    total_contracts = len(contracts)
    logger.info(f"Processing {total_contracts} contracts previously marked as Chinese")

    # Statistics
    stats = {
        'processed': 0,
        'confirmed_chinese': 0,
        'false_positives_eliminated': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'by_method': {}
    }

    start_time = time.time()

    for i, (contract_id, contractor, country, authority) in enumerate(contracts):
        # Apply refined detection
        result = detector.detect_chinese_entity(contractor, country, authority)

        # Update database
        cursor.execute('''
            UPDATE ted_contracts
            SET refined_china_linked = ?,
                refined_china_confidence = ?,
                refined_china_evidence = ?,
                refined_detection_method = ?
            WHERE contract_id = ?
        ''', (
            result.is_chinese,
            result.confidence,
            json.dumps(result.evidence),
            result.method,
            contract_id
        ))

        # Update statistics
        stats['processed'] += 1

        if result.is_chinese:
            stats['confirmed_chinese'] += 1

            if result.confidence >= 0.9:
                stats['high_confidence'] += 1
            elif result.confidence >= 0.6:
                stats['medium_confidence'] += 1

            method = result.method
            stats['by_method'][method] = stats['by_method'].get(method, 0) + 1
        else:
            stats['false_positives_eliminated'] += 1

        # Progress update every 1000 contracts
        if (i + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            eta = (total_contracts - i - 1) / rate if rate > 0 else 0

            logger.info(f"Processed {i + 1}/{total_contracts} contracts "
                       f"({(i + 1)/total_contracts:.1%}) - "
                       f"ETA: {eta:.0f}s - "
                       f"Found {stats['confirmed_chinese']} Chinese entities")

    # Commit changes
    conn.commit()

    # Generate final statistics
    cursor.execute('''
        SELECT COUNT(*) FROM ted_china_contracts
        WHERE refined_china_linked = 1 AND refined_china_confidence >= 0.9
    ''')
    high_conf_total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*) FROM ted_china_contracts
        WHERE refined_china_linked = 1 AND refined_china_confidence >= 0.6
    ''')
    medium_conf_total = cursor.fetchone()[0]

    conn.close()

    # Final report
    elapsed_total = time.time() - start_time

    print("\n" + "="*60)
    print("TED DATABASE REFINEMENT COMPLETE")
    print("="*60)
    print(f"Processing time: {elapsed_total:.1f} seconds")
    print(f"Contracts processed: {stats['processed']:,}")
    print(f"")
    print(f"BEFORE REFINEMENT:")
    print(f"  Chinese-linked contracts: {total_contracts:,}")
    print(f"")
    print(f"AFTER REFINEMENT:")
    print(f"  Confirmed Chinese entities: {stats['confirmed_chinese']:,}")
    print(f"  High confidence (≥90%): {stats['high_confidence']:,}")
    print(f"  Medium confidence (≥60%): {stats['medium_confidence']:,}")
    print(f"  False positives eliminated: {stats['false_positives_eliminated']:,}")
    print(f"")
    print(f"ACCURACY IMPROVEMENT:")
    print(f"  False positive reduction: {stats['false_positives_eliminated']/total_contracts:.1%}")
    print(f"")
    print(f"DETECTION METHODS:")
    for method, count in stats['by_method'].items():
        print(f"  {method}: {count:,} entities")

    return stats

def generate_refined_analysis_report():
    """Generate analysis report with refined data"""
    db_path = "F:/OSINT_WAREHOUSE/osint_master.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    report = {
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'analysis_type': 'Refined Chinese Entity Detection',
        'database': db_path
    }

    # Overall statistics
    cursor.execute('SELECT COUNT(*) FROM ted_china_contracts')
    report['total_contracts'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM ted_china_contracts WHERE refined_china_linked = 1')
    report['refined_chinese_contracts'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM ted_china_contracts WHERE china_linked = 1')
    report['original_chinese_contracts'] = cursor.fetchone()[0]

    # Confidence breakdown
    cursor.execute('''
        SELECT
            SUM(CASE WHEN refined_china_confidence >= 0.9 THEN 1 ELSE 0 END) as high_conf,
            SUM(CASE WHEN refined_china_confidence >= 0.6 AND refined_china_confidence < 0.9 THEN 1 ELSE 0 END) as med_conf,
            SUM(CASE WHEN refined_china_confidence > 0 AND refined_china_confidence < 0.6 THEN 1 ELSE 0 END) as low_conf
        FROM ted_china_contracts
        WHERE refined_china_linked = 1
    ''')
    conf_data = cursor.fetchone()
    report['confidence_breakdown'] = {
        'high': conf_data[0] or 0,
        'medium': conf_data[1] or 0,
        'low': conf_data[2] or 0
    }

    # Detection methods
    cursor.execute('''
        SELECT refined_detection_method, COUNT(*) as count
        FROM ted_china_contracts
        WHERE refined_china_linked = 1
        GROUP BY refined_detection_method
        ORDER BY count DESC
    ''')
    report['detection_methods'] = [
        {'method': row[0], 'count': row[1]}
        for row in cursor.fetchall()
    ]

    # Top Chinese entities found
    cursor.execute('''
        SELECT contractor_name, contractor_country,
               refined_china_confidence, refined_detection_method,
               COUNT(*) as contracts
        FROM ted_china_contracts
        WHERE refined_china_linked = 1
        AND contractor_name IS NOT NULL
        GROUP BY contractor_name
        ORDER BY refined_china_confidence DESC, contracts DESC
        LIMIT 10
    ''')

    report['top_chinese_entities'] = []
    for row in cursor.fetchall():
        try:
            name_clean = row[0].encode('ascii', 'ignore').decode('ascii')[:80]
            report['top_chinese_entities'].append({
                'name': name_clean,
                'country': row[1] or 'Unknown',
                'confidence': row[2],
                'method': row[3],
                'contracts': row[4]
            })
        except:
            pass  # Skip encoding issues

    conn.close()

    # Save report
    report_path = Path("C:/Projects/OSINT - Foresight/analysis/refined_chinese_detection_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"Analysis report saved to {report_path}")
    return report

if __name__ == "__main__":
    logger.info("Starting TED database refinement with improved Chinese detection")

    # Update database
    stats = update_ted_database()

    # Generate analysis report
    logger.info("Generating refined analysis report")
    report = generate_refined_analysis_report()

    print(f"\nREFINED CHINESE ENTITIES FOUND:")
    for entity in report['top_chinese_entities']:
        print(f"- {entity['name']} ({entity['country']}) - "
              f"Conf: {entity['confidence']:.2f} via {entity['method']} - "
              f"{entity['contracts']} contracts")

    logger.info("TED database refinement complete")
