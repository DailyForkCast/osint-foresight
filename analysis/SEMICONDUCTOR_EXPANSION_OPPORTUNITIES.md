# Semiconductor Research Expansion Opportunities
**Date:** 2025-11-02
**Status:** Strategic Planning - Resource Identification
**Zero Fabrication Protocol:** MANDATORY for all expansions

---

## Executive Summary

Current semiconductor data integration provides **market and supply chain foundation** (466 records). Major expansion opportunities exist across **10 categories** leveraging existing databases and publicly available sources. Highest value: **Patent analysis, trade flows, academic collaborations, and geopolitical event correlation**.

---

## Category 1: Patent Intelligence (HIGHEST PRIORITY)

### What We Have
- **USPTO patents:** 425,074 Chinese patents in database
- **CPC classifications:** 65.6M classifications including semiconductor codes
- **Patent metadata:** Assignees, filing dates, technology areas

### What We DON'T Have Yet
- ❌ Semiconductor-specific patent analysis by technology node
- ❌ Time-series patent filing trends (US vs China vs Taiwan)
- ❌ Patent citation networks (US research → Chinese patents)
- ❌ Entity-level analysis (which Chinese companies filing most semiconductor patents)
- ❌ Geographic concentration of semiconductor innovation

### Expansion Opportunities

**1A. Semiconductor CPC Code Analysis**
**Effort:** LOW (data already in database)
**Value:** VERY HIGH (reveals technology transfer patterns)

