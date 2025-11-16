#!/usr/bin/env python3
"""
Generate Manual Review Samples for Detection Accuracy Validation

Creates stratified random samples from each format for manual precision review.
Goal: 100 samples per format (300 total)

Stratification ensures representation across:
- Confidence levels (HIGH/MEDIUM/LOW)
- Detection types (country/name/entity)
- Value ranges (high/medium/low)
"""

import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict


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

    # Configuration for stratified sampling
    formats = [
        {
            'name': '101-column',
            'table': 'usaspending_china_101',
            'sample_size': 100
        },
        {
            'name': '305-column',
            'table': 'usaspending_china_305',
            'sample_size': 100
        },
        {
            'name': '206-column',
            'table': 'usaspending_china_comprehensive',
            'sample_size': 100
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
        sample_size = format_config['sample_size']

        print(f"\n{'='*100}")
        print(f"SAMPLING: {format_name}")
        print(f"{'='*100}")

        # Get stratification info
        cursor = conn.execute(f"""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN highest_confidence = 'HIGH' THEN 1 END) as high_conf,
                COUNT(CASE WHEN highest_confidence = 'MEDIUM' THEN 1 END) as med_conf,
                COUNT(CASE WHEN highest_confidence = 'LOW' THEN 1 END) as low_conf,
                MIN(award_amount) as min_value,
                MAX(award_amount) as max_value,
                AVG(award_amount) as avg_value
            FROM {table}
        """)
        stats = cursor.fetchone()

        print(f"Total records: {stats['total']:,}")
        print(f"  HIGH confidence: {stats['high_conf']:,}")
        print(f"  MEDIUM confidence: {stats['med_conf']:,}")
        print(f"  LOW confidence: {stats['low_conf']:,}")
        print(f"Value range: ${stats['min_value']:,.2f} - ${stats['max_value']:,.2f}")
        print(f"Average value: ${stats['avg_value']:,.2f}")
        print()

        # Stratified sampling strategy
        # 50% HIGH confidence, 30% MEDIUM, 20% LOW (reflects importance)
        strata = [
            ('HIGH', int(sample_size * 0.5)),
            ('MEDIUM', int(sample_size * 0.3)),
            ('LOW', int(sample_size * 0.2))
        ]

        format_samples = []

        for confidence_level, stratum_size in strata:
            print(f"Sampling {stratum_size} {confidence_level} confidence records...")

            cursor = conn.execute(f"""
                SELECT * FROM {table}
                WHERE highest_confidence = ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (confidence_level, stratum_size))

            samples = cursor.fetchall()
            print(f"  Retrieved: {len(samples)} samples")

            for sample in samples:
                # Convert to dict and add metadata
                sample_dict = dict(sample)
                sample_dict['format'] = format_name
                sample_dict['sample_stratum'] = confidence_level

                # Parse detection_details if JSON string
                if 'detection_details' in sample_dict and sample_dict['detection_details']:
                    try:
                        sample_dict['detection_details_parsed'] = json.loads(sample_dict['detection_details'])
                    except:
                        sample_dict['detection_details_parsed'] = sample_dict['detection_details']

                # Parse detection_types if JSON string
                if 'detection_types' in sample_dict and sample_dict['detection_types']:
                    try:
                        sample_dict['detection_types_parsed'] = json.loads(sample_dict['detection_types'])
                    except:
                        sample_dict['detection_types_parsed'] = sample_dict['detection_types']

                format_samples.append(sample_dict)

        all_samples.extend(format_samples)

        summary['by_format'][format_name] = {
            'total_population': stats['total'],
            'samples_generated': len(format_samples),
            'stratification': {s[0]: s[1] for s in strata}
        }

        print(f"\nTotal samples for {format_name}: {len(format_samples)}")

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

    # Define CSV fields (most important for review)
    fieldnames = [
        'review_id',
        'format',
        'transaction_id',
        'recipient_name',
        'recipient_country_name',
        'pop_country_name',
        'award_amount',
        'award_description',
        'action_date',
        'highest_confidence',
        'detection_types',
        'awarding_agency',
        'TRUE_POSITIVE',  # For manual entry
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
                'recipient_country_name': sample.get('recipient_country_name', '') or sample.get('recipient_country', ''),
                'pop_country_name': sample.get('pop_country_name', '') or sample.get('pop_country', ''),
                'award_amount': sample.get('award_amount', 0),
                'award_description': (sample.get('award_description', '') or '')[:200],  # Truncate
                'action_date': sample.get('action_date', ''),
                'highest_confidence': sample.get('highest_confidence', ''),
                'detection_types': sample.get('detection_types', ''),
                'awarding_agency': sample.get('awarding_agency', '') or sample.get('funding_agency_code', ''),
                'TRUE_POSITIVE': '',  # Empty for manual entry
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

    return len(all_samples), csv_output


def create_review_instructions():
    """Create instructions document for manual review."""

    instructions_path = Path("C:/Projects/OSINT - Foresight/analysis/manual_review/REVIEW_INSTRUCTIONS.md")

    instructions = """# Manual Review Instructions

## Purpose
Validate detection accuracy by manually reviewing 300 randomly sampled transactions to calculate precision (false positive rate).

**Goal:** Achieve >95% precision to establish confidence in detection methodology.

## Review Process

### Step 1: Open the CSV File
- File: `manual_review_samples_[timestamp].csv`
- Open in Excel or similar spreadsheet software
- 300 rows total (100 per format)

### Step 2: Review Each Transaction

For each row, answer the question:

**"Is this transaction genuinely China (PRC) related?"**

### Step 3: Mark TRUE_POSITIVE Column

Enter one of the following values:

- **YES** = True Positive (correctly detected as China-related)
- **NO** = False Positive (incorrectly detected, NOT China-related)
- **UNCERTAIN** = Cannot determine with available information

### Step 4: Add Notes

In the NOTES column, explain your reasoning, especially for:
- All "NO" (false positive) cases
- All "UNCERTAIN" cases
- Interesting patterns or edge cases

## Classification Guidelines

### TRUE POSITIVE (YES) - Mark if ANY of these apply:

1. **Direct PRC Entity**
   - Recipient is a Chinese company/organization
   - Example: "CHINA MOBILE COMMUNICATIONS"
   - Example: "HUAWEI TECHNOLOGIES"

2. **PRC Geographic Location**
   - Work performed in mainland China
   - Recipient country = CHINA
   - Place of Performance = CHINA
   - Example: US university conducting research in Beijing

3. **Hong Kong Entity**
   - Hong Kong company or organization
   - HKG country code
   - Example: "HONG KONG TRADE DEVELOPMENT COUNCIL"

4. **Taiwan → China Cross-Strait**
   - Taiwan recipient with work in mainland China
   - Example: Taiwan company with Shanghai office
   - **POLICY:** This IS a valid China-related transaction

5. **Indirect PRC Connection**
   - Sub-awardee is Chinese
   - Parent company is Chinese
   - Example: US recipient subcontracting to Beijing firm

### FALSE POSITIVE (NO) - Mark if ALL of these apply:

1. **No PRC Connection**
   - Not a Chinese entity
   - No work in China/Hong Kong
   - No Chinese sub-awardees

2. **Common False Positive Patterns:**
   - "China" in street address (e.g., "123 China Street, USA")
   - Non-Chinese company with "china" in name (e.g., "CHINA PORCELAIN SHOP")
   - Taiwan entity with NO mainland China work
   - Data error or corruption

3. **Name Confusion**
   - Italian names containing "CHIN" (e.g., "FACCHINA")
   - Non-Chinese words containing "china"
   - Person names (e.g., "CHINA JONES")

### UNCERTAIN - Mark if:

1. **Insufficient Information**
   - Award description too vague
   - Country codes unclear
   - Entity name ambiguous

2. **Complex Cases**
   - Multiple countries involved
   - Unclear if sub-awardee exists
   - Conflicting information

3. **Need External Verification**
   - Need to look up company
   - Need additional context
   - Borderline classification

## Review Fields Reference

### Key Fields for Review:

1. **recipient_name**
   - Who is receiving the money?
   - Is this a Chinese entity?

2. **recipient_country_name**
   - Where is the recipient based?
   - CHINA, HONG KONG = likely yes
   - TAIWAN = check pop_country_name

3. **pop_country_name** (Place of Performance)
   - Where is the work being done?
   - If CHINA/HONG KONG = YES even if recipient is US/Taiwan

4. **award_description**
   - What is this for?
   - Does it mention China/Chinese locations?
   - Technology transfer implications?

5. **detection_types**
   - How was this detected?
   - "country" = high confidence
   - "chinese_name" = lower confidence (more FPs)

6. **highest_confidence**
   - HIGH = country-based (usually accurate)
   - MEDIUM = entity name match (fairly accurate)
   - LOW = name pattern match (more FPs expected)

## Examples

### Example 1: Clear TRUE POSITIVE
```
Recipient: BEIJING TELECOM ENGINEERING BUREAU
Recipient Country: CHINA
POP Country: CHINA
Award: $101,268
Detection: country, entity_name
Classification: YES
Notes: Chinese state-owned enterprise, clear China connection
```

### Example 2: Clear FALSE POSITIVE
```
Recipient: HOMER LAUGHLIN CHINA COMPANY
Recipient Country: UNITED STATES
POP Country: UNITED STATES
Award: $15,000
Detection: chinese_name_recipient
Classification: NO
Notes: US company that makes porcelain dishes, "china" refers to dinnerware
```

### Example 3: Taiwan Cross-Strait (TRUE POSITIVE per policy)
```
Recipient: TAISHEN RESEARCH
Recipient Country: TAIWAN
POP Country: CHINA
Award: $250,000
Detection: pop_country_china
Classification: YES
Notes: Taiwan company performing work in mainland China - valid per Option A policy
```

### Example 4: UNCERTAIN
```
Recipient: GLOBAL RESEARCH CONSORTIUM
Recipient Country: UNITED STATES
POP Country: [empty]
Award: $500,000
Detection: chinese_name_vendor
Award Description: "International collaboration"
Classification: UNCERTAIN
Notes: Description mentions international work but unclear if China involved. Need more info.
```

## Quality Checks

As you review, watch for:

1. **Consistency**
   - Are similar transactions classified the same way?
   - Is your reasoning consistent?

2. **Taiwan Policy**
   - Remember: Taiwan → China POP = TRUE POSITIVE
   - Taiwan alone (no China connection) = FALSE POSITIVE

3. **Hong Kong**
   - Hong Kong entities = TRUE POSITIVE
   - Part of PRC sphere

4. **Detection Type Patterns**
   - Are "country" detections more accurate than "name" detections?
   - This validates our confidence scoring

## After Review

### Calculate Statistics:
1. Count TRUE POSITIVE (YES)
2. Count FALSE POSITIVE (NO)
3. Count UNCERTAIN

### Precision Calculation:
```
Precision = TRUE POSITIVE / (TRUE POSITIVE + FALSE POSITIVE)
```

Exclude UNCERTAIN from calculation (or count conservatively as FALSE POSITIVE).

**Target:** >95% precision

### Report Findings:
- Overall precision per format
- Common false positive patterns
- Recommendations for improvement

## Time Estimate

- ~2-3 minutes per transaction
- 300 transactions × 2.5 min = 12.5 hours total
- Can be done in multiple sessions
- Aim for 50-100 transactions per session

## Questions?

Refer to:
- `analysis/TAIWAN_POLICY_FINAL_DECISION.md` - Taiwan policy
- `analysis/TAIWAN_DETECTION_POLICY_ANALYSIS.md` - Policy rationale
- Original detection methodology in processor scripts

## Save Your Work

Save the CSV file frequently with your TRUE_POSITIVE and NOTES entries filled in.

When complete, email or save as:
`manual_review_samples_[timestamp]_COMPLETED.csv`
"""

    with open(instructions_path, 'w') as f:
        f.write(instructions)

    print(f"\nReview instructions: {instructions_path}")

    return instructions_path


if __name__ == '__main__':
    print("\n" + "="*100)
    print("STARTING MANUAL REVIEW SAMPLE GENERATION")
    print("="*100 + "\n")

    # Generate samples
    sample_count, csv_file = generate_samples()

    # Create instructions
    instructions_file = create_review_instructions()

    print("\n" + "="*100)
    print("GENERATION COMPLETE")
    print("="*100)
    print(f"\nSamples generated: {sample_count}")
    print(f"CSV file: {csv_file}")
    print(f"Instructions: {instructions_file}")
    print(f"\nNext step: Open CSV file and begin manual review following instructions.")
    print("="*100 + "\n")
