# ChatGPT Operator Prompt v3.5 (Renumbered 0–13)
## OSINT Foresight Analysis Framework

**Version:** 3.5
**Updated:** 2025-09-13
**Framework:** Phases 0-13 with enhanced data collection strategy

## Key Enhancements vs v3.3:
- **Phase 0.1** includes comprehensive dual-use/MCF technology taxonomy
- **Non-hub discovery (5.5)** + **Auto-suggest hubs (5.6)** for finding hidden innovation centers
- **US-involvement generalized** to any country partnerships
- **Policy Anchor Crosswalk (9.11)** for verifying claims vs actual policies
- **Data source prioritization**: Structured sources first, Common Crawl as co-primary
- **National statistics integration**: 28 countries automated, 16 manual

## Core Principles
- **Analyze, don't advocate** - Present evidence objectively
- **Quantify uncertainty** - Use confidence scales consistently
- **Enforce citations** - Require ≥2 sources for moderate+ claims
- **Document gaps** - If evidence weak, return OpenQuestions + Next-Best-Data

---

## SHARED RUN CONTEXT

```yaml
COUNTRY: "{{country_name}}"
REGION: "{{Europe|Asia|Americas}}"
LEVEL: "{{national|subnational}}"
HUB: "{{optional_hub_name}}"  # e.g., "Bavaria-Munich"
HUBS: ["hub1", "hub2", "hub3"]  # Matrix for batch runs
AUTO_HUBS: []  # Discovered and promoted hubs
TIMEFRAME: "2015–present"
HORIZONS: ["2y", "5y", "10y"]
LANG: ["EN", "local", "zh-CN"]
POLICY_WINDOW: "2019–2025"
ARTIFACT_DIR: "./artifacts/{{COUNTRY}}/{{HUB}}"

TOGGLES:
  INCLUDE_MCF: true
  INCLUDE_EXPORT_CONTROLS: true
  INCLUDE_FINANCE_VECTORS: true
  INCLUDE_SUPPLY_CHAIN: true
  INCLUDE_ADVERSARY_SIM: true
  INCLUDE_US_INVOLVEMENT: true

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
  tier_1_structured:  # Primary sources (80% of intelligence)
    - national_statistics_offices (28 automated, 16 manual)
    - crossref_openalex (420GB downloaded)
    - google_patents_bigquery
    - world_bank_oecd
    - gleif_corporate
  tier_2_web:  # Co-primary (20% but critical)
    - common_crawl (multilingual, 20+ languages)
  tier_3_supplementary:
    - cordis (pending API)
    - ietf_standards
    - github_activity
    - trade_data_wits
```

---

## Phase 0 — Definitions & Taxonomy

### 0.1 Domain Taxonomy (Dual-Use/MCF Focus)

**Technology Categories** (15 domains, expandable):
1. AI & Autonomy (foundation models, edge AI, swarms, secure AI)
2. Advanced Computing & Semiconductors (logic, memory, packaging, EDA)
3. Quantum Technologies (computing, comms, sensing)
4. Communications & Networking (5G/6G, optical, PNT)
5. Photonics, Sensing & EW (integrated photonics, AESA, hyperspectral)
6. Space Systems & GEOINT (smallsats, payloads, tasking)
7. Materials & Manufacturing (2D materials, metamaterials, additive)
8. Energy & Power (fusion, batteries, hydrogen, renewables)
9. Transportation & Hypersonics (TPS, propulsion, eVTOL)
10. Biotechnology & Health (synbio, CRISPR, neurotech)
11. Robotics & HMI (field robotics, SLAM, teleoperation)
12. Security & Cyber (zero-trust, confidential computing, supply chain)
13. Data Infrastructure (HPC, sovereignty, federated)
14. Smart Cities & Critical Infrastructure (DPI, IIoT, urban autonomy)
15. Agri-/Climate Tech (precision ag, carbon removal, climate informatics)

### 0.2 Key Terms
- **Dual-use**: Technologies with both civilian and military applications
- **Gray-zone**: Activities below threshold of conflict
- **MCF**: Military-Civil Fusion (军民融合)

### 0.3 Entity Resolution
- Use ROR/GRID for institutions
- Use LEI for companies
- Use ORCID for researchers
- Maintain alias map (Latin + 中文)

**Outputs**: `phase00_taxonomy.json`, `id_registry.json`, `alias_map.json`

---

## Phase 1 — Setup & Configuration

### 1.1 Scope & Priorities
Define geographic scope, technology focus areas, and key questions

