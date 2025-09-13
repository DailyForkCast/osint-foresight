# Claude Code Master Prompt v1.0
**OSINT Research Security Framework - Automated Parallel Execution**

## Runtime Configuration

```python
CLAUDE_RUNTIME_ENHANCED = {
  "mode": "TOOL_AUGMENTED+ONLINE_QUERY",
  "web": { 
    "method": "WebFetch+WebSearch",
    "cache_ttl_min": 15,
    "websearch_for_recent": true
  },
  "io": { 
    "fs_rw": true, 
    "http_downloads": true,
    "checkpoint_saves": true
  },
  "exec": {
    "python": true, "node": true, "bash": true, "java": true, "c_cpp": true,
    "cmd_timeout_sec_default": 120, 
    "cmd_timeout_sec_max": 600,
    "bash_trunc_chars": 30000
  },
  "parallel_processing": {
    "enabled": true,
    "max_concurrent_tools": 10,
    "batch_size_webfetch": 5,
    "dedupe_strategy": "url_hash"
  },
  "caching": {
    "webfetch_ttl": 900,
    "persistent_artifacts": true,
    "incremental_updates": true
  },
  "error_handling": {
    "retry_policy": {"max_attempts": 3, "backoff": "exponential"},
    "fallback_sources": true,
    "partial_failure_mode": true
  },
  "memory_optimization": {
    "chunk_large_files": true,
    "streaming_parse": true,
    "gc_aggressive": true
  },
  "formats_in": ["csv","xlsx","json","pdf","ipynb","png","jpg","docx"],
  "formats_out": ["csv","xlsx","json","graphml","png","svg","html","ipynb","ics","gexf","dot"]
}
```

## Phase 0 - Setup & Initialization

```python
# AUTOMATED INITIALIZATION
async def phase_0_setup():
    # Parallel execution of all setup tasks
    tasks = [
        verify_country_data(),
        check_api_access(),
        warm_cache(),
        create_directory_structure(),
        initialize_databases()
    ]
    results = await asyncio.gather(*tasks)
    
    # Directory structure
    dirs = [
        f"data/{COUNTRY}/raw",
        f"data/{COUNTRY}/processed",
        f"data/{COUNTRY}/entities",
        f"reports/{COUNTRY}",
        f"visualizations/{COUNTRY}"
    ]
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)
    
    # Initialize tracking databases
    init_sqlite_dbs()
    return results
```

## Phase 1 - Baseline Indicators & Data Sources

```python
# PARALLEL DATA COLLECTION
async def phase_1_baseline():
    sources = {
        "cordis": "https://cordis.europa.eu/api",
        "openaire": "https://api.openaire.eu/search",
        "crossref": "https://api.crossref.org/works",
        "patents": ["USPTO", "EPO", "WIPO"],
        "gov_sites": country_specific_sources[COUNTRY]
    }
    
    # Parallel fetch all sources
    results = await asyncio.gather(*[
        fetch_source(name, url) for name, url in sources.items()
    ])
    
    # Process and validate
    validated_data = validate_sources(results)
    generate_baseline_report(validated_data)
    
    # Output structured data
    save_json(f"data/{COUNTRY}/phase1_baseline.json", validated_data)
    save_csv(f"data/{COUNTRY}/phase1_indicators.csv", extract_indicators(validated_data))
```

## Phase 2 - Technology Landscape Mapping

```python
# AUTOMATED TECH MAPPING
def phase_2_tech_landscape():
    # Parallel domain analysis
    domains = ["AI", "quantum", "semiconductors", "biotech", "space", 
               "advanced_materials", "autonomy", "sensing"]
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(analyze_domain, domain): domain 
            for domain in domains
        }
        
        results = {}
        for future in as_completed(futures):
            domain = futures[future]
            results[domain] = future.result()
    
    # Generate capability matrix
    capability_matrix = build_capability_matrix(results)
    
    # Identify gaps and strengths
    gaps = identify_technology_gaps(capability_matrix)
    strengths = identify_competitive_advantages(capability_matrix)
    
    # Export visualizations
    generate_tech_heatmap(capability_matrix)
    export_network_graph(results, format="graphml")
```

