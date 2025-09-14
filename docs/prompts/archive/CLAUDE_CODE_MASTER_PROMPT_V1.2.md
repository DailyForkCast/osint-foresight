# Claude Code Master Prompt v1.2 - OSINT Implementation Framework (Renumbered 0-13)

**Goal:** Produce artifacts with strict schemas, corroboration rules (≥2 sources for moderate+ claims), bilingual search (EN/local/中文), and date filters (POLICY_WINDOW).

**Runtime:** TOOL_AUGMENTED+ONLINE_QUERY; fs_rw enabled; webfetch/cache; retries; parallelization with guards; schema validation on save; fail-fast with `validation_report.txt`.

## SHARED RUN CONTEXT
```
COUNTRY = {{country_name}}
TIMEFRAME = {{2015-present}}
HORIZONS = {{2y,5y,10y}}
LANG = {{EN + local + zh-CN}}
POLICY_WINDOW = {{2019-2025 inclusive}}
ARTIFACT_DIR = {{./artifacts/{{COUNTRY}}}}
TOGGLES = {
  INCLUDE_MCF: true,
  INCLUDE_EXPORT_CONTROLS: true,
  INCLUDE_FINANCE_VECTORS: true,
  INCLUDE_SUPPLY_CHAIN: true,
  INCLUDE_ADVERSARY_SIM: true
}
SCALES = {
  prob: ["10-30%","30-60%","60-90%"],
  confidence: ["Low","Med","High"],
  data_quality: {1:"rumor",2:"single weak",3:"mixed",4:"multi independent",5:"primary/official"}
}
EVIDENCE_TABLE (CSV columns) = "ClaimID,Claim,SourceURL,PubDate,Lang,Corroboration,Contradiction,Probability,Confidence,DataQuality"
```

## 1) Shared Constants & Validation
- `POLICY_WINDOW = (2019, 2025)`
- Probability/Confidence/DataQuality bands as in **SCALES**
- Evidence table columns as listed above
- JSON Schemas for: landscape, links, MCF, risks, scenarios, EWS, recommendations, implementation, adversary_plan, forecast_registry, calibration

## 2) Phase Orchestrator (0-13)
- Group phases to respect dependencies
- Phase 4 runs parallel to Phase 3
- Write stubs with gaps when a source is unavailable
- Always validate schemas before save
- Append all evidence to `evidence_master.csv`

---

## Phase 0 - Definitions & Taxonomy

### 0.1 Build Taxonomy
```python
def build_taxonomy():
    taxonomy = {
        "domains": ["AI", "semiconductors", "quantum", "biotech", "space",
                   "materials", "autonomy", "sensing", "maritime", "smart_city"],
        "key_terms": {
            "dual_use": "Technology with both civilian and military applications",
            "gray_zone": "Activities below threshold of traditional conflict",
            "MCF": "Military-Civil Fusion - PRC strategy integrating civilian and military development"
        }
    }
    save_json("taxonomy.json", taxonomy)
```

### 0.2 ID Registry
```python
def build_id_registry():
    registry = {
        "org": ["ROR", "GRID"],
        "person": ["ORCID"],
        "company": ["LEI"]
    }
    # If missing IDs, set null and log in validation_report.txt
    save_json("id_registry.json", registry)
```

**Files:** `taxonomy.json`, `id_registry.json`

---

## Phase 1 - Setup & Configuration

### 1.1 Verify Presets
```python
def verify_presets():
    # Create directories
    os.makedirs(f"artifacts/{COUNTRY}", exist_ok=True)
    os.makedirs(f"reports/country={COUNTRY}", exist_ok=True)
    os.makedirs(f"data/processed/country={COUNTRY}", exist_ok=True)

    # Cache warm
    warm_cache_sources()
```

### 1.2 Write Configuration
```python
def write_configuration():
    scope = {
        "country": COUNTRY,
        "timeframe": "2015-present",
        "horizons": ["2y", "5y", "10y"],
        "languages": ["en", get_local_language(COUNTRY), "zh-CN"]
    }
    save_json("scope.json", scope)

    assumptions = {
        "data_availability": "Public sources only",
        "analytical_limits": "Signals-only for sensitive topics",
        "corroboration_rule": "≥2 sources for moderate+ claims"
    }
    save_json("assumption_log.json", assumptions)
```

**Files:** `scope.json`, `assumption_log.json`

---

## Phase 2 - Indicators & Data Sources

