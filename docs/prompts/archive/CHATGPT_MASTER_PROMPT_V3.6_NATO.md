# ChatGPT Operator Prompt v3.6 - NATO & US Enhanced
## OSINT Foresight Analysis Framework with Alliance Assessment

**Version:** 3.6
**Updated:** 2025-09-13
**Framework:** Phases 0-13 with NATO integration and US involvement tracking

## Critical Enhancement: NATO Assessment
Previous versions completely missed NATO - the primary defense framework for 31/44 target countries. This version adds comprehensive NATO assessment throughout.

## Key Enhancements vs v3.5:
- **NATO integration** across all phases (new Phase 2.5 for dedicated NATO assessment)
- **US involvement tracking** (phases 4.4, 6.6, 7.4, 9.10, 11.5)
- **Alliance dynamics** (burden-sharing, specialization, minilateral formats)
- **Defense innovation ecosystem** (DIANA, NIF, COEs, STO)
- **Interoperability requirements** (STANAGs, certification, exercises)
- **Policy Anchor Crosswalk** (9.11) for claim verification

---

## SHARED RUN CONTEXT

```yaml
COUNTRY: "{{country_name}}"
REGION: "{{Europe|Asia|Americas}}"
LEVEL: "{{national|subnational}}"
HUB: "{{optional_hub_name}}"  # e.g., "Bavaria-Munich"
HUBS: ["hub1", "hub2", "hub3"]  # Matrix for batch runs
AUTO_HUBS: []  # Discovered and promoted hubs
XHUB: "{{optional_crossborder_hub}}"  # e.g., "QuantumTriangle-DE-AT-CH"
TIMEFRAME: "2015–present"
HORIZONS: ["2y", "5y", "10y"]
LANG: ["EN", "local", "zh-CN"]
POLICY_WINDOW: "2019–2025"
ARTIFACT_DIR: "./artifacts/{{COUNTRY}}/{{HUB}}"

# NATO Context (NEW)
NATO_STATUS: "{{member|partner|non-aligned}}"
NATO_JOINED: "{{year|null}}"  # Membership year if applicable
PARTNERSHIP: "{{PfP|EOP|ICI|MD|null}}"  # Partnership type if applicable
FRAMEWORK_NATION: "{{true|false}}"
HOSTING_COES: []  # List of hosted COEs

TOGGLES:
  INCLUDE_MCF: true
  INCLUDE_EXPORT_CONTROLS: true
  INCLUDE_FINANCE_VECTORS: true
  INCLUDE_SUPPLY_CHAIN: true
  INCLUDE_ADVERSARY_SIM: true
  INCLUDE_US_INVOLVEMENT: true  # Enables 4.4, 6.6, 7.4, 9.10, 11.5
  INCLUDE_NATO_ASSESSMENT: true  # NEW - Enables NATO components

SCALES:
  prob: ["10-30%", "30-60%", "60-90%"]
  confidence: ["Low", "Med", "High"]
  data_quality:
    1: "rumor"
    2: "single weak"
    3: "mixed"
    4: "multi independent"
    5: "primary/official"

DATA_SOURCES:
  tier_1_structured:
    - national_statistics_offices (28 automated, 16 manual)
    - crossref_openalex (420GB downloaded)
    - google_patents_bigquery
    - world_bank_oecd
    - gleif_corporate
    - nato_sto_publications  # NEW
    - diana_portal  # NEW

  tier_2_web:
    - common_crawl (multilingual, 20+ languages)
    - nato_multimedia  # NEW
    - coe_websites  # NEW

  tier_3_supplementary:
    - cordis (pending API)
    - ietf_standards
    - nspa_contracts  # NEW
    - stanag_registry  # NEW
```

---

## Phase 0 — Definitions & Taxonomy

### 0.1 Domain Taxonomy (Enhanced with NATO)

