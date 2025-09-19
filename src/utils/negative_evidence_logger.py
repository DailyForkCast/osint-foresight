"""
Negative Evidence Logger
Critical for avoiding blind spots in intelligence analysis
As emphasized by ChatGPT across multiple phases
"""

import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvidenceType(Enum):
    """Types of negative evidence to track"""
    NOT_FOUND = "not_found"
    NO_ACTIVITY = "no_activity"
    BELOW_THRESHOLD = "below_threshold"
    DISCONTINUED = "discontinued"
    FALSE_POSITIVE = "false_positive"
    INSUFFICIENT_DATA = "insufficient_data"
    ACCESS_DENIED = "access_denied"
    CONTRADICTORY = "contradictory"


class SearchContext(Enum):
    """Context where we looked for evidence"""
    CONFERENCE = "conference"
    PROCUREMENT = "procurement"
    PATENTS = "patents"
    PUBLICATIONS = "publications"
    FUNDING = "funding"
    PARTNERSHIPS = "partnerships"
    STANDARDS = "standards"
    SUPPLY_CHAIN = "supply_chain"
    TALENT = "talent"
    FACILITIES = "facilities"


class NegativeEvidenceLogger:
    """
    System to track what we DON'T find - critical for accurate assessment
    Addresses ChatGPT's emphasis on documenting gaps and negative evidence
    """

    def __init__(self, base_path: str = "data/evidence"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.negative_log = self.base_path / "negative_evidence.json"
        self.gap_registry = self.base_path / "gap_registry.json"
        self.contradiction_log = self.base_path / "contradictions.json"

        # Load existing logs
        self.evidence = self.load_evidence()

        # Critical areas from ChatGPT analysis
        self.critical_gaps = {
            "student_numbers": {
                "description": "No reliable data on Chinese STEM students in Italy",
                "impact": "Cannot assess academic penetration",
                "mitigation": "Need academic census data"
            },
            "talent_programs": {
                "description": "Thousand Talents participation unknown",
                "impact": "Cannot track talent recruitment",
                "mitigation": "Cross-reference with publication data"
            },
            "conference_rosters": {
                "description": "Incomplete attendee lists 2020-2024",
                "impact": "Cannot track relationship building",
                "mitigation": "Archive future events, reconstruct from press"
            },
            "mou_transparency": {
                "description": "Many MoUs not publicly disclosed",
                "impact": "Hidden partnership risks",
                "mitigation": "Require mandatory disclosure"
            },
            "funding_chains": {
                "description": "Ultimate beneficial ownership unclear",
                "impact": "Hidden PRC funding possible",
                "mitigation": "Implement LEI parent chain tracking"
            },
            "arctic_relevance": {
                "description": "Italy not Arctic-adjacent",
                "impact": "Arctic analysis not applicable",
                "mitigation": "Focus on Mediterranean/Space instead"
            }
        }

    def load_evidence(self) -> Dict:
        """Load existing negative evidence log"""
        if self.negative_log.exists():
            with open(self.negative_log, 'r') as f:
                return json.load(f)
        return {
            "entries": [],
            "summary": {},
            "metadata": {"created": datetime.now().isoformat()}
        }

    def save_evidence(self):
        """Save evidence log to disk"""
        with open(self.negative_log, 'w') as f:
            json.dump(self.evidence, f, indent=2, default=str)

    def log_negative_evidence(
        self,
        search_target: str,
        context: SearchContext,
        evidence_type: EvidenceType,
        details: Dict[str, Any],
        confidence: float = 0.8
    ) -> str:
        """
        Log a negative evidence finding
        Returns evidence ID
        """
        # Generate ID
        evidence_id = f"NEG-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(self.evidence['entries']) + 1:04d}"

        # Create entry
        entry = {
            "evidence_id": evidence_id,
            "timestamp": datetime.now().isoformat(),
            "search_target": search_target,
            "context": context.value,
            "evidence_type": evidence_type.value,
            "confidence": confidence,
            "details": details,
            "implications": self.assess_implications(search_target, evidence_type, context),
            "follow_up_required": evidence_type in [
                EvidenceType.INSUFFICIENT_DATA,
                EvidenceType.ACCESS_DENIED,
                EvidenceType.CONTRADICTORY
            ]
        }

        # Add to log
        self.evidence["entries"].append(entry)

        # Update summary statistics
        self.update_summary(context, evidence_type)

        # Save
        self.save_evidence()

        logger.info(f"Logged negative evidence: {evidence_id} - {search_target} ({evidence_type.value})")

        # Check for patterns
        self.detect_patterns()

        return evidence_id

    def assess_implications(
        self,
        search_target: str,
        evidence_type: EvidenceType,
        context: SearchContext
    ) -> Dict:
        """
        Assess implications of negative evidence
        What does NOT finding something tell us?
        """
        implications = {
            "significance": "unknown",
            "alternative_explanations": [],
            "confidence_impact": 0,
            "collection_priority": "standard"
        }

        # NOT_FOUND can be significant
        if evidence_type == EvidenceType.NOT_FOUND:
            if context == SearchContext.CONFERENCE:
                implications["significance"] = "medium"
                implications["alternative_explanations"].append("May use different conference circuit")
                implications["alternative_explanations"].append("Direct bilateral engagement instead")
            elif context == SearchContext.PROCUREMENT:
                implications["significance"] = "low"
                implications["alternative_explanations"].append("May use intermediaries")
                implications["alternative_explanations"].append("Focus on other markets")
            elif context == SearchContext.TALENT:
                implications["significance"] = "high"
                implications["alternative_explanations"].append("Operating through other channels")
                implications["collection_priority"] = "high"

        # NO_ACTIVITY is important context
        elif evidence_type == EvidenceType.NO_ACTIVITY:
            implications["significance"] = "medium"
            implications["alternative_explanations"].append("Dormant but not terminated")
            implications["alternative_explanations"].append("Activity hidden or indirect")
            implications["confidence_impact"] = -0.1  # Slightly reduce confidence

        # INSUFFICIENT_DATA requires follow-up
        elif evidence_type == EvidenceType.INSUFFICIENT_DATA:
            implications["significance"] = "high"
            implications["collection_priority"] = "urgent"
            implications["confidence_impact"] = -0.3  # Significantly reduce confidence

        # CONTRADICTORY evidence is critical
        elif evidence_type == EvidenceType.CONTRADICTORY:
            implications["significance"] = "critical"
            implications["collection_priority"] = "urgent"
            implications["confidence_impact"] = -0.5  # Major confidence reduction
            self.log_contradiction(search_target, context)

        return implications

    def log_contradiction(self, target: str, context: SearchContext):
        """
        Log contradictory evidence for special handling
        """
        contradictions = []
        if self.contradiction_log.exists():
            with open(self.contradiction_log, 'r') as f:
                contradictions = json.load(f)

        contradictions.append({
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "context": context.value,
            "status": "unresolved",
            "priority": "high"
        })

        with open(self.contradiction_log, 'w') as f:
            json.dump(contradictions, f, indent=2)

    def update_summary(self, context: SearchContext, evidence_type: EvidenceType):
        """Update summary statistics"""
        if "summary" not in self.evidence:
            self.evidence["summary"] = {}

        context_key = context.value
        if context_key not in self.evidence["summary"]:
            self.evidence["summary"][context_key] = {}

        type_key = evidence_type.value
        if type_key not in self.evidence["summary"][context_key]:
            self.evidence["summary"][context_key][type_key] = 0

        self.evidence["summary"][context_key][type_key] += 1

    def detect_patterns(self):
        """
        Detect patterns in negative evidence
        Multiple "not found" in same area = systematic gap
        """
        patterns = {
            "systematic_gaps": [],
            "data_voids": [],
            "potential_deception": []
        }

        # Check for systematic gaps
        for context in SearchContext:
            context_entries = [
                e for e in self.evidence["entries"]
                if e["context"] == context.value
            ]

            not_found_count = sum(
                1 for e in context_entries
                if e["evidence_type"] == EvidenceType.NOT_FOUND.value
            )

            if not_found_count > 5:
                patterns["systematic_gaps"].append({
                    "context": context.value,
                    "count": not_found_count,
                    "assessment": "Likely systematic data gap or collection blind spot"
                })

        # Check for data voids (areas with no positive OR negative evidence)
        contexts_with_data = set(e["context"] for e in self.evidence["entries"])
        all_contexts = set(c.value for c in SearchContext)
        data_voids = all_contexts - contexts_with_data

        for void in data_voids:
            patterns["data_voids"].append({
                "context": void,
                "assessment": "No collection attempts - critical intelligence gap"
            })

        # Check for potential deception patterns
        contradictory = [
            e for e in self.evidence["entries"]
            if e["evidence_type"] == EvidenceType.CONTRADICTORY.value
        ]

        if len(contradictory) > 3:
            patterns["potential_deception"].append({
                "indicator": "Multiple contradictory findings",
                "count": len(contradictory),
                "assessment": "Possible disinformation or active concealment"
            })

        # Log patterns if significant
        if any(patterns.values()):
            patterns_file = self.base_path / f"patterns_{datetime.now().strftime('%Y%m%d')}.json"
            with open(patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
            logger.warning(f"Significant patterns detected: {patterns_file}")

        return patterns

    def generate_gap_report(self) -> Dict:
        """
        Generate comprehensive gap report
        Critical for honest intelligence assessment
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_negative_entries": len(self.evidence["entries"]),
            "by_type": {},
            "by_context": {},
            "critical_gaps": self.critical_gaps,
            "confidence_impacts": {},
            "collection_priorities": [],
            "patterns": self.detect_patterns()
        }

        # Analyze by type
        for entry in self.evidence["entries"]:
            evt = entry["evidence_type"]
            report["by_type"][evt] = report["by_type"].get(evt, 0) + 1

            ctx = entry["context"]
            report["by_context"][ctx] = report["by_context"].get(ctx, 0) + 1

            # Track confidence impacts
            impact = entry.get("implications", {}).get("confidence_impact", 0)
            if impact != 0:
                target = entry["search_target"]
                if target not in report["confidence_impacts"]:
                    report["confidence_impacts"][target] = 0
                report["confidence_impacts"][target] += impact

        # Identify collection priorities
        urgent = [
            e for e in self.evidence["entries"]
            if e.get("implications", {}).get("collection_priority") == "urgent"
        ]

        for entry in urgent:
            report["collection_priorities"].append({
                "target": entry["search_target"],
                "context": entry["context"],
                "reason": entry["evidence_type"]
            })

        # Calculate overall confidence adjustment
        total_impact = sum(report["confidence_impacts"].values())
        report["overall_confidence_adjustment"] = total_impact

        # Add recommendations
        report["recommendations"] = self.generate_recommendations(report)

        return report

    def generate_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on gaps"""
        recommendations = []

        # Check for systematic gaps
        if report["patterns"]["systematic_gaps"]:
            recommendations.append(
                "Systematic data gaps detected - review collection methodology"
            )

        # Check for data voids
        if report["patterns"]["data_voids"]:
            void_contexts = [v["context"] for v in report["patterns"]["data_voids"]]
            recommendations.append(
                f"Initiate collection in void areas: {', '.join(void_contexts)}"
            )

        # Check confidence impacts
        if report["overall_confidence_adjustment"] < -1.0:
            recommendations.append(
                "Significant negative evidence reducing confidence - caveat assessments"
            )

        # Check for insufficient data
        insufficient_count = report["by_type"].get(EvidenceType.INSUFFICIENT_DATA.value, 0)
        if insufficient_count > 5:
            recommendations.append(
                f"High insufficient data count ({insufficient_count}) - expand collection"
            )

        # Check for contradictions
        contradictory_count = report["by_type"].get(EvidenceType.CONTRADICTORY.value, 0)
        if contradictory_count > 0:
            recommendations.append(
                f"Resolve {contradictory_count} contradictory findings before assessment"
            )

        return recommendations


def demonstrate_negative_evidence():
    """Demonstrate negative evidence logging based on ChatGPT Italy analysis"""
    logger_instance = NegativeEvidenceLogger()

    # Log examples from ChatGPT's identified gaps

    # 1. Student numbers gap
    logger_instance.log_negative_evidence(
        search_target="Chinese STEM student numbers in Italy",
        context=SearchContext.TALENT,
        evidence_type=EvidenceType.INSUFFICIENT_DATA,
        details={
            "searched": ["University websites", "Ministry of Education", "Eurostat"],
            "found": "Aggregate foreign student data only",
            "missing": "Breakdown by nationality and field",
            "note": "COVID baseline disruption 2020-2022 makes trending difficult"
        },
        confidence=0.3
    )

    # 2. Conference rosters gap
    logger_instance.log_negative_evidence(
        search_target="Paris Air Show 2023 Italian delegation",
        context=SearchContext.CONFERENCE,
        evidence_type=EvidenceType.ACCESS_DENIED,
        details={
            "source": "Official roster",
            "issue": "Paywall/registration required",
            "alternative": "Press releases provide partial list",
            "completeness": "Estimated 30% coverage"
        },
        confidence=0.5
    )

    # 3. No military technology transfer (important negative)
    logger_instance.log_negative_evidence(
        search_target="Italy-China military technology transfer",
        context=SearchContext.PARTNERSHIPS,
        evidence_type=EvidenceType.NOT_FOUND,
        details={
            "searched": ["Defense procurement", "Export licenses", "Intelligence reports"],
            "period": "2020-2025",
            "result": "No confirmed military tech transfers",
            "caveat": "Dual-use technology transfers possible"
        },
        confidence=0.75
    )

    # 4. Arctic irrelevance (important context)
    logger_instance.log_negative_evidence(
        search_target="Italian Arctic technology development",
        context=SearchContext.FACILITIES,
        evidence_type=EvidenceType.NO_ACTIVITY,
        details={
            "rationale": "Italy not Arctic-adjacent",
            "focus": "Mediterranean and space technologies instead",
            "recommendation": "De-prioritize Arctic analysis for Italy"
        },
        confidence=0.95
    )

    # 5. Contradictory semiconductor evidence
    logger_instance.log_negative_evidence(
        search_target="STMicroelectronics Shenzhen operations",
        context=SearchContext.SUPPLY_CHAIN,
        evidence_type=EvidenceType.CONTRADICTORY,
        details={
            "source_1": "Reports SiC production in Shenzhen",
            "source_2": "Company denies manufacturing in China",
            "resolution": "Requires ground truth verification",
            "impact": "Critical for dual-exposure assessment"
        },
        confidence=0.4
    )

    # Generate gap report
    report = logger_instance.generate_gap_report()

    return report


def main():
    """Main entry point"""
    print("\n=== Negative Evidence Logger ===")
    print("Critical for avoiding intelligence blind spots")
    print("As emphasized throughout ChatGPT v6 analysis\n")

    # Run demonstration
    report = demonstrate_negative_evidence()

    print(f"Logged {report['total_negative_entries']} negative evidence entries")
    print(f"\nBy Type:")
    for evt, count in report["by_type"].items():
        print(f"  {evt}: {count}")

    print(f"\nBy Context:")
    for ctx, count in report["by_context"].items():
        print(f"  {ctx}: {count}")

    print(f"\nOverall Confidence Adjustment: {report['overall_confidence_adjustment']:.2f}")

    print(f"\nCritical Gaps Acknowledged:")
    for gap_name, gap_info in report["critical_gaps"].items():
        print(f"  • {gap_name}: {gap_info['description']}")

    print(f"\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  → {rec}")

    # Save report
    logger_instance = NegativeEvidenceLogger()
    report_file = logger_instance.base_path / "gap_assessment_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nFull report saved to: {report_file}")


if __name__ == "__main__":
    main()