### 2.1 Enumerate Sources
```python
def enumerate_sources():
    sources = [
        {"name": "OpenAIRE", "type": "publications", "auth": check_auth("openaire")},
        {"name": "CORDIS", "type": "projects", "auth": check_auth("cordis")},
        {"name": "Crossref", "type": "publications", "auth": True},
        {"name": "OpenAlex", "type": "publications", "auth": True},
        {"name": "WIPO", "type": "patents", "auth": check_auth("wipo")},
        {"name": "EPO", "type": "patents", "auth": check_auth("epo")},
        {"name": "USPTO", "type": "patents", "auth": check_auth("uspto")},
        {"name": f"{COUNTRY}_national", "type": "mixed", "auth": check_national()}
    ]
    return sources
```

### 2.2 Build Metric Catalog
```python
def build_metric_catalog():
    metrics = []
    for indicator in get_indicators():
        metric = {
            "name": indicator.name,
            "type": indicator.type,  # leading/coincident/lagging
            "source": indicator.source,
            "provenance": indicator.provenance,
            "latency_days": indicator.latency,
            "update_freq": indicator.frequency
        }
        metrics.append(metric)

    save_csv("metric_catalog.csv", metrics)
```

### 2.3 Save Indicators
```python
save_json("phase2_indicators.json", {
    "sources": sources,
    "indicators": metrics
})
```

**Files:** `phase2_indicators.json`, `metric_catalog.csv`

---

## Phase 3 - Technology Landscape

### 3.1 Map Actors
```python
def map_actors():
    actors = []
    # Query multiple sources with bilingual search
    for query in [f"{COUNTRY} AI ministry", f"{COUNTRY} 人工智能 部门"]:
        results = parallel_search(query, sources=["web", "news", "gov"])
        for result in results:
            actor = {
                "name": result.name,
                "type": classify_actor_type(result),  # ministry|agency|SOE|university|company
                "aka": extract_aliases(result),  # Include 中文名
                "jurisdiction": result.jurisdiction,
                "notes": summarize(result, max_words=25)
            }
            actors.append(dedupe_actor(actor))
    return actors
```

### 3.2 Analyze Policies
```python
def analyze_policies():
    policies = []
    for year in range(2019, 2026):
        policy_search = f"{COUNTRY} AI policy {year}"
        results = search_policies(policy_search)
        for policy in results:
            if policy.year in POLICY_WINDOW:
                policies.append({
                    "title": policy.title,
                    "year": policy.year,
                    "authority": classify_authority(policy),  # law|regulation|strategy|guideline
                    "bindingness": assess_bindingness(policy),  # binding|advisory
                    "summary": summarize(policy, max_words=25),
                    "link": policy.url
                })
    return policies
```

### 3.3 Infrastructure Assessment
```python
def assess_infrastructure():
    infrastructure = []
    for asset_type in ["supercomputers", "fab_facilities", "research_centers"]:
        assets = search_infrastructure(COUNTRY, asset_type)
        for asset in assets:
            infrastructure.append({
                "asset": asset.name,
                "asset_uid": generate_uid(asset),
                "domain": classify_domain(asset),
                "criticality": assess_criticality(asset),  # Low|Med|High
                "export_sensitive_parts": identify_sensitive_components(asset)
            })
    return infrastructure
```

**Output:** `phase3_landscape.json`, `policy_index.json`
**Evidence:** Append to `evidence_master.csv`

---

## Phase 4 - Supply Chain Security (parallel to Phase 3)

### 4.1 Critical Components
```python
def identify_critical_components():
    components = []
    for tech in ["semiconductors", "rare_earths", "photolithography"]:
        component_search = f"{COUNTRY} {tech} supply chain"
        results = search_components(component_search)
        for component in results:
            components.append({
                "name": component.name,
                "hs_code": get_hs_code(component),
                "cn_code": get_cn_code(component),
                "criticality": assess_criticality(component),
                "alternatives": find_alternatives(component)
            })
    return components
```

### 4.2 Trace Signals
```python
def trace_procurement_signals():
    signals = []
    # Signals-only approach - no sensitive procurement details
    patterns = ["repeat orders", "vendor concentration", "sudden shifts"]
    for pattern in patterns:
        occurrences = detect_pattern(pattern, COUNTRY)
        for occurrence in occurrences:
            signals.append({
                "pattern": pattern,
                "date": occurrence.date,
                "magnitude": occurrence.magnitude,
                "confidence": assess_confidence(occurrence)
            })
    return signals
```

