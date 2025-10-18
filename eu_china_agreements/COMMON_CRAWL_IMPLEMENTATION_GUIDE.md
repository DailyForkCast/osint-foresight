# Common Crawl Implementation Guide for EU-China Agreements Discovery

## 🎯 Why Common Crawl for Bilateral Agreements?

**Common Crawl addresses our key limitations:**
- **Municipal websites** poorly indexed by search engines
- **University partnership pages** buried in search results
- **Historical agreements** no longer on live websites
- **PDF documents** within institutional sites
- **Native language content** not prioritized by Google

---

## 🚀 Quick Start: Common Crawl Access

### **Method 1: AWS Athena (Recommended)**
```sql
-- Setup: Use AWS Athena with Common Crawl public dataset
-- Database: s3://commoncrawl/cc-index/table/cc-index/warc_filename/

-- Basic sister city query
SELECT url, content_digest, warc_filename, warc_record_offset
FROM "ccindex"."ccindex"
WHERE crawl = 'CC-MAIN-2024-10'  -- Latest crawl
AND content_languages = 'eng'
AND (
    url_host_name LIKE '%.gov.%' OR
    url_host_name LIKE '%.city.%' OR
    url_host_name LIKE '%.edu.%'
)
AND (
    content LIKE '%sister city%China%' OR
    content LIKE '%twin city%China%' OR
    content LIKE '%partnership%China%'
)
LIMIT 1000;
```

### **Method 2: Python with cdx-toolkit**
```python
# Install: pip install cdx-toolkit
from cdx_toolkit import CDXFetcher

cdx = CDXFetcher(source='cc')

# Search for sister city agreements
query = 'site:*.gov.* sister city China'
for record in cdx.iter(query, from_ts='20200101', to_ts='20241201'):
    print(f"URL: {record.url}")
    print(f"Timestamp: {record.timestamp}")
    print(f"Status: {record.status}")
```

---

## 🔍 Targeted Query Strategies

### **1. Sister City Partnerships**

#### **English Terms**:
```sql
WHERE (
    content LIKE '%sister city%China%' OR
    content LIKE '%twin city%China%' OR
    content LIKE '%friendship city%China%' OR
    content LIKE '%partnership%China%'
)
AND (
    url_host_name LIKE '%.gov.%' OR
    url_host_name LIKE '%.city.%' OR
    url_host_name LIKE '%.municipality.%'
)
```

#### **Multi-Language Terms**:
```sql
-- German
WHERE content LIKE '%Städtepartnerschaft%China%'
OR content LIKE '%Partnerstadt%China%'

-- French
WHERE content LIKE '%ville jumelée%Chine%'
OR content LIKE '%jumelage%Chine%'

-- Italian
WHERE content LIKE '%città gemelle%Cina%'
OR content LIKE '%gemellaggio%Cina%'

-- Spanish
WHERE content LIKE '%ciudades hermanas%China%'
OR content LIKE '%hermanamiento%China%'
```

### **2. University Partnerships**

```sql
SELECT url, content_digest, warc_filename
FROM "ccindex"."ccindex"
WHERE crawl = 'CC-MAIN-2024-10'
AND (
    url_host_name LIKE '%.edu%' OR
    url_host_name LIKE '%.ac.%' OR
    url_host_name LIKE '%.uni.%' OR
    url_host_name LIKE '%.university.%'
)
AND (
    content LIKE '%partnership%China%university%' OR
    content LIKE '%cooperation%China%academic%' OR
    content LIKE '%exchange%China%student%' OR
    content LIKE '%collaboration%China%research%'
)
```

### **3. Government Agreements**

```sql
SELECT url, content_digest, warc_filename
FROM "ccindex"."ccindex"
WHERE crawl = 'CC-MAIN-2024-10'
AND (
    url_host_name LIKE '%.gov.%' OR
    url_host_name LIKE '%.mfa.%' OR
    url_host_name LIKE '%.foreign.%'
)
AND (
    content LIKE '%memorandum%China%' OR
    content LIKE '%agreement%China%' OR
    content LIKE '%treaty%China%' OR
    content LIKE '%protocol%China%'
)
AND content_type = 'text/html'
```

---

## 📋 Country-Specific Implementation

### **Germany (DE)**
```sql
-- German government and municipal sites
WHERE (
    url_host_name LIKE '%.gov.de%' OR
    url_host_name LIKE '%.stadt.%' OR
    url_host_name LIKE '%.city.de%'
)
AND (
    content LIKE '%China%Abkommen%' OR
    content LIKE '%China%Vereinbarung%' OR
    content LIKE '%China%Kooperation%' OR
    content LIKE '%Städtepartnerschaft%China%'
)
```

