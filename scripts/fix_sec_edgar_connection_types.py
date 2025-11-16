#!/usr/bin/env python3
"""
Fix SEC_EDGAR Investment Analysis - Populate chinese_connection_type field
Based on actual company data and indicators

IMPORTANT: Taiwan (TW) is NOT China - this script explicitly separates them
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")


def populate_connection_types():
    """Populate chinese_connection_type in sec_edgar_investment_analysis"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    logger.info("Starting SEC_EDGAR connection type population...")

    # Get all records from investment_analysis
    records = conn.execute('''
        SELECT id, cik, company_name, ticker
        FROM sec_edgar_investment_analysis
        WHERE chinese_connection_type IS NULL
    ''').fetchall()

    logger.info(f"Found {len(records)} records to process")

    updates = 0
    mainland_china = 0
    hong_kong = 0
    taiwan = 0
    offshore_shell = 0
    chinese_investor = 0
    not_chinese = 0

    for record in records:
        cik = record['cik']
        company_name = record['company_name'] or ''

        connection_type = None

        # Check 1: Is company in sec_edgar_chinese table?
        chinese_company = conn.execute('''
            SELECT state, company_name FROM sec_edgar_chinese WHERE cik = ?
        ''', (cik,)).fetchone()

        if chinese_company:
            state = chinese_company['state']

            # Classify by state code
            if state == 'E9':
                connection_type = 'hong_kong_company'
                hong_kong += 1
            elif state == 'TW':
                connection_type = 'taiwan_company'  # SEPARATE FROM CHINA
                taiwan += 1
            elif state in ('K3', 'B9'):  # Cayman, other offshore
                connection_type = 'offshore_shell_company'
                offshore_shell += 1
            elif state in ('CN', 'Y6'):  # Mainland China
                connection_type = 'mainland_china_company'
                mainland_china += 1
            else:
                connection_type = 'chinese_related_company'
                chinese_investor += 1

        # Check 2: Is company marked is_chinese in companies table?
        if not connection_type:
            is_chinese = conn.execute('''
                SELECT is_chinese, state_of_incorporation, detection_reasons
                FROM sec_edgar_companies
                WHERE cik = ?
            ''', (cik,)).fetchone()

            if is_chinese and is_chinese['is_chinese'] == 1:
                state = is_chinese['state_of_incorporation']
                reasons = is_chinese['detection_reasons'] or ''

                # Check if Taiwan
                if state == 'TW' or 'taiwan' in reasons.lower():
                    connection_type = 'taiwan_company'  # NOT CHINA
                    taiwan += 1
                # Check if Hong Kong
                elif state == 'E9' or 'hong kong' in reasons.lower():
                    connection_type = 'hong_kong_company'
                    hong_kong += 1
                # Check if offshore
                elif state in ('K3', 'KY') or any(x in reasons.lower() for x in ['cayman', 'bermuda', 'bvi']):
                    connection_type = 'offshore_shell_company'
                    offshore_shell += 1
                # Otherwise mainland China
                else:
                    connection_type = 'mainland_china_company'
                    mainland_china += 1

        # Check 3: Check indicators table
        if not connection_type:
            indicators = conn.execute('''
                SELECT indicator_type, indicator_value
                FROM sec_edgar_chinese_indicators
                WHERE cik = ?
            ''', (cik,)).fetchall()

            if indicators:
                indicator_values = [i['indicator_value'].lower() for i in indicators]

                # Check for Taiwan indicators
                if any('taiwan' in v or v == 'tw' for v in indicator_values):
                    connection_type = 'taiwan_company'  # NOT CHINA
                    taiwan += 1
                # Check for Hong Kong
                elif any('hong kong' in v or v == 'hk' or v == 'e9' for v in indicator_values):
                    connection_type = 'hong_kong_company'
                    hong_kong += 1
                # Check for offshore
                elif any(x in ' '.join(indicator_values) for x in ['cayman', 'bermuda', 'bvi', 'ky', 'bm', 'vg']):
                    connection_type = 'offshore_shell_company'
                    offshore_shell += 1
                else:
                    connection_type = 'chinese_related_company'
                    chinese_investor += 1

        # Check 4: Name-based detection (as last resort)
        if not connection_type:
            name_lower = company_name.lower()

            # Taiwan keywords
            if any(x in name_lower for x in ['taiwan', 'taipei']):
                connection_type = 'taiwan_company'  # NOT CHINA
                taiwan += 1
            # Hong Kong keywords
            elif any(x in name_lower for x in ['hong kong', 'hk ltd']):
                connection_type = 'hong_kong_company'
                hong_kong += 1
            # Chinese keywords
            elif any(x in name_lower for x in ['china', 'chinese', 'beijing', 'shanghai', 'shenzhen',
                                                'guangzhou', 'hangzhou', 'wuhan', 'chengdu']):
                connection_type = 'mainland_china_company'
                mainland_china += 1

        # If still no connection, mark as not_chinese
        if not connection_type:
            connection_type = 'not_chinese_related'
            not_chinese += 1

        # Update the record
        conn.execute('''
            UPDATE sec_edgar_investment_analysis
            SET chinese_connection_type = ?,
                analysis_notes = 'Auto-populated by fix_sec_edgar_connection_types.py on ' || ?
            WHERE id = ?
        ''', (connection_type, datetime.now().isoformat(), record['id']))

        updates += 1

        if updates % 50 == 0:
            logger.info(f"  Processed {updates}/{len(records)} records...")

    conn.commit()
    conn.close()

    logger.info(f"\nProcessing complete!")
    logger.info(f"  Total updates: {updates}")
    logger.info(f"  Mainland China: {mainland_china}")
    logger.info(f"  Hong Kong: {hong_kong}")
    logger.info(f"  Taiwan: {taiwan} (SEPARATE from China)")
    logger.info(f"  Offshore shells: {offshore_shell}")
    logger.info(f"  Chinese-related: {chinese_investor}")
    logger.info(f"  Not Chinese: {not_chinese}")

    return {
        'total': updates,
        'mainland_china': mainland_china,
        'hong_kong': hong_kong,
        'taiwan': taiwan,
        'offshore_shell': offshore_shell,
        'chinese_investor': chinese_investor,
        'not_chinese': not_chinese
    }