**Output:** `phase4_supply_chain.json`, `supply_chain_map.json`, `procurement_signals.csv`
**Evidence:** Append to `evidence_master.csv`

---

## Phase 5 - Institutions & Accredited Labs

### 5.1 Entity Resolution
```python
def resolve_entities():
    entities = []
    # Load from multiple sources
    raw_entities = load_entities_from_sources()

    for entity in raw_entities:
        resolved = {
            "name": entity.name,
            "name_local": entity.name_local,  # 中文名
            "ror_id": lookup_ror(entity),
            "lei_id": lookup_lei(entity),
            "grid_id": lookup_grid(entity),
            "type": entity.type,
            "capabilities": extract_capabilities(entity)
        }
        entities.append(resolved)

    # Dedupe based on IDs
    return dedupe_entities(entities)
```

### 5.2 Build Collaboration Network
```python
def build_collab_network():
    network = {}
    collaborations = get_collaborations(COUNTRY)

    for collab in collaborations:
        # Guard against disconnected graphs
        if is_connected(collab.entity_a, collab.entity_b):
            add_edge(network, collab.entity_a, collab.entity_b, collab.type)

    # Calculate centrality with guards
    centrality = calculate_centrality_safe(network)
    return network, centrality
```

**Output:** `phase5_institutions.json`

---

## Phase 6 - Funding & Instruments

### 6.1 Collect Funding Data
```python
def collect_funding():
    funding = {
        "public_grants": [],
        "vc_pe": [],
        "corporate_rd": [],
        "military_contracts": []
    }

    # Public grants (Horizon, national)
    for program in ["Horizon Europe", f"{COUNTRY} national funding"]:
        grants = search_grants(program, COUNTRY)
        funding["public_grants"].extend(process_grants(grants))

    # VC/PE/LP
    investments = search_investments(COUNTRY)
    funding["vc_pe"] = process_investments(investments)

    # Corporate R&D
    corporate = search_corporate_rd(COUNTRY)
    funding["corporate_rd"] = process_corporate(corporate)

    # Military contracts (signals only)
    military = search_military_contracts(COUNTRY)
    funding["military_contracts"] = sanitize_military(military)

    return funding
```

### 6.2 Map Controls
```python
def map_funding_controls():
    controls = []
    for funding_type in ["grants", "investments", "contracts"]:
        applicable_controls = identify_controls(funding_type)
        for control in applicable_controls:
            controls.append({
                "type": funding_type,
                "control": control.name,  # NSPM-33, EU, ITAR, EAR
                "obligation_level": control.obligation,  # mandatory|recommended
                "enforcement": control.enforcement_notes
            })
    return controls
```

**Output:** `phase6_funders.json`, `funding_controls_map.json`

---

## Phase 7 - International Links & Collaboration

### 7.1 Co-authorships
```python
def analyze_coauthorships():
    coauthors = []
    papers = search_papers(COUNTRY, TIMEFRAME)

    for paper in papers:
        for author in paper.authors:
            coauthor = {
                "name": author.name,
                "orcid": author.orcid,
                "affiliation_at_pub": author.affiliation,
                "secondary_affiliation": detect_secondary(author),
                "paper_id": paper.id,
                "year": paper.year
            }
            coauthors.append(coauthor)

    return coauthors
```

### 7.2 Standards Activity
```python
def track_standards_activity():
    standards = []
    bodies = ["ISO", "IEC", "IEEE", "ETSI", "3GPP", "ITU"]

    for body in bodies:
        participants = get_participants(body, COUNTRY)
        for participant in participants:
            activity = {
                "body": body,
                "wg": participant.working_group,
                "topic": participant.topic,
                "role": participant.role,  # member|rapporteur|editor
                "contribution_type": participant.contribution,  # edit|comment|proposal
                "entity": participant.entity
            }
            standards.append(activity)

    return standards
```

### 7.3 Risk Patterns
```python
def identify_risk_patterns():
    patterns = []

    # Dual-use technologies
    dual_use = identify_dual_use(COUNTRY)
    patterns.extend(dual_use)

    # PRC-military ties
    prc_ties = identify_prc_military_ties(COUNTRY)
    patterns.extend(prc_ties)

    return patterns
```

**Output:** `phase7_links.json`, `standards_activity.json`

---

## Phase 8 - Risk Assessment & Best Practice

