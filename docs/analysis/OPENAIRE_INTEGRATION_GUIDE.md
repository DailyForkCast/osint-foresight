# OpenAIRE Integration Guide for OSINT System

**Date:** September 18, 2025
**Purpose:** Integration guide for connecting OpenAIRE research data to OSINT analysis system
**Status:** Active API endpoints confirmed working

---

## EXECUTIVE SUMMARY

OpenAIRE provides comprehensive access to European research data through their Graph API, covering **7.2+ million Italian research outputs** and extensive international collaboration data. The API is free, requires no authentication for basic usage, and offers both real-time search and bulk download capabilities.

**Key Numbers:**
- Total IT research products: **7,277,853**
- Total research products globally: **~267 million** (193M publications, 73.5M datasets, ~600K software)
- Data sources: **2,000+**
- Coverage: All EU research outputs plus global collaboration data

---

## 1. API OVERVIEW

### Base URLs
```
Search API (Legacy): https://api.openaire.eu/search/
Graph API (New): https://api.openaire.eu/graph/
```

### Authentication
- **No authentication required** for basic usage
- **No API keys needed** for standard queries
- Rate limits apply but not publicly documented

### Data Coverage
- **Publications:** Journal articles, conference papers, preprints
- **Research Data:** Datasets, protocols, research workflows
- **Software:** Research software, tools, libraries
- **Projects:** EU-funded research projects (H2020, FP7, etc.)
- **Organizations:** Universities, research institutes, companies

---

## 2. CONFIRMED API ENDPOINTS

### Research Products Search
```
GET https://api.openaire.eu/search/researchProducts
```

**Available Parameters:**
- `country` - Two-letter country code (IT, DE, FR, etc.)
- `title` - Search in publication titles
- `author` - Author search
- `keywords` - Keyword search
- `funder` - Funding organization
- `projectID` - Project identifier
- `openaireProjectID` - OpenAIRE project ID
- `doi` - Digital Object Identifier
- `orcid` - ORCID author identifier
- `community` - Research community
- `instancetype` - Type of instance
- `OA` - Open Access filter
- `fromDateAccepted` / `toDateAccepted` - Date range
- `size` - Results per page (default: 10, max: 50)
- `page` - Page number
- `format` - Response format (json, xml)
- `sortBy` - Sort criteria

### Projects Search
```
GET https://api.openaire.eu/search/projects
```

### Organizations Search
```
GET https://api.openaire.eu/search/organizations
```

---

## 3. DATA STRUCTURE

### Sample Response Structure
```json
{
  "response": {
    "header": {
      "query": {"$": "(oaftype exact result) and (country exact \"IT\")"},
      "total": {"$": 7277853},
      "size": {"$": 1},
      "page": {"$": 1}
    },
    "results": {
      "result": [{
        "metadata": {
          "oaf:entity": {
            "oaf:result": {
              "title": {"$": "Research Title"},
              "creator": [
                {"@name": "First", "@surname": "Author", "$": "Author, First"}
              ],
              "dateofacceptance": {"$": "2024-01-01"},
              "description": {"$": "Research description"},
              "publisher": {"$": "Publisher Name"},
              "resulttype": {"@classid": "publication"},
              "pid": [
                {"@classid": "doi", "$": "10.1000/example"}
              ],
              "rels": {
                "rel": [{
                  "to": {"@type": "organization"},
                  "country": {"@classid": "IT", "@classname": "Italy"},
                  "legalname": {"$": "University Name"}
                }]
              }
            }
          }
        }
      }]
    }
  }
}
```

### Key Data Fields
- **Identifiers:** DOI, ORCID, Handle, OpenAIRE ID
- **Bibliographic:** Title, authors, publisher, date
- **Classification:** Result type, instance type, access rights
- **Relationships:** Author affiliations, project links, citations
- **Metrics:** Influence score, popularity, citation count

---

## 4. INTEGRATION FOR OSINT ANALYSIS

### Country-Specific Research Mapping