**Technology Categories** (15 domains + NATO capability areas):
```yaml
civilian_dual_use:
  1. AI & Autonomy
  2. Advanced Computing & Semiconductors
  3. Quantum Technologies
  4. Communications & Networking
  5. Photonics, Sensing & EW
  6. Space Systems & GEOINT
  7. Materials & Manufacturing
  8. Energy & Power
  9. Transportation & Hypersonics
  10. Biotechnology & Health
  11. Robotics & HMI
  12. Security & Cyber
  13. Data Infrastructure
  14. Smart Cities & Critical Infrastructure
  15. Agri-/Climate Tech

nato_capability_areas:  # NEW
  joint_enablers: [ISR, strategic_airlift, AAR, SATCOM]
  high_end_warfare: [A2/AD, precision_strike, EW, cyber]
  readiness: [NRF, VJTF, EFP, air_policing]
  emerging_disruptive: [AI, quantum, hypersonics, space, biotech]
```

### 0.2 Key Terms (NATO additions)
- **Dual-use**: Technologies with both civilian and military applications
- **Gray-zone**: Activities below threshold of conflict
- **MCF**: Military-Civil Fusion (军民融合)
- **STANAG**: NATO Standardization Agreement  # NEW
- **DIANA**: Defence Innovation Accelerator for the North Atlantic  # NEW
- **NIF**: NATO Innovation Fund  # NEW
- **NDPP**: NATO Defence Planning Process  # NEW
- **COE**: NATO Centre of Excellence  # NEW

### 0.3 Entity Resolution (NATO additions)
- Use ROR/GRID for institutions
- Use LEI for companies
- Use ORCID for researchers
- Map NATO facility codes  # NEW
- Track COE affiliations  # NEW
- Link DIANA accelerator memberships  # NEW

**Outputs**: `phase00_taxonomy.json`, `id_registry.json`, `alias_map.json`

---

## Phase 1 — Setup & Configuration

### 1.1 Scope & Priorities
Define geographic scope, technology focus areas, key questions, and NATO relationship

### 1.2 Data Collection Strategy (NATO-aware)
**Prioritize structured sources first**:
1. National statistics (R&D, innovation metrics)
2. Patents & publications (innovation output)
3. NATO STO reports (defense research)  # NEW
4. DIANA/NIF portfolios (defense innovation)  # NEW
5. Economic indicators (capacity)
6. Common Crawl validation (deployment signals)

### 1.3 Data Ethics
- Signals-only approach for sensitive data
- No personal data collection
- Transparency in methods
- Respect classification boundaries  # NEW

### 1.4 Country/Hub Configuration (NATO context)
```python
def configure_country_context():
    context = {
        "national": determine_national_scope(COUNTRY),
        "subnational": identify_hubs(COUNTRY),
        "nato_relationship": {  # NEW
            "status": check_nato_membership(COUNTRY),
            "joined": get_membership_year(COUNTRY),
            "partnerships": list_partnership_programs(COUNTRY),
            "hosted_infrastructure": list_nato_facilities(COUNTRY),
            "coes": list_hosted_coes(COUNTRY)
        }
    }
```

### 1.5 Narrative Analysis (US + NATO)
Track prevalent narratives and policy reactions:
- Media prevalence index
- Policy document references
- NATO communiqué analysis  # NEW
- Fact-check against data

**Outputs**: `phase01_setup.json`, `phase01_sub5_narratives.json`

---

## Phase 2 — Indicators & Data Sources

### 2.1 Source Inventory (NATO additions)

**Automated Sources** (expanded):
```yaml
tier_1_apis:
  # Existing 28 country APIs...

nato_sources:  # NEW
  sto_publications: "https://www.sto.nato.int"
  diana_portal: "Registration required"
  multimedia_library: "https://www.nato.int/library"
  act_innovation: "https://www.act.nato.int"
```

### 2.2 Key Indicators (NATO metrics)

**Innovation Capacity** (existing):
- GERD/BERD (R&D expenditure)
- R&D personnel per million
- Patent applications (EPO/USPTO)
- Publication output & citations

**NATO Integration** (NEW):
```yaml
defence_indicators:
  - defence_gdp_ratio  # 2% target
  - equipment_modernization  # 20% target
  - nato_exercise_participation
  - stanag_compliance_rate
  - sto_project_leadership
  - coe_contributions
  - diana_site_hosting
  - nif_investment_exposure
```

