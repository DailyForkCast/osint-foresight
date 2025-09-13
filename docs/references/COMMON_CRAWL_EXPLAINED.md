# Common Crawl - What It Is and How to Use It

## What is Common Crawl?

Common Crawl is a **massive dataset of web crawl data** - essentially a copy of the internet that's freely available to everyone. Think of it as a periodic snapshot of billions of web pages.

### Key Facts
- **Size**: 3-5 billion web pages per crawl (petabytes of data)
- **Frequency**: New crawl every 1-2 months
- **History**: Data available since 2008
- **Format**: WARC files (Web ARChive format), plus extracted text and metadata
- **Cost**: FREE to access (but you pay for compute/bandwidth)
- **Storage**: Hosted on AWS S3

---

## What Would You Use It For?

### 1. **Company Intelligence & Supply Chain Discovery**
```python
# Example: Find all mentions of suppliers on company websites
def find_supplier_mentions(company_domain):
    """
    Search Common Crawl for pages mentioning "supplier", "vendor", 
    "partner" on a company's website
    """
    # This reveals supply chain relationships not in databases
```

**Use cases**:
- Discover unlisted suppliers/partners from company websites
- Track changes in supplier relationships over time
- Find procurement notices on company sites
- Extract product catalogs and specifications

### 2. **Technology Adoption Tracking**
```python
# Example: Track which companies use specific technologies
def track_tech_adoption():
    """
    Search for JavaScript libraries, frameworks, or tech stack mentions
    across all corporate websites in a country
    """
    # Reveals actual technology usage vs. claimed capabilities
```

**Use cases**:
- Identify companies using specific software/frameworks
- Track adoption of standards (ISO, security certificates)
- Find companies mentioning AI, quantum, blockchain etc.
- Map technology clusters by region

### 3. **Research & Innovation Signals**
```python
# Example: Find research collaboration mentions
def find_research_partnerships():
    """
    Extract mentions of joint research, collaboration agreements,
    university partnerships from organizational websites
    """
```

**Use cases**:
- Discover research partnerships not in formal databases
- Track innovation announcements and R&D investments
- Find technical documentation and whitepapers
- Identify expertise claims and capabilities

### 4. **Regulatory & Compliance Intelligence**
```python
# Example: Track regulatory compliance statements
def track_compliance():
    """
    Find GDPR notices, export control statements, 
    sanctions compliance mentions across websites
    """
```

**Use cases**:
- Monitor compliance with regulations
- Find export control classifications
- Track data sovereignty statements
- Identify regulatory risks

---

## How Common Crawl Helps OSINT Foresight

### Supply Chain Mapping
- **Problem**: Official databases miss informal relationships
- **Solution**: Extract supplier mentions from "About Us" pages, press releases, case studies
- **Example**: "We're proud to supply components to [Major Company]"

### Technology Intelligence
- **Problem**: No database tracks actual technology implementation
- **Solution**: Analyze website source code, job postings, technical docs
- **Example**: Finding all Austrian companies using specific ML frameworks

### Early Warning Signals
- **Problem**: Traditional sources have delays
- **Solution**: Detect changes in website content as leading indicators
- **Example**: Removal of partnership mentions, technology pivots

### Hidden Networks
- **Problem**: Not all collaborations are formally registered
- **Solution**: Extract mentions of joint projects, shared facilities, co-located offices
- **Example**: Finding informal research clusters

---

## Practical Approaches for Your Project

### Option 1: Targeted Extraction (Recommended)
```python
# Use Common Crawl Index to find specific domains
# Only download relevant pages, not entire crawl

def extract_austrian_tech_companies():
    # 1. Query CC Index for .at domains
    # 2. Filter for technology-related companies
    # 3. Download only those pages
    # 4. Extract supply chain and tech signals
```

**Pros**: Manageable size (GB not PB), focused results
**Cons**: Might miss some relationships

### Option 2: Use Derived Datasets
Several projects provide processed Common Crawl data:
- **WDC Web Tables**: Structured data extracted from web tables
- **Web Data Commons**: RDF triples, microdata, JSON-LD
- **C4 Dataset**: Cleaned Common Crawl for NLP (used to train T5, GPT)

**Pros**: Pre-processed, smaller, easier to use
**Cons**: May not have specific data you need