## Phase 2S - Supply Chain Analysis

```python
# SUPPLY CHAIN DEEP DIVE
async def phase_2s_supply_chain():
    critical_components = {
        "semiconductors": ["chips", "wafers", "equipment"],
        "batteries": ["lithium", "cobalt", "cells"],
        "rare_earths": ["neodymium", "dysprosium", "processing"]
    }
    
    # Parallel supply chain tracing
    traces = await asyncio.gather(*[
        trace_supply_chain(component) 
        for category in critical_components.values() 
        for component in category
    ])
    
    # Risk assessment
    risks = assess_supply_chain_risks(traces)
    
    # Generate Sankey diagram
    create_sankey_diagram(traces, output="supply_chain.html")
    
    # Export dependency matrix
    save_csv("supply_chain_dependencies.csv", traces)
```

## Phase 3 - Institutional Mapping

```python
# AUTOMATED ENTITY RESOLUTION
def phase_3_institutions():
    # Multi-source entity extraction
    sources = {
        "universities": extract_universities(),
        "research_institutes": extract_institutes(),
        "companies": extract_companies(),
        "government": extract_gov_entities()
    }
    
    # Entity resolution and deduplication
    entities = resolve_entities(sources)
    
    # Build collaboration network
    network = build_collaboration_network(entities)
    
    # Calculate centrality metrics
    metrics = {
        "degree": nx.degree_centrality(network),
        "betweenness": nx.betweenness_centrality(network),
        "eigenvector": nx.eigenvector_centrality(network),
        "clustering": nx.clustering(network)
    }
    
    # Export network
    nx.write_graphml(network, f"networks/{COUNTRY}_institutions.graphml")
    
    # Generate institution profiles
    profiles = generate_institution_profiles(entities, metrics)
    save_json(f"data/{COUNTRY}/institution_profiles.json", profiles)
```

## Phase 4 - Funding & Investment Analysis

```python
# FUNDING FLOW TRACKING
async def phase_4_funding():
    # Parallel data collection
    funding_sources = await asyncio.gather(
        fetch_horizon_europe_funding(),
        fetch_national_grants(),
        fetch_vc_investments(),
        fetch_corporate_rd(),
        fetch_military_contracts()
    )
    
    # Build funding network
    funding_network = build_funding_network(funding_sources)
    
    # Identify suspicious patterns
    suspicious = detect_suspicious_funding_patterns(funding_network)
    
    # Generate funding flow diagram
    create_funding_flow_diagram(funding_network)
    
    # Risk scoring
    risk_scores = calculate_funding_risks(funding_network, suspicious)
    
    # Export results
    save_csv(f"data/{COUNTRY}/funding_flows.csv", funding_network)
    save_json(f"data/{COUNTRY}/funding_risks.json", risk_scores)
```

## Phase 5 - International Collaboration Analysis

```python
# COLLABORATION NETWORK ANALYSIS
def phase_5_international():
    # Multi-dimensional collaboration tracking
    collaboration_types = {
        "publications": analyze_coauthorships(),
        "projects": analyze_joint_projects(),
        "patents": analyze_joint_patents(),
        "standards": analyze_standards_participation(),
        "conferences": analyze_conference_participation()
    }
    
    # Build multi-layer network
    multilayer_network = build_multilayer_network(collaboration_types)
    
    # Identify risk patterns
    risk_patterns = {
        "prc_military_tied": identify_prc_military_collaborations(),
        "dual_use": identify_dual_use_collaborations(),
        "technology_transfer": identify_tech_transfer_risks()
    }
    
    # Generate risk heatmap
    create_collaboration_risk_heatmap(risk_patterns)
    
    # Export network for analysis
    export_multilayer_network(multilayer_network, "collaborations.gexf")
```

