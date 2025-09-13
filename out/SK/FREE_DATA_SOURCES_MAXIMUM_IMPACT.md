# Maximum Impact with Zero-Budget Data Sources
**How to dramatically improve analysis using only free resources**
**Date: September 10, 2025**

## 1. HIGHEST IMPACT FREE SOURCES

### 1.1 Patent Intelligence (Completely Free)

**Google Patents with BigQuery**
- **What**: 130+ million patents, full text searchable
- **How**: Use BigQuery public dataset (1TB free/month)
- **Impact**: Complete technology transfer mapping
```sql
-- Example query for Slovak-Chinese co-inventions
SELECT * FROM `patents-public-data.patents.publications`
WHERE country_code = 'SK' 
AND inventor_harmonized LIKE '%China%'
```

**Lens.org**
- **What**: 127+ million patents, analytical tools included
- **How**: Free account, API access available
- **Impact**: Citation networks, technology evolution, ownership changes
- **Bonus**: Scholarly articles linked to patents

**Espacenet**
- **What**: 140+ million patents
- **How**: Advanced search, legal status, INPADOC families
- **Impact**: Complete European coverage, machine translations

### 1.2 Corporate and Ownership Data

**OpenCorporates**
- **What**: 200+ million companies globally
- **How**: API with free tier (500 calls/month)
- **Impact**: Ownership chains, director networks, corporate history

**National Business Registries (Free)**
- **Slovakia**: orsr.sk, finstat.sk (basic data)
- **UK**: Companies House (extensive free data)
- **US**: SEC EDGAR (all public company filings)
- **EU**: Business Registers Interconnection System (BRIS)
- **China**: National Enterprise Credit Information (basic)

**LEI Database (GLEIF)**
- **What**: Legal Entity Identifiers with ownership
- **How**: Bulk download entire database
- **Impact**: Parent-subsidiary relationships globally

### 1.3 Academic and Research

**CORE**
- **What**: 250+ million open access papers
- **How**: API access, bulk download
- **Impact**: Complete academic collaboration mapping

**PubMed Central**
- **What**: 8+ million biomedical articles
- **How**: API, bulk download
- **Impact**: Life sciences/battery chemistry research

**arXiv**
- **What**: 2+ million preprints
- **How**: Bulk download, API
- **Impact**: Early technology indicators

**SSRN**
- **What**: 1+ million social science papers
- **How**: Free access, RSS feeds
- **Impact**: Policy and economic research

**OpenAlex (formerly Microsoft Academic)**
- **What**: 250+ million papers with metadata
- **How**: Complete database downloadable
- **Impact**: Citation networks, collaboration patterns

### 1.4 EU Funding and Projects

**CORDIS**
- **What**: All EU-funded research projects
- **How**: Bulk download in JSON/CSV
- **Impact**: Complete funding flows, partner networks
```python
# Download all H2020 projects
import requests
import json

url = "https://cordis.europa.eu/data/cordis-h2020-projects.json"
data = requests.get(url).json()
# Parse for Slovak-Chinese collaborations
```

**EU Open Data Portal**
- **What**: 1+ million datasets
- **How**: API, bulk download
- **Impact**: Economic, trade, regulatory data

**TED (Tenders Electronic Daily)**
- **What**: All EU public procurement
- **How**: Bulk download, API
- **Impact**: Government contracts, supplier relationships

### 1.5 Trade and Customs Data

**UN Comtrade**
- **What**: Global trade statistics
- **How**: API with free tier, bulk download
- **Impact**: Trade flows, dependencies

**ITC Trade Map** (limited free)
- **What**: Trade statistics by product
- **How**: Free registration, monthly limits
- **Impact**: Detailed product-level trade

**National Statistics Offices**
- **Slovakia**: statistics.sk (full data)
- **China**: stats.gov.cn (English version)
- **EU**: Eurostat (complete database)

## 2. POWERFUL FREE TOOLS FOR ANALYSIS

### 2.1 Network Analysis

**Gephi**
- **What**: Network visualization and analysis
- **How**: Open source, runs locally
- **Use**: Map collaboration networks, ownership structures

**Cytoscape**
- **What**: Complex network analysis
- **How**: Open source, extensive plugins
- **Use**: Analyze patent citations, research networks

**NetworkX (Python)**
```python
import networkx as nx
# Build collaboration network
G = nx.Graph()
G.add_edge("Slovak_Uni", "Chinese_Uni", weight=5)
# Analyze centrality, clusters
```

### 2.2 Data Collection and Processing

**BeautifulSoup + Requests (Python)**
```python
# Scrape public registries
import requests
from bs4 import BeautifulSoup

url = "https://orsr.sk/search"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
```

**Scrapy Framework**
- **What**: Industrial-strength web scraping
- **How**: Open source Python framework
- **Use**: Systematic data collection from multiple sources

**OpenRefine**
- **What**: Data cleaning and reconciliation
- **How**: Open source, GUI interface
- **Use**: Clean messy data, entity reconciliation

