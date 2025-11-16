#!/usr/bin/env python3
"""
Verify XML format consistency across all TED years
Sample one file from each year to understand format changes
"""

import tarfile
import logging
from pathlib import Path
from datetime import datetime
from lxml import etree
import sys

# Setup logging
log_file = Path("C:/Projects/OSINT - Foresight/logs") / f"ted_format_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

ARCHIVE_DIR = Path("F:/TED_Data/monthly")
TEMP_BASE = Path("C:/Projects/OSINT - Foresight/data/temp/format_check")
TEMP_BASE.mkdir(parents=True, exist_ok=True)

def check_xml_format(xml_path, year):
    """Analyze XML structure and identify format"""
    try:
        tree = etree.parse(str(xml_path))
        root = tree.getroot()

        # Get root element and namespace
        root_tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        namespace = root.tag.split('}')[0][1:] if '}' in root.tag else None

        logger.info(f"\n{'='*80}")
        logger.info(f"YEAR {year}: {xml_path.name}")
        logger.info(f"{'='*80}")
        logger.info(f"Root element: {root_tag}")
        logger.info(f"Namespace: {namespace}")

        # Check for different formats
        if 'TED_EXPORT' in root_tag or namespace == 'http://publications.europa.eu/TED_schema/Export':
            logger.info("Format: OLD TED EXPORT (pre-2020)")

            # Check for ECONOMIC_OPERATOR
            ns = {'ted': 'http://publications.europa.eu/TED_schema/Export'}
            operators = root.findall('.//ted:ECONOMIC_OPERATOR_NAME_ADDRESS', ns)
            logger.info(f"  ECONOMIC_OPERATOR sections: {len(operators)}")

            if operators:
                # Show structure of first operator
                op = operators[0]
                logger.info("  Structure:")
                contact = op.find('ted:CONTACT_DATA_WITHOUT_RESPONSIBLE_NAME', ns)
                if contact is not None:
                    org = contact.find('ted:ORGANISATION', ns)
                    if org is not None:
                        name = org.find('ted:OFFICIALNAME', ns)
                        if name is not None:
                            logger.info(f"    Path: ECONOMIC_OPERATOR -> CONTACT_DATA -> ORGANISATION -> OFFICIALNAME")
                            logger.info(f"    Sample: {name.text[:50] if name.text else 'Empty'}")
                        else:
                            logger.info("    ERROR: OFFICIALNAME not found")
                    else:
                        logger.info("    ERROR: ORGANISATION not found")
                else:
                    logger.info("    ERROR: CONTACT_DATA not found")

        elif 'ContractAwardNotice' in root_tag or 'ContractNotice' in root_tag:
            logger.info("Format: NEW eFORMS (post-2019)")

            # Different structure for eForms
            # Try to find economic operator in new format
            ns = {
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
            }

            parties = root.findall('.//cac:Party', ns)
            logger.info(f"  cac:Party sections: {len(parties)}")

            if parties:
                logger.info("  Structure:")
                party = parties[0]
                party_name = party.find('.//cbc:Name', ns)
                if party_name is not None:
                    logger.info(f"    Path: cac:Party -> cbc:Name")
                    logger.info(f"    Sample: {party_name.text[:50] if party_name.text else 'Empty'}")

        else:
            logger.info(f"Format: UNKNOWN - Root: {root_tag}")

        return {
            'year': year,
            'root_tag': root_tag,
            'namespace': namespace,
            'format': 'old' if 'TED_EXPORT' in root_tag else 'new' if 'Notice' in root_tag else 'unknown'
        }

    except Exception as e:
        logger.error(f"  Failed to parse: {e}")
        return None