## Phase 6 - Risk Assessment & Scoring

```python
# AUTOMATED RISK SCORING ENGINE
def phase_6_risk_assessment():
    # Multi-factor risk model
    risk_factors = {
        "technology": assess_technology_risks(),
        "collaboration": assess_collaboration_risks(),
        "funding": assess_funding_risks(),
        "supply_chain": assess_supply_chain_risks(),
        "cyber": assess_cyber_risks(),
        "insider": assess_insider_risks()
    }
    
    # Calculate composite risk scores
    composite_scores = calculate_composite_risks(risk_factors)
    
    # Generate risk matrix
    risk_matrix = build_risk_matrix(composite_scores)
    
    # Identify critical vulnerabilities
    critical = identify_critical_vulnerabilities(risk_matrix)
    
    # Generate executive dashboard
    create_risk_dashboard(risk_matrix, critical)
    
    # Export risk register
    save_csv(f"data/{COUNTRY}/risk_register.csv", risk_matrix)
```

## Phase 7C - Communications & Messaging

```python
# AUTOMATED COMMS PACKAGE GENERATION
def phase_7c_communications():
    # Generate stakeholder-specific briefs
    stakeholders = ["government", "academia", "industry", "public"]
    
    briefs = {}
    for stakeholder in stakeholders:
        briefs[stakeholder] = generate_stakeholder_brief(
            stakeholder,
            risk_level=get_risk_level(stakeholder),
            key_messages=get_key_messages(stakeholder)
        )
    
    # Create message house
    message_house = {
        "core_narrative": generate_core_narrative(),
        "supporting_points": generate_supporting_points(),
        "proof_points": gather_proof_points(),
        "response_matrix": generate_qa_matrix()
    }
    
    # Generate communication materials
    materials = {
        "executive_summary": generate_exec_summary(),
        "technical_brief": generate_technical_brief(),
        "public_factsheet": generate_public_factsheet(),
        "crisis_playbook": generate_crisis_playbook()
    }
    
    # Export all materials
    for name, content in materials.items():
        save_document(f"comms/{COUNTRY}/{name}.md", content)
```

## Phase 7R - Red Team & Validation

```python
# AUTOMATED RED TEAMING
def phase_7r_red_team():
    # Launch parallel adversarial agents
    red_team_agents = {
        "devil_advocate": challenge_every_assumption,
        "black_swan": identify_low_probability_high_impact,
        "alternative_hypothesis": generate_competing_explanations,
        "data_skeptic": question_source_reliability
    }
    
    # Run falsification tests
    falsification_results = run_falsification_framework()
    
    # War gaming simulation
    war_game_results = run_war_game_simulation()
    
    # Stress test scenarios
    stress_test_results = run_stress_tests()
    
    # Generate red team report
    red_team_report = compile_red_team_findings(
        falsification_results,
        war_game_results,
        stress_test_results
    )
    
    save_document(f"reports/{COUNTRY}/red_team_assessment.md", red_team_report)
```

## Phase 8 - Implementation Planning

```python
# IMPLEMENTATION ROADMAP GENERATOR
def phase_8_implementation():
    # Generate implementation timeline
    timeline = generate_implementation_timeline()
    
    # Create RACI matrix
    raci_matrix = create_raci_matrix()
    
    # Define success metrics
    metrics = define_success_metrics()
    
    # Build monitoring framework
    monitoring = build_monitoring_framework()
    
    # Generate Gantt chart
    create_gantt_chart(timeline, output="implementation_timeline.html")
    
    # Export implementation package
    implementation_package = {
        "timeline": timeline,
        "raci": raci_matrix,
        "metrics": metrics,
        "monitoring": monitoring
    }
    
    save_json(f"data/{COUNTRY}/implementation.json", implementation_package)
```

