# Supply Chain Intelligence: Free and Low-Cost Resources
**Mapping global supply chains without expensive subscriptions**
**Date: September 10, 2025**

## 1. FREE GOVERNMENT TRADE DATABASES

### 1.1 UN Comtrade - The Foundation

**What It Is:**
- Global trade statistics from 170+ countries
- Product-level detail (HS codes)
- Monthly/annual data
- API access (free tier)

**How to Use for Supply Chain:**
```python
import requests
import pandas as pd

def get_trade_flows(reporter='703', partner='156', year='2024'):
    # 703 = Slovakia, 156 = China
    url = "https://comtrade.un.org/api/get"
    params = {
        'r': reporter,  # Slovakia
        'p': partner,   # China
        'ps': year,
        'px': 'HS',
        'cc': '8507',   # HS code for batteries
        'fmt': 'json'
    }
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json()['dataset'])

# Analyze battery component imports
battery_components = {
    '8507': 'Electric batteries',
    '2836': 'Carbonates (lithium)',
    '8506': 'Primary cells',
    '3801': 'Graphite',
    '2805': 'Rare earth metals'
}

for hs_code, description in battery_components.items():
    data = get_trade_flows(cc=hs_code)
    print(f"{description}: ${data['TradeValue'].sum():,.0f}")
```

**Limitations:**
- Aggregated data (not company-specific)
- 2-3 month delay
- Some countries report poorly

### 1.2 National Customs Databases (Free)

**US Import Data:**
```python
# US Census Bureau - USA Trade Online (free)
# https://usatrade.census.gov/

# Automated Manifest System (AMS) - some free access
# Shows actual importers/exporters for US trade
```

**EU Trade Data:**
```python
# Eurostat COMEXT (free)
def get_eu_trade_data():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DS-018995"
    params = {
        'geo': 'SK',
        'partner': 'CN',
        'product': '8507'  # Batteries
    }
    # Returns detailed EU trade statistics
```

**China Customs (English):**
- http://english.customs.gov.cn/
- Monthly trade bulletins
- Some company-specific data in reports

### 1.3 Export Control and Sanctions Data

**Free Sources:**
```python
# US Export Administration Regulations (EAR)
# Entity List - updated weekly
import pandas as pd

def get_entity_list():
    url = "https://www.bis.doc.gov/index.php/documents/consolidated-entity-list/downloads"
    # Download and parse Excel file
    entity_list = pd.read_excel('entity_list.xlsx')
    
    # Check if suppliers are restricted
    restricted = entity_list[entity_list['Country'] == 'China']
    return restricted

# EU Sanctions Map (API available)
def check_eu_sanctions():
    url = "https://www.sanctionsmap.eu/api/v1/sanctions"
    # Returns JSON of all EU sanctions
```

## 2. BILL OF LADING AND SHIPPING DATA

### 2.1 Free/Cheap Maritime Intelligence

**MarineTraffic (Limited Free)**
```python
# Track vessels carrying goods
# Free: Current position, basic vessel info
# API: Starting at €99/month

def track_vessel(vessel_name):
    # Basic vessel position from AIS data
    # Free tier shows current location only
    pass
```

**VesselFinder (Free Tier)**
- Real-time vessel positions
- Port calls history (limited)
- Container tracking (basic)

**Port Authority Websites (Free)**
```python
# Many ports publish arrival/departure data
port_sources = {
    'Hamburg': 'https://www.hafen-hamburg.de/en/ships',
    'Rotterdam': 'https://www.portofrotterdam.com/en/shipping/arrivals-and-departures',
    'Koper': 'https://www.luka-kp.si/eng/vessel-arrivals',
    'Gdansk': 'https://www.portgdansk.pl/en/ships-in-port'
}

# Scrape arrival/departure data
def get_port_calls(port_url):
    # Parse vessel arrivals with cargo type
    pass
```

### 2.2 US Import Records (Partially Free)

**ImportYeti (Free Tier)**
```python
# https://www.importyeti.com/
# Free: 5 searches/month
# Shows actual US importers and their suppliers

def search_importyeti(company_name):
    # Manual search required
    # Returns:
    # - Supplier names and addresses
    # - Product descriptions
    # - Shipment frequency
    # - Competitor suppliers
```

