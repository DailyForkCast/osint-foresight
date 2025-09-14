# Claude Code Implementation Prompt v1.7 FINAL - NATO Enhanced
## Technical Implementation Framework for OSINT Foresight

**Version:** 1.7 FINAL
**Updated:** 2025-09-13
**Framework:** Full phase implementation with NATO integration

**Role:** Technical implementer. Build data pipelines, execute collection scripts, validate schemas, and respond to ChatGPT tickets.

---

## CRITICAL: Phase Execution Checklist
**MANDATORY**: Execute ALL phases. Verify before completion:
```
□ Phase 0: Taxonomy (phase00_taxonomy.json)
□ Phase 1: Setup (phase01_setup.json, phase01_sub5_narratives.json)
□ Phase 2: Indicators (phase02_indicators.json)
□ Phase 3: Landscape (phase03_landscape.json, phase03_sub4_nato_policies.json)
□ Phase 4: Supply Chain (phase04_supply_chain.json, phase04_sub5_nato_supply_nodes.json)
□ Phase 5: Institutions (phase05_institutions.json, phase05_sub7_diana_sites.json)
□ Phase 6: Funders (phase06_funders.json)
□ Phase 7: Links (phase07_links.json, phase07_sub5_nato_links.json)
□ Phase 8: Risk (phase08_risk.json)
□ Phase 9: PRC/MCF (phase09_posture.json) ← CRITICAL - OFTEN MISSED
□ Phase 10: Red Team (phase10_redteam.json) ← CRITICAL - OFTEN MISSED
□ Phase 11: Foresight (phase11_foresight.json, phase11_sub7_nato_ews.json)
□ Phase 12: Extended (phase12_extended.json) ← CRITICAL - OFTEN MISSED
□ Phase 13: Closeout (phase13_closeout.json)
```
**WARNING**: Phases 9, 10, 12 frequently skipped. MUST complete ALL phases.

## Runtime Configuration

```python
# Core settings
RUNTIME = "TOOL_AUGMENTED+ONLINE_QUERY"
FS_RW = True
WEBFETCH_CACHE = True
PARALLELIZATION = True
SCHEMA_VALIDATION = True

# Paths
DATA_DIR = "F:/OSINT_Data/country={{COUNTRY}}"
ARTIFACT_DIR = "./artifacts/{{COUNTRY}}/{{HUB|_national}}"
SCRIPTS_DIR = "./scripts"

# NATO Configuration
NATO_MEMBERS = [
    "AL", "BE", "BG", "CA", "HR", "CZ", "DK", "EE", "FI", "FR", "DE",
    "GR", "HU", "IS", "IT", "LV", "LT", "LU", "ME", "NL", "MK", "NO",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE", "TR", "UK", "US"
]

NATO_PARTNERS = {
    "EOP": ["UA"],  # Enhanced Opportunity Partner
    "MAP": ["BA"],  # Membership Action Plan
    "PfP": ["AT", "IE", "CH", "RS", "MD", "GE", "AM", "AZ"]
}

# Automation capabilities
AUTOMATED_STATS = [
    "DE", "FR", "NL", "NO", "DK", "UK", "SE", "CH", "IT", "ES",
    "AT", "FI", "IE", "PL", "BE", "CZ", "HU", "PT", "GR", "SI",
    "LU", "LT", "LV", "EE", "IS", "LI", "AD", "SM"
]

MANUAL_STATS = [
    "BG", "HR", "RO", "SK", "CY", "MT", "TR", "RS", "ME", "MK",
    "AL", "BA", "XK", "MD", "UA", "GE"
]
```

---

## Phase Implementation Scripts