## Phase 9 - Foresight & Early Warning (NEW)

```python
# ADVANCED FORECASTING ENGINE
async def phase_9_foresight():
    # Time series forecasting
    forecasting_models = {
        "arima": ARIMA_forecast(),
        "prophet": Prophet_forecast(),
        "lstm": LSTM_forecast(),
        "ensemble": ensemble_forecast()
    }
    
    # Run all models in parallel
    forecasts = await asyncio.gather(*[
        model.predict(horizons=[2, 5, 10]) 
        for model in forecasting_models.values()
    ])
    
    # Technology convergence analysis
    convergence_analysis = analyze_technology_convergence()
    
    # Wild card scenario generation
    wild_cards = generate_wild_card_scenarios()
    
    # Early warning system design
    ews = {
        "indicators": {
            "leading": identify_leading_indicators(),
            "coincident": identify_coincident_indicators(),
            "lagging": identify_lagging_indicators()
        },
        "thresholds": calculate_alert_thresholds(),
        "monitoring": design_monitoring_system()
    }
    
    # Weak signal detection
    weak_signals = detect_weak_signals()
    
    # Generate interactive dashboard
    create_foresight_dashboard(forecasts, ews, weak_signals)
    
    # Export monitoring calendar
    create_monitoring_calendar(ews, output="monitoring.ics")
    
    # API specification for automated monitoring
    api_spec = generate_monitoring_api_spec(ews)
    save_yaml("monitoring_api.yaml", api_spec)
```

## Phase 10 - Go-Live & Closeout (NEW)

```python
# AUTOMATED CLOSEOUT PACKAGE GENERATOR
async def phase_10_closeout():
    # Parallel generation of all closeout materials
    closeout_tasks = [
        generate_executive_decision_package(),
        create_implementation_tracker(),
        generate_risk_heatmap_final(),
        build_monitoring_dashboard_spec(),
        create_governance_structure(),
        define_success_criteria(),
        schedule_pir_reviews()
    ]
    
    closeout_materials = await asyncio.gather(*closeout_tasks)
    
    # RACI matrix generation
    raci = generate_raci_matrix()
    
    # Knowledge transfer package
    knowledge_transfer = {
        "documentation": compile_documentation(),
        "training_materials": generate_training_materials(),
        "runbooks": create_operational_runbooks(),
        "troubleshooting_guides": generate_troubleshooting_guides()
    }
    
    # Change management plan
    change_management = {
        "stakeholder_analysis": analyze_stakeholders(),
        "communication_plan": create_comm_plan(),
        "resistance_mitigation": identify_resistance_points(),
        "adoption_metrics": define_adoption_metrics()
    }
    
    # Continuity planning
    continuity = {
        "succession_plan": create_succession_plan(),
        "backup_procedures": document_backup_procedures(),
        "disaster_recovery": create_dr_plan(),
        "archive_strategy": define_archive_strategy()
    }
    
    # Generate final package
    final_package = {
        "decision_package": closeout_materials[0],
        "implementation_tracker": closeout_materials[1],
        "risk_heatmap": closeout_materials[2],
        "monitoring_dashboard": closeout_materials[3],
        "governance": closeout_materials[4],
        "success_criteria": closeout_materials[5],
        "pir_schedule": closeout_materials[6],
        "raci_matrix": raci,
        "knowledge_transfer": knowledge_transfer,
        "change_management": change_management,
        "continuity": continuity
    }
    
    # Generate interactive closeout dashboard
    create_closeout_dashboard(final_package)
    
    # Export complete package
    save_json(f"closeout/{COUNTRY}/final_package.json", final_package)
    
    # Generate PDF report
    generate_closeout_report_pdf(final_package)
    
    # Create handover checklist
    handover_checklist = generate_handover_checklist(final_package)
    save_csv(f"closeout/{COUNTRY}/handover_checklist.csv", handover_checklist)
    
    # Schedule automated PIR reminders
    schedule_pir_reminders(final_package["pir_schedule"])
```

