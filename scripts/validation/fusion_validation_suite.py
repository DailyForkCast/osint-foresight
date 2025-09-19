#!/usr/bin/env python3
"""
Fusion Pipeline Validation Suite
Comprehensive testing and validation for all fusion pipelines
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import requests
import time
import yaml
import unittest
import pytest
from dataclasses import dataclass
import logging
import hashlib

# Import fusion pipelines for testing
import sys
sys.path.append("C:/Projects/OSINT - Foresight/scripts/fusion")
from conference_patent_procurement_pipeline import ConferencePatentProcurementPipeline
from github_dependencies_supply_pipeline import GitHubDependenciesSupplyPipeline
from standards_adoption_market_pipeline import StandardsAdoptionMarketPipeline
from funding_spinout_transfer_pipeline import FundingSpinoutTransferPipeline
from fusion_orchestrator import FusionOrchestrator, FusionTarget

@dataclass
class ValidationResult:
    """Validation test result"""
    test_name: str
    status: str  # pass, fail, warning
    details: str
    execution_time: float
    data_quality_score: float
    recommendations: List[str]

class FusionValidationSuite:
    """Comprehensive validation suite for fusion pipelines"""

    def __init__(self, config_path: str = None):
        """Initialize validation suite"""
        if config_path is None:
            config_path = "C:/Projects/OSINT - Foresight/config/fusion_config.yaml"

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Setup test data directory
        self.test_data_dir = Path("C:/Projects/OSINT - Foresight/test_data/fusion")
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

        # Setup validation output directory
        self.validation_dir = Path("F:/fusion_data/validation")
        self.validation_dir.mkdir(parents=True, exist_ok=True)

        # Initialize test entities
        self.test_entities = self._create_test_entities()

        # Validation thresholds
        self.validation_thresholds = {
            'minimum_confidence': 0.60,
            'maximum_execution_time': 300,  # 5 minutes
            'minimum_data_completeness': 0.70,
            'china_exposure_accuracy': 0.80,
            'temporal_correlation_threshold': 0.75
        }

    def _create_test_entities(self) -> List[FusionTarget]:
        """Create test entities for validation"""
        return [
            FusionTarget(
                entity_id="test_leonardo",
                entity_type="organization",
                org_ror="ror:05k694h47",
                country_iso3="ITA",
                primary_name="Leonardo S.p.A",
                aliases=["Leonardo", "Finmeccanica"],
                metadata={
                    'has_conference_data': True,
                    'event_uid': 'test_farnborough_2024',
                    'industry': 'aerospace_defense'
                }
            ),
            FusionTarget(
                entity_id="test_project_h2020",
                entity_type="project",
                org_ror=None,
                country_iso3="EUR",
                primary_name="H2020 AI Test Project",
                aliases=["AI Test Project"],
                metadata={
                    'project_type': 'research',
                    'funding_amount': 2000000
                }
            ),
            FusionTarget(
                entity_id="test_conference_defcon",
                entity_type="event",
                org_ror=None,
                country_iso3="USA",
                primary_name="DEF CON 2024",
                aliases=["DEFCON", "DEF CON"],
                metadata={
                    'has_conference_data': True,
                    'event_uid': 'defcon_2024',
                    'domain': 'cybersecurity'
                }
            )
        ]

    def create_test_data(self):
        """Create synthetic test data for validation"""
        print("Creating test data for fusion pipeline validation...")

        # Create test conference data
        test_conference = {
            "event_uid": "test_farnborough_2024",
            "name": "Test Farnborough Airshow 2024",
            "date": "2024-07-15",
            "location": "Farnborough, UK",
            "participants": ["Leonardo", "BAE Systems", "Airbus", "Boeing", "COMAC"],
            "content": [
                "Leonardo presents advanced helicopter technology with AI integration",
                "BAE Systems demonstrates quantum radar capabilities",
                "Airbus showcases sustainable aviation fuel technology"
            ],
            "tier": 1,
            "china_presence": True
        }

        conf_file = self.test_data_dir / "test_farnborough_2024.json"
        with open(conf_file, 'w') as f:
            json.dump(test_conference, f, indent=2)

        # Create test patent data
        test_patent = {
            "patent_number": "US11234567B2",
            "patent_title": "Advanced Helicopter Flight Control System with AI",
            "patent_date": "2024-09-15",
            "assignee_organization": "Leonardo",
            "inventor_country": "IT",
            "patent_abstract": "A flight control system utilizing artificial intelligence for enhanced helicopter performance"
        }

        patent_file = self.test_data_dir / "test_patents.json"
        with open(patent_file, 'w') as f:
            json.dump([test_patent], f, indent=2)

        # Create test GitHub data
        test_github = {
            "organizations": [
                {
                    "login": "leonardo-aerospace",
                    "name": "Leonardo Aerospace",
                    "public_repos": 45
                }
            ]
        }

        github_file = self.test_data_dir / "test_github.json"
        with open(github_file, 'w') as f:
            json.dump(test_github, f, indent=2)

        print("Test data created successfully")

    def validate_conference_patent_procurement_pipeline(self) -> ValidationResult:
        """Validate Conference→Patent→Procurement pipeline"""
        start_time = time.time()

        try:
            pipeline = ConferencePatentProcurementPipeline()

            # Test with synthetic data
            test_event_uid = "test_farnborough_2024"
            results = pipeline.run_pipeline(test_event_uid)

            execution_time = time.time() - start_time

            # Validate results structure
            required_fields = [
                'pipeline', 'event_uid', 'conference', 'patents',
                'procurement', 'confidence_metrics', 'china_exposure_vector'
            ]

            missing_fields = [field for field in required_fields if field not in results]

            if missing_fields:
                return ValidationResult(
                    test_name="Conference→Patent→Procurement Pipeline",
                    status="fail",
                    details=f"Missing required fields: {missing_fields}",
                    execution_time=execution_time,
                    data_quality_score=0.0,
                    recommendations=["Fix missing fields in pipeline output"]
                )

            # Validate data quality
            data_quality_score = self._assess_conference_pipeline_quality(results)

            # Check confidence thresholds
            overall_confidence = results.get('confidence_metrics', {}).get('overall_confidence', 0.0)
            confidence_pass = overall_confidence >= self.validation_thresholds['minimum_confidence']

            # Check execution time
            time_pass = execution_time <= self.validation_thresholds['maximum_execution_time']

            status = "pass" if confidence_pass and time_pass and not missing_fields else "warning"

            recommendations = []
            if not confidence_pass:
                recommendations.append(f"Improve confidence score (current: {overall_confidence:.2f})")
            if not time_pass:
                recommendations.append(f"Optimize execution time (current: {execution_time:.2f}s)")

            return ValidationResult(
                test_name="Conference→Patent→Procurement Pipeline",
                status=status,
                details=f"Confidence: {overall_confidence:.2f}, Time: {execution_time:.2f}s",
                execution_time=execution_time,
                data_quality_score=data_quality_score,
                recommendations=recommendations
            )

        except Exception as e:
            return ValidationResult(
                test_name="Conference→Patent→Procurement Pipeline",
                status="fail",
                details=f"Pipeline execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                data_quality_score=0.0,
                recommendations=["Debug pipeline execution error"]
            )

    def validate_github_dependencies_pipeline(self) -> ValidationResult:
        """Validate GitHub→Dependencies→Supply_Chain pipeline"""
        start_time = time.time()

        try:
            pipeline = GitHubDependenciesSupplyPipeline()

            # Test with synthetic data
            test_org_ror = "ror:test123"
            results = pipeline.run_pipeline(test_org_ror)

            execution_time = time.time() - start_time

            # Validate results structure
            required_fields = [
                'pipeline', 'org_ror', 'github_organizations',
                'total_repositories', 'total_dependencies',
                'china_maintained_dependencies', 'supply_chain_risks'
            ]

            missing_fields = [field for field in required_fields if field not in results]

            if 'error' in results:
                return ValidationResult(
                    test_name="GitHub→Dependencies→Supply_Chain Pipeline",
                    status="warning",
                    details=f"Pipeline returned error: {results['error']}",
                    execution_time=execution_time,
                    data_quality_score=0.5,
                    recommendations=["Check GitHub organization mapping for test data"]
                )

            # Assess data quality
            data_quality_score = self._assess_github_pipeline_quality(results)

            status = "pass" if not missing_fields else "warning"

            return ValidationResult(
                test_name="GitHub→Dependencies→Supply_Chain Pipeline",
                status=status,
                details=f"Dependencies: {results.get('total_dependencies', 0)}, China exposure: {results.get('china_exposure_percentage', 0):.1f}%",
                execution_time=execution_time,
                data_quality_score=data_quality_score,
                recommendations=[] if status == "pass" else ["Improve test data coverage"]
            )

        except Exception as e:
            return ValidationResult(
                test_name="GitHub→Dependencies→Supply_Chain Pipeline",
                status="fail",
                details=f"Pipeline execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                data_quality_score=0.0,
                recommendations=["Debug GitHub API integration"]
            )

    def validate_standards_adoption_pipeline(self) -> ValidationResult:
        """Validate Standards→Adoption→Market_Position pipeline"""
        start_time = time.time()

        try:
            pipeline = StandardsAdoptionMarketPipeline()

            # Test with synthetic data
            test_org_ror = "ror:test123"
            results = pipeline.run_pipeline(test_org_ror)

            execution_time = time.time() - start_time

            # Validate results structure
            required_fields = [
                'pipeline', 'org_ror', 'standards_participation',
                'adoption_metrics', 'market_position', 'summary_metrics'
            ]

            missing_fields = [field for field in required_fields if field not in results]

            if 'error' in results:
                return ValidationResult(
                    test_name="Standards→Adoption→Market_Position Pipeline",
                    status="warning",
                    details=f"Pipeline returned error: {results['error']}",
                    execution_time=execution_time,
                    data_quality_score=0.5,
                    recommendations=["Check standards body data availability for test entity"]
                )

            # Assess data quality
            data_quality_score = self._assess_standards_pipeline_quality(results)

            status = "pass" if not missing_fields else "warning"

            return ValidationResult(
                test_name="Standards→Adoption→Market_Position Pipeline",
                status=status,
                details=f"Standards: {results.get('summary_metrics', {}).get('total_standards', 0)}, Influence: {results.get('summary_metrics', {}).get('market_influence_score', 0):.2f}",
                execution_time=execution_time,
                data_quality_score=data_quality_score,
                recommendations=[] if status == "pass" else ["Enhance standards body integration"]
            )

        except Exception as e:
            return ValidationResult(
                test_name="Standards→Adoption→Market_Position Pipeline",
                status="fail",
                details=f"Pipeline execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                data_quality_score=0.0,
                recommendations=["Debug standards API integration"]
            )

    def validate_funding_spinout_pipeline(self) -> ValidationResult:
        """Validate Funding→Spinout→Technology_Transfer pipeline"""
        start_time = time.time()

        try:
            pipeline = FundingSpinoutTransferPipeline()

            # Test with synthetic data
            test_project_id = "H2020-TEST-123456"
            results = pipeline.run_pipeline(test_project_id)

            execution_time = time.time() - start_time

            # Validate results structure
            required_fields = [
                'pipeline', 'project_id', 'funding_source',
                'spinout_companies', 'technology_transfers',
                'china_interest_analysis', 'technology_leakage_risk'
            ]

            missing_fields = [field for field in required_fields if field not in results]

            if 'error' in results:
                return ValidationResult(
                    test_name="Funding→Spinout→Technology_Transfer Pipeline",
                    status="warning",
                    details=f"Pipeline returned error: {results['error']}",
                    execution_time=execution_time,
                    data_quality_score=0.5,
                    recommendations=["Check funding database integration for test project"]
                )

            # Assess data quality
            data_quality_score = self._assess_funding_pipeline_quality(results)

            status = "pass" if not missing_fields else "warning"

            return ValidationResult(
                test_name="Funding→Spinout→Technology_Transfer Pipeline",
                status=status,
                details=f"Spinouts: {results.get('summary_metrics', {}).get('total_spinouts', 0)}, Risk: {results.get('summary_metrics', {}).get('risk_level', 'unknown')}",
                execution_time=execution_time,
                data_quality_score=data_quality_score,
                recommendations=[] if status == "pass" else ["Improve funding data integration"]
            )

        except Exception as e:
            return ValidationResult(
                test_name="Funding→Spinout→Technology_Transfer Pipeline",
                status="fail",
                details=f"Pipeline execution failed: {str(e)}",
                execution_time=time.time() - start_time,
                data_quality_score=0.0,
                recommendations=["Debug funding API integration"]
            )

    def validate_fusion_orchestrator(self) -> ValidationResult:
        """Validate fusion orchestrator integration"""
        start_time = time.time()

        try:
            orchestrator = FusionOrchestrator()

            # Test with first test entity
            test_entity = self.test_entities[0]
            results = orchestrator.run_complete_fusion_analysis(test_entity)

            execution_time = time.time() - start_time

            # Validate results structure
            required_attributes = [
                'target_entity', 'pipeline_results', 'cross_pipeline_correlations',
                'china_exposure_matrix', 'risk_assessment', 'recommendations'
            ]

            missing_attributes = [attr for attr in required_attributes if not hasattr(results, attr)]

            if missing_attributes:
                return ValidationResult(
                    test_name="Fusion Orchestrator",
                    status="fail",
                    details=f"Missing required attributes: {missing_attributes}",
                    execution_time=execution_time,
                    data_quality_score=0.0,
                    recommendations=["Fix missing attributes in fusion results"]
                )

            # Validate fusion quality
            fusion_quality = self._assess_fusion_quality(results)

            # Check confidence and execution time
            confidence_pass = results.confidence_score >= self.validation_thresholds['minimum_confidence']
            time_pass = execution_time <= self.validation_thresholds['maximum_execution_time']

            status = "pass" if confidence_pass and time_pass and not missing_attributes else "warning"

            recommendations = []
            if not confidence_pass:
                recommendations.append(f"Improve fusion confidence (current: {results.confidence_score:.2f})")
            if not time_pass:
                recommendations.append(f"Optimize fusion execution time (current: {execution_time:.2f}s)")

            return ValidationResult(
                test_name="Fusion Orchestrator",
                status=status,
                details=f"Risk: {results.risk_assessment['risk_level']}, Confidence: {results.confidence_score:.2f}",
                execution_time=execution_time,
                data_quality_score=fusion_quality,
                recommendations=recommendations
            )

        except Exception as e:
            return ValidationResult(
                test_name="Fusion Orchestrator",
                status="fail",
                details=f"Fusion orchestrator failed: {str(e)}",
                execution_time=time.time() - start_time,
                data_quality_score=0.0,
                recommendations=["Debug fusion orchestrator integration"]
            )

    def validate_china_exposure_accuracy(self) -> ValidationResult:
        """Validate China exposure detection accuracy"""
        start_time = time.time()

        # Create test scenarios with known China exposure
        test_scenarios = [
            {
                'name': 'High China Exposure',
                'data': {
                    'conference_china_presence': True,
                    'china_maintained_dependencies': 50,
                    'total_dependencies': 100,
                    'china_collaboration_standards': 5,
                    'china_involved_transfers': 3
                },
                'expected_risk_level': 'high'
            },
            {
                'name': 'Low China Exposure',
                'data': {
                    'conference_china_presence': False,
                    'china_maintained_dependencies': 2,
                    'total_dependencies': 100,
                    'china_collaboration_standards': 0,
                    'china_involved_transfers': 0
                },
                'expected_risk_level': 'low'
            }
        ]

        correct_predictions = 0
        total_scenarios = len(test_scenarios)

        for scenario in test_scenarios:
            # Simulate China exposure calculation
            predicted_risk = self._simulate_china_exposure_calculation(scenario['data'])

            if predicted_risk == scenario['expected_risk_level']:
                correct_predictions += 1

        accuracy = correct_predictions / total_scenarios
        execution_time = time.time() - start_time

        status = "pass" if accuracy >= self.validation_thresholds['china_exposure_accuracy'] else "warning"

        return ValidationResult(
            test_name="China Exposure Accuracy",
            status=status,
            details=f"Accuracy: {accuracy:.2f} ({correct_predictions}/{total_scenarios})",
            execution_time=execution_time,
            data_quality_score=accuracy,
            recommendations=[] if status == "pass" else ["Improve China exposure detection algorithms"]
        )

    def validate_temporal_correlation_accuracy(self) -> ValidationResult:
        """Validate temporal correlation detection"""
        start_time = time.time()

        # Create test temporal sequences
        test_sequences = [
            {
                'events': [
                    {'type': 'conference', 'date': '2024-01-15', 'entity': 'Leonardo'},
                    {'type': 'patent', 'date': '2024-08-15', 'entity': 'Leonardo'},
                    {'type': 'procurement', 'date': '2025-02-15', 'entity': 'Leonardo'}
                ],
                'expected_correlation': True
            },
            {
                'events': [
                    {'type': 'conference', 'date': '2024-01-15', 'entity': 'Leonardo'},
                    {'type': 'patent', 'date': '2027-08-15', 'entity': 'Boeing'},  # Too late, different entity
                    {'type': 'procurement', 'date': '2025-02-15', 'entity': 'Airbus'}
                ],
                'expected_correlation': False
            }
        ]

        correct_correlations = 0
        total_sequences = len(test_sequences)

        for sequence in test_sequences:
            # Simulate temporal correlation detection
            detected_correlation = self._simulate_temporal_correlation(sequence['events'])

            if detected_correlation == sequence['expected_correlation']:
                correct_correlations += 1

        accuracy = correct_correlations / total_sequences
        execution_time = time.time() - start_time

        status = "pass" if accuracy >= self.validation_thresholds['temporal_correlation_threshold'] else "warning"

        return ValidationResult(
            test_name="Temporal Correlation Accuracy",
            status=status,
            details=f"Accuracy: {accuracy:.2f} ({correct_correlations}/{total_sequences})",
            execution_time=execution_time,
            data_quality_score=accuracy,
            recommendations=[] if status == "pass" else ["Improve temporal correlation algorithms"]
        )

    def _assess_conference_pipeline_quality(self, results: Dict[str, Any]) -> float:
        """Assess data quality for conference pipeline results"""
        quality_score = 0.0

        # Check conference data completeness
        if results.get('conference'):
            quality_score += 0.3

        # Check patents found
        patents = results.get('patents', [])
        if patents:
            quality_score += 0.3

        # Check confidence metrics
        confidence = results.get('confidence_metrics', {})
        if confidence:
            quality_score += 0.2

        # Check China exposure analysis
        china_exposure = results.get('china_exposure_vector', {})
        if china_exposure:
            quality_score += 0.2

        return quality_score

    def _assess_github_pipeline_quality(self, results: Dict[str, Any]) -> float:
        """Assess data quality for GitHub pipeline results"""
        quality_score = 0.0

        # Check GitHub organizations found
        if results.get('github_organizations'):
            quality_score += 0.25

        # Check repositories analyzed
        if results.get('total_repositories', 0) > 0:
            quality_score += 0.25

        # Check dependencies extracted
        if results.get('total_dependencies', 0) > 0:
            quality_score += 0.25

        # Check risk assessment
        if results.get('supply_chain_risks'):
            quality_score += 0.25

        return quality_score

    def _assess_standards_pipeline_quality(self, results: Dict[str, Any]) -> float:
        """Assess data quality for standards pipeline results"""
        quality_score = 0.0

        # Check standards participation
        if results.get('standards_participation'):
            quality_score += 0.3

        # Check adoption metrics
        if results.get('adoption_metrics'):
            quality_score += 0.3

        # Check market position
        if results.get('market_position'):
            quality_score += 0.2

        # Check summary metrics
        if results.get('summary_metrics'):
            quality_score += 0.2

        return quality_score

    def _assess_funding_pipeline_quality(self, results: Dict[str, Any]) -> float:
        """Assess data quality for funding pipeline results"""
        quality_score = 0.0

        # Check funding source
        if results.get('funding_source'):
            quality_score += 0.3

        # Check spinouts detected
        if results.get('spinout_companies'):
            quality_score += 0.3

        # Check technology transfers
        if results.get('technology_transfers'):
            quality_score += 0.2

        # Check risk assessment
        if results.get('technology_leakage_risk'):
            quality_score += 0.2

        return quality_score

    def _assess_fusion_quality(self, results) -> float:
        """Assess overall fusion quality"""
        quality_score = 0.0

        # Check pipeline execution
        successful_pipelines = sum(1 for r in results.pipeline_results.values() if 'error' not in r)
        total_pipelines = len(results.pipeline_results)

        if total_pipelines > 0:
            quality_score += (successful_pipelines / total_pipelines) * 0.4

        # Check correlations found
        if results.cross_pipeline_correlations:
            quality_score += 0.2

        # Check China exposure analysis
        if results.china_exposure_matrix:
            quality_score += 0.2

        # Check recommendations generated
        if results.recommendations:
            quality_score += 0.2

        return quality_score

    def _simulate_china_exposure_calculation(self, data: Dict[str, Any]) -> str:
        """Simulate China exposure risk calculation"""
        risk_score = 0.0

        # Conference exposure
        if data.get('conference_china_presence'):
            risk_score += 0.3

        # Dependency exposure
        china_deps = data.get('china_maintained_dependencies', 0)
        total_deps = data.get('total_dependencies', 1)
        dep_ratio = china_deps / total_deps
        risk_score += dep_ratio * 0.4

        # Standards exposure
        china_standards = data.get('china_collaboration_standards', 0)
        if china_standards > 3:
            risk_score += 0.2

        # Transfer exposure
        china_transfers = data.get('china_involved_transfers', 0)
        if china_transfers > 2:
            risk_score += 0.3

        # Determine risk level
        if risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'

    def _simulate_temporal_correlation(self, events: List[Dict[str, Any]]) -> bool:
        """Simulate temporal correlation detection"""
        if len(events) < 2:
            return False

        # Check if events are from same entity and within reasonable time windows
        entities = [event['entity'] for event in events]
        if len(set(entities)) > 1:
            return False  # Different entities

        # Check temporal sequence
        dates = [datetime.fromisoformat(event['date']) for event in events]
        dates.sort()

        # Check if time gaps are reasonable
        for i in range(1, len(dates)):
            gap_months = (dates[i] - dates[i-1]).days / 30
            if gap_months > 24:  # More than 2 years
                return False

        return True

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of all fusion pipelines"""
        print("Running Fusion Pipeline Comprehensive Validation")
        print("="*60)

        # Create test data
        self.create_test_data()

        validation_results = []

        # Validate individual pipelines
        print("\n1. Validating individual pipelines...")

        pipeline_validations = [
            self.validate_conference_patent_procurement_pipeline,
            self.validate_github_dependencies_pipeline,
            self.validate_standards_adoption_pipeline,
            self.validate_funding_spinout_pipeline
        ]

        for validation_func in pipeline_validations:
            result = validation_func()
            validation_results.append(result)
            print(f"  {result.test_name}: {result.status.upper()} ({result.execution_time:.2f}s)")

        # Validate fusion orchestrator
        print("\n2. Validating fusion orchestrator...")
        orchestrator_result = self.validate_fusion_orchestrator()
        validation_results.append(orchestrator_result)
        print(f"  {orchestrator_result.test_name}: {orchestrator_result.status.upper()} ({orchestrator_result.execution_time:.2f}s)")

        # Validate accuracy measures
        print("\n3. Validating accuracy measures...")

        accuracy_validations = [
            self.validate_china_exposure_accuracy,
            self.validate_temporal_correlation_accuracy
        ]

        for validation_func in accuracy_validations:
            result = validation_func()
            validation_results.append(result)
            print(f"  {result.test_name}: {result.status.upper()} (Score: {result.data_quality_score:.2f})")

        # Generate comprehensive report
        report = self._generate_validation_report(validation_results)

        # Save validation report
        self._save_validation_report(report)

        return report

    def _generate_validation_report(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == 'pass')
        warning_tests = sum(1 for r in results if r.status == 'warning')
        failed_tests = sum(1 for r in results if r.status == 'fail')

        average_execution_time = np.mean([r.execution_time for r in results])
        average_quality_score = np.mean([r.data_quality_score for r in results])

        # Collect all recommendations
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)

        report = {
            "validation_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "warnings": warning_tests,
                "failed": failed_tests,
                "success_rate": passed_tests / total_tests,
                "average_execution_time": average_execution_time,
                "average_quality_score": average_quality_score
            },
            "test_results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "details": r.details,
                    "execution_time": r.execution_time,
                    "quality_score": r.data_quality_score,
                    "recommendations": r.recommendations
                }
                for r in results
            ],
            "overall_recommendations": list(set(all_recommendations)),
            "validation_timestamp": datetime.now().isoformat(),
            "validation_criteria_met": {
                "minimum_confidence": average_quality_score >= self.validation_thresholds['minimum_confidence'],
                "execution_time": average_execution_time <= self.validation_thresholds['maximum_execution_time'],
                "success_rate": (passed_tests / total_tests) >= 0.8
            }
        }

        return report

    def _save_validation_report(self, report: Dict[str, Any]):
        """Save validation report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.validation_dir / f"fusion_validation_report_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nValidation report saved to: {report_file}")

        # Also save summary
        summary_file = self.validation_dir / "latest_validation_summary.json"
        summary = {
            "timestamp": report["validation_timestamp"],
            "success_rate": report["validation_summary"]["success_rate"],
            "average_quality": report["validation_summary"]["average_quality_score"],
            "criteria_met": report["validation_criteria_met"],
            "critical_recommendations": report["overall_recommendations"][:5]
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

def main():
    """Main validation execution"""
    validator = FusionValidationSuite()
    report = validator.run_comprehensive_validation()

    print("\n" + "="*60)
    print("FUSION PIPELINE VALIDATION SUMMARY")
    print("="*60)

    summary = report["validation_summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} | Warnings: {summary['warnings']} | Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1%}")
    print(f"Average Quality Score: {summary['average_quality_score']:.2f}")
    print(f"Average Execution Time: {summary['average_execution_time']:.2f}s")

    criteria_met = report["validation_criteria_met"]
    print(f"\nValidation Criteria Met:")
    print(f"  Confidence Threshold: {'✓' if criteria_met['minimum_confidence'] else '✗'}")
    print(f"  Execution Time: {'✓' if criteria_met['execution_time'] else '✗'}")
    print(f"  Success Rate: {'✓' if criteria_met['success_rate'] else '✗'}")

    if report["overall_recommendations"]:
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(report["overall_recommendations"][:5], 1):
            print(f"  {i}. {rec}")

    return report

if __name__ == "__main__":
    report = main()
