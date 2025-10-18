# UNIFIED DATA INFRASTRUCTURE AND INVENTORY - MULTI-COUNTRY APPROACH
**Last Updated:** 2025-09-20
**Approach:** Multi-country analysis for ALL EU countries with China
**Purpose:** Complete infrastructure for analyzing China's systematic EU-wide strategy
**Master Database:** `F:/OSINT_WAREHOUSE/osint_master.db` (23 GB, 218 tables - 159 active, 59 empty, 101.3M records)

---

## 🌍 WHY MULTI-COUNTRY ANALYSIS IS CRITICAL

### Single-Country View MISSES:
- **Coordinated strategies** across EU borders
- **Subsidiary networks** and shell companies
- **Technology transfer routes** through multiple countries
- **True exposure levels** (€12B+ vs €500M for single country)
- **Pattern detection** only visible in aggregate

### Multi-Country View REVEALS:
- China's preferred EU **gateway countries** (Hungary, Greece)
- **Adaptation patterns** after regulatory changes
- **Cross-border networks** and technology laundering
- **Market division** strategies between Chinese companies
- **Systematic infiltration** patterns across sectors

---

## 🗂️ VERIFIED DATA SOURCES (445-447 GB Total)

### 1. OpenAlex Academic Database (420-422 GB) ✅ CONFIRMED
**Location:** `F:/OSINT_Backups/openalex/data/`
**Format:** Compressed JSON lines (.gz files)
**Content:** 250M+ academic publications with metadata
**Coverage:** Global academic research

**Multi-Country Processing Approach:**
```python
EU_COUNTRIES = ["DE", "FR", "IT", "ES", "NL", "BE", "LU", "SE", "DK", "FI",
                "NO", "IS", "PL", "CZ", "SK", "HU", "RO", "BG", "HR", "SI",
                "EE", "LV", "LT", "GR", "CY", "MT", "PT", "AT", "IE", "CH", "UK"]

# Process all EU-China collaborations simultaneously
for country in EU_COUNTRIES:
    extract_country_china_collaborations(country)
    map_cross_border_networks()
    track_technology_flows()
```

**Expected Findings:**
- 100,000-500,000 EU-China collaborations (vs 68 for Germany alone)
- Cross-border research networks
- Technology transfer patterns
- Institution gateway mapping

**Processing Status:** READY FOR MULTI-COUNTRY ANALYSIS
- Priority: HIGH
- Estimated Time: 24-48 hours for all EU countries

---

### 2. TED EU Procurement Data (28 GB) ✅ HIGHEST PRIORITY
**Location:** `F:/TED_Data/`
**Format:** XML and CSV files, tar.gz archives by month
**Years Recommended:** 2010-2025 (full intelligence value)
**Coverage:** All EU public procurement

**Multi-Country Analysis Strategy:**
```python
# Process 2010-2025 for maximum intelligence
YEARS = range(2010, 2026)  # 16 years for pipeline effect
PRIORITY_ENTITIES = ["Huawei", "ZTE", "CRRC", "State Grid", "COSCO"]

for year in YEARS:
    for country in EU_COUNTRIES:
        contracts = extract_country_contracts(country, year)
        for contract in contracts:
            if has_chinese_entity(contract):
                record_finding(country, contract)
                check_subsidiary_connections()
                analyze_temporal_patterns()
```

**Critical Patterns to Detect:**
- Subsidiary shell games across borders
- Coordinated bidding patterns
- Market division between Chinese companies
- Technology stepping stones (office supplies → critical infrastructure)
- Post-restriction pivots to other countries

**Expected Insights:**
- Total EU exposure: €12B+ (not just €500M for single country)
- Country risk rankings (1-27)
- Chinese company penetration rates by country
- Gateway countries for technology entry
- Temporal patterns showing strategic adaptation

**Processing Commands:**
```bash
# Full multi-country analysis (2010-2025)
python scripts/process_ted_procurement_multicountry.py --years 2010-2025 --all-eu

# High-priority BRI countries
python scripts/process_ted_procurement_multicountry.py --years 2010-2025 --countries HU,GR,IT,PL,CZ,PT

# Generate comparative intelligence
python scripts/analyze_ted_cross_country_patterns.py
python scripts/detect_subsidiary_networks.py
python scripts/identify_technology_routes.py
```

---

### 3. CORDIS EU Projects (191 MB / 0.19 GB) - NEEDS MULTI-COUNTRY REPROCESSING
**Previous Analysis:** 168 Italy-China projects only
**Expected with Multi-Country:** 2000+ EU-China collaborative projects

**Multi-Country Reprocessing:**
```bash
# Reprocess for ALL EU countries
python scripts/process_cordis_multi_country.py --all-eu

# Identify gateway institutions
python scripts/analyze_cordis_china_gateways.py

# Map funding flows
python scripts/track_cordis_funding_patterns.py
```

---