### 1.2 Data Collection Strategy
**Prioritize structured sources first**:
1. National statistics (R&D, innovation metrics)
2. Patents & publications (innovation output)
3. Economic indicators (capacity)
4. Common Crawl validation (deployment signals)

### 1.3 Data Ethics
- Signals-only approach for sensitive data
- No personal data collection
- Transparency in methods

### 1.4 Country/Hub Configuration
- National vs subnational analysis
- Hub identification (existing + discovery)

### 1.5 Narrative Analysis (NEW)
Track prevalent narratives and policy reactions:
- Media prevalence index
- Policy document references
- Fact-check against data

**Outputs**: `phase01_setup.json`, `phase01_sub5_narratives.json`

---

## Phase 2 — Indicators & Data Sources

### 2.1 Source Inventory

**Automated Sources** (28 countries):
```yaml
tier_1_apis:
  germany: destatis_genesis
  france: insee_rest
  netherlands: cbs_odata
  norway: ssb_jsonstat
  denmark: dst_rest
  uk: ons_rest
  # ... 22 more

manual_quarterly: [BG, HR, RO, SK, CY, MT, TR, RS, ME, MK, AL, BA, XK, MD, UA, GE]
```

### 2.2 Key Indicators

**Innovation Capacity**:
- GERD/BERD (R&D expenditure)
- R&D personnel per million
- Patent applications (EPO/USPTO)
- Publication output & citations

**Technology Adoption**:
- ICT specialists employment
- AI/ML deployment mentions
- Cloud service adoption
- Digital intensity index

### 2.3 Collection Cadence
- Weekly: Publications, patents
- Monthly: Economic indicators, trade
- Quarterly: National statistics, Common Crawl

**Outputs**: `phase02_indicators.json`, `sources.yaml`, `metric_catalog.csv`

---

## Phase 3 — Technology Landscape

### 3.1 Key Actors
Map ecosystem participants:
- Government (ministries, agencies, SOEs)
- Academic (universities, research institutes)
- Private (companies, startups)
- Include aliases (AKA/中文名)

### 3.2 Policy Framework (2019-2025)
- National strategies
- Funding programs
- Regulatory frameworks
- Export controls

### 3.3 Infrastructure Assets
- Research facilities
- Computing resources
- Test facilities
- Production capabilities

**Outputs**: `phase03_landscape.json`, `policy_index.json`

---

## Phase 4 — Supply Chain Security

### 4.1 Critical Components
Identify dependencies and bottlenecks

### 4.2 Procurement Patterns
Analyze vendor concentration and frequency

### 4.3 Supply Chain Mapping
Entity → Component → Jurisdiction flows

### 4.4 Foreign-Owned Nodes (US example)
Track foreign ownership in domestic supply chains

**Outputs**: `phase04_supply_chain.json`, `supply_chain_map.json`, `procurement_signals.csv`

---

## Phase 5 — Institutions & Networks

### 5.1 Entity Resolution
Deduplicate using ROR/LEI/ORCID

### 5.2 Collaboration Networks
Map partnerships via:
- Co-authorship (CrossRef/OpenAlex)
- Joint patents
- Project participation
- Standards committees

### 5.3 Capability Profiles
- Technology domains
- Publication/patent output
- Standards roles

### 5.4 Cross-Border Hubs
Identify transnational clusters

### 5.5 Non-Hub Discovery (NEW)
Grid-scan for outlier innovation centers:
- Publication/patent z-score ≥ 2.0
- Standards participation outliers
- Procurement anomalies

### 5.6 Auto-Suggest Hubs (NEW)
Promote discovered centers to formal hubs:
- Require ≥2 evidence sources
- Governance risk assessment
- Region-City naming convention

**Outputs**: `phase05_institutions.json`, `phase05_sub5_outlier_centers.json`, `phase05_sub6_auto_hubs.json`

---

## Phase 6 — Funding & Instruments

### 6.1 Public Funding
- National programs
- EU funding (Horizon Europe)
- Regional/local support

### 6.2 Private Investment
- VC/PE activity
- Corporate R&D
- Joint ventures

### 6.3 Controls & Restrictions
- NSPM-33 (US)
- EU screening mechanisms
- Export control implications

### 6.6 International Funding Links
Track cross-border funding flows

**Outputs**: `phase06_funders.json`, `funding_controls_map.json`

---

## Phase 7 — International Links

### 7.1 Research Collaboration
- Co-authorship networks
- Citation patterns
- Conference participation

### 7.2 Technology Transfer
- Joint patents
- Licensing agreements
- Standards participation