**USA Trade Data (Free Samples)**
- Some providers offer free samples
- Historical data sometimes free
- Academic access sometimes available

## 3. COMPANY SELF-REPORTED DATA

### 3.1 Sustainability and ESG Reports

**Where to Find Supply Chain Disclosures:**
```python
import requests
from bs4 import BeautifulSoup

def get_sustainability_reports(company):
    sources = [
        f"https://{company}.com/sustainability",
        f"https://{company}.com/investors/annual-reports",
        f"https://{company}.com/esg"
    ]
    
    supply_chain_info = []
    for url in sources:
        # Parse PDFs for supplier lists
        # Look for: "key suppliers", "supply chain", "sourcing"
        pass
    
    return supply_chain_info

# CDP Supply Chain (some free data)
def check_cdp_disclosures():
    # https://www.cdp.net/en/supply-chain
    # Companies disclose supplier emissions
    pass
```

### 3.2 Regulatory Filings

**Conflict Minerals Reports (US Listed):**
```python
# SEC Form SD - Specialized Disclosure
def get_conflict_minerals_report(ticker):
    # Shows entire supply chain for tin, tantalum, tungsten, gold
    url = f"https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'CIK': ticker,
        'type': 'SD',
        'output': 'atom'
    }
    # Parse for supplier lists
```

**EU Supply Chain Due Diligence:**
```python
# Coming into force 2024-2027
# Will require supply chain mapping disclosure
# Check company websites for early compliance
```

## 4. INDUSTRY AND TRADE ASSOCIATIONS

### 4.1 Battery Industry Specific (Free Reports)

**Benchmark Mineral Intelligence (Some Free)**
- Monthly free webinars with data
- Quarterly free reports
- Price assessments (delayed)

**IEA Battery Reports (Free)**
```python
def get_iea_battery_data():
    reports = [
        "https://www.iea.org/reports/global-ev-outlook-2024",
        "https://www.iea.org/reports/batteries-and-secure-energy-transitions"
    ]
    # Contains supply chain analysis
    # Regional production data
    # Trade flow analysis
```

**China Battery Industry Association**
- Some English reports
- Production statistics
- Export data

### 4.2 Trade Association Databases

**European Battery Alliance**
- Member lists (potential suppliers)
- Project mappings
- Supply chain initiatives

**Slovak Battery Alliance**
```python
# If exists, would show:
# - Local suppliers
# - Partnership announcements
# - Industry statistics
```

## 5. PATENT AND TECHNICAL STANDARDS

### 5.1 Patent Supply Chain Clues

```python
# Patents often reveal suppliers through:
# 1. Co-assignees (joint development)
# 2. Citations (technology sources)
# 3. Inventor affiliations (personnel movement)

def analyze_patent_supply_chain(company):
    url = "https://api.lens.org/patent/search"
    query = {
        'applicant': company,
        'include': ['biblio', 'parties']
    }
    
    # Look for:
    # - Joint patents with suppliers
    # - Licensed technology sources
    # - Technical dependencies
```

### 5.2 Technical Standards Participation

```python
# Standards bodies show who's working together
standards_sources = {
    'ISO': 'https://www.iso.org/committee/5269920.html',  # Battery standards
    'IEC': 'https://www.iec.ch/batteries',
    'SAE': 'https://www.sae.org/standards/power-and-energy-storage-batteries'
}

# Committee membership reveals supply chain relationships
```

## 6. OPEN SOURCE INTELLIGENCE TECHNIQUES

### 6.1 LinkedIn Intelligence (Free)

```python
# Map personnel movement between companies
def map_supplier_relationships():
    # Search for:
    # "formerly at [Supplier] now at [Customer]"
    # "procurement manager" + company
    # "supply chain" + company
    # "vendor management" + company
    
    # Reveals:
    # - Actual supplier relationships
    # - New partnerships forming
    # - Supply chain changes
```

### 6.2 Job Postings Analysis