### Phase 0: Taxonomy & Definitions
```python
def build_taxonomy():
    taxonomy = {
        "civilian_dual_use": [
            "AI & Autonomy", "Advanced Computing", "Quantum",
            "Communications", "Photonics", "Space", "Materials",
            "Energy", "Hypersonics", "Biotech", "Robotics",
            "Cyber", "Data Infra", "Smart Cities", "Climate"
        ],
        "nato_capabilities": {  # NEW
            "joint_enablers": ["ISR", "strategic_airlift", "AAR", "SATCOM"],
            "high_end_warfare": ["A2/AD", "precision_strike", "EW", "cyber"],
            "readiness": ["NRF", "VJTF", "EFP", "air_policing"],
            "emerging": ["AI", "quantum", "hypersonics", "space", "biotech"]
        },
        "key_terms": {
            "dual_use": "Civilian and military applications",
            "MCF": "Military-Civil Fusion (军民融合)",
            "STANAG": "NATO Standardization Agreement",
            "DIANA": "Defence Innovation Accelerator",
            "NIF": "NATO Innovation Fund"
        }
    }
    save_json("phase00_taxonomy.json", taxonomy)

    # Entity resolution registry
    registry = {
        "identifiers": {
            "institutions": ["ROR", "GRID"],
            "companies": ["LEI"],
            "researchers": ["ORCID"],
            "nato_facilities": ["NATO_CODE"],  # NEW
            "coes": ["COE_ID"]  # NEW
        }
    }
    save_json("id_registry.json", registry)
```

### Phase 2: Indicators Collection
```python
def collect_indicators(country):
    indicators = {}

    # Standard indicators
    if country in AUTOMATED_STATS:
        indicators.update(pull_automated_stats(country))
    else:
        log_manual_required(country)
        indicators.update(get_cached_stats(country))

    # NATO indicators (NEW)
    if country in NATO_MEMBERS:
        nato_indicators = {
            "defence_spending": collect_defence_spending(country),
            "equipment_ratio": calculate_equipment_ratio(country),
            "exercise_participation": count_exercises(country),
            "stanag_compliance": track_stanag_implementation(country),
            "diana_participation": check_diana_involvement(country),
            "nif_exposure": track_nif_investments(country),
            "coe_hosting": list_hosted_coes(country)
        }
        indicators["nato"] = nato_indicators

        # Check against targets
        if nato_indicators["defence_spending"]["gdp_percentage"] < 2.0:
            create_ticket("Low defence spending vs NATO target")

    save_json("phase02_indicators.json", indicators)
```

### Phase 3: Landscape with NATO
```python
def map_technology_landscape(country):
    landscape = {
        "actors": collect_actors(country),
        "policies": analyze_policies(country, POLICY_WINDOW),
        "infrastructure": map_infrastructure(country)
    }

    # NATO additions (NEW)
    if TOGGLES["INCLUDE_NATO"] and country in NATO_MEMBERS:
        nato_landscape = {
            "nato_commands": list_nato_commands(country),
            "nato_bases": list_nato_installations(country),
            "coes_hosted": get_hosted_coes(country),
            "diana_sites": get_diana_locations(country),
            "framework_role": check_framework_nation(country),
            "ndpp_alignment": assess_ndpp_compliance(country)
        }
        save_json("phase03_sub4_nato_policies.json", nato_landscape)

    save_json("phase03_landscape.json", landscape)
```

### Phase 4: Supply Chain with NATO
```python
def analyze_supply_chain(country):
    supply_chain = {
        "critical_components": identify_critical_components(country),
        "vendor_patterns": analyze_procurement_patterns(country),
        "supply_map": create_supply_chain_map(country)
    }

    # US-owned nodes
    if TOGGLES["INCLUDE_US_INVOLVEMENT"]:
        us_nodes = find_us_owned_suppliers(country)
        save_json("phase04_sub4_us_owned_supply.json", us_nodes)

    # NATO supply chain (NEW)
    if TOGGLES["INCLUDE_NATO"]:
        nato_supply = {
            "nspa_procurement": calculate_nspa_share(country),
            "stanag_requirements": map_stanag_components(country),
            "multinational_logistics": identify_shared_capabilities(country),
            "certification_bottlenecks": find_certification_delays(country)
        }
        save_json("phase04_sub5_nato_supply_nodes.json", nato_supply)

    save_json("phase04_supply_chain.json", supply_chain)
```

