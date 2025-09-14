# OSINT Foresight v3.5 Execution Checklist
## Complete Implementation Guide for Phases 0-13

Generated: 2025-09-13

---

## 🚀 QUICK START CHECKLIST

### Prerequisites
- [ ] OpenAlex snapshot downloaded (420GB on F: drive)
- [ ] National statistics API keys obtained (where required)
- [ ] CORDIS scraping configured (bulk API pending)
- [ ] Google Patents BigQuery access setup
- [ ] Multilingual search terms configured (20+ languages)
- [ ] Country selection confirmed: _________________

---

## 📋 PHASE-BY-PHASE EXECUTION

### ✅ Phase 0: Definitions & Taxonomy

**Scripts to run:**
```bash
python src/analysis/phase0_taxonomy.py --country={{COUNTRY}}
```

**Outputs to verify:**
- [ ] `phase00_taxonomy.json` - 15 technology domains defined
- [ ] `id_registry.json` - ROR/GRID/LEI/ORCID mappings
- [ ] `alias_map.json` - Multilingual entity aliases

**Quality checks:**
- [ ] All 15 technology categories populated
- [ ] Dual-use classifications assigned
- [ ] MCF terminology defined

---

### ✅ Phase 1: Setup & Configuration

**Scripts to run:**
```bash
python src/analysis/phase1_setup.py --country={{COUNTRY}}
```

**Manual tasks:**
- [ ] Define geographic scope (national vs subnational)
- [ ] Select priority technologies (3-5 from taxonomy)
- [ ] Configure hub discovery parameters
- [ ] Set narrative tracking keywords

**Outputs to verify:**
- [ ] `phase01_setup.json` - Complete configuration
- [ ] `collection_strategy.json` - Data source priorities
- [ ] `phase01_sub5_narratives.json` - Narrative framework

---

### ✅ Phase 2: Indicators & Data Sources

**Scripts to run:**
```bash
# For automated countries (28)
python scripts/data_pull/pull_national_statistics.py --country={{COUNTRY}}

# For manual countries (16) - quarterly download required
python scripts/data_pull/download_manual_stats.py --country={{COUNTRY}}
```

**Data source status:**
| Source | Status | Action Required |
|--------|--------|-----------------|
| National Stats | ⚡ | Check if automated (28) or manual (16) |
| CrossRef | ✅ | API ready |
| OpenAlex | ✅ | Use F: drive snapshot |
| Patents | ✅ | BigQuery configured |
| CORDIS | ⚠️ | Use scraper if no API |
| Common Crawl | ⚡ | Configure search patterns |

**Outputs to verify:**
- [ ] `phase02_indicators.json` - Indicator catalog
- [ ] `sources.yaml` - Active data sources
- [ ] `metric_catalog.csv` - Complete metrics list

---

### ✅ Phase 3: Technology Landscape

**Scripts to run:**
```bash
python src/analysis/phase3_landscape.py --country={{COUNTRY}}
```

**Multilingual searches:**
- [ ] Government actors (EN + local + 中文)
- [ ] Academic institutions
- [ ] Private sector players
- [ ] Policy documents (2019-2025 window)

**Outputs to verify:**
- [ ] `phase03_landscape.json` - Complete ecosystem map
- [ ] `policy_index.json` - Policies within window
- [ ] `phase03_actors.json` - Deduplicated entities

---

### ✅ Phase 4: Supply Chain Security (PARALLEL)

**Scripts to run:**
```bash
# Run parallel to Phase 3
python src/analysis/phase4_supply_chain.py --country={{COUNTRY}}
```

**Common Crawl patterns:**
```yaml
patterns:
  - "our suppliers include"
  - "we partner with"
  - "sourced from"
  - "manufactured by"
languages: [EN, local, zh-CN]
```

**Outputs to verify:**
- [ ] `phase04_supply_chain.json` - Component analysis
- [ ] `supply_chain_map.json` - Visual network
- [ ] `procurement_signals.csv` - Pattern detection

---

### ✅ Phase 5: Institutions & Networks

**Scripts to run:**
```bash
python src/analysis/phase5_institutions.py --country={{COUNTRY}}
```

**Entity resolution tasks:**
- [ ] Match ROR IDs for institutions
- [ ] Assign LEI codes for companies
- [ ] Link ORCID profiles for researchers
- [ ] Deduplicate across sources

**NEW: Hub Discovery (5.5-5.6):**
- [ ] Run outlier detection (z-score ≥ 2.0)
- [ ] Review discovered centers
- [ ] Auto-promote qualified hubs
- [ ] Add to AUTO_HUBS array

**Outputs to verify:**
- [ ] `phase05_institutions.json` - Resolved entities
- [ ] `phase05_sub5_outlier_centers.json` - Hidden innovation
- [ ] `phase05_sub6_auto_hubs.json` - Promoted hubs

---

### ✅ Phase 6: Funding & Instruments

**Scripts to run:**
```bash
python src/analysis/phase6_funders.py --country={{COUNTRY}}
```