### 2.3 OSINT Tools

**Maltego Community Edition**
- **What**: Link analysis and data mining
- **How**: Free version with limitations
- **Use**: Entity relationship mapping

**TheHarvester**
```bash
# Gather emails, subdomains, IPs
theHarvester -d company.com -b all
```

**Shodan (limited free)**
- **What**: Internet-connected devices
- **How**: Free account, 100 results/month
- **Use**: Find exposed systems, verify infrastructure

**Recon-ng**
- **What**: Web reconnaissance framework
- **How**: Open source, modular
- **Use**: Systematic OSINT collection

## 3. MAXIMIZING FREE GOVERNMENT SOURCES

### 3.1 US Government Resources

**USPTO**
- Complete US patent database
- Patent assignment (ownership changes)
- Trademark database

**SEC EDGAR**
- All public company filings
- Ownership reports (13D, 13F)
- Material agreements

**FOIA Reading Rooms**
- CIA FOIA (crest.ciadocuments.gov)
- State Department FOIA
- DOD FOIA

**Export.gov Data**
- Export control lists
- Country commercial guides
- Market research

### 3.2 EU Resources

**EU Sanctions Map**
- Interactive sanctions database
- Free API access
- Historical data

**European Court of Justice**
- All EU court decisions
- Competition/state aid cases
- Search API available

**European Patent Register**
- Legal status of patents
- Opposition proceedings
- Licensing information

### 3.3 Chinese Sources (English Accessible)

**CNIPA English**
- Chinese patent database (English interface)
- Limited but useful

**Ministry of Commerce (MOFCOM)**
- Investment catalogs
- FDI statistics
- Policy documents

**China Judgments Online**
- Court decisions (some in English)
- IP disputes
- Commercial cases

## 4. FREE ALTERNATIVES TO PAID SERVICES

### 4.1 Instead of Bloomberg Terminal

**Combination of:**
- Yahoo Finance API (real-time quotes)
- SEC EDGAR (filings)
- Google Finance (historical data)
- TradingView (free charts)
- Seeking Alpha (free articles)

### 4.2 Instead of Factiva

**Combination of:**
- Google News Archive
- Internet Archive newspapers
- GDELT Project (news database)
- MediaCloud (media analysis)
- AllSides (media bias checking)

### 4.3 Instead of Patent Analytics Platforms

**Build your own with:**
- Google Patents BigQuery
- Lens.org API
- Python libraries (pandas, networkx)
- Jupyter notebooks
- GitHub for collaboration

### 4.4 Instead of Supply Chain Databases

**Piece together from:**
- Port authority websites
- Shipping line schedules
- Company sustainability reports
- Industry association data
- Government trade statistics

## 5. CRITICAL FREE SOURCES FOR SLOVAKIA ANALYSIS

### 5.1 Slovak-Specific

**Register účtovných závierok**
- **What**: All Slovak company financial statements
- **URL**: registeruz.sk
- **Impact**: Complete financials for InoBat, others

**Centrálny register zmlúv**
- **What**: All Slovak government contracts
- **URL**: crz.gov.sk
- **Impact**: State aid agreements, subsidies

**Vestník verejného obstarávania**
- **What**: Public procurement bulletin
- **URL**: uvo.gov.sk
- **Impact**: Government contracts

### 5.2 Battery Industry Specific

**DOE Battery500 Consortium**
- Technical reports
- Performance benchmarks
- Roadmaps

**Argonne National Lab**
- Battery cost models
- Supply chain reports
- Technical publications

**IEA Data**
- Energy statistics
- EV sales data
- Battery demand projections

### 5.3 Security and Dual-Use

**Wassenaar Arrangement**
- Dual-use control lists
- Participating state reports

**Nuclear Suppliers Group**
- Control lists
- Public statements

**SIPRI Databases**
- Arms trade
- Military expenditure
- Sanctions

## 6. DATA COLLECTION STRATEGY

### 6.1 Systematic Approach

**Week 1: Corporate Baseline**
```python
# Pseudocode for systematic collection
for company in ['Gotion', 'InoBat', 'Others']:
    check_opencorporates()
    check_national_registry()
    check_lei_database()
    download_financial_statements()
    map_subsidiaries()
```

**Week 2: Patent Landscape**
```python
# Build patent database
patents = []
for database in ['Google Patents', 'Lens', 'Espacenet']:
    results = search(assignee='Slovak OR Chinese')
    patents.extend(results)
analyze_coinventions(patents)
```

**Week 3: Academic Networks**
```python
# Map collaborations
papers = query_openalex(affiliation='Slovakia')
chinese_collabs = filter(papers, coauthor_country='China')
build_network_graph(chinese_collabs)
```

**Week 4: Trade Flows**
```python
# Analyze trade dependencies
trade_data = un_comtrade_api(reporter='Slovakia', partner='China')
identify_critical_products(trade_data)
```

