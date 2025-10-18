"""
Advanced Technology Classification for OpenAlex Analysis
Enhanced dual-use technology detection with context analysis
"""

import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict

class AdvancedTechnologyClassifier:
    """Advanced classifier for dual-use technologies in research papers"""

    def __init__(self):
        # Enhanced keyword patterns with context
        self.technology_patterns = {
            "artificial_intelligence": {
                "primary_keywords": [
                    "artificial intelligence", "machine learning", "deep learning",
                    "neural network", "computer vision", "natural language processing",
                    "reinforcement learning", "convolutional neural", "transformer model"
                ],
                "context_keywords": [
                    "surveillance", "facial recognition", "behavior prediction",
                    "autonomous weapon", "military ai", "defense application"
                ],
                "risk_indicators": [
                    "dual use", "military application", "surveillance system",
                    "autonomous targeting", "predictive policing"
                ],
                "risk_level": "CRITICAL"
            },

            "quantum_computing": {
                "primary_keywords": [
                    "quantum computing", "quantum communication", "quantum cryptography",
                    "quantum algorithm", "quantum entanglement", "quantum key distribution",
                    "quantum supremacy", "quantum annealing", "qubits"
                ],
                "context_keywords": [
                    "encryption breaking", "cryptographic attack", "secure communication",
                    "quantum radar", "quantum sensing"
                ],
                "risk_indicators": [
                    "cryptanalysis", "code breaking", "quantum advantage",
                    "post-quantum cryptography"
                ],
                "risk_level": "CRITICAL"
            },

            "semiconductors": {
                "primary_keywords": [
                    "semiconductor", "microprocessor", "integrated circuit",
                    "chip design", "lithography", "silicon wafer", "ASIC",
                    "system on chip", "processor architecture", "chip fabrication"
                ],
                "context_keywords": [
                    "advanced node", "EUV lithography", "chip shortage",
                    "supply chain", "foundry", "semiconductor equipment"
                ],
                "risk_indicators": [
                    "export control", "technology transfer", "critical semiconductor",
                    "advanced packaging", "high performance computing"
                ],
                "risk_level": "CRITICAL"
            },

            "biotechnology": {
                "primary_keywords": [
                    "biotechnology", "genetic engineering", "CRISPR", "gene therapy",
                    "synthetic biology", "bioengineering", "genome editing",
                    "protein design", "metabolic engineering"
                ],
                "context_keywords": [
                    "bioweapon", "biological warfare", "pathogen enhancement",
                    "gain of function", "dual use research"
                ],
                "risk_indicators": [
                    "pandemic potential", "biodefense", "biological agent",
                    "enhanced pathogenicity", "select agent"
                ],
                "risk_level": "HIGH"
            },

            "aerospace": {
                "primary_keywords": [
                    "aerospace", "satellite", "rocket", "missile", "space technology",
                    "launch vehicle", "hypersonic", "spacecraft", "orbital mechanics",
                    "propulsion system"
                ],
                "context_keywords": [
                    "military satellite", "reconnaissance", "ballistic missile",
                    "interceptor", "space weapon", "anti-satellite"
                ],
                "risk_indicators": [
                    "dual use", "military application", "strategic missile",
                    "space warfare", "kinetic weapon"
                ],
                "risk_level": "HIGH"
            },

            "nuclear_technology": {
                "primary_keywords": [
                    "nuclear reactor", "uranium enrichment", "nuclear fuel",
                    "fusion", "fission", "radioactive", "nuclear physics",
                    "reactor design", "nuclear material", "isotope separation"
                ],
                "context_keywords": [
                    "weapons grade", "proliferation", "nuclear weapon",
                    "enrichment technology", "plutonium"
                ],
                "risk_indicators": [
                    "weapons application", "proliferation risk", "nuclear security",
                    "fissile material", "nuclear export"
                ],
                "risk_level": "CRITICAL"
            },

            "telecommunications": {
                "primary_keywords": [
                    "5G", "6G", "wireless communication", "telecommunications",
                    "network infrastructure", "fiber optic", "cellular network",
                    "base station", "spectrum management"
                ],
                "context_keywords": [
                    "surveillance", "intelligence gathering", "backdoor",
                    "network security", "critical infrastructure"
                ],
                "risk_indicators": [
                    "supply chain security", "technology dependence",
                    "network vulnerability", "foreign equipment"
                ],
                "risk_level": "HIGH"
            },

            "cybersecurity": {
                "primary_keywords": [
                    "cybersecurity", "encryption", "cryptography",
                    "network security", "malware", "cyber warfare",
                    "intrusion detection", "vulnerability assessment"
                ],
                "context_keywords": [
                    "offensive cyber", "cyber weapon", "advanced persistent threat",
                    "zero day", "cyber attack"
                ],
                "risk_indicators": [
                    "dual use tool", "weaponization", "cyber espionage",
                    "critical infrastructure", "supply chain attack"
                ],
                "risk_level": "HIGH"
            },

            "advanced_materials": {
                "primary_keywords": [
                    "graphene", "carbon nanotube", "metamaterial",
                    "superconductor", "smart material", "composites",
                    "nanomaterial", "advanced ceramic", "polymer"
                ],
                "context_keywords": [
                    "stealth technology", "armor application", "sensor",
                    "military use", "defense application"
                ],
                "risk_indicators": [
                    "dual use", "military specification", "strategic material",
                    "export controlled", "defense contractor"
                ],
                "risk_level": "MEDIUM"
            },

            "energy_storage": {
                "primary_keywords": [
                    "battery technology", "energy storage", "lithium ion",
                    "fuel cell", "supercapacitor", "energy density",
                    "battery management", "power systems"
                ],
                "context_keywords": [
                    "military application", "electric vehicle", "grid storage",
                    "portable power", "critical mineral"
                ],
                "risk_indicators": [
                    "strategic importance", "supply chain", "mineral dependence",
                    "dual use", "defense application"
                ],
                "risk_level": "MEDIUM"
            }
        }

        # Compile regex patterns for efficiency
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, Dict[str, List[re.Pattern]]]:
        """Compile regex patterns for efficient matching"""
        compiled = {}

        for tech, patterns in self.technology_patterns.items():
            compiled[tech] = {}
            for pattern_type in ["primary_keywords", "context_keywords", "risk_indicators"]:
                compiled[tech][pattern_type] = [
                    re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                    for keyword in patterns.get(pattern_type, [])
                ]

        return compiled

    def classify_text(self, title: str, abstract: str = "", full_text: str = "") -> Dict[str, Dict]:
        """
        Classify text for dual-use technologies with confidence scoring

        Returns:
            Dict mapping technology names to classification details
        """
        # Combine all text
        combined_text = f"{title} {abstract} {full_text}".lower()

        classifications = {}

        for tech_name, patterns in self.compiled_patterns.items():
            classification = self._classify_single_technology(combined_text, tech_name, patterns)
            if classification["detected"]:
                classifications[tech_name] = classification

        return classifications

    def _classify_single_technology(self, text: str, tech_name: str, patterns: Dict) -> Dict:
        """Classify text for a single technology"""

        # Count matches for each pattern type
        primary_matches = sum(1 for pattern in patterns["primary_keywords"] if pattern.search(text))
        context_matches = sum(1 for pattern in patterns["context_keywords"] if pattern.search(text))
        risk_matches = sum(1 for pattern in patterns["risk_indicators"] if pattern.search(text))

        # Calculate confidence score
        total_primary = len(patterns["primary_keywords"])
        total_context = len(patterns["context_keywords"])
        total_risk = len(patterns["risk_indicators"])

        primary_score = primary_matches / max(total_primary, 1)
        context_score = context_matches / max(total_context, 1) if total_context > 0 else 0
        risk_score = risk_matches / max(total_risk, 1) if total_risk > 0 else 0

        # Weighted confidence calculation
        confidence = (primary_score * 0.6) + (context_score * 0.25) + (risk_score * 0.15)

        # Determine if technology is detected (require at least one primary match)
        detected = primary_matches > 0

        # Enhanced risk assessment
        base_risk = self.technology_patterns[tech_name]["risk_level"]
        enhanced_risk = self._assess_enhanced_risk(base_risk, risk_matches, context_matches)

        return {
            "detected": detected,
            "confidence": round(confidence, 3),
            "primary_matches": primary_matches,
            "context_matches": context_matches,
            "risk_matches": risk_matches,
            "base_risk_level": base_risk,
            "enhanced_risk_level": enhanced_risk,
            "dual_use_indicators": risk_matches > 0,
            "strategic_importance": self.technology_patterns[tech_name].get("strategic_importance", "")
        }

    def _assess_enhanced_risk(self, base_risk: str, risk_matches: int, context_matches: int) -> str:
        """Assess enhanced risk level based on context"""
        risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        base_index = risk_levels.index(base_risk)

        # Increase risk if dual-use indicators are present
        if risk_matches > 0:
            base_index = min(base_index + 1, len(risk_levels) - 1)

        # Increase risk if military/security context is present
        if context_matches > 1:
            base_index = min(base_index + 1, len(risk_levels) - 1)

        return risk_levels[base_index]

    def analyze_collaboration_risk(self, paper_technologies: Dict[str, Dict],
                                 countries: List[str], institutions: Dict[str, List[str]]) -> Dict:
        """Analyze collaboration risk based on technologies and participants"""

        # Count critical and high-risk technologies
        critical_techs = [tech for tech, data in paper_technologies.items()
                         if data["enhanced_risk_level"] == "CRITICAL"]
        high_risk_techs = [tech for tech, data in paper_technologies.items()
                          if data["enhanced_risk_level"] == "HIGH"]

        # Assess institutional risk (simplified)
        high_risk_institutions = self._identify_high_risk_institutions(institutions)

        # Calculate overall collaboration risk
        overall_risk = "LOW"
        risk_factors = []

        if critical_techs:
            overall_risk = "CRITICAL"
            risk_factors.append(f"Critical dual-use technologies: {', '.join(critical_techs)}")
        elif high_risk_techs:
            overall_risk = "HIGH"
            risk_factors.append(f"High-risk technologies: {', '.join(high_risk_techs)}")
        elif paper_technologies:
            overall_risk = "MEDIUM"
            risk_factors.append("Dual-use technologies present")

        if high_risk_institutions:
            risk_factors.append(f"High-risk institutions involved: {len(high_risk_institutions)}")
            if overall_risk in ["LOW", "MEDIUM"]:
                overall_risk = "HIGH"

        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "critical_technologies": critical_techs,
            "high_risk_technologies": high_risk_techs,
            "technology_count": len(paper_technologies),
            "dual_use_indicators": sum(1 for data in paper_technologies.values()
                                     if data["dual_use_indicators"]),
            "high_risk_institutions": high_risk_institutions
        }

    def _identify_high_risk_institutions(self, institutions: Dict[str, List[str]]) -> List[str]:
        """Identify potentially high-risk institutions (simplified heuristic)"""
        high_risk_keywords = [
            "military", "defense", "army", "navy", "air force", "strategic",
            "national defense", "academy of sciences", "technology university",
            "research institute", "laboratory"
        ]

        high_risk_institutions = []

        for country, inst_list in institutions.items():
            for inst in inst_list:
                inst_lower = inst.lower()
                if any(keyword in inst_lower for keyword in high_risk_keywords):
                    high_risk_institutions.append(f"{inst} ({country})")

        return high_risk_institutions

    def generate_technology_report(self, all_classifications: List[Dict]) -> Dict:
        """Generate summary report of technology classifications"""

        tech_summary = defaultdict(lambda: {
            "total_papers": 0,
            "confidence_scores": [],
            "risk_distribution": defaultdict(int),
            "dual_use_papers": 0
        })

        for classification in all_classifications:
            for tech, data in classification.items():
                tech_summary[tech]["total_papers"] += 1
                tech_summary[tech]["confidence_scores"].append(data["confidence"])
                tech_summary[tech]["risk_distribution"][data["enhanced_risk_level"]] += 1
                if data["dual_use_indicators"]:
                    tech_summary[tech]["dual_use_papers"] += 1

        # Calculate statistics
        final_report = {}
        for tech, data in tech_summary.items():
            avg_confidence = sum(data["confidence_scores"]) / len(data["confidence_scores"])
            final_report[tech] = {
                "total_papers": data["total_papers"],
                "average_confidence": round(avg_confidence, 3),
                "dual_use_percentage": round((data["dual_use_papers"] / data["total_papers"]) * 100, 2),
                "risk_distribution": dict(data["risk_distribution"]),
                "base_risk_level": self.technology_patterns[tech]["risk_level"]
            }

        return final_report


def main():
    """Test the technology classifier"""
    classifier = AdvancedTechnologyClassifier()

    # Test classifications
    test_papers = [
        {
            "title": "Deep Learning for Autonomous Vehicle Navigation",
            "abstract": "We present a neural network approach for autonomous driving using computer vision and reinforcement learning."
        },
        {
            "title": "Quantum Key Distribution for Secure Communications",
            "abstract": "Implementation of quantum cryptography protocols for unbreakable encryption systems."
        },
        {
            "title": "CRISPR Gene Editing in Agricultural Applications",
            "abstract": "Using genetic engineering techniques to enhance crop resistance and yield."
        }
    ]

    for i, paper in enumerate(test_papers, 1):
        print(f"\n=== Test Paper {i} ===")
        print(f"Title: {paper['title']}")

        classifications = classifier.classify_text(paper["title"], paper["abstract"])

        if classifications:
            for tech, data in classifications.items():
                print(f"\nTechnology: {tech}")
                print(f"  Confidence: {data['confidence']}")
                print(f"  Risk Level: {data['enhanced_risk_level']}")
                print(f"  Dual-use: {data['dual_use_indicators']}")
        else:
            print("No dual-use technologies detected")

if __name__ == "__main__":
    main()
