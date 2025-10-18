# CLAUDE CODE — MASTER PROMPT v9.5 SEQUENTIAL
## Python-First OSINT Intelligence Framework with Sequential Phases (0-14)

**Version:** 9.5 SEQUENTIAL
**Date:** 2025-09-20
**Purpose:** Zero-fabrication Python implementation with complete sequential phase execution (0-14)
**Core Mission:**
  - PRIMARY: Identify how China exploits target countries to access US technology
  - SECONDARY: Document ALL Chinese exploitation to gain dual-use technology (even without US connection)
  - SCOPE: US angle always explored, but non-US dual-use exploitation equally important

---

## 1. CORE ARCHITECTURE

```python
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ConfidenceLevel(Enum):
    VERY_LOW = (0.0, 0.3, "Very low confidence - speculative")
    LOW = (0.3, 0.5, "Low confidence - provisional finding")
    MEDIUM = (0.5, 0.7, "Medium confidence - likely accurate")
    HIGH = (0.7, 0.9, "High confidence - well evidenced")
    VERY_HIGH = (0.9, 1.0, "Very high confidence - multiply verified")

@dataclass
class Evidence:
    """Every claim must have evidence with verification"""
    url: str
    quote: str
    access_date: str  # UTC ISO-8601
    archived_url: str
    verification_method: str  # "sha256_for_downloads" | "wayback_url" | "cached_url" | "direct_quote"
    source_weight: float
    locator: Optional[str] = None  # page/section
    sha256_hash: Optional[str] = None  # ONLY for downloaded files

    def __post_init__(self):
        if self.verification_method == "sha256_for_downloads" and not self.sha256_hash:
            raise ValueError("SHA256 hash required for downloaded files")
        if self.sha256_hash and self.verification_method != "sha256_for_downloads":
            raise ValueError("SHA256 only valid for downloaded files, not web sources")
```

## 2. DATA INFRASTRUCTURE

```python
DATA_SOURCES = {
    "openalex": {
        "path": "F:/OSINT_Backups/openalex/",
        "size_gb": 420,
        "processing": "streaming_required",
        "contains": "250M+ academic papers"
    },
    "ted": {
        "path": "F:/TED_Data/monthly/",
        "size_gb": 24,
        "format": "tar.gz by month",
        "contains": "EU procurement contracts"
    },
    "cordis": {
        "path": "F:/2025-09-14 Horizons/",
        "size_gb": 0.19,
        "contains": "EU research projects"
    },
    "sec_edgar": {
        "path": "F:/OSINT_DATA/SEC_EDGAR/",
        "contains": "US corporate filings"
    },
    "patents": {
        "path": "F:/OSINT_DATA/EPO_PATENTS/",
        "contains": "European patents"
    }
}

def verify_data_access() -> Dict[str, bool]:
    """Verify all data sources are accessible"""
    status = {}
    for source, config in DATA_SOURCES.items():
        try:
            path = Path(config["path"])
            status[source] = path.exists()
            if status[source]:
                print(f"✓ {source}: {config['size_gb']}GB at {config['path']}")
            else:
                print(f"✗ {source}: NOT FOUND at {config['path']}")
        except Exception as e:
            status[source] = False
            print(f"✗ {source}: ERROR - {e}")
    return status
```

## 3. SEQUENTIAL PHASE FRAMEWORK (0-14)

