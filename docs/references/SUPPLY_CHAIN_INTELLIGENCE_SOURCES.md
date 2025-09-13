# Supply Chain Intelligence Sources - Free Alternatives to UN Comtrade

## Overview
Comprehensive supply chain analysis using multiple free data sources to replace UN Comtrade dependency.

---

## 🟢 Trade Flow Data - FREE Sources

### 1. WITS (World Bank) - Primary Recommendation
- **URL**: https://wits.worldbank.org/
- **Coverage**: 200+ countries, historical data back to 1962
- **Data**: Import/export by HS codes, tariffs, trade agreements
- **API**: Yes, free
- **Format**: CSV, Excel, JSON
- **Update**: Monthly
- **Usage**: Bilateral trade flows, product-level analysis

### 2. Eurostat Comext Database
- **URL**: https://ec.europa.eu/eurostat/web/international-trade-in-goods/database
- **Coverage**: All EU/EEA countries + partners
- **Data**: Monthly import/export by CN8 codes
- **API**: Multiple (SDMX, REST, JSON)
- **Format**: CSV, SDMX-ML, JSON-stat
- **Update**: Monthly (11:00 and 23:00 CET)
- **Usage**: Detailed EU trade analysis

### 3. National Statistics Agencies
```yaml
priority_countries:
  Germany: 
    agency: Destatis
    url: https://www-genesis.destatis.de/
    api: GENESIS-Online API
  
  France:
    agency: INSEE  
    url: https://www.insee.fr/en/accueil
    api: Sirene API
  
  Netherlands:
    agency: CBS
    url: https://opendata.cbs.nl/
    api: CBS Open Data API
  
  Austria:
    agency: Statistik Austria
    url: https://www.statistik.at/
    api: STATcube API
```

### 4. Observatory of Economic Complexity (OEC)
- **URL**: https://oec.world/
- **Coverage**: 5000+ products, 200+ countries
- **Data**: Export/import complexity, RCA analysis
- **API**: Yes, GraphQL
- **Visualization**: Built-in charts and maps
- **Usage**: Product competitiveness analysis

---

## 🚢 Shipping & Logistics Data

### Vessel Tracking (Real-time)
1. **VesselFinder** - https://www.vesselfinder.com/
2. **MarineTraffic** - https://www.marinetraffic.com/
3. **AISHub** - https://www.aishub.net/ (API available)
4. **MyShipTracking** - https://www.myshiptracking.com/

### Port Statistics
1. **World Bank Port Data** - Container throughput (TEU)
2. **UNCTAD Port Statistics** - Annual container data
3. **National Port Authorities** - Country-specific data
4. **Port Performance Index** - World Bank efficiency metrics

### Supply Chain Mapping
```python
# Example: Track vessels from key suppliers
import requests

def track_supply_route(origin_port, destination_port):
    """Track shipping routes between key ports"""
    # Use AISHub API for vessel positions
    # Cross-reference with port statistics
    # Identify supply chain bottlenecks
```

---

## 🏢 Company & Ownership Data

### Limited Free Access
1. **GLEIF** - Legal Entity Identifiers (LEI)
   - Global LEI database
   - Corporate hierarchy (limited)
   - API: https://www.gleif.org/lei-data/

2. **EU Business Registers** 
   - Basic company information
   - **Portal**: https://e-justice.europa.eu/
   - **EBRA Network**: https://ebra.be/

3. **National Company Registers**
```yaml
free_access:
  UK: Companies House (basic data free)
  Denmark: CVR (Central Business Register)
  Latvia: Lursoft (limited free)
  Estonia: Business Registry

limited_free:
  Germany: Handelsregister (paid)
  France: INSEE Sirene (basic free)
  Netherlands: KVK (limited free)
```

### ⚠️ Beneficial Ownership Limitations
- **BORIS system**: Connects EU registers but paid access
- **Court ruling 2022**: Reduced public access
- **Alternative**: Focus on direct suppliers, use procurement data

---

## 💰 Procurement & Contract Intelligence

### EU-Wide
1. **TED (Tenders Electronic Daily)**
   - All major EU contracts
   - Supply chain relationships via awards
   - **Coverage**: Contracts >€140k (supplies), >€215k (services)

### National Procurement Portals
```yaml
high_value_sources:
  Germany: 
    - vergabe24.de
    - evergabe-online.de
  France:
    - marches-publics.gouv.fr
  Netherlands:
    - tenderned.nl
  Austria:
    - bbg.gv.at
```

### Usage for Supply Chain Analysis
- Map government suppliers by sector
- Identify critical technology providers  
- Track contract awards over time
- Analyze supplier concentration

---

## 🔬 Technology & Research Networks

### Research Collaboration (Supply Chain R&D)
1. **OpenAlex** - Research partnerships
2. **CORDIS** - EU project participants
3. **CrossRef** - Co-authorship networks

### Standards Participation
1. **IETF Datatracker** - Internet standards
2. **ETSI** - European telecom standards
3. **ISO** - International standards participation

### Patent Networks
1. **EPO OPS** - European patents
2. **Google Patents** - Global patent data (BigQuery)
3. **WIPO Global Brand Database** - Trademarks