#### Query Pattern for Target Country
```bash
# Get all research products from target country
curl "https://api.openaire.eu/search/researchProducts?country={COUNTRY_CODE}&size=50&format=json"

# Examples:
# Italy: country=IT
# Germany: country=DE
# Slovakia: country=SK
# China: country=CN
```

#### Technology Area Filtering
```bash
# Combine with keyword searches
curl "https://api.openaire.eu/search/researchProducts?country=IT&keywords=artificial%20intelligence&size=50"

# Or title-based filtering
curl "https://api.openaire.eu/search/researchProducts?country=IT&title=quantum&size=50"
```

### International Collaboration Detection

#### Multi-Country Projects
```bash
# Search for EU projects with specific country participation
curl "https://api.openaire.eu/search/projects?funder=EC&country=IT&size=50"
```

#### Cross-Border Research
- Parse `rels.rel` sections for organization affiliations
- Extract `country` attributes from relationship data
- Identify co-authorship patterns across countries

### Technology Transfer Indicators

#### Research-to-Industry Pipeline
- Track publications from universities
- Monitor spin-off company formations
- Identify patent citations to research papers

#### Funding Source Analysis
```bash
# Search by specific funders
curl "https://api.openaire.eu/search/researchProducts?funder=European%20Commission&country=IT"

# Date-based trend analysis
curl "https://api.openaire.eu/search/researchProducts?country=IT&fromDateAccepted=2020-01-01&toDateAccepted=2024-12-31"
```

---

## 5. PYTHON INTEGRATION CODE

### Basic Client Implementation
```python
import requests
import pandas as pd
import json
from typing import Dict, List, Optional
import time

class OpenAIREClient:
    def __init__(self):
        self.base_url = "https://api.openaire.eu/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINT-Research-System/1.0',
            'Accept': 'application/json'
        })

    def search_research_products(self,
                               country: str = None,
                               keywords: str = None,
                               author: str = None,
                               funder: str = None,
                               from_date: str = None,
                               to_date: str = None,
                               size: int = 50,
                               page: int = 1) -> Dict:
        """Search research products with filters"""

        params = {
            'format': 'json',
            'size': min(size, 50),  # Max 50 per request
            'page': page
        }

        if country:
            params['country'] = country
        if keywords:
            params['keywords'] = keywords
        if author:
            params['author'] = author
        if funder:
            params['funder'] = funder
        if from_date:
            params['fromDateAccepted'] = from_date
        if to_date:
            params['toDateAccepted'] = to_date

        url = f"{self.base_url}/researchProducts"

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return {}

    def get_all_country_research(self, country: str, max_results: int = 1000) -> List[Dict]:
        """Get comprehensive research data for a country"""
        all_results = []
        page = 1
        size = 50

        while len(all_results) < max_results:
            print(f"Fetching page {page} for {country}...")

            data = self.search_research_products(
                country=country,
                size=size,
                page=page
            )

            if not data.get('response', {}).get('results', {}).get('result'):
                break

            results = data['response']['results']['result']
            all_results.extend(results)

            total = int(data['response']['header']['total']['$'])
            if len(all_results) >= total:
                break

            page += 1
            time.sleep(0.5)  # Be respectful to API

        return all_results[:max_results]

    def extract_collaborations(self, research_data: List[Dict]) -> pd.DataFrame:
        """Extract international collaboration data"""
        collaborations = []

        for item in research_data:
            try:
                result = item['metadata']['oaf:entity']['oaf:result']

                # Extract basic info
                title = result.get('title', {}).get('$', '')
                date = result.get('dateofacceptance', {}).get('$', '')

                # Extract organization relationships
                if 'rels' in result and 'rel' in result['rels']:
                    rels = result['rels']['rel']
                    if not isinstance(rels, list):
                        rels = [rels]

                    for rel in rels:
                        if rel.get('to', {}).get('@type') == 'organization':
                            country = rel.get('country', {}).get('@classid', '')
                            org_name = rel.get('legalname', {}).get('$', '')

                            collaborations.append({
                                'title': title,
                                'date': date,
                                'partner_country': country,
                                'partner_organization': org_name
                            })
            except Exception as e:
                continue

        return pd.DataFrame(collaborations)

# Usage Example
client = OpenAIREClient()

# Get Italian research data
italy_research = client.get_all_country_research('IT', max_results=500)

# Extract collaboration patterns
collaborations = client.extract_collaborations(italy_research)

# Analyze China-Italy collaborations
china_italy = collaborations[collaborations['partner_country'] == 'CN']
print(f"Found {len(china_italy)} China-Italy research collaborations")
```