### 8.1 Compute Risks
```python
def compute_risks():
    risks = []
    domains = ["AI", "semiconductors", "quantum", "biotech", "space",
               "materials", "autonomy", "sensing", "maritime", "smart_city"]

    for domain in domains:
        domain_risks = assess_domain_risks(domain, COUNTRY)
        # Limit to top 6 risks
        for risk in domain_risks[:6]:
            risks.append({
                "name": risk.name,
                "domain": domain,
                "mechanism": describe_mechanism(risk, max_words=30),  # who→what→how→to what end
                "prob": risk.probability_range,  # "30-60%"
                "impact": risk.impact_level,  # Low|Med|High
                "horizon": risk.time_horizon,  # "5y"
                "indicators": extract_indicators(risk),  # ≥1 numeric
                "uncertainty": describe_uncertainty(risk, max_words=20),
                "voi_hint": suggest_voi(risk, max_words=15),
                "text_dag": create_dag(risk)  # "A>B>C>D>E"
            })

    return risks
```

**Output:** `phase8_risk.json`

---

## Phase 9 - PRC Interest & MCF Acquisition

### 9.1 Pull Doctrine & Policies
```python
def analyze_prc_doctrine():
    doctrine = {
        "motivations": extract_motivations(),
        "strategic_goals": extract_strategic_goals(),
        "policy_framework": extract_policies(POLICY_WINDOW),
        "governance": map_governance_structure()
    }
    return doctrine
```

### 9.2 Actor & Alias Resolution
```python
def resolve_prc_actors():
    actors = []
    raw_actors = search_prc_actors(COUNTRY)

    for actor in raw_actors:
        resolved = {
            "name": actor.name,
            "aka": actor.aliases,  # Include 中文名
            "role": classify_role(actor),  # SOE|university|military|agency
            "links": extract_links(actor)
        }
        actors.append(resolved)

    return dedupe_actors(actors)
```

### 9.3 Classify Mechanisms
```python
def classify_acquisition_mechanisms():
    mechanisms = []
    types = ["licit", "gray", "illicit"]

    for mech_type in types:
        instances = find_mechanisms(mech_type, COUNTRY)
        for instance in instances:
            mechanisms.append({
                "type": mech_type,
                "tech": instance.technology,
                "event": instance.event_description,
                "date": instance.date,
                "evidence_url": instance.source,
                "confidence": assess_confidence(instance)
            })

    return mechanisms
```

### 9.4 Build Tech Taxonomy
```python
def build_tech_taxonomy():
    taxonomy = []
    target_techs = identify_target_technologies(COUNTRY)

    for tech in target_techs:
        entry = {
            "tech": tech.name,
            "maturity": assess_maturity(tech),
            "maturity_metric": {"TRL": tech.trl},
            "attractiveness": assess_attractiveness(tech),  # Low|Med|High
            "barriers": identify_barriers(tech),
            "signals": extract_recent_signals(tech)
        }
        taxonomy.append(entry)

    return taxonomy
```

### 9.5 Generate Predictions
```python
def generate_mcf_predictions():
    predictions = []
    horizons = ["2y", "5y", "10y"]

    for horizon in horizons:
        prediction = {
            "horizon": horizon,
            "claim": generate_claim(horizon),
            "prob": estimate_probability(horizon),
            "confidence": assess_prediction_confidence(horizon)
        }
        predictions.append(prediction)

    return predictions
```

**Output:** `phase9_posture.json`
**Evidence:** Must meet corroboration rule (≥2 sources)

---

## Phase 10 - Red Team Review & Assumption Check

### 10.1 Falsification Tests
```python
def run_falsification_tests():
    tests = []
    assumptions = load_assumptions()

    for assumption in assumptions:
        test = {
            "assumption": assumption.text,
            "falsification_test": design_test(assumption),
            "result": execute_test(assumption),
            "implications": assess_implications(assumption)
        }
        tests.append(test)

    return tests
```

### 10.2 War-Game Scenarios
```python
def create_wargame_scenarios():
    scenarios = []

    for scenario_type in ["escalation", "de-escalation", "stalemate"]:
        scenario = {
            "type": scenario_type,
            "injects": create_injects(scenario_type),
            "responses": simulate_responses(scenario_type),
            "outcomes": assess_outcomes(scenario_type)
        }
        scenarios.append(scenario)

    return scenarios
```

### 10.3 Stress Tests
```python
def run_stress_tests():
    stress_tests = []
    parameters = ["funding_cut", "tech_embargo", "talent_flight"]

    for param in parameters:
        test = {
            "parameter": param,
            "stress_level": ["10%", "25%", "50%"],
            "impact": assess_stress_impact(param),
            "breaking_point": find_breaking_point(param)
        }
        stress_tests.append(test)

    return stress_tests
```

