# Skills & Technology Learning Roadmap
## How to Build an OSINT Intelligence Analysis System from Scratch

**Project Context:** OSINT Foresight Framework
- **Scale:** 1.2TB data, 101.3M records, 739 scripts, 210 database tables
- **Scope:** Multi-country intelligence analysis tracking China's technology activities
- **Complexity:** Enterprise-grade data engineering + intelligence analysis

**Target Audience:** Someone wanting to replicate or understand this work

---

## 📚 Learning Path Overview

### Beginner → Intermediate → Advanced → Expert
**Estimated Time:** 12-18 months of dedicated study + hands-on practice
**Prerequisites:** Basic computer skills, logical thinking, willingness to learn

---

## 1. 🐍 Python Programming (CRITICAL - 40% of project)

### Why We Need It
- **Primary language** for all data processing (739 Python scripts)
- ETL pipelines, API interactions, data validation
- Text processing, entity detection, intelligence analysis

### Beginner Level (2-3 months)
**Topics:**
- Python basics (variables, data types, control flow)
- Functions and modules
- File I/O (reading/writing files)
- String manipulation
- Lists, dictionaries, sets
- Exception handling (try/except)
- Working with paths (pathlib)

**Specific to Our Project:**
```python
# File handling (we process 52,030 XML files)
with open('data.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# String operations (entity detection)
name_lower = name.lower()
if 'huawei' in name_lower:
    return True

# Path operations (organizing 1.2TB data)
from pathlib import Path
data_dir = Path('F:/TED_Data')
for file in data_dir.rglob('*.xml'):
    process_file(file)
```

**Resources:**
- Book: "Python Crash Course" by Eric Matthes
- Course: Codecademy Python 3
- Practice: Process small XML files, read/write CSV

### Intermediate Level (3-4 months)
**Topics:**
- Object-oriented programming (classes)
- Regular expressions (regex)
- JSON/XML parsing
- External libraries (requests, lxml, pandas)
- Command-line arguments (argparse)
- Logging
- Virtual environments

**Specific to Our Project:**
```python
# Regex for entity detection
import re
pattern = r'\b(huawei|zte|alibaba)\b'
if re.search(pattern, text, re.IGNORECASE):
    detected = True

# XML parsing (52,030 XML files processed)
from lxml import etree
tree = etree.parse('ted_contract.xml')
title = tree.xpath('//TITLE/text()')[0]

# JSON handling (3,038 JSON files)
import json
with open('openalex_work.json', 'r') as f:
    data = json.load(f)

# Class-based processors
class USAspendingProcessor:
    def __init__(self):
        self.patterns = {...}

    def process(self, file):
        # Processing logic
        pass
```

**Resources:**
- Book: "Automate the Boring Stuff with Python"
- Course: Real Python (realpython.com)
- Practice: Parse TED XML samples, extract entities

### Advanced Level (3-4 months)
**Topics:**
- Multiprocessing/threading (parallel processing)
- Database interactions (sqlite3, SQLAlchemy)
- Large file handling (streaming, generators)
- Memory optimization
- Progress bars (tqdm)
- Checkpointing (resume interrupted processing)
- Data validation frameworks

**Specific to Our Project:**
```python
# Multiprocessing (process 422GB OpenAlex data)
from multiprocessing import Pool
with Pool(processes=8) as pool:
    results = pool.map(process_file, file_list)

# Database operations (101.3M records)
import sqlite3
conn = sqlite3.connect('osint_master.db')
cursor = conn.cursor()
cursor.execute('INSERT INTO ted_contracts VALUES (?, ?, ?)',
               (notice_num, title, value))
conn.commit()

# Streaming large files (not loading all in memory)
def read_large_file(filepath):
    with open(filepath, 'r') as f:
        for line in f:  # Read line by line
            yield process_line(line)

# Checkpointing (resume processing)
import json
checkpoint = {'last_file': file_path, 'processed_count': 1000}
with open('checkpoint.json', 'w') as f:
    json.dump(checkpoint, f)
```

**Resources:**
- Book: "Fluent Python" by Luciano Ramalho
- Course: Real Python advanced courses
- Practice: Build ETL pipeline for sample dataset

### Expert Level (2-3 months)
**Topics:**
- Performance profiling
- Memory profiling
- Async programming (asyncio)
- Package distribution
- Testing frameworks (pytest)
- Documentation (docstrings, Sphinx)

**Specific to Our Project:**
```python
# Performance profiling
import cProfile
cProfile.run('process_all_files()')

# Testing (31+ unit tests in project)
import pytest
def test_chinese_detection():
    processor = ChineseDetector()
    assert processor.is_chinese('Huawei') == True
    assert processor.is_chinese('Boeing') == False

# Async for API calls
import asyncio
import aiohttp
async def fetch_openalex_data(work_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

**Resources:**
- Book: "High Performance Python"
- Course: Talk Python Advanced Courses
- Practice: Optimize slow processing scripts

**Python Libraries We Use:**
- **Core:** os, pathlib, json, xml, re, datetime, time
- **Data:** pandas, numpy, sqlite3
- **Web:** requests, urllib, aiohttp
- **Parsing:** lxml, BeautifulSoup4, xmltodict
- **Progress:** tqdm
- **Text:** langdetect, difflib
- **Visualization:** matplotlib, networkx
- **Office:** openpyxl (Excel), python-docx (Word), python-pptx (PowerPoint)
- **PDF:** PyMuPDF (fitz)

---

## 2. 🗄️ SQL & Database Management (CRITICAL - 25% of project)

### Why We Need It
- Store and query 101.3M records across 210 tables
- Cross-source intelligence analysis
- Fast lookups and aggregations

### Beginner Level (2-3 months)
**Topics:**
- SQL basics (SELECT, WHERE, ORDER BY, LIMIT)
- INSERT, UPDATE, DELETE
- Basic aggregations (COUNT, SUM, AVG, MAX, MIN)
- JOIN operations (INNER, LEFT, RIGHT)
- GROUP BY and HAVING
- Database design basics (primary keys, foreign keys)

**Specific to Our Project:**
```sql
-- Count Chinese entities in TED data
SELECT COUNT(*)
FROM ted_contracts_production
WHERE is_chinese_related = 1;

