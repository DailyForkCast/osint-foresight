#!/usr/bin/env python3
"""
Calculate Precision Statistics from Manual Review Results

Analyzes completed manual review CSV and generates precision report.
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def calculate_precision(csv_path: Path):
    """Calculate precision statistics from completed manual review."""

    print("="*100)
    print("PRECISION CALCULATION FROM MANUAL REVIEW")
    print("="*100)
    print(f"Input: {csv_path}")
    print()

    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}")
        return

    # Read review results
    reviews = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviews.append(row)

    print(f"Total reviews loaded: {len(reviews)}")
    print()

    # Calculate statistics
    stats = {
        'total_reviews': len(reviews),
        'by_format': defaultdict(lambda: {
            'total': 0,
            'true_positive': 0,
            'false_positive': 0,
            'uncertain': 0,
            'not_reviewed': 0
        }),
        'by_confidence': defaultdict(lambda: {
            'total': 0,
            'true_positive': 0,
            'false_positive': 0
        }),
        'by_detection_type': defaultdict(lambda: {
            'total': 0,
            'true_positive': 0,
            'false_positive': 0
        }),
        'overall': {
            'true_positive': 0,
            'false_positive': 0,
            'uncertain': 0,
            'not_reviewed': 0
        },
        'confidence_scores': [],
        'false_positive_examples': []
    }

    # Analyze each review
    for review in reviews:
        format_name = review.get('format', 'unknown')
        true_positive = review.get('TRUE_POSITIVE', '').strip().upper()
        conf_level = review.get('highest_confidence', 'UNKNOWN')
        detection_types = review.get('detection_types', '')
        conf_score = review.get('CONFIDENCE_SCORE', '').strip()

        # Overall counts
        if true_positive == 'YES':
            stats['overall']['true_positive'] += 1
            stats['by_format'][format_name]['true_positive'] += 1
            stats['by_confidence'][conf_level]['true_positive'] += 1

            # Track by detection type
            if 'country' in detection_types:
                stats['by_detection_type']['country']['true_positive'] += 1
            if 'chinese_name' in detection_types or 'name' in detection_types:
                stats['by_detection_type']['name']['true_positive'] += 1

        elif true_positive == 'NO':
            stats['overall']['false_positive'] += 1
            stats['by_format'][format_name]['false_positive'] += 1
            stats['by_confidence'][conf_level]['false_positive'] += 1

            # Track by detection type
            if 'country' in detection_types:
                stats['by_detection_type']['country']['false_positive'] += 1
            if 'chinese_name' in detection_types or 'name' in detection_types:
                stats['by_detection_type']['name']['false_positive'] += 1

            # Collect false positive examples
            stats['false_positive_examples'].append({
                'review_id': review.get('review_id', ''),
                'recipient_name': review.get('recipient_name', ''),
                'recipient_country': review.get('recipient_country', ''),
                'detection_types': detection_types,
                'notes': review.get('NOTES', '')
            })

        elif true_positive == 'UNCERTAIN':
            stats['overall']['uncertain'] += 1
            stats['by_format'][format_name]['uncertain'] += 1
        else:
            stats['overall']['not_reviewed'] += 1
            stats['by_format'][format_name]['not_reviewed'] += 1

        # Format totals
        stats['by_format'][format_name]['total'] += 1

        # Confidence totals
        stats['by_confidence'][conf_level]['total'] += 1

        # Detection type totals
        if 'country' in detection_types:
            stats['by_detection_type']['country']['total'] += 1
        if 'chinese_name' in detection_types or 'name' in detection_types:
            stats['by_detection_type']['name']['total'] += 1

        # Confidence scores
        if conf_score and conf_score.isdigit():
            stats['confidence_scores'].append(int(conf_score))

    # Calculate precision metrics
    print("="*100)
    print("OVERALL RESULTS")
    print("="*100)
    print(f"Total Reviewed: {len(reviews)}")
    print(f"  True Positives (YES): {stats['overall']['true_positive']}")
    print(f"  False Positives (NO): {stats['overall']['false_positive']}")
    print(f"  Uncertain: {stats['overall']['uncertain']}")
    print(f"  Not Reviewed: {stats['overall']['not_reviewed']}")
    print()

    # Calculate precision (excluding uncertain)
    tp = stats['overall']['true_positive']
    fp = stats['overall']['false_positive']
    total_classified = tp + fp

    if total_classified > 0:
        precision = tp / total_classified
        print(f"PRECISION: {precision:.2%} ({tp}/{total_classified})")

        # Conservative precision (count uncertain as FP)
        total_conservative = tp + fp + stats['overall']['uncertain']
        precision_conservative = tp / total_conservative if total_conservative > 0 else 0
        print(f"PRECISION (Conservative): {precision_conservative:.2%} ({tp}/{total_conservative})")

        if precision >= 0.95:
            print("\n*** TARGET ACHIEVED: Precision >= 95% ***")
        else:
            print(f"\n*** BELOW TARGET: Need {0.95-precision:.2%} improvement ***")
    else:
        print("ERROR: No classifications made (all UNCERTAIN or not reviewed)")
        precision = 0
        precision_conservative = 0

    # By format
    print()
    print("="*100)
    print("PRECISION BY FORMAT")
    print("="*100)

    for format_name, format_stats in sorted(stats['by_format'].items()):
        tp_fmt = format_stats['true_positive']
        fp_fmt = format_stats['false_positive']
        total_fmt = tp_fmt + fp_fmt

        if total_fmt > 0:
            precision_fmt = tp_fmt / total_fmt
            print(f"\n{format_name}:")
            print(f"  Precision: {precision_fmt:.2%} ({tp_fmt}/{total_fmt})")
            print(f"  True Positives: {tp_fmt}")
            print(f"  False Positives: {fp_fmt}")
            print(f"  Uncertain: {format_stats['uncertain']}")

    # By confidence level
    print()
    print("="*100)
    print("PRECISION BY CONFIDENCE LEVEL")
    print("="*100)

    for conf_level, conf_stats in sorted(stats['by_confidence'].items()):
        tp_conf = conf_stats['true_positive']
        fp_conf = conf_stats['false_positive']
        total_conf = tp_conf + fp_conf

        if total_conf > 0:
            precision_conf = tp_conf / total_conf
            print(f"\n{conf_level}:")
            print(f"  Precision: {precision_conf:.2%} ({tp_conf}/{total_conf})")
            print(f"  True Positives: {tp_conf}")
            print(f"  False Positives: {fp_conf}")

    # By detection type
    print()
    print("="*100)
    print("PRECISION BY DETECTION TYPE")
    print("="*100)

    for det_type, det_stats in sorted(stats['by_detection_type'].items()):
        tp_det = det_stats['true_positive']
        fp_det = det_stats['false_positive']
        total_det = tp_det + fp_det

        if total_det > 0:
            precision_det = tp_det / total_det
            print(f"\n{det_type}:")
            print(f"  Precision: {precision_det:.2%} ({tp_det}/{total_det})")
            print(f"  True Positives: {tp_det}")
            print(f"  False Positives: {fp_det}")

    # Confidence score distribution
    if stats['confidence_scores']:
        print()
        print("="*100)
        print("MANUAL CONFIDENCE SCORES (1-5 scale)")
        print("="*100)

        avg_score = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
        print(f"Average Score: {avg_score:.2f}")
        print(f"Total Scored: {len(stats['confidence_scores'])}")

        for score in [5, 4, 3, 2, 1]:
            count = stats['confidence_scores'].count(score)
            pct = count / len(stats['confidence_scores']) * 100 if stats['confidence_scores'] else 0
            print(f"  Score {score}: {count} ({pct:.1f}%)")

    # False positive examples
    if stats['false_positive_examples']:
        print()
        print("="*100)
        print(f"FALSE POSITIVE EXAMPLES ({len(stats['false_positive_examples'])} total)")
        print("="*100)

        for i, example in enumerate(stats['false_positive_examples'][:10], 1):
            print(f"\n{i}. {example['recipient_name']}")
            print(f"   Country: {example['recipient_country']}")
            print(f"   Detection: {example['detection_types']}")
            print(f"   Notes: {example['notes'][:100]}")

        if len(stats['false_positive_examples']) > 10:
            print(f"\n... and {len(stats['false_positive_examples']) - 10} more false positives")

    # Save results
    output_dir = csv_path.parent
    results_path = output_dir / f"precision_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    results = {
        'analysis_date': datetime.now().isoformat(),
        'input_file': str(csv_path),
        'total_reviews': stats['total_reviews'],
        'overall_precision': precision,
        'conservative_precision': precision_conservative,
        'true_positives': tp,
        'false_positives': fp,
        'uncertain': stats['overall']['uncertain'],
        'by_format': dict(stats['by_format']),
        'by_confidence': dict(stats['by_confidence']),
        'by_detection_type': dict(stats['by_detection_type']),
        'average_confidence_score': avg_score if stats['confidence_scores'] else None,
        'false_positive_count': len(stats['false_positive_examples']),
        'target_achieved': precision >= 0.95
    }

    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print("="*100)
    print(f"Results saved: {results_path}")
    print("="*100)

    return results


if __name__ == '__main__':
    # Look for completed review file
    review_dir = Path("C:/Projects/OSINT - Foresight/analysis/manual_review")

    print("\nLooking for completed review files in:")
    print(f"  {review_dir}")
    print()

    completed_files = list(review_dir.glob("*_COMPLETED.csv"))

    if not completed_files:
        # Try the most recent file
        all_csv = list(review_dir.glob("manual_review_samples_*.csv"))
        if all_csv:
            latest = sorted(all_csv)[-1]
            print(f"No *_COMPLETED.csv found, using latest: {latest.name}")
            calculate_precision(latest)
        else:
            print("No review files found.")
            print("Expected file: manual_review_samples_*_COMPLETED.csv")
    else:
        latest_completed = sorted(completed_files)[-1]
        print(f"Found completed review: {latest_completed.name}")
        print()
        calculate_precision(latest_completed)