### **France (FR)**
```sql
-- French government and municipal sites
WHERE (
    url_host_name LIKE '%.gouv.fr%' OR
    url_host_name LIKE '%.ville.%' OR
    url_host_name LIKE '%.mairie.%'
)
AND (
    content LIKE '%Chine%accord%' OR
    content LIKE '%Chine%coopération%' OR
    content LIKE '%ville jumelée%Chine%'
)
```

### **Italy (IT)**
```sql
-- Italian government and municipal sites
WHERE (
    url_host_name LIKE '%.gov.it%' OR
    url_host_name LIKE '%.comune.%' OR
    url_host_name LIKE '%.city.it%'
)
AND (
    content LIKE '%Cina%accordo%' OR
    content LIKE '%Cina%cooperazione%' OR
    content LIKE '%città gemelle%Cina%'
)
```

---

## 🛠️ Practical Implementation Script

### **Python Implementation for Bilateral Agreement Discovery**

```python
#!/usr/bin/env python3
"""
Common Crawl EU-China Agreements Harvester
Production implementation for discovering bilateral agreements
"""

import boto3
import pandas as pd
import requests
import gzip
import json
from datetime import datetime
from pathlib import Path

class CommonCrawlAgreementHarvester:
    def __init__(self, output_dir='common_crawl_results'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Setup AWS Athena (requires AWS credentials)
        self.athena_client = boto3.client('athena', region_name='us-east-1')
        self.s3_client = boto3.client('s3')

    def query_sister_cities(self, crawl_id='CC-MAIN-2024-10'):
        """Query Common Crawl for sister city agreements"""

        query = f"""
        SELECT url, content_digest, warc_filename, warc_record_offset
        FROM "ccindex"."ccindex"
        WHERE crawl = '{crawl_id}'
        AND (
            url_host_name LIKE '%.gov.%' OR
            url_host_name LIKE '%.city.%' OR
            url_host_name LIKE '%.municipality.%' OR
            url_host_name LIKE '%.comune.%' OR
            url_host_name LIKE '%.ville.%' OR
            url_host_name LIKE '%.stadt.%'
        )
        AND (
            content LIKE '%sister city%China%' OR
            content LIKE '%twin city%China%' OR
            content LIKE '%Städtepartnerschaft%China%' OR
            content LIKE '%ville jumelée%Chine%' OR
            content LIKE '%città gemelle%Cina%' OR
            content LIKE '%ciudades hermanas%China%'
        )
        LIMIT 1000;
        """

        return self._execute_athena_query(query, 'sister_cities')

    def query_university_partnerships(self, crawl_id='CC-MAIN-2024-10'):
        """Query Common Crawl for university partnerships"""

        query = f"""
        SELECT url, content_digest, warc_filename, warc_record_offset
        FROM "ccindex"."ccindex"
        WHERE crawl = '{crawl_id}'
        AND (
            url_host_name LIKE '%.edu%' OR
            url_host_name LIKE '%.ac.%' OR
            url_host_name LIKE '%.uni.%' OR
            url_host_name LIKE '%.university.%'
        )
        AND (
            content LIKE '%partnership%China%university%' OR
            content LIKE '%cooperation%China%academic%' OR
            content LIKE '%exchange%China%student%' OR
            content LIKE '%collaboration%China%research%'
        )
        LIMIT 500;
        """

        return self._execute_athena_query(query, 'university_partnerships')

    def query_government_agreements(self, crawl_id='CC-MAIN-2024-10'):
        """Query Common Crawl for government agreements"""

        query = f"""
        SELECT url, content_digest, warc_filename, warc_record_offset
        FROM "ccindex"."ccindex"
        WHERE crawl = '{crawl_id}'
        AND (
            url_host_name LIKE '%.gov.%' OR
            url_host_name LIKE '%.mfa.%' OR
            url_host_name LIKE '%.foreign.%'
        )
        AND (
            content LIKE '%memorandum%China%' OR
            content LIKE '%agreement%China%' OR
            content LIKE '%treaty%China%' OR
            content LIKE '%protocol%China%'
        )
        LIMIT 300;
        """

        return self._execute_athena_query(query, 'government_agreements')

    def _execute_athena_query(self, query, query_type):
        """Execute Athena query and return results"""
        try:
            # Start query execution
            response = self.athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={'Database': 'ccindex'},
                ResultConfiguration={
                    'OutputLocation': f's3://your-athena-results-bucket/{query_type}/'
                }
            )

            query_execution_id = response['QueryExecutionId']

            # Wait for completion (simplified - should add proper polling)
            # In production, implement proper status checking

            return query_execution_id

        except Exception as e:
            print(f"Athena query failed for {query_type}: {e}")
            return None

    def fetch_warc_content(self, warc_filename, warc_record_offset):
        """Fetch actual content from WARC file"""
        try:
            # Download WARC record from Common Crawl S3
            s3_key = f"crawl-data/{warc_filename}"

            # Use range request to get specific record
            response = self.s3_client.get_object(
                Bucket='commoncrawl',
                Key=s3_key,
                Range=f'bytes={warc_record_offset}-{warc_record_offset + 10000}'
            )

            # Parse WARC record (simplified)
            content = response['Body'].read()
            return content.decode('utf-8', errors='ignore')

        except Exception as e:
            print(f"Failed to fetch WARC content: {e}")
            return None

    def extract_agreements_from_content(self, content, url):
        """Extract agreement information from page content"""
        agreements = []

        # Simple pattern matching (should be enhanced with NLP)
        patterns = [
            r'sister city.*?China',
            r'twin city.*?China',
            r'partnership.*?China',
            r'agreement.*?China',
            r'memorandum.*?China'
        ]

        import re
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                agreements.append({
                    'url': url,
                    'extracted_text': match,
                    'extraction_method': 'regex_pattern',
                    'confidence': 'medium',
                    'requires_verification': True
                })

        return agreements

    def harvest_all_agreement_types(self):
        """Execute comprehensive harvest across all agreement types"""
        print("Starting Common Crawl bilateral agreements harvest...")

        results = {
            'sister_cities': self.query_sister_cities(),
            'university_partnerships': self.query_university_partnerships(),
            'government_agreements': self.query_government_agreements()
        }

        # Save query IDs for later result retrieval
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(self.output_dir / f'query_ids_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Queries submitted. Results will be available in S3.")
        print(f"Query IDs saved to: query_ids_{timestamp}.json")

        return results

# Alternative: Using cdx-toolkit for simpler access
def simple_common_crawl_search():
    """Simplified Common Crawl search using cdx-toolkit"""
    try:
        from cdx_toolkit import CDXFetcher

        cdx = CDXFetcher(source='cc')

        queries = [
            'site:*.gov.* sister city China',
            'site:*.edu* partnership China university',
            'site:*.ac.* cooperation China academic'
        ]

        results = []
        for query in queries:
            print(f"Searching: {query}")

            for record in cdx.iter(query, from_ts='20200101', to_ts='20241201', limit=100):
                results.append({
                    'url': record.url,
                    'timestamp': record.timestamp,
                    'status': record.status,
                    'query': query
                })

        return results

    except ImportError:
        print("cdx-toolkit not installed. Run: pip install cdx-toolkit")
        return []

if __name__ == "__main__":
    # For quick testing without AWS setup
    results = simple_common_crawl_search()
    print(f"Found {len(results)} potential agreement pages")

    # For production with AWS Athena
    # harvester = CommonCrawlAgreementHarvester()
    # harvester.harvest_all_agreement_types()
```