-- Find high-value contracts
SELECT notice_number, title, value_eur
FROM ted_contracts_production
WHERE value_eur > 1000000
ORDER BY value_eur DESC
LIMIT 100;

-- Cross-source analysis (JOIN)
SELECT
    t.contractor_name,
    COUNT(DISTINCT t.notice_number) as contracts,
    COUNT(DISTINCT p.patent_number) as patents
FROM ted_contractors t
LEFT JOIN uspto_patents_chinese p
    ON t.contractor_name LIKE '%' || p.assignee_name || '%'
GROUP BY t.contractor_name;
```

**Resources:**
- Course: Khan Academy SQL
- Book: "SQL in 10 Minutes"
- Practice: Query sample TED contracts

### Intermediate Level (2-3 months)
**Topics:**
- Subqueries and CTEs (WITH clause)
- Window functions (ROW_NUMBER, RANK, LAG)
- Indexes (CREATE INDEX)
- Views (CREATE VIEW)
- Transactions (BEGIN, COMMIT, ROLLBACK)
- NULL handling
- Date/time functions

**Specific to Our Project:**
```sql
-- CTE for complex analysis
WITH yearly_stats AS (
    SELECT
        SUBSTR(publication_date, 1, 4) as year,
        COUNT(*) as total,
        SUM(CASE WHEN is_chinese_related = 1 THEN 1 ELSE 0 END) as chinese
    FROM ted_contracts_production
    WHERE publication_date >= '2020-01-01'
    GROUP BY year
)
SELECT
    year,
    total,
    chinese,
    ROUND(100.0 * chinese / total, 2) as chinese_percentage
FROM yearly_stats
ORDER BY year DESC;

-- Create index for performance (critical!)
CREATE INDEX idx_ted_publication_date
ON ted_contracts_production(publication_date);

-- Window function for ranking
SELECT
    country_code,
    contractor_name,
    value_eur,
    ROW_NUMBER() OVER (PARTITION BY country_code ORDER BY value_eur DESC) as rank
FROM ted_contracts_production;
```

**Resources:**
- Course: Mode Analytics SQL Tutorial (Advanced)
- Book: "Learning SQL" by Alan Beaulieu
- Practice: Build queries for TED + USPTO cross-reference

### Advanced Level (2-3 months)
**Topics:**
- Query optimization (EXPLAIN QUERY PLAN)
- Database normalization
- Schema design for large datasets
- VACUUM and ANALYZE (maintenance)
- Compound indexes
- Full-text search (FTS5)
- SQLite-specific features
- Database migration strategies

**Specific to Our Project:**
```sql
-- Query optimization
EXPLAIN QUERY PLAN
SELECT * FROM ted_contracts_production
WHERE publication_date >= '2024-01-01'
AND is_chinese_related = 1;

-- Database maintenance (30-40% speedup)
VACUUM;
ANALYZE;

-- Full-text search for contract titles
CREATE VIRTUAL TABLE ted_fts USING fts5(
    notice_number,
    title,
    description
);

-- Complex data quality check
SELECT
    table_name,
    COUNT(*) as records,
    SUM(CASE WHEN critical_field IS NULL THEN 1 ELSE 0 END) as null_count
FROM (
    SELECT 'ted' as table_name, notice_number as critical_field FROM ted_contracts_production
    UNION ALL
    SELECT 'uspto', patent_number FROM uspto_patents_chinese
)
GROUP BY table_name;
```

**Resources:**
- Book: "SQL Performance Explained"
- SQLite documentation (sqlite.org)
- Practice: Optimize slow queries, design schema for new data source

**SQL Skills Summary:**
- **Querying:** SELECT with complex WHERE, JOINs across 5+ tables
- **Aggregation:** GROUP BY with HAVING, window functions
- **Performance:** Indexing strategy (6 indexes added this session)
- **Maintenance:** VACUUM, ANALYZE, backup procedures
- **Design:** Normalized schemas, relationship mapping
- **Data Types:** Text, integers, floats, dates, JSON fields

---

## 3. 📊 Data Engineering & ETL (CRITICAL - 20% of project)

### Why We Need It
- Process 1.2TB of raw data into structured intelligence
- Handle multiple data formats (XML, JSON, CSV, PDF, Excel)
- Build reliable pipelines that can resume after failures

### Beginner Level (2-3 months)
**Topics:**
- ETL concept (Extract, Transform, Load)
- File format basics (CSV, JSON, XML)
- Data cleaning (handling NULLs, duplicates)
- Basic transformations (string cleanup, date parsing)
- Data validation

**Specific to Our Project:**
```python
# Extract: Read from source
with open('ted_contract.xml', 'r') as f:
    raw_data = f.read()

# Transform: Clean and structure
from lxml import etree
tree = etree.fromstring(raw_data)
cleaned_data = {
    'notice_number': tree.xpath('//NOTICE_NUMBER/text()')[0],
    'title': tree.xpath('//TITLE/text()')[0].strip(),
    'value': float(tree.xpath('//VALUE/@AMOUNT')[0])
}