### 2.3 Collection Cadence
- Weekly: Publications, patents
- Monthly: Economic indicators, trade, NATO updates  # NEW
- Quarterly: National statistics, Common Crawl, COE reports  # NEW

**Outputs**: `phase02_indicators.json`, `sources.yaml`, `metric_catalog.csv`

---

## Phase 2.5 — NATO Assessment (NEW PHASE)

### 2.5.1 Alliance Integration
```python
def assess_nato_integration():
    if NATO_STATUS == "member":
        assessment = {
            "defence_spending": {
                "gdp_percentage": get_defence_gdp_ratio(),
                "meets_2_percent": check_target_compliance(),
                "equipment_ratio": get_modernization_ratio(),
                "meets_20_percent": check_equipment_target()
            },
            "capability_contributions": {
                "ndpp_targets": list_capability_commitments(),
                "fulfillment_rate": calculate_fulfillment(),
                "high_readiness": get_nrf_contributions(),
                "specializations": identify_niche_capabilities()
            }
        }
    elif NATO_STATUS == "partner":
        assessment = {
            "partnership_level": PARTNERSHIP,
            "interoperability": assess_stanag_adoption(),
            "exercise_participation": count_joint_exercises()
        }
    else:
        assessment = {
            "indirect_impacts": assess_nato_spillovers()
        }
```

### 2.5.2 Innovation Ecosystem
```python
def map_nato_innovation():
    ecosystem = {
        "diana": {
            "accelerator_sites": count_in_country(),
            "test_centers": list_facilities(),
            "portfolio_companies": find_accelerated_startups()
        },
        "nif": {
            "contribution": get_fund_contribution(),
            "investments": track_portfolio_exposure()
        },
        "sto": {
            "panels": list_participation(),
            "leadership_roles": find_chairs_rapporteurs(),
            "active_projects": count_research_projects()
        },
        "coes": {
            "hosted": HOSTING_COES,
            "membership": list_coe_participations()
        }
    }
```

### 2.5.3 Industrial Integration
```python
def assess_defence_industrial_integration():
    industrial = {
        "nspa_procurement": calculate_centralized_share(),
        "stanag_implementation": {
            "adopted": count_implemented_stanags(),
            "pending": list_under_consideration(),
            "national_variations": identify_deviations()
        },
        "multinational_programs": [
            "AGS", "AWACS", "Alliance_Future_Surveillance"
        ],
        "certification_capability": assess_test_facilities()
    }
```

**Outputs**: `phase02_sub5_nato_assessment.json`

---

## Phase 3 — Technology Landscape (NATO-enhanced)

### 3.1 Key Actors (NATO dimension)
Map ecosystem participants:
- Government (ministries, agencies, SOEs)
- Academic (universities, research institutes)
- Private (companies, startups)
- **NATO entities** (COEs, DIANA sites, NIF portfolio)  # NEW
- Include aliases (AKA/中文名)

### 3.2 Policy Framework (NATO alignment)
- National strategies
- NATO capability priorities  # NEW
- NDPP commitments  # NEW
- Funding programs
- Regulatory frameworks
- Export controls

### 3.3 Infrastructure Assets (NATO footprint)
- Research facilities
- Computing resources
- Test facilities
- Production capabilities
- **NATO installations** (commands, COEs, DIANA)  # NEW
- **Certification centers** (STANAG compliance)  # NEW

**Outputs**: `phase03_landscape.json`, `policy_index.json`, `phase03_sub5_nato_landscape.json`  # NEW

---

## Phase 4 — Supply Chain Security (NATO requirements)

### 4.1 Critical Components
Identify dependencies and bottlenecks with NATO requirements

### 4.2 Procurement Patterns
Analyze vendor concentration including NSPA share  # NEW

### 4.3 Supply Chain Mapping
Entity → Component → Jurisdiction flows with NATO certification  # NEW

### 4.4 Foreign-Owned Nodes (US focus)
Track US ownership in European supply chains

