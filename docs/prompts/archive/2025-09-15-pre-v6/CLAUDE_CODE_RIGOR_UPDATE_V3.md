# Claude Code Rigor Update v3.0
## Enforcing Technology Value Assessment & Specificity Across All Phases

**Date:** 2025-09-14
**Purpose:** Ensure all Claude Code phases meet Leonardo-level analysis standards

---

## 🎯 Core Rigor Requirements

### Universal Principle
**"Generic statements about China risk are worthless. We need SPECIFIC technologies, EXACT overlaps, and QUANTIFIED strategic value."**

---

## 📊 Technology Value Framework (ALL PHASES)

### For EVERY technology mentioned, assess:

```python
def assess_technology_value(tech_item):
    """
    Mandatory assessment for any technology/product/service
    """
    return {
        "technology_name": str,  # Specific, not generic
        "technology_readiness_level": int,  # TRL 1-9
        "advancement_category": {
            "cutting_edge": bool,  # TRL 6-8, <5 years old
            "mature": bool,  # TRL 9, 5-15 years old
            "commodity": bool  # TRL 9, >15 years old, widely available
        },
        "strategic_value_to_china": {
            "leapfrog_potential": int,  # Years of advancement (0-10+)
            "capability_gap_filled": str,  # Specific Chinese weakness addressed
            "alternatives_available": bool,  # Can China get elsewhere?
            "domestic_development_time": int  # Years for China to develop alone
        },
        "us_china_overlap": {
            "exact_same_product": bool,  # Identical item to both
            "shared_platform": bool,  # Common base, different config
            "technology_family": bool,  # Related but distinct
            "no_overlap": bool  # Completely different
        },
        "exploitation_specificity": {
            "physical_access": str,  # "Complete/Partial/None"
            "knowledge_transfer": str,  # "Direct/Indirect/None"
            "reverse_engineering": str,  # "Feasible/Difficult/Impossible"
            "countermeasure_development": list  # Specific countermeasures
        }
    }
```

---

## 🔧 Phase-Specific Rigor Updates

### Phase 0: Scoping
```python
def phase0_scoping_rigor(country):
    """
    Don't just list domains - assess strategic value
    """
    for domain in country.technology_domains:
        assessment = {
            "domain": domain.name,
            "global_ranking": domain.get_world_ranking(),  # Where does country stand?
            "china_interest_level": {
                "evidence": "Specific Chinese publications, investments, espionage cases",
                "intensity": "CRITICAL/HIGH/MEDIUM/LOW",
                "specific_targets": ["Named companies/labs/programs"]
            },
            "us_dependencies": {
                "programs": ["Named US programs using this country's tech"],
                "value": "Dollar amount or criticality assessment"
            }
        }
```

### Phase 1: Setup & Indicators
```python
def phase1_indicators_rigor(data_sources):
    """
    Not just 'innovation metrics' - specific technology tracking
    """
    metrics = {
        "patent_analysis": {
            "total_patents": int,  # Not interesting
            "breakthrough_patents": {  # THIS is interesting
                "quantum": ["Specific patent numbers"],
                "ai_military": ["Specific applications"],
                "hypersonics": ["Specific innovations"]
            },
            "china_co_patents": {  # CRITICAL
                "count": int,
                "technologies": ["Specific tech areas"],
                "entities": ["Named Chinese partners"]
            }
        }
    }
```

### Phase 2: Technology Indicators
```python
def phase2_technology_rigor(tech_landscape):
    """
    Move beyond categories to specific capabilities
    """
    for technology in tech_landscape:
        deep_analysis = {
            "generic_category": "AI",  # NOT SUFFICIENT
            "specific_capability": "Computer vision for drone target recognition",  # BETTER
            "exact_implementation": "YOLOv8 modified for IR imagery on edge devices",  # BEST
            "performance_metrics": {
                "accuracy": "98.5% on military vehicles",
                "speed": "30 FPS on Jetson Orin",
                "conditions": "Day/night, all weather"
            },
            "china_comparison": {
                "current_capability": "YOLOv5, 85% accuracy, day only",
                "gap_size": "2-3 years behind",
                "catch_up_timeline": "12-18 months with this technology"
            }
        }
```

### Phase 3: Technology Landscape
```python
def phase3_landscape_rigor(organizations):
    """
    Not just 'works on quantum' - specific quantum capabilities
    """
    for org in organizations:
        capability_assessment = {
            "vague": "Quantum research",  # UNACCEPTABLE
            "better": "Quantum computing research",  # STILL WEAK
            "specific": "Superconducting transmon qubits",  # BETTER
            "rigorous": {  # REQUIRED STANDARD
                "exact_capability": "5-qubit superconducting processor",
                "performance": "100μs coherence time",
                "breakthrough": "Novel error correction achieving 0.1% error rate",
                "china_relevance": "Addresses China's coherence time limitation",
                "us_programs_affected": ["DARPA ONISQ", "Army quantum sensing"],
                "exploitation_pathway": "Joint paper reveals fabrication process"
            }
        }
```

