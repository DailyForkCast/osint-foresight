# Free Data Source Integration Guide
## Cost-Effective Implementation for OSINT Foresight

### 1. Patent Signals (Google Patents BigQuery)

**Setup:**
1. Create Google Cloud Project (free tier)
2. Enable BigQuery API
3. No credit card required for 1TB/month

**Query Example:**
```sql
-- Italian AI patents with Chinese co-inventors
SELECT
  p.family_id,
  p.publication_number,
  STRING_AGG(DISTINCT a.assignee_harmonized, '; ') as assignees,
  STRING_AGG(DISTINCT i.country_code, ', ') as inventor_countries,
  p.title.text as title
FROM `patents-public-data.patents.publications` p,
  UNNEST(assignee) a,
  UNNEST(inventor) i
WHERE p.country_code = 'IT'
  AND '2020' <= SUBSTR(p.application_date, 1, 4)
  AND EXISTS(SELECT 1 FROM UNNEST(cpc) c WHERE c.code LIKE 'G06N%')
  AND 'CN' IN (SELECT country_code FROM UNNEST(inventor))
GROUP BY 1,2,5
```

**Python Integration:**
```python
from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/service-account-key.json"
client = bigquery.Client()

def get_italy_china_patents(cpc_prefix="G06N", years_back=5):
    query = f"""
    SELECT
      COUNT(DISTINCT family_id) as patent_count,
      EXTRACT(YEAR FROM PARSE_DATE('%Y%m%d', application_date)) as year,
      STRING_AGG(DISTINCT assignee_harmonized, '; ' LIMIT 5) as top_assignees
    FROM `patents-public-data.patents.publications`,
      UNNEST(assignee) a
    WHERE country_code = 'IT'
      AND application_date >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL {years_back} YEAR))
      AND EXISTS(SELECT 1 FROM UNNEST(cpc) c WHERE c.code LIKE '{cpc_prefix}%')
      AND EXISTS(SELECT 1 FROM UNNEST(inventor) i WHERE i.country_code = 'CN')
    GROUP BY year
    ORDER BY year DESC
    """
    return client.query(query).to_dataframe()
```

### 2. Co-authorship Networks (OpenAlex)

**No Setup Required - Just HTTP requests**

**Python Implementation:**
```python
import requests
import json
from typing import Dict, List
from datetime import datetime, timedelta

class OpenAlexAnalyzer:
    def __init__(self, email: str):
        self.base_url = "https://api.openalex.org"
        self.headers = {
            "User-Agent": f"OSINT-Foresight/1.0 (mailto:{email})"
        }

    def get_italy_collaborations(self, days_back: int = 365) -> Dict:
        """Get Italy's research collaborations"""
        date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = f"{self.base_url}/works"
        params = {
            "filter": f"institutions.country_code:IT,from_publication_date:{date_from}",
            "group_by": "authorships.countries",
            "per_page": 200
        }

        response = requests.get(url, params=params, headers=self.headers)
        data = response.json()

        # Extract China collaboration metrics
        china_collab = next((g for g in data.get('group_by', [])
                            if 'CN' in g.get('key', '')), None)

        return {
            "total_papers": data.get('meta', {}).get('count', 0),
            "china_papers": china_collab.get('count', 0) if china_collab else 0,
            "top_collab_countries": data.get('group_by', [])[:10]
        }

    def get_institution_collaborations(self, ror_id: str) -> List:
        """Get specific institution's international collaborations"""
        url = f"{self.base_url}/works"
        params = {
            "filter": f"institutions.ror:{ror_id}",
            "group_by": "authorships.institutions.country_code",
            "per_page": 100
        }

        response = requests.get(url, params=params, headers=self.headers)
        return response.json().get('group_by', [])
```

### 3. Critical Components (UN Comtrade)

**Free Tier: 100 requests/hour**