```python
PHASE_DEFINITIONS = {
    "phase_0": {
        "name": "Setup & Context",
        "dependencies": [],
        "outputs": ["country_profile.json", "research_parameters.yaml", "threat_vectors.md"],
        "confidence_required": 0.0  # Setup phase
    },
    "phase_1": {
        "name": "Data Source Validation",
        "dependencies": ["phase_0"],
        "outputs": ["data_sources_validated.json", "collection_capabilities.yaml"],
        "confidence_required": 0.0  # Validation phase
    },
    "phase_2": {
        "name": "Technology Landscape",
        "dependencies": ["phase_1"],
        "outputs": ["technology_landscape.json", "china_overlap.json"],
        "confidence_required": 0.5
    },
    "phase_3": {
        "name": "Supply Chain Analysis",
        "dependencies": ["phase_2"],
        "outputs": ["supply_chain.json", "critical_dependencies.json"],
        "confidence_required": 0.6
    },
    "phase_4": {
        "name": "Institutions Mapping",
        "dependencies": ["phase_3"],
        "outputs": ["institutions.json", "personnel_flows.json"],
        "confidence_required": 0.5
    },
    "phase_5": {
        "name": "Funding Flows",
        "dependencies": ["phase_3"],
        "outputs": ["funding.json", "investment_patterns.json"],
        "confidence_required": 0.6
    },
    "phase_6": {
        "name": "International Links",
        "dependencies": ["phase_2", "phase_3", "phase_4", "phase_5"],
        "outputs": ["international_links.json", "collaboration_networks.json"],
        "confidence_required": 0.6
    },
    "phase_7": {
        "name": "Risk Assessment (Initial)",
        "dependencies": ["phase_6"],
        "outputs": ["risk_register.json", "vulnerability_map.json"],
        "confidence_required": 0.7
    },
    "phase_8": {
        "name": "China Strategy Assessment",
        "dependencies": ["phase_7"],
        "outputs": ["china_strategy.json", "targeting_priorities.json"],
        "confidence_required": 0.7
    },
    "phase_9": {
        "name": "Red Team Analysis",
        "dependencies": ["phase_7"],
        "outputs": ["red_team_findings.json", "alternative_hypotheses.json"],
        "confidence_required": 0.0  # Red team challenges everything
    },
    "phase_10": {
        "name": "Comprehensive Risk Assessment",
        "dependencies": ["phase_8", "phase_9"],
        "outputs": ["comprehensive_risk_matrix.json", "mitigation_strategies.json"],
        "confidence_required": 0.9  # Highest requirement
    },
    "phase_11": {
        "name": "Strategic Posture",
        "dependencies": ["phase_10"],
        "outputs": ["strategic_posture.json", "policy_contradictions.json"],
        "confidence_required": 0.7
    },
    "phase_12": {
        "name": "Foresight Analysis",
        "dependencies": ["phase_11"],
        "outputs": ["scenarios.json", "early_warning_indicators.json"],
        "confidence_required": 0.6
    },
    "phase_13": {
        "name": "Extended Analysis",
        "dependencies": ["phase_12"],
        "outputs": ["extended_findings.json", "cascade_analysis.json"],
        "confidence_required": 0.7
    },
    "phase_14": {
        "name": "Closeout & Handoff",
        "dependencies": ["phase_0", "phase_1", "phase_2", "phase_3", "phase_4",
                        "phase_5", "phase_6", "phase_7", "phase_8", "phase_9",
                        "phase_10", "phase_11", "phase_12", "phase_13"],
        "outputs": ["executive_brief.pdf", "master_findings.json", "implementation_roadmap.md"],
        "confidence_required": 0.8
    }
}

class PhaseOrchestrator:
    """Manages sequential phase execution"""

    def __init__(self):
        self.completed_phases = set()
        self.phase_outputs = {}

    def can_execute_phase(self, phase: str) -> Tuple[bool, List[str]]:
        """Check if phase dependencies are met"""
        if phase not in PHASE_DEFINITIONS:
            return False, [f"Unknown phase: {phase}"]

        missing = []
        for dep in PHASE_DEFINITIONS[phase]["dependencies"]:
            if dep not in self.completed_phases:
                missing.append(dep)

        return len(missing) == 0, missing

    def execute_phase(self, phase: str, country: str) -> Dict[str, Any]:
        """Execute a specific phase"""
        can_run, missing = self.can_execute_phase(phase)
        if not can_run:
            raise ValueError(f"Cannot execute {phase}. Missing: {missing}")

        print(f"Executing {phase}: {PHASE_DEFINITIONS[phase]['name']}")

        # Phase-specific execution
        if phase == "phase_0":
            return self._phase_0_setup(country)
        elif phase == "phase_1":
            return self._phase_1_validation()
        elif phase == "phase_2":
            return self._phase_2_technology()
        elif phase == "phase_3":
            return self._phase_3_supply_chain()
        elif phase == "phase_4":
            return self._phase_4_institutions()
        elif phase == "phase_5":
            return self._phase_5_funding()
        elif phase == "phase_6":
            return self._phase_6_international()
        elif phase == "phase_7":
            return self._phase_7_initial_risk()
        elif phase == "phase_8":
            return self._phase_8_china_strategy()
        elif phase == "phase_9":
            return self._phase_9_red_team()
        elif phase == "phase_10":
            return self._phase_10_comprehensive_risk()
        elif phase == "phase_11":
            return self._phase_11_strategic_posture()
        elif phase == "phase_12":
            return self._phase_12_foresight()
        elif phase == "phase_13":
            return self._phase_13_extended()
        elif phase == "phase_14":
            return self._phase_14_closeout()
        else:
            raise NotImplementedError(f"Phase {phase} not implemented")
```

