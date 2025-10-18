# CLAUDE CODE — MASTER ENFORCEMENT PROMPT v9.4 COMPLETE
## Zero-Fabrication Technical Implementation with Phase Framework

**Version:** 9.4 COMPLETE
**Date:** 2025-09-20
**Core Rule:** No Evidence = No Claim = Return INSUFFICIENT_EVIDENCE
**Purpose:** Technical implementation of intelligence analysis
**Mission Scope:**
  - PRIMARY: Identify how China exploits target countries to access US technology
  - SECONDARY: Document ALL Chinese exploitation to gain dual-use technology (even without US connection)
  - IMPLEMENTATION: Always check US angle, but capture all dual-use exploitation patterns

---

## 0) META (Required at Start of Every Run)
```
RUN_META = {
  model: "Claude-Opus/Haiku/…",
  model_version: "{{provider_reported_version}}",
  run_id: "{{UUID}}",
  task: "{{short_task_name}}",
  operator: "{{analyst_name}}",
  started_utc: "{{ISO8601}}",
  zero_fabrication_standard: "v1.0",
  repository_commit: "{{git_sha}}"
}
```

## 1) SYSTEM — Universal Guardrails
```
You must not invent numbers, names, entities, or citations. If evidence is insufficient, output exactly `INSUFFICIENT_EVIDENCE` and list missing items.
All claims must be grounded in retrieved sources with a provenance bundle: {url, access_date(UTC ISO-8601), archived_url, verification_method, quoted_span, locator}.
IMPORTANT: sha256 is ONLY available for downloaded data files. Neither Claude Code nor ChatGPT can create screenshots.
For web sources use: verification_method="wayback_machine_url" or "cached_version_url" or "direct_quote_verification".
Copy digits exactly as written. Use the sub-prompt chain and schemas below.
```

## 2) HARD RULES - ENFORCED BY CODE

```python
def validate_output(claim):
    """Enforce zero fabrication rules"""

    # Rule 1: No Evidence → No Claim
    if not claim.has_source():
        return "INSUFFICIENT_EVIDENCE"

    # Rule 2: Never Invent Quantities
    if claim.has_number() and not claim.has_recompute_command():
        return "REJECTED: Number without recompute"

    # Rule 3: Two-Source Rule for Tier A
    if claim.tier == "A" and len(claim.sources) < 2:
        if not claim.has_data_artifact():
            return "REJECTED: Tier A needs 2 sources"

    # Rule 4: Confidence Label Required
    if not claim.confidence or not claim.rationale:
        return "REJECTED: Missing confidence/rationale"

    # Rule 5: Self-Verification Required
    if not claim.self_verified:
        return "REJECTED: Not self-verified"

    return "VALID"
```

## 3) DATA INFRASTRUCTURE & PROCESSING

```python
# ACTUAL DATA AVAILABLE
DATA_PATHS = {
    "openalex": "F:/OSINT_Backups/openalex/",  # 420GB - stream process
    "ted": "F:/TED_Data/monthly/",  # 24GB tar.gz archives
    "cordis": "F:/2025-09-14 Horizons/",  # 0.19GB EU research
    "sec_edgar": "F:/OSINT_DATA/SEC_EDGAR/",  # Connected
    "patents": "F:/OSINT_DATA/EPO_PATENTS/",  # European patents
}

PROCESSORS = {
    "orchestrator": "scripts/phase_orchestrator.py",
    "ted_processor": "scripts/process_ted_data.py",
    "openalex_processor": "scripts/systematic_data_processor.py",
}

# Stream processing for large datasets
def process_large_dataset(path, batch_size=1000):
    """Process data in verifiable chunks"""
    checkpoint_every = 10000
    for batch in chunk_data(path, batch_size):
        results = process_batch(batch)
        if results.count % checkpoint_every == 0:
            save_checkpoint(results)
    return results
```

## 4) RISK TIER CLASSIFICATION

```python
class ClaimTier(Enum):
    """Every claim must be classified"""

    TIER_A_CRITICAL = {
        "definition": "Counts, transfers, linkages, briefings",
        "examples": ["78 personnel transfers", "joint patents", "contracts"],
        "requirements": {
            "sources": 2,  # Minimum
            "admiralty_max": "B2",  # No worse than B2
            "provenance": "complete",
            "recompute": "mandatory",
            "ACH": "required"
        }
    }

    TIER_B_SUBSTANTIVE = {
        "definition": "Assessments, trends, inferences",
        "examples": ["improving capability", "likely dual-use"],
        "requirements": {
            "sources": 1,
            "quote": "mandatory",
            "admiralty": "required",
            "alternatives": "considered"
        }
    }

    TIER_C_CONTEXT = {
        "definition": "Background, definitions",
        "examples": ["NATO history", "tech definitions"],
        "requirements": {
            "sources": 1,
            "credible": True,
            "document": "still required"
        }
    }
```

