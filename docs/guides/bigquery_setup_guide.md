# BigQuery Patent Analysis Setup Guide
**For Slovakia-China Technology Transfer Analysis**

## Quick Start Options

### Option 1: Web Console (No Installation Required)
1. Go to: https://console.cloud.google.com/bigquery
2. Click "Create Project" or use sandbox (free tier)
3. Navigate to "patents-public-data" dataset
4. Run queries directly in SQL workspace

### Option 2: Command Line (bq tool)
```bash
# Install Google Cloud SDK
# Windows: Download installer from https://cloud.google.com/sdk/docs/install
# Or use PowerShell:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# Initialize and authenticate
gcloud init
gcloud auth login

# Run queries
bq query --use_legacy_sql=false 'YOUR_SQL_QUERY'
```

### Option 3: Python Script
```bash
# Install required packages
pip install google-cloud-bigquery pandas

# Run the analysis script
python bigquery_patents_analysis.py
```

## Priority Queries to Run Manually

### Query 1: Find Slovak-Chinese Co-inventions
```sql
-- Run this in BigQuery Console
WITH slovak_patents AS (
    SELECT DISTINCT
        publication_number,
        application_date,
        title_localized[SAFE_OFFSET(0)].text as title
    FROM `patents-public-data.patents.publications_202410`,
        UNNEST(inventor_localized) as inventor
    WHERE inventor.country_code = 'SK'
        AND CAST(application_date AS STRING) >= '20180101'
),
chinese_inventors AS (
    SELECT DISTINCT
        publication_number,
        STRING_AGG(inventor.name, '; ') as chinese_inventors
    FROM `patents-public-data.patents.publications_202410`,
        UNNEST(inventor_localized) as inventor
    WHERE inventor.country_code = 'CN'
    GROUP BY publication_number
)
SELECT
    sp.publication_number,
    sp.title,
    sp.application_date,
    ci.chinese_inventors
FROM slovak_patents sp
JOIN chinese_inventors ci ON sp.publication_number = ci.publication_number
LIMIT 100
```

### Query 2: Slovak University Patents
```sql
SELECT
    assignee_harmonized.name as university,
    COUNT(DISTINCT publication_number) as patent_count,
    STRING_AGG(DISTINCT inventor.country_code, ', ') as countries
FROM `patents-public-data.patents.publications_202410`,
    UNNEST(assignee_harmonized) as assignee_harmonized,
    UNNEST(inventor_localized) as inventor
WHERE (
    LOWER(assignee_harmonized.name) LIKE '%slovak%university%' OR
    LOWER(assignee_harmonized.name) LIKE '%comenius%' OR
    LOWER(assignee_harmonized.name) LIKE '%technical university%kosice%'
)
AND CAST(application_date AS STRING) >= '20180101'
GROUP BY university
ORDER BY patent_count DESC
```

### Query 3: Critical Technology Areas
```sql
SELECT
    CASE
        WHEN cpc.code LIKE 'G06N10/%' THEN 'Quantum Computing'
        WHEN cpc.code LIKE 'G06N3/%' THEN 'AI/ML'
        WHEN cpc.code LIKE 'C12N%' THEN 'Biotechnology'
        WHEN cpc.code LIKE 'H01L%' THEN 'Semiconductors'
        WHEN cpc.code LIKE 'B82Y%' THEN 'Nanotechnology'
        ELSE 'Other'
    END as technology,
    COUNT(DISTINCT publication_number) as count
FROM `patents-public-data.patents.publications_202410`,
    UNNEST(inventor_localized) as inventor,
    UNNEST(cpc) as cpc
WHERE inventor.country_code = 'SK'
    AND CAST(application_date AS STRING) >= '20180101'
GROUP BY technology
ORDER BY count DESC
```

## Using BigQuery Sandbox (Free)

1. **No Credit Card Required**
   - Go to: https://console.cloud.google.com/bigquery
   - Click "Try BigQuery free"
   - Create project with sandbox mode

2. **Sandbox Limits**
   - 1 TB of queries per month (free)
   - 10 GB storage (free)
   - Perfect for patent analysis

3. **Access Public Datasets**
   - Click "+ ADD DATA" → "Explore public datasets"
   - Search for "Google Patents Public Datasets"
   - Or directly query: `patents-public-data.patents.publications_202410`

## Export Results

### From Web Console:
1. Run your query
2. Click "SAVE RESULTS"
3. Choose format: CSV, JSON, or Google Sheets
4. Download for analysis

### From Command Line:
```bash
# Export to CSV
bq query --use_legacy_sql=false --format=csv 'YOUR_QUERY' > results.csv

# Export to JSON
bq query --use_legacy_sql=false --format=json 'YOUR_QUERY' > results.json
```

### From Python:
```python
# The script automatically saves to CSV
# Check: out/SK/slovak_chinese_coinventions.csv
```

## What to Look For

### Red Flags:
- Any Slovak-Chinese co-invented patents
- Slovak universities with Chinese assignees
- Patents in quantum, AI, or biotech with China links
- Rapid growth in co-inventions 2020-2025

### Key Metrics:
- Total Slovak patents: Expected 500-1000
- Co-inventions with China: Critical if >20
- University involvement: Risk if >5 institutions
- Critical tech exposure: Any quantum/AI/biotech

## Troubleshooting

### "Permission denied" error:
- Use sandbox mode (no authentication needed)
- Or run: `gcloud auth application-default login`

### "Table not found" error:
- Check table name: `patents-public-data.patents.publications_202410`
- Older versions: Try `publications_202310` or `publications_202210`

### Query timeout:
- Add `LIMIT 100` to queries
- Use date filters to reduce data

## Next Steps

1. **Run Query 1** first to find co-inventions
2. **Export results** as CSV
3. **Share findings** for risk assessment
4. **Set up monitoring** for new patents monthly

---
**Support**: BigQuery documentation at https://cloud.google.com/bigquery/docs
**Dataset info**: https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data