### 4.5 NATO Supply Dependencies (NEW)
```python
def map_nato_supply_chain():
    dependencies = {
        "nspa_managed": identify_centralized_procurement(),
        "stanag_required": list_interoperability_components(),
        "multinational_logistics": map_shared_capabilities(),
        "certification_bottlenecks": find_approval_delays(),
        "single_sources": identify_alliance_dependencies()
    }
```

**Outputs**: `phase04_supply_chain.json`, `phase04_sub4_us_owned_supply.json`, `phase04_sub5_nato_supply.json`  # NEW

---

## Phase 5 — Institutions & Networks (NATO collaboration)

### 5.1 Entity Resolution
Deduplicate using ROR/LEI/ORCID + NATO affiliations  # NEW

### 5.2 Collaboration Networks (NATO dimension)
Map partnerships via:
- Co-authorship (CrossRef/OpenAlex)
- Joint patents
- Project participation
- Standards committees
- **STO working groups**  # NEW
- **COE partnerships**  # NEW
- **DIANA cohorts**  # NEW

### 5.3 Capability Profiles
- Technology domains
- Publication/patent output
- Standards roles
- **NATO specializations**  # NEW

### 5.4 Cross-Border Hubs
Identify transnational clusters including NATO regions  # NEW

### 5.5 Non-Hub Discovery
Grid-scan for outlier innovation centers

### 5.6 Auto-Suggest Hubs
Promote discovered centers to formal hubs

**Outputs**: `phase05_institutions.json`, `phase05_sub4_crossborder_hubs.json`

---

## Phase 6 — Funding & Instruments (NATO programs)

### 6.1 Public Funding (NATO additions)
- National programs
- EU funding (Horizon Europe)
- **NATO SPS grants**  # NEW
- **DIANA funding**  # NEW
- Regional/local support

### 6.2 Private Investment (NIF tracking)
- VC/PE activity
- **NATO Innovation Fund**  # NEW
- Corporate R&D
- Joint ventures

### 6.3 Controls & Restrictions
- NSPM-33 (US)
- EU screening mechanisms
- **STANAG requirements**  # NEW
- Export control implications

### 6.6 International Funding Links (US to EU)
Track cross-border funding flows including US-NATO programs  # NEW

**Outputs**: `phase06_funders.json`, `phase06_sub6_us_funding_links.json`

---

## Phase 7 — International Links (Alliance dynamics)

### 7.1 Research Collaboration
- Co-authorship networks
- Citation patterns
- Conference participation
- **STO collaboration**  # NEW

### 7.2 Technology Transfer
- Joint patents
- Licensing agreements
- Standards participation
- **STANAG development**  # NEW

### 7.3 Risk Patterns
- Dual-use collaborations
- Ties to sensitive entities
- **Non-NATO dependencies**  # NEW

### 7.4 Bilateral Collaboration Maps (US-EU)
Detailed partner country analysis within NATO context  # NEW

### 7.5 NATO Cooperation Patterns (NEW)
```python
def map_alliance_cooperation():
    patterns = {
        "bilateral_within_nato": identify_special_relationships(),
        "minilateral_formats": {
            "JEF": ["UK", "NL", "DK", "NO", "SE", "FI", "EE", "LV", "LT"],
            "V4": ["PL", "CZ", "SK", "HU"],
            "NORDEFCO": ["NO", "SE", "FI", "DK", "IS"],
            "B9": ["PL", "RO", "BG", "CZ", "SK", "HU", "EE", "LV", "LT"]
        },
        "framework_nations": identify_framework_relationships(),
        "capability_specialization": map_burden_sharing()
    }
```

**Outputs**: `phase07_links.json`, `phase07_sub4_us_eu_links.json`, `phase07_sub5_nato_cooperation.json`  # NEW

---

## Phase 8 — Risk Assessment (Alliance risks)

### 8.1 Risk Mechanisms (NATO additions)
For each risk (≤6), define:
- Single-sentence mechanism (who→what→how→outcome)
- **Alliance impact assessment**  # NEW
- Probability & impact
- Time horizon

### 8.2 Risk Indicators (NATO metrics)
- Leading indicators (6-24 months ahead)
- **NATO readiness metrics**  # NEW
- Coincident indicators
- Lagging indicators (confirmation)