## 7. AUTOMATION FOR CONTINUOUS MONITORING

### 7.1 Free Monitoring Tools

**Google Alerts**
- Set up for all key entities
- News monitoring
- Patent publications

**IFTTT (If This Then That)**
- Connect multiple services
- Automated workflows
- RSS to spreadsheet

**Huginn**
- Open source automation
- Complex workflows
- Self-hosted

**GitHub Actions**
```yaml
# Daily data collection
name: Daily OSINT Collection
on:
  schedule:
    - cron: '0 9 * * *'
jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - run: python collect_data.py
      - run: python analyze_changes.py
```

### 7.2 Change Detection

**Visualping**
- Free tier (65 checks/month)
- Website change monitoring
- Email alerts

**Distill Web Monitor**
- Browser extension
- Local monitoring
- Cloud sync (paid)

**WatchTower**
- Open source
- Self-hosted
- API monitoring

## 8. COLLABORATION AND KNOWLEDGE MANAGEMENT

### 8.1 Free Platforms

**GitHub**
- Version control for data
- Collaboration on analysis
- Jupyter notebooks
- GitHub Pages for reports

**GitLab**
- Similar to GitHub
- Better CI/CD in free tier
- Self-hostable

**Obsidian**
- Knowledge graph
- Markdown-based
- Link analysis
- Free for personal use

### 8.2 Data Sharing

**Zenodo**
- Academic data repository
- DOI assignment
- 50GB free storage

**Kaggle**
- Dataset hosting
- Collaborative analysis
- Free compute resources

**HuggingFace**
- Dataset hosting
- Model sharing
- Collaboration tools

## 9. MAXIMUM IMPACT PRIORITIES

### 9.1 If You Do Nothing Else (Top 5)

1. **Set up Lens.org saved searches** for Slovak-Chinese patents
2. **Download CORDIS data** and analyze all Slovak-Chinese projects
3. **Monitor finstat.sk** for Slovak company changes
4. **Use OpenCorporates API** to map ownership networks
5. **Create Google Alerts** for all key entities

### 9.2 Next Level (Additional 5)

6. **Build patent citation network** using Google Patents BigQuery
7. **Analyze trade flows** with UN Comtrade
8. **Map academic collaborations** using OpenAlex
9. **Set up GitHub Actions** for automated monitoring
10. **Create Gephi visualizations** of relationship networks

### 9.3 Advanced (If Time Permits)

11. Build custom scrapers for Chinese sources
12. Develop predictive models using historical data
13. Create automated report generation
14. Establish crowdsourced intelligence network
15. Develop custom analytics dashboards

## 10. REALISTIC IMPROVEMENTS ACHIEVABLE

### 10.1 What We Can Achieve with Free Sources

**Accuracy Improvements:**
- Verify ownership to ±5% (vs ±20% now)
- Track actual patent filings (vs estimates)
- Monitor real financial performance (vs assumptions)
- Document actual trade flows (vs guesses)

**Detail Improvements:**
- Complete patent landscape mapping
- Full academic collaboration network
- Detailed ownership structures
- Comprehensive EU funding analysis

**Nuance Improvements:**
- Multiple source verification
- Historical trend analysis
- Comparative peer analysis
- Stakeholder network mapping

### 10.2 Limitations of Free Sources

**What We Still Won't Have:**
- Real-time market data (delayed 15-20 minutes)
- Paywall academic papers (only open access)
- Private company details (only public info)
- Expert interviews (unless volunteered)
- Satellite imagery (only low-resolution)

**Mitigation Strategies:**
- Use multiple sources for verification
- Focus on trends vs point-in-time data
- Leverage government filings
- Build relationships for voluntary info
- Use free satellite sources creatively

## 11. IMPLEMENTATION ROADMAP

### 11.1 Week 1: Foundation

- Set up all free accounts
- Download bulk datasets
- Configure monitoring alerts
- Install analysis tools

### 11.2 Month 1: Collection

- Systematic data gathering
- Build initial databases
- Create network maps
- Establish baselines

### 11.3 Month 2-3: Analysis

- Deep dive analysis
- Pattern identification
- Relationship mapping
- Report generation

### 11.4 Ongoing: Monitoring

- Daily alert reviews
- Weekly data updates
- Monthly trend analysis
- Quarterly deep reviews

## 12. KEY INSIGHT

**The Gap Between Free and Paid is Smaller Than Ever**

With systematic use of free sources, we can achieve 70-80% of the intelligence value of paid services. The key is:
- **Automation** to handle volume
- **Integration** of multiple sources
- **Persistence** in collection
- **Creativity** in analysis

The main trade-off is time vs money. Free sources require more effort to collect and clean, but the raw intelligence value is largely accessible.

---
**Bottom Line**: Zero budget doesn't mean zero intelligence. With the right approach, free sources can provide professional-grade analysis. The key is systematic collection, creative integration, and persistent monitoring.