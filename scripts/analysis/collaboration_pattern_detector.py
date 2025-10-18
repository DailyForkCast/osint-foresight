"""
Advanced Collaboration Pattern Detection for OpenAlex Analysis
Detects strategic partnership patterns, talent acquisition, and technology transfer
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime

class CollaborationPatternDetector:
    """Detect strategic collaboration patterns in research papers"""

    def __init__(self):
        # Enhanced pattern definitions with context and risk assessment
        self.pattern_definitions = {
            "talent_acquisition": {
                "indicators": [
                    "visiting scholar", "visiting researcher", "visiting professor",
                    "joint PhD", "joint doctorate", "dual degree",
                    "postdoc exchange", "postdoctoral fellow",
                    "faculty hire", "faculty exchange", "faculty visit",
                    "student exchange", "scholar program", "fellowship program",
                    "research sabbatical", "guest researcher"
                ],
                "context_keywords": [
                    "talent program", "recruitment", "brain drain",
                    "knowledge transfer", "capacity building",
                    "international collaboration", "academic mobility"
                ],
                "risk_indicators": [
                    "strategic talent", "critical expertise", "defense research",
                    "dual use knowledge", "technology transfer"
                ],
                "risk_level": "HIGH",
                "description": "Brain drain and knowledge transfer through academic mobility"
            },

            "technology_transfer": {
                "indicators": [
                    "patent collaboration", "joint patent", "patent sharing",
                    "licensing agreement", "technology licensing",
                    "technology sharing", "knowledge transfer",
                    "IP collaboration", "intellectual property",
                    "joint invention", "technology commercialization",
                    "spin-off company", "startup collaboration"
                ],
                "context_keywords": [
                    "commercialization", "industry partnership",
                    "technology validation", "proof of concept",
                    "R&D collaboration", "innovation transfer"
                ],
                "risk_indicators": [
                    "dual use technology", "export controlled",
                    "military application", "strategic technology",
                    "critical capability"
                ],
                "risk_level": "CRITICAL",
                "description": "Direct dual-use technology acquisition and transfer"
            },

            "strategic_partnerships": {
                "indicators": [
                    "belt and road", "BRI", "one belt one road",
                    "sister university", "sister institution",
                    "Confucius Institute", "Confucius Classroom",
                    "strategic partnership", "strategic collaboration",
                    "MOU", "memorandum of understanding",
                    "framework agreement", "cooperation agreement",
                    "joint institute", "bilateral agreement"
                ],
                "context_keywords": [
                    "China initiative", "Chinese government",
                    "state sponsored", "national program",
                    "diplomatic cooperation", "soft power"
                ],
                "risk_indicators": [
                    "influence operation", "political influence",
                    "strategic positioning", "institutional capture",
                    "long term commitment"
                ],
                "risk_level": "HIGH",
                "description": "Influence operations and strategic institutional positioning"
            },

            "funding_influence": {
                "indicators": [
                    "China funding", "Chinese funding", "Chinese grant",
                    "NSFC", "National Natural Science Foundation of China",
                    "CAS funding", "Chinese Academy of Sciences",
                    "China scholarship", "Chinese government funding",
                    "state funding", "national key project",
                    "973 program", "863 program", "thousand talents"
                ],
                "context_keywords": [
                    "research direction", "agenda setting",
                    "strategic priorities", "national goals",
                    "government policy", "state objectives"
                ],
                "risk_indicators": [
                    "research steering", "agenda influence",
                    "strategic direction", "policy alignment",
                    "institutional dependence"
                ],
                "risk_level": "HIGH",
                "description": "Research direction influence through funding mechanisms"
            },

            "institution_building": {
                "indicators": [
                    "joint institute", "joint laboratory", "joint center",
                    "research center", "collaboration center",
                    "international center", "bilateral center",
                    "cooperation platform", "research platform",
                    "innovation hub", "technology park",
                    "joint facility", "shared facility"
                ],
                "context_keywords": [
                    "long term collaboration", "institutional framework",
                    "permanent presence", "infrastructure development",
                    "capacity building", "institutional development"
                ],
                "risk_indicators": [
                    "institutional capture", "long term presence",
                    "strategic foothold", "influence infrastructure",
                    "permanent access"
                ],
                "risk_level": "MEDIUM",
                "description": "Long-term institutional capture and influence infrastructure"
            },

            "defense_collaboration": {
                "indicators": [
                    "defense research", "military research", "national defense",
                    "defense contractor", "military contractor",
                    "defense agency", "military academy",
                    "defense laboratory", "weapons research",
                    "military technology", "defense application"
                ],
                "context_keywords": [
                    "classified research", "sensitive research",
                    "controlled technology", "restricted access",
                    "security clearance", "export control"
                ],
                "risk_indicators": [
                    "weapons development", "military capability",
                    "dual use research", "strategic advantage",
                    "national security"
                ],
                "risk_level": "CRITICAL",
                "description": "Direct defense and military research collaboration"
            },

            "supply_chain_integration": {
                "indicators": [
                    "supply chain", "manufacturing partnership",
                    "production collaboration", "joint manufacturing",
                    "vendor relationship", "supplier integration",
                    "industrial cooperation", "equipment sharing",
                    "component sourcing", "materials sourcing"
                ],
                "context_keywords": [
                    "critical materials", "rare earth",
                    "semiconductor supply", "advanced materials",
                    "manufacturing capacity", "production capability"
                ],
                "risk_indicators": [
                    "supply dependency", "critical dependence",
                    "strategic materials", "supply vulnerability",
                    "industrial espionage"
                ],
                "risk_level": "HIGH",
                "description": "Critical supply chain dependencies and vulnerabilities"
            }
        }

        # Compile patterns for efficiency
        self.compiled_patterns = self._compile_patterns()

        # Institution risk classifications
        self.institution_risk_keywords = {
            "CRITICAL": [
                "military", "defense", "army", "navy", "air force",
                "strategic", "national defense", "weapons",
                "intelligence", "security", "classified"
            ],
            "HIGH": [
                "academy of sciences", "national laboratory",
                "research institute", "technology university",
                "engineering university", "polytechnic"
            ],
            "MEDIUM": [
                "university", "college", "institute", "center"
            ]
        }

    def _compile_patterns(self) -> Dict[str, Dict[str, List[re.Pattern]]]:
        """Compile regex patterns for efficient matching"""
        compiled = {}

        for pattern_name, pattern_data in self.pattern_definitions.items():
            compiled[pattern_name] = {}
            for keyword_type in ["indicators", "context_keywords", "risk_indicators"]:
                compiled[pattern_name][keyword_type] = [
                    re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    for keyword in pattern_data.get(keyword_type, [])
                ]

        return compiled

    def detect_patterns(self, paper: Dict, institutions: Dict[str, List[str]],
                       authors: Dict[str, List[str]], funding_info: List[Dict] = None) -> Dict:
        """
        Comprehensive pattern detection for a research paper

        Args:
            paper: Paper metadata (title, abstract, etc.)
            institutions: Institutions by country
            authors: Authors by country
            funding_info: Funding information

        Returns:
            Dict with detected patterns and risk assessment
        """
        # Combine all text for analysis
        full_text = self._combine_text(paper, funding_info or [])

        detected_patterns = {}

        # Detect each pattern type
        for pattern_name, compiled_pattern in self.compiled_patterns.items():
            detection = self._detect_single_pattern(
                full_text, pattern_name, compiled_pattern, institutions, authors
            )
            if detection["detected"]:
                detected_patterns[pattern_name] = detection

        # Assess overall collaboration risk
        overall_assessment = self._assess_overall_collaboration_risk(
            detected_patterns, institutions, authors
        )

        return {
            "detected_patterns": detected_patterns,
            "overall_assessment": overall_assessment,
            "pattern_count": len(detected_patterns),
            "highest_risk_level": overall_assessment["highest_risk_level"],
            "strategic_concerns": overall_assessment["strategic_concerns"]
        }

    def _combine_text(self, paper: Dict, funding_info: List[Dict]) -> str:
        """Combine all available text for pattern detection"""
        text_parts = []

        # Paper content
        if paper.get("title"):
            text_parts.append(paper["title"])
        if paper.get("abstract"):
            text_parts.append(paper["abstract"])

        # Funding information
        for grant in funding_info:
            if grant.get("funder", {}).get("display_name"):
                text_parts.append(grant["funder"]["display_name"])
            if grant.get("award_title"):
                text_parts.append(grant["award_title"])

        # Keywords and concepts
        for concept in paper.get("concepts", []):
            if concept.get("display_name"):
                text_parts.append(concept["display_name"])

        return " ".join(text_parts).lower()

    def _detect_single_pattern(self, text: str, pattern_name: str,
                             compiled_pattern: Dict, institutions: Dict[str, List[str]],
                             authors: Dict[str, List[str]]) -> Dict:
        """Detect a single collaboration pattern"""

        # Count matches
        indicator_matches = sum(1 for pattern in compiled_pattern["indicators"] if pattern.search(text))
        context_matches = sum(1 for pattern in compiled_pattern["context_keywords"] if pattern.search(text))
        risk_matches = sum(1 for pattern in compiled_pattern["risk_indicators"] if pattern.search(text))

        # Institution-based detection
        institution_signals = self._detect_institutional_signals(pattern_name, institutions)

        # Calculate confidence
        total_indicators = len(self.pattern_definitions[pattern_name]["indicators"])
        total_context = len(self.pattern_definitions[pattern_name]["context_keywords"])
        total_risk = len(self.pattern_definitions[pattern_name]["risk_indicators"])

        indicator_score = indicator_matches / max(total_indicators, 1)
        context_score = context_matches / max(total_context, 1) if total_context > 0 else 0
        risk_score = risk_matches / max(total_risk, 1) if total_risk > 0 else 0
        institution_score = institution_signals["score"]

        # Weighted confidence
        confidence = (
            indicator_score * 0.4 +
            context_score * 0.2 +
            risk_score * 0.2 +
            institution_score * 0.2
        )

        # Detection threshold
        detected = (indicator_matches > 0 or institution_signals["detected"]) and confidence > 0.1

        # Risk assessment
        base_risk = self.pattern_definitions[pattern_name]["risk_level"]
        enhanced_risk = self._enhance_pattern_risk(base_risk, risk_matches, institution_signals)

        return {
            "detected": detected,
            "confidence": round(confidence, 3),
            "indicator_matches": indicator_matches,
            "context_matches": context_matches,
            "risk_matches": risk_matches,
            "institutional_signals": institution_signals,
            "base_risk_level": base_risk,
            "enhanced_risk_level": enhanced_risk,
            "description": self.pattern_definitions[pattern_name]["description"],
            "evidence": self._collect_evidence(text, compiled_pattern, institution_signals)
        }

    def _detect_institutional_signals(self, pattern_name: str,
                                    institutions: Dict[str, List[str]]) -> Dict:
        """Detect pattern signals from institutional affiliations"""
        signals = {
            "detected": False,
            "score": 0.0,
            "high_risk_institutions": [],
            "pattern_specific_institutions": []
        }

        # Pattern-specific institutional indicators
        pattern_institutions = {
            "talent_acquisition": ["university", "academy", "institute", "college"],
            "technology_transfer": ["laboratory", "research center", "innovation", "technology"],
            "defense_collaboration": ["military", "defense", "army", "navy", "air force", "strategic"],
            "funding_influence": ["academy of sciences", "national", "government"],
            "institution_building": ["joint", "international", "collaboration", "center"],
            "strategic_partnerships": ["confucius", "partnership", "cooperation"],
            "supply_chain_integration": ["manufacturing", "industrial", "production", "materials"]
        }

        pattern_keywords = pattern_institutions.get(pattern_name, [])

        total_institutions = 0
        matching_institutions = 0

        for country, inst_list in institutions.items():
            for inst in inst_list:
                total_institutions += 1
                inst_lower = inst.lower()

                # Check for pattern-specific keywords
                if any(keyword in inst_lower for keyword in pattern_keywords):
                    matching_institutions += 1
                    signals["pattern_specific_institutions"].append(f"{inst} ({country})")

                # Check for high-risk institution indicators
                for risk_level, keywords in self.institution_risk_keywords.items():
                    if any(keyword in inst_lower for keyword in keywords):
                        if risk_level in ["CRITICAL", "HIGH"]:
                            signals["high_risk_institutions"].append({
                                "institution": f"{inst} ({country})",
                                "risk_level": risk_level
                            })

        # Calculate institutional score
        if total_institutions > 0:
            signals["score"] = matching_institutions / total_institutions
            signals["detected"] = matching_institutions > 0

        return signals

    def _enhance_pattern_risk(self, base_risk: str, risk_matches: int,
                            institution_signals: Dict) -> str:
        """Enhance risk level based on additional indicators"""
        risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        base_index = risk_levels.index(base_risk)

        # Increase risk for direct risk indicators
        if risk_matches > 0:
            base_index = min(base_index + 1, len(risk_levels) - 1)

        # Increase risk for high-risk institutions
        critical_institutions = [
            inst for inst in institution_signals.get("high_risk_institutions", [])
            if inst.get("risk_level") == "CRITICAL"
        ]
        if critical_institutions:
            base_index = min(base_index + 1, len(risk_levels) - 1)

        return risk_levels[base_index]

    def _collect_evidence(self, text: str, compiled_pattern: Dict,
                         institution_signals: Dict) -> Dict:
        """Collect specific evidence for detected patterns"""
        evidence = {
            "text_matches": [],
            "institutional_evidence": institution_signals.get("pattern_specific_institutions", []),
            "high_risk_institutions": institution_signals.get("high_risk_institutions", [])
        }

        # Find specific text matches (sample - in production would extract actual matches)
        for pattern_type in ["indicators", "context_keywords", "risk_indicators"]:
            for pattern in compiled_pattern[pattern_type]:
                matches = pattern.findall(text)
                if matches:
                    evidence["text_matches"].extend(matches)

        return evidence

    def _assess_overall_collaboration_risk(self, detected_patterns: Dict,
                                         institutions: Dict[str, List[str]],
                                         authors: Dict[str, List[str]]) -> Dict:
        """Assess overall collaboration risk based on all detected patterns"""

        if not detected_patterns:
            return {
                "highest_risk_level": "LOW",
                "strategic_concerns": [],
                "risk_score": 0.0,
                "pattern_diversity": 0
            }

        # Find highest risk level
        risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        highest_risk = max(
            [data["enhanced_risk_level"] for data in detected_patterns.values()],
            key=lambda x: risk_levels.index(x)
        )

        # Count high-risk patterns
        high_risk_patterns = [
            name for name, data in detected_patterns.items()
            if data["enhanced_risk_level"] in ["HIGH", "CRITICAL"]
        ]

        # Generate strategic concerns
        strategic_concerns = []

        if "defense_collaboration" in detected_patterns:
            strategic_concerns.append("Direct defense research collaboration detected")

        if "technology_transfer" in detected_patterns:
            strategic_concerns.append("Technology transfer mechanisms identified")

        if "talent_acquisition" in detected_patterns:
            strategic_concerns.append("Talent acquisition patterns present")

        if "funding_influence" in detected_patterns:
            strategic_concerns.append("Chinese funding influence detected")

        if len(high_risk_patterns) > 2:
            strategic_concerns.append("Multiple high-risk collaboration patterns")

        # Calculate risk score
        pattern_scores = [data["confidence"] for data in detected_patterns.values()]
        avg_confidence = sum(pattern_scores) / len(pattern_scores)
        risk_multiplier = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}[highest_risk]
        risk_score = avg_confidence * risk_multiplier * min(len(detected_patterns) / 3, 1.0)

        return {
            "highest_risk_level": highest_risk,
            "strategic_concerns": strategic_concerns,
            "risk_score": round(risk_score, 3),
            "pattern_diversity": len(detected_patterns),
            "high_risk_pattern_count": len(high_risk_patterns),
            "institutional_risk_count": sum(
                len(data.get("institutional_signals", {}).get("high_risk_institutions", []))
                for data in detected_patterns.values()
            )
        }

    def analyze_temporal_patterns(self, collaboration_history: List[Dict]) -> Dict:
        """Analyze how collaboration patterns evolve over time"""

        temporal_analysis = {
            "pattern_evolution": defaultdict(lambda: defaultdict(int)),
            "risk_escalation": [],
            "strategic_timing": [],
            "trend_analysis": {}
        }

        # Sort by year
        sorted_history = sorted(collaboration_history, key=lambda x: x.get("year", 0))

        # Track pattern evolution
        for collab in sorted_history:
            year = collab.get("year", 0)
            patterns = collab.get("detected_patterns", {})

            for pattern_name in patterns.keys():
                temporal_analysis["pattern_evolution"][pattern_name][year] += 1

        # Identify risk escalation periods
        for pattern_name, yearly_data in temporal_analysis["pattern_evolution"].items():
            years = sorted(yearly_data.keys())
            if len(years) >= 3:
                recent_avg = sum(yearly_data[y] for y in years[-3:]) / 3
                early_avg = sum(yearly_data[y] for y in years[:3]) / 3

                if recent_avg > early_avg * 1.5:
                    temporal_analysis["risk_escalation"].append({
                        "pattern": pattern_name,
                        "trend": "INCREASING",
                        "magnitude": round(recent_avg / max(early_avg, 1), 2)
                    })

        return temporal_analysis

    def generate_pattern_report(self, all_detections: List[Dict]) -> Dict:
        """Generate comprehensive pattern detection report"""

        pattern_summary = defaultdict(lambda: {
            "total_occurrences": 0,
            "average_confidence": 0.0,
            "risk_distribution": defaultdict(int),
            "confidence_scores": []
        })

        # Aggregate statistics
        for detection in all_detections:
            for pattern_name, pattern_data in detection.get("detected_patterns", {}).items():
                pattern_summary[pattern_name]["total_occurrences"] += 1
                pattern_summary[pattern_name]["confidence_scores"].append(pattern_data["confidence"])
                pattern_summary[pattern_name]["risk_distribution"][pattern_data["enhanced_risk_level"]] += 1

        # Calculate final statistics
        final_report = {}
        for pattern_name, data in pattern_summary.items():
            if data["confidence_scores"]:
                avg_confidence = sum(data["confidence_scores"]) / len(data["confidence_scores"])
                final_report[pattern_name] = {
                    "total_occurrences": data["total_occurrences"],
                    "average_confidence": round(avg_confidence, 3),
                    "risk_distribution": dict(data["risk_distribution"]),
                    "base_risk_level": self.pattern_definitions[pattern_name]["risk_level"],
                    "description": self.pattern_definitions[pattern_name]["description"]
                }

        return final_report


def main():
    """Test the collaboration pattern detector"""
    detector = CollaborationPatternDetector()

    # Test paper
    test_paper = {
        "title": "Joint AI Research for Autonomous Systems with Defense Applications",
        "abstract": "Collaboration between MIT and Tsinghua University under Belt and Road Initiative funding for military AI systems."
    }

    test_institutions = {
        "US": ["Massachusetts Institute of Technology"],
        "CN": ["Tsinghua University", "Chinese Academy of Sciences"]
    }

    test_authors = {
        "US": ["John Smith (MIT)"],
        "CN": ["Li Wei (Tsinghua)", "Zhang Ming (CAS)"]
    }

    test_funding = [
        {
            "funder": {"display_name": "National Natural Science Foundation of China"},
            "award_title": "Strategic Defense Technology Research"
        }
    ]

    print("=== Collaboration Pattern Detection Test ===")
    results = detector.detect_patterns(test_paper, test_institutions, test_authors, test_funding)

    print(f"\nPatterns detected: {results['pattern_count']}")
    print(f"Highest risk level: {results['highest_risk_level']}")

    for pattern_name, pattern_data in results["detected_patterns"].items():
        print(f"\n{pattern_name}:")
        print(f"  Confidence: {pattern_data['confidence']}")
        print(f"  Risk Level: {pattern_data['enhanced_risk_level']}")
        print(f"  Description: {pattern_data['description']}")

    print(f"\nStrategic Concerns:")
    for concern in results["overall_assessment"]["strategic_concerns"]:
        print(f"  - {concern}")

if __name__ == "__main__":
    main()