## 4. PHASE IMPLEMENTATIONS

```python
class PhaseImplementations:
    """Detailed implementations for each phase"""

    def _phase_0_setup(self, country: str) -> Dict:
        """Phase 0: Setup & Context"""
        return {
            "country": country,
            "why_matters": self._analyze_strategic_importance(country),
            "china_connections": self._identify_known_connections(country),
            "technology_priorities": self._determine_tech_focus(country),
            "collection_strategy": self._plan_collection(country)
        }

    def _phase_1_validation(self) -> Dict:
        """Phase 1: Validate all data sources"""
        results = {}
        for source, config in DATA_SOURCES.items():
            results[source] = self._test_source_access(source, config)
        return results

    def _phase_2_technology(self) -> Dict:
        """Phase 2: Technology Landscape Analysis"""
        # MUST be specific
        return {
            "technologies": self._extract_specific_technologies(),
            "china_overlap": self._identify_china_overlap(),
            "dual_use": self._assess_dual_use_potential()
        }

    def _phase_3_supply_chain(self) -> Dict:
        """Phase 3: Supply Chain Analysis"""
        # Process TED data for procurement
        return {
            "chinese_suppliers": self._find_chinese_suppliers(),
            "critical_dependencies": self._identify_dependencies(),
            "single_points_failure": self._find_spof()
        }

    def _phase_4_institutions(self) -> Dict:
        """Phase 4: Map Institutions"""
        return {
            "universities": self._map_academic_institutions(),
            "companies": self._map_corporate_entities(),
            "government": self._map_government_agencies(),
            "china_mous": self._find_china_agreements()
        }

    def _phase_5_funding(self) -> Dict:
        """Phase 5: Track Funding Flows"""
        return {
            "government_rd": self._analyze_government_funding(),
            "chinese_investment": self._track_chinese_investment(),
            "eu_projects": self._analyze_cordis_funding(),
            "venture_capital": self._track_vc_in_sensitive_tech()
        }

    def _phase_6_international(self) -> Dict:
        """Phase 6: International Links"""
        return {
            "research_partnerships": self._map_research_collaborations(),
            "conference_networks": self._analyze_conference_attendance(),
            "standards_committees": self._track_standards_participation(),
            "sister_cities": self._identify_sister_city_programs()
        }

    def _phase_7_initial_risk(self) -> Dict:
        """Phase 7: Initial Risk Assessment"""
        return {
            "vulnerabilities": self._identify_vulnerabilities(),
            "threat_vectors": self._map_threat_vectors(),
            "control_gaps": self._assess_control_gaps(),
            "risk_register": self._create_risk_register()
        }

    def _phase_8_china_strategy(self) -> Dict:
        """Phase 8: Assess China's Strategy"""
        return {
            "targeting_priorities": self._analyze_china_priorities(),
            "collection_methods": self._identify_collection_methods(),
            "exploitation_pathways": self._map_exploitation_routes(),
            "success_indicators": self._identify_success_metrics()
        }

    def _phase_9_red_team(self) -> Dict:
        """Phase 9: Red Team Analysis"""
        return {
            "challenged_assumptions": self._challenge_all_assumptions(),
            "alternative_hypotheses": self._generate_alternatives(),
            "evidence_gaps": self._identify_evidence_gaps(),
            "deception_indicators": self._check_for_deception()
        }

    def _phase_10_comprehensive_risk(self) -> Dict:
        """Phase 10: Comprehensive Risk Assessment"""
        # HIGHEST CONFIDENCE REQUIREMENT (0.9)
        return {
            "technology_transfer_risks": self._assess_tech_transfer_risk(),
            "supply_chain_vulnerabilities": self._assess_supply_risk(),
            "personnel_compromise": self._assess_personnel_risk(),
            "cyber_exposure": self._assess_cyber_risk(),
            "regulatory_gaps": self._assess_regulatory_risk(),
            "mitigation_strategies": self._develop_mitigations()
        }

    def _phase_11_strategic_posture(self) -> Dict:
        """Phase 11: Strategic Posture Assessment"""
        return {
            "strategy_coherence": self._assess_strategy_coherence(),
            "policy_vs_reality": self._compare_policy_reality(),
            "conference_influence": self._assess_conference_strategy(),
            "standards_leadership": self._assess_standards_position(),
            "forecast_trajectory": self._forecast_12_24_months()
        }

    def _phase_12_foresight(self) -> Dict:
        """Phase 12: Foresight Analysis"""
        return {
            "immediate_risks": self._analyze_6_12_months(),
            "developing_threats": self._analyze_1_2_years(),
            "strategic_shifts": self._analyze_3_5_years(),
            "long_term": self._analyze_5_10_years(),
            "wild_cards": self._identify_wild_cards(),
            "early_warnings": self._develop_indicators()
        }

    def _phase_13_extended(self) -> Dict:
        """Phase 13: Extended Analysis"""
        return {
            "cross_domain": self._integrate_cross_domain(),
            "hidden_connections": self._reveal_hidden_links(),
            "second_order": self._analyze_second_order_effects(),
            "arctic": self._assess_arctic_implications(),
            "cascade_effects": self._model_cascade_effects()
        }

    def _phase_14_closeout(self) -> Dict:
        """Phase 14: Closeout & Handoff"""
        return {
            "executive_summary": self._create_executive_summary(),
            "top_findings": self._crystallize_findings(),
            "confidence_assessment": self._assess_overall_confidence(),
            "intelligence_gaps": self._document_gaps(),
            "recommendations": self._develop_recommendations(),
            "implementation_roadmap": self._create_roadmap(),
            "monitoring_dashboard": self._design_dashboard(),
            "lessons_learned": self._capture_lessons()
        }
```