### Phase 4: Supply Chain
```python
def phase4_supply_chain_rigor(dependencies):
    """
    Not just 'depends on China' - exact dependencies and alternatives
    """
    for component in critical_components:
        dependency_analysis = {
            "component_specification": {
                "exact_part": "Neodymium-iron-boron magnets, Grade N52",
                "specifications": "1.44 Tesla, 150°C max temp",
                "application": "Leonardo AW139 tail rotor actuator"
            },
            "china_control": {
                "market_share": "87% global production",
                "specific_suppliers": ["Xiamen Tungsten", "JL MAG"],
                "supply_chain_depth": "Mining → Processing → Manufacturing"
            },
            "strategic_leverage": {
                "disruption_impact": "All helicopter production stops in 60 days",
                "military_programs_affected": ["MH-139", "CH-47F upgrades"],
                "china_exploitation": "Quality degradation, supply restriction, embedded trackers"
            },
            "alternatives": {
                "technical": "SmCo magnets - 30% performance loss",
                "suppliers": "Japan (20% capacity), US (5% capacity)",
                "timeline": "24 months to qualify alternatives",
                "cost_impact": "3.5x current cost"
            }
        }
```

### Phase 5: Institutions
```python
def phase5_institutions_rigor(institutions):
    """
    Not just 'university partnership' - specific research and personnel
    """
    for institution in institutions:
        partnership_analysis = {
            "surface_level": "MOU with Chinese university",  # NOT ENOUGH
            "required_depth": {
                "specific_program": "Joint PhD in hypersonic materials",
                "chinese_institution": "Beijing Institute of Technology",
                "personnel_exchange": {
                    "chinese_researchers_incoming": 12,
                    "their_focus": ["Scramjet cooling", "Heat shields"],
                    "access_level": "Classified test data via lab access"
                },
                "technology_transfer": {
                    "documented": ["3 joint patents", "15 joint papers"],
                    "suspected": ["Manufacturing process knowledge"],
                    "confirmed": ["Simulation software shared"]
                },
                "us_program_overlap": {
                    "program": "DARPA HAWC",
                    "same_lab": true,
                    "same_researchers": ["Dr. Smith works both programs"],
                    "isolation_measures": "None identified"
                }
            }
        }
```

### Phase 6: Funding
```python
def phase6_funding_rigor(funding_sources):
    """
    Not just 'Chinese investment exists' - follow the money precisely
    """
    for investment in chinese_investments:
        money_trail = {
            "surface": "€10M Chinese VC investment",  # INSUFFICIENT
            "required_analysis": {
                "investor_identity": {
                    "public_name": "Innovation Ventures Ltd",
                    "ultimate_owner": "Via 3 shells → State-owned Assets Commission",
                    "intelligence_links": "CEO former PLA Unit 61398"
                },
                "investment_terms": {
                    "board_seats": 2,
                    "veto_rights": ["Technology licensing", "US contracts"],
                    "information_rights": "Monthly technical reports"
                },
                "technology_access": {
                    "direct": "Source code for AI targeting system",
                    "indirect": "Customer list includes NATO members",
                    "personnel": "Right to place 3 'advisors' in company"
                },
                "strategic_purpose": {
                    "immediate": "Technology acquisition",
                    "medium": "Supply chain positioning",
                    "long_term": "Deny technology to US at critical moment"
                }
            }
        }
```

### Phase 7: International Links
```python
def phase7_links_rigor(collaborations):
    """
    Not just 'works with US and China' - map the exact triangles
    """
    for collaboration in international_partnerships:
        triangle_mapping = {
            "participants": {
                "us_entity": "MIT Lincoln Laboratory",
                "target_entity": "Politecnico Milano",
                "chinese_entity": "Tsinghua University"
            },
            "technology_focus": {
                "specific_area": "Photonic integrated circuits for quantum communication",
                "advancement_level": "World-leading, TRL 6",
                "publications": ["DOI:10.1234/specific_paper"]
            },
            "data_flow": {
                "us_to_target": "Quantum key distribution protocols",
                "target_to_china": "Photonic chip fabrication techniques",
                "triangle_completion": "China gets US QKD via Italian partnership"
            },
            "timeline": {
                "partnership_started": "2019",
                "technology_matured": "2023",
                "china_access_gained": "2024 via joint PhD student"
            }
        }
```