### Phase 5: Institutions with DIANA
```python
def resolve_institutions(country):
    institutions = {
        "entities": resolve_and_deduplicate_entities(country),
        "networks": build_collaboration_networks(country),
        "capabilities": create_capability_profiles(country)
    }

    # Hub discovery
    outliers = discover_outlier_centers(country)
    save_json("phase05_sub5_outlier_centers.json", outliers)

    auto_hubs = promote_qualified_hubs(outliers)
    save_json("phase05_sub6_auto_hubs.json", auto_hubs)

    # NATO DIANA/COE (NEW)
    if TOGGLES["INCLUDE_NATO"]:
        diana_footprint = {
            "accelerator_sites": find_diana_accelerators(country),
            "test_centers": find_test_facilities(country),
            "portfolio_companies": track_diana_startups(country),
            "coe_participation": map_coe_involvement(country)
        }
        save_json("phase05_sub7_diana_sites.json", diana_footprint)

    save_json("phase05_institutions.json", institutions)
```

### Phase 6: Funding with NATO Programs
```python
def track_funding(country):
    funding = {
        "public_grants": collect_public_funding(country),
        "private_investment": track_private_investment(country),
        "controls": map_funding_controls(country)
    }

    # US funding links
    if TOGGLES["INCLUDE_US_INVOLVEMENT"]:
        us_funding = track_us_eu_funding(country)
        save_json("phase06_sub6_us_funding_links.json", us_funding)

    # NATO funding (NEW)
    if TOGGLES["INCLUDE_NATO"]:
        nato_funding = {
            "diana_grants": track_diana_funding(country),
            "nif_investments": get_nif_portfolio(country),
            "sto_projects": list_sto_research_funding(country),
            "sps_programme": track_sps_grants(country),
            "nsip_infrastructure": get_nsip_funding(country)
        }
        save_json("phase06_sub7_nato_funding_links.json", nato_funding)

    save_json("phase06_funders.json", funding)
```

### Phase 7: International Links with NATO
```python
def analyze_international_links(country):
    links = {
        "research_collaboration": analyze_coauthorships(country),
        "technology_transfer": track_tech_transfer(country),
        "risk_patterns": identify_risk_patterns(country)
    }

    # US partnerships
    if TOGGLES["INCLUDE_US_INVOLVEMENT"]:
        us_links = map_us_partnerships(country)
        save_json("phase07_sub4_us_partner_links.json", us_links)

    # NATO cooperation (NEW)
    if TOGGLES["INCLUDE_NATO"]:
        nato_links = {
            "exercises": track_exercise_participation(country),
            "coe_collaboration": map_coe_partnerships(country),
            "sto_projects": list_sto_collaboration(country),
            "minilateral_formats": identify_minilateral_participation(country)
        }
        save_json("phase07_sub5_nato_links.json", nato_links)

        # STANAG mapping
        stanag_map = map_stanags_to_civil_standards()
        save_json("phase07_sub6_standards_stanag_map.json", stanag_map)

    save_json("phase07_links.json", links)
```

### Phase 8: Risk Assessment
```python
def assess_risks(country):
    risks = {
        "technology_risks": identify_tech_vulnerabilities(country),
        "supply_chain_risks": map_critical_dependencies(country),
        "talent_risks": assess_brain_drain(country),
        "investment_risks": screen_foreign_acquisitions(country),
        "cyber_risks": evaluate_cyber_posture(country)
    }

    # NATO-specific risks
    if TOGGLES["INCLUDE_NATO"]:
        nato_risks = {
            "article_5_credibility": assess_collective_defense_gaps(country),
            "capability_shortfalls": identify_ndpp_gaps(country),
            "interoperability_failures": find_stanag_issues(country),
            "burden_sharing_tensions": calculate_contribution_gaps(country)
        }
        risks["nato_risks"] = nato_risks

    save_json("phase08_risk.json", risks)
```