## 5. EVIDENCE REQUIREMENTS

```python
class EvidenceValidator:
    """Validate all evidence meets requirements"""

    @staticmethod
    def validate_claim(claim: str, evidence: List[Evidence]) -> Tuple[bool, str]:
        """Every claim must have evidence"""
        if not evidence:
            return False, f"INSUFFICIENT_EVIDENCE: No evidence for '{claim}'"

        total_weight = sum(e.source_weight for e in evidence)

        # Critical findings can have single source
        if total_weight >= 0.3:
            return True, "Valid"

        return False, f"INSUFFICIENT_EVIDENCE: Weight {total_weight} < 0.3"

    @staticmethod
    def verify_technology_claim(tech: Dict) -> bool:
        """Leonardo Standard - 8 requirements"""
        required = [
            "specific_technology",  # Not generic
            "overlap_with_china",
            "access_mechanism",
            "exploitation_pathway",
            "timeline",
            "alternatives_tested",  # 5+ alternatives
            "oversight_gaps",
            "confidence_score"  # 0-20 with explanation
        ]

        missing = [r for r in required if r not in tech]
        if missing:
            raise ValueError(f"Technology claim missing: {missing}")

        if tech["alternatives_tested"] < 5:
            raise ValueError("Must test 5+ alternative explanations")

        return True
```

## 6. PROCESSING PATTERNS

```python
def process_openalex_streaming(country: str, batch_size: int = 10000):
    """Stream process 420GB OpenAlex data"""
    import gzip

    checkpoint_file = f"checkpoint_{country}.json"
    processed_count = 0
    china_collaborations = []

    # Load checkpoint if exists
    if Path(checkpoint_file).exists():
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)
            processed_count = checkpoint["processed"]
            china_collaborations = checkpoint["collaborations"]

    for file_path in Path("F:/OSINT_Backups/openalex/data/works/").rglob("*.gz"):
        with gzip.open(file_path, 'rt') as f:
            for line_num, line in enumerate(f):
                if line_num < processed_count:
                    continue  # Skip already processed

                paper = json.loads(line)

                # Check for country-China collaboration
                if has_country_china_collab(paper, country):
                    china_collaborations.append(extract_collaboration(paper))

                processed_count += 1

                # Save checkpoint every batch_size records
                if processed_count % batch_size == 0:
                    save_checkpoint(checkpoint_file, processed_count, china_collaborations)
                    print(f"Processed {processed_count:,} papers, found {len(china_collaborations)} collaborations")

    return china_collaborations

def process_ted_procurement(years: range, countries: List[str]):
    """Process TED data for multiple countries and years"""
    import tarfile

    all_contracts = []
    chinese_companies = load_chinese_entities()

    for year in years:
        for month in range(1, 13):
            archive = f"F:/TED_Data/monthly/{year}_{month:02d}.tar.gz"

            if not Path(archive).exists():
                continue

            with tarfile.open(archive) as tar:
                for member in tar:
                    if member.name.endswith('.xml'):
                        content = tar.extractfile(member).read()
                        contract = parse_ted_contract(content)

                        # Check if involves any EU country + China
                        for country in countries:
                            if is_country_china_contract(contract, country, chinese_companies):
                                all_contracts.append({
                                    "country": country,
                                    "year": year,
                                    "contract": contract
                                })

    return analyze_cross_country_patterns(all_contracts)
```