**Python Implementation:**
```python
import requests
from typing import List, Dict

class ComtradeAnalyzer:
    def __init__(self):
        self.base_url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
        # Free tier - no API key needed

    def get_component_suppliers(self, hs_code: str, reporter: str = "380") -> Dict:
        """Get suppliers for critical components to Italy"""
        params = {
            "reporterCode": reporter,  # 380 = Italy
            "period": "2024",
            "cmdCode": hs_code,
            "flowCode": "M",  # Imports
            "partnerCode": "0",  # All partners
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        # Identify concentration risk
        total_value = sum(r['primaryValue'] for r in data.get('data', []))
        china_value = sum(r['primaryValue'] for r in data.get('data', [])
                         if r['partnerCode'] == '156')  # China

        return {
            "hs_code": hs_code,
            "total_import_value": total_value,
            "china_share": (china_value / total_value * 100) if total_value > 0 else 0,
            "top_suppliers": sorted(data.get('data', []),
                                  key=lambda x: x['primaryValue'],
                                  reverse=True)[:10]
        }

# Critical components to monitor
CRITICAL_HS_CODES = {
    "8542": "Integrated circuits",
    "8541": "Semiconductor devices",
    "9013": "Liquid crystal devices/lasers/optical",
    "8803": "Aircraft parts",
    "8471": "Automatic data processing machines",
    "2804": "Rare gases",
    "8105": "Cobalt",
    "2846": "Rare earth compounds"
}
```

### 4. Scholar Flows (ORCID)

**Public API - No authentication required**

**Python Implementation:**
```python
import requests
from typing import List, Dict, Optional
from datetime import datetime

class ORCIDTracker:
    def __init__(self):
        self.base_url = "https://pub.orcid.org/v3.0"
        self.headers = {"Accept": "application/json"}

    def get_researcher_mobility(self, orcid_id: str) -> List[Dict]:
        """Track researcher institutional movements"""
        # Get employment history
        emp_url = f"{self.base_url}/{orcid_id}/employments"
        emp_response = requests.get(emp_url, headers=self.headers)

        if emp_response.status_code != 200:
            return []

        employments = emp_response.json()
        movements = []

        for emp_summary in employments.get('employment-summary', []):
            # Get detailed employment record
            put_code = emp_summary.get('put-code')
            detail_url = f"{self.base_url}/{orcid_id}/employment/{put_code}"
            detail_resp = requests.get(detail_url, headers=self.headers)

            if detail_resp.status_code == 200:
                detail = detail_resp.json()
                org = detail.get('organization', {})

                movement = {
                    "organization": org.get('name'),
                    "country": org.get('address', {}).get('country'),
                    "city": org.get('address', {}).get('city'),
                    "start_date": detail.get('start-date'),
                    "end_date": detail.get('end-date'),
                    "role": detail.get('role-title')
                }
                movements.append(movement)

        # Sort by start date
        movements.sort(key=lambda x: (
            x.get('start_date', {}).get('year', {}).get('value', '0000'),
            x.get('start_date', {}).get('month', {}).get('value', '00')
        ))

        return movements

    def find_china_trained_researchers(self, institution_ror: str) -> List:
        """Find researchers at institution who trained in China"""
        # Would need to combine with institution's researcher list
        # This is a simplified example

        search_url = f"{self.base_url}/search"
        params = {
            "q": f'affiliation-org-name:"{institution_ror}"'
        }

        response = requests.get(search_url, params=params, headers=self.headers)
        results = response.json()

        china_trained = []
        for result in results.get('result', [])[:100]:  # Check first 100
            orcid = result.get('orcid-identifier', {}).get('path')
            if orcid:
                movements = self.get_researcher_mobility(orcid)
                if any(m.get('country') == 'CN' for m in movements):
                    china_trained.append({
                        "orcid": orcid,
                        "name": result.get('given-names', '') + ' ' + result.get('family-name', ''),
                        "movements": movements
                    })

        return china_trained
```

