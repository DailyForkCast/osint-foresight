# AWS Athena Setup for Common Crawl EU-China Agreements Discovery
## ZERO FABRICATION - COMPLETE PROVENANCE - FULL CITATIONS

---

## 📋 Step 1: AWS Athena Setup

### Prerequisites
1. **AWS Account**: Create at https://aws.amazon.com
2. **S3 Bucket**: For query results (e.g., `s3://your-athena-results/`)
3. **IAM Permissions**: Read access to Common Crawl public dataset

### Initial Setup Commands

```sql
-- 1. Create Database for Common Crawl
CREATE DATABASE IF NOT EXISTS ccindex;

-- 2. Create External Table pointing to Common Crawl Index
CREATE EXTERNAL TABLE IF NOT EXISTS ccindex.ccindex (
  url_surtkey                   STRING,
  url                           STRING,
  url_host_name                 STRING,
  url_host_tld                  STRING,
  url_host_2nd_last_part        STRING,
  url_host_3rd_last_part        STRING,
  url_host_4th_last_part        STRING,
  url_host_5th_last_part        STRING,
  url_host_registry_suffix      STRING,
  url_host_registered_domain    STRING,
  url_host_private_suffix       STRING,
  url_host_private_domain       STRING,
  url_protocol                  STRING,
  url_port                      INT,
  url_path                      STRING,
  url_query                     STRING,
  fetch_time                    TIMESTAMP,
  fetch_status                  SMALLINT,
  content_digest                STRING,
  content_mime_type             STRING,
  content_mime_detected         STRING,
  content_charset               STRING,
  content_languages             STRING,
  warc_filename                 STRING,
  warc_record_offset            INT,
  warc_record_length            INT,
  warc_segment                  STRING
)
STORED AS parquet
LOCATION 's3://commoncrawl/cc-index/table/cc-main/warc/';

-- 3. Add Partitions for Specific Crawls
MSCK REPAIR TABLE ccindex.ccindex;
```

### Verification Query
```sql
-- Verify table is accessible
SELECT COUNT(*) as total_records
FROM ccindex.ccindex
WHERE crawl = 'CC-MAIN-2024-10'
LIMIT 1;
```

### Cost Optimization
- **Use LIMIT**: Always limit results during testing
- **Partition by crawl**: Query specific crawls only
- **Project columns**: Select only needed columns
- **S3 Select**: Enable for reduced data transfer

---

## 📋 Step 2: Targeted SQL Patterns for Agreement Discovery

### Sister City Agreements Pattern

```sql
-- PATTERN: Sister City Agreements with Full Provenance
WITH sister_cities AS (
  SELECT
    url,
    url_host_name,
    fetch_time,
    content_digest,
    warc_filename,
    warc_record_offset,
    warc_record_length,
    crawl
  FROM ccindex.ccindex
  WHERE crawl = 'CC-MAIN-2024-10'
    AND (
      -- Municipal domains
      url_host_name LIKE '%.gov%'
      OR url_host_name LIKE '%.city%'
      OR url_host_name LIKE '%.municipality%'
      OR url_host_name LIKE '%.kommune%'
      OR url_host_name LIKE '%.comune%'
      OR url_host_name LIKE '%.ville%'
      OR url_host_name LIKE '%.stadt%'
    )
    AND (
      -- Sister city patterns in URL
      LOWER(url_path) LIKE '%sister-cit%'
      OR LOWER(url_path) LIKE '%twin-cit%'
      OR LOWER(url_path) LIKE '%partnership%'
      OR LOWER(url_path) LIKE '%cooperation%'
      OR LOWER(url_path) LIKE '%international%'
    )
    AND (
      -- China-related
      LOWER(url) LIKE '%china%'
      OR LOWER(url) LIKE '%chinese%'
      OR LOWER(url) LIKE '%beijing%'
      OR LOWER(url) LIKE '%shanghai%'
    )
)
SELECT
  url AS source_url,
  url_host_name AS domain,
  fetch_time AS crawl_date,
  content_digest AS content_hash,
  CONCAT('Common Crawl Foundation. ',
         YEAR(fetch_time),
         '. Web crawl data from ', url,
         '. Dataset: ', crawl,
         '. WARC: ', warc_filename,
         ', Offset: ', CAST(warc_record_offset AS VARCHAR),
         '. Available at: https://commoncrawl.org/') AS citation,
  'REQUIRES_VERIFICATION' AS verification_status,
  'Common Crawl' AS data_source,
  warc_filename,
  warc_record_offset,
  warc_record_length
FROM sister_cities
LIMIT 1000;
```