## 7. OUTPUT REQUIREMENTS

```python
class PhaseOutput:
    """Standard output format for each phase"""

    def __init__(self, phase: str, country: str):
        self.phase = phase
        self.country = country
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.findings = []
        self.evidence = []
        self.gaps = []

    def add_finding(self, finding: str, confidence: float, evidence: List[Evidence]):
        """Add a finding with evidence"""
        validator = EvidenceValidator()
        valid, msg = validator.validate_claim(finding, evidence)

        if not valid:
            self.gaps.append(msg)
            return

        self.findings.append({
            "finding": finding,
            "confidence": confidence,
            "confidence_label": self._get_confidence_label(confidence),
            "evidence_count": len(evidence),
            "evidence_refs": [e.url for e in evidence]
        })

        self.evidence.extend(evidence)

    def _get_confidence_label(self, conf: float) -> str:
        """Convert confidence score to label"""
        for level in ConfidenceLevel:
            min_conf, max_conf, label = level.value
            if min_conf <= conf < max_conf:
                return label
        return "Unknown confidence"

    def generate_report(self) -> Dict:
        """Generate phase report"""
        return {
            "phase": self.phase,
            "phase_name": PHASE_DEFINITIONS[self.phase]["name"],
            "country": self.country,
            "timestamp": self.timestamp,
            "summary": {
                "total_findings": len(self.findings),
                "high_confidence": len([f for f in self.findings if f["confidence"] >= 0.7]),
                "evidence_pieces": len(self.evidence),
                "gaps_identified": len(self.gaps)
            },
            "findings": self.findings,
            "evidence": [asdict(e) for e in self.evidence],
            "gaps": self.gaps,
            "next_phase": self._get_next_phase()
        }

    def _get_next_phase(self) -> Optional[str]:
        """Determine next phase in sequence"""
        phase_num = int(self.phase.split("_")[1])
        if phase_num < 14:
            return f"phase_{phase_num + 1}"
        return None
```

## 8. CRITICAL RULES & FABRICATION PREVENTION