### 8.3 Monitoring Strategy
- Metrics & thresholds
- **Exercise performance tracking**  # NEW
- Collection frequency
- Responsible parties

### 8.4 NATO-Specific Risks (NEW)
```python
def assess_alliance_risks():
    nato_risks = {
        "article_5_credibility": assess_deterrence_strength(),
        "capability_gaps": identify_critical_shortfalls(),
        "interoperability_failures": evaluate_stanag_gaps(),
        "burden_sharing_tensions": measure_contribution_disparities(),
        "innovation_lag": compare_edt_adoption_rates()
    }
```

**Outputs**: `phase08_risk.json`, `phase08_sub4_nato_risks.json`  # NEW

---

## Phase 9 — PRC Interest & MCF (NATO context)

### 9.1-9.9 Standard MCF Assessment
- Motivations & doctrine
- Policy framework
- Key actors
- Acquisition mechanisms
- Target technologies
- Progress assessment
- Early warning indicators
- **NATO technology priorities overlap**  # NEW

### 9.10 Soft-Points Analysis (US→EU via NATO)
Identify influence pathways:
- Standards committees
- Talent pipelines
- Cloud dependencies
- Supply chain nodes
- **NATO innovation ecosystem**  # NEW

### 9.11 Policy Anchor Crosswalk
Compare claims vs actual PRC policies:
- Verify against primary sources
- Document enforcement examples
- Log contradictions
- **Check NATO threat assessments**  # NEW

**Outputs**: `phase09_posture.json`, `phase09_sub10_softpoints.json`, `phase09_sub11_anchor_crosswalk.json`

---

## Phase 10 — Red Team Review (Alliance scenarios)

### 10.1 Assumption Testing
Challenge key assumptions with:
- Falsification tests
- Alternative explanations
- Data quality assessment
- **NATO scenario validation**  # NEW

### 10.2 Adversary Simulation (NATO context)
- Develop adversary plans
- **Test Article 5 scenarios**  # NEW
- Identify counter-indicators
- Test detection capabilities
- **Assess collective response**  # NEW

**Outputs**: `phase10_redteam.json`, `adversary_plan.json`

---

## Phase 11 — Foresight & Early Warning (NATO indicators)

### 11.1 Scenario Development (Alliance futures)
Create 2-4 scenarios with:
- Narrative (≤180 words)
- **NATO cohesion variables**  # NEW
- Numeric indicators
- Trigger events

### 11.2 Early Warning System (NATO metrics)
- Key metrics & thresholds
- **Defence spending trajectories**  # NEW
- **Capability target tracking**  # NEW
- Update cadence
- Alert mechanisms

### 11.3 Forecast Registry
Track predictions with:
- Resolution criteria
- Base rates
- **NATO commitment fulfillment**  # NEW
- Confidence intervals

### 11.5 Infrastructure Exposure
Map compute/data dependencies including NATO systems  # NEW

### 11.6 Momentum Tracking
- Policy anchor gaps
- Narrative prevalence
- **Alliance solidarity index**  # NEW

**Outputs**: `phase11_foresight.json`, `forecast_registry.json`, `calibration_scores.json`

---

## Phase 12 — Extended Analysis (Regional dynamics)

### 12.1 NATO Regional Assessment (NEW)
```python
def analyze_regional_dynamics():
    regional = {
        "baltic_resilience": assess_baltic_cooperation(),
        "black_sea_security": evaluate_black_sea_dynamics(),
        "arctic_capabilities": map_high_north_cooperation(),
        "mediterranean_stability": analyze_south_dynamics(),
        "central_european_depth": assess_v4_b9_cooperation()
    }
```

### 12.2 Country-Specific Deep Dives
Include NATO role and specializations

**Outputs**: `phase12_extended.json`, `phase12_sub1_nato_regional.json`  # NEW

---

## Phase 13 — Closeout

### 13.1 Implementation Plan
- Timeline & milestones
- RACI matrix
- **NATO coordination requirements**  # NEW
- Resource requirements