### Phase 9: PRC/MCF Assessment ⚠️ CRITICAL - OFTEN SKIPPED
```python
def assess_prc_mcf(country):
    """MANDATORY: Generate comprehensive China/PRC risk assessment"""
    prc_assessment = {
        "prc_interest": {
            "strategic_objectives": identify_prc_goals(country),
            "historical_context": {
                "bri_participation": check_bri_status(country),
                "peak_engagement": find_peak_period(country),
                "current_status": assess_current_relationship(country)
            }
        },
        "acquisition_mechanisms": [
            {
                "type": "licit",
                "method": "Academic collaboration",
                "volume": count_joint_papers(country),
                "trend": analyze_collaboration_trend(country)
            },
            {
                "type": "gray",
                "method": "Investment in strategic sectors",
                "controls": assess_screening_mechanisms(country),
                "blocked_cases": count_blocked_investments(country)
            },
            {
                "type": "illicit",
                "method": "Cyber espionage",
                "incidents": count_attributed_incidents(country),
                "response": evaluate_counter_measures(country)
            }
        ],
        "target_technologies": identify_prc_tech_interests(country),
        "early_warning_indicators": build_prc_ews(country)
    }

    # US counter-PRC coordination
    if TOGGLES["INCLUDE_US_INVOLVEMENT"]:
        us_coordination = assess_us_china_policy_alignment(country)
        prc_assessment["us_coordination"] = us_coordination

    save_json("phase09_posture.json", prc_assessment)
    print("⚠️ Phase 9 PRC/MCF assessment completed - CRITICAL for executive brief")
```

### Phase 10: Red Team Analysis ⚠️ CRITICAL - OFTEN SKIPPED
```python
def red_team_analysis(country):
    """MANDATORY: Challenge assumptions and test alternative hypotheses"""
    red_team = {
        "assumption_challenges": [
            {
                "assumption": identify_key_assumption(),
                "challenge": develop_counter_narrative(),
                "evidence_against": find_contradictory_evidence(),
                "probability_wrong": assess_failure_probability(),
                "impact_if_wrong": evaluate_consequences()
            }
        ],
        "adversarial_perspectives": {
            "prc_view": simulate_prc_strategy(country),
            "russian_view": simulate_russian_approach(country),
            "competitor_view": assess_allied_competition(country)
        },
        "blind_spots": identify_analytical_gaps(country),
        "stress_tests": run_scenario_stress_tests(country),
        "alternative_futures": develop_alternative_scenarios(country),
        "recommendation_critique": challenge_recommendations()
    }

    save_json("phase10_redteam.json", red_team)
    print("⚠️ Phase 10 Red Team completed - CRITICAL for analytical rigor")
```

### Phase 11: Foresight with NATO EWS
```python
def generate_foresight(country):
    foresight = {
        "scenarios": develop_scenarios(country),
        "early_warning": build_ews_system(country),
        "forecasts": create_forecast_registry(country)
    }

    # US infrastructure exposure
    if TOGGLES["INCLUDE_US_INVOLVEMENT"]:
        compute_exposure = assess_compute_dependencies(country)
        save_json("phase11_sub5_compute_data_exposure.json", compute_exposure)

    # NATO early warning (NEW)
    if TOGGLES["INCLUDE_NATO"]:
        nato_ews = {
            "defence_spending_trajectory": project_defence_spending(country),
            "capability_gaps": identify_ndpp_shortfalls(country),
            "interoperability_risks": assess_stanag_gaps(country),
            "innovation_lag": measure_edt_adoption(country),
            "alliance_cohesion": calculate_solidarity_index(country)
        }

        # Set thresholds
        thresholds = {
            "defence_decline": "< 1.5% GDP for 2 years",
            "exercise_absence": "Missing 2+ major exercises",
            "stanag_lag": "> 30% not implemented",
            "innovation_gap": "No DIANA/NIF participation"
        }

        nato_ews["thresholds"] = thresholds
        save_json("phase11_sub7_nato_ews.json", nato_ews)

    save_json("phase11_foresight.json", foresight)
```