### 10.4 Adversary Simulation
```python
def build_adversary_simulation():
    adversary_plan = {
        "objectives": define_adversary_objectives(),
        "capabilities": assess_adversary_capabilities(),
        "likely_actions": predict_adversary_actions(),
        "counter_indicators": identify_counter_indicators(),
        "countermeasures": develop_countermeasures()
    }
    save_json("adversary_plan.json", adversary_plan)
    return adversary_plan
```

**Output:** `phase10_redteam.json`, `adversary_plan.json`

---

## Phase 11 - Foresight & Early Warning

### 11.1 Generate Scenarios
```python
def generate_scenarios():
    scenarios = []
    types = ["baseline", "accelerated", "disrupted", "wildcard"]

    for scenario_type in types[:4]:  # Limit to 4 scenarios
        scenario = {
            "name": scenario_type.title(),
            "prob": estimate_scenario_probability(scenario_type),
            "drivers": identify_drivers(scenario_type),
            "indicators": define_numeric_indicators(scenario_type),
            "timeline": project_timeline(scenario_type),
            "summary": write_summary(scenario_type, max_words=180)
        }
        scenarios.append(scenario)

    save_json("phase11_foresight.json", {"scenarios": scenarios})
    return scenarios
```

### 11.2 Build Early Warning System
```python
def build_ews():
    ews = {
        "metrics": [],
        "playbook": []
    }

    # Define metrics
    for risk in load_risks():
        metric = {
            "name": f"{risk.name}_indicator",
            "source": identify_source(risk),
            "threshold": calculate_threshold(risk),
            "cadence": determine_cadence(risk),  # weekly|monthly
            "owner": assign_owner(risk),
            "provenance": document_provenance(risk),
            "latency_days": estimate_latency(risk),
            "rationale": explain_rationale(risk),
            "suppression_rule": define_suppression(risk)
        }
        ews["metrics"].append(metric)

    # Define playbook
    for metric in ews["metrics"]:
        action = {
            "trigger": f"{metric['name']} > {metric['threshold']}",
            "action": determine_action(metric),
            "notes": write_action_notes(metric, max_words=18)
        }
        ews["playbook"].append(action)

    save_json("phase11_ews.json", ews)
    save_yaml("rules.yaml", convert_to_rules(ews))
    return ews
```

### 11.3 Create Forecast Registry
```python
def create_forecast_registry():
    forecasts = []

    for question in generate_forecast_questions(COUNTRY):
        forecast = {
            "question": question.text,
            "type": question.type,  # binary|numeric|date
            "resolution_criteria": define_resolution(question),
            "base_rates": calculate_base_rates(question),
            "forecast": {
                "p": estimate_probability(question),
                "ci": calculate_confidence_interval(question)
            },
            "predictors": identify_predictors(question),
            "update_notes": write_update_notes(question, max_words=60),
            "next_review": schedule_review(question)
        }
        forecasts.append(forecast)

    save_json("forecast_registry.json", {"forecast_registry": forecasts})
    save_csv("forecast_registry.csv", forecasts)
    return forecasts
```

### 11.4 Compute Calibration
```python
def compute_calibration():
    calibration = {
        "brier_scores": {},
        "reliability_curves": []
    }

    for horizon in ["2y", "5y", "10y"]:
        brier = calculate_brier_score(horizon)
        calibration["brier_scores"][horizon] = brier

        curve = generate_reliability_curve(horizon)
        calibration["reliability_curves"].append(curve)

    save_json("calibration_scores.json", calibration)
    save_csv("reliability_curves.csv", calibration["reliability_curves"])
    return calibration
```

**Outputs:** `phase11_foresight.json`, `forecast_registry.json/.csv`, `phase11_ews.json`, `calibration_scores.json`, `rules.yaml`

---

## Phase 12 - Extended Foresight (Optional)

### 12.1 Country-Specific Wildcards
```python
def identify_wildcards():
    wildcards = []

    # Country-specific edge cases
    country_specific = get_country_specific_factors(COUNTRY)
    for factor in country_specific:
        wildcard = {
            "name": factor.name,
            "probability": factor.probability,
            "impact": factor.impact,
            "early_signals": factor.signals
        }
        wildcards.append(wildcard)

    return wildcards
```

