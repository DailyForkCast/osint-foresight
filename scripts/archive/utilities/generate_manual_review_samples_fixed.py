#!/usr/bin/env python3
"""
Generate Manual Review Samples for Detection Accuracy Validation - FIXED

Handles schema differences across three formats:
- 101-column: highest_confidence='HIGH' (text), award_amount
- 305-column: highest_confidence=0.9 (numeric), award_amount
- 206-column: highest_confidence='HIGH' (text), federal_action_obligation
"""

import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime


def map_numeric_confidence(value):
    """Map numeric confidence to text level."""
    if value is None:
        return 'UNKNOWN'
    try:
        val = float(value)
        if val >= 0.85:
            return 'HIGH'
        elif val >= 0.70:
            return 'MEDIUM'
        else:
            return 'LOW'
    except:
        return str(value)  # Already text


def generate_samples():
    """Generate stratified random samples for manual review."""

    db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")
    output_dir = Path("C:/Projects/OSINT - Foresight/analysis/manual_review")
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    print("="*100)
    print("MANUAL REVIEW SAMPLE GENERATION")
    print("="*100)
    print(f"Database: {db_path}")
    print(f"Output: {output_dir}")
    print()

    # Configuration for each format (schema-aware)
    formats = [
        {
            'name': '101-column',
            'table': 'usaspending_china_101',
            'amount_field': 'award_amount',
            'confidence_is_numeric': False
        },
        {
            'name': '305-column',
            'table': 'usaspending_china_305',
            'amount_field': 'award_amount',
            'confidence_is_numeric': True
        },
        {
            'name': '206-column',
            'table': 'usaspending_china_comprehensive',
            'amount_field': 'federal_action_obligation',
            'confidence_is_numeric': False
        }
    ]

    all_samples = []
    summary = {
        'generation_date': datetime.now().isoformat(),
        'total_samples': 0,
        'by_format': {}
    }

    for format_config in formats:
        format_name = format_config['name']
        table = format_config['table']
        amount_field = format_config['amount_field']
        conf_is_numeric = format_config['confidence_is_numeric']

        print(f"\n{'='*100}")
        print(f"SAMPLING: {format_name}")
        print(f"{'='*100}")

        # Get total count
        cursor = conn.execute(f"SELECT COUNT(*) as total FROM {table}")
        total_count = cursor.fetchone()['total']

        print(f"Total records: {total_count:,}")

        # Determine sample size (proportional, but minimum 50)
        if total_count < 100:
            sample_size = total_count  # Take all if < 100
        elif total_count < 1000:
            sample_size = 50
        elif total_count < 10000:
            sample_size = 75
        else:
            sample_size = 100

        print(f"Sample size: {sample_size}")

        # Sample records randomly (no stratification since confidence types differ)
        print(f"Sampling {sample_size} random records...")

        cursor = conn.execute(f"""
            SELECT * FROM {table}
            ORDER BY RANDOM()
            LIMIT ?
        """, (sample_size,))

        samples = cursor.fetchall()
        print(f"  Retrieved: {len(samples)} samples")

        for sample in samples:
            # Convert to dict and add metadata
            sample_dict = dict(sample)
            sample_dict['format'] = format_name
            sample_dict['amount_field_name'] = amount_field

            # Normalize confidence to text
            if conf_is_numeric:
                orig_conf = sample_dict.get('highest_confidence')
                sample_dict['highest_confidence_numeric'] = orig_conf
                sample_dict['highest_confidence'] = map_numeric_confidence(orig_conf)

            # Add unified amount field
            sample_dict['review_amount'] = sample_dict.get(amount_field, 0)

            # Parse JSON fields
            for field in ['detection_details', 'detection_types']:
                if field in sample_dict and sample_dict[field]:
                    try:
                        sample_dict[f'{field}_parsed'] = json.loads(sample_dict[field])
                    except:
                        sample_dict[f'{field}_parsed'] = sample_dict[field]

            all_samples.append(sample_dict)

        # Get actual confidence distribution
        if conf_is_numeric:
            cursor = conn.execute(f"""
                SELECT
                    SUM(CASE WHEN highest_confidence >= 0.85 THEN 1 ELSE 0 END) as high_conf,
                    SUM(CASE WHEN highest_confidence >= 0.70 AND highest_confidence < 0.85 THEN 1 ELSE 0 END) as med_conf,
                    SUM(CASE WHEN highest_confidence < 0.70 THEN 1 ELSE 0 END) as low_conf
                FROM {table}
            """)
        else:
            cursor = conn.execute(f"""
                SELECT
                    COUNT(CASE WHEN highest_confidence = 'HIGH' THEN 1 END) as high_conf,
                    COUNT(CASE WHEN highest_confidence = 'MEDIUM' THEN 1 END) as med_conf,
                    COUNT(CASE WHEN highest_confidence = 'LOW' THEN 1 END) as low_conf
                FROM {table}
            """)

        stats = cursor.fetchone()

        summary['by_format'][format_name] = {
            'total_population': total_count,
            'samples_generated': len(samples),
            'confidence_distribution': {
                'HIGH': stats['high_conf'],
                'MEDIUM': stats['med_conf'],
                'LOW': stats['low_conf']
            }
        }

        print(f"  Population confidence: HIGH={stats['high_conf']:,}, MED={stats['med_conf']:,}, LOW={stats['low_conf']:,}")
        print(f"Total samples for {format_name}: {len(samples)}")

    summary['total_samples'] = len(all_samples)

    print(f"\n{'='*100}")
    print("SAMPLE GENERATION COMPLETE")
    print(f"{'='*100}")
    print(f"Total samples generated: {len(all_samples)}")
    print()

    # Save as JSON (full detail)
    json_output = output_dir / f"manual_review_samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_output, 'w') as f:
        json.dump({
            'summary': summary,
            'samples': all_samples
        }, f, indent=2)
    print(f"JSON output: {json_output}")

    # Save as CSV (for manual review in Excel)
    csv_output = output_dir / f"manual_review_samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

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
                'review_id': f"REVIEW_{i:04d}",
                'format': sample.get('format', ''),
                'transaction_id': sample.get('transaction_id', ''),
                'recipient_name': sample.get('recipient_name', ''),
                'recipient_country': sample.get('recipient_country_name', '') or sample.get('recipient_country', ''),
                'pop_country': sample.get('pop_country_name', '') or sample.get('pop_country', ''),
                'sub_awardee_country': sample.get('sub_awardee_country', ''),
                'award_amount': sample.get('review_amount', 0),
                'award_description': (sample.get('award_description', '') or '')[:200],  # Truncate
                'action_date': sample.get('action_date', ''),
                'highest_confidence': sample.get('highest_confidence', ''),
                'detection_types': sample.get('detection_types', ''),
                'awarding_agency': sample.get('awarding_agency', '') or sample.get('funding_agency_code', ''),
                'TRUE_POSITIVE': '',  # Empty for manual entry
                'CONFIDENCE_SCORE': '',  # Empty for manual entry
                'NOTES': ''  # Empty for manual entry
            }
            writer.writerow(row)

    print(f"CSV output: {csv_output}")

    # Save summary
    summary_output = output_dir / "sample_generation_summary.json"
    with open(summary_output, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary: {summary_output}")

    conn.close()

    # Also create instructions
    create_review_instructions(output_dir)

    return len(all_samples), csv_output


def create_review_instructions(output_dir):
    """Create instructions document for manual review."""

    instructions_path = output_dir / "REVIEW_INSTRUCTIONS.md"

    instructions = """# Manual Review Instructions

## Purpose
Validate detection accuracy by manually reviewing randomly sampled transactions to calculate precision (false positive rate).

**Goal:** Achieve >95% precision to establish confidence in detection methodology.

## Files
- **CSV File:** `manual_review_samples_[timestamp].csv` - Open in Excel
- **Sample Count:** Varies by format (50-100 per format based on population size)

## Review Process

### For Each Row, Answer:

**"Is this transaction genuinely China (PRC) related?"**

### Fill in THREE Columns:

1. **TRUE_POSITIVE**
   - `YES` = Correctly detected (true positive)
   - `NO` = Incorrectly detected (false positive)
   - `UNCERTAIN` = Cannot determine

2. **CONFIDENCE_SCORE** (1-5 scale)
   - `5` = Absolutely China-related
   - `4` = Very likely China-related
   - `3` = Probably China-related
   - `2` = Probably NOT China-related
   - `1` = Definitely NOT China-related

3. **NOTES**
   - Explain reasoning, especially for NO and UNCERTAIN

## Classification Guidelines

### TRUE POSITIVE (YES) Examples:

1. **Direct PRC Entity**
   ```
   Recipient: CHINA MOBILE COMMUNICATIONS
   Country: CHINA
   → YES (5) - Chinese state-owned enterprise
   ```

2. **PRC Geographic Location**
   ```
   Recipient: MIT
   Recipient Country: USA
   POP Country: CHINA
   → YES (4) - US entity performing work in China
   ```

3. **Hong Kong**
   ```
   Recipient: HONG KONG UNIVERSITY
   Country: HONG KONG
   → YES (4) - Hong Kong is part of PRC sphere
   ```

4. **Taiwan → China (Per Policy)**
   ```
   Recipient: TAIWAN RESEARCH INSTITUTE
   Recipient Country: TAIWAN
   POP Country: CHINA
   → YES (4) - Cross-strait activity
   ```

5. **Indirect Connection**
   ```
   Recipient: US COMPANY
   Sub-Awardee Country: China
   → YES (3) - Money flows to Chinese sub-contractor
   ```

### FALSE POSITIVE (NO) Examples:

1. **Name Confusion**
   ```
   Recipient: HOMER LAUGHLIN CHINA COMPANY
   Country: USA
   → NO (1) - "China" refers to porcelain dishes, not PRC
   ```

2. **Geographic Name (Not PRC)**
   ```
   Recipient: BEIJING STREET CORPORATION
   Country: USA
   → NO (1) - "Beijing" is street name, US company
   ```

3. **Taiwan Only (No PRC Connection)**
   ```
   Recipient: TAIWAN SEMICONDUCTOR
   Country: TAIWAN
   POP Country: TAIWAN
   → NO (1) - Taiwan only, no mainland China involvement
   ```

### UNCERTAIN Examples:

1. **Insufficient Information**
   ```
   Recipient: GLOBAL CONSORTIUM
   Country: USA
   Description: "International collaboration"
   → UNCERTAIN (3) - Could involve China, unclear
   ```

## Review Tips

### Check These Fields:

1. **recipient_country** - Where is recipient based?
2. **pop_country** - Where is work performed?
3. **sub_awardee_country** - Who is subcontractor?
4. **detection_types** - How was this detected?
5. **award_description** - What is this for?

### Detection Type Meaning:

- `["country"]` = Detected by country code/name (high precision)
- `["chinese_name_recipient"]` = Detected by name pattern (lower precision)
- `["pop_country_china"]` = Place of Performance in China
- `["entity_name"]` = Known Chinese entity (high precision)

### Taiwan Policy:

**Taiwan recipient + China POP = TRUE POSITIVE**
- Tracks cross-strait economic activity
- This is intentional, not an error

**Taiwan alone (no China POP) = FALSE POSITIVE**
- Taiwan ≠ PRC

## Time Estimate

- ~2 minutes per transaction
- Total time varies by sample count
- Can be done in multiple sessions

## When Complete

Save CSV file as: `manual_review_samples_[timestamp]_COMPLETED.csv`

The system will calculate:
- Precision = YES / (YES + NO)
- Confidence distribution
- False positive patterns

## Questions?

See: `analysis/TAIWAN_POLICY_FINAL_DECISION.md`
"""

    with open(instructions_path, 'w') as f:
        f.write(instructions)

    print(f"\nReview instructions: {instructions_path}")


if __name__ == '__main__':
    print("\n" + "="*100)
    print("STARTING MANUAL REVIEW SAMPLE GENERATION")
    print("="*100 + "\n")

    # Generate samples
    sample_count, csv_file = generate_samples()

    print("\n" + "="*100)
    print("GENERATION COMPLETE")
    print("="*100)
    print(f"\nSamples generated: {sample_count}")
    print(f"CSV file: {csv_file}")
    print(f"\nNext step: Open CSV file and begin manual review.")
    print("="*100 + "\n")