### University Partnership Pattern

```sql
-- PATTERN: University Partnerships with Provenance
WITH university_partnerships AS (
  SELECT
    url,
    url_host_name,
    fetch_time,
    content_digest,
    warc_filename,
    warc_record_offset,
    crawl
  FROM ccindex.ccindex
  WHERE crawl = 'CC-MAIN-2024-10'
    AND (
      -- Academic domains
      url_host_tld = 'edu'
      OR url_host_name LIKE '%.ac.%'
      OR url_host_name LIKE '%.edu.%'
      OR url_host_name LIKE '%.uni-%'
      OR url_host_name LIKE '%.university%'
    )
    AND (
      -- Partnership patterns
      LOWER(url_path) LIKE '%partnership%'
      OR LOWER(url_path) LIKE '%cooperation%'
      OR LOWER(url_path) LIKE '%exchange%'
      OR LOWER(url_path) LIKE '%collaboration%'
      OR LOWER(url_path) LIKE '%international%'
      OR LOWER(url_path) LIKE '%global%'
    )
    AND (
      -- China-related
      LOWER(url) LIKE '%china%'
      OR LOWER(url) LIKE '%chinese%'
    )
)
SELECT
  url AS source_url,
  url_host_name AS institution,
  fetch_time AS crawl_date,
  content_digest AS content_hash,
  CONCAT('Common Crawl Foundation. ',
         YEAR(fetch_time),
         '. Academic partnership data from ', url,
         '. Dataset: ', crawl,
         '. Retrieved: ', CURRENT_DATE) AS citation,
  'REQUIRES_VERIFICATION' AS verification_status,
  warc_filename,
  warc_record_offset
FROM university_partnerships
LIMIT 500;
```

### Government Agreements Pattern

```sql
-- PATTERN: Government Agreements with Complete Attribution
WITH government_agreements AS (
  SELECT
    url,
    url_host_name,
    fetch_time,
    content_digest,
    warc_filename,
    warc_record_offset,
    crawl
  FROM ccindex.ccindex
  WHERE crawl = 'CC-MAIN-2024-10'
    AND (
      -- Government domains
      url_host_name LIKE '%.gov.%'
      OR url_host_name LIKE '%.mfa.%'
      OR url_host_name LIKE '%.foreign.%'
      OR url_host_name LIKE '%.diplo%'
    )
    AND (
      -- Agreement patterns
      LOWER(url_path) LIKE '%agreement%'
      OR LOWER(url_path) LIKE '%treaty%'
      OR LOWER(url_path) LIKE '%memorandum%'
      OR LOWER(url_path) LIKE '%mou%'
      OR LOWER(url_path) LIKE '%bilateral%'
    )
    AND (
      -- China-related
      LOWER(url) LIKE '%china%'
      OR LOWER(url) LIKE '%prc%'
    )
)
SELECT
  url AS source_url,
  url_host_name AS government_domain,
  fetch_time AS crawl_date,
  content_digest,
  'Official government source via Common Crawl' AS source_type,
  CONCAT('Common Crawl Foundation (', YEAR(fetch_time), '). ',
         'Government agreement data. Source: ', url) AS citation,
  warc_filename,
  warc_record_offset
FROM government_agreements
LIMIT 300;
```

---

## 📋 Step 3: Multi-Language Search Implementation

### German Sister Cities (Städtepartnerschaft)

```sql
-- GERMAN: Städtepartnerschaft with China
SELECT
  url AS source_url,
  url_host_name AS german_municipality,
  fetch_time AS crawl_date,
  CONCAT('Common Crawl (', YEAR(fetch_time), '). ',
         'Städtepartnerschaft data from ', url) AS citation,
  'REQUIRES_VERIFICATION' AS status,
  warc_filename,
  warc_record_offset
FROM ccindex.ccindex
WHERE crawl = 'CC-MAIN-2024-10'
  AND (url_host_name LIKE '%.de' OR url_host_name LIKE '%.stadt%')
  AND (
    LOWER(url) LIKE '%städtepartnerschaft%'
    OR LOWER(url) LIKE '%partnerstadt%'
    OR LOWER(url) LIKE '%freundschaft%'
  )
  AND (
    LOWER(url) LIKE '%china%'
    OR LOWER(url) LIKE '%chinesisch%'
    OR LOWER(url) LIKE '%peking%'
    OR LOWER(url) LIKE '%shanghai%'
  )
LIMIT 200;
```