Key CPC codes to analyze:
- **H01L 21/00** - Semiconductor manufacturing processes
- **H01L 23/00** - Semiconductor device packaging
- **H01L 27/00** - Integrated circuits
- **H01L 29/00** - Semiconductor devices
- **G11C** - Memory devices (DRAM, NAND)
- **H03K 19/** - Logic circuits

**Query Template:**
```sql
SELECT
    SUBSTR(cpc_code, 1, 7) as tech_area,
    COUNT(*) as patent_count,
    COUNT(CASE WHEN assignee_country = 'CN' THEN 1 END) as china_patents,
    MIN(filing_year) as first_filing,
    MAX(filing_year) as latest_filing
FROM uspto_cpc_classifications cpc
JOIN uspto_patents_chinese cp ON cpc.patent_id = cp.patent_id
WHERE cpc_code LIKE 'H01L%' OR cpc_code LIKE 'G11C%'
GROUP BY tech_area
ORDER BY china_patents DESC;
```

**Deliverable:** Semiconductor patent landscape report by technology area

---

**1B. Time-Series Patent Trend Analysis**
**Effort:** LOW (data in database)
**Value:** HIGH (shows China's semiconductor innovation acceleration)

**Analysis Plan:**
1. Chinese semiconductor patent filings 2000-2025 by year
2. Compare to US, Taiwan, South Korea, Japan filing trends
3. Identify inflection points (2015 Made in China 2025, 2018 Trade War, 2022 CHIPS Act)
4. Breakdown by technology node (leading-edge vs mature)
5. Top Chinese assignees (SMIC, Huawei HiSilicon, YMTC, etc.)

**Expected Finding:** Massive surge in Chinese semiconductor patents post-2015

---

**1C. Patent Citation Network Analysis**
**Effort:** MEDIUM (requires citation parsing)
**Value:** VERY HIGH (reveals technology transfer pathways)

**Detection Pattern:**
- US university/company patents (2015-2020)
- → Cited by Chinese company patents (2018-2023)
- → Time lag <3 years = rapid technology transfer
- → Cross-reference with academic collaborations (OpenAlex)

**High-Value Targets:**
- Stanford/MIT semiconductor research → Chinese company patents
- ASML/Applied Materials patents → Chinese equipment companies
- TSMC/Intel process patents → SMIC patents

**Zero Fabrication Note:** Can only report actual citation patterns found in USPTO data, cannot infer "likely" citations.

---

**1D. European Patent Office (EPO) Integration**
**Effort:** MEDIUM (new data source)
**Value:** HIGH (EU-specific semiconductor innovation)

**Data Source:** EPO Open Patent Services (OPS) API
- **Coverage:** European patent applications and grants
- **Free Access:** Yes (with rate limits)
- **Relevance:** European semiconductor equipment patents (ASML, Infineon, STMicroelectronics)

**Collection Strategy:**
- Query EPO API for IPC/CPC codes H01L, G11C
- Focus on Chinese applicants in Europe
- Cross-reference with GLEIF entity data
- Identify EU-China joint patent applications

**Key Intelligence:** Which Chinese companies are filing patents in Europe (strategic EU market entry indicator)

---

## Category 2: Academic Collaboration Intelligence

### What We Have
- **OpenAlex:** 1.56M academic works in database
- **arXiv:** 2.85M preprints with Chinese detection
- **CORDIS:** 383 EU-China research projects

### What We DON'T Have Yet
- ❌ Semiconductor-specific OpenAlex query
- ❌ EU-China semiconductor collaboration network
- ❌ Researcher mobility tracking (EU → China → back to EU)
- ❌ PLA-affiliated semiconductor research identification
- ❌ Technology node research trends (who's publishing on 2nm, GAA, etc.)

### Expansion Opportunities

**2A. OpenAlex Semiconductor Research Query**
**Effort:** LOW (use existing v5 keywords)
**Value:** VERY HIGH (identifies EU-China semiconductor partnerships)

**Query Strategy:**
```python
# Use openalex_technology_keywords_v5.json
# Semiconductor keywords already configured:
# - "semiconductor", "CMOS", "FinFET", "lithography"
# - "EUV", "gate-all-around", "3nm", "5nm", "7nm"
# - "TSMC", "ASML", "photolithography"

# Run OpenAlex collection with filters:
# - Topics: semiconductor manufacturing, chip design, lithography
# - Countries: EU countries + China collaborations
# - Years: 2015-2025 (track CHIPS Act impact)
# - Institution types: University + Corporate
```

**Expected Output:** 5,000-10,000 semiconductor research papers with EU-China co-authorships

**High-Value Analysis:**
- Which EU universities collaborate most with Chinese semiconductor researchers
- Which Chinese institutions partner with EU (Tsinghua, CAS, SMIC corporate research)
- Technology areas of collaboration (design vs manufacturing vs materials)
- Temporal trends (acceleration or deceleration post-2022 export controls)

---

**2B. Researcher Mobility Network Analysis**
**Effort:** MEDIUM (requires author tracking across papers)
**Value:** VERY HIGH (brain drain / talent flow detection)

**Pattern Detection:**
1. **EU → China Flow:**
   - Researcher published at EU institution (2015-2018)
   - → Same researcher at Chinese institution (2019-2022)
   - → Technology transfer risk

2. **China → EU → China Flow:**
   - Chinese researcher at EU institution (training/collaboration)
   - → Returns to China with advanced knowledge
   - → Publications cite EU research methods

3. **Dual Affiliation:**
   - Researcher lists both EU and Chinese institutions
   - → Potential IP leakage pathway

**Data Source:** OpenAlex author affiliation history

**Cross-Reference:** USPTO patents (same authors on both papers and patents)

---

**2C. PLA-Affiliated Semiconductor Research**
**Effort:** LOW (use existing PLA detection patterns)
**Value:** VERY HIGH (military dual-use identification)

**Detection Method:**
- Query OpenAlex for semiconductor keywords + Chinese institutions
- Filter for known PLA universities (National University of Defense Technology, etc.)
- Identify EU co-authors on PLA-affiliated semiconductor papers
- Flag for potential NDAA Section 1260H violations

**Critical Intelligence:** Which EU researchers unknowingly collaborating with Chinese military on semiconductor tech

---

**2D. arXiv Semiconductor Backfill**
**Effort:** LOW (data already in database)
**Value:** MEDIUM (early-stage research indicators)

**Query Pattern:**
```sql
-- Extract semiconductor papers from existing 2.85M arXiv corpus
SELECT * FROM arxiv_papers
WHERE title LIKE '%semiconductor%'
   OR title LIKE '%chip design%'
   OR title LIKE '%lithography%'
   OR categories LIKE '%cs.AR%'  -- Computer Architecture
   OR categories LIKE '%physics.app-ph%';  -- Applied Physics
```

**Expected Output:** 50,000-100,000 semiconductor-related preprints

**Analysis:** Pre-publication collaboration detection (earlier signal than published papers)

---

## Category 3: International Trade Intelligence

### What We Have
- **COMTRADE infrastructure:** Configured but no semiconductor queries run
- **Eurostat:** Economic data including trade flows

### What We DON'T Have Yet
- ❌ Semiconductor equipment import/export data (US, EU, China, Taiwan)
- ❌ Critical mineral trade flows (Gallium, Germanium, Neon)
- ❌ Photoresist and specialty chemical shipments
- ❌ Wafer substrate trade patterns

### Expansion Opportunities

**3A. Semiconductor Equipment Trade Analysis**
**Effort:** MEDIUM (COMTRADE API integration)
**Value:** VERY HIGH (reveals actual equipment flows despite export controls)

**HS Codes for Semiconductors:**
- **8486** - Semiconductor manufacturing equipment (primary code)
  - 8486.10 - Photolithography equipment (EUV, DUV)
  - 8486.20 - Deposition equipment (CVD, PVD, ALD)
  - 8486.30 - Ion implantation equipment
  - 8486.40 - Etching and cleaning equipment
  - 8486.90 - Other semiconductor equipment
- **8541** - Semiconductor devices and ICs
- **8542** - Electronic integrated circuits
- **2804.50** - Silicon (ultra-pure semiconductor-grade)
- **2811.29** - Silane gas (semiconductor precursor)

**Critical Queries:**

**Query 1: US Equipment Exports to China (2015-2025)**
```python
# COMTRADE API query
params = {
    'reporter': 'USA',
    'partner': 'China',
    'hs_code': '8486',  # Semiconductor equipment
    'years': '2015,2016,2017,2018,2019,2020,2021,2022,2023,2024',
    'flow': 'export'
}
```

**Expected Finding:** Sharp decline in 8486.10 (lithography) exports post-2022 (BIS restrictions)

**Query 2: Netherlands (ASML) Exports to China**
```python
# Track ASML EUV equipment exports
params = {
    'reporter': 'Netherlands',
    'partner': 'China',
    'hs_code': '8486.10',  # Photolithography
    'years': '2019,2020,2021,2022,2023,2024',
    'flow': 'export'
}
```

**Expected Finding:** EUV exports stopped ~2020, DUV exports restricted ~2023

**Query 3: China Semiconductor Equipment Imports by Source**
```python
# Who's supplying China's semiconductor industry?
params = {
    'reporter': 'all',
    'partner': 'China',
    'hs_code': '8486',
    'year': '2024',
    'flow': 'export'
}
```

**Expected Output:** Rankings - Japan, South Korea, Taiwan (vs restricted US, Netherlands)

---

**3B. Critical Mineral Trade Flow Analysis**
**Effort:** LOW (COMTRADE API)
**Value:** HIGH (supply chain vulnerability confirmation)

**HS Codes for Critical Minerals:**
- **8112.92** - Gallium (99%+ China supply)
- **8112.99** - Germanium (60% China supply)
- **2804.40** - Neon gas (Ukraine/Russia supply)
- **2846.10** - Rare earth compounds
- **2805.30** - Hafnium

**Critical Analysis:**
1. **China's Gallium/Germanium Export Restrictions (August 2023):**
   - Query HS 8112.92/8112.99 exports from China pre/post August 2023
   - Identify countries most impacted by restrictions
   - Validate supply chain risk assessment in our database

2. **Neon Gas Supply Chain:**
   - Track Ukraine exports pre-war (2021) vs during war (2022-2024)
   - Identify alternative suppliers (Russia, China substitution)
   - Correlate with semiconductor equipment delays

**Expected Finding:** Confirmation of critical mineral chokepoints, quantified impact

---

**3C. Photoresist and Specialty Chemical Trade**
**Effort:** MEDIUM (complex HS codes)
**Value:** MEDIUM (completes supply chain picture)

**HS Codes:**
- **3707** - Photoresist materials
- **2811** - Specialty gases for semiconductors
- **3824.99** - Other chemical preparations (CMP slurries)

**Intelligence Value:** Identify if China developing domestic photoresist capacity (reducing Japan dependency)

---

## Category 4: Corporate Intelligence & Investment Tracking

### What We Have
- **SEC EDGAR:** 944 Chinese companies, 805 in database
- **GLEIF:** 3.1M legal entities with ownership relationships
- **OpenSanctions:** 184K sanctioned entities

### What We DON'T Have Yet
- ❌ Semiconductor-focused company analysis (Chinese investment in US/EU chip firms)
- ❌ Ownership network mapping (who owns semiconductor equipment suppliers)
- ❌ M&A activity tracking (Chinese acquisition attempts)
- ❌ VC funding flows (Chinese investors in European chip startups)

### Expansion Opportunities

**4A. SEC EDGAR Semiconductor Company Deep Dive**
**Effort:** LOW (data in database)
**Value:** HIGH (identifies Chinese-connected semiconductor firms)

**Analysis Plan:**
```sql
-- Find semiconductor companies in SEC EDGAR
SELECT * FROM sec_edgar_companies
WHERE (industry LIKE '%semiconductor%'
   OR industry LIKE '%chip%'
   OR industry LIKE '%integrated circuit%')
  AND (chinese_indicators > 0 OR offshore_jurisdiction IS NOT NULL);
```

**Key Intelligence:**
- Chinese semiconductor companies listed on US exchanges (SMIC, Hua Hong, etc.)
- VIE structures for chip design firms
- US companies with Chinese manufacturing/operations
- Offshore-registered chip companies (Cayman, BVI)

**Cross-Reference:** BIS Entity List (which companies are sanctioned/restricted)

---

**4B. GLEIF Ownership Network - Semiconductor Equipment**
**Effort:** MEDIUM (relationship traversal)
**Value:** VERY HIGH (reveals hidden ownership)

**Analysis Strategy:**
1. **Identify Equipment Suppliers:**
   - Use `semiconductor_equipment_suppliers` table (13 suppliers)
   - Search GLEIF for LEI (Legal Entity Identifier)
   - Map corporate ownership tree

2. **Detect Chinese Investment:**
   - Traverse ownership relationships
   - Flag if Chinese entities appear in ownership chain
   - Identify investment funds with Chinese LPs

3. **Critical Targets:**
   - ASML ownership structure (Dutch government involvement?)
   - Lam Research (any Chinese ownership?)
   - Applied Materials (ownership verification)

**Expected Finding:** Minimal Chinese ownership in critical equipment suppliers (by design), but potential indirect exposure through investment funds

---

**4C. Chinese VC Investment in European Chip Startups**
**Effort:** HIGH (requires external data sources)
**Value:** HIGH (early-stage technology transfer detection)

**Data Sources (Public/Free):**
- **Crunchbase:** Startup funding data (partial free access)
- **PitchBook:** VC investment tracking (paid, but may have free trial)
- **AngelList:** Startup and investor data
- **EU Horizon results:** EU-funded chip startups

**Collection Strategy:**
1. Identify European semiconductor startups (TED contracts, Horizon funding)
2. Check investor lists for Chinese VC firms
3. Cross-reference with Chinese state-backed funds
4. Flag for potential CFIUS-equivalent EU review

**Known Chinese VCs in Tech:**
- Sequoia Capital China
- GGV Capital
- Hillhouse Capital
- IDG Capital

**Critical Question:** Are Chinese VCs investing in European chip design tools, EDA software, or novel materials startups?

---

**4D. M&A Activity Tracking - Failed Chinese Acquisitions**
**Effort:** MEDIUM (news scraping + CFIUS filings)
**Value:** HIGH (reveals Chinese strategic priorities)

**Data Sources:**
- **CFIUS Notices:** Committee on Foreign Investment in the US (annual reports)
- **EU Investment Screening:** European Commission decisions
- **News Archives:** WSJ, FT, Reuters semiconductor M&A coverage

**Notable Failed Acquisitions to Document:**
- 2016: Canyon Bridge (China) → Lattice Semiconductor (US) - BLOCKED by CFIUS
- 2018: CFIUS retroactive block of Ant Financial → MoneyGram (not semiconductor, but pattern)
- 2022: EU blocked Chinese acquisition of European chip equipment firms

**Analysis:** Build database of attempted vs completed Chinese semiconductor M&A (reveals intent even when blocked)

---

## Category 5: Geopolitical Event Correlation

### What We Have
- **GDELT:** Event database configured
- **Semiconductor market data:** WSTS quarterly sales

### What We DON'T Have Yet
- ❌ Correlation of geopolitical events with semiconductor market impacts
- ❌ Export control announcement tracking
- ❌ Taiwan Strait crisis impact on supply chain
- ❌ CHIPS Act milestone tracking

### Expansion Opportunities

**5A. GDELT Semiconductor Event Extraction**
**Effort:** LOW (GDELT infrastructure ready)
**Value:** HIGH (real-time geopolitical risk monitoring)

**Event Categories to Track:**
1. **Export Controls:**
   - CAMEO codes: 174 (Demand policy support), 138 (Threaten with sanctions)
   - Keywords: "export control", "semiconductor restriction", "chip ban"
   - Actors: US, Netherlands, Japan vs China

2. **Taiwan Strait Tensions:**
   - CAMEO codes: 190-195 (Military action/threats)
   - Keywords: "Taiwan Strait", "TSMC", "chip shortage"
   - Sentiment analysis: Escalation vs de-escalation

3. **CHIPS Act Milestones:**
   - Keywords: "CHIPS Act", "fab construction", "Intel Arizona", "TSMC Arizona"
   - Track positive announcements (groundbreaking, hiring, production start)

4. **Supply Chain Disruptions:**
   - Keywords: "semiconductor shortage", "chip shortage", "neon supply"
   - Correlate with market data (WSTS quarterly sales changes)

**Correlation Analysis:**
```sql
-- Example: Taiwan tensions → Market volatility
SELECT
    g.event_date,
    g.goldstein_scale as tension_level,
    m.q1, m.q2, m.q3, m.q4
FROM gdelt_events g
LEFT JOIN semiconductor_market_billings m
    ON YEAR(g.event_date) = m.year
WHERE g.actor1_name LIKE '%China%'
  AND g.actor2_name LIKE '%Taiwan%'
  AND g.event_code BETWEEN 190 AND 195
ORDER BY g.event_date;
```

**Expected Finding:** Taiwan crisis events correlate with semiconductor market volatility

---

**5B. Export Control Impact Analysis**
**Effort:** MEDIUM (event detection + market correlation)
**Value:** VERY HIGH (quantifies policy effectiveness)

**Key Export Control Events to Track:**
- **Oct 7, 2022:** BIS comprehensive China semiconductor restrictions
- **Jan 2023:** Netherlands restricts ASML DUV exports to China
- **July 2023:** Japan restricts semiconductor equipment exports
- **Oct 2023:** BIS updated controls on AI chips

**Analysis Framework:**
1. Extract GDELT events ±30 days around control announcements
2. Query WSTS billings data for same period
3. Measure market impact (China vs Worldwide sales)
4. Track sentiment in media coverage (compliance vs circumvention)

**Expected Finding:** Immediate dip in China semiconductor market post-controls, recovery via domestic substitution

---

**5C. CHIPS Act Project Tracking Dashboard**
**Effort:** MEDIUM (requires Commerce Dept website scraping)
**Value:** MEDIUM (monitors US reshoring progress)

**Data Source:** Department of Commerce CHIPS Act announcements
- URL: https://www.commerce.gov/tags/chips-act
- Format: Press releases, funding announcements

**Collection Strategy:**
1. Scrape Commerce Dept press releases
2. Extract project details:
   - Company name
   - Location (state, city)
   - Funding amount (federal + private)
   - Technology node (leading-edge vs mature)
   - Expected completion date
   - Jobs created estimate

3. Store in new table: `chips_act_projects`

**Database Schema:**
```sql
CREATE TABLE chips_act_projects (
    id INTEGER PRIMARY KEY,
    company_name TEXT,
    project_location TEXT,
    state TEXT,
    federal_funding REAL,  -- USD millions
    private_investment REAL,
    technology_node TEXT,  -- e.g., "2nm leading-edge"
    expected_completion DATE,
    jobs_created INTEGER,
    announcement_date DATE,
    source_url TEXT
);
```

**Analysis:** Track progress toward 2032 capacity tripling goal

---

## Category 6: European-Specific Intelligence

### What We Have
- **TED contracts:** 862K European public procurement
- **Eurostat:** Economic data
- **CORDIS:** EU research projects

### What We DON'T Have Yet
- ❌ European Chips Act project tracking
- ❌ TED semiconductor equipment/facility contracts
- ❌ EU-China semiconductor partnerships beyond CORDIS
- ❌ European semiconductor company landscape

### Expansion Opportunities

**6A. TED Semiconductor Contract Analysis**
**Effort:** LOW (data in database)
**Value:** MEDIUM (EU public investment in semiconductors)

**Query Strategy:**
```sql
-- Find semiconductor-related TED contracts
SELECT * FROM ted_contracts_production
WHERE (contract_title LIKE '%semiconductor%'
   OR contract_title LIKE '%microelectronics%'
   OR contract_title LIKE '%chip%'
   OR cpv_code LIKE '32420000%'  -- Electronic components
   OR cpv_code LIKE '32000000%')  -- Electronic equipment
  AND award_value > 1000000;  -- €1M+ contracts only
```

**Intelligence Value:**
- Which EU countries investing in semiconductor facilities (fabs, R&D centers)
- Chinese companies winning EU semiconductor contracts (potential concern)
- EU subsidy tracking (complements CHIPS Act tracking)

---

**6B. European Chips Act Project Database**
**Effort:** MEDIUM (requires EU Commission website scraping)
**Value:** HIGH (mirrors US CHIPS Act tracking for EU)

**Data Source:** EU Commission Digital Decade
- URL: https://digital-strategy.ec.europa.eu/en/policies/european-chips-act
- Funding: €43B (€3.3B grants + €40B public/private investment)

**Projects to Track:**
- Intel Magdeburg fab (Germany) - €30B investment
- STMicroelectronics/GlobalFoundries France fab - €5.9B
- Infineon Dresden expansion (Germany)
- IMEC research programs (Belgium)

**Database Schema:** Similar to `chips_act_projects` but for EU

---

**6C. EU Semiconductor Company Landscape**
**Effort:** MEDIUM (requires company registry scraping)
**Value:** MEDIUM (identifies European chip firms)

**Data Sources:**
- Companies House (UK)
- Handelsregister (Germany)
- OpenCorporates (global registry aggregator)

**Target Companies:**
- **Major:**
  - Infineon (Germany)
  - STMicroelectronics (France/Italy)
  - NXP (Netherlands)
  - ASML (Netherlands - equipment)
- **Emerging:**
  - SiC/GaN power semiconductor startups
  - Chip design tool companies
  - Novel materials firms

**Cross-Reference:** GLEIF ownership, CORDIS projects, TED contracts

---

## Category 7: Industry Data Sources (Paid/Limited Free Access)

### Available But Not Yet Used

**7A. SEMI (Semiconductor Equipment and Materials International)**
**Access:** Paid membership, some free reports
**Value:** VERY HIGH (official equipment market data)

**Data Available:**
- **SEMI Equipment Market Data (EMDS):** Quarterly equipment sales by region
- **SEMI Silicon Manufacturers Group (SMG):** Wafer shipment data
- **SEMI World Fab Forecast:** New fab construction announcements

**Use Case:** Validate WSTS market data, track equipment sales separate from chip sales

**Free Resources:**
- SEMI press releases (monthly equipment billings - 3 months delayed)
- Annual market reports (summary statistics)

---

**7B. IC Insights**
**Access:** Paid subscription (~$5,000/year)
**Value:** HIGH (detailed forecasts)

**Data Available:**
- Market forecasts by product category
- Company rankings (top 25 semiconductor companies)
- Technology node transition timelines
- Capital expenditure tracking

**Alternative:** Free monthly bulletins provide summary statistics

---

**7C. Gartner Semiconductor Research**
**Access:** Paid subscription
**Value:** MEDIUM (analyst perspectives)

**Data Available:**
- Market share rankings
- Technology trends analysis
- Competitive landscape assessment

**Alternative:** Free webinars and summary reports

---

**7D. TechInsights (formerly Chipworks)**
**Access:** Paid subscription (VERY expensive)
**Value:** VERY HIGH (reverse engineering data)

**Data Available:**
- **Chip teardowns:** Physical analysis of Chinese chips (SMIC process nodes)
- **Process verification:** Actual vs claimed technology nodes
- **IP infringement detection:** Patent violation identification

**Use Case:** Verify if Chinese companies actually achieving claimed technology nodes (e.g., SMIC "7nm" vs TSMC 7nm)

**Zero Fabrication Note:** Would need actual subscription to cite their findings, cannot estimate/assume

---

## Category 8: Shipping & Logistics Intelligence

### Not Currently Tracked

**8A. Semiconductor Equipment Shipment Tracking**
**Effort:** HIGH (requires commercial shipping data)
**Value:** MEDIUM (early indicator of fab construction)

**Data Sources:**
- **Import Genius:** US import records (public via FOIA)
- **Panjiva:** Trade intelligence platform (paid)
- **AIS shipping data:** Track vessels carrying semiconductor equipment

**Use Case:** Detect semiconductor equipment shipments to China despite export controls (gray market, third-country routing)

**Example Intelligence:**
- Dutch ports → Singapore → China (ASML equipment re-routing?)
- Japan → South Korea → China (equipment transit through allies)

---

**8B. Rare Earth Element Shipping Patterns**
**Effort:** HIGH (specialized data source)
**Value:** LOW-MEDIUM (completes supply chain picture)

**Use Case:** Track gallium/germanium shipments from China to US/EU semiconductor manufacturers

---

## Category 9: Regulatory & Policy Tracking

### Partially Tracked (Need Systematization)

**9A. BIS Entity List Semiconductor Updates**
**Effort:** LOW (monthly website check)
**Value:** HIGH (export control enforcement)

**Data Source:** BIS Entity List
- URL: https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern/entity-list
- Update frequency: Monthly

**Collection Strategy:**
1. Monthly scrape of BIS Entity List
2. Filter for semiconductor-related entities
3. Track additions (new restrictions) vs removals (compliance verified)
4. Cross-reference with GLEIF (ownership), USPTO (patents), OpenAlex (research)

**Database Table:** `bis_entity_list` (already exists with 49 entities - expand to full list)

---

**9B. CFIUS Case Tracking - Semiconductor M&A**
**Effort:** MEDIUM (annual report parsing)
**Value:** MEDIUM (blocked deal intelligence)

**Data Source:** CFIUS Annual Report to Congress
- Published annually
- Lists sectors reviewed (semiconductors usually top category)
- Does NOT name companies (confidential)

**Use Case:** Quantify Chinese semiconductor M&A attempts (successful vs blocked)

---

**9C. European Investment Screening Mechanism**
**Effort:** MEDIUM (requires EU Commission monitoring)
**Value:** MEDIUM (EU equivalent of CFIUS)

**Data Source:** EU FDI Screening Regulation (2019)
- Member states notify Commission of FDI screenings
- Semiconductors = critical infrastructure

**Use Case:** Track Chinese attempts to acquire EU semiconductor companies

---

## Category 10: Real-Time Industry Metrics

### Not Yet Tracked (Would Require Automation)

**10A. Fab Construction Announcements**
**Effort:** MEDIUM (news monitoring)
**Value:** MEDIUM (leading indicator)

**Data Sources:**
- Company press releases (TSMC, Intel, Samsung, SMIC)
- Industry news (Semiconductor Engineering, EE Times, AnandTech)
- Government announcements (CHIPS Act awards)

**Collection Strategy:**
- RSS feeds from semiconductor news sites
- Google Alerts for "fab construction", "semiconductor facility"
- Quarterly earnings call transcripts

**Database Table:** `fab_construction_tracker`

---

**10B. Technology Node Transition Tracking**
**Effort:** LOW (news monitoring)
**Value:** HIGH (validates technology leadership claims)

**Milestones to Track:**
- **TSMC:** 2nm risk production (2024), HVM (2025)
- **Intel:** 18A production start (2025)
- **Samsung:** 2nm GAA production (2025)
- **SMIC:** 7nm yield improvement (ongoing)

**Cross-Reference:** TechInsights teardowns to verify actual vs claimed nodes

---

**10C. Yield Rate Intelligence**
**Effort:** HIGH (proprietary data, limited public info)
**Value:** HIGH (actual manufacturing capability indicator)

**Data Sources:**
- Company earnings calls (mentions of yield improvements)
- Industry rumors/reports
- Reverse-calculated from unit sales vs capacity

**Use Case:** Assess if Chinese fabs (SMIC) achieving competitive yields at mature nodes

**Zero Fabrication Note:** Can only report publicly stated yields, cannot estimate

---

## Prioritized Expansion Roadmap

### Phase 1: Quick Wins (Existing Data)
**Timeframe:** 1-2 weeks
**Effort:** LOW
**Value:** VERY HIGH

1. ✅ **USPTO Semiconductor Patent Analysis**
   - Query existing database for H01L, G11C CPC codes
   - Time-series analysis (2000-2025)
   - Chinese vs US patent trends
   - **Deliverable:** Patent intelligence report

2. ✅ **OpenAlex Semiconductor Research Query**
   - Run collection with semiconductor keywords
   - EU-China collaboration network
   - **Deliverable:** Academic collaboration report

3. ✅ **SEC EDGAR Semiconductor Company Analysis**
   - Query existing database for chip companies
   - Chinese ownership/VIE structures
   - **Deliverable:** Corporate intelligence brief

4. ✅ **TED Semiconductor Contract Extraction**
   - Query existing database for semiconductor CPV codes
   - EU public investment analysis
   - **Deliverable:** EU procurement report

**Total:** ~40 hours work, leverages existing data

---

### Phase 2: Medium-Lift Integration (New Queries)
**Timeframe:** 3-4 weeks
**Effort:** MEDIUM
**Value:** HIGH

1. ✅ **COMTRADE Semiconductor Equipment Trade**
   - Query HS code 8486 (equipment)
   - US/Netherlands/Japan → China flows
   - Pre/post export control comparison
   - **Deliverable:** Trade flow intelligence report

2. ✅ **COMTRADE Critical Mineral Flows**
   - Query HS codes for Gallium, Germanium, Neon
   - China export restrictions impact (Aug 2023)
   - **Deliverable:** Supply chain vulnerability validation

3. ✅ **GDELT Semiconductor Event Extraction**
   - Export control announcements
   - Taiwan Strait tensions
   - CHIPS Act milestones
   - **Deliverable:** Geopolitical event timeline

4. ✅ **GLEIF Equipment Supplier Ownership**
   - Map ASML, Lam Research, Applied Materials ownership
   - Detect Chinese investment exposure
   - **Deliverable:** Ownership network analysis

5. ✅ **BIS Entity List Semiconductor Filtering**
   - Expand entity list to full coverage
   - Cross-reference with patents, research, trade
   - **Deliverable:** Sanctions compliance dashboard

**Total:** ~80 hours work, new data integrations

---

### Phase 3: External Data Sources (Requires New Access)
**Timeframe:** 2-3 months
**Effort:** HIGH
**Value:** HIGH

1. ✅ **EPO Patent Data Collection**
   - Set up EPO OPS API access
   - Query for Chinese semiconductor patents in Europe
   - **Deliverable:** European patent landscape

2. ✅ **CHIPS Act Project Tracker**
   - Scrape Commerce Dept announcements
   - Build project database
   - Progress dashboard
   - **Deliverable:** US reshoring tracker

3. ✅ **European Chips Act Tracker**
   - Scrape EU Commission site
   - Build EU project database
   - **Deliverable:** EU reshoring tracker

4. ✅ **SEMI Data Integration (if budget available)**
   - Subscribe to SEMI equipment data
   - Integrate quarterly equipment sales
   - **Deliverable:** Equipment market trends

5. ⚠️ **VC Investment Research**
   - Research Chinese VC investments in EU chip startups
   - Manual collection (no free API)
   - **Deliverable:** Investment risk report

**Total:** ~150 hours work + potential subscription costs

---

### Phase 4: Advanced Analytics (Long-term)
**Timeframe:** 6+ months
**Effort:** VERY HIGH
**Value:** VERY HIGH

1. ✅ **Patent Citation Network Analysis**
   - Parse USPTO citation data
   - Build US → China citation graph
   - Identify technology transfer pathways
   - **Deliverable:** Technology transfer network map

2. ✅ **Researcher Mobility Tracking**
   - OpenAlex author affiliation history
   - Track EU → China → EU flows
   - **Deliverable:** Brain drain analysis

3. ✅ **Shipping Data Integration**
   - Access import/export records (Import Genius)
   - Track equipment shipments
   - **Deliverable:** Logistics intelligence

4. ✅ **Real-time News Monitoring**
   - Set up RSS feeds + alerts
   - Automate fab construction tracking
   - **Deliverable:** Live industry dashboard

5. ✅ **Yield Rate Intelligence (if possible)**
   - Collect public statements
   - Build yield tracking database
   - **Deliverable:** Manufacturing capability assessment

**Total:** 250+ hours, ongoing monitoring

---

## Resource Requirements

### Internal Resources (No Cost)
- ✅ USPTO patents (already in database)
- ✅ OpenAlex academic research (free API)
- ✅ COMTRADE trade data (free API, rate-limited)
- ✅ SEC EDGAR filings (public)
- ✅ GLEIF entity data (already in database)
- ✅ TED contracts (already in database)
- ✅ GDELT events (public)
- ✅ BIS Entity List (public website)

### External Resources (Free/Limited)
- ✅ EPO OPS API (free with rate limits)
- ✅ CHIPS Act announcements (public website scraping)
- ✅ European Chips Act (public website scraping)
- ✅ SEMI press releases (free, 3-month delay)
- ✅ Company press releases (public)
- ⚠️ OpenCorporates (freemium - limited free queries)

### Paid Resources (Optional)
- ⚠️ SEMI EMDS subscription (~$5,000-10,000/year)
- ⚠️ IC Insights subscription (~$5,000/year)
- ⚠️ TechInsights teardowns (~$50,000+/year)
- ⚠️ Import Genius shipping data (~$1,000-5,000/year)
- ⚠️ Panjiva trade intelligence (expensive)

### Time Investment Estimates
- **Phase 1 (Quick Wins):** 40 hours (1 week full-time)
- **Phase 2 (Medium-Lift):** 80 hours (2 weeks full-time)
- **Phase 3 (External Sources):** 150 hours (4 weeks full-time)
- **Phase 4 (Advanced Analytics):** 250+ hours (ongoing)

**Total for Phases 1-3:** ~270 hours (7 weeks full-time)

---

## Highest Value Targets (Top 5)

### 1. USPTO Semiconductor Patent Analysis
**Why:** Data already in database, reveals China's technology progression
**Effort:** LOW (2-3 days)
**Value:** VERY HIGH
**Deliverable:** Patent landscape report showing China's semiconductor innovation surge

### 2. COMTRADE Equipment Trade Flows
**Why:** Quantifies export control effectiveness, reveals actual equipment flows
**Effort:** MEDIUM (1 week)
**Value:** VERY HIGH
**Deliverable:** Trade intelligence showing pre/post control comparisons

### 3. OpenAlex Semiconductor Collaborations
**Why:** Identifies EU-China research partnerships in semiconductors
**Effort:** LOW (2-3 days)
**Value:** VERY HIGH
**Deliverable:** Academic collaboration network analysis

### 4. GDELT Geopolitical Event Correlation
**Why:** Links policy events to market impacts, real-time risk monitoring
**Effort:** MEDIUM (1 week)
**Value:** HIGH
**Deliverable:** Geopolitical risk timeline with market correlation

### 5. GLEIF Equipment Supplier Ownership
**Why:** Reveals hidden Chinese exposure in critical supply chain
**Effort:** MEDIUM (1 week)
**Value:** HIGH
**Deliverable:** Ownership network map for ASML, Lam Research, etc.

---

## Zero Fabrication Protocol Compliance

All expansion activities MUST comply with Zero Fabrication Protocol:

### ✅ ALLOWED:
- Report actual patent counts from USPTO database
- Quote trade statistics from COMTRADE API
- List verified collaborations from OpenAlex
- Document announced projects from government websites
- Present ownership relationships from GLEIF

### ❌ FORBIDDEN:
- Estimate equipment sales without SEMI subscription
- Infer yield rates without public company statements
- Assume technology transfer without citation evidence
- Guess investment amounts without source documents
- Claim market share without industry data

### 📋 REQUIRED FOR ALL EXPANSIONS:
1. **Source Attribution:** Every data point cited to source
2. **Extraction Method:** Document how data was obtained
3. **Audit Trail:** Reproducible queries and scripts
4. **Limitations:** Explicitly state what we DON'T know

---

## Recommendation

**START WITH PHASE 1 (Quick Wins):**
1. USPTO semiconductor patents (2-3 days)
2. OpenAlex semiconductor research (2-3 days)
3. SEC EDGAR semiconductor companies (1 day)
4. TED semiconductor contracts (1 day)

**Total: 1 week, zero cost, very high value**

This provides immediate intelligence value while validating the expansion approach before investing in more complex integrations.

**Next: Phase 2 (COMTRADE + GDELT + GLEIF) - 2 weeks**

Would you like me to start with any of these expansions?