---

## 📊 Economic Indicators

### Country-Level Risk Assessment
1. **World Bank** - GDP, trade ratios, economic complexity
2. **OECD** - Economic indicators, trade in value added
3. **Eurostat** - EU economic statistics
4. **IMF** - Balance of payments, external debt

### Sector-Specific Indicators
1. **IEA** - Energy trade, critical minerals
2. **FAO** - Agricultural trade dependencies
3. **UNCTAD** - Digital trade, services

---

## 🧩 Integrated Supply Chain Framework

### Multi-Source Analysis Pipeline

```python
# Comprehensive supply chain intelligence
class SupplyChainIntelligence:
    
    def analyze_country_dependencies(self, country_code):
        """Multi-source supply chain analysis"""
        
        # 1. Trade flows (WITS + Eurostat)
        trade_data = self.get_trade_flows(country_code)
        
        # 2. Shipping routes (AIS data)
        shipping_data = self.get_shipping_routes(country_code)
        
        # 3. Procurement contracts (TED + national)
        procurement_data = self.get_procurement_awards(country_code)
        
        # 4. Research networks (OpenAlex, CORDIS)
        research_networks = self.get_research_collaboration(country_code)
        
        # 5. Company networks (GLEIF, business registers)
        company_data = self.get_company_networks(country_code)
        
        return self.synthesize_intelligence(
            trade_data, shipping_data, procurement_data,
            research_networks, company_data
        )
```

### Key Metrics to Track

#### Trade Dependency Metrics
- **Import concentration**: Top 5 suppliers' share by product
- **Single points of failure**: Products with >50% from one country
- **Critical materials**: Rare earth, semiconductors, energy

#### Network Resilience
- **Route diversity**: Number of shipping routes per product
- **Supplier redundancy**: Alternative suppliers available
- **Geographic concentration**: Risk clustering

#### Innovation Networks
- **R&D partnerships**: Cross-border research collaboration
- **Patent co-filing**: Joint intellectual property
- **Standards participation**: Influence in technology standards

---

## 🎯 Implementation Priority

### Phase 1: Core Trade Intelligence
1. **WITS API** - Set up automated trade flow collection
2. **Eurostat API** - EU-specific detailed analysis
3. **National APIs** - Country-specific granular data

### Phase 2: Real-Time Monitoring
1. **AISHub API** - Vessel tracking automation
2. **TED scraping** - Procurement contract monitoring
3. **Port statistics** - Throughput trend analysis

### Phase 3: Network Analysis
1. **OpenAlex** - Research network mapping
2. **GLEIF** - Corporate structure analysis
3. **Patent networks** - Technology dependency mapping

### Phase 4: Integration & Automation
1. **Multi-source dashboard** - Real-time supply chain status
2. **Alert system** - Dependency concentration warnings
3. **Predictive analytics** - Risk scenario modeling

---

## 📝 Data Collection Scripts

### Trade Flows
```bash
# WITS trade data
python -m src.pulls.wits_pull --country AT --years 2020-2024

# Eurostat detailed data  
python -m src.pulls.eurostat_pull --country AT --monthly

# National statistics
python -m src.pulls.national_stats_pull --country AT --agency destatis
```

### Shipping Intelligence
```bash
# Vessel tracking
python -m src.pulls.ais_pull --ports "Hamburg,Rotterdam,Antwerp"

# Port statistics
python -m src.pulls.port_stats_pull --regions EU --quarterly
```

### Procurement Networks
```bash
# TED contracts
python -m src.pulls.ted_pull --country AT --cpv-tech

# National procurement
python -m src.pulls.procurement_pull --country AT --monthly-export
```

---

## 🔍 Alternative Intelligence Sources

### Satellite Data (Free Tiers)
1. **Sentinel Hub** - Ship detection, port activity
2. **NASA Worldview** - Economic activity indicators
3. **Google Earth Engine** - Industrial facility monitoring

### Social Intelligence
1. **LinkedIn** - Company relationships, employee movement
2. **GitHub** - Software supply chains, developer networks
3. **Academic conferences** - Research collaboration trends

### Financial Intelligence
1. **SEC filings** (US) - Supplier relationships in 10-K forms
2. **Annual reports** - Supply chain risk disclosures
3. **Credit risk databases** - Company financial health

---

## ✅ Success Metrics

### Coverage Goals
- **Trade flows**: 95% of imports by value tracked
- **Key suppliers**: Top 20 suppliers per critical product identified
- **Shipping routes**: Major routes monitored in real-time
- **Procurement**: Government suppliers mapped by technology sector

### Quality Targets
- **Update frequency**: Weekly for trade, daily for shipping
- **Accuracy**: Cross-validation between 2+ sources
- **Completeness**: Missing data <5% for critical categories
- **Timeliness**: Data lag <30 days for trade, real-time for shipping

---

*This framework provides comprehensive supply chain intelligence without dependency on paid UN Comtrade subscriptions*

*Total cost: $0 for all core sources*
*Coverage: Global trade flows, EU detailed data, real-time shipping, procurement networks*