```python
CRITICAL_RULES = """
1. NEVER FABRICATE: If no data, return INSUFFICIENT_EVIDENCE
2. ALWAYS VERIFY: Every number must trace to source + line
3. USE ACTUAL DATA: 445GB available - USE IT
4. SPECIFY TECHNOLOGY: "AW139 helicopter" not "helicopters"
5. TEST ALTERNATIVES: 5+ explanations for every pattern
6. INCLUDE LOW CONFIDENCE: Even 30% confidence findings included
7. MARK GAPS: [EVIDENCE GAP: specific missing element]
8. SHA256 ONLY FOR DOWNLOADS: Not for web sources
9. SEQUENTIAL PHASES: Must complete dependencies before proceeding
10. MULTI-COUNTRY ANALYSIS: Process ALL EU countries, not single country
11. MARK ALL EXAMPLES: Use [HYPOTHETICAL], [ILLUSTRATIVE], etc.
12. NEVER MIX REAL/FAKE: Segregate verified from illustrative
"""

FABRICATION_PREVENTION_PROTOCOL = {
    "marking_required": {
        "[VERIFIED DATA]": "For any real number with source",
        "[HYPOTHETICAL EXAMPLE]": "For illustrative scenarios",
        "[ILLUSTRATIVE ONLY]": "For example code/values",
        "[PROJECTION - NOT VERIFIED]": "For extrapolations"
    },

    "segregation_rules": [
        "Never mix real and hypothetical in same section",
        "Use obviously fake numbers (999, XXX) in examples",
        "Separate verified_findings from illustrative_scenarios"
    ],

    "verification_chain": {
        "every_number_needs": [
            "source_file: exact path",
            "extraction: query or line number",
            "verification: hash or reproduction",
            "timestamp: when extracted"
        ]
    },

    "prohibited": [
        "Extrapolating from single country to EU totals",
        "Using 'expected' without [PROJECTION] marker",
        "Mixing real data with examples",
        "Creating illustrative numbers that look real"
    ]
}

class FabricationChecker:
    """Enforce fabrication prevention rules"""

    @staticmethod
    def validate_number(value: Any, source: str) -> Tuple[bool, str]:
        """Check if a number has proper verification"""
        if isinstance(value, (int, float)):
            if not source or "EXAMPLE" in source or "ILLUSTRATIVE" in source:
                return False, f"Number {value} lacks verification source"
            if not any(marker in source for marker in ["[VERIFIED DATA]", "source:", "file:"]):
                return False, f"Number {value} not marked as verified"
        return True, "Valid"

    @staticmethod
    def check_document(content: str) -> List[str]:
        """Scan document for potential fabrication risks"""
        issues = []

        # Check for unmarked projections
        projection_terms = ["expected", "anticipated", "likely", "could be", "might reach"]
        for term in projection_terms:
            if term in content.lower() and "[PROJECTION" not in content:
                issues.append(f"Unmarked projection: '{term}' used without [PROJECTION] marker")

        # Check for mixed real/hypothetical
        if "[VERIFIED DATA]" in content and "[HYPOTHETICAL" in content:
            sections = content.split("\n\n")
            for section in sections:
                if "[VERIFIED DATA]" in section and "[HYPOTHETICAL" in section:
                    issues.append("Real and hypothetical data mixed in same section")

        # Check for realistic-looking fake numbers
        import re
        numbers = re.findall(r'\b\d+[.,]?\d*[BMK]?\b', content)
        for num in numbers:
            if num not in ["999", "XXX", "[NUMBER]"]:
                # Check if number has proper marking within 100 chars before
                context_start = max(0, content.index(num)-100)
                context = content[context_start:content.index(num)]
                if not any(marker in context for marker in
                          ["[VERIFIED", "[HYPOTHETICAL", "[ILLUSTRATIVE",
                           "[EXAMPLE", "source:", "file:"]):
                    issues.append(f"Unmarked number: {num}")

        return issues

def enforce_rules(output: Any) -> bool:
    """Enforce critical rules on output"""
    # Run fabrication checker
    if isinstance(output, str):
        issues = FabricationChecker.check_document(output)
        if issues:
            raise ValueError(f"Fabrication risks detected: {issues}")

    # Check for fabrication markers
    if contains_fabrication_markers(output):
        raise ValueError("Fabrication detected")

    # Verify evidence trails
    if not has_complete_evidence_trail(output):
        raise ValueError("Missing evidence trail")

    # Ensure specificity
    if contains_generic_technology(output):
        raise ValueError("Technology not specific enough")

    return True
```

## 9. EXECUTION EXAMPLE

```python
def run_complete_analysis(country: str, phases_to_run: Optional[List[str]] = None):
    """Run complete sequential analysis for a country"""

    orchestrator = PhaseOrchestrator()

    # Default to all phases in sequence
    if phases_to_run is None:
        phases_to_run = [f"phase_{i}" for i in range(15)]

    results = {}

    for phase in phases_to_run:
        # Check dependencies
        can_run, missing = orchestrator.can_execute_phase(phase)

        if not can_run:
            print(f"⚠️ Cannot run {phase}. Missing phases: {missing}")
            break

        print(f"\n{'='*60}")
        print(f"Executing {phase}: {PHASE_DEFINITIONS[phase]['name']}")
        print(f"{'='*60}")

        # Execute phase
        try:
            phase_results = orchestrator.execute_phase(phase, country)
            results[phase] = phase_results
            orchestrator.completed_phases.add(phase)

            # Save outputs
            output_file = f"artifacts/{country}/sequential/{phase}.json"
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(phase_results, f, indent=2)

            print(f"✅ {phase} completed successfully")

        except Exception as e:
            print(f"❌ {phase} failed: {e}")
            break

    # Generate master report
    master_report = {
        "country": country,
        "phases_completed": list(orchestrator.completed_phases),
        "phases_remaining": [p for p in phases_to_run if p not in orchestrator.completed_phases],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results
    }

    with open(f"artifacts/{country}/master_analysis.json", 'w') as f:
        json.dump(master_report, f, indent=2)

    return master_report

# Execute analysis
if __name__ == "__main__":
    # Run all phases sequentially
    results = run_complete_analysis("Italy", phases_to_run=None)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print(f"Phases completed: {len(results['phases_completed'])}/15")
    print(f"Output: artifacts/Italy/master_analysis.json")
```

---

**END v9.5 SEQUENTIAL - Complete Python Implementation with Sequential Phases 0-14**