# Load: Insert into database
cursor.execute('''
    INSERT INTO ted_contracts (notice_number, title, value_eur)
    VALUES (?, ?, ?)
''', (cleaned_data['notice_number'], cleaned_data['title'], cleaned_data['value']))
conn.commit()
```

**Resources:**
- Course: DataCamp Data Engineering track
- Book: "Data Engineering with Python"
- Practice: Build ETL for small dataset (100 files)

### Intermediate Level (3-4 months)
**Topics:**
- Batch processing
- Error handling and retry logic
- Checkpointing (resume processing)
- Data deduplication
- Schema validation
- Logging and monitoring
- Progress tracking

**Specific to Our Project:**
```python
# Batch processing with checkpointing
import json
from pathlib import Path

def process_batch(files, checkpoint_file):
    # Load checkpoint
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
            last_file = checkpoint.get('last_file')
            processed_count = checkpoint.get('processed_count', 0)
    else:
        last_file = None
        processed_count = 0

    # Resume from checkpoint
    start_processing = (last_file is None)

    for file in files:
        if not start_processing:
            if str(file) == last_file:
                start_processing = True
            continue

        try:
            # Process file
            process_ted_file(file)
            processed_count += 1

            # Update checkpoint every 100 files
            if processed_count % 100 == 0:
                with open(checkpoint_file, 'w') as f:
                    json.dump({
                        'last_file': str(file),
                        'processed_count': processed_count
                    }, f)

        except Exception as e:
            print(f"Error processing {file}: {e}")
            # Log error but continue

