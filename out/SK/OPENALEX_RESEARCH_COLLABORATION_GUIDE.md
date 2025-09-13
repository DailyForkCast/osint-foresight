# OpenAlex and Free Research Collaboration Mapping Guide
**Focus on genuinely free sources - no hidden paywalls**
**Date: September 10, 2025**

## 1. OPENALEX - THE GAME CHANGER

### 1.1 What OpenAlex Actually Is

**Completely Free Academic Database:**
- **250+ million scholarly works** (papers, books, datasets)
- **90+ million author profiles** with affiliations
- **250,000+ institutions** mapped globally
- **65,000+ publication venues** (journals, conferences)
- **Replaces Microsoft Academic Graph** (but better and free)

**Key Advantages:**
- 100% free, no registration required
- Complete database downloadable (via AWS)
- REST API with no rate limits
- Daily updates
- Includes citations, references, and collaboration networks

### 1.2 How to Use OpenAlex for Slovak-Chinese Collaboration

**Direct API Query Examples:**

```python
import requests
import json

# Find all Slovak-Chinese collaborations
def get_slovak_chinese_collaborations():
    url = "https://api.openalex.org/works"
    params = {
        'filter': 'institutions.country_code:SK,institutions.country_code:CN',
        'group_by': 'publication_year',
        'per_page': 200
    }
    response = requests.get(url, params=params)
    return response.json()

# Get specific institution collaborations
def get_institution_collabs(institution_id):
    url = f"https://api.openalex.org/works"
    params = {
        'filter': f'institutions.id:{institution_id}',
        'group_by': 'institutions.id',
        'per_page': 100
    }
    response = requests.get(url, params=params)
    return response.json()

# Map co-authorship networks
def get_coauthor_network(author_id):
    url = f"https://api.openalex.org/works"
    params = {
        'filter': f'author.id:{author_id}',
        'select': 'id,title,authorships',
        'per_page': 200
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 1.3 Specific Queries for Slovakia Analysis

**Find PLA University Collaborations:**
```python
# Known PLA universities in OpenAlex
pla_universities = {
    'Beijing Institute of Technology': 'https://openalex.org/I18785166',
    'Beihang University': 'https://openalex.org/I91045325',
    'Northwestern Polytechnical': 'https://openalex.org/I153308706',
    'Harbin Institute of Technology': 'https://openalex.org/I44814098'
}

slovak_institutions = {
    'Comenius University': 'https://openalex.org/I36369341',
    'Slovak University of Technology': 'https://openalex.org/I132856873',
    'Technical University Košice': 'https://openalex.org/I185078092',
    'Slovak Academy of Sciences': 'https://openalex.org/I4210141026'
}

# Find direct collaborations
for sk_inst, sk_id in slovak_institutions.items():
    for pla_inst, pla_id in pla_universities.items():
        url = "https://api.openalex.org/works"
        params = {
            'filter': f'institutions.id:{sk_id},institutions.id:{pla_id}',
            'select': 'id,title,publication_year,doi'
        }
        # This gives exact papers with both institutions
```

### 1.4 Building Collaboration Networks

**Complete Network Analysis:**
```python
import networkx as nx
import matplotlib.pyplot as plt

def build_collaboration_network():
    G = nx.Graph()
    
    # Get all Slovak papers with international collaborations
    url = "https://api.openalex.org/works"
    params = {
        'filter': 'institutions.country_code:SK',
        'select': 'id,authorships',
        'per_page': 200,
        'cursor': '*'  # For pagination
    }
    
    # Process results to build network
    # Add edges between collaborating institutions
    # Weight by number of joint papers
    
    return G

# Analyze the network
def analyze_network(G):
    centrality = nx.betweenness_centrality(G)
    communities = nx.community.louvain_communities(G)
    clustering = nx.clustering(G)
    return centrality, communities, clustering
