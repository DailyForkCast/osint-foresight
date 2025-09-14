# OSINT Foresight Data Sources Analysis

## Status Overview

### ✅ Already Implemented (Have Pull Scripts)
1. **OpenAIRE** - Research publications & projects
2. **CrossRef** - Publications metadata & Event Data
3. **IETF Datatracker** - Standards participation
4. **GLEIF** - Legal Entity Identifiers
5. **CORDIS** - EU research projects
6. **Patents** (partial) - Google Patents via BigQuery

### ❌ Cannot Use (Requires Payment)
1. **OpenCorporates** - Company data (requires paid API key)

### 📋 To-Do List (Free Sources)

## Detailed Analysis of Remaining Sources

### 1. **OpenAlex**
- **Cost**: FREE
- **Size**: ~300GB compressed
- **CLI**: AWS CLI (no account needed)
- **Automation**: Fully automated via AWS S3 sync
- **Command**: `aws s3 sync "s3://openalex" "F:/openalex" --no-sign-request`
- **Priority**: HIGH - Comprehensive bibliometric data
- **Status**: Planned for F: drive

### 2. **TED (Tenders Electronic Daily)**
- **Cost**: FREE
- **API**: YES - TED API v3
- **Documentation**: https://ted.europa.eu/en/api
- **CLI**: Can build with requests
- **Automation**: Fully automated
- **Data**: EU public procurement notices
- **Priority**: HIGH - Supply chain intelligence
```python
# Example API call
https://ted.europa.eu/api/v3/notices/search?q=country:AT&pageSize=100
```

### 3. **UN Comtrade**
- **Cost**: FREE (with limits)
- **API**: YES - REST API
- **Documentation**: https://comtradeapi.un.org/
- **CLI**: Python comtradeapicall package
- **Automation**: Fully automated
- **Limits**: 100 requests/hour for free tier
- **Data**: International trade flows by HS codes
- **Priority**: HIGH - Supply chain analysis
```bash
pip install comtradeapicall
```

### 4. **ITC Trade Map**
- **Cost**: LIMITED FREE (requires registration)
- **API**: NO - Web interface only
- **CLI**: No
- **Automation**: Manual export only
- **Alternative**: Use UN Comtrade instead
- **Priority**: LOW - Redundant with Comtrade

### 5. **World Bank Data**
- **Cost**: FREE
- **API**: YES - World Bank API
- **Documentation**: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- **CLI**: wbgapi Python package
- **Automation**: Fully automated
- **Priority**: MEDIUM - Economic indicators
```bash
pip install wbgapi
```

### 6. **WIPO Global Brand Database**
- **Cost**: FREE
- **API**: NO - Web interface
- **CLI**: No
- **Automation**: Manual search only
- **Data**: Trademarks, designs
- **Priority**: LOW - Manual process

### 7. **EPO PATSTAT**
- **Cost**: FREE for online queries
- **API**: OPS API (limited)
- **CLI**: Can build with epo-ops Python package
- **Automation**: Semi-automated (rate limits)
- **Priority**: MEDIUM - Patent analysis
```bash
pip install python-epo-ops-client
```

### 8. **National Procurement Portals**
- **Austria**: https://www.data.gv.at/
- **Portugal**: https://www.base.gov.pt/
- **Ireland**: https://www.etenders.gov.ie/
- **Slovakia**: https://www.uvo.gov.sk/
- **Cost**: FREE
- **API**: Varies by country
- **Automation**: Semi-automated (scrapers needed)
- **Priority**: HIGH - National supply chain

### 9. **EU Open Data Portal**
- **Cost**: FREE
- **URL**: https://data.europa.eu/
- **API**: YES - SPARQL endpoint
- **CLI**: Can query programmatically
- **Automation**: Fully automated
- **Priority**: MEDIUM

### 10. **ESA Business Applications**
- **Cost**: FREE
- **API**: NO - Manual search
- **URL**: https://business.esa.int/
- **Automation**: Manual only
- **Priority**: LOW - Specific to space sector

### 11. **EuroHPC JU Projects**
- **Cost**: FREE
- **API**: NO - Website only
- **URL**: https://eurohpc-ju.europa.eu/
- **Automation**: Web scraping possible
- **Priority**: LOW - Limited data

### 12. **National Accreditation Bodies**
- **Cost**: FREE
- **API**: NO - Manual search
- **Examples**: UKAS (UK), DAkkS (DE), IPAC (PT)
- **Automation**: Web scraping needed
- **Priority**: MEDIUM - Lab certifications

## Supply Chain Specific Sources

### Primary (Implement First)
1. **UN Comtrade** - Trade flows by product/country
2. **TED API** - EU procurement data
3. **National procurement portals** - Country-specific tenders

### Secondary
4. **Port/shipping data** (MarineTraffic, FlightRadar24 - limited free)
5. **Customs data** - Usually not freely available
6. **Supply chain databases** - Mostly commercial (Panjiva, ImportGenius)

## Implementation Priority

### Phase 1: High-Value Automated Sources
```bash
# 1. TED API - EU Procurement
python -m src.pulls.ted_pull --country AT --years 2020-2025

# 2. UN Comtrade - Trade flows
python -m src.pulls.comtrade_pull --country AT --products "84,85,90"

# 3. World Bank - Economic indicators
python -m src.pulls.worldbank_pull --country AT --indicators "NY.GDP.MKTP.CD"
```

### Phase 2: Large Dataset Downloads
```bash
# OpenAlex on F: drive
aws s3 sync "s3://openalex" "F:/OSINT_Backups/openalex" --no-sign-request
```

### Phase 3: Semi-Automated Sources
- National procurement (build scrapers)
- EPO patents (use epo-ops client)
- Accreditation bodies (web scraping)

### Phase 4: Manual Sources (Low Priority)
- ITC Trade Map (if needed beyond Comtrade)
- WIPO Global Brand Database
- ESA/EuroHPC project lists

## Next Steps

1. **Create pull scripts for**:
   - TED API (`src/pulls/ted_pull.py`)
   - UN Comtrade (`src/pulls/comtrade_pull.py`)
   - World Bank (`src/pulls/worldbank_pull.py`)

2. **Set up F: drive for OpenAlex**:
   - Install AWS CLI
   - Schedule weekend download

3. **Build scrapers for**:
   - National procurement portals
   - Accreditation body databases

## Cost Summary

**Total cost for all sources**: $0 (all free)
**Storage needed**:
- OpenAlex: 300GB
- Other sources: <10GB total
**Rate limits**:
- UN Comtrade: 100/hour
- TED: Reasonable use
- World Bank: 120 requests/minute

## Automation Capability

- **Fully Automated** (70%): OpenAlex, TED, Comtrade, World Bank, CORDIS, CrossRef, IETF, GLEIF
- **Semi-Automated** (20%): EPO patents, national procurement
- **Manual Only** (10%): WIPO brands, ITC Trade Map, accreditation bodies

---
*Last updated: September 2025*