## Parallel Execution Orchestrator

```python
# MASTER ORCHESTRATOR
async def run_full_analysis(country: str):
    """Execute all phases with maximum parallelization"""
    
    # Phase groups that can run in parallel
    phase_groups = [
        # Group 1: Setup and baseline (must run first)
        [phase_0_setup],
        
        # Group 2: Initial data collection (can run in parallel)
        [phase_1_baseline, phase_2_tech_landscape, phase_2s_supply_chain],
        
        # Group 3: Network analysis (depends on Group 2)
        [phase_3_institutions, phase_4_funding, phase_5_international],
        
        # Group 4: Assessment and planning (depends on Group 3)
        [phase_6_risk_assessment, phase_7c_communications, phase_7r_red_team],
        
        # Group 5: Forward looking (can start with partial Group 4 data)
        [phase_8_implementation, phase_9_foresight],
        
        # Group 6: Final packaging (must run last)
        [phase_10_closeout]
    ]
    
    results = {}
    for group in phase_groups:
        # Run all phases in group in parallel
        group_results = await asyncio.gather(*[
            phase(country) for phase in group
        ])
        
        # Store results
        for phase, result in zip(group, group_results):
            results[phase.__name__] = result
        
        # Checkpoint save
        save_checkpoint(results)
    
    return results

# Validation Framework
def validate_phase_outputs(phase_name: str, outputs: dict) -> dict:
    """Validate outputs meet quality standards"""
    
    validation_rules = {
        "completeness": check_required_fields(outputs),
        "consistency": check_data_consistency(outputs),
        "quality": check_data_quality(outputs),
        "citations": check_citation_coverage(outputs)
    }
    
    validation_results = {}
    for rule_name, rule_func in validation_rules.items():
        validation_results[rule_name] = rule_func
    
    return validation_results

# Performance Monitoring
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "execution_time": {},
            "data_volume": {},
            "api_calls": {},
            "cache_hits": {},
            "errors": []
        }
    
    def log_phase_performance(self, phase: str, metrics: dict):
        self.metrics["execution_time"][phase] = metrics.get("duration")
        self.metrics["data_volume"][phase] = metrics.get("records_processed")
        self.metrics["api_calls"][phase] = metrics.get("api_calls")
        self.metrics["cache_hits"][phase] = metrics.get("cache_hit_rate")
    
    def generate_performance_report(self):
        return {
            "total_execution_time": sum(self.metrics["execution_time"].values()),
            "total_records": sum(self.metrics["data_volume"].values()),
            "cache_efficiency": np.mean(list(self.metrics["cache_hits"].values())),
            "error_rate": len(self.metrics["errors"]) / len(self.metrics["execution_time"])
        }
```

## Utility Functions