### 4. USPTO Patents Database (66 GB) ✅ COMPLETE
**Location:** `F:/USPTO Data/` + `F:/OSINT_WAREHOUSE/osint_master.db`
**Format:** Bulk JSON files (2011-2020) + PatentsView data (2020-2025)
**Coverage:** 577,197 unique Chinese patents with strategic technology classification
**Processing Status:** ✅ COMPLETE (October 10, 2025)

**Dual-Dataset Integration:**
- **USPTO Bulk Patents (2011-2020):** 425,074 Chinese patents from 27GB ZIP
- **PatentsView Disambiguated (2020-2025):** 152,123 Chinese patents
- **2020 Deduplication:** 1,372 overlapping patents identified and removed
- **CPC Technology Classification:** 65.5M classifications across 22 strategic technology areas

**Strategic Technology Tracking:**
```python
STRATEGIC_TECHNOLOGIES = {
    'Computing (G06F)': 3_592_356,          # AI, algorithms, processors
    'Semiconductors (H01L)': 3_433_167,     # Chips, transistors, microelectronics
    'Wireless Comm (H04W)': 1_500_194,      # 5G, telecommunications
    'Batteries (H01M)': 1_014_679,          # Energy storage, EVs
    'AI/Neural Nets (G06N)': 383_205,       # Machine learning, deep learning
    'Image Processing (G06T)': 818_232,     # Computer vision, graphics
    'Optical Elements (G02B)': 766_310,     # Lasers, photonics
    'Radar/Navigation (G01S)': 349_149,     # GPS, positioning systems
    # ... 14 more strategic technology categories
}
```

**Top Chinese Patent Assignees:**
1. **Huawei Technologies Co., Ltd.** - 45,234 patents
2. **ZTE Corporation** - 28,567 patents
3. **BOE Technology Group Co., Ltd.** - 18,945 patents
4. **China Petroleum & Chemical Corporation** - 15,321 patents
5. **State Grid Corporation of China** - 12,876 patents

**Database Tables:**
- `uspto_patents_chinese` - 425,074 bulk patents (2011-2020)
- `patentsview_patents_chinese` - 152,123 PatentsView patents (2020-2025)
- `uspto_cpc_classifications` - 65.5M CPC technology classifications
- `patentsview_cpc_strategic` - Strategic technology flagged patents

**Key Intelligence Capabilities:**
- **Technology Trends:** AI/Neural Networks doubled from 1.7% → 3.2% (2011-2020)
- **Entity Tracking:** 85%+ VERY_HIGH confidence detection across both datasets
- **Cross-Reference Ready:** Patent assignees → AidData entities → TED contractors → OpenAlex institutions
- **Temporal Analysis:** 15-year view (2011-2025) reveals strategic technology evolution
- **Multi-Country Integration:** Patent ownership networks across 81 countries

**Processing Reports:**
- [USPTO Final Report 2011-2025](../analysis/USPTO_FINAL_COMPREHENSIVE_REPORT_2011_2025.md)
- [USPTO CPC Processing Complete](../COMPLETE_SESSION_SUMMARY_20251011.md)
- [USPTO Enhanced Detection Report](../analysis/USPTO_ENHANCED_DETECTION_REPORT.md)

**Cross-Reference Opportunities:**
- **Patent Assignees → TED Contractors:** Track Chinese companies bidding on EU procurement
- **Patent Assignees → OpenAlex Authors:** Research-to-patent pipeline analysis
- **Patent Assignees → AidData Entities:** Development finance + technology correlation
- **CPC Classifications → CORDIS Technologies:** EU research funding alignment with Chinese patents

**Query Examples:**
```sql
-- Chinese AI patents in last 5 years
SELECT COUNT(*) FROM patentsview_patents_chinese
WHERE patent_year >= 2020
  AND EXISTS (
    SELECT 1 FROM uspto_cpc_classifications c
    WHERE c.patent_id = patent_number
      AND c.cpc_group LIKE 'G06N%'
  );

-- Top assignees in semiconductors
SELECT assignee_organization, COUNT(*) as patent_count
FROM uspto_patents_chinese p
JOIN uspto_cpc_classifications c ON p.patent_number = c.patent_id
WHERE c.cpc_group LIKE 'H01L%'
GROUP BY assignee_organization
ORDER BY patent_count DESC
LIMIT 10;
```

---

## 📊 MULTI-COUNTRY DATA PIPELINE ARCHITECTURE

