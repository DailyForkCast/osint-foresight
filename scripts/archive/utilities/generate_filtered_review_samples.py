#!/usr/bin/env python3
"""
Generate Filtered Manual Review Samples - Excluding Known False Positives

Generates 300 random samples (100 per format) while excluding:
- San Antonio organizations
- COSCO Fire Protection
- Homer Laughlin China Company
- Italian surnames (facchinaggi, etc.)

This provides a cleaner sample for assessing precision of remaining detections.
"""

import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime


def has_false_positive_pattern(row_dict):
    """Check if record matches any known false positive pattern."""

    # Get all name fields (case-insensitive)
    recipient_name = (row_dict.get('recipient_name') or '').lower()
    sub_awardee_name = (row_dict.get('sub_awardee_name') or '').lower()
    vendor_name = (row_dict.get('vendor_name') or '').lower()
    description = (row_dict.get('award_description') or '').lower()

    # Combine all searchable text
    all_text = f"{recipient_name} {sub_awardee_name} {vendor_name}"

    # Known false positive patterns (from manual review rounds 1, 2, 3 & 4)
    false_positive_patterns = [
        # Round 1: Original patterns
        'san antonio',
        'homer laughlin',
        'cosco fire protection',
        'facchinaggi',
        'facchin',
        'vecchini',
        'zecchin',
        'china porcelain',
        'fine china',
        'bone china',

        # Round 2: Additional patterns from filtered sample review
        'antonio',  # Matches "J Antonio Inc", "Galleria Antonio", etc.
        'milenio',  # Spanish word (Los Bebes del Milenio)
        'alibaba kitchen',  # Local kitchen/bath store (not Chinese Alibaba)
        'alibaba bath',
        'jusino',  # Spanish surnames
        'berrios',
        'tonchala',  # Hotel Tonchala Casino (Colombian)
        'glassware',  # "United Glassware & China" (porcelain context)
        'cosco, inc',  # US company (not COSCO shipping)

        # Round 3: More Alibaba variants and trust names
        'alibaba lighting',  # Alibaba Lighting And Furnitures Inc (local store)
        'alibaba furnitures',
        'haier trust',  # Eula A Haier Trust (personal trust, not Haier company)

        # Round 4: Entity name substring false positives
        'comac pump',  # Comac Pump & Well LLC (not COMAC aircraft)
        'comac well',
        'aztec environmental',  # Aztec Environmental (not ZTE)
        'ezteq',  # EZ Tech company
        't k c enterprises',  # T K C Enterprises (41 false positives)
        'tkc enterprises',
        'mavich',  # Mavich LLC (contains "avic")
        'vista gorgonio',  # Vista Gorgonio Inc
        'pri/djv',  # PRI/DJI Construction JV (not DJI drones)
        "avic's travel",  # Avic's Travel LLC (not AVIC)
    ]

    for pattern in false_positive_patterns:
        if pattern in all_text:
            return True

    # Description-based exclusions
    description_exclusions = [
        'ethnic tibet',  # Humanitarian aid to Tibetan people (71 records)
        'support to ethnic',  # General humanitarian aid
        # NOTE: "made in china" NOT excluded - keeping per Option B (separate category)
    ]

    for pattern in description_exclusions:
        if pattern in description:
            return True

    # NOTE: "Economic Injury Disaster Grant" records are KEPT in sample
    # NOTE: "made in China" records are KEPT per Option B (will be categorized separately)
    # User wants to review these, but they are likely false positives
    # (Small business disaster relief, not China-related)

    return False