### Phase 12: Extended Analysis ⚠️ CRITICAL - OFTEN SKIPPED
```python
def extended_analysis(country):
    """MANDATORY: Deep-dive sector analysis and long-term assessment"""
    extended = {
        "deep_dive_sectors": {},
        "emerging_technology_assessment": {},
        "supply_chain_deep_dive": {},
        "innovation_ecosystem_analysis": {},
        "geopolitical_positioning": {},
        "long_term_trajectories": {},
        "strategic_recommendations_extended": {}
    }

    # Top 3 sectors for deep analysis
    top_sectors = identify_strategic_sectors(country, top_n=3)
    for sector in top_sectors:
        extended["deep_dive_sectors"][sector] = {
            "current_position": assess_global_position(country, sector),
            "competitive_analysis": swot_analysis(country, sector),
            "technology_roadmap": develop_tech_roadmap(country, sector),
            "collaboration_map": map_partnerships(country, sector)
        }

    # Emerging tech assessment
    for tech in ["quantum", "ai_ml", "hypersonics", "biotech_defense"]:
        extended["emerging_technology_assessment"][tech] = {
            "current_state": assess_maturity(country, tech),
            "gap_vs_leaders": measure_technology_gap(country, tech),
            "catch_up_feasibility": evaluate_catch_up_potential(country, tech),
            "sovereignty_risk": assess_dependency_risk(country, tech)
        }

    # Supply chain vulnerabilities
    extended["supply_chain_deep_dive"] = {
        "critical_dependencies": map_critical_components(country),
        "vulnerability_assessment": assess_supply_resilience(country),
        "mitigation_strategies": develop_diversification_plan(country)
    }

    # Long-term factors
    extended["long_term_trajectories"] = {
        "demographic_impact": project_demographic_effects(country),
        "climate_security": assess_climate_risks(country),
        "technology_convergence": identify_convergence_opportunities(country)
    }

    save_json("phase12_extended.json", extended)
    print("⚠️ Phase 12 Extended Analysis completed - CRITICAL for strategic depth")
```

### Phase 13: Closeout & Implementation
```python
def closeout_analysis(country):
    """Final implementation planning and handoff"""
    closeout = {
        "implementation_plan": {
            "timeline": create_implementation_timeline(),
            "raci_matrix": define_responsibilities(),
            "resource_requirements": estimate_resources()
        },
        "success_metrics": define_kpis(),
        "monitoring_handoff": {
            "procedures": document_monitoring_procedures(),
            "dashboard_config": configure_monitoring_dashboard(),
            "alert_thresholds": set_alert_parameters()
        },
        "critical_recommendations": prioritize_actions()
    }

    # Validate all phases completed
    validate_phase_completion(country)

    # Generate executive brief
    generate_executive_brief(country)

    save_json("phase13_closeout.json", closeout)
    print("✅ All 14 phases completed successfully")
```

---

## NATO Data Collection Pipeline

### Automated Collection (35-40%)
```python
class NATOCollector:
    def __init__(self, country):
        self.country = country
        self.nato_status = self.determine_status(country)

    def collect_automated(self):
        """Collect what can be automated"""
        data = {}

        # Defense spending (95% automated)
        data["defence_spending"] = self.parse_nato_pdf()

        # Exercise news (80% automated)
        data["exercises"] = self.scrape_exercise_news()

        # Document metadata (70% automated)
        data["documents"] = self.scrape_nato_library()

        # STO abstracts (60% automated)
        data["research"] = self.scrape_sto_public()

        # COE updates (50% automated)
        data["coe_news"] = self.aggregate_coe_news()

        return data

    def schedule_manual(self):
        """Create tickets for manual collection"""
        tickets = []

        manual_items = [
            "DIANA site updates",
            "NIF portfolio companies",
            "NSPA contract details",
            "STANAG implementation status",
            "COE research projects",
            "Minilateral agreements"
        ]

        for item in manual_items:
            tickets.append(create_collection_ticket(item))

        return tickets
```

### STANAG Compliance Tracking
```python
def track_stanag_compliance(country):
    """Track STANAG implementation"""

    # Get STANAG list (automated)
    stanag_list = scrape_stanag_registry()

    # Check national implementation (manual)
    implementation = {
        "implemented": [],
        "partial": [],
        "planned": [],
        "not_applicable": []
    }

    # For automated countries, check standards databases
    if country in AUTOMATED_STATS:
        national_standards = query_national_standards_db(country)

        for stanag in stanag_list:
            status = check_stanag_status(stanag, national_standards)
            implementation[status].append(stanag)
    else:
        # Create ticket for manual assessment
        create_ticket({
            "type": "manual_stanag_survey",
            "country": country,
            "stanag_count": len(stanag_list)
        })

    # Calculate compliance score
    compliance_rate = len(implementation["implemented"]) / len(stanag_list)

    return {
        "compliance_rate": compliance_rate,
        "implementation": implementation,
        "critical_gaps": identify_critical_stanag_gaps(implementation)
    }
```