def verify_taiwan_separation():
    """Verify that Taiwan companies are NOT marked as mainland China"""

    conn = sqlite3.connect(DB_PATH)

    logger.info("\nVerifying Taiwan vs China separation...")

    # Check for any Taiwan companies incorrectly marked as mainland_china
    incorrect = conn.execute('''
        SELECT company_name, cik, chinese_connection_type
        FROM sec_edgar_investment_analysis
        WHERE (company_name LIKE '%Taiwan%' OR company_name LIKE '%Taipei%')
          AND chinese_connection_type = 'mainland_china_company'
    ''').fetchall()

    if incorrect:
        logger.warning(f"  WARNING: Found {len(incorrect)} Taiwan companies marked as mainland China!")
        for row in incorrect:
            logger.warning(f"    {row[0]} ({row[1]}) - {row[2]}")
    else:
        logger.info(f"  [OK] No Taiwan companies incorrectly marked as China")

    # Show Taiwan classification
    taiwan_count = conn.execute('''
        SELECT COUNT(*) FROM sec_edgar_investment_analysis
        WHERE chinese_connection_type = 'taiwan_company'
    ''').fetchone()[0]

    logger.info(f"  Taiwan companies properly classified: {taiwan_count}")

    conn.close()


if __name__ == "__main__":
    print("="*70)
    print("SEC_EDGAR CONNECTION TYPE FIX")
    print("="*70)
    print("\nIMPORTANT: Taiwan (TW) is NOT China - separate classification")
    print("")

    results = populate_connection_types()
    verify_taiwan_separation()

    print("\n" + "="*70)
    print("SUMMARY:")
    print(f"  Mainland China companies: {results['mainland_china']}")
    print(f"  Hong Kong companies: {results['hong_kong']}")
    print(f"  Taiwan companies: {results['taiwan']} (SEPARATE from China)")
    print(f"  Offshore shell companies: {results['offshore_shell']}")
    print(f"  Chinese-related: {results['chinese_investor']}")
    print(f"  Not Chinese-related: {results['not_chinese']}")
    print("="*70)