## 5) INSUFFICIENT_EVIDENCE PROTOCOL

```python
def insufficient_evidence(query, attempts):
    """Return when data unavailable"""
    return {
        "status": "INSUFFICIENT_EVIDENCE",
        "query": query,
        "missing": identify_missing_data(query),
        "searched": attempts.sources_checked,
        "needed": suggest_data_sources(query),
        "confidence": "Cannot assess without data",
        "timestamp": datetime.utcnow().isoformat()
    }
```

## 6) PHASE EXECUTION IMPLEMENTATION

### Phase Dependencies
```python
PHASE_DEPENDENCIES = {
    "phase_0": [],  # No dependencies
    "phase_x": ["phase_0"],  # Definitions after setup
    "phase_1": ["phase_0"],
    "phase_2": ["phase_1"],
    "phase_3": ["phase_1"],
    "phase_2s": ["phase_2"],  # Supply chain after tech landscape
    "phase_4": ["phase_3"],
    "phase_5": ["phase_3"],
    "phase_6": ["phase_2", "phase_2s", "phase_3", "phase_4", "phase_5"],
    "phase_7c": ["phase_6"],
    "phase_7r": ["phase_6"],
    "phase_8": ["phase_7c", "phase_7r"],  # Comprehensive risk assessment
    "phase_9": ["phase_8"],  # Strategic posture
    "phase_10": ["phase_9"],  # Red team
    "phase_11": ["phase_10"],  # Foresight analysis
    "phase_12": ["phase_11"],  # Extended analysis
    "phase_13": ["phase_0", "phase_1", "phase_2", "phase_2s", "phase_3",
                 "phase_4", "phase_5", "phase_6", "phase_7c", "phase_7r",
                 "phase_8", "phase_9", "phase_10", "phase_11", "phase_12"]  # Closeout requires all
}

def can_execute_phase(phase_id):
    """Check if dependencies met"""
    required = PHASE_DEPENDENCIES.get(phase_id, [])
    return all(phase_complete(p) for p in required)
```

### Phase 0: Setup & Context
```python
def phase_0_setup(country_code):
    """Initialize country analysis"""
    outputs = {
        "country_profile": generate_profile(country_code),
        "research_parameters": define_parameters(country_code),
        "threat_vectors": identify_threats(country_code),
        "data_sources": validate_sources(country_code)
    }

    # Test data access
    for source in outputs["data_sources"]:
        if not test_access(source):
            outputs["gaps"].append(source)

    return outputs
```

### Phase 1: Data Source Validation
```python
def phase_1_validation():
    """Validate all data sources"""
    results = {}

    for source_name, source_path in DATA_PATHS.items():
        validation = {
            "accessible": os.path.exists(source_path),
            "size": get_size(source_path),
            "format": detect_format(source_path),
            "processor": PROCESSORS.get(source_name),
            "rate_limits": test_rate_limits(source_name)
        }
        results[source_name] = validation

    return results
```

### Phase 2: Technology Landscape
```python
def phase_2_technology(country_code):
    """Map technology capabilities"""

    # Stream process OpenAlex
    publications = stream_process_openalex(
        country=country_code,
        batch_size=1000,
        fields=["quantum", "AI", "semiconductors"]
    )

    # Process patents
    patents = process_patents(
        path=DATA_PATHS["patents"],
        country=country_code
    )

    # Required specificity
    for tech in identified_technologies:
        tech.validate_specificity()  # "5-qubit processor" not "quantum"
        tech.check_china_overlap()
        tech.assess_dual_use()

    return {
        "technologies": identified_technologies,
        "china_overlaps": overlaps,
        "capability_gaps": gaps
    }
```