### 5. Ownership Chains (GLEIF)

**Completely FREE - No registration required**

**Python Implementation:**
```python
import requests
from typing import Dict, Optional, List

class GLEIFOwnershipTracker:
    def __init__(self):
        self.base_url = "https://api.gleif.org/api/v1"

    def get_ownership_chain(self, lei: str) -> Dict:
        """Get complete ownership structure"""
        chain = {
            "lei": lei,
            "entity": self.get_entity_details(lei),
            "direct_parent": None,
            "ultimate_parent": None,
            "china_owned": False
        }

        # Get direct parent
        direct_url = f"{self.base_url}/lei-records/{lei}/direct-parent-relationship"
        direct_resp = requests.get(direct_url)
        if direct_resp.status_code == 200:
            direct_data = direct_resp.json().get('data', [])
            if direct_data:
                parent_lei = direct_data[0]['attributes']['parent']['lei']
                chain['direct_parent'] = {
                    "lei": parent_lei,
                    "details": self.get_entity_details(parent_lei)
                }

        # Get ultimate parent
        ultimate_url = f"{self.base_url}/lei-records/{lei}/ultimate-parent-relationship"
        ultimate_resp = requests.get(ultimate_url)
        if ultimate_resp.status_code == 200:
            ultimate_data = ultimate_resp.json().get('data', [])
            if ultimate_data:
                ultimate_lei = ultimate_data[0]['attributes']['parent']['lei']
                chain['ultimate_parent'] = {
                    "lei": ultimate_lei,
                    "details": self.get_entity_details(ultimate_lei)
                }

                # Check if China-owned
                ultimate_country = chain['ultimate_parent']['details'].get('country')
                if ultimate_country == 'CN':
                    chain['china_owned'] = True

        return chain

    def get_entity_details(self, lei: str) -> Dict:
        """Get entity information"""
        url = f"{self.base_url}/lei-records/{lei}"
        response = requests.get(url)

        if response.status_code != 200:
            return {}

        data = response.json()['data'][0]['attributes']['entity']
        return {
            "name": data['legalName']['name'],
            "country": data['legalAddress']['country'],
            "city": data['legalAddress']['city'],
            "status": data['status']
        }
```

## Cost Summary

| System | Data Source | Cost | Limits |
|--------|------------|------|--------|
| Patent Signals | Google Patents BigQuery | FREE | 1TB queries/month |
| Co-authorship | OpenAlex | FREE | 100k requests/day |
| Components | UN Comtrade | FREE | 100 requests/hour |
| Scholar Flows | ORCID | FREE | 24 requests/second |
| Ownership | GLEIF | FREE | No limits |
| Trade Data | Eurostat | FREE | No limits |
| EU Projects | CORDIS | FREE | No limits |

## Alternative Sources

### For Ownership (if no LEI):
- **SEC EDGAR API**: Free for US companies
- **Companies House UK**: Free with registration
- **InfoCamere** (Italy): Some free access
- **Handelsregister** (Germany): Basic free search

### For Scholar Tracking:
- **Semantic Scholar API**: Free, good coverage
- **CrossRef API**: Free, publication metadata
- **PubMed API**: Free for biomedical
- **arXiv API**: Free for physics/CS/math

### For Supply Chain:
- **ITC Trade Map**: Some free data
- **Observatory of Economic Complexity**: Free visualizations
- **WITS (World Bank)**: Free trade statistics

## Implementation Order

1. **Day 1**: Set up OpenAlex and ORCID (no registration needed)
2. **Day 2**: Configure Google Cloud for BigQuery (free tier)
3. **Day 3**: Implement UN Comtrade for components
4. **Day 4**: Add GLEIF for ownership chains
5. **Week 2**: Integrate CORDIS and other EU sources

This approach provides comprehensive coverage at zero cost, with rate limits that are sufficient for monitoring 67 countries on a rotating basis.