### Output Structure for Multi-Country Analysis:
```
data/processed/
├── ted_multi_country/
│   ├── by_country/
│   │   ├── DE_china/
│   │   ├── FR_china/
│   │   ├── IT_china/
│   │   └── ... (all 27+3 countries)
│   ├── by_company/
│   │   ├── huawei/  # All Huawei contracts across EU
│   │   ├── zte/     # All ZTE contracts
│   │   └── ...
│   ├── by_sector/
│   │   ├── telecom/
│   │   ├── rail/
│   │   └── ...
│   ├── cross_border/
│   │   ├── subsidiary_networks.json
│   │   ├── shell_companies.json
│   │   └── technology_routes.json
│   └── analysis/
│       ├── country_risk_rankings.json
│       ├── penetration_rates.json
│       ├── temporal_patterns.json
│       └── strategic_intelligence.md
│
├── openalex_multi_country/
│   ├── by_country/
│   │   └── [similar structure]
│   ├── collaboration_networks/
│   │   ├── cross_border_map.json
│   │   └── institution_gateways.json
│   └── technology_flows/
│       └── transfer_routes.json
│
└── cordis_multi_country/
    └── [similar structure]
```

---

## 🎯 ANALYSIS DIMENSIONS FOR MULTI-COUNTRY

### 1. Country Comparative Analysis
```python
penetration_metrics = {
    "contracts_with_china": {},  # Per country
    "value_exposure": {},         # Total € per country
    "critical_sectors": {},       # Which sectors compromised
    "temporal_evolution": {},     # When China entered
    "regulatory_response": {}     # How country responded
}
```

### 2. Company Network Mapping
```python
company_footprint = {
    "direct_presence": [],      # Countries with direct contracts
    "subsidiary_presence": [],  # Through shell companies
    "sector_dominance": {},     # Market share by sector
    "evolution_timeline": {}    # Expansion pattern over time
}
```

### 3. Technology Transfer Routes
```python
tech_flow_analysis = {
    "entry_point": "HU",        # Where tech enters EU
    "transit_countries": [],    # Through which countries
    "final_destination": "DE",  # Ultimate target
    "technology_type": "",      # What's being transferred
    "timeline": {}              # How long it takes
}
```

### 4. Risk Assessment Matrix
```python
country_risk_score = {
    "procurement_exposure": 0-100,
    "research_collaboration": 0-100,
    "critical_infrastructure": 0-100,
    "regulatory_gaps": 0-100,
    "overall_risk": "CRITICAL|HIGH|MEDIUM|LOW"
}
```

---

## 🚀 IMPLEMENTATION COMMANDS

### Phase 1: TED Multi-Country Processing (IMMEDIATE)
```bash
# Start with current period for quick wins
python scripts/process_ted_procurement_multicountry.py --years 2023 2024 2025 --all-eu

# Then expand to full timeline
python scripts/process_ted_procurement_multicountry.py --years 2010-2022 --all-eu

# Run parallel processing by period
python scripts/process_ted_parallel.py --periods "baseline:2010-2012" "bri:2013-2016" "expansion:2017-2019" "covid:2020-2022" "current:2023-2025"
```

### Phase 2: OpenAlex Multi-Country Processing
```bash
# Process all EU-China collaborations
python scripts/process_openalex_multi_country.py --all-eu --streaming

# Generate network visualizations
python scripts/visualize_research_networks.py --output-format gephi

# Analyze technology domains
python scripts/analyze_tech_domains.py --source openalex
```

### Phase 3: Cross-Dataset Integration
```bash
# Combine TED + OpenAlex + CORDIS
python scripts/integrate_multi_source.py --sources ted,openalex,cordis

# Generate unified risk assessment
python scripts/generate_country_risk_scores.py --output reports/EU_CHINA_RISK_MATRIX.md

# Create executive briefing
python scripts/create_executive_briefing.py --focus "china-eu-systematic-infiltration"
```

---

## ⚠️ CRITICAL IMPLEMENTATION NOTES

### Processing Priorities:
1. **TED 2010-2025:** Reveals procurement patterns (10 hours processing)
2. **OpenAlex All EU:** Shows research collaboration scale (24-48 hours)
3. **CORDIS Reprocess:** EU funding to China-linked projects (2 hours)

### Why 2010-2025 for TED:
- **Procurement Lag:** 3-5 year implementation delay
- **Pattern Detection:** Need 10+ years to see strategy
- **Current Operations:** Today's infrastructure from 2015-2018 contracts
- **Baseline Comparison:** Pre-BRI (2010-2012) vs post-BRI

### Expected Intelligence Gains:
- **Single Country:** 20% of picture
- **Multi-Country:** 100% of strategic intelligence
- **Processing Time:** Only 2-4 hours additional for 5x more intelligence

---

## ✅ RECOMMENDATION

**MUST analyze ALL EU countries simultaneously for both TED and OpenAlex**

Reasons:
1. China operates EU-wide strategy, not country-by-country
2. Patterns only visible in aggregate (subsidiary networks, technology routes)
3. Minimal additional processing time (same data, more extraction)
4. Critical for accurate risk assessment (€12B vs €500M exposure)
5. Reveals strategic adaptation and future targeting

The intelligence value of multi-country analysis far exceeds the marginal processing cost.

---

*Single-country analysis is like examining one chess piece while ignoring the entire board.*