### Phase 2S: Supply Chain
```python
def phase_2s_supply_chain(country_code):
    """Analyze supply chain dependencies"""

    # Process TED procurement data
    ted_data = process_ted_archives(
        path=DATA_PATHS["ted"],
        country=country_code,
        focus="technology_procurement"
    )

    # Identify Chinese suppliers
    chinese_suppliers = []
    for contract in ted_data:
        if is_chinese_entity(contract.supplier):
            chinese_suppliers.append({
                "supplier": contract.supplier,
                "technology": contract.items,  # Specific not generic
                "value": contract.value,
                "criticality": assess_criticality(contract)
            })

    return {
        "total_contracts": len(ted_data),
        "chinese_suppliers": chinese_suppliers,
        "critical_dependencies": identify_critical_deps(ted_data)
    }
```

### Phase 3-8: Additional Phases
```python
# Phase 3: Institutions
def phase_3_institutions(country_code):
    """Map institutional relationships"""
    return map_institutions_with_china_links(country_code)

# Phase 4: Funding Flows
def phase_4_funding(country_code):
    """Track funding sources"""
    return analyze_funding_flows(country_code)

# Phase 5: International Links
def phase_5_links(country_code):
    """Map collaboration networks"""
    return identify_international_collaborations(country_code)

# Phase 6: Risk Assessment
def phase_6_risk(country_code, prior_phases):
    """Synthesize risks from all phases"""
    return comprehensive_risk_assessment(prior_phases)

# Phase 7C: China Strategy Assessment
def phase_7c_china_strategy(country_code, phase_6_output):
    """Assess China targeting strategy"""
    return analyze_china_strategy(phase_6_output)

# Phase 7R: Red Team Analysis
def phase_7r_red_team(all_phases):
    """Challenge assumptions and findings"""
    return red_team_analysis(all_phases)

# Phase 8: Comprehensive Risk Assessment
def phase_8_risk_assessment(country_code, all_phases):
    """Comprehensive risk synthesis after 7C and 7R"""
    risks = {
        "technology_transfer": assess_tech_transfer_risk(all_phases),
        "supply_chain": assess_supply_chain_risk(all_phases),
        "personnel": assess_personnel_risk(all_phases),
        "cyber": assess_cyber_risk(all_phases),
        "regulatory": assess_regulatory_gaps(all_phases)
    }

    for risk_type, risk_data in risks.items():
        risk_data["leonardo_validation"] = apply_leonardo_standard(risk_data)
        risk_data["alternatives_tested"] = test_alternatives(risk_data, n=5)
        risk_data["confidence_score"] = calculate_confidence([risk_data])

    return risks

# Phase 9: Strategic Posture
def phase_9_strategic_posture(country_code, phase_8_output):
    """Assess national strategic coherence and China policy"""
    return {
        "strategy_coherence": assess_national_strategy(country_code),
        "china_policy_analysis": analyze_china_stance(country_code),
        "conference_influence": track_standards_leadership(country_code),
        "negative_evidence": document_what_not_found(all_phases),
        "decision_points": identify_conflict_points(country_code),
        "forecast": project_12_24_month_trajectory(country_code)
    }

# Phase 10: Red Team
def phase_10_red_team(all_phases):
    """Challenge all assumptions and findings"""
    return {
        "assumption_challenges": challenge_assumptions(all_phases),
        "alternative_hypotheses": generate_alternatives(all_phases),
        "collection_blind_spots": identify_gaps(all_phases),
        "deception_indicators": assess_deception(all_phases),
        "validation_results": validate_assumptions(all_phases)
    }

# Phase 11: Foresight Analysis
def phase_11_foresight(country_code, all_phases):
    """Project future scenarios and early warning indicators"""
    timeframes = {
        "6_12_months": immediate_risks_analysis(all_phases),
        "1_2_years": developing_threats_analysis(all_phases),
        "3_5_years": strategic_shifts_analysis(all_phases),
        "5_10_years": long_term_trajectories(all_phases)
    }

    return {
        "scenarios": timeframes,
        "trend_projections": project_trends(all_phases),
        "weak_signals": identify_early_indicators(all_phases),
        "wild_cards": assess_low_prob_high_impact(all_phases),
        "strategic_warnings": define_red_lines_tripwires(all_phases),
        "monitoring_priorities": set_collection_priorities(all_phases)
    }

# Phase 12: Extended Analysis
def phase_12_extended_analysis(all_phases):
    """Deep dives and cross-domain integration"""
    return {
        "cross_domain_integration": integrate_across_domains(all_phases),
        "hidden_connections": reveal_connections(all_phases),
        "second_order_effects": analyze_cascades(all_phases),
        "arctic_considerations": arctic_analysis() if is_arctic_state else None,
        "strategic_implications": assess_implications(all_phases),
        "technology_convergence": analyze_convergence(all_phases),
        "system_vulnerabilities": map_vulnerabilities(all_phases)
    }

# Phase 13: Closeout
def phase_13_closeout(all_phases):
    """Final packaging and governance handoff"""
    return {
        "executive_summary": synthesize_findings(all_phases),
        "top_findings": crystallize_insights(all_phases),
        "confidence_assessment": assess_knowledge_vs_suspicion(all_phases),
        "intelligence_gaps": prioritize_collection(all_phases),
        "recommendations": generate_next_steps(all_phases),
        "implementation_roadmap": create_roadmap(all_phases),
        "governance_package": {
            "raci_matrix": define_responsibilities(),
            "risk_heatmap": generate_heatmap(all_phases),
            "monitoring_dashboard": specify_dashboard(),
            "success_criteria": define_kpis(),
            "review_schedule": set_pir_dates()
        },
        "knowledge_transfer": {
            "lessons_learned": capture_lessons(all_phases),
            "archive_requirements": specify_retention(),
            "continuity_plan": ensure_continuity(),
            "change_management": plan_changes()
        }
    }
```