### French Sister Cities (Jumelage)

```sql
-- FRENCH: Villes jumelées with China
SELECT
  url AS source_url,
  url_host_name AS french_municipality,
  fetch_time AS crawl_date,
  CONCAT('Common Crawl (', YEAR(fetch_time), '). ',
         'Jumelage data from ', url) AS citation,
  warc_filename,
  warc_record_offset
FROM ccindex.ccindex
WHERE crawl = 'CC-MAIN-2024-10'
  AND (url_host_name LIKE '%.fr' OR url_host_name LIKE '%.ville%')
  AND (
    LOWER(url) LIKE '%jumelage%'
    OR LOWER(url) LIKE '%jumele%'
    OR LOWER(url) LIKE '%cooperation%'
  )
  AND (
    LOWER(url) LIKE '%chine%'
    OR LOWER(url) LIKE '%chinois%'
    OR LOWER(url) LIKE '%pekin%'
  )
LIMIT 200;
```

### Italian Sister Cities (Gemellaggio)

```sql
-- ITALIAN: Città gemelle with China
SELECT
  url AS source_url,
  url_host_name AS italian_municipality,
  fetch_time AS crawl_date,
  CONCAT('Common Crawl (', YEAR(fetch_time), '). ',
         'Gemellaggio data from ', url) AS citation,
  warc_filename,
  warc_record_offset
FROM ccindex.ccindex
WHERE crawl = 'CC-MAIN-2024-10'
  AND (url_host_name LIKE '%.it' OR url_host_name LIKE '%.comune%')
  AND (
    LOWER(url) LIKE '%gemell%'
    OR LOWER(url) LIKE '%cooperazione%'
    OR LOWER(url) LIKE '%internazional%'
  )
  AND (
    LOWER(url) LIKE '%cina%'
    OR LOWER(url) LIKE '%cinese%'
    OR LOWER(url) LIKE '%pechino%'
  )
LIMIT 200;
```

### Master Multi-Language Query

```sql
-- COMPREHENSIVE: All EU languages with China agreements
WITH multilingual_agreements AS (
  SELECT
    url,
    url_host_name,
    url_host_tld,
    fetch_time,
    content_digest,
    warc_filename,
    warc_record_offset,
    crawl,
    CASE
      WHEN url_host_tld = 'de' THEN 'German'
      WHEN url_host_tld = 'fr' THEN 'French'
      WHEN url_host_tld = 'it' THEN 'Italian'
      WHEN url_host_tld = 'es' THEN 'Spanish'
      WHEN url_host_tld = 'pl' THEN 'Polish'
      WHEN url_host_tld = 'nl' THEN 'Dutch'
      WHEN url_host_tld = 'pt' THEN 'Portuguese'
      ELSE 'Other'
    END AS language_context
  FROM ccindex.ccindex
  WHERE crawl = 'CC-MAIN-2024-10'
    AND url_host_tld IN ('de', 'fr', 'it', 'es', 'pl', 'nl', 'pt', 'be',
                         'at', 'ch', 'cz', 'hu', 'sk', 'si', 'hr', 'ro',
                         'bg', 'gr', 'dk', 'se', 'no', 'fi', 'ee', 'lv', 'lt')
    AND (
      -- Multi-language partnership terms
      LOWER(url) LIKE '%partnership%' OR
      LOWER(url) LIKE '%cooperation%' OR
      LOWER(url) LIKE '%städtepartnerschaft%' OR
      LOWER(url) LIKE '%jumelage%' OR
      LOWER(url) LIKE '%gemell%' OR
      LOWER(url) LIKE '%hermanamiento%' OR
      LOWER(url) LIKE '%partnerstwo%'
    )
    AND (
      -- China in multiple languages
      LOWER(url) LIKE '%china%' OR
      LOWER(url) LIKE '%chine%' OR
      LOWER(url) LIKE '%cina%' OR
      LOWER(url) LIKE '%chiny%'
    )
)
SELECT
  url AS source_url,
  url_host_name AS domain,
  language_context,
  fetch_time AS crawl_date,
  CONCAT('Common Crawl Foundation (', YEAR(fetch_time), '). ',
         'Bilateral agreement data (', language_context, '). ',
         'Source: ', url, '. ',
         'WARC: ', warc_filename, ', Offset: ', CAST(warc_record_offset AS VARCHAR)) AS full_citation,
  'REQUIRES_MANUAL_VERIFICATION' AS verification_status,
  content_digest AS content_hash,
  warc_filename,
  warc_record_offset
FROM multilingual_agreements
ORDER BY language_context, fetch_time DESC
LIMIT 2000;
```