---

## Ticket Response System

### Ticket Handler
```python
def handle_chatgpt_ticket(ticket):
    """Respond to ChatGPT tickets"""

    phase = ticket["phase"]
    artifact = ticket["artifact"]
    missing = ticket["fields_missing"]
    sources = ticket["suggested_source"]

    # Route to appropriate handler
    if "DIANA" in sources:
        data = collect_diana_data(manual=True)
    elif "NSPA" in sources:
        data = scrape_nspa_contracts()
    elif "STO" in sources:
        data = enhance_sto_collection()
    elif "COE" in sources:
        data = aggregate_coe_resources()
    elif "STANAG" in sources:
        data = update_stanag_tracking()
    else:
        data = generic_collection(sources)

    # Update artifact
    update_artifact(artifact, data)

    # Validate and respond
    validation = validate_artifact(artifact)

    return {
        "ticket_id": ticket.get("id"),
        "status": "resolved" if validation["valid"] else "partial",
        "data_collected": len(data),
        "confidence_impact": calculate_confidence_delta(data),
        "notes": generate_resolution_notes(ticket, data)
    }
```

---

## Schema Validation

### NATO-Enhanced Schemas
```python
SCHEMAS = {
    "phase03_sub4_nato_policies": {
        "type": "object",
        "required": ["nato_commands", "coes_hosted", "ndpp_alignment"],
        "properties": {
            "nato_commands": {"type": "array"},
            "nato_bases": {"type": "array"},
            "coes_hosted": {"type": "array"},
            "diana_sites": {"type": "array"},
            "framework_role": {"type": "boolean"},
            "ndpp_alignment": {"type": "object"}
        }
    },
    "phase04_sub5_nato_supply_nodes": {
        "type": "object",
        "required": ["nspa_procurement", "stanag_requirements"],
        "properties": {
            "nspa_procurement": {"type": "number", "minimum": 0, "maximum": 100},
            "stanag_requirements": {"type": "array"},
            "multinational_logistics": {"type": "array"},
            "certification_bottlenecks": {"type": "array"}
        }
    },
    "phase05_sub7_diana_sites": {
        "type": "object",
        "required": ["accelerator_sites", "test_centers"],
        "properties": {
            "accelerator_sites": {"type": "array"},
            "test_centers": {"type": "array"},
            "portfolio_companies": {"type": "array"},
            "coe_participation": {"type": "object"}
        }
    }
}

def validate_all_artifacts():
    """Validate all artifacts against schemas"""

    validation_report = []

    for artifact_name, schema in SCHEMAS.items():
        artifact_path = f"{ARTIFACT_DIR}/{artifact_name}.json"

        if os.path.exists(artifact_path):
            with open(artifact_path) as f:
                data = json.load(f)

            try:
                jsonschema.validate(data, schema)
                validation_report.append({
                    "artifact": artifact_name,
                    "status": "valid"
                })
            except jsonschema.ValidationError as e:
                validation_report.append({
                    "artifact": artifact_name,
                    "status": "invalid",
                    "error": str(e)
                })

                # Create ticket for fixing
                create_ticket({
                    "type": "schema_validation_failure",
                    "artifact": artifact_name,
                    "error": str(e)
                })

    save_json("validation_report.json", validation_report)
    return validation_report
```

---

## Quality Gates

