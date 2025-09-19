#!/usr/bin/env python3
"""
Multi-Stage Validation Pipeline
Comprehensive pipeline to prevent false positive incidents like NIO
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from .entity_validator import EntityValidator
    from .enhanced_pattern_matcher import EnhancedPatternMatcher, MatchResult
    from .anomaly_detector import StatisticalAnomalyDetector
except ImportError:
    from entity_validator import EntityValidator
    from enhanced_pattern_matcher import EnhancedPatternMatcher, MatchResult
    from anomaly_detector import StatisticalAnomalyDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationStage(Enum):
    """Validation pipeline stages"""
    EXTRACTION = "extraction"
    ENTITY_VALIDATION = "entity_validation"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    CROSS_VALIDATION = "cross_validation"
    HUMAN_REVIEW = "human_review"
    FINAL_APPROVAL = "final_approval"

class ValidationStatus(Enum):
    """Status of validation"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    BLOCKED = "blocked"

@dataclass
class ValidationGate:
    """A validation gate in the pipeline"""
    stage: ValidationStage
    status: ValidationStatus
    confidence: float
    issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    timestamp: str
    metrics: Dict[str, Any]

class ValidationPipeline:
    """
    Multi-stage validation pipeline to prevent false positive incidents

    Designed to catch issues like:
    - NIO substring matching (182,008 false positives)
    - Statistical anomalies (93% concentration)
    - Temporal inconsistencies (contracts before company founded)
    - Context mismatches (automotive company in telecom contracts)
    """

    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {}

        # Initialize components
        self.entity_validator = EntityValidator()
        self.pattern_matcher = EnhancedPatternMatcher()
        self.anomaly_detector = StatisticalAnomalyDetector()

        # Pipeline configuration
        self.config = {
            'require_manual_review_threshold': config.get('manual_review_threshold', 0.6),
            'block_critical_anomalies': config.get('block_critical_anomalies', True),
            'minimum_confidence': config.get('minimum_confidence', 0.7),
            'statistical_anomaly_threshold': config.get('anomaly_threshold', 0.95),
            'max_entity_concentration': config.get('max_concentration', 0.5),
            'sample_rate_for_review': config.get('sample_rate', 0.1)
        }

        # Pipeline state
        self.validation_gates = []
        self.current_stage = ValidationStage.EXTRACTION
        self.overall_status = ValidationStatus.PENDING
        self.pipeline_results = {}

    def run_full_pipeline(self, text_data: List[str],
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the complete validation pipeline on text data

        Args:
            text_data: List of text documents to analyze
            context: Additional context (dates, countries, etc.)

        Returns:
            Complete pipeline results with validation status
        """
        if context is None:
            context = {}

        pipeline_start = datetime.now()
        logger.info(f"Starting validation pipeline on {len(text_data)} documents")

        self.pipeline_results = {
            'pipeline_id': f"pipeline_{int(pipeline_start.timestamp())}",
            'started': pipeline_start.isoformat(),
            'input_size': len(text_data),
            'stages': {},
            'overall_status': ValidationStatus.PENDING.value,
            'final_results': {},
            'quality_metrics': {},
            'recommendations': []
        }

        try:
            # Stage 1: Extraction and Pattern Matching
            stage1_result = self._stage1_extraction(text_data, context)
            self._record_stage_result(ValidationStage.EXTRACTION, stage1_result)

            if stage1_result['gate'].status == ValidationStatus.FAILED:
                return self._finalize_pipeline("Stage 1 extraction failed")

            # Stage 2: Entity Validation
            stage2_result = self._stage2_entity_validation(stage1_result['matches'], context)
            self._record_stage_result(ValidationStage.ENTITY_VALIDATION, stage2_result)

            if stage2_result['gate'].status == ValidationStatus.FAILED:
                return self._finalize_pipeline("Stage 2 entity validation failed")

            # Stage 3: Statistical Analysis
            stage3_result = self._stage3_statistical_analysis(stage2_result['validated_matches'])
            self._record_stage_result(ValidationStage.STATISTICAL_ANALYSIS, stage3_result)

            if stage3_result['gate'].status == ValidationStatus.BLOCKED:
                return self._finalize_pipeline("Stage 3 blocked due to critical anomalies")

            # Stage 4: Cross-Validation
            stage4_result = self._stage4_cross_validation(stage3_result['clean_matches'], context)
            self._record_stage_result(ValidationStage.CROSS_VALIDATION, stage4_result)

            # Stage 5: Human Review (if needed)
            if stage4_result['gate'].status == ValidationStatus.NEEDS_REVIEW:
                stage5_result = self._stage5_human_review_queue(stage4_result['matches'])
                self._record_stage_result(ValidationStage.HUMAN_REVIEW, stage5_result)
            else:
                stage5_result = {'matches': stage4_result['matches']}

            # Final approval
            final_result = self._stage6_final_approval(stage5_result['matches'])

            return self._finalize_pipeline("Pipeline completed successfully", final_result)

        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            return self._finalize_pipeline(f"Pipeline error: {str(e)}")

    def _stage1_extraction(self, text_data: List[str],
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 1: Extract entity matches using enhanced pattern matching"""

        logger.info("Stage 1: Entity extraction starting")
        stage_start = datetime.now()

        all_matches = []
        extraction_stats = {
            'documents_processed': 0,
            'total_raw_matches': 0,
            'entities_found': set(),
            'processing_errors': 0
        }

        for i, text in enumerate(text_data):
            try:
                # Add document context
                doc_context = context.copy()
                doc_context['document_id'] = i

                # Extract matches using enhanced pattern matcher
                matches = self.pattern_matcher.find_chinese_companies(text, doc_context)
                all_matches.extend(matches)

                extraction_stats['documents_processed'] += 1
                extraction_stats['total_raw_matches'] += len(matches)
                extraction_stats['entities_found'].update(m.entity for m in matches)

                if i % 1000 == 0:
                    logger.info(f"Processed {i}/{len(text_data)} documents")

            except Exception as e:
                extraction_stats['processing_errors'] += 1
                logger.warning(f"Error processing document {i}: {e}")

        # Create validation gate
        gate = ValidationGate(
            stage=ValidationStage.EXTRACTION,
            status=ValidationStatus.PASSED if extraction_stats['processing_errors'] < len(text_data) * 0.1 else ValidationStatus.FAILED,
            confidence=1.0 - (extraction_stats['processing_errors'] / len(text_data)),
            issues=[f"{extraction_stats['processing_errors']} processing errors"] if extraction_stats['processing_errors'] > 0 else [],
            warnings=[],
            recommendations=[],
            timestamp=datetime.now().isoformat(),
            metrics=extraction_stats
        )

        # Convert set to list for JSON serialization
        extraction_stats['entities_found'] = list(extraction_stats['entities_found'])

        logger.info(f"Stage 1 completed: {len(all_matches)} matches from {len(extraction_stats['entities_found'])} entities")

        return {
            'gate': gate,
            'matches': all_matches,
            'statistics': extraction_stats,
            'duration': (datetime.now() - stage_start).total_seconds()
        }

    def _stage2_entity_validation(self, matches: List[MatchResult],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Validate individual entity matches"""

        logger.info(f"Stage 2: Entity validation starting on {len(matches)} matches")
        stage_start = datetime.now()

        validated_matches = []
        validation_stats = {
            'total_matches': len(matches),
            'valid_matches': 0,
            'invalid_matches': 0,
            'low_confidence_matches': 0,
            'false_positives_caught': 0
        }

        for match in matches:
            # Re-validate with additional context
            validation = self.entity_validator.validate_entity_match(
                match.entity, match.text_snippet, match.context
            )

            if validation['valid'] and validation['confidence'] >= self.config['minimum_confidence']:
                # Update match with validation results
                match.confidence = validation['confidence']
                match.validation_status = 'validated'
                validated_matches.append(match)
                validation_stats['valid_matches'] += 1

            elif validation['confidence'] < self.config['minimum_confidence']:
                validation_stats['low_confidence_matches'] += 1

            else:
                validation_stats['invalid_matches'] += 1
                if 'false_positive' in validation.get('match_type', ''):
                    validation_stats['false_positives_caught'] += 1

        # Determine gate status
        validation_rate = validation_stats['valid_matches'] / max(1, validation_stats['total_matches'])

        gate = ValidationGate(
            stage=ValidationStage.ENTITY_VALIDATION,
            status=ValidationStatus.PASSED if validation_rate >= 0.1 else ValidationStatus.FAILED,
            confidence=validation_rate,
            issues=[] if validation_rate >= 0.1 else [f"Low validation rate: {validation_rate:.1%}"],
            warnings=[f"{validation_stats['false_positives_caught']} false positives caught"] if validation_stats['false_positives_caught'] > 0 else [],
            recommendations=[],
            timestamp=datetime.now().isoformat(),
            metrics=validation_stats
        )

        logger.info(f"Stage 2 completed: {validation_stats['valid_matches']}/{validation_stats['total_matches']} matches validated")

        return {
            'gate': gate,
            'validated_matches': validated_matches,
            'statistics': validation_stats,
            'duration': (datetime.now() - stage_start).total_seconds()
        }

    def _stage3_statistical_analysis(self, matches: List[MatchResult]) -> Dict[str, Any]:
        """Stage 3: Statistical anomaly detection"""

        logger.info(f"Stage 3: Statistical analysis starting on {len(matches)} matches")
        stage_start = datetime.now()

        # Count matches by entity
        entity_counts = {}
        for match in matches:
            entity_counts[match.entity] = entity_counts.get(match.entity, 0) + 1

        # Detect statistical anomalies
        anomalies = self.entity_validator.detect_statistical_anomalies(entity_counts)

        # Analyze anomalies
        critical_anomalies = [a for a in anomalies if a['severity'] == 'critical']
        high_anomalies = [a for a in anomalies if a['severity'] == 'high']

        # Filter out matches from critically anomalous entities if configured
        clean_matches = matches
        if self.config['block_critical_anomalies'] and critical_anomalies:
            anomalous_entities = {a['entity'] for a in critical_anomalies}
            original_count = len(matches)
            clean_matches = [m for m in matches if m.entity not in anomalous_entities]

            logger.warning(f"Filtered {original_count - len(clean_matches)} matches from critically anomalous entities")

        # Determine gate status
        status = ValidationStatus.PASSED
        if critical_anomalies and self.config['block_critical_anomalies']:
            status = ValidationStatus.BLOCKED
        elif critical_anomalies or len(high_anomalies) > 2:
            status = ValidationStatus.NEEDS_REVIEW

        gate = ValidationGate(
            stage=ValidationStage.STATISTICAL_ANALYSIS,
            status=status,
            confidence=1.0 - (len(critical_anomalies) * 0.5 + len(high_anomalies) * 0.2),
            issues=[a['message'] for a in critical_anomalies],
            warnings=[a['message'] for a in high_anomalies],
            recommendations=[f"Review entity: {a['entity']}" for a in critical_anomalies],
            timestamp=datetime.now().isoformat(),
            metrics={
                'total_anomalies': len(anomalies),
                'critical_anomalies': len(critical_anomalies),
                'high_anomalies': len(high_anomalies),
                'entity_distribution': entity_counts,
                'matches_filtered': len(matches) - len(clean_matches)
            }
        )

        logger.info(f"Stage 3 completed: {len(anomalies)} anomalies detected, {len(critical_anomalies)} critical")

        return {
            'gate': gate,
            'clean_matches': clean_matches,
            'anomalies': anomalies,
            'statistics': gate.metrics,
            'duration': (datetime.now() - stage_start).total_seconds()
        }

    def _stage4_cross_validation(self, matches: List[MatchResult],
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 4: Cross-validation with external sources"""

        logger.info(f"Stage 4: Cross-validation starting on {len(matches)} matches")
        stage_start = datetime.now()

        # Simulate cross-validation (in real implementation, would check external sources)
        cross_validation_stats = {
            'matches_checked': len(matches),
            'external_confirmations': 0,
            'external_conflicts': 0,
            'confidence_adjustments': 0
        }

        # For each unique entity, simulate external validation
        entities = set(m.entity for m in matches)
        for entity in entities:
            # Simulate external source check
            # In reality, this would query company registries, news sources, etc.

            # Mock validation - flag if entity has unusually high match count
            entity_matches = [m for m in matches if m.entity == entity]
            if len(entity_matches) > 1000:  # Suspicious volume
                cross_validation_stats['external_conflicts'] += 1
                # Reduce confidence for these matches
                for match in entity_matches:
                    match.confidence *= 0.7
                    cross_validation_stats['confidence_adjustments'] += 1
            else:
                cross_validation_stats['external_confirmations'] += 1

        # Determine if manual review is needed
        conflict_rate = cross_validation_stats['external_conflicts'] / max(1, len(entities))
        needs_review = conflict_rate > 0.2 or cross_validation_stats['confidence_adjustments'] > len(matches) * 0.1

        gate = ValidationGate(
            stage=ValidationStage.CROSS_VALIDATION,
            status=ValidationStatus.NEEDS_REVIEW if needs_review else ValidationStatus.PASSED,
            confidence=1.0 - conflict_rate,
            issues=[],
            warnings=[f"High conflict rate: {conflict_rate:.1%}"] if conflict_rate > 0.1 else [],
            recommendations=["Manual review recommended"] if needs_review else [],
            timestamp=datetime.now().isoformat(),
            metrics=cross_validation_stats
        )

        logger.info(f"Stage 4 completed: {cross_validation_stats['external_confirmations']} confirmations, {cross_validation_stats['external_conflicts']} conflicts")

        return {
            'gate': gate,
            'matches': matches,
            'statistics': cross_validation_stats,
            'duration': (datetime.now() - stage_start).total_seconds()
        }

    def _stage5_human_review_queue(self, matches: List[MatchResult]) -> Dict[str, Any]:
        """Stage 5: Queue items for human review"""

        logger.info(f"Stage 5: Queueing {len(matches)} matches for human review")
        stage_start = datetime.now()

        # Sample matches for human review
        sample_size = max(100, int(len(matches) * self.config['sample_rate_for_review']))
        sample_size = min(sample_size, len(matches))

        # Stratified sampling - prioritize low confidence and high volume entities
        high_priority = [m for m in matches if m.confidence < 0.8]
        random_sample = [m for m in matches if m not in high_priority]

        import random
        if len(random_sample) > sample_size - len(high_priority):
            random_sample = random.sample(random_sample, sample_size - len(high_priority))

        review_queue = high_priority + random_sample

        # Save review queue
        review_data = {
            'timestamp': datetime.now().isoformat(),
            'total_matches': len(matches),
            'review_queue_size': len(review_queue),
            'priority_items': len(high_priority),
            'matches': [asdict(m) for m in review_queue]
        }

        review_file = Path('artifacts/human_review_queue.json')
        review_file.parent.mkdir(exist_ok=True)
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, indent=2, default=str)

        gate = ValidationGate(
            stage=ValidationStage.HUMAN_REVIEW,
            status=ValidationStatus.NEEDS_REVIEW,
            confidence=0.8,  # Pending human review
            issues=[],
            warnings=[],
            recommendations=[f"Review {len(review_queue)} sampled matches"],
            timestamp=datetime.now().isoformat(),
            metrics={
                'total_matches': len(matches),
                'queued_for_review': len(review_queue),
                'review_file': str(review_file)
            }
        )

        logger.info(f"Stage 5 completed: {len(review_queue)} matches queued for review")

        return {
            'gate': gate,
            'matches': matches,
            'review_queue': review_queue,
            'duration': (datetime.now() - stage_start).total_seconds()
        }

    def _stage6_final_approval(self, matches: List[MatchResult]) -> Dict[str, Any]:
        """Stage 6: Final approval and results compilation"""

        logger.info(f"Stage 6: Final approval for {len(matches)} matches")
        stage_start = datetime.now()

        # Calculate final statistics
        final_stats = {
            'total_matches': len(matches),
            'entities': len(set(m.entity for m in matches)),
            'average_confidence': sum(m.confidence for m in matches) / max(1, len(matches)),
            'high_confidence_matches': len([m for m in matches if m.confidence >= 0.8]),
            'entity_distribution': {}
        }

        # Entity distribution
        for match in matches:
            entity = match.entity
            if entity not in final_stats['entity_distribution']:
                final_stats['entity_distribution'][entity] = 0
            final_stats['entity_distribution'][entity] += 1

        gate = ValidationGate(
            stage=ValidationStage.FINAL_APPROVAL,
            status=ValidationStatus.PASSED,
            confidence=final_stats['average_confidence'],
            issues=[],
            warnings=[],
            recommendations=[],
            timestamp=datetime.now().isoformat(),
            metrics=final_stats
        )

        return {
            'gate': gate,
            'final_matches': matches,
            'statistics': final_stats,
            'duration': (datetime.now() - stage_start).total_seconds()
        }

    def _record_stage_result(self, stage: ValidationStage, result: Dict[str, Any]):
        """Record the result of a validation stage"""

        self.validation_gates.append(result['gate'])
        self.pipeline_results['stages'][stage.value] = {
            'gate': asdict(result['gate']),
            'statistics': result.get('statistics', {}),
            'duration': result.get('duration', 0)
        }
        self.current_stage = stage

    def _finalize_pipeline(self, message: str, final_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Finalize the pipeline execution"""

        self.pipeline_results['completed'] = datetime.now().isoformat()
        self.pipeline_results['message'] = message

        if final_result:
            self.pipeline_results['final_results'] = final_result['statistics']
            self.pipeline_results['final_matches'] = [asdict(m) for m in final_result.get('final_matches', [])]

        # Calculate overall status
        failed_gates = [g for g in self.validation_gates if g.status == ValidationStatus.FAILED]
        blocked_gates = [g for g in self.validation_gates if g.status == ValidationStatus.BLOCKED]
        review_gates = [g for g in self.validation_gates if g.status == ValidationStatus.NEEDS_REVIEW]

        if failed_gates or blocked_gates:
            self.overall_status = ValidationStatus.FAILED
        elif review_gates:
            self.overall_status = ValidationStatus.NEEDS_REVIEW
        else:
            self.overall_status = ValidationStatus.PASSED

        self.pipeline_results['overall_status'] = self.overall_status.value

        # Generate quality metrics
        if self.validation_gates:
            confidence_scores = [g.confidence for g in self.validation_gates]
            self.pipeline_results['quality_metrics'] = {
                'overall_confidence': sum(confidence_scores) / len(confidence_scores),
                'min_stage_confidence': min(confidence_scores),
                'gates_passed': len([g for g in self.validation_gates if g.status == ValidationStatus.PASSED]),
                'total_gates': len(self.validation_gates)
            }

        # Save pipeline results
        results_file = Path(f"artifacts/pipeline_results_{self.pipeline_results['pipeline_id']}.json")
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.pipeline_results, f, indent=2, default=str)

        logger.info(f"Pipeline completed with status: {self.overall_status.value}")
        return self.pipeline_results


def test_validation_pipeline():
    """Test the validation pipeline with NIO false positive scenario"""

    pipeline = ValidationPipeline()

    print("Testing Validation Pipeline")
    print("=" * 70)

    # Test Case 1: NIO false positive scenario
    print("\nTest 1: NIO False Positive Scenario")

    # Create test data simulating the original incident
    false_positive_texts = [
        "Il patrimonio culturale dell'unione europea include numerosi siti archeologici.",
        "Antonio Merloni ha firmato un convenio per il millennio con l'università.",
        "La cerimonia matrimoniale ha avuto luogo nel dominio pubblico della città.",
        "Il senio dirigente ha approvato l'opinio dell'esperto consultore."
    ] * 1000  # Simulate large dataset

    legitimate_texts = [
        "Huawei Technologies provided telecommunications equipment for the infrastructure project.",
        "ZTE Corporation delivered network infrastructure components under the contract.",
        "Xiaomi smartphone procurement contract was signed for government employees."
    ] * 100

    all_texts = false_positive_texts + legitimate_texts

    # Run pipeline
    context = {
        'analysis_type': 'procurement_analysis',
        'date_range': '2015-2020',
        'countries': ['IT', 'DE', 'FR']
    }

    results = pipeline.run_full_pipeline(all_texts, context)

    print(f"  Input size: {results['input_size']} documents")
    print(f"  Overall status: {results['overall_status']}")
    print(f"  Stages completed: {len(results['stages'])}")

    if 'quality_metrics' in results:
        print(f"  Overall confidence: {results['quality_metrics']['overall_confidence']:.2f}")
        print(f"  Gates passed: {results['quality_metrics']['gates_passed']}/{results['quality_metrics']['total_gates']}")

    # Show stage results
    for stage_name, stage_data in results['stages'].items():
        gate = stage_data['gate']
        print(f"  {stage_name}: {gate['status']} (confidence: {gate['confidence']:.2f})")
        if gate['issues']:
            print(f"    Issues: {gate['issues']}")

    return pipeline

if __name__ == "__main__":
    test_validation_pipeline()