---

## 📊 Expected Results from Common Crawl

### **Sister Cities (High Probability)**
- **Municipal websites** with partnership announcements
- **City council minutes** documenting partnership agreements
- **Sister city association pages** with partnership lists
- **Historical agreements** no longer on current websites

### **University Partnerships (Medium Probability)**
- **International office pages** with China partnerships
- **News releases** about cooperation agreements
- **Faculty exchange program announcements**
- **Research collaboration documentation**

### **Government Agreements (Lower Volume, Higher Quality)**
- **Official press releases** about bilateral agreements
- **Treaty publication pages**
- **Diplomatic mission announcements**
- **Trade cooperation frameworks**

---

## 🎯 Implementation Recommendation

### **Phase 1: Simple CDX Search**
1. Use `cdx-toolkit` for initial exploration
2. Test query patterns on recent crawls
3. Validate content quality and relevance
4. Refine search terms based on results

### **Phase 2: Production Athena Queries**
1. Set up AWS account with Athena access
2. Implement structured SQL queries
3. Process WARC files for full content
4. Extract and validate agreement information

### **Phase 3: Content Processing**
1. NLP extraction of agreement details
2. Cross-reference with official sources
3. Build comprehensive agreement database
4. Implement verification workflows

**Common Crawl provides access to the deep web content where bilateral agreements are actually documented, bypassing the limitations of real-time web scraping.**