### Option 3: Cloud Processing (Advanced)
```python
# Use AWS Athena to query Common Crawl without downloading

def query_on_aws():
    # Common Crawl provides Athena tables
    # Pay only for queries, not storage
    # Can search petabytes in minutes
```

**Pros**: Search entire internet
**Cons**: Requires AWS account, costs per query

---

## Specific OSINT Foresight Use Cases

### 1. Austrian Supply Chain Discovery
```sql
-- Find all mentions of Austrian companies as suppliers
SELECT url, content_snippet 
FROM common_crawl
WHERE content LIKE '%supplier%' 
  AND (content LIKE '%.at%' OR content LIKE '%Austria%')
  AND crawl_date > '2023-01-01'
```

### 2. Technology Adoption Trends
```python
# Track quantum computing mentions over time
def track_quantum_adoption():
    crawls_2020 = search_cc("quantum computing", year=2020)
    crawls_2024 = search_cc("quantum computing", year=2024)
    
    # Identify new entrants, measure growth
    return growth_analysis(crawls_2020, crawls_2024)
```

### 3. Sanctions Evasion Detection
```python
# Find companies that removed Russia mentions after 2022
def detect_relationship_changes():
    pre_2022 = search_cc(domain="company.com", "Russia", before="2022-02")
    post_2022 = search_cc(domain="company.com", "Russia", after="2022-03")
    
    # Flag companies that scrubbed Russia references
```

---

## How to Access Common Crawl

### 1. Common Crawl Index (Start Here)
```python
import requests

# Query the index to find pages
index_url = "https://index.commoncrawl.org/CC-MAIN-2024-10-index"
params = {"url": "*.at/*", "output": "json"}
response = requests.get(index_url, params=params)

# Returns WARC file locations for Austrian domains
```

### 2. Download Specific Pages
```python
import boto3
from io import BytesIO
import warc

# No AWS account needed for public S3
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

# Download specific WARC segment
s3.download_file('commoncrawl', 
                 'crawl-data/CC-MAIN-2024-10/segments/1234/warc/file.warc.gz',
                 'local_file.warc.gz')
```

### 3. Process WARC Files
```python
import warc
import gzip

with gzip.open('local_file.warc.gz', 'rb') as f:
    for record in warc.WARCFile(fileobj=f):
        if record['WARC-Type'] == 'response':
            url = record['WARC-Target-URI']
            content = record.payload.read()
            # Extract supply chain signals
```

---

## Cost Considerations

### Storage Costs
- **Full crawl**: 100+ TB (not recommended)
- **Targeted extraction**: 10-100 GB (manageable)
- **Index searches**: MB (very efficient)

### Processing Costs
- **Local processing**: Free but slow
- **AWS EC2**: $50-500 depending on scale
- **AWS Athena**: $5 per TB scanned
- **Google BigQuery**: Similar pricing

### Recommended Approach
1. Start with index searches (free, fast)
2. Download only relevant pages (GB not TB)
3. Process locally or on small cloud instance
4. Store results in your existing BigQuery dataset

---

## Why Common Crawl vs. Scraping Yourself?

### Advantages
- **Historical data**: See how websites changed over time
- **Scale**: Billions of pages already crawled
- **Legal**: Public dataset, no scraping concerns
- **Cost**: Cheaper than crawling yourself
- **Speed**: Data already collected

### Disadvantages  
- **Not real-time**: 1-2 month delay
- **Not complete**: Doesn't crawl everything
- **Large files**: Even filtered data can be big
- **Processing needed**: Raw HTML requires extraction

---

## Next Steps for OSINT Foresight

### Quick Win (This Week)
```python
# Search Common Crawl index for Austrian tech companies
# Extract supplier mentions and technology signals
# No download needed, just index queries
```

### Medium Term (Next Month)
```python
# Download pages for all 44 target countries
# Extract supply chain and innovation signals
# Store structured data in BigQuery
```

### Advanced (Future)
```python
# Set up automated monthly processing
# Track changes over time
# Build prediction models from web signals
```

---

## Summary

**Common Crawl = The Internet's Archive**
- Free copy of billions of web pages
- Perfect for discovering hidden relationships
- Complements official databases
- Requires processing but provides unique insights

**For OSINT Foresight**: Use it to find supply chain relationships, technology adoption, and innovation signals that aren't in any official database.

---

*Think of Common Crawl as having access to every company website, research institution page, and government portal - frozen in time every month. It's like having a time machine for the internet.*