---

## 6. BULK DATA ACCESS

### Alternative: Full Dataset Download

For comprehensive analysis, OpenAIRE offers **full graph downloads**:

```bash
# Download complete OpenAIRE Graph (largest scholarly knowledge graph)
# Available formats: JSON, Parquet
# Size: Several TB of compressed data
```

### Recommended Approach for Large-Scale Analysis
1. **API for Discovery:** Use Search API to identify relevant subsets
2. **Bulk Download:** Get full dataset for comprehensive analysis
3. **Local Processing:** Build custom indices for your specific use cases

---

## 7. DATA QUALITY CONSIDERATIONS

### Strengths
- **Comprehensive Coverage:** All EU research outputs
- **Real-time Updates:** Data refreshed regularly
- **Rich Metadata:** Detailed bibliographic and relationship data
- **Standardized Format:** Consistent data structure across sources

### Limitations
- **Deduplication Complexity:** Same research may appear multiple times
- **Affiliation Accuracy:** Organization matching can be inconsistent
- **Language Coverage:** Primarily English and European languages
- **Commercial Research:** Limited coverage of private sector R&D

### Data Validation Required
- Cross-reference organization names with authoritative sources
- Validate country assignments for multinational organizations
- Check for duplicate detection across different identifiers
- Verify funding information with original sources

---

## 8. OSINT INTEGRATION OPPORTUNITIES

### Cross-Reference with Other Sources

| OpenAIRE Data | Cross-Reference | Intelligence Value |
|---------------|-----------------|-------------------|
| Author ORCID | LinkedIn/Academic profiles | Current affiliations |
| Organization IDs | Corporate registries | Ownership structures |
| Project funding | Government databases | Policy priorities |
| DOIs | Patent citations | Research commercialization |
| Publication dates | TED procurement | Technology adoption timing |

### Automated Monitoring Setup

```python
# Weekly monitoring script
def monitor_new_research(countries: List[str], keywords: List[str]):
    client = OpenAIREClient()

    # Check last week's publications
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    for country in countries:
        for keyword in keywords:
            results = client.search_research_products(
                country=country,
                keywords=keyword,
                from_date=from_date
            )

            # Process and alert on significant findings
            analyze_results(results, country, keyword)
```

---

## 9. INTEGRATION TIMELINE

### Phase 1: Basic Integration (Week 1)
- [ ] Implement OpenAIRE client
- [ ] Test API connectivity and parameters
- [ ] Extract sample data for target countries
- [ ] Validate data structure and quality

### Phase 2: Data Pipeline (Week 2-3)
- [ ] Build automated collection workflows
- [ ] Implement collaboration detection algorithms
- [ ] Create data validation and cleaning processes
- [ ] Establish local data storage and indexing

### Phase 3: Analysis Integration (Week 4)
- [ ] Connect to existing OSINT pipeline
- [ ] Cross-reference with USPTO, TED, and other sources
- [ ] Implement trend analysis and alerting
- [ ] Create visualization and reporting capabilities

---

## SUMMARY

OpenAIRE provides **exceptional value** for OSINT research systems:

✅ **Free access** to 7.2M+ Italian research outputs
✅ **Real-time** research collaboration monitoring
✅ **No authentication** barriers for basic usage
✅ **Comprehensive coverage** of EU research ecosystem
✅ **Rich metadata** for relationship mapping
✅ **Active development** with new features in 2025

**Immediate Action:** Begin with country-specific research product searches to validate data quality and relevance for your analysis objectives.

---

*Last Updated: September 18, 2025*
*API Status: Confirmed Working*
*Next Review: October 1, 2025*