## 7) SOURCE WEIGHTING (Admiralty + Type)

```python
WEIGHTS = {
    "primary_dataset": 1.0,
    "official_filing/standard": 0.95,
    "peer_review/long_form": 0.9,
    "think_tank_report": 0.8,
    "reputable_news": 0.6,
    "commentary/social": 0.3
}

def calculate_confidence(sources):
    """Weight-based confidence calculation"""
    if not sources:
        return 0.0

    weights = [WEIGHTS.get(s.type, 0.3) for s in sources]

    # Tier-A requires special handling
    if any(s.tier == "A" for s in sources):
        if len([w for w in weights if w >= 0.8]) >= 2:
            return max(weights)
        elif max(weights) >= 0.95:
            return max(weights)
        else:
            return min(0.5, max(weights))

    return sum(weights) / len(weights)
```

## 8) LEONARDO STANDARD IMPLEMENTATION

```python
def apply_leonardo_standard(technology_claim):
    """Enforce specificity for technology claims"""

    required = {
        "technology": extract_specific_tech(claim),  # "AW139" not "helicopter"
        "overlap": identify_us_overlap(claim),  # Military variants
        "access": quantify_china_access(claim),  # "40+ aircraft"
        "exploitation": define_pathway(claim),  # How exploited
        "timeline": extract_timeline(claim),  # When
        "alternatives": test_alternatives(claim, n=5),  # Other explanations
        "oversight": check_restrictions(claim),  # Export controls
        "confidence": calculate_score(claim, max=20)  # 0-20 scale
    }

    if not all(required.values()):
        return "INCOMPLETE: Missing Leonardo standard elements"

    return required
```

## 9) ALTERNATIVE EXPLANATIONS ENGINE

```python
def check_alternatives(pattern_observed):
    """Test mundane before sinister explanations"""

    mundane_checks = {
        "publishing_schedule": check_journal_schedules(),
        "conference_timing": check_conference_dates(),
        "fiscal_calendar": check_fiscal_periods(),
        "regulatory_deadline": check_compliance_dates(),
        "industry_standard": check_industry_practice(),
        "market_dynamics": check_market_conditions()
    }

    # Score each hypothesis
    hypotheses = {
        "coordinated_action": 0.0,
        "market_response": 0.0,
        "regulatory_compliance": 0.0,
        "industry_practice": 0.0,
        "pure_coincidence": 0.0
    }

    for h in hypotheses:
        hypotheses[h] = score_hypothesis(h, pattern_observed, mundane_checks)

    # Return most likely explanation
    best = max(hypotheses, key=hypotheses.get)

    if best != "coordinated_action":
        return f"[ALTERNATIVE: {best} explains pattern better than coordination]"

    return "[COORDINATION: Alternative explanations insufficient]"
```

## 10) OUTPUT GENERATION

```python
def generate_phase_output(phase_id, results):
    """Standard output format for all phases"""

    output = {
        "analytical_narrative": write_narrative(results, min_words=400),
        "key_findings": extract_key_findings(results, max_items=5),
        "what_it_means": write_implications(results),
        "evidence_gaps": identify_gaps(results),
        "data_references": list_artifacts_used(results),
        "confidence_assessment": calculate_overall_confidence(results),
        "china_connections": extract_china_elements(results)
    }

    # Validate output
    for claim in output["key_findings"]:
        if validate_output(claim) != "VALID":
            raise ValueError(f"Invalid claim: {claim}")

    return output
```

