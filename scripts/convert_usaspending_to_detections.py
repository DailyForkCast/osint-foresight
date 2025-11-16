#!/usr/bin/env python3
"""
Convert USAspending findings (JSON batch format) to detection format (NDJSON)

INPUT:  data/processed/usaspending_production/usaspending_china_findings_20251002_095642.json
OUTPUT: data/processed/usaspending_china/detections.ndjson

Purpose: Convert USAspending validator output to standardized detection schema
         for Phase 2 Bayesian fusion.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def convert_usaspending_findings():
    """Convert USAspending findings to detection format"""

    input_path = Path("data/processed/usaspending_production/usaspending_china_findings_20251002_095642.json")
    output_dir = Path("data/processed/usaspending_china")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "detections.ndjson"

    logging.info(f"Converting: {input_path}")

    # Load findings
    with open(input_path) as f:
        data = json.load(f)

    findings = data.get('findings', [])
    logging.info(f"Found {len(findings)} findings to convert")

    # Convert to detection format
    detections_written = 0

    with open(output_path, 'w') as f_out:
        for i, finding in enumerate(findings):
            # Extract key fields
            validation_result = finding.get('validation_result', {})
            provenance = finding.get('provenance', {})

            # Create detection record
            detection = {
                'detection_id': f"usaspending_{finding.get('record_hash', i)}",
                'detector_id': 'usaspending_v2.0',
                'confidence_score': int(validation_result.get('confidence', 0.5) * 100),
                'evidence': {
                    'file_id_or_url': finding.get('source_file', 'usaspending_batch'),
                    'record_id_or_line': f"line_{finding.get('source_line', i)}",
                    'field_name': 'extracted_text',
                    'field_value': finding.get('extracted_text', '')[:500],  # Truncate
                    'extraction_method': 'validator_v3.0',
                    'feature_hash': f"sha256:{finding.get('record_hash', '0' * 16)}"
                },
                'entity_identifiers': {
                    'extracted_text': finding.get('extracted_text', '')[:200],
                    'country': validation_result.get('country_name', 'Unknown'),
                    'languages_detected': validation_result.get('language_names', [])
                },
                'temporal_range': {
                    'valid_from': 'unknown',
                    'valid_to': '9999-12-31',
                    'inferred': True
                },
                'validation_metadata': {
                    'false_positive_risk': validation_result.get('false_positive_risk', 'unknown'),
                    'validator_confidence': validation_result.get('confidence', 0.0),
                    'detection_timestamp': provenance.get('timestamp', datetime.now().isoformat())
                },
                'incomplete': False,
                'human_verified': False
            }

            # Write as NDJSON
            f_out.write(json.dumps(detection) + '\n')
            detections_written += 1

    logging.info(f"Converted {detections_written} detections")
    logging.info(f"Output: {output_path}")

    # Create statistics file
    stats = {
        'conversion_date': datetime.now().isoformat(),
        'source_file': str(input_path),
        'total_findings': len(findings),
        'detections_written': detections_written,
        'detector_id': 'usaspending_v2.0',
        'detector_version': 'v2.0',
        'source_records_scanned': data.get('records_scanned', 0),
        'by_country': data.get('by_country', {}),
        'high_confidence_count': data.get('high_confidence', 0)
    }

    stats_path = output_dir / 'statistics.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    logging.info(f"Statistics: {stats_path}")

    # Create checkpoint for orchestrator
    checkpoint = {
        'complete': True,
        'processing_complete': True,
        'final_detections': detections_written,
        'completion_time': datetime.now().isoformat()
    }

    checkpoint_path = output_dir / 'checkpoint.json'
    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)

    logging.info(f"Checkpoint: {checkpoint_path}")

    return output_path, detections_written


if __name__ == '__main__':
    logging.info("=" * 80)
    logging.info("USAspending Findings → Detection Format Converter")
    logging.info("=" * 80)

    output_path, count = convert_usaspending_findings()

    logging.info("=" * 80)
    logging.info("CONVERSION COMPLETE")
    logging.info("=" * 80)
    logging.info(f"Detections: {count}")
    logging.info(f"Output: {output_path}")
    logging.info("=" * 80)