def sample_year(year):
    """Extract and check one XML file from given year"""
    # Find first archive from this year
    year_dir = ARCHIVE_DIR / str(year)
    if not year_dir.exists():
        logger.warning(f"Year {year} directory not found")
        return None

    archives = list(year_dir.glob("TED_monthly_*.tar.gz"))
    if not archives:
        logger.warning(f"No archives found for year {year}")
        return None

    # Use first month
    archive = archives[0]
    logger.info(f"\nSampling {archive.name}...")

    archive_temp = TEMP_BASE / f"year_{year}"
    archive_temp.mkdir(exist_ok=True)

    try:
        # Extract monthly archive
        with tarfile.open(archive, 'r:gz', errorlevel=0) as tar:
            # Get first member
            members = tar.getmembers()
            if members:
                tar.extract(members[0], archive_temp)

        # Find first daily archive
        daily_archives = list(archive_temp.rglob("*.tar.gz"))
        if not daily_archives:
            logger.warning(f"  No daily archives found")
            return None

        daily_archive = daily_archives[0]
        daily_temp = TEMP_BASE / f"daily_{year}"
        daily_temp.mkdir(exist_ok=True)

        # Extract daily archive
        with tarfile.open(daily_archive, 'r:gz', errorlevel=0) as tar:
            # Get first member
            members = tar.getmembers()
            if members:
                tar.extract(members[0], daily_temp)

        # Find first XML file
        xml_files = list(daily_temp.rglob("*.xml"))
        if not xml_files:
            logger.warning(f"  No XML files found")
            return None

        # Analyze XML
        return check_xml_format(xml_files[0], year)

    except Exception as e:
        logger.error(f"  Failed to extract: {e}")
        return None

def main():
    """Sample XML files from each year to identify format changes"""
    logger.info("="*80)
    logger.info("TED XML FORMAT VERIFICATION")
    logger.info("="*80)

    # Sample years from 2006 to 2025
    results = []
    for year in range(2006, 2026):
        result = sample_year(year)
        if result:
            results.append(result)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("SUMMARY")
    logger.info("="*80)

    old_format_years = [r['year'] for r in results if r['format'] == 'old']
    new_format_years = [r['year'] for r in results if r['format'] == 'new']
    unknown_years = [r['year'] for r in results if r['format'] == 'unknown']

    logger.info(f"\nOLD FORMAT (TED_EXPORT): {len(old_format_years)} years")
    if old_format_years:
        logger.info(f"  Years: {min(old_format_years)}-{max(old_format_years)}")
        logger.info(f"  List: {', '.join(map(str, old_format_years))}")

    logger.info(f"\nNEW FORMAT (eForms): {len(new_format_years)} years")
    if new_format_years:
        logger.info(f"  Years: {min(new_format_years)}-{max(new_format_years)}")
        logger.info(f"  List: {', '.join(map(str, new_format_years))}")

    if unknown_years:
        logger.info(f"\nUNKNOWN FORMAT: {len(unknown_years)} years")
        logger.info(f"  Years: {', '.join(map(str, unknown_years))}")

    # Save results
    import json
    report_path = Path("C:/Projects/OSINT - Foresight/analysis/ted_format_analysis.json")
    with open(report_path, 'w') as f:
        json.dump({
            'old_format_years': old_format_years,
            'new_format_years': new_format_years,
            'unknown_years': unknown_years,
            'details': results
        }, f, indent=2)

    logger.info(f"\nReport saved: {report_path}")

    # Recommendations
    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATIONS")
    logger.info("="*80)
    if old_format_years and new_format_years:
        logger.info(f"⚠ Multiple formats detected!")
        logger.info(f"  Need TWO different extraction strategies:")
        logger.info(f"    1. OLD format ({min(old_format_years)}-{max(old_format_years)}): ECONOMIC_OPERATOR_NAME_ADDRESS path")
        logger.info(f"    2. NEW format ({min(new_format_years)}-{max(new_format_years)}): cac:Party path")
    elif old_format_years:
        logger.info(f"✓ Single format (OLD) across all years")
        logger.info(f"  Use ECONOMIC_OPERATOR_NAME_ADDRESS extraction")
    elif new_format_years:
        logger.info(f"✓ Single format (NEW) across all years")
        logger.info(f"  Use cac:Party extraction")

if __name__ == '__main__':
    main()