---

## 📋 Step 4: Manual Verification Workflow

### Verification Checklist Template

```sql
-- Create verification tracking table
CREATE TABLE IF NOT EXISTS agreement_verification (
  record_id VARCHAR(255) PRIMARY KEY,
  source_url VARCHAR(2048),
  crawl_date TIMESTAMP,
  content_hash VARCHAR(255),
  warc_location VARCHAR(500),
  verification_status VARCHAR(50) DEFAULT 'PENDING',
  verification_date TIMESTAMP,
  verified_by VARCHAR(100),
  agreement_type VARCHAR(100),
  parties_confirmed VARCHAR(500),
  date_signed DATE,
  current_status VARCHAR(50),
  notes TEXT,
  citation TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert candidates for verification
INSERT INTO agreement_verification (
  record_id,
  source_url,
  crawl_date,
  content_hash,
  warc_location,
  citation
)
SELECT
  MD5(CONCAT(url, fetch_time)) AS record_id,
  url AS source_url,
  fetch_time AS crawl_date,
  content_digest AS content_hash,
  CONCAT(warc_filename, ':', CAST(warc_record_offset AS VARCHAR)) AS warc_location,
  CONCAT('Common Crawl Foundation (', YEAR(fetch_time), '). ',
         'Source: ', url, '. Retrieved from Common Crawl.') AS citation
FROM ccindex.ccindex
WHERE crawl = 'CC-MAIN-2024-10'
  AND /* your filter conditions */
LIMIT 100;
```

### Verification Process SQL

```sql
-- Mark record as verified
UPDATE agreement_verification
SET
  verification_status = 'VERIFIED',
  verification_date = CURRENT_TIMESTAMP,
  verified_by = 'researcher_name',
  agreement_type = 'sister_city',
  parties_confirmed = 'Hamburg-Shanghai',
  date_signed = DATE '1986-05-29',
  current_status = 'ACTIVE',
  notes = 'Confirmed via original municipal website'
WHERE record_id = 'specific_record_id';

-- Generate verification report
SELECT
  agreement_type,
  COUNT(*) AS total,
  COUNT(CASE WHEN verification_status = 'VERIFIED' THEN 1 END) AS verified,
  COUNT(CASE WHEN verification_status = 'PENDING' THEN 1 END) AS pending,
  COUNT(CASE WHEN verification_status = 'REJECTED' THEN 1 END) AS rejected
FROM agreement_verification
GROUP BY agreement_type
ORDER BY total DESC;
```

---

## 🔒 Data Provenance Requirements

### Every Query Must Include:

1. **Source URL**: Complete URL from Common Crawl
2. **Crawl Date**: When Common Crawl captured the page
3. **Content Hash**: SHA256 digest for verification
4. **WARC Location**: File and offset for raw data access
5. **Citation**: Proper attribution to Common Crawl
6. **Verification Status**: Always "REQUIRES_VERIFICATION"

### Citation Format:
```
Common Crawl Foundation. (YEAR). [Description of data].
Dataset: [Crawl ID]. Source: [Original URL].
WARC: [Filename], Offset: [Offset].
Retrieved: [Current Date]. Available at: https://commoncrawl.org/
```

---

## ⚠️ Critical Reminders

1. **NO FABRICATION**: Only return actual crawled URLs
2. **VERIFICATION REQUIRED**: All results need manual checking
3. **CITATION MANDATORY**: Every record must have full citation
4. **RAW DATA ACCESS**: WARC files contain actual page content
5. **COSTS**: Monitor AWS Athena query costs (typically $5/TB scanned)

---

## 📊 Expected Results

With these queries properly executed:

- **Sister Cities**: 50-100+ URLs pointing to partnership pages
- **University Partnerships**: 30-50+ academic cooperation pages
- **Government Agreements**: 15-30+ official agreement documents
- **Multi-language Results**: Additional 20-40+ in native languages

**Total Expected**: 115-220+ agreement-related URLs requiring verification

All with complete provenance and zero fabrication.