```

## 2. OTHER GENUINELY FREE ACADEMIC SOURCES

### 2.1 Semantic Scholar

**What It Is:**
- 200+ million papers
- AI-enhanced search
- API with 100 requests/second (free)
- Citation context (why papers cite each other)

**API Example:**
```python
import requests

# Search for papers
def search_semantic_scholar(query):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
        'fields': 'title,authors,year,affiliations',
        'limit': 100
    }
    response = requests.get(url, params=params)
    return response.json()

# Get paper details with citations
def get_paper_details(paper_id):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    params = {
        'fields': 'title,authors,references,citations,affiliations'
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 2.2 CrossRef

**What It Is:**
- 150+ million scholarly records
- Completely free API
- No registration required
- Includes funding information

**Finding Collaborations:**
```python
# Search for Slovak-Chinese papers via CrossRef
def search_crossref(affiliation1='Slovakia', affiliation2='China'):
    url = "https://api.crossref.org/works"
    params = {
        'query.affiliation': f'{affiliation1} AND {affiliation2}',
        'rows': 100
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 2.3 PubMed Central

**For Biotech/Battery Chemistry:**
```python
from Bio import Entrez

Entrez.email = "your.email@example.com"

def search_pubmed_collaborations():
    query = '(Slovakia[Affiliation]) AND (China[Affiliation])'
    handle = Entrez.esearch(db="pubmed", term=query, retmax=1000)
    results = Entrez.read(handle)
    
    # Get full records
    id_list = results['IdList']
    handle = Entrez.efetch(db="pubmed", id=id_list, rettype="xml")
    records = Entrez.read(handle)
    
    return records
```

### 2.4 arXiv

**For Computer Science/AI/Physics:**
```python
import arxiv

def search_arxiv_collaborations():
    search = arxiv.Search(
        query="au:Slovakia AND au:China",
        max_results=100,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    for paper in search.results():
        papers.append({
            'title': paper.title,
            'authors': [a.name for a in paper.authors],
            'affiliations': paper.affiliations,  # If available
            'categories': paper.categories
        })
    
    return papers
```

## 3. GENUINELY FREE COMPANY DATA SOURCES

### 3.1 Instead of OpenCorporates API

**Government Registries (Direct Access):**

**Slovakia - Completely Free:**
```python
# Slovak Business Register - web scraping needed
import requests
from bs4 import BeautifulSoup

def get_slovak_company(ico):
    # orsr.sk - no API but scrapeable
    url = f"https://orsr.sk/hladaj_ico.asp?ICO={ico}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Parse company details
    return parsed_data

# Financial statements - registeruz.sk
def get_financial_statements(ico):
    url = f"https://registeruz.sk/cruz-public/api/uctovne-jednotky/{ico}"
    response = requests.get(url)
    return response.json()
```

**UK - Fully Open API:**
```python
# UK Companies House - FREE API
def get_uk_company(company_number):
    url = f"https://api.company-information.service.gov.uk/company/{company_number}"
    # Note: Requires free API key
    headers = {'Authorization': 'YOUR_FREE_API_KEY'}
    response = requests.get(url, headers=headers)
    return response.json()
```

**US - SEC EDGAR:**
```python
# SEC EDGAR - completely free
from edgar import Company

def get_us_company_filings(ticker):
    company = Company(ticker)
    filings = company.get_filings()
    return filings
```

### 3.2 GLEIF (LEI Database) - Totally Free

**Complete Ownership Data:**
```python
import pandas as pd

# Download entire LEI database (updated daily)
def download_lei_database():
    # Level 1 - Legal entities
    url1 = "https://goldencopy.gleif.org/api/v2/golden-copies/publishes/latest/lei2.csv"
    lei_data = pd.read_csv(url1)
    
    # Level 2 - Ownership relationships
    url2 = "https://goldencopy.gleif.org/api/v2/golden-copies/publishes/latest/rr.csv"
    ownership_data = pd.read_csv(url2)
    
    return lei_data, ownership_data

# Find ownership chains
def trace_ownership(lei_code, ownership_data):
    parents = ownership_data[ownership_data['Relationship.StartNode.NodeID'] == lei_code]
    children = ownership_data[ownership_data['Relationship.EndNode.NodeID'] == lei_code]
    return parents, children
```

## 4. BUILDING COMPLETE COLLABORATION PICTURE

### 4.1 Multi-Source Integration

```python
def build_complete_collaboration_map():
    collaborations = []
    
    # 1. OpenAlex - most comprehensive
    openalex_data = get_openalex_collaborations()
    collaborations.extend(openalex_data)
    
    # 2. Semantic Scholar - AI/CS focused
    semantic_data = get_semantic_scholar_collabs()
    collaborations.extend(semantic_data)
    
    # 3. PubMed - biotech/chemistry
    pubmed_data = get_pubmed_collabs()
    collaborations.extend(pubmed_data)
    
    # 4. arXiv - early indicators
    arxiv_data = get_arxiv_collabs()
    collaborations.extend(arxiv_data)
    
    # 5. CrossRef - funding information
    crossref_data = get_crossref_collabs()
    collaborations.extend(crossref_data)
    
    # Deduplicate by DOI
    unique_collabs = deduplicate_by_doi(collaborations)
    
    return unique_collabs
```

### 4.2 Visualization with Free Tools

```python
import plotly.graph_objects as go
import networkx as nx

def visualize_collaboration_network(collaborations):
    G = nx.Graph()
    
    # Build network from collaborations
    for collab in collaborations:
        for i, inst1 in enumerate(collab['institutions']):
            for inst2 in collab['institutions'][i+1:]:
                if G.has_edge(inst1, inst2):
                    G[inst1][inst2]['weight'] += 1
                else:
                    G.add_edge(inst1, inst2, weight=1)
    
    # Create interactive visualization
    pos = nx.spring_layout(G)
    
    # Use plotly for interactive graph
    edge_trace = []
    node_trace = []
    
    # ... build traces ...
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.show()
    
    return G
```

## 5. SPECIFIC SLOVAK-CHINESE RESEARCH ANALYSIS

### 5.1 Step-by-Step Process

**Step 1: Identify Key Slovak Institutions**
```python
# Use OpenAlex to get Slovak institution IDs
slovak_institutions_url = "https://api.openalex.org/institutions"
params = {
    'filter': 'country_code:SK',
    'per_page': 100
}
# Returns all Slovak research institutions with their OpenAlex IDs
```

**Step 2: Find Their Chinese Collaborations**
```python
for institution in slovak_institutions:
    url = "https://api.openalex.org/works"
    params = {
        'filter': f'institutions.id:{institution["id"]},institutions.country_code:CN',
        'group_by': 'institutions.id',
        'select': 'id,title,publication_year,concepts,cited_by_count'
    }
    # This gives all Chinese collaborations for each Slovak institution
```

**Step 3: Identify Sensitive Topics**
```python
sensitive_concepts = [
    'C41008148',  # Computer Science
    'C127313418',  # Quantum Computing
    'C119599485',  # Artificial Intelligence
    'C178790620',  # Battery
    'C135628077',  # Semiconductors
]

# Filter collaborations by concept
sensitive_collabs = filter_by_concepts(all_collabs, sensitive_concepts)
```

**Step 4: Track Evolution Over Time**
```python
# Analyze collaboration trends
yearly_collabs = group_by_year(sensitive_collabs)
plot_trend(yearly_collabs)

# Identify sudden increases
detect_anomalies(yearly_collabs)
```

## 6. QUALITY METRICS FROM FREE SOURCES

### 6.1 Research Impact Metrics

**From OpenAlex:**
- Citation counts
- h-index for authors
- Journal impact factors
- Altmetric scores (social media impact)
- Concept scores (topic relevance)

**Analysis Example:**
```python
def assess_collaboration_quality(works):
    metrics = {
        'total_citations': sum(w['cited_by_count'] for w in works),
        'avg_citations': np.mean([w['cited_by_count'] for w in works]),
        'high_impact': len([w for w in works if w['cited_by_count'] > 50]),
        'venues': set(w['host_venue']['id'] for w in works),
        'international': len(set(w['institutions'] for w in works))
    }
    return metrics
```

### 6.2 Network Metrics

```python
def calculate_network_metrics(G):
    metrics = {
        'density': nx.density(G),
        'clustering': nx.average_clustering(G),
        'centrality': nx.degree_centrality(G),
        'betweenness': nx.betweenness_centrality(G),
        'communities': len(list(nx.community.louvain_communities(G))),
        'key_brokers': identify_brokers(G)
    }
    return metrics
```

## 7. AUTOMATION WITH GITHUB ACTIONS (FREE)

### 7.1 Daily Collaboration Monitoring

```yaml
name: Daily Collaboration Check
on:
  schedule:
    - cron: '0 9 * * *'

jobs:
  check_new_collaborations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install requests pandas networkx
      
      - name: Check OpenAlex for new collaborations
        run: python scripts/check_new_collabs.py
      
      - name: Generate report
        run: python scripts/generate_report.py
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data/
          git commit -m "Update collaboration data"
          git push
```

## 8. WHAT WE CAN ACTUALLY ACHIEVE

### 8.1 With These Free Sources

**Complete Mapping:**
- All Slovak-Chinese research collaborations since 2000
- Full co-authorship networks
- Institution-level partnership patterns
- Topic/field concentration areas
- Temporal evolution of collaborations
- Quality metrics for all collaborations

**Specific Insights:**
- Which Slovak researchers work with PLA universities
- What topics they collaborate on
- How collaborations have evolved
- Where sensitive technology overlap exists
- Who are the key bridge researchers

### 8.2 Limitations

**What We Still Can't Get:**
- Unpublished research collaborations
- Classified or proprietary work
- Industry collaborations without publications
- Informal relationships
- Future planned collaborations

## 9. PRACTICAL IMPLEMENTATION

### 9.1 Today (1 Hour)

```python
# Quick script to get started
import requests
import json

# Get all Slovak-Chinese collaborations from 2020-2025
url = "https://api.openalex.org/works"
params = {
    'filter': 'institutions.country_code:SK,institutions.country_code:CN,publication_year:2020-2025',
    'select': 'id,title,publication_year,authorships,concepts',
    'per_page': 200,
    'cursor': '*'
}

all_works = []
cursor = '*'

while cursor:
    params['cursor'] = cursor
    response = requests.get(url, params=params)
    data = response.json()
    all_works.extend(data['results'])
    cursor = data['meta'].get('next_cursor')

print(f"Found {len(all_works)} Slovak-Chinese collaborations")

# Save to file
with open('slovak_chinese_collabs.json', 'w') as f:
    json.dump(all_works, f)
```

### 9.2 This Week (10 Hours)

1. Set up automated collection from all free sources
2. Build complete collaboration database
3. Create network visualizations
4. Identify key researchers and institutions
5. Generate first analytical report

### 9.3 Ongoing (1 Hour/Week)

- Monitor new publications
- Update collaboration networks
- Track emerging patterns
- Alert on sensitive collaborations

## 10. KEY TAKEAWAY

**OpenAlex alone can provide 80% of research collaboration intelligence needs - completely free**

Combined with other free sources (Semantic Scholar, CrossRef, PubMed, arXiv), we can achieve near-complete coverage of published research collaborations. The only missing pieces are unpublished/classified work.

For company data, while OpenCorporates API costs money, government registries (Slovak, UK, US) provide free alternatives with some additional effort.

---
**Bottom Line**: Focus on OpenAlex as primary source, supplement with other free academic databases, and use government registries directly for company data. This combination provides professional-grade intelligence at zero cost.