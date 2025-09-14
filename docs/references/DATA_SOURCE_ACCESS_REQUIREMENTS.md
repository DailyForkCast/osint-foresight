# Data Source Access Requirements

## Overview
This document details which data sources require registration, API keys, or paid subscriptions.

---

## 🟢 Completely Free (No Registration)

### Research & Publications
- **OpenAlex API** - https://api.openalex.org/
  - No API key needed
  - Rate limit: 100,000 requests/day
  - Polite pool: max 10 requests/second

- **CrossRef API** - https://api.crossref.org/
  - No API key needed
  - Polite pool: Include email in User-Agent
  - Rate limit: 50/second with email

- **CrossRef Event Data** - https://api.eventdata.crossref.org/
  - No registration required
  - Free for all users

- **arXiv API** - https://arxiv.org/help/api/
  - No registration needed
  - Rate limit: 3 requests/second

### Economic & Trade Data
- **World Bank API** - https://api.worldbank.org/v2/
  - No registration required
  - Rate limit: 120 requests/minute

- **OECD Data API** - https://data.oecd.org/
  - No registration for API
  - Free access to all datasets

- **Eurostat API** - https://ec.europa.eu/eurostat/
  - No registration needed
  - Bulk download available

### Other Sources
- **Wikidata SPARQL** - https://query.wikidata.org/
  - No registration
  - Rate limits apply

---

## 🟡 Free with Registration

### Research & Standards
- **IETF Datatracker** - https://datatracker.ietf.org/api/v1/
  - Optional registration for higher limits
  - Free tier: 100 requests/hour
  - Registered: 5000 requests/hour

- **Europe PMC** - https://www.ebi.ac.uk/europepmc/
  - Registration recommended
  - Higher rate limits with account

- **ORCID API** - https://orcid.org/
  - Public API requires registration
  - Free client ID needed
  - Rate limit: 24 requests/second

### Patents
- **EPO OPS** - https://developers.epo.org/
  - **Registration Required**: Yes (free)
  - Consumer key & secret needed
  - Rate limit: 20GB/month free
  - Setup: Register at developers.epo.org

- **USPTO PatentsView** - https://patentsview.org/apis/
  - API key required (free)
  - Register at their portal
  - Rate limit: 45 requests/minute

### EU Data
- **CORDIS** - https://cordis.europa.eu/
  - No API registration needed
  - Bulk downloads require account
  - Free EU Login account

- **EU Open Data Portal** - https://data.europa.eu/
  - Some datasets need EU Login
  - API access free

### Company Data
- **GLEIF API** - https://www.gleif.org/
  - Registration optional
  - Higher limits with account
  - Free tier sufficient for most uses

---

## 🔴 Paid or Limited Free Tier

### Trade Data
- **UN Comtrade** - https://comtradeplus.un.org/
  - **Free Tier**: 100 requests/hour
  - **Subscription**: Required for bulk/unlimited
  - Pricing: $99/month for premium
  - Register at: https://comtradedeveloper.un.org/

- **ITC Trade Map** - https://www.trademap.org/
  - Free registration required
  - Limited downloads per month
  - Premium subscription for bulk data

### Company Information
- **OpenCorporates** - https://opencorporates.com/
  - **Status**: PAID ONLY for API
  - Free web search only
  - API pricing: Starting $399/month
  - **Decision**: EXCLUDED from project

### Patents & IP
- **PATSTAT** - https://www.epo.org/searching-for-patents/business/patstat
  - Online access: Free with registration
  - Bulk data: Expensive subscription
  - Alternative: Use EPO OPS instead

### Procurement
- **TED API** - https://ted.europa.eu/api/
  - Complex authentication required
  - Free but needs proper setup
  - Alternative: Manual download

---

## 🔵 Special Requirements

### Large Downloads
- **OpenAlex Snapshot** - https://openalex.org/data
  - **Size**: 300GB compressed
  - **Method**: AWS S3 sync (no AWS account needed)
  - **Command**: `aws s3 sync s3://openalex F:/openalex --no-sign-request`

- **Common Crawl** - https://commoncrawl.org/
  - Petabytes of data
  - AWS S3 access
  - Usually need EC2 for processing

### Authentication Methods

#### API Key in Header
```python
headers = {'X-API-Key': 'your-key-here'}
```
- UN Comtrade
- EPO OPS
- USPTO

#### OAuth 2.0
```python
# EPO OPS example
token = get_oauth_token(client_id, client_secret)
headers = {'Authorization': f'Bearer {token}'}
```
- EPO OPS
- Some EU services

#### Basic Authentication
```python
auth = ('username', 'password')
```
- Some academic databases

#### Email in User-Agent
```python
headers = {'User-Agent': 'ProjectName (email@example.com)'}
```
- CrossRef (for polite pool)
- PubMed

---

## Setup Priority

### 1. Immediate (No Action Needed)
- ✅ OpenAlex API
- ✅ CrossRef API
- ✅ World Bank API
- ✅ Eurostat
- ✅ OECD Data

### 2. Quick Registration (5 minutes)
- ⏳ EPO OPS - Patent data
- ⏳ ORCID - Researcher data
- ⏳ EU Login - CORDIS bulk
- ⏳ IETF account - Higher limits

### 3. Evaluate Need
- ❓ UN Comtrade subscription ($99/month)
- ❓ ITC Trade Map premium
- ❓ USPTO PatentsView API key

### 4. Excluded (Too Expensive)
- ❌ OpenCorporates API ($399+/month)
- ❌ PATSTAT bulk data
- ❌ Commercial trade databases

---

## Environment Variables Needed

Create `.env` file:
```bash
# Free with registration
EPO_OPS_KEY=your_key_here
EPO_OPS_SECRET=your_secret_here
ORCID_CLIENT_ID=your_id_here
ORCID_CLIENT_SECRET=your_secret_here

# Optional paid
COMTRADE_SUBSCRIPTION_KEY=your_key_if_purchased

# For polite crawling
CONTACT_EMAIL=your_email@example.com
PROJECT_NAME=OSINT_Foresight

# Google Cloud (already set up)
GCP_PROJECT=osint-foresight-2025
```

---

## Cost Summary

### Current Monthly Cost: $0
- All essential sources available free
- Optional subscriptions not required

### Potential Future Costs
- UN Comtrade Premium: $99/month (optional)
- Cloud storage: ~$10/month for 500GB
- External drive: $50-100 one-time

### Excluded Due to Cost
- OpenCorporates: $399+/month
- PATSTAT bulk: €1000+/year
- Commercial databases: $1000+/month

---

*Last updated: September 2025*
*Recommendation: Register for free EPO OPS and ORCID accounts first*