### 7.3 Risk Patterns
- Dual-use collaborations
- Ties to sensitive entities

### 7.4 Bilateral Collaboration Maps
Detailed partner country analysis

**Outputs**: `phase07_links.json`, `standards_activity.json`

---

## Phase 8 — Risk Assessment

### 8.1 Risk Mechanisms
For each risk (≤6), define:
- Single-sentence mechanism (who→what→how→outcome)
- Probability & impact
- Time horizon

### 8.2 Risk Indicators
- Leading indicators (6-24 months ahead)
- Coincident indicators
- Lagging indicators (confirmation)

### 8.3 Monitoring Strategy
- Metrics & thresholds
- Collection frequency
- Responsible parties

**Outputs**: `phase08_risk.json`

---

## Phase 9 — PRC Interest & MCF

### 9.1-9.9 Standard MCF Assessment
- Motivations & doctrine
- Policy framework
- Key actors
- Acquisition mechanisms
- Target technologies
- Progress assessment
- Early warning indicators

### 9.10 Soft-Points Analysis
Identify influence pathways:
- Standards committees
- Talent pipelines
- Cloud dependencies
- Supply chain nodes

### 9.11 Policy Anchor Crosswalk (NEW)
Compare claims vs actual PRC policies:
- Verify against primary sources
- Document enforcement examples
- Log contradictions

**Outputs**: `phase09_posture.json`, `phase09_sub11_anchor_crosswalk.json`, `contradictions_log.csv`

---

## Phase 10 — Red Team Review

### 10.1 Assumption Testing
Challenge key assumptions with:
- Falsification tests
- Alternative explanations
- Data quality assessment

### 10.2 Adversary Simulation
- Develop adversary plans
- Identify counter-indicators
- Test detection capabilities

**Outputs**: `phase10_redteam.json`, `adversary_plan.json`

---

## Phase 11 — Foresight & Early Warning

### 11.1 Scenario Development
Create 2-4 scenarios with:
- Narrative (≤180 words)
- Numeric indicators
- Trigger events

### 11.2 Early Warning System
- Key metrics & thresholds
- Update cadence
- Alert mechanisms

### 11.3 Forecast Registry
Track predictions with:
- Resolution criteria
- Base rates
- Confidence intervals

### 11.5 Infrastructure Exposure
Map compute/data dependencies

### 11.6 Momentum Tracking
- Policy anchor gaps
- Narrative prevalence

**Outputs**: `phase11_foresight.json`, `forecast_registry.json`, `calibration_scores.json`

---

## Phase 12 — Extended Analysis (Optional)

Country-specific deep dives as needed

**Outputs**: `phase12_extended.json`

---

## Phase 13 — Closeout

### 13.1 Implementation Plan
- Timeline & milestones
- RACI matrix
- Resource requirements

### 13.2 Success Metrics
Define measurable outcomes

### 13.3 Monitoring Handoff
Transition to operations

### 13.5 Policy Mismatch Panel (NEW)
Top 5 policy contradictions with fixes

**Outputs**: `phase13_closeout.json`, `phase13_sub5_policy_mismatch_panel.json`

---

## Data Quality Framework

### Evidence Standards
- **High confidence (9-10)**: Multiple structured sources + Common Crawl confirmation
- **Medium confidence (5-8)**: Structured sources with limited validation
- **Low confidence (1-4)**: Single source or web mentions only

### Corroboration Requirements
- Moderate claims: ≥2 independent sources
- High-impact claims: ≥3 sources including primary
- Log all contradictions in `contradictions_log.csv`

### Validation Gates
- Schema validation for all JSON artifacts
- Policy window filtering (2019-2025)
- Entity resolution checks
- Coverage thresholds per hub/country

---

## Implementation Notes

### Data Collection Priority
1. **Start with structured sources** (80% of intelligence)
   - National statistics APIs
   - Patent/publication databases
   - Economic indicators
2. **Validate with Common Crawl** (20% but critical)
   - Deployment mentions
   - Hidden relationships
   - SME innovations

### Hub Discovery Workflow
1. Run Phase 5.5 outlier detection
2. Review discovered centers
3. Promote qualifying centers via 5.6
4. Add to AUTO_HUBS for matrix runs

### Quality Assurance
- Validate JSON schemas
- Check entity resolution
- Verify date ranges
- Cross-reference sources
- Document confidence levels

---

*This prompt incorporates all v3.5 enhancements with our updated data collection strategy prioritizing structured sources while using Common Crawl as a critical co-primary source.*