```python
def analyze_supply_chain_jobs(company):
    sites = [
        'indeed.com',
        'linkedin.com/jobs',
        'glassdoor.com'
    ]
    
    keywords = [
        'supplier quality engineer',
        'vendor manager',
        'procurement specialist',
        'supply chain analyst'
    ]
    
    # Job descriptions often mention:
    # - Specific suppliers
    # - Technologies used
    # - Geographic focus
    # - Compliance requirements
```

### 6.3 Press Release Mining

```python
import feedparser

def monitor_supply_chain_news():
    feeds = [
        'https://news.google.com/rss/search?q=supply+agreement+battery',
        'https://news.google.com/rss/search?q=supplier+contract+slovakia'
    ]
    
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            # Parse for supplier announcements
            # Partnership agreements
            # Supply disruptions
```

## 7. SATELLITE AND GEOSPATIAL (Free Tiers)

### 7.1 Sentinel Hub (Free European Satellites)

```python
# Monitor factory construction, expansions
from sentinelhub import SHConfig, SentinelHubRequest

def monitor_facility(lat, lon, date_from, date_to):
    # 10m resolution, updated every 5 days
    # Can track:
    # - Construction progress
    # - Truck traffic patterns
    # - Storage yard inventory
    # - Production activity (heat signatures)
```

### 7.2 Google Earth Engine (Free for Research)

```python
import ee
ee.Initialize()

def analyze_supply_chain_infrastructure():
    # Historical imagery back to 1984
    # Can identify:
    # - Facility expansions
    # - New warehouses
    # - Transport infrastructure
    # - Environmental impacts
```

## 8. FINANCIAL INDICATORS

### 8.1 Credit and Payment Data

**Trade Credit Insurance Indicators:**
- Euler Hermes country risk (free summaries)
- Coface country/sector assessments (free)
- Atradius payment behavior reports (free)

**What They Reveal:**
- Payment delays indicate supply stress
- Credit limit reductions show risk
- Sector reports identify weak suppliers

### 8.2 Commodity Prices (Free)

```python
# Battery material prices indicate supply chain stress
commodity_sources = {
    'Lithium': 'https://tradingeconomics.com/commodity/lithium',
    'Cobalt': 'https://www.lme.com/en/metals/minor-metals/cobalt',
    'Nickel': 'https://www.lme.com/en/metals/non-ferrous/nickel',
    'Graphite': 'https://www.fastmarkets.com/commodities/industrial-minerals/graphite'
}

# Price spikes indicate:
# - Supply constraints
# - Supplier market power
# - Need for diversification
```

## 9. BUILDING A COMPLETE PICTURE

### 9.1 Combining Free Sources

```python
def build_supply_chain_map(company):
    supply_chain = {}
    
    # 1. Trade data - what's being imported
    trade_flows = get_un_comtrade_data(company_country)
    
    # 2. Shipping - how it's moving
    port_calls = scrape_port_data()
    
    # 3. Corporate - who's involved
    sustainability_reports = get_esg_reports(company)
    
    # 4. Patents - technology dependencies
    patent_network = analyze_patent_relationships(company)
    
    # 5. Personnel - LinkedIn connections
    employee_network = map_linkedin_relationships(company)
    
    # 6. Financial - credit and risk
    credit_indicators = get_credit_assessments()
    
    # 7. Satellite - physical verification
    facility_analysis = satellite_monitoring()
    
    return integrate_all_sources(supply_chain)
```

### 9.2 Key Indicators to Monitor

**For Battery Supply Chain Specifically:**

| Indicator | Source | What It Shows | Free? |
|-----------|--------|---------------|-------|
| Lithium carbonate imports | UN Comtrade | Raw material dependency | Yes |
| Chinese HS 8507 exports | China Customs | Battery cell sourcing | Yes |
| Port calls at Koper/Hamburg | Port websites | Logistics routes | Yes |
| Patent co-assignments | Lens.org | Technology dependencies | Yes |
| LinkedIn "former Gotion" | LinkedIn search | Personnel connections | Yes |
| Sustainability reports | Company websites | Disclosed suppliers | Yes |
| Satellite imagery | Sentinel Hub | Facility activity | Yes |
| Form SD filings | SEC EDGAR | Mineral sources | Yes |