### NATO-Specific Quality Checks
```python
def nato_quality_gates(country):
    """Apply NATO-specific quality gates"""

    gates_passed = True
    issues = []

    if country in NATO_MEMBERS:
        # Check defense spending data freshness
        spending_data = load_json("phase02_indicators.json").get("nato", {})
        if spending_data:
            data_age = calculate_data_age(spending_data.get("collection_date"))
            if data_age > 730:  # 2 years
                issues.append("Defense spending data >2 years old")
                gates_passed = False

        # Check STANAG compliance tracking
        stanag_data = load_json("phase07_sub6_standards_stanag_map.json")
        if not stanag_data or len(stanag_data) < 10:
            issues.append("Insufficient STANAG tracking")
            gates_passed = False

        # Check exercise participation
        exercise_data = load_json("phase07_sub5_nato_links.json")
        if not exercise_data.get("exercises"):
            issues.append("No exercise participation data")
            gates_passed = False

    return {
        "passed": gates_passed,
        "issues": issues,
        "recommendations": generate_remediation_steps(issues)
    }
```

---

## Implementation Checklist

### Setup Phase
```bash
# 1. Check NATO status
python scripts/check_nato_status.py --country={{COUNTRY}}

# 2. Configure automation
python scripts/configure_nato_automation.py --country={{COUNTRY}}

# 3. Initialize collectors
python scripts/init_nato_collectors.py
```

### Collection Phase
```bash
# Automated collection (35-40%)
python scripts/nato_automated_collection.py --country={{COUNTRY}}

# Generate manual tasks
python scripts/generate_manual_tasks.py --country={{COUNTRY}}

# Validate artifacts
python scripts/validate_nato_artifacts.py
```

### Quality Assurance
```bash
# Run quality gates
python scripts/nato_quality_gates.py --country={{COUNTRY}}

# Check compliance
python scripts/check_stanag_compliance.py --country={{COUNTRY}}

# Generate report
python scripts/generate_nato_report.py --country={{COUNTRY}}
```

---

## Key NATO Resources

### Must Monitor
- NATO official statistics (annual)
- STO publications (monthly)
- COE websites (weekly)
- DIANA announcements (quarterly)
- Exercise schedules (continuous)

### Manual Quarterly Updates
- DIANA portfolio companies
- NIF investments
- NSPA major contracts
- Minilateral developments
- COE research projects

---

## CRITICAL: Phase Validation Function

```python
def validate_phase_completion(country):
    """MANDATORY: Verify all 14 phases completed before declaring success"""

    required_files = {
        "Phase 0": ["phase00_taxonomy.json"],
        "Phase 1": ["phase01_setup.json", "phase01_sub5_narratives.json"],
        "Phase 2": ["phase02_indicators.json"],
        "Phase 3": ["phase03_landscape.json", "phase03_sub4_nato_policies.json"],
        "Phase 4": ["phase04_supply_chain.json", "phase04_sub5_nato_supply_nodes.json"],
        "Phase 5": ["phase05_institutions.json", "phase05_sub7_diana_sites.json"],
        "Phase 6": ["phase06_funders.json"],
        "Phase 7": ["phase07_links.json", "phase07_sub5_nato_links.json"],
        "Phase 8": ["phase08_risk.json"],
        "Phase 9": ["phase09_posture.json"],  # CRITICAL - PRC/MCF
        "Phase 10": ["phase10_redteam.json"],  # CRITICAL - Red Team
        "Phase 11": ["phase11_foresight.json", "phase11_sub7_nato_ews.json"],
        "Phase 12": ["phase12_extended.json"],  # CRITICAL - Extended
        "Phase 13": ["phase13_closeout.json"]
    }

    missing_phases = []
    for phase, files in required_files.items():
        for file in files:
            if not os.path.exists(f"{ARTIFACT_DIR}/{file}"):
                missing_phases.append(f"{phase}: {file}")

    if missing_phases:
        print("❌ INCOMPLETE - Missing phases:")
        for missing in missing_phases:
            print(f"  - {missing}")
        raise ValueError("Cannot proceed - phases 9, 10, 12 are MANDATORY")

    # Validate China content in executive brief
    exec_brief = read_file(f"{ARTIFACT_DIR}/EXECUTIVE_BRIEF.md")
    if "China" not in exec_brief and "PRC" not in exec_brief:
        print("⚠️ WARNING: Executive brief missing China/PRC analysis from Phase 9")

    print("✅ All 14 phases validated successfully")
    return True
```

---

*End of Claude Code Implementation Prompt v1.7 FINAL - This version provides complete technical implementation for NATO-enhanced OSINT Foresight analysis with mandatory phase validation.*