def generate_filtered_samples():
    """Generate stratified random samples excluding known false positives."""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    output_dir = Path("C:/Projects/OSINT - Foresight/analysis/manual_review")
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print("="*100)
    print("FILTERED MANUAL REVIEW SAMPLE GENERATION - ROUND 4")
    print("="*100)
    print(f"Database: {db_path}")
    print(f"Output: {output_dir}")
    print("\nExcluding known false positive patterns (Rounds 1-4):")
    print("  Round 1 patterns:")
    print("    - San Antonio organizations")
    print("    - COSCO Fire Protection")
    print("    - Homer Laughlin China Company")
    print("    - Italian surnames (facchinaggi, etc.)")
    print("  Round 2 patterns:")
    print("    - Antonio/Milenio (Spanish names with 'nio')")
    print("    - Alibaba kitchen/bath (local stores)")
    print("    - Spanish surnames (Jusino, Berrios)")
    print("    - Glassware/china (porcelain context)")
    print("    - COSCO, Inc. (US company variant)")
    print("  Round 3 patterns:")
    print("    - Alibaba lighting/furnitures (more local store variants)")
    print("    - Haier Trust (personal trusts, not Haier company)")
    print("  Round 4 patterns:")
    print("    - COMAC Pump/Well, Aztec Environmental, EZTEQ (entity substring matches)")
    print("    - T K C Enterprises (41 records, 'made in China' products)")
    print("    - Mavich, Vista Gorgonio, PRI/DJI, Avic's Travel")
    print("    - 'Ethnic Tibet' descriptions (71 records, humanitarian aid)")
    print("\nNOTE: Economic Injury Disaster Grant records are KEPT in sample")
    print("NOTE: 'Made in China' product records are KEPT per Option B (separate category)")
    print("      (Will distinguish China-sourced products from Chinese entities)")
    print()

    # Configuration for each format
    formats = [
        {
            'name': '101-column',
            'table': 'usaspending_china_101',
            'amount_field': 'award_amount',
            'confidence_is_numeric': False,
            'target_samples': 100
        },
        {
            'name': '305-column',
            'table': 'usaspending_china_305',
            'amount_field': 'award_amount',
            'confidence_is_numeric': True,
            'target_samples': 100
        },
        {
            'name': '206-column',
            'table': 'usaspending_china_comprehensive',
            'amount_field': 'federal_action_obligation',
            'confidence_is_numeric': False,
            'target_samples': 100
        }
    ]

    all_samples = []
    summary = {
        'generation_date': datetime.now().isoformat(),
        'total_samples': 0,
        'filtering_applied': True,
        'by_format': {}
    }

    for format_config in formats:
        format_name = format_config['name']
        table = format_config['table']
        amount_field = format_config['amount_field']
        conf_is_numeric = format_config['confidence_is_numeric']
        target_samples = format_config['target_samples']

        print(f"\n{'='*100}")
        print(f"SAMPLING: {format_name}")
        print(f"{'='*100}")

        # Get total count
        cursor = conn.execute(f"SELECT COUNT(*) as total FROM {table}")
        total_count = cursor.fetchone()['total']
        print(f"Total records in table: {total_count:,}")

        # Get ALL records (we'll filter in Python)
        # Request more than needed to account for filtering
        oversample_factor = 3  # Get 3x records to ensure we get enough after filtering

        cursor = conn.execute(f"""
            SELECT * FROM {table}
            ORDER BY RANDOM()
            LIMIT ?
        """, (target_samples * oversample_factor,))

        candidate_records = cursor.fetchall()
        print(f"Retrieved {len(candidate_records):,} candidate records")

        # Filter out false positives
        filtered_samples = []
        filtered_count = 0

        for record in candidate_records:
            record_dict = dict(record)

            if has_false_positive_pattern(record_dict):
                filtered_count += 1
                continue

            # Add metadata
            record_dict['format'] = format_name
            record_dict['amount_field_name'] = amount_field

            # Normalize confidence to text
            if conf_is_numeric:
                orig_conf = record_dict.get('highest_confidence')
                record_dict['highest_confidence_numeric'] = orig_conf

                # Map numeric to text
                if orig_conf is not None:
                    try:
                        val = float(orig_conf)
                        if val >= 0.85:
                            record_dict['highest_confidence'] = 'HIGH'
                        elif val >= 0.70:
                            record_dict['highest_confidence'] = 'MEDIUM'
                        else:
                            record_dict['highest_confidence'] = 'LOW'
                    except:
                        record_dict['highest_confidence'] = 'UNKNOWN'

            # Add unified amount field
            record_dict['review_amount'] = record_dict.get(amount_field, 0)

            filtered_samples.append(record_dict)

            # Stop when we have enough
            if len(filtered_samples) >= target_samples:
                break

        print(f"  Filtered out: {filtered_count} false positive patterns")
        print(f"  Clean samples collected: {len(filtered_samples)}")

        if len(filtered_samples) < target_samples:
            print(f"  WARNING: Only got {len(filtered_samples)} of target {target_samples}")
            print(f"           (Most detections may be false positives!)")

        all_samples.extend(filtered_samples[:target_samples])

        summary['by_format'][format_name] = {
            'total_population': total_count,
            'candidates_retrieved': len(candidate_records),
            'filtered_out': filtered_count,
            'samples_generated': len(filtered_samples[:target_samples])
        }

    summary['total_samples'] = len(all_samples)

    print(f"\n{'='*100}")
    print("FILTERED SAMPLE GENERATION COMPLETE")
    print(f"{'='*100}")
    print(f"Total clean samples generated: {len(all_samples)}")
    print()

    # Save as CSV (for manual review in Excel)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_output = output_dir / f"filtered_review_samples_{timestamp}.csv"

    # Define CSV fields
    fieldnames = [
        'review_id',
        'format',
        'transaction_id',
        'recipient_name',
        'recipient_country',
        'pop_country',
        'sub_awardee_country',
        'award_amount',
        'award_description',
        'action_date',
        'highest_confidence',
        'detection_types',
        'awarding_agency',
        'TRUE_POSITIVE',  # For manual entry
        'CONFIDENCE_SCORE',  # For manual entry (1-5)
        'NOTES'  # For manual entry
    ]

    with open(csv_output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for i, sample in enumerate(all_samples, 1):
            row = {
                'review_id': f"FILTERED_{i:04d}",
                'format': sample.get('format', ''),
                'transaction_id': sample.get('transaction_id', ''),
                'recipient_name': sample.get('recipient_name', ''),
                'recipient_country': sample.get('recipient_country_name', '') or sample.get('recipient_country', ''),
                'pop_country': sample.get('pop_country_name', '') or sample.get('pop_country', ''),
                'sub_awardee_country': sample.get('sub_awardee_country', ''),
                'award_amount': sample.get('review_amount', 0),
                'award_description': (sample.get('award_description', '') or '')[:200],
                'action_date': sample.get('action_date', ''),
                'highest_confidence': sample.get('highest_confidence', ''),
                'detection_types': sample.get('detection_types', ''),
                'awarding_agency': sample.get('awarding_agency', '') or sample.get('funding_agency_code', ''),
                'TRUE_POSITIVE': '',
                'CONFIDENCE_SCORE': '',
                'NOTES': ''
            }
            writer.writerow(row)

    print(f"CSV output: {csv_output}")

    # Save summary
    summary_output = output_dir / f"filtered_sample_summary_{timestamp}.json"
    with open(summary_output, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary: {summary_output}")

    conn.close()

    return len(all_samples), csv_output


if __name__ == '__main__':
    print("\n" + "="*100)
    print("STARTING FILTERED MANUAL REVIEW SAMPLE GENERATION")
    print("="*100 + "\n")

    sample_count, csv_file = generate_filtered_samples()

    print("\n" + "="*100)
    print("GENERATION COMPLETE - ROUND 4 FILTERED SAMPLES")
    print("="*100)
    print(f"\nClean samples generated: {sample_count}")
    print(f"CSV file: {csv_file}")
    print(f"\nNext step: Open CSV file and continue manual review.")
    print("These samples exclude ALL known false positive patterns from Rounds 1-4.")
    print("NOTE: Economic Injury Disaster Grant records are included for review.")
    print("NOTE: 'Made in China' product records are included (Option B - separate category).")
    print("="*100 + "\n")
