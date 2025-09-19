#!/usr/bin/env python3
"""
Statistical Anomaly Detection System
Detects and flags suspicious or extreme results
"""

import json
import logging
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
import statistics
from collections import Counter
from pathlib import Path
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies to detect"""
    EXTREME_HIGH = "extreme_high"  # Value above threshold
    EXTREME_LOW = "extreme_low"    # Value below threshold
    IMPOSSIBLE = "impossible"       # Logically impossible value
    TEMPORAL = "temporal"           # Time-based anomaly
    STATISTICAL = "statistical"     # Statistical outlier
    PATTERN_BREAK = "pattern_break" # Breaks established pattern
    DATA_QUALITY = "data_quality"   # Data quality issue


class AnomalySeverity(Enum):
    """Severity levels for anomalies"""
    CRITICAL = "critical"  # Must investigate
    HIGH = "high"         # Should investigate
    MEDIUM = "medium"     # Flag for review
    LOW = "low"          # Note but continue


class StatisticalAnomalyDetector:
    """Detects statistical anomalies in OSINT data"""

    def __init__(self):
        # Critical thresholds
        self.thresholds = {
            'collaboration_rate': {
                'max': 0.95,  # >95% collaboration is suspicious
                'min': 0.001, # <0.1% collaboration is suspicious
                'typical_range': (0.05, 0.40)  # Expected range
            },
            'hhi': {
                'max': 0.95,  # Near monopoly
                'min': 0.0,   # Perfect competition (suspicious)
                'typical_range': (0.10, 0.60)
            },
            'growth_rate': {
                'max': 2.0,   # >200% annual growth
                'min': -0.5,  # >50% annual decline
                'typical_range': (-0.10, 0.30)
            },
            'dependency_rate': {
                'max': 0.90,  # >90% dependency
                'min': 0.0,   # Zero dependency (check if real)
                'typical_range': (0.10, 0.50)
            },
            'citation_rate': {
                'max': 100,   # >100 citations per paper per year
                'min': 0,     # Zero citations (verify)
                'typical_range': (1, 20)
            },
            'funding_concentration': {
                'max': 0.80,  # >80% from single source
                'min': 0.0,   # No concentration
                'typical_range': (0.20, 0.60)
            },
            'publication_count': {
                'min': 0,
                'max': 100000,
                'typical_range': (10, 1000)
            },
            'patent_filings': {
                'min': 0,  # Negative values are impossible
                'max': 10000,
                'typical_range': (1, 100)
            },
            'funding_amount': {
                'min': 0,
                'max': 1e12,  # 1 trillion
                'typical_range': (1000, 1e9)
            },
            'success_rate': {
                'min': 0.0,
                'max': 1.0,
                'typical_range': (0.1, 0.9)
            },
            'participation_rate': {
                'min': 0.0,
                'max': 1.0,
                'typical_range': (0.05, 0.8)
            },
            'data_quality': {
                'min': 0.0,
                'max': 1.0,
                'typical_range': (0.7, 1.0)
            },
            'rate': {  # Generic rate metric
                'min': 0.0,
                'max': 1.0,
                'typical_range': (0.1, 0.9)
            },
            'rate1': {
                'min': 0.0,
                'max': 1.0,
                'typical_range': (0.1, 0.9)
            },
            'rate2': {
                'min': 0.0,
                'max': 1.0,
                'typical_range': (0.1, 0.9)
            },
            'rate3': {
                'min': 0.0,
                'max': 1.0,
                'typical_range': (0.1, 0.9)
            },
            'count': {
                'min': 0,
                'max': 1000000,
                'typical_range': (1, 10000)
            },
            'percentage': {
                'min': 0.0,
                'max': 100.0,
                'typical_range': (5.0, 95.0)
            }
        }

        # Statistical parameters
        self.z_score_threshold = 3.0  # Standard deviations for outlier
        self.iqr_multiplier = 1.5     # IQR multiplier for outliers

        # Anomaly log
        self.anomalies_detected = []
        self.investigations = []

    def check_value(self, metric: str, value: float, context: Dict = None) -> Optional[Dict]:
        """Check a single value for anomalies"""

        anomaly = None

        if metric not in self.thresholds:
            logger.warning(f"Unknown metric: {metric}")
            return None

        threshold = self.thresholds[metric]

        # Check extreme values
        if value > threshold['max']:
            anomaly = {
                'type': AnomalyType.EXTREME_HIGH,
                'severity': AnomalySeverity.HIGH,
                'metric': metric,
                'value': value,
                'threshold': threshold['max'],
                'message': f"{metric} = {value:.2f} exceeds maximum threshold {threshold['max']}",
                'action': 'Investigate data quality and verify calculation'
            }

            # Special case: 100% collaboration
            if metric == 'collaboration_rate' and value >= 1.0:
                anomaly['severity'] = AnomalySeverity.CRITICAL
                anomaly['message'] = f"100% collaboration detected - highly suspicious"
                anomaly['action'] = 'Verify data completeness and search methodology'

        elif value < threshold['min'] and threshold['min'] > 0:
            anomaly = {
                'type': AnomalyType.EXTREME_LOW,
                'severity': AnomalySeverity.HIGH,
                'metric': metric,
                'value': value,
                'threshold': threshold['min'],
                'message': f"{metric} = {value:.2f} below minimum threshold {threshold['min']}",
                'action': 'Check for missing data or calculation errors'
            }

            # Special case: Zero results in large dataset
            if value == 0 and context and context.get('data_size_gb', 0) > 100:
                anomaly['severity'] = AnomalySeverity.CRITICAL
                anomaly['message'] = f"Zero {metric} despite {context['data_size_gb']}GB dataset"
                anomaly['action'] = 'Verify query, expand search parameters, check data completeness'

        # Check if outside typical range
        elif 'typical_range' in threshold:
            min_typical, max_typical = threshold['typical_range']
            if not (min_typical <= value <= max_typical):
                anomaly = {
                    'type': AnomalyType.STATISTICAL,
                    'severity': AnomalySeverity.MEDIUM,
                    'metric': metric,
                    'value': value,
                    'typical_range': threshold['typical_range'],
                    'message': f"{metric} = {value:.2f} outside typical range {threshold['typical_range']}",
                    'action': 'Flag for review'
                }

        if anomaly:
            anomaly['timestamp'] = datetime.now().isoformat()
            anomaly['context'] = context or {}
            self.anomalies_detected.append(anomaly)
            logger.warning(f"ANOMALY DETECTED: {anomaly['message']}")

            # Trigger investigation for critical anomalies
            if anomaly['severity'] == AnomalySeverity.CRITICAL:
                self._trigger_investigation(anomaly)
                logger.critical(f"INVESTIGATION TRIGGERED: {anomaly['message']}")

            # Convert enums to strings for external use
            anomaly_for_return = {}
            for k, v in anomaly.items():
                if hasattr(v, 'value'):  # Enum
                    anomaly_for_return[k] = v.value
                else:
                    anomaly_for_return[k] = v

            return anomaly_for_return

        return anomaly

    def check_distribution(self, data: List[float], metric: str) -> List[Dict]:
        """Check a distribution of values for anomalies"""

        anomalies = []

        if not data:
            return anomalies

        # Calculate statistics
        mean = statistics.mean(data)
        stdev = statistics.stdev(data) if len(data) > 1 else 0
        median = statistics.median(data)
        q1 = statistics.quantiles(data, n=4)[0] if len(data) > 3 else min(data)
        q3 = statistics.quantiles(data, n=4)[2] if len(data) > 3 else max(data)
        iqr = q3 - q1

        # Z-score method
        if stdev > 0:
            for value in data:
                z_score = (value - mean) / stdev
                if abs(z_score) > self.z_score_threshold:
                    anomalies.append({
                        'type': AnomalyType.STATISTICAL,
                        'severity': AnomalySeverity.MEDIUM,
                        'metric': metric,
                        'value': value,
                        'z_score': z_score,
                        'message': f"Statistical outlier: z-score = {z_score:.2f}",
                        'action': 'Review for data quality'
                    })

        # IQR method
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr

        for value in data:
            if value < lower_bound or value > upper_bound:
                if not any(a['value'] == value for a in anomalies):  # Avoid duplicates
                    anomalies.append({
                        'type': AnomalyType.STATISTICAL,
                        'severity': AnomalySeverity.MEDIUM,
                        'metric': metric,
                        'value': value,
                        'bounds': (lower_bound, upper_bound),
                        'message': f"IQR outlier: value {value:.2f} outside [{lower_bound:.2f}, {upper_bound:.2f}]",
                        'action': 'Verify calculation'
                    })

        return anomalies

    def check_temporal_pattern(self, time_series: List[Tuple[datetime, float]],
                              metric: str) -> List[Dict]:
        """Check time series for temporal anomalies"""

        anomalies = []

        if len(time_series) < 2:
            return anomalies

        # Sort by time
        time_series.sort(key=lambda x: x[0])

        # Check for impossible jumps
        for i in range(1, len(time_series)):
            prev_time, prev_value = time_series[i-1]
            curr_time, curr_value = time_series[i]

            time_diff = (curr_time - prev_time).days
            if time_diff > 0:
                daily_change = (curr_value - prev_value) / time_diff

                # Check for impossible growth
                if daily_change > 1.0:  # >100% daily growth
                    anomalies.append({
                        'type': AnomalyType.TEMPORAL,
                        'severity': AnomalySeverity.HIGH,
                        'metric': metric,
                        'period': (prev_time, curr_time),
                        'change': curr_value - prev_value,
                        'daily_rate': daily_change,
                        'message': f"Impossible growth rate: {daily_change:.1%} per day",
                        'action': 'Check data integrity and timestamps'
                    })

        # Check for suspicious patterns
        values = [v for _, v in time_series]

        # All values identical
        if len(set(values)) == 1 and len(values) > 5:
            anomalies.append({
                'type': AnomalyType.PATTERN_BREAK,
                'severity': AnomalySeverity.MEDIUM,
                'metric': metric,
                'pattern': 'All values identical',
                'message': f"Suspicious pattern: All {len(values)} values are identical",
                'action': 'Verify data collection process'
            })

        # All values increasing monotonically
        if all(values[i] >= values[i-1] for i in range(1, len(values))) and len(values) > 5:
            anomalies.append({
                'type': AnomalyType.PATTERN_BREAK,
                'severity': AnomalySeverity.LOW,
                'metric': metric,
                'pattern': 'Monotonic increase',
                'message': 'Perfectly monotonic increase detected',
                'action': 'Verify if realistic'
            })

        return anomalies

    def check_logical_consistency(self, data: Dict) -> List[Dict]:
        """Check for logical inconsistencies"""

        anomalies = []

        # Check: Total should equal sum of parts
        if 'total' in data and 'components' in data:
            calculated_total = sum(data['components'].values())
            if abs(data['total'] - calculated_total) > 0.01:
                anomalies.append({
                    'type': AnomalyType.IMPOSSIBLE,
                    'severity': AnomalySeverity.CRITICAL,
                    'check': 'Total != Sum',
                    'total': data['total'],
                    'calculated': calculated_total,
                    'message': f"Total {data['total']} != Sum {calculated_total}",
                    'action': 'Fix calculation error'
                })

        # Check: Percentages should sum to 100
        if 'percentages' in data:
            total_pct = sum(data['percentages'].values())
            if abs(total_pct - 100.0) > 1.0:
                anomalies.append({
                    'type': AnomalyType.IMPOSSIBLE,
                    'severity': AnomalySeverity.HIGH,
                    'check': 'Percentages != 100',
                    'sum': total_pct,
                    'message': f"Percentages sum to {total_pct:.1f}%, not 100%",
                    'action': 'Recalculate percentages'
                })

        # Check: Child <= Parent
        if 'parent_count' in data and 'child_count' in data:
            if data['child_count'] > data['parent_count']:
                anomalies.append({
                    'type': AnomalyType.IMPOSSIBLE,
                    'severity': AnomalySeverity.CRITICAL,
                    'check': 'Child > Parent',
                    'parent': data['parent_count'],
                    'child': data['child_count'],
                    'message': f"Child count {data['child_count']} > Parent count {data['parent_count']}",
                    'action': 'Verify entity relationships'
                })

        # Check: Dates in correct order
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] < data['start_date']:
                anomalies.append({
                    'type': AnomalyType.IMPOSSIBLE,
                    'severity': AnomalySeverity.CRITICAL,
                    'check': 'Date order',
                    'start': data['start_date'],
                    'end': data['end_date'],
                    'message': 'End date before start date',
                    'action': 'Fix date values'
                })

        return anomalies

    def _trigger_investigation(self, anomaly: Dict):
        """Trigger automated investigation for critical anomalies"""

        # Convert enum values to strings for JSON serialization
        anomaly_serializable = {
            k: (v.value if hasattr(v, 'value') else v)
            for k, v in anomaly.items()
        }

        investigation = {
            'id': hashlib.md5(json.dumps(anomaly_serializable, sort_keys=True, default=str).encode()).hexdigest()[:8],
            'anomaly': anomaly_serializable,  # Use serializable version
            'timestamp': datetime.now().isoformat(),
            'status': 'initiated',
            'steps': []
        }

        logger.critical(f"INVESTIGATION TRIGGERED: {anomaly['message']}")

        # Investigation steps based on anomaly type
        if anomaly['type'] == AnomalyType.EXTREME_HIGH:
            if 'collaboration_rate' in anomaly['metric']:
                investigation['steps'] = [
                    'Verify source data completeness',
                    'Check for data duplication',
                    'Validate search query parameters',
                    'Cross-reference with alternative sources',
                    'Calculate confidence interval'
                ]

        elif anomaly['type'] == AnomalyType.EXTREME_LOW:
            if anomaly['value'] == 0:
                investigation['steps'] = [
                    'Expand search parameters',
                    'Check alternative spellings/names',
                    'Verify time period coverage',
                    'Test with known positive example',
                    'Document as negative evidence if confirmed'
                ]

        self.investigations.append(investigation)

        # Save investigation plan
        self._save_investigation(investigation)

    def _save_investigation(self, investigation: Dict):
        """Save investigation to file"""

        investigations_file = Path('artifacts/anomaly_investigations.json')
        investigations_file.parent.mkdir(exist_ok=True)

        existing = []
        if investigations_file.exists():
            with open(investigations_file, 'r') as f:
                existing = json.load(f)

        existing.append(investigation)

        with open(investigations_file, 'w') as f:
            json.dump(existing, f, indent=2)

    def generate_anomaly_report(self) -> Dict:
        """Generate comprehensive anomaly report"""

        report = {
            'generated': datetime.now().isoformat(),
            'total_anomalies': len(self.anomalies_detected),
            'by_severity': {},
            'by_type': {},
            'investigations': len(self.investigations),
            'critical_findings': [],
            'recommendations': []
        }

        # Count by severity
        for anomaly in self.anomalies_detected:
            severity = anomaly['severity'].value
            if severity not in report['by_severity']:
                report['by_severity'][severity] = 0
            report['by_severity'][severity] += 1

            # Count by type
            atype = anomaly['type'].value
            if atype not in report['by_type']:
                report['by_type'][atype] = 0
            report['by_type'][atype] += 1

            # Collect critical findings
            if anomaly['severity'] == AnomalySeverity.CRITICAL:
                report['critical_findings'].append({
                    'metric': anomaly['metric'],
                    'value': anomaly['value'],
                    'message': anomaly['message'],
                    'action': anomaly['action']
                })

        # Generate recommendations
        if report['by_severity'].get('critical', 0) > 0:
            report['recommendations'].append('Immediate investigation required for critical anomalies')

        if report['by_type'].get('extreme_high', 0) > 2:
            report['recommendations'].append('Review calculation methodology for systematic overestimation')

        if report['by_type'].get('extreme_low', 0) > 2:
            report['recommendations'].append('Check data completeness and query parameters')

        return report


def test_anomaly_detector():
    """Test the anomaly detection system"""

    detector = StatisticalAnomalyDetector()

    print("Testing Anomaly Detection System")
    print("="*60)

    # Test 1: 100% collaboration rate
    print("\nTest 1: 100% collaboration rate")
    anomaly = detector.check_value('collaboration_rate', 1.0, {'country': 'Germany'})
    if anomaly:
        print(f"  DETECTED: {anomaly['message']}")
        print(f"  Severity: {anomaly['severity'].value}")
        print(f"  Action: {anomaly['action']}")

    # Test 2: Zero results in 350GB dataset
    print("\nTest 2: Zero results in large dataset")
    anomaly = detector.check_value('collaboration_rate', 0.0, {'data_size_gb': 350})
    if anomaly:
        print(f"  DETECTED: {anomaly['message']}")
        print(f"  Action: {anomaly['action']}")

    # Test 3: Statistical outliers
    print("\nTest 3: Statistical outliers")
    data = [0.1, 0.15, 0.12, 0.14, 0.95, 0.13, 0.11]  # 0.95 is outlier
    anomalies = detector.check_distribution(data, 'collaboration_rate')
    for a in anomalies:
        print(f"  DETECTED: {a['message']}")

    # Test 4: Temporal anomaly
    print("\nTest 4: Temporal patterns")
    time_series = [
        (datetime(2023, 1, 1), 100),
        (datetime(2023, 1, 2), 10000),  # Impossible jump
        (datetime(2023, 1, 3), 10100)
    ]
    anomalies = detector.check_temporal_pattern(time_series, 'paper_count')
    for a in anomalies:
        print(f"  DETECTED: {a['message']}")

    # Test 5: Logical consistency
    print("\nTest 5: Logical consistency")
    data = {
        'total': 100,
        'components': {'A': 40, 'B': 35, 'C': 30},  # Sum = 105, not 100
        'percentages': {'X': 45, 'Y': 35, 'Z': 15}  # Sum = 95%, not 100%
    }
    anomalies = detector.check_logical_consistency(data)
    for a in anomalies:
        print(f"  DETECTED: {a['message']}")

    # Generate report
    print("\n" + "="*60)
    report = detector.generate_anomaly_report()
    print(f"Total Anomalies Detected: {report['total_anomalies']}")
    print(f"Critical: {report['by_severity'].get('critical', 0)}")
    print(f"Investigations Triggered: {report['investigations']}")

    return detector

if __name__ == "__main__":
    test_anomaly_detector()