## 10. PRACTICAL IMPLEMENTATION

### 10.1 Weekly Monitoring Routine (2 Hours)

**Monday: Trade Data Check**
- UN Comtrade monthly update
- China customs bulletin
- Port arrival schedules

**Wednesday: Corporate Intelligence**
- New sustainability reports
- Press releases
- LinkedIn changes

**Friday: Technical/Financial**
- Patent filings
- Commodity prices
- Credit indicators

### 10.2 Monthly Deep Dive (8 Hours)

1. Download latest trade data
2. Update shipping patterns
3. Analyze satellite imagery
4. Review regulatory filings
5. Map personnel movements
6. Generate supply chain report

### 10.3 Automation Opportunities

```python
# GitHub Actions for daily monitoring
# Free tier: 2,000 minutes/month

name: Supply Chain Monitor
on:
  schedule:
    - cron: '0 9 * * *'
    
jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Check trade data
        run: python check_trade_updates.py
      
      - name: Scrape port calls  
        run: python scrape_ports.py
      
      - name: Monitor news
        run: python news_monitor.py
      
      - name: Generate alert
        if: changes_detected
        run: python send_alert.py
```

## 11. LIMITATIONS AND WORKAROUNDS

### 11.1 What Free Sources Can't Provide

**Missing:**
- Real-time shipment tracking
- Detailed bills of lading
- Private company suppliers
- Tier 2/3 suppliers
- Pricing information
- Contract terms

### 11.2 Workarounds

**For Real-Time Tracking:**
- Combine multiple port websites
- Use vessel tracking for inference
- Monitor social media for disruptions

**For Private Companies:**
- Job postings often reveal suppliers
- Local news coverage
- Industry event attendee lists
- Patent collaborations

**For Deep Tier Visibility:**
- Sustainability reports sometimes include
- Conflict minerals reports (if applicable)
- Industry association member lists
- Technical standards participation

## 12. KEY INSIGHTS FOR SLOVAKIA ANALYSIS

### 12.1 Specific Free Sources for Gotion-InoBat

1. **Slovak Statistical Office** (statistics.sk)
   - Monthly trade with China
   - HS 8507 battery imports
   - Chemical imports (lithium, cobalt)

2. **Port of Koper** (luka-kp.si)
   - Main sea route for Slovakia
   - Vessel arrivals with cargo types
   - Container traffic statistics

3. **German Federal Statistics** (destatis.de)
   - Transit trade through Germany
   - Battery component flows

4. **Gotion Sustainability Reports**
   - Should list key suppliers
   - Environmental impact data
   - Supply chain policies

5. **Patent Analysis** (Lens.org)
   - Gotion-supplier co-patents
   - Technology dependencies
   - Licensed technologies

### 12.2 Red Flags to Monitor

**Supply Chain Concentration:**
- >50% single source for any component
- All logistics through one route
- Single technology dependency

**Financial Stress Indicators:**
- Trade credit insurance downgrades
- Commodity price spikes
- Payment delays in trade data

**Operational Indicators:**
- Satellite: Reduced activity at supplier
- Shipping: Route changes
- Personnel: Mass departures on LinkedIn

## BOTTOM LINE

**With free and low-cost sources, we can map 60-70% of Tier 1 supply chain and identify major dependencies**. The key is systematic collection and creative integration of multiple data sources. While we can't match the detail of paid services like Panjiva ($10,000+/year), we can identify critical vulnerabilities and concentration risks.

**Most Valuable Free Sources for Supply Chain:**
1. UN Comtrade (trade flows)
2. Port websites (shipping patterns)
3. Sustainability reports (supplier disclosure)
4. Patent databases (technology dependencies)
5. LinkedIn (personnel connections)

**Time Investment:** 10-15 hours initial setup, 2-3 hours weekly monitoring

---
**Key Finding**: Supply chain intelligence is possible without expensive subscriptions, but requires more manual effort and creative data integration.