**Funding sources to check:**
- [ ] National programs (automated or manual)
- [ ] EU Horizon Europe (if eligible)
- [ ] Regional/local support
- [ ] VC/PE activity (Common Crawl)
- [ ] Corporate R&D

**Control mapping:**
- [ ] NSPM-33 applicability
- [ ] EU screening requirements
- [ ] Export control implications

**Outputs to verify:**
- [ ] `phase06_funders.json` - Funding landscape
- [ ] `funding_controls_map.json` - Restrictions

---

### ✅ Phase 7: International Links

**Scripts to run:**
```bash
python src/analysis/phase7_links.py --country={{COUNTRY}}
```

**Collaboration analysis:**
- [ ] Co-authorship networks (OpenAlex)
- [ ] Joint patents (BigQuery)
- [ ] Standards participation (IETF)
- [ ] Conference participation

**Risk patterns:**
- [ ] Dual-use collaborations identified
- [ ] Sensitive entity ties mapped
- [ ] Risk levels assessed

**Outputs to verify:**
- [ ] `phase07_links.json` - Collaboration data
- [ ] `standards_activity.json` - Committee participation
- [ ] `phase07_bilateral.json` - Partner analysis

---

### ✅ Phase 8: Risk Assessment

**Scripts to run:**
```bash
python src/analysis/phase8_risk.py --country={{COUNTRY}}
```

**Risk mechanisms (limit 6):**
1. [ ] Technology leakage
2. [ ] Supply disruption
3. [ ] Talent drain
4. [ ] Standards capture
5. [ ] Investment dependency
6. [ ] Cyber vulnerability

**For each risk define:**
- [ ] Single-sentence mechanism
- [ ] Probability range (10-30%, 30-60%, 60-90%)
- [ ] Impact level (Low/Med/High)
- [ ] Time horizon (2y/5y/10y)
- [ ] Numeric indicators

**Outputs to verify:**
- [ ] `phase08_risk.json` - Risk assessment
- [ ] `risk_indicators.json` - Monitoring metrics
- [ ] `phase08_monitoring.json` - Strategy

---

### ✅ Phase 9: PRC Interest & MCF

**Scripts to run:**
```bash
python src/analysis/phase9_posture.py --country={{COUNTRY}}
```

**Standard assessment (9.1-9.9):**
- [ ] Motivations & doctrine
- [ ] Policy framework
- [ ] Key actors (with 中文 aliases)
- [ ] Acquisition mechanisms
- [ ] Target technologies
- [ ] Progress assessment

**NEW: Soft-points (9.10):**
- [ ] Standards committees
- [ ] Talent pipelines
- [ ] Cloud dependencies
- [ ] Supply chain nodes

**NEW: Policy Crosswalk (9.11):**
- [ ] Verify claims vs primary sources
- [ ] Document enforcement examples
- [ ] Log contradictions

**Outputs to verify:**
- [ ] `phase09_posture.json` - MCF assessment
- [ ] `phase09_sub11_anchor_crosswalk.json` - Verification
- [ ] `contradictions_log.csv` - Discrepancies

---

### ✅ Phase 10: Red Team Review

**Scripts to run:**
```bash
python src/analysis/phase10_redteam.py --country={{COUNTRY}}
```

**Assumption testing:**
- [ ] Design falsification tests
- [ ] Generate alternative explanations
- [ ] Assess data quality
- [ ] Document confidence levels

**Adversary simulation:**
- [ ] Define adversary objectives
- [ ] Develop adversary plans
- [ ] Identify counter-indicators
- [ ] Test detection capabilities

**Outputs to verify:**
- [ ] `phase10_redteam.json` - Review results
- [ ] `adversary_plan.json` - Simulation output

---

### ✅ Phase 11: Foresight & Early Warning

**Scripts to run:**
```bash
python src/analysis/phase11_foresight.py --country={{COUNTRY}}
```

**Scenario development (2-4):**
- [ ] Baseline scenario
- [ ] Accelerated scenario
- [ ] Disrupted scenario
- [ ] Wildcard scenario

**Each scenario needs:**
- [ ] Narrative (≤180 words)
- [ ] Numeric indicators
- [ ] Trigger events
- [ ] Probability estimate

**Early warning system:**
- [ ] Key metrics defined
- [ ] Thresholds calculated
- [ ] Update cadence set
- [ ] Alert mechanisms configured

**Outputs to verify:**
- [ ] `phase11_foresight.json` - Scenarios
- [ ] `forecast_registry.json` - Predictions
- [ ] `calibration_scores.json` - Accuracy tracking
- [ ] `early_warning_system.json` - Monitoring

---

### ✅ Phase 12: Extended Analysis (Optional)

**Country-specific deep dives:**
- [ ] Identify unique factors
- [ ] Conduct sector analysis
- [ ] Define wildcards
- [ ] Assess special risks

**Outputs to verify:**
- [ ] `phase12_extended.json` - Deep dive results

---

### ✅ Phase 13: Closeout