# Data deduplication
def deduplicate_records(conn):
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM ted_contracts
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM ted_contracts
            GROUP BY notice_number
        )
    ''')
    deleted = cursor.rowcount
    print(f"Removed {deleted:,} duplicate records")
```

**Resources:**
- Book: "Data Pipelines Pocket Reference"
- Udemy: Building ETL Pipelines with Python
- Practice: Build fault-tolerant pipeline for TED data

### Advanced Level (3-4 months)
**Topics:**
- Parallel processing (multiprocessing)
- Stream processing (generators, iterators)
- Large file handling (chunking)
- Memory-efficient algorithms
- Data quality frameworks
- Schema evolution
- Incremental updates (delta processing)

**Specific to Our Project:**
```python
# Parallel processing (8 workers for 422GB OpenAlex)
from multiprocessing import Pool, Queue
import os

def process_openalex_file(filepath):
    """Process single OpenAlex .gz file"""
    import gzip
    import json

    results = []
    with gzip.open(filepath, 'rt') as f:
        for line in f:
            work = json.loads(line)
            if is_relevant(work):
                results.append(extract_data(work))
    return results

def parallel_pipeline(file_list, num_workers=8):
    with Pool(processes=num_workers) as pool:
        # Process files in parallel
        results = pool.map(process_openalex_file, file_list)

    # Flatten results and load to database
    all_records = [item for sublist in results for item in sublist]
    bulk_insert_to_db(all_records)

# Stream processing (memory-efficient)
def stream_large_file(filepath):
    """Process 49GB log file without loading into memory"""
    with open(filepath, 'r') as f:
        for line in f:
            yield process_log_line(line)

# Chunked reading
def process_huge_csv(filepath, chunksize=10000):
    """Process large CSV in chunks"""
    import pandas as pd

    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        # Process chunk
        cleaned = clean_chunk(chunk)
        # Load to database
        chunk.to_sql('table_name', conn, if_exists='append', index=False)

# Incremental updates (only process new data)
def incremental_update(source_dir, last_processed_date):
    """Only process files modified after last run"""
    from datetime import datetime

    for file in source_dir.rglob('*.xml'):
        file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if file_mtime > last_processed_date:
            process_file(file)
```

**Resources:**
- Book: "Designing Data-Intensive Applications"
- Course: Coursera Data Engineering
- Practice: Build parallel processor for USPTO patents

**Data Engineering Skills Summary:**
- **Formats Handled:** XML (52K files), JSON (3K files), PDF (1.5K files), CSV, Excel, NDJSON
- **Scale:** 1.2TB processed, 101.3M records
- **Reliability:** Checkpointing every 100 files, error handling, retry logic
- **Performance:** 8-core parallel processing, streaming for large files
- **Quality:** NULL handling, deduplication, validation frameworks

---

## 4. 🔍 Text Processing & Entity Detection (IMPORTANT - 15% of project)

### Why We Need It
- Detect Chinese entities from messy text data
- Extract companies, locations, technologies from documents
- Handle multilingual text (40 European languages + Chinese)

### Beginner Level (2 months)
**Topics:**
- String operations (lower(), strip(), split())
- String searching (in, find(), startswith())
- Basic regex (literal matching)
- Word boundaries

**Specific to Our Project:**
```python
# Basic entity detection
def is_chinese_company(name):
    name_lower = name.lower()
    chinese_keywords = ['huawei', 'zte', 'alibaba', 'tencent', 'baidu']

    for keyword in chinese_keywords:
        if keyword in name_lower:
            return True
    return False

# Word boundary checking
def has_chinese_name(text):
    text_lower = text.lower()

    # False positive check
    if 'china town' in text_lower:
        return False

    # Actual detection
    chinese_patterns = ['beijing', 'shanghai', 'shenzhen', 'china']
    for pattern in chinese_patterns:
        if pattern in text_lower:
            return True
    return False
```

**Resources:**
- Tutorial: Python String Methods (docs.python.org)
- Practice: Detect companies in sample TED contracts

### Intermediate Level (3 months)
**Topics:**
- Regular expressions (advanced)
- Pattern matching
- Character encoding (UTF-8, Unicode)
- Normalization (accents, spacing)
- Language detection
- Named entity recognition (basic)

**Specific to Our Project:**
```python
import re

# Regex for entity detection
def detect_chinese_entity_regex(text):
    """Detect Chinese entities with word boundaries"""
    text_lower = text.lower()

    # Pattern with word boundaries
    patterns = [
        r'\b(huawei|zte|alibaba|tencent|baidu)\b',
        r'\b(beijing|shanghai|shenzhen|guangzhou)\b',
        r'\bchina\s+(telecom|mobile|unicom)\b'
    ]

    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False

# Normalization (handle "H u a w e i" obfuscation)
def normalize_text(text):
    """Remove spaces to catch spaced obfuscation"""
    # "H u a w e i" becomes "huawei"
    normalized = re.sub(r'\s+', '', text.lower())
    return normalized

def has_chinese_name_normalized(text):
    text_norm = normalize_text(text)
    patterns_norm = [normalize_text(p) for p in ['huawei', 'zte']]

    for pattern in patterns_norm:
        if len(pattern) >= 5 and pattern in text_norm:
            return True
    return False

# Language detection
from langdetect import detect

def is_chinese_language(text):
    try:
        lang = detect(text)
        return lang in ['zh-cn', 'zh-tw']
    except:
        return False

# Extract entities
def extract_companies(text):
    """Extract company names from text"""
    # Pattern for "Ltd", "Inc", "Corp"
    company_pattern = r'([A-Z][A-Za-z\s&]+(?:Ltd|Inc|Corp|Company|GmbH|SAS|SpA)\.?)'
    companies = re.findall(company_pattern, text)
    return [c.strip() for c in companies]
```

**Resources:**
- Website: regex101.com (practice regex)
- Book: "Mastering Regular Expressions"
- Course: DataCamp Text Mining with Python
- Practice: Detect entities in multilingual TED contracts

### Advanced Level (3 months)
**Topics:**
- NLP (Natural Language Processing)
- Named Entity Recognition (NER)
- Text classification
- Fuzzy matching (Levenshtein distance)
- Confidence scoring
- False positive filtering

**Specific to Our Project:**
```python
# Confidence scoring
def detect_with_confidence(text, name, country):
    """Detect Chinese entity with confidence score"""
    confidence = 0.0
    indicators = []

    # Country code (highest confidence)
    if country and country.upper() in ['CHN', 'CN', 'CHINA']:
        confidence = 0.9
        indicators.append('country_code_china')

    # Chinese company name (medium confidence)
    elif has_chinese_company_name(name):
        confidence = 0.6
        indicators.append('chinese_company_name')

    # Description mentions China (low confidence)
    elif 'made in china' in text.lower():
        confidence = 0.3
        indicators.append('china_mentioned_in_description')

    if confidence > 0:
        return {
            'is_chinese': True,
            'confidence': confidence,
            'indicators': indicators
        }
    return None

# Fuzzy matching for entity matching across sources
from difflib import SequenceMatcher

def fuzzy_match(str1, str2, threshold=0.85):
    """Check if two strings are similar enough"""
    ratio = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return ratio >= threshold

# Example: Match TED contractor to USPTO assignee
ted_name = "Huawei Technologies Co Ltd"
uspto_name = "Huawei Technologies Company Limited"
if fuzzy_match(ted_name, uspto_name):
    print("Same entity detected across sources")

# False positive filtering
FALSE_POSITIVES = {
    'china town', 'china beach', 'china garden',
    'china king restaurant', 'great wall restaurant'
}

def filter_false_positives(text):
    text_lower = text.lower()
    for fp in FALSE_POSITIVES:
        if fp in text_lower:
            return False
    return True
```

**Resources:**
- Library: spaCy (NLP library)
- Course: Coursera NLP Specialization
- Book: "Natural Language Processing with Python"
- Practice: Build entity matcher for cross-source analysis

**Text Processing Skills Summary:**
- **Entity Detection:** Chinese companies, locations, technologies
- **Languages:** 40 European languages + Chinese
- **Techniques:** Regex, NLP, fuzzy matching, confidence scoring
- **Validation:** False positive filtering, manual review samples
- **Scale:** 1.13M TED contracts, 425K USPTO patents processed

---

## 5. 🌐 Web Scraping & APIs (IMPORTANT - 10% of project)

### Why We Need It
- Collect data from TED, OpenAlex, USAspending, USPTO
- Download reports from think tanks
- Access government APIs

### Beginner Level (2 months)
**Topics:**
- HTTP basics (GET, POST requests)
- Requests library
- JSON APIs
- Rate limiting
- Error handling

**Specific to Our Project:**
```python
import requests
import time

# Simple API call (OpenAlex)
def fetch_openalex_work(work_id):
    url = f'https://api.openalex.org/works/{work_id}'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# USAspending API
def fetch_usaspending_contracts(year):
    url = 'https://api.usaspending.gov/api/v2/search/spending_by_award/'
    payload = {
        'filters': {
            'time_period': [{'start_date': f'{year}-01-01', 'end_date': f'{year}-12-31'}]
        }
    }

    response = requests.post(url, json=payload)
    return response.json()

# Rate limiting (respectful scraping)
def fetch_with_rate_limit(urls, requests_per_second=2):
    delay = 1.0 / requests_per_second
    results = []

    for url in urls:
        response = requests.get(url)
        results.append(response.json())
        time.sleep(delay)  # Be nice to servers

    return results
```

**Resources:**
- Tutorial: Real Python Web Scraping guide
- Course: Udemy Web Scraping with Python
- Practice: Fetch OpenAlex works via API

### Intermediate Level (3 months)
**Topics:**
- HTML parsing (BeautifulSoup)
- XML parsing (lxml)
- Selenium (browser automation)
- Download management
- Retry logic
- Session management

**Specific to Our Project:**
```python
from bs4 import BeautifulSoup
import requests

# HTML scraping (think tank reports)
def scrape_thinktank_reports(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all PDF links
    reports = []
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pdf'):
            reports.append({
                'title': link.text.strip(),
                'url': link['href']
            })

    return reports

# Download with retry logic
def download_with_retry(url, filepath, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"Downloaded: {filepath}")
            return True

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))  # Exponential backoff

    return False

# Selenium for JavaScript-heavy sites
from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_dynamic_content(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)  # Wait for JavaScript to load

    # Extract content
    elements = driver.find_elements(By.CLASS_NAME, 'report-link')
    reports = [elem.text for elem in elements]

    driver.quit()
    return reports
```

**Resources:**
- Library: requests, BeautifulSoup4, Selenium
- Course: DataCamp Web Scraping
- Practice: Scrape think tank websites for reports

### Advanced Level (2 months)
**Topics:**
- Async requests (aiohttp)
- Concurrent downloading
- API pagination
- Authentication (API keys, OAuth)
- Bulk data downloads
- Download verification (checksums)

**Specific to Our Project:**
```python
import asyncio
import aiohttp

# Async downloading (faster for many files)
async def download_file_async(session, url, filepath):
    async with session.get(url) as response:
        if response.status == 200:
            content = await response.read()
            with open(filepath, 'wb') as f:
                f.write(content)
            return True
        return False

async def download_many_files(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [download_file_async(session, url, f'file_{i}.pdf')
                 for i, url in enumerate(urls)]
        results = await asyncio.gather(*tasks)
    return results

# Run async downloads
urls = [...]  # List of 1000+ PDF URLs
asyncio.run(download_many_files(urls))

# API pagination (handle large result sets)
def fetch_all_pages(base_url):
    all_results = []
    page = 1

    while True:
        response = requests.get(f'{base_url}?page={page}')
        data = response.json()

        if not data['results']:
            break  # No more pages

        all_results.extend(data['results'])
        page += 1
        time.sleep(1)  # Rate limiting

    return all_results

# Download verification (MD5 checksums)
import hashlib

def verify_download(filepath, expected_md5):
    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash == expected_md5
```

**Resources:**
- Library: aiohttp, asyncio
- Course: Real Python Async IO
- Practice: Build async downloader for TED archives

**Web Scraping & API Skills Summary:**
- **Data Sources:** TED, OpenAlex, USAspending, USPTO, think tanks
- **Techniques:** REST APIs, HTML scraping, Selenium, async downloads
- **Scale:** 140 TED archives (28GB), 2,938 OpenAlex files (422GB)
- **Reliability:** Retry logic, rate limiting, checksum verification

---

## 6. 📈 Data Analysis & Intelligence (IMPORTANT - 10% of project)

### Why We Need It
- Extract intelligence from 101.3M records
- Identify trends and patterns
- Cross-source validation

### Beginner Level (2 months)
**Topics:**
- Pandas basics (DataFrames)
- Data aggregation (groupby)
- Filtering and sorting
- Basic statistics (mean, median, percentile)
- Data visualization (matplotlib)

**Specific to Our Project:**
```python
import pandas as pd
import sqlite3

# Load data from database
conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
df = pd.read_sql_query("""
    SELECT country_code, value_eur, publication_date
    FROM ted_contracts_production
    WHERE is_chinese_related = 1
""", conn)

# Aggregation
country_stats = df.groupby('country_code').agg({
    'value_eur': ['sum', 'mean', 'count']
}).reset_index()

# Visualization
import matplotlib.pyplot as plt

country_stats.plot(x='country_code', y='value_eur_sum', kind='bar')
plt.title('Chinese TED Contracts by Country')
plt.xlabel('Country')
plt.ylabel('Total Value (EUR)')
plt.savefig('analysis.png')
```

**Resources:**
- Course: DataCamp Pandas Fundamentals
- Book: "Python for Data Analysis" by Wes McKinney
- Practice: Analyze TED contract trends

### Intermediate Level (3 months)
**Topics:**
- Time series analysis
- Pivot tables
- Cross-source analysis
- Correlation analysis
- Geographic analysis
- Data export (Excel, PowerPoint)

**Specific to Our Project:**
```python
# Time series analysis
df['year'] = pd.to_datetime(df['publication_date']).dt.year
yearly_trend = df.groupby('year')['value_eur'].sum()
yearly_trend.plot(kind='line', title='Chinese TED Contracts Over Time')

# Cross-source analysis (TED + USPTO)
ted_df = pd.read_sql_query("SELECT * FROM ted_contractors WHERE is_chinese_related = 1", conn)
uspto_df = pd.read_sql_query("SELECT * FROM uspto_patents_chinese", conn)

# Find entities in both sources
merged = pd.merge(ted_df, uspto_df,
                  left_on='contractor_name',
                  right_on='assignee_name',
                  how='inner')

print(f"Entities found in both TED and USPTO: {len(merged)}")

# Geographic analysis
import folium

def create_map(df):
    m = folium.Map(location=[50, 10], zoom_start=4)

    for _, row in df.iterrows():
        folium.Marker(
            [row['lat'], row['lon']],
            popup=f"{row['contractor_name']}: {row['value_eur']:,.0f} EUR"
        ).add_to(m)

    m.save('contracts_map.html')

# Export to PowerPoint (automated reporting)
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank slide
title = slide.shapes.title
title.text = "Chinese TED Contracts Analysis"

# Add chart
img_path = 'analysis.png'
left = Inches(1)
top = Inches(2)
slide.shapes.add_picture(img_path, left, top, width=Inches(8))

prs.save('intelligence_report.pptx')
```

**Resources:**
- Course: Coursera Applied Data Analysis
- Library: pandas, matplotlib, seaborn, folium
- Practice: Build intelligence report with visualizations

### Advanced Level (3 months)
**Topics:**
- Network analysis
- Entity resolution
- Anomaly detection
- Statistical significance
- Machine learning basics
- Risk scoring

**Specific to Our Project:**
```python
# Network analysis (entity relationships)
import networkx as nx

def build_entity_network(df):
    """Build network of Chinese entities and their connections"""
    G = nx.Graph()

    # Add nodes (entities)
    for entity in df['entity_name'].unique():
        G.add_node(entity)

    # Add edges (connections via projects/contracts)
    for project in df['project_id'].unique():
        entities = df[df['project_id'] == project]['entity_name'].tolist()
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                if G.has_edge(e1, e2):
                    G[e1][e2]['weight'] += 1
                else:
                    G.add_edge(e1, e2, weight=1)

    return G

# Find most connected entities
G = build_entity_network(df)
centrality = nx.degree_centrality(G)
top_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]

# Entity resolution (match entities across sources)
from difflib import SequenceMatcher

def match_entities(source1_names, source2_names, threshold=0.85):
    """Find matching entities across two data sources"""
    matches = []

    for name1 in source1_names:
        for name2 in source2_names:
            similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
            if similarity >= threshold:
                matches.append({
                    'source1': name1,
                    'source2': name2,
                    'similarity': similarity
                })

    return pd.DataFrame(matches)

# Risk scoring
def calculate_risk_score(entity_data):
    """Calculate risk score for entity"""
    score = 0

    # Factor 1: Country (30% weight)
    if entity_data['country'] == 'CHN':
        score += 30

    # Factor 2: Sanctioned entity (50% weight)
    if entity_data['is_sanctioned']:
        score += 50

    # Factor 3: Volume of contracts (20% weight)
    if entity_data['contract_count'] > 10:
        score += 20
    elif entity_data['contract_count'] > 5:
        score += 10

    return min(score, 100)  # Cap at 100

# Anomaly detection
from scipy import stats

def detect_anomalies(df, column='value_eur'):
    """Detect statistical outliers"""
    z_scores = stats.zscore(df[column].dropna())
    anomalies = df[abs(z_scores) > 3]  # > 3 standard deviations
    return anomalies
```

**Resources:**
- Library: networkx, scikit-learn, scipy
- Course: Coursera Machine Learning
- Book: "Data Science for Business"
- Practice: Build entity network analysis for TED + USPTO

**Data Analysis Skills Summary:**
- **Scale:** 101.3M records analyzed
- **Techniques:** Aggregation, time series, cross-source matching, network analysis
- **Visualization:** Charts, maps, PowerPoint reports
- **Intelligence:** Risk scoring, anomaly detection, trend analysis
- **Export:** Excel, PowerPoint, PDF reports

---

## 7. 🚀 Automation & DevOps (MODERATE - 5% of project)

### Why We Need It
- Schedule recurring data collection (weekly, daily)
- Automate intelligence reporting
- Monitor system health

### Beginner Level (1-2 months)
**Topics:**
- Command line basics (bash, cmd)
- Batch scripts (.bat files)
- Scheduled tasks (cron, Task Scheduler)
- Environment variables
- Basic error logging

**Specific to Our Project:**
```bash
# Bash script for automation
#!/bin/bash
# Daily TED processing script

echo "Starting TED processing..."
date

# Run Python processor
python scripts/process_ted_procurement.py --date $(date +%Y-%m-%d)

# Check if successful
if [ $? -eq 0 ]; then
    echo "SUCCESS: Processing complete"
else
    echo "ERROR: Processing failed"
    exit 1
fi

# Backup database
cp F:/OSINT_WAREHOUSE/osint_master.db F:/OSINT_WAREHOUSE/backups/osint_master_$(date +%Y%m%d).db

echo "Script complete"
```

```batch
REM Windows batch script
@echo off
echo Starting weekly intelligence collection...

REM Run Python script
python scripts/automation/intake_scheduler.py --run-weekly

REM Check error level
if %errorlevel% neq 0 (
    echo ERROR: Collection failed
    exit /b 1
)

echo Collection complete
```

**Windows Task Scheduler:**
- Schedule script to run Mondays at 9 AM
- Email on failure
- Log all output

**Resources:**
- Tutorial: Linux command line basics
- Course: Windows PowerShell fundamentals
- Practice: Schedule weekly data collection

### Intermediate Level (2 months)
**Topics:**
- PowerShell scripting
- Git version control
- Log management
- Error handling and alerting
- Process monitoring

**Specific to Our Project:**
```powershell
# PowerShell monitoring script
# Check if automation tasks are running

Get-ScheduledTask -TaskName 'OSINT_*' | ForEach-Object {
    $task = $_
    $info = Get-ScheduledTaskInfo -TaskName $task.TaskName

    Write-Host "$($task.TaskName): $($task.State)"
    Write-Host "  Last Run: $($info.LastRunTime)"
    Write-Host "  Next Run: $($info.NextRunTime)"
    Write-Host "  Last Result: $($info.LastTaskResult)"
    Write-Host ""
}

# Check database size
$dbPath = "F:/OSINT_WAREHOUSE/osint_master.db"
$dbSize = (Get-Item $dbPath).Length / 1GB
Write-Host "Database size: $($dbSize.ToString('F2')) GB"

# Check disk space
$drive = Get-PSDrive -Name F
$freeGB = $drive.Free / 1GB
Write-Host "Free space: $($freeGB.ToString('F2')) GB"

if ($freeGB -lt 100) {
    Write-Host "WARNING: Low disk space!"
    # Send email alert
}
```

```python
# Python logging setup
import logging
from datetime import datetime

# Configure logging
log_file = f'logs/processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.info("Starting TED processing...")
logger.warning("No records found for date 2024-01-15")
logger.error("Failed to process file: corrupted_data.xml")
```

**Git Version Control:**
```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit: OSINT Foresight framework"

# Daily commits
git add scripts/process_ted.py
git commit -m "feat: Add TED UBL eForms parser"
git push origin main

# Branching for features
git checkout -b feature/openalex-integration
# ... make changes ...
git commit -m "feat: Add OpenAlex API integration"
git push origin feature/openalex-integration
```

**Resources:**
- Course: LinkedIn Learning PowerShell
- Book: "Pro Git" (free online)
- Practice: Set up automated backup and monitoring

### Advanced Level (2 months)
**Topics:**
- CI/CD pipelines
- Docker containers
- Automated testing
- Performance monitoring
- Backup automation

**Specific to Our Project:**
```yaml
# GitHub Actions CI/CD (.github/workflows/tests.yml)
name: Run Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run unit tests
      run: |
        pytest tests/unit/ -v

    - name: Run integration tests
      run: |
        pytest tests/integration/ -v

    - name: Run red team validation
      run: |
        python tests/RED_TEAM_VALIDATION.py
```

```python
# Automated backup script
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def automated_backup():
    """Daily database backup with retention policy"""
    db_path = Path('F:/OSINT_WAREHOUSE/osint_master.db')
    backup_dir = Path('F:/OSINT_WAREHOUSE/backups')
    backup_dir.mkdir(exist_ok=True)

    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'osint_master_{timestamp}.db'
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")

    # Retention: Keep daily backups for 7 days, weekly for 4 weeks
    cutoff_daily = datetime.now() - timedelta(days=7)
    cutoff_weekly = datetime.now() - timedelta(weeks=4)

    for backup in backup_dir.glob('osint_master_*.db'):
        backup_date = datetime.strptime(backup.stem.split('_')[-2], '%Y%m%d')

        # Delete old backups
        if backup_date < cutoff_weekly:
            backup.unlink()
            print(f"Deleted old backup: {backup.name}")

if __name__ == "__main__":
    automated_backup()
```

**Resources:**
- Course: Docker for Data Science
- GitHub Actions documentation
- Practice: Set up CI/CD pipeline for testing

**Automation Skills Summary:**
- **Scheduled Tasks:** 7 active (Windows Task Scheduler)
- **Monitoring:** Database size, disk space, task status
- **Version Control:** Git for 739 scripts
- **Logging:** Structured logging for all processors
- **Backup:** Automated daily backups with retention

---

## 8. 🛠️ Domain-Specific Knowledge (CRITICAL - 10% of project)

### Intelligence Analysis Fundamentals
**Topics:**
- Open-source intelligence (OSINT) methodology
- Entity attribution
- Cross-source verification
- Confidence scoring
- Intelligence reporting

**Specific to Our Project:**
- Leonardo compliance standard (intelligence validation)
- Multi-source validation (TED + USPTO + OpenAlex)
- Zero fabrication protocol
- Confidence levels (0.3 = low, 0.6 = medium, 0.9 = high)

**Resources:**
- Book: "Open Source Intelligence Techniques" by Michael Bazzell
- Course: SANS FOR578 Cyber Threat Intelligence
- Practice: Build intelligence report with confidence scores

### Data Governance & Compliance
**Topics:**
- Data provenance (tracking data sources)
- Audit trails
- Data retention policies
- Privacy considerations (GDPR)

**Specific to Our Project:**
- Source attribution for every record
- Processing timestamps
- Verification procedures
- Documentation requirements

### Domain Knowledge: European Procurement
**Topics:**
- TED (Tenders Electronic Daily) system
- EU procurement regulations
- UBL (Universal Business Language) format
- eForms standard

**Resources:**
- TED documentation (ted.europa.eu)
- EU procurement directives

### Domain Knowledge: Patents
**Topics:**
- Patent classifications (CPC, IPC)
- USPTO structure
- Patent assignees vs inventors
- Technology classifications

**Resources:**
- USPTO documentation
- PatentsView API documentation

### Domain Knowledge: Academic Research
**Topics:**
- OpenAlex data model
- DOI (Digital Object Identifier)
- Research collaboration patterns
- Academic institutions

**Resources:**
- OpenAlex documentation (docs.openalex.org)
- Understanding research metrics

---

## 9. 📖 Supporting Skills (5% each)

### A. XML & Data Formats
**Why:** Process 52,030 XML files (TED contracts)

**Topics:**
- XML structure (elements, attributes, namespaces)
- XPath queries
- JSON structure
- CSV/TSV handling
- PDF text extraction

**Tools:**
- lxml (Python library)
- xmltodict
- PyPDF2, PyMuPDF
- pandas

**Practice:** Parse TED XML contract

---

### B. Geographic Data
**Why:** Analyze 81 countries, map contract locations

**Topics:**
- ISO country codes
- Geocoding
- Map visualization
- NUTS codes (EU regional classification)

**Tools:**
- folium (interactive maps)
- geopy (geocoding)
- matplotlib basemap

**Practice:** Create map of Chinese contracts

---

### C. Office Automation
**Why:** Generate PowerPoint reports, Excel exports

**Topics:**
- Excel manipulation (openpyxl)
- PowerPoint generation (python-pptx)
- Word documents (python-docx)
- PDF generation

**Tools:**
- openpyxl, python-pptx, python-docx
- ReportLab (PDF)

**Practice:** Auto-generate intelligence report

---

### D. Windows System Administration
**Why:** Windows Task Scheduler, drive management

**Topics:**
- Task Scheduler
- PowerShell scripting
- Drive management
- Permissions

**Practice:** Schedule weekly data collection

---

## 📅 Suggested Learning Timeline

### Months 1-3: Foundations
**Focus:** Python basics + SQL basics
- Complete Python Crash Course
- Khan Academy SQL
- Build simple ETL for CSV → SQLite

**Milestone:** Process 100 TED contracts into database

---

### Months 4-6: Intermediate Skills
**Focus:** Python intermediate + Data engineering
- Regular expressions
- XML/JSON parsing
- Database queries with JOINs
- Error handling and logging

**Milestone:** Build full TED processor with checkpoint support

---

### Months 7-9: Advanced Processing
**Focus:** Large-scale data processing
- Multiprocessing
- Stream processing
- Entity detection
- Text processing

**Milestone:** Process full TED dataset (1.13M contracts)

---

### Months 10-12: Integration & Intelligence
**Focus:** Cross-source analysis + Automation
- Data analysis with pandas
- Visualization
- Network analysis
- Automation (Task Scheduler)

**Milestone:** Build intelligence report combining TED + USPTO

---

### Months 13-15: Expert Level
**Focus:** Optimization + Production
- Performance tuning
- Testing frameworks
- Documentation
- CI/CD

**Milestone:** Production-ready system with monitoring

---

### Months 16-18: Specialization
**Focus:** Domain expertise
- OSINT methodology
- Advanced NLP
- Machine learning
- Real-time processing

**Milestone:** Automated intelligence pipeline

---

## 🎓 Recommended Learning Resources

### Online Platforms
1. **DataCamp** - Data engineering, pandas, SQL (monthly subscription)
2. **Real Python** - Python tutorials, all levels ($60/year)
3. **Coursera** - University courses (free to audit)
4. **Udemy** - Specific skill courses ($10-15 on sale)

### Books (Essential)
1. "Python Crash Course" - Eric Matthes (beginner)
2. "Automate the Boring Stuff with Python" - Al Sweigart (intermediate)
3. "Fluent Python" - Luciano Ramalho (advanced)
4. "SQL Performance Explained" - Markus Winand
5. "Designing Data-Intensive Applications" - Martin Kleppmann

### Free Resources
- Python documentation (docs.python.org)
- SQLite documentation (sqlite.org)
- Real Python free tutorials
- Stack Overflow (for troubleshooting)
- GitHub (study other projects)

---

## 🎯 Practice Projects (Build Your Portfolio)

### Project 1: Mini TED Analyzer (Months 1-3)
**Goal:** Process 100 TED contracts
- Download sample XML files
- Parse with lxml
- Store in SQLite
- Query for Chinese entities

**Skills:** Python basics, XML, SQL

---

### Project 2: USPTO Patent Tracker (Months 4-6)
**Goal:** Track Chinese patents in your city
- Access USPTO bulk data
- Parse XML patents
- Detect Chinese assignees
- Visualize trends

**Skills:** Large file handling, text processing, visualization

---

### Project 3: Think Tank Monitor (Months 7-9)
**Goal:** Monitor think tank reports
- Scrape think tank websites
- Download PDFs
- Extract text
- Detect China mentions

**Skills:** Web scraping, PDF processing, automation

---

### Project 4: Cross-Source Intel Report (Months 10-12)
**Goal:** Match entities across TED + USPTO
- Load data from both sources
- Entity matching algorithm
- Network visualization
- PowerPoint report generation

**Skills:** Data integration, analysis, reporting

---

## 💼 Career Paths This Prepares You For

1. **Data Engineer** ($80K-150K)
   - Build data pipelines
   - Manage large datasets
   - Database optimization

2. **Intelligence Analyst** ($70K-120K)
   - OSINT analysis
   - Report writing
   - Cross-source validation

3. **Python Developer** ($70K-130K)
   - Automation systems
   - Data processing tools
   - Web scraping

4. **Data Scientist** ($90K-160K)
   - Statistical analysis
   - Machine learning
   - Visualization

5. **DevOps Engineer** ($90K-150K)
   - Automation
   - System monitoring
   - CI/CD pipelines

---

## 🏆 Success Criteria

You'll know you've mastered these skills when you can:

✅ Process 1GB+ datasets without memory issues
✅ Write SQL queries joining 5+ tables
✅ Build ETL pipeline with error handling and checkpointing
✅ Detect entities with 90%+ accuracy
✅ Automate weekly data collection
✅ Generate intelligence reports programmatically
✅ Optimize database queries for 10x+ speedup
✅ Handle multilingual text data
✅ Build network visualizations
✅ Deploy production-ready pipelines

---

## 📊 Technology Stack Summary

**Languages:**
- Python (primary) - 1,330 .py files
- SQL (SQLite) - 17 .sql files
- Bash/PowerShell - 54 .bat files
- Regular expressions

**Data Formats:**
- XML (52,030 files)
- JSON (3,038 files)
- CSV/TSV (183 files)
- PDF (1,560 files)
- Excel (.xlsx) - 17 files
- NDJSON (30 files)

**Python Libraries (Core):**
- Data: pandas, numpy, sqlite3
- XML/JSON: lxml, xml.etree, json, xmltodict
- Web: requests, urllib, aiohttp, BeautifulSoup4, selenium
- Text: re, langdetect, difflib
- Files: pathlib, os, shutil, gzip, tarfile
- Progress: tqdm
- Dates: datetime, dateutil
- Visualization: matplotlib, seaborn, networkx, folium
- Office: openpyxl, python-docx, python-pptx
- PDF: PyMuPDF (fitz), PyPDF2

**Tools & Services:**
- Database: SQLite (23GB, 210 tables)
- Version Control: Git
- Task Scheduling: Windows Task Scheduler
- APIs: OpenAlex, USAspending, TED
- Testing: pytest

**Infrastructure:**
- Storage: 8TB external drive (1.2TB data, 5.5TB free)
- Processing: Windows system with 8-core parallel processing
- Automation: 7 scheduled tasks (daily/weekly)

---

**Total Learning Time Estimate:** 12-18 months (assuming 10-15 hours/week)
**Difficulty Level:** Intermediate to Advanced
**Prerequisites:** High school math, basic computer skills
**Output:** Production-ready OSINT intelligence system

---

*"The best way to learn is by doing. Start small, build projects, and gradually increase complexity."*

---

**Document Version:** 1.0
**Created:** October 18, 2025
**Project:** OSINT Foresight Framework
**Scale Reference:** 1.2TB data, 101.3M records, 739 scripts