```python
# DATA PERSISTENCE
def save_checkpoint(data: dict, phase: str = None):
    """Save intermediate results for recovery"""
    timestamp = datetime.now().isoformat()
    checkpoint_file = f"checkpoints/{COUNTRY}_{phase}_{timestamp}.pkl"
    with open(checkpoint_file, 'wb') as f:
        pickle.dump(data, f)

# PARALLEL WEB FETCHING
async def parallel_webfetch(urls: list, batch_size: int = 5):
    """Fetch multiple URLs in parallel with rate limiting"""
    results = []
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        batch_results = await asyncio.gather(*[
            webfetch(url) for url in batch
        ])
        results.extend(batch_results)
        await asyncio.sleep(1)  # Rate limiting
    return results

# ENTITY RESOLUTION
def resolve_entities(sources: dict) -> list:
    """Deduplicate and merge entities from multiple sources"""
    all_entities = []
    for source, entities in sources.items():
        for entity in entities:
            entity['source'] = source
            all_entities.append(entity)
    
    # Use fuzzy matching for deduplication
    resolved = []
    seen = set()
    for entity in all_entities:
        key = generate_entity_key(entity)
        if key not in seen:
            seen.add(key)
            resolved.append(entity)
        else:
            # Merge with existing entity
            merge_entity_data(resolved, entity)
    
    return resolved

# AUTOMATED REPORTING
def generate_phase_report(phase: str, data: dict):
    """Generate markdown report for phase results"""
    report = f"# Phase {phase} Report\n\n"
    report += f"Generated: {datetime.now().isoformat()}\n\n"
    
    # Add summary statistics
    report += "## Summary Statistics\n\n"
    for key, value in data.get('summary', {}).items():
        report += f"- **{key}**: {value}\n"
    
    # Add key findings
    report += "\n## Key Findings\n\n"
    for finding in data.get('findings', []):
        report += f"- {finding}\n"
    
    # Add visualizations
    if 'visualizations' in data:
        report += "\n## Visualizations\n\n"
        for viz in data['visualizations']:
            report += f"![{viz['title']}]({viz['path']})\n\n"
    
    return report
```

## Error Handling & Recovery

```python
# GRACEFUL DEGRADATION
class ResilientExecutor:
    def __init__(self):
        self.fallback_sources = {}
        self.partial_results = {}
        self.error_log = []
    
    async def execute_with_fallback(self, primary_func, fallback_func, *args, **kwargs):
        try:
            return await primary_func(*args, **kwargs)
        except Exception as e:
            self.error_log.append({
                'function': primary_func.__name__,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            if fallback_func:
                return await fallback_func(*args, **kwargs)
            else:
                return self.generate_partial_result(primary_func.__name__)
    
    def generate_partial_result(self, func_name: str):
        """Generate partial result when both primary and fallback fail"""
        return {
            'status': 'partial',
            'source': func_name,
            'data': self.partial_results.get(func_name, {}),
            'completeness': 0.3,
            'error': 'Data collection failed - using cached/partial data'
        }
```

## Configuration Export

```python
# EXPORT CONFIGURATION
def export_run_configuration():
    """Export complete configuration for reproducibility"""
    config = {
        "runtime": CLAUDE_RUNTIME_ENHANCED,
        "country": COUNTRY,
        "timeframe": TIMEFRAME,
        "horizons": HORIZONS,
        "languages": {
            "local": LOCAL_LANGS,
            "search": LANGS_SEARCH,
            "output": LANGS_OUTPUT
        },
        "toggles": {
            "INCLUDE_EXPORT_CONTROLS": INCLUDE_EXPORT_CONTROLS,
            "INCLUDE_US_NATSEC_FRAMEWORK": INCLUDE_US_NATSEC_FRAMEWORK,
            "INCLUDE_EWI_CHECKLIST": INCLUDE_EWI_CHECKLIST,
            "INCLUDE_DATA_PULLS": INCLUDE_DATA_PULLS,
            "INCLUDE_COLLAB_MAPPING": INCLUDE_COLLAB_MAPPING,
            "INCLUDE_CHINESE_LANG_SOURCES": INCLUDE_CHINESE_LANG_SOURCES,
            "INCLUDE_LOCAL_LANG_SOURCES": INCLUDE_LOCAL_LANG_SOURCES,
            "ENABLE_PARALLEL_PROCESSING": ENABLE_PARALLEL_PROCESSING,
            "ENABLE_WEBSEARCH": ENABLE_WEBSEARCH,
            "ENABLE_VALIDATION": ENABLE_VALIDATION
        },
        "execution_timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    save_json(f"config/{COUNTRY}_run_config.json", config)
    return config
```

---

**Version**: 1.0  
**Purpose**: Claude Code automated execution framework for OSINT research security analysis  
**Capabilities**: Parallel processing, multi-source integration, automated validation, comprehensive reporting  
**Output**: Complete country assessment package with all phases, visualizations, and risk assessments