**Implementation planning:**
- [ ] Create timeline with milestones
- [ ] Build RACI matrix
- [ ] Estimate resource requirements
- [ ] Define success metrics

**NEW: Policy Mismatch Panel (13.5):**
- [ ] Identify top 5 contradictions
- [ ] Assess impact
- [ ] Recommend fixes

**Handoff preparation:**
- [ ] Document monitoring procedures
- [ ] Package collection scripts
- [ ] Create training materials
- [ ] Export configurations

**Outputs to verify:**
- [ ] `phase13_closeout.json` - Complete plan
- [ ] `phase13_sub5_policy_mismatch_panel.json` - Fixes

---

## 🔍 QUALITY ASSURANCE

### Data Quality Checks
- [ ] **Structured sources**: 80% of claims backed
- [ ] **Common Crawl validation**: 20% enhancement
- [ ] **Corroboration**: ≥2 sources for moderate+ claims
- [ ] **Primary sources**: Required for high-impact claims
- [ ] **Date compliance**: All within POLICY_WINDOW (2019-2025)

### Evidence Tracking
- [ ] All claims logged to `evidence_master.csv`
- [ ] Contradictions logged to `contradictions_log.csv`
- [ ] Confidence levels documented (1-10 scale)
- [ ] Data quality assessed (1-5 scale)

### Schema Validation
- [ ] All JSON outputs validate against schemas
- [ ] Required fields populated
- [ ] Data types correct
- [ ] Relationships valid

---

## 📊 DATA SOURCE AUTOMATION STATUS

### Fully Automated (28 countries)
```
Tier 1: DE, FR, NL, NO, DK, UK, SE, CH, IT, ES
Tier 2: AT, FI, IE, PL, BE, CZ, HU, PT, GR, SI
```

### Partially Automated (8 countries)
```
LU, LT, LV, EE, IS, LI, AD, SM
```

### Manual Quarterly (16 countries)
```
Eastern EU: BG, HR, RO, SK
Balkans: RS, ME, MK, AL, BA, XK
Other: TR, CY, MT, UA, GE, MD
```

---

## 🎯 CRITICAL SUCCESS FACTORS

1. **Data Foundation**
   - OpenAlex snapshot accessible (F: drive)
   - National statistics pulling correctly
   - Common Crawl patterns configured

2. **Multilingual Coverage**
   - Searches in EN + local + 中文
   - Entity aliases captured
   - Translation quality verified

3. **Evidence Standards**
   - Corroboration rule enforced
   - Sources properly cited
   - Confidence documented

4. **Temporal Compliance**
   - Policy window respected (2019-2025)
   - Update frequencies maintained
   - Historical baselines established

5. **Quality Gates**
   - Schema validation passing
   - Entity resolution complete
   - Coverage thresholds met

---

## 💡 TROUBLESHOOTING

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| National stats API fails | Check if country is manual (16) not automated (28) |
| CORDIS access denied | Use web scraper fallback |
| EPO OPS not approved | Use Google Patents BigQuery instead |
| Low corroboration | Expand Common Crawl search patterns |
| Entity duplicates | Improve ROR/LEI/ORCID matching |
| Policy outside window | Filter to 2019-2025 only |
| Hub discovery empty | Lower z-score threshold from 2.0 to 1.5 |
| Contradictions found | Log to CSV and document in report |

---

## 📅 RECOMMENDED TIMELINE

**Week 1**: Foundation (Phases 0-2)
- Day 1-2: Taxonomy & setup
- Day 3-4: Configure data sources
- Day 5: Pull initial indicators

**Week 2**: Landscape (Phases 3-4)
- Day 1-2: Technology landscape
- Day 1-2: Supply chain (parallel)
- Day 3-4: Policy analysis
- Day 5: Infrastructure mapping

**Week 3**: Networks (Phases 5-7)
- Day 1-2: Entity resolution
- Day 3: Hub discovery
- Day 4-5: Collaboration analysis

**Week 4**: Assessment (Phases 8-9)
- Day 1-2: Risk mechanisms
- Day 3-4: MCF analysis
- Day 5: Policy crosswalk

**Week 5**: Validation (Phases 10-11)
- Day 1-2: Red team review
- Day 3-4: Scenario development
- Day 5: Early warning system

**Week 6**: Finalization (Phases 12-13)
- Day 1-2: Extended analysis
- Day 3-4: Implementation planning
- Day 5: Handoff preparation

---

## ✅ FINAL CHECKLIST

Before considering analysis complete:

- [ ] All 14 phases executed (0-13)
- [ ] All required outputs generated
- [ ] Evidence standards met (≥2 sources)
- [ ] Multilingual searches completed
- [ ] Hub discovery performed
- [ ] Policy crosswalk verified
- [ ] Contradictions documented
- [ ] Schemas validated
- [ ] Quality gates passed
- [ ] Handoff materials prepared

---

*This checklist ensures comprehensive implementation of the OSINT Foresight v3.5 framework with all enhancements.*
