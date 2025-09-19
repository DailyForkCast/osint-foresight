#!/usr/bin/env python3
"""
Counterfactual Query Implementation
Systematic search for disconfirming evidence to prevent confirmation bias
Priority 1 Implementation - Week 1
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of counterfactual queries"""
    OPPOSITE_SEARCH = "opposite_search"
    ALTERNATIVE_EXPLANATION = "alternative_explanation"
    MISSING_EVIDENCE = "missing_evidence"
    STATISTICAL_BASELINE = "statistical_baseline"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    CONTRADICTORY_SOURCE = "contradictory_source"
    NULL_HYPOTHESIS = "null_hypothesis"

class CounterfactualQueryEngine:
    """
    Engine for systematic disconfirming evidence search
    Addresses confirmation bias as identified in best practices analysis
    """

    def __init__(self, data_sources: List[str] = None):
        self.data_sources = data_sources or [
            "OpenAlex", "CORDIS", "TED", "USPTO", "EPO",
            "GLEIF", "SEC_EDGAR", "Crossref", "OpenAIRE"
        ]

        self.query_log = []
        self.contradiction_log = []

        # Balance tracking
        self.evidence_balance = {
            "confirmatory": 0,
            "contradictory": 0,
            "neutral": 0,
            "insufficient": 0
        }

    def generate_counterfactual_queries(self, finding: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate counterfactual queries for a finding

        Args:
            finding: Original finding with claim and evidence

        Returns:
            List of counterfactual queries to execute
        """
        queries = []
        claim = finding.get("claim", "")
        evidence = finding.get("evidence", [])

        # 1. Opposite search
        queries.append({
            "type": QueryType.OPPOSITE_SEARCH,
            "query": self._generate_opposite_query(claim),
            "purpose": "Find evidence that directly contradicts the claim",
            "priority": "HIGH"
        })

        # 2. Alternative explanations
        alternatives = self._generate_alternative_explanations(finding)
        for alt in alternatives:
            queries.append({
                "type": QueryType.ALTERNATIVE_EXPLANATION,
                "query": alt,
                "purpose": "Test benign/alternative explanation",
                "priority": "HIGH"
            })

        # 3. Missing evidence that would be expected
        queries.append({
            "type": QueryType.MISSING_EVIDENCE,
            "query": self._identify_missing_evidence(finding),
            "purpose": "What should exist if claim is true but doesn't?",
            "priority": "MEDIUM"
        })

        # 4. Statistical baseline
        queries.append({
            "type": QueryType.STATISTICAL_BASELINE,
            "query": self._generate_baseline_query(finding),
            "purpose": "Is this pattern normal or anomalous?",
            "priority": "MEDIUM"
        })

        # 5. Temporal inconsistency check
        queries.append({
            "type": QueryType.TEMPORAL_INCONSISTENCY,
            "query": self._check_temporal_consistency(finding),
            "purpose": "Does the timeline make logical sense?",
            "priority": "HIGH"
        })

        # 6. Contradictory sources
        queries.append({
            "type": QueryType.CONTRADICTORY_SOURCE,
            "query": self._find_contradictory_sources(evidence),
            "purpose": "Do other sources disagree?",
            "priority": "MEDIUM"
        })

        # 7. Null hypothesis
        queries.append({
            "type": QueryType.NULL_HYPOTHESIS,
            "query": self._test_null_hypothesis(finding),
            "purpose": "What if there's no real effect?",
            "priority": "LOW"
        })

        return queries

    def _generate_opposite_query(self, claim: str) -> str:
        """Generate query to find opposite evidence"""

        # Key inversions
        inversions = {
            "increases": "decreases",
            "collaborates": "competes",
            "exports": "blocks exports",
            "shares": "restricts",
            "joint": "independent",
            "together": "separately",
            "provides": "denies",
            "allows": "prohibits"
        }

        query = claim.lower()
        for original, opposite in inversions.items():
            if original in query:
                query = query.replace(original, opposite)
                break

        return f"Evidence for: {query}"

    def _generate_alternative_explanations(self, finding: Dict) -> List[str]:
        """Generate alternative explanations for observed pattern"""

        alternatives = []
        claim = finding.get("claim", "")

        # Standard alternative patterns
        if "collaboration" in claim.lower():
            alternatives.extend([
                "Commercial transaction without technology transfer",
                "Academic exchange without sensitive content",
                "Routine business relationship",
                "Historical relationship now terminated"
            ])

        if "technology transfer" in claim.lower():
            alternatives.extend([
                "Public domain technology",
                "Commercially available product",
                "Licensed under normal terms",
                "Obsolete technology"
            ])

        if "increase" in claim.lower():
            alternatives.extend([
                "Normal business growth",
                "Market expansion unrelated to China",
                "Statistical fluctuation",
                "Data collection improvement"
            ])

        return alternatives[:5]  # Limit to 5 alternatives

    def _identify_missing_evidence(self, finding: Dict) -> str:
        """Identify evidence that should exist if claim is true"""

        claim = finding.get("claim", "")

        missing_patterns = []

        if "partnership" in claim.lower():
            missing_patterns.append("MOU or formal agreement")
            missing_patterns.append("Joint publications")
            missing_patterns.append("Co-located facilities")

        if "technology" in claim.lower():
            missing_patterns.append("Patent filings")
            missing_patterns.append("Export licenses")
            missing_patterns.append("Technical specifications")

        if "funding" in claim.lower():
            missing_patterns.append("Financial disclosures")
            missing_patterns.append("Grant records")
            missing_patterns.append("Investment filings")

        return f"Search for missing: {', '.join(missing_patterns[:3])}"

    def _generate_baseline_query(self, finding: Dict) -> str:
        """Generate query to establish statistical baseline"""

        # Extract metrics from finding
        metrics = finding.get("metrics", {})

        return f"Baseline comparison: Similar organizations without China exposure"

    def _check_temporal_consistency(self, finding: Dict) -> str:
        """Check if timeline makes sense"""

        temporal_checks = [
            "Event sequence chronologically possible?",
            "Development timeline realistic?",
            "Announcements match actual activity?",
            "Historical precedent exists?"
        ]

        return f"Temporal validation: {temporal_checks[0]}"

    def _find_contradictory_sources(self, evidence: List[Dict]) -> str:
        """Find sources that contradict current evidence"""

        current_sources = [e.get("source", "") for e in evidence]

        # Identify alternative authoritative sources
        alternative_sources = []

        if not any("government" in s.lower() for s in current_sources):
            alternative_sources.append("government registry data")

        if not any("academic" in s.lower() for s in current_sources):
            alternative_sources.append("peer-reviewed publications")

        if not any("industry" in s.lower() for s in current_sources):
            alternative_sources.append("industry reports")

        return f"Check contradictory sources: {', '.join(alternative_sources)}"

    def _test_null_hypothesis(self, finding: Dict) -> str:
        """Test null hypothesis - no real effect"""

        return "Statistical test: Pattern exists in control group without China exposure?"

    def execute_counterfactual_search(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute counterfactual queries and evaluate evidence balance

        Returns:
            Dictionary with balance assessment and adjusted confidence
        """

        # Generate queries
        queries = self.generate_counterfactual_queries(finding)

        # Execute searches (simulated - in production would call actual search APIs)
        search_results = self._execute_searches(queries)

        # Evaluate balance
        balance = self._evaluate_evidence_balance(
            finding.get("evidence", []),
            search_results
        )

        # Calculate adjusted confidence
        original_confidence = finding.get("confidence", 0.5)
        adjusted_confidence = self._adjust_confidence(original_confidence, balance)

        # Log results
        self.query_log.append({
            "timestamp": datetime.now().isoformat(),
            "finding_id": finding.get("id", "unknown"),
            "queries_executed": len(queries),
            "balance": balance,
            "confidence_adjustment": adjusted_confidence - original_confidence
        })

        return {
            "original_confidence": original_confidence,
            "adjusted_confidence": adjusted_confidence,
            "evidence_balance": balance,
            "contradictions_found": balance["contradictory"],
            "recommendation": self._generate_recommendation(balance, adjusted_confidence),
            "counterfactual_queries": queries,
            "search_results": search_results
        }

    def _execute_searches(self, queries: List[Dict]) -> List[Dict]:
        """
        Execute actual searches (placeholder for integration)
        In production, this would call actual data source APIs
        """

        results = []

        for query in queries:
            # Simulate search execution
            result = {
                "query": query,
                "results_found": 0,  # Would be actual search count
                "relevance_score": 0.0,
                "evidence_type": "contradictory",  # or "confirmatory" or "neutral"
                "sources": []
            }

            # Simulate finding contradictory evidence ~30% of the time
            import random
            if random.random() < 0.3:
                result["results_found"] = random.randint(1, 10)
                result["relevance_score"] = random.random()
                result["evidence_type"] = "contradictory"
                self.evidence_balance["contradictory"] += result["results_found"]

            results.append(result)

        return results

    def _evaluate_evidence_balance(self,
                                  original_evidence: List[Dict],
                                  counterfactual_results: List[Dict]) -> Dict[str, Any]:
        """Evaluate balance between confirmatory and contradictory evidence"""

        confirmatory_count = len(original_evidence)
        contradictory_count = sum(
            r["results_found"] for r in counterfactual_results
            if r["evidence_type"] == "contradictory"
        )

        total = confirmatory_count + contradictory_count

        if total == 0:
            balance_ratio = 0.5
        else:
            balance_ratio = confirmatory_count / total

        return {
            "confirmatory": confirmatory_count,
            "contradictory": contradictory_count,
            "balance_ratio": balance_ratio,
            "assessment": self._assess_balance(balance_ratio)
        }

    def _assess_balance(self, ratio: float) -> str:
        """Assess evidence balance"""

        if ratio > 0.9:
            return "HEAVILY_BIASED_CONFIRMATORY"
        elif ratio > 0.75:
            return "MODERATELY_BIASED_CONFIRMATORY"
        elif ratio > 0.6:
            return "SLIGHTLY_BIASED_CONFIRMATORY"
        elif ratio > 0.4:
            return "BALANCED"
        elif ratio > 0.25:
            return "SLIGHTLY_BIASED_CONTRADICTORY"
        else:
            return "HEAVILY_BIASED_CONTRADICTORY"

    def _adjust_confidence(self, original: float, balance: Dict[str, Any]) -> float:
        """
        Adjust confidence based on evidence balance

        Penalizes unbalanced evidence patterns
        """

        ratio = balance["balance_ratio"]
        assessment = balance["assessment"]

        # Adjustment factors based on balance
        adjustments = {
            "HEAVILY_BIASED_CONFIRMATORY": -0.3,
            "MODERATELY_BIASED_CONFIRMATORY": -0.15,
            "SLIGHTLY_BIASED_CONFIRMATORY": -0.05,
            "BALANCED": 0.0,
            "SLIGHTLY_BIASED_CONTRADICTORY": -0.1,
            "HEAVILY_BIASED_CONTRADICTORY": -0.4
        }

        adjustment = adjustments.get(assessment, 0.0)

        # Apply adjustment
        adjusted = max(0.0, min(1.0, original + adjustment))

        return round(adjusted, 3)

    def _generate_recommendation(self, balance: Dict[str, Any], confidence: float) -> str:
        """Generate recommendation based on counterfactual analysis"""

        if balance["assessment"] == "HEAVILY_BIASED_CONFIRMATORY":
            return "HIGH_RISK: Severe confirmation bias detected. Require additional contradictory source search."

        elif balance["assessment"] == "BALANCED" and confidence > 0.7:
            return "VALIDATED: Finding withstands counterfactual testing."

        elif balance["contradictory"] > balance["confirmatory"]:
            return "RECONSIDER: Substantial contradictory evidence found. Re-evaluate finding."

        elif confidence < 0.5:
            return "INSUFFICIENT: Low confidence after counterfactual testing. Gather more evidence."

        else:
            return "PROCEED_WITH_CAUTION: Some contradictory evidence exists. Document caveats."

    def generate_batch_report(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report for batch counterfactual analysis"""

        report = {
            "timestamp": datetime.now().isoformat(),
            "findings_tested": len(findings),
            "average_confidence_adjustment": 0.0,
            "balance_distribution": {},
            "high_risk_findings": [],
            "validated_findings": [],
            "recommendations": []
        }

        total_adjustment = 0.0

        for finding in findings:
            result = self.execute_counterfactual_search(finding)

            adjustment = result["adjusted_confidence"] - result["original_confidence"]
            total_adjustment += adjustment

            # Track distribution
            assessment = result["evidence_balance"]["assessment"]
            report["balance_distribution"][assessment] = \
                report["balance_distribution"].get(assessment, 0) + 1

            # Flag high-risk findings
            if "HIGH_RISK" in result["recommendation"]:
                report["high_risk_findings"].append({
                    "finding_id": finding.get("id"),
                    "claim": finding.get("claim"),
                    "risk": result["recommendation"]
                })

            # Track validated findings
            elif "VALIDATED" in result["recommendation"]:
                report["validated_findings"].append({
                    "finding_id": finding.get("id"),
                    "claim": finding.get("claim"),
                    "confidence": result["adjusted_confidence"]
                })

        report["average_confidence_adjustment"] = round(total_adjustment / len(findings), 3)

        # Generate overall recommendations
        if len(report["high_risk_findings"]) > len(findings) * 0.3:
            report["recommendations"].append(
                "CRITICAL: Over 30% of findings show severe confirmation bias. Review methodology."
            )

        if report["average_confidence_adjustment"] < -0.2:
            report["recommendations"].append(
                "Significant downward confidence adjustment. Strengthen evidence collection."
            )

        return report

def demonstrate_counterfactual_analysis():
    """Demonstrate counterfactual query system"""

    # Example finding
    finding = {
        "id": "FIND-001",
        "claim": "Italy collaborates extensively with China on quantum research",
        "confidence": 0.85,
        "evidence": [
            {"source": "OpenAlex", "type": "publications", "count": 45},
            {"source": "CORDIS", "type": "projects", "count": 3}
        ],
        "metrics": {
            "collaboration_papers": 45,
            "joint_projects": 3,
            "time_period": "2020-2025"
        }
    }

    engine = CounterfactualQueryEngine()

    print("="*70)
    print("COUNTERFACTUAL QUERY DEMONSTRATION")
    print("="*70)

    # Generate counterfactual queries
    queries = engine.generate_counterfactual_queries(finding)

    print(f"\nOriginal Claim: {finding['claim']}")
    print(f"Original Confidence: {finding['confidence']}")

    print("\nGenerated Counterfactual Queries:")
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. {query['type'].value}")
        print(f"   Query: {query['query']}")
        print(f"   Purpose: {query['purpose']}")
        print(f"   Priority: {query['priority']}")

    # Execute counterfactual search
    result = engine.execute_counterfactual_search(finding)

    print("\n" + "="*70)
    print("COUNTERFACTUAL ANALYSIS RESULTS")
    print("="*70)

    print(f"\nEvidence Balance:")
    print(f"  Confirmatory: {result['evidence_balance']['confirmatory']}")
    print(f"  Contradictory: {result['evidence_balance']['contradictory']}")
    print(f"  Balance Ratio: {result['evidence_balance']['balance_ratio']:.2f}")
    print(f"  Assessment: {result['evidence_balance']['assessment']}")

    print(f"\nConfidence Adjustment:")
    print(f"  Original: {result['original_confidence']}")
    print(f"  Adjusted: {result['adjusted_confidence']}")
    print(f"  Change: {result['adjusted_confidence'] - result['original_confidence']:+.3f}")

    print(f"\nRecommendation: {result['recommendation']}")

    return engine

def main():
    """Main execution"""
    engine = demonstrate_counterfactual_analysis()

    # Test batch processing
    print("\n" + "="*70)
    print("BATCH COUNTERFACTUAL ANALYSIS")
    print("="*70)

    test_findings = [
        {
            "id": "FIND-002",
            "claim": "Germany exports semiconductor equipment to China",
            "confidence": 0.75,
            "evidence": [{"source": "Trade data", "type": "exports"}]
        },
        {
            "id": "FIND-003",
            "claim": "UK universities train Chinese military researchers",
            "confidence": 0.90,
            "evidence": [{"source": "University records", "type": "students"}]
        }
    ]

    batch_report = engine.generate_batch_report(test_findings)

    print(f"\nFindings Tested: {batch_report['findings_tested']}")
    print(f"Average Confidence Adjustment: {batch_report['average_confidence_adjustment']:+.3f}")
    print(f"High Risk Findings: {len(batch_report['high_risk_findings'])}")
    print(f"Validated Findings: {len(batch_report['validated_findings'])}")

    if batch_report['recommendations']:
        print("\nRecommendations:")
        for rec in batch_report['recommendations']:
            print(f"  • {rec}")

if __name__ == "__main__":
    main()