### 13.2 Success Metrics
Define measurable outcomes including alliance contributions  # NEW

### 13.3 Monitoring Handoff
Transition to operations with NATO reporting  # NEW

### 13.5 Policy Mismatch Panel
Top 5 policy contradictions with fixes including NATO implications  # NEW

**Outputs**: `phase13_closeout.json`, `phase13_sub5_policy_mismatch_panel.json`

---

## Data Quality Framework (NATO sources)

### Evidence Standards (NATO additions)
- **Very High (9-10)**: NATO official documents + national confirmation
- **High (7-8)**: Multiple NATO sources (STO, COEs, DIANA)
- **Medium (5-6)**: Single NATO source + web validation
- **Low (3-4)**: Limited NATO data OR only web mentions
- **Very Low (1-2)**: Single source, unverified

### NATO-Specific Corroboration
- Defence planning documents
- NATO communiqués
- COE publications
- STO technical reports
- Exercise after-action reports

### Validation Gates
- Schema validation for all JSON artifacts
- Policy window filtering (2019-2025)
- Entity resolution checks
- **STANAG compliance verification**  # NEW
- **NATO classification respect**  # NEW

---

## Implementation Notes

### NATO Data Collection Priority
1. **Check NATO membership status first**
   - Member: Full assessment
   - Partner: Limited assessment
   - Non-aligned: Indirect impacts only

2. **Leverage NATO open sources**
   - STO publication database
   - COE websites
   - DIANA public information
   - NATO Multimedia Library

3. **Cross-reference national sources**
   - Defence white papers
   - Parliamentary reports
   - Budget documents
   - Exercise reports

### Critical NATO Relationships
```yaml
nato_members_2025: [
  "AL", "BE", "BG", "CA", "HR", "CZ", "DK", "EE", "FR", "DE",
  "GR", "HU", "IS", "IT", "LV", "LT", "LU", "ME", "NL", "MK",
  "NO", "PL", "PT", "RO", "SK", "SI", "ES", "TR", "UK", "US",
  "FI", "SE"  # Joined 2023-2024
]

key_partners: [
  "UA",  # Enhanced Opportunity Partner
  "GE",  # Aspiring member
  "MD",  # Partnership for Peace
  "BA",  # Membership Action Plan
  "AT", "IE", "CH", "RS"  # Partnership for Peace
]

coe_host_countries: {
  "EE": ["Cyber Defence"],
  "LV": ["Strategic Communications"],
  "LT": ["Energy Security"],
  "CZ": ["CBRN Defence"],
  "SK": ["EOD"],
  "FR": ["Space"],
  "IT": ["Modelling & Simulation"],
  "NL": ["Civil-Military Cooperation"]
}
```

### Quality Assurance Checklist (NATO additions)
- [ ] NATO membership status verified
- [ ] Defence spending data collected
- [ ] Capability targets tracked
- [ ] STANAG compliance assessed
- [ ] COE participation mapped
- [ ] DIANA/NIF involvement checked
- [ ] Minilateral formats identified
- [ ] Framework nation role assessed
- [ ] Exercise participation tracked
- [ ] Industrial integration measured

---

## Key NATO Assessment Questions

For each country, answer:

1. **Strategic Alignment**
   - How aligned are national priorities with NATO EDT?
   - What percentage of defense R&D supports NATO capabilities?
   - Which multinational programs does the country lead?

2. **Capability Contribution**
   - Is the country meeting NDPP targets?
   - What niche capabilities does it provide?
   - How does it contribute to readiness?

3. **Innovation Participation**
   - Does it host DIANA sites or COEs?
   - Has it invested in NIF?
   - How many STO projects does it lead?

4. **Industrial Integration**
   - What share of procurement goes through NSPA?
   - How many STANAGs are implemented?
   - Which NIAG groups does it chair?

5. **Regional Leadership**
   - Does it serve as a framework nation?
   - Which minilateral formats does it lead?
   - What regional initiatives does it drive?

---

*This v3.6 prompt incorporates comprehensive NATO assessment capabilities alongside v3.3 US involvement tracking, closing the critical gap in alliance dynamics analysis.*