### 12.2 Sector Deep-Dives
```python
def conduct_deep_dives():
    deep_dives = []
    priority_sectors = identify_priority_sectors(COUNTRY)

    for sector in priority_sectors:
        analysis = {
            "sector": sector,
            "detailed_assessment": conduct_detailed_assessment(sector),
            "supply_chain_mapping": map_sector_supply_chain(sector),
            "vulnerability_analysis": analyze_vulnerabilities(sector),
            "opportunity_assessment": assess_opportunities(sector)
        }
        deep_dives.append(analysis)

    save_json("phase12_extended.json", {
        "wildcards": wildcards,
        "deep_dives": deep_dives
    })
```

**Output:** `phase12_extended.json`

---

## Phase 13 - Closeout

### 13.1 Implementation Timeline & RACI
```python
def create_implementation_plan():
    implementation = {
        "timeline": [],
        "raci_matrix": {}
    }

    # Timeline
    milestones = define_milestones()
    for milestone in milestones:
        implementation["timeline"].append({
            "milestone": milestone.name,
            "date": milestone.target_date,
            "owner": milestone.owner,
            "dependencies": milestone.dependencies
        })

    # RACI Matrix
    for task in get_all_tasks():
        implementation["raci_matrix"][task] = {
            "responsible": identify_responsible(task),
            "accountable": identify_accountable(task),
            "consulted": identify_consulted(task),
            "informed": identify_informed(task)
        }

    return implementation
```

### 13.2 Success Metrics
```python
def define_success_metrics():
    metrics = []

    for objective in get_objectives():
        metric = {
            "name": objective.metric_name,
            "target": objective.target_value,
            "frequency": objective.measurement_frequency,
            "owner": objective.owner,
            "baseline": objective.baseline_value
        }
        metrics.append(metric)

    return metrics
```

### 13.3 Monitoring Handoff
```python
def create_monitoring_handoff():
    handoff = {
        "monitoring_calendar": generate_calendar(),
        "alert_thresholds": define_alert_thresholds(),
        "escalation_procedures": document_escalation(),
        "reporting_templates": create_templates()
    }

    # Export calendar
    save_ics("monitoring.ics", handoff["monitoring_calendar"])
    return handoff
```

### 13.4 Archive & Continuity
```python
def create_archive_strategy():
    archive = {
        "retention_policy": define_retention_policy(),
        "backup_locations": specify_backup_locations(),
        "access_controls": define_access_controls(),
        "continuity_plan": create_continuity_plan(),
        "knowledge_transfer": document_knowledge_transfer()
    }

    save_json("phase13_closeout.json", {
        "implementation": implementation,
        "metrics": metrics,
        "handoff": handoff,
        "archive": archive
    })

    return archive
```

**Output:** `phase13_closeout.json`

---

## Validation & Error Handling

### Schema Validation
```python
def validate_all_outputs():
    validation_report = []

    for phase in range(14):
        artifacts = get_phase_artifacts(phase)
        for artifact in artifacts:
            if not validate_schema(artifact):
                validation_report.append({
                    "phase": phase,
                    "artifact": artifact.name,
                    "errors": get_validation_errors(artifact)
                })

    if validation_report:
        save_txt("validation_report.txt", format_report(validation_report))
        raise ValidationError("Schema validation failed. See validation_report.txt")
```

### Evidence Tracking
```python
def track_evidence():
    evidence_master = []

    for claim in get_all_claims():
        evidence_row = {
            "ClaimID": generate_claim_id(claim),
            "Claim": claim.text,
            "SourceURL": claim.source_url,
            "PubDate": claim.publication_date,
            "Lang": claim.language,
            "Corroboration": find_corroboration(claim),
            "Contradiction": find_contradictions(claim),
            "Probability": claim.probability,
            "Confidence": claim.confidence,
            "DataQuality": assess_data_quality(claim)
        }
        evidence_master.append(evidence_row)

    save_csv("evidence_master.csv", evidence_master)
```

---

## Workflow Notes
- Always append to `evidence_master.csv`
- Enforce corroboration for moderate+ claims (≥2 sources)
- Respect `POLICY_WINDOW` when indexing policies (2019-2025)
- When artifacts exist, **ingest first**; compute only gaps
- Phase 4 runs parallel to Phase 3
- Write stubs with gaps when a source is unavailable
- Fail-fast with `validation_report.txt` if schemas don't validate
- Use bilingual search (EN/local/中文) for comprehensive coverage
- When in doubt, prefer smaller, validated artifacts over large, noisy dumps
