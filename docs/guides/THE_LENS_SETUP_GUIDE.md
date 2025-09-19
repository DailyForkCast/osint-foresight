# The Lens Setup Guide for OSINT Foresight

## Overview
The Lens provides integrated patent and scholarly literature search with unique patent-to-science linkage capabilities essential for technology transfer analysis.

## Registration Process

### Step 1: Create Free Account
1. Go to https://www.lens.org
2. Click "Sign Up" (takes ~30 seconds)
3. Free account includes:
   - Collections (up to 10,000 IDs recommended)
   - Query Alerts
   - Notes functionality
   - Export capabilities

### Step 2: Account Benefits
- **Export Limit:** 50,000 records per batch (vs 1,000 for anonymous users)
- **Dynamic Collections:** Auto-update with new matching content
- **Email Alerts:** Monitor saved searches
- **API Access:** Available with token generation

## Key Features for OSINT Foresight

### 1. Patent-Science Integration
- Cross-references 200M scientific papers with 136M patents
- Track how research influences innovation
- Essential for China tech transfer analysis

### 2. PatCite Analysis
- Identify which scholarly works are cited in patents
- Discover research-to-commercialization pathways
- Map university-to-industry knowledge flows

### 3. Biological Sequences (PatSeq)
- 480M+ searchable patent sequences
- BLAST+ similarity search
- Critical for biotech/pharma analysis

### 4. Export Capabilities
- **Registered users:** 50,000 records per export
- **Formats:** CSV, JSON, RIS, BibTeX
- **Bulk downloads:** Available with updates

### 5. API Access
- **Scholarly API:** 50,000 requests/month, 1,000 records per request
- **Patent API:** Requires institutional access (1,000 requests/month)
- **Token-based authentication**

## Search Strategies for Our Project

### Italy Technology Transfer Analysis
```
Search Examples:
1. Italian institutions + Chinese co-authors:
   applicant.owner:"Leonardo" AND applicant.country:"CN"

2. Cross-border collaborations:
   inventor.country:"IT" AND applicant.country:"CN"

3. Technology fields of interest:
   cpc.symbol:"H04L" AND jurisdiction:"EP" AND applicant.country:"IT"
```

### Conference Intelligence Enhancement
- Search for patents filed after major conferences
- Track inventor movements between institutions
- Identify patent families across jurisdictions

## API Integration

### Setup API Access
1. Log into account
2. Navigate to Profile → API Access
3. Generate API token
4. Store in `.env` file:
```
LENS_API_TOKEN=your_token_here
```

### Basic API Script Template
```python
"""
The Lens API Client for OSINT Foresight
"""
import requests
import json
from typing import Dict, List

class LensAPIClient:
    def __init__(self, api_token: str):
        self.base_url = "https://api.lens.org"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def search_patents(self, query: Dict) -> Dict:
        """Search patents with complex queries"""
        endpoint = f"{self.base_url}/patent/search"
        response = requests.post(
            endpoint,
            headers=self.headers,
            json=query
        )
        return response.json()

    def get_patent_citations(self, patent_id: str) -> List:
        """Get scholarly works cited by patent"""
        # PatCite functionality
        pass

    def export_results(self, collection_id: str, format: str = "csv"):
        """Export collection results"""
        # Bulk export functionality
        pass
```

## Priority Searches for Italy Analysis

### 1. Leonardo Patent Portfolio
- All Leonardo patents globally
- Joint patents with Chinese entities
- Technology overlap with US systems

### 2. University Collaborations
- Politecnico di Milano + Chinese universities
- Joint publications leading to patents
- Researcher mobility patterns

### 3. Supply Chain Intelligence
- Component manufacturer patents
- Technology dependencies
- Alternative supplier identification

## Data Collection Schedule

### Weekly Tasks
- Monitor new Italian patents with Chinese connections
- Track Leonardo patent family expansions
- Check for new China-Italy joint filings

### Monthly Analysis
- Export full dataset (up to 50K records)
- Cross-reference with CORDIS projects
- Update technology transfer metrics

### Quarterly Deep Dives
- Comprehensive patent landscape analysis
- Citation network mapping
- Technology emergence tracking

## Integration with Existing Tools

### Combine with:
- **Google Patents BigQuery:** For comprehensive coverage
- **CORDIS:** Link EU-funded research to patents
- **OpenAlex:** Academic publication analysis
- **TED:** Connect patents to procurement

### Output Artifacts
```
artifacts/Italy/_national/
├── lens_patent_portfolio.json
├── patent_science_links.csv
├── technology_transfer_map.json
└── china_collaboration_patents.csv
```

## OECD Patent Databases (Secondary Priority)

### Access Points
1. **OECD.Stat:** https://stats.oecd.org
   - Patent statistics by technology
   - International co-inventions
   - Triadic patent families

2. **Key Databases:**
   - **REGPAT:** Patent regional data
   - **HAN:** Harmonized Applicant Names
   - **Patent Quality Indicators**
   - **Citations Database**

3. **Unique Value:**
   - Policy-oriented aggregations
   - Cross-country standardized metrics
   - Pre-calculated innovation indicators

### Setup Process
1. No registration required for basic access
2. Navigate to OECD.Stat → Science, Technology and Patents
3. Export data in CSV/Excel format
4. API access available for some datasets

## Success Metrics

### Week 1
- [ ] Lens account created and verified
- [ ] First 1,000 patents exported
- [ ] API token generated
- [ ] Initial Italy-China search completed

### Month 1
- [ ] 50,000 record export completed
- [ ] Patent-to-science links mapped
- [ ] Integration scripts operational
- [ ] OECD databases accessed

### Ongoing
- [ ] Weekly monitoring active
- [ ] Automated alerts configured
- [ ] Regular exports scheduled
- [ ] Cross-database linkage established

## Troubleshooting

### Common Issues
1. **Export limits reached:** Wait 24 hours or split query
2. **API rate limits:** Implement exponential backoff
3. **Complex queries timeout:** Simplify and batch
4. **Missing data fields:** Check coverage by jurisdiction

## Next Steps
1. Create Lens account immediately (free)
2. Run initial Leonardo patent search
3. Export first dataset for analysis
4. Set up API integration
5. Access OECD.Stat for comparative metrics

---

*Last Updated: 2025-09-16*
*Guide for OSINT Foresight Italy Analysis*