### Phase 8: Risk Assessment
```python
def phase8_risk_rigor(risks):
    """
    Not just 'high risk' - specific, actionable, quantified risks
    """
    for risk in identified_risks:
        actionable_assessment = {
            "vague_risk": "Technology transfer risk",  # USELESS
            "specific_risk": {
                "what": "YOLOv8 drone detection algorithm",
                "from": "University X AI lab",
                "to": "Beijing Institute via visiting researcher",
                "when": "Current - researcher returns December 2025",
                "impact": {
                    "immediate": "China improves drone detection 40%",
                    "military": "Defeats US stealth drone advantages",
                    "timeline": "Operational in 6-12 months"
                },
                "evidence": {
                    "confirmed": ["Researcher published related paper"],
                    "suspected": ["Lab access logs show unusual hours"],
                    "circumstantial": ["Sudden interest in export controls"]
                },
                "mitigation": {
                    "immediate": "Revoke lab access",
                    "medium": "Compartmentalize research",
                    "long_term": "Develop next-gen algorithm"
                }
            }
        }
```

### Phase 9-13: Advanced Analysis
```python
def advanced_phases_rigor(phase_data):
    """
    Every assessment must include:
    1. Specific technologies (not categories)
    2. Exact Chinese entities involved (not 'Chinese interests')
    3. Precise exploitation pathways (not 'dual-use concerns')
    4. Quantified impacts (not 'significant risk')
    5. Evidence chain (not assumptions)
    """

    required_elements = {
        "technology_specificity": {
            "bad": "AI capabilities",
            "good": "TensorFlow model for target recognition",
            "best": "Modified EfficientDet-D7 trained on NATO vehicle dataset"
        },
        "entity_precision": {
            "bad": "Chinese companies interested",
            "good": "Huawei and ZTE examining",
            "best": "Huawei 2012 Labs Munich office, Dr. Wei Zhang leading"
        },
        "pathway_detail": {
            "bad": "Possible technology transfer",
            "good": "Joint research enables transfer",
            "best": "CVE-2024-1234 in shared codebase allows data exfiltration"
        },
        "impact_quantification": {
            "bad": "Significant advantage to China",
            "good": "2-3 year advancement",
            "best": "Reduces US detection advantage from 15km to 3km"
        },
        "evidence_chain": {
            "bad": "Believed to be occurring",
            "good": "Pattern suggests transfer",
            "best": "Git commit a3f2b shows algorithm shared 2024-03-15"
        }
    }
```

---

## 🚫 Unacceptable Analysis Examples

### ❌ NEVER WRITE THIS:
- "Company X has operations in China (concern)"
- "Dual-use technology risks"
- "Potential for technology transfer"
- "May benefit Chinese military"
- "Could pose risks to US interests"
- "Significant China presence"

### ✅ ALWAYS WRITE THIS:
- "Company X sells EXACT_PRODUCT to China giving access to SPECIFIC_TECHNOLOGY"
- "TRL 7 quantum encryption system sold to both US Navy and Beijing University"
- "Chinese engineer from NORINCO working on same lab bench as DARPA project"
- "Algorithm achieves 98% accuracy, China currently at 67%, would save 4 years R&D"
- "Physical access to 40 units allows complete reverse engineering in 6 months"
- "Training manual reveals specific frequencies used by US military variant"

---

## 📋 Quality Checklist for Every Entity

### Minimum Requirements:
- [ ] Technology specified to component/algorithm level
- [ ] TRL assessment for maturity
- [ ] Years of advancement China would gain
- [ ] Exact overlap with US systems identified
- [ ] Physical/digital access level documented
- [ ] Specific countermeasures China could develop listed
- [ ] Timeline for exploitation provided
- [ ] Evidence with sources cited

### Excellence Indicators:
- [ ] Part numbers and specifications included
- [ ] Performance metrics quantified
- [ ] Chinese personnel named
- [ ] Exploitation pathway step-by-step
- [ ] US programs affected listed
- [ ] Mitigation costs calculated
- [ ] Alternative suppliers identified
- [ ] Historical precedents cited

---

## 🔍 Investigation Depth Examples

### Surface Level (Unacceptable):
"STMicroelectronics sells semiconductors to China"

### Basic (Minimum):
"STMicroelectronics sells SiC power semiconductors to Chinese EV manufacturers"

### Good (Expected):
"STMicroelectronics sells SiC MOSFETs (650V, 20A) used in both Tesla Model 3 inverters and similar components in F-35 power systems"

### Excellent (Target):
"STMicroelectronics SiC MOSFET part SCT30N120 sells to BYD for EV inverters. Same substrate technology and manufacturing process as SCT30N120M military variant in F-35 power management. Chinese reverse engineering would reveal thermal characteristics, failure modes, and optimal jamming frequencies for power disruption. Mitigation requires redesign of military variant with different substrate ($30M, 18 months)."

---

## ENFORCEMENT

Every Claude Code output will be audited against these standards. Responses lacking this specificity will be rejected and must be redone with proper rigor.