## 11) CHUNKING & CONTEXT MANAGEMENT

```
MAX_DOCS_PER_BATCH = 20
MAX_TOKENS_PER_BATCH = 6000
RANK_FUNCTION = BM25 + recency + source_weight

Process in batches; never exceed limits. Summarize per-batch; then synthesize across batch summaries only.
```

## 12) SUB-PROMPT CHAIN (Controllers + Schemas)

### A) Retrieval
```
Task: Retrieve sources for {{QUESTION}} from {{DATASETS_OR_SITES}} within {{DATE_RANGE}} and languages {{LANGS}} using keywords {{KEYWORDS}}.
Output JSON:
{ "retrieval": [ {"title":"","url":"","source":"","date_published":"","access_date":"UTC","archived_url":"","verification_method":"sha256_for_downloads_only | wayback_url | cached_url","language":"","weight":0.0} ], "notes":"selection rationale, gaps" }
```

### B) Extraction (Quote-only)
```
Extract verbatim quotes relevant to {{QUESTION}}. Include locators.
Output JSON:
{ "evidence": [ {"url":"","quote":"<exact>","locator":"p.12 fig3 / §2.1","access_date":"UTC","archived_url":"","verification_method":"sha256_downloads | wayback | direct_quote"} ] }
Rules: copy digits exactly; one fact per evidence item.
```

### C) Draft Claims
```
Propose minimal claims from evidence. Do not synthesize beyond quotes.
Output JSON: { "draft_claims": [ {"text":"","risk_tier":"A|B|C"} ] }
```

### D) Verification (Independent Evaluators Required)
```
Verify each draft claim against evidence using:
- Groundedness evaluator: claim must be entailed by at least one quote
- Numeric recompute: show calc path from quoted spans
- Source weight check: apply WEIGHTS

Output JSON:
{ "validated_claims": [ {"text":"","risk_tier":"A|B|C","confidence":"High|Moderate|Low","evidence_idx":[0,2],"calc_block":"<table cells/steps or N/A>","weight":0.0} ],
  "removed_claims": [ {"text":"","reason":"unsupported|mismatch|insufficient_sources"} ] }
```

### E) Translation Safeguards
```
For each non-EN evidence item:
- Provide original quote + machine translation
- Back-translate summary sentence; if meaning diverges, mark `translation_risk=true` and lower confidence
```

### F) Synthesis (Analyst-Ready)
```
Synthesize only from validated_claims.
Output JSON:
{ "claims": [...],
  "summary": "4–5 sentence neutral abstract",
  "relevance": "2–3 sentence dual-use/MCF rationale",
  "provenance": [ {"url":"","access_date":"","archived_url":"","verification_method":"sha256 | wayback | cached_url"} ] }
Rules: No new facts. Absolute dates. Include confidence after each claim.
```

### G) Self-Verification Pass
```
Re-check synthesis. Remove any sentence without a linked evidence quote.
Output: { "removed_lines": ["…"], "final_text": "…" }
```

## 13) HUMAN-IN-THE-LOOP FEEDBACK

```python
def capture_feedback(analyst_action):
    """Log analyst corrections for learning"""
    feedback = {
        "run_id": RUN_META["run_id"],
        "claim_text": analyst_action.claim,
        "action": analyst_action.type,  # accepted|rejected|edited
        "reason": analyst_action.reason,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Add to regression test suite
    add_to_regression_tests(feedback)

    return feedback
```

## 14) CI GATES (Blocking)

- **Provenance Lint**: missing {url, access_date, archived_url, verification_method} → FAIL
- **Groundedness Score ≥ 0.9** for all claims
- **Numeric Recompute** matches quoted spans; else FAIL
- **Dup Audit** across runs
- **Tier-A Review**: human sign-off required
- **SHA256 only for downloaded files**; web sources must use alternative verification

## 15) ADVERSARIAL/RED-TEAM TESTS

Include bait cases (contradictory numbers, missing sources). Model must respond `INSUFFICIENT_EVIDENCE` or flag conflicts with low confidence.

## 16) DRIFT & VERSIONING

Any model/provider update → run regression suite; freeze outputs with run metadata; block deployment on regression failure.

---

**END v9.4 COMPLETE - Full Technical Implementation with Phases**
