# Google Patents BigQuery Analysis Templates for Slovakia
**Generated: 2025-01-10**
**Platform: Google Cloud BigQuery Public Datasets**

## Setup Instructions

### Access Google Patents Public Datasets
1. Go to: https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data
2. Use dataset: `patents-public-data.patents.publications`
3. Free tier: 1TB/month processing

## Priority Queries for Slovakia-China Analysis

### Query 1: Slovak Inventors in Chinese Patents
```sql
SELECT
  publication_number,
  application_date,
  title.text as patent_title,
  assignee_harmonized.name as assignee,
  inventor.name as inventor_name,
  inventor.country_code as inventor_country,
  cpc.code as technology_class
FROM `patents-public-data.patents.publications`,
  UNNEST(title_localized) as title,
  UNNEST(inventor_localized) as inventor,
  UNNEST(assignee_harmonized) as assignee_harmonized,
  UNNEST(cpc) as cpc
WHERE country_code = 'CN'
  AND inventor.country_code = 'SK'
  AND PARSE_DATE('%Y%m%d', CAST(application_date AS STRING)) >= '2018-01-01'
ORDER BY application_date DESC
```

### Query 2: Chinese-Slovak Co-inventions
```sql
WITH slovak_chinese_patents AS (
  SELECT DISTINCT
    publication_number,
    application_date,
    title.text as patent_title
  FROM `patents-public-data.patents.publications`,
    UNNEST(title_localized) as title,
    UNNEST(inventor_localized) as inv
  WHERE inv.country_code = 'SK'
    AND PARSE_DATE('%Y%m%d', CAST(application_date AS STRING)) >= '2018-01-01'
)
SELECT
  scp.publication_number,
  scp.application_date,
  scp.patent_title,
  STRING_AGG(DISTINCT inv.name, '; ') as all_inventors,
  STRING_AGG(DISTINCT inv.country_code, '; ') as inventor_countries,
  STRING_AGG(DISTINCT assignee.name, '; ') as assignees
FROM slovak_chinese_patents scp
JOIN `patents-public-data.patents.publications` p
  ON scp.publication_number = p.publication_number,
  UNNEST(p.inventor_localized) as inv,
  UNNEST(p.assignee_harmonized) as assignee
WHERE inv.country_code IN ('SK', 'CN')
GROUP BY 1,2,3
HAVING inventor_countries LIKE '%CN%' AND inventor_countries LIKE '%SK%'
```

### Query 3: Technology Transfer Indicators
```sql
-- Patents with Slovak inventors that were later assigned to Chinese entities
SELECT
  p1.publication_number as original_patent,
  p1.application_date,
  inv.name as slovak_inventor,
  p1.assignee_harmonized.name as original_assignee,
  p2.assignee_harmonized.name as current_assignee,
  p2.assignee_harmonized.country_code as current_country
FROM `patents-public-data.patents.publications` p1,
  UNNEST(inventor_localized) as inv,
  UNNEST(assignee_harmonized) as assignee_harmonized
JOIN `patents-public-data.patents.publications` p2
  ON p1.family_id = p2.family_id
WHERE inv.country_code = 'SK'
  AND p2.assignee_harmonized.country_code = 'CN'
  AND p1.publication_number != p2.publication_number
  AND PARSE_DATE('%Y%m%d', CAST(p1.application_date AS STRING)) >= '2018-01-01'
```

### Query 4: Critical Technology Areas
```sql
-- Slovak patents in quantum, AI, biotech
SELECT
  publication_number,
  application_date,
  title.text as patent_title,
  assignee_harmonized.name as assignee,
  cpc.code as cpc_code,
  CASE
    WHEN cpc.code LIKE 'G06N10/%' THEN 'Quantum Computing'
    WHEN cpc.code LIKE 'G06N3/%' OR cpc.code LIKE 'G06N20/%' THEN 'AI/ML'
    WHEN cpc.code LIKE 'C12N%' THEN 'Biotechnology'
    WHEN cpc.code LIKE 'H01L%' THEN 'Semiconductors'
    WHEN cpc.code LIKE 'B82Y%' THEN 'Nanotechnology'
    ELSE 'Other'
  END as technology_domain
FROM `patents-public-data.patents.publications`,
  UNNEST(title_localized) as title,
  UNNEST(inventor_localized) as inventor,
  UNNEST(assignee_harmonized) as assignee_harmonized,
  UNNEST(cpc) as cpc
WHERE inventor.country_code = 'SK'
  AND PARSE_DATE('%Y%m%d', CAST(application_date AS STRING)) >= '2018-01-01'
  AND (
    cpc.code LIKE 'G06N%' OR
    cpc.code LIKE 'C12N%' OR
    cpc.code LIKE 'H01L%' OR
    cpc.code LIKE 'B82Y%'
  )
ORDER BY application_date DESC
```

### Query 5: Citation Analysis
```sql
-- Chinese entities citing Slovak patents
SELECT
  cited.publication_number as slovak_patent,
  cited_title.text as slovak_patent_title,
  citing.publication_number as chinese_citing_patent,
  citing_title.text as chinese_patent_title,
  citing.application_date as citation_date
FROM `patents-public-data.patents.publications` cited,
  UNNEST(title_localized) as cited_title,
  UNNEST(inventor_localized) as cited_inv,
  `patents-public-data.patents.publications` citing,
  UNNEST(citing.citation) as citation,
  UNNEST(citing.title_localized) as citing_title
WHERE cited_inv.country_code = 'SK'
  AND citing.country_code = 'CN'
  AND citation.publication_number = cited.publication_number
  AND PARSE_DATE('%Y%m%d', CAST(cited.application_date AS STRING)) >= '2018-01-01'
```

### Query 6: Slovak University Patents
```sql
-- Patents from Slovak universities
SELECT
  publication_number,
  application_date,
  title.text as patent_title,
  assignee_harmonized.name as assignee,
  STRING_AGG(DISTINCT inventor.name, '; ') as inventors,
  STRING_AGG(DISTINCT cpc.code, '; ') as technology_classes
FROM `patents-public-data.patents.publications`,
  UNNEST(title_localized) as title,
  UNNEST(inventor_localized) as inventor,
  UNNEST(assignee_harmonized) as assignee_harmonized,
  UNNEST(cpc) as cpc
WHERE (
    LOWER(assignee_harmonized.name) LIKE '%slovak%university%' OR
    LOWER(assignee_harmonized.name) LIKE '%comenius%' OR
    LOWER(assignee_harmonized.name) LIKE '%technical university%' OR
    LOWER(assignee_harmonized.name) LIKE '%slovak academy%'
  )
  AND PARSE_DATE('%Y%m%d', CAST(application_date AS STRING)) >= '2018-01-01'
GROUP BY 1,2,3,4
ORDER BY application_date DESC
```

## Analysis Metrics to Calculate

### From Query Results:
1. **Co-invention Rate**: Slovak-Chinese patents / Total Slovak patents
2. **Technology Transfer Rate**: Patents reassigned to China / Total
3. **Citation Impact**: Chinese citations of Slovak work
4. **Domain Concentration**: Distribution across CPC codes
5. **Temporal Trends**: Year-over-year growth rates

### Risk Scoring Formula:
```
Risk Score = (Co-invention_Rate * 0.3) +
             (Transfer_Rate * 0.3) +
             (Critical_Tech_Share * 0.2) +
             (Citation_Dependency * 0.2)
```

## Export Instructions

### For each query:
1. Run in BigQuery console
2. Export results to Google Sheets or CSV
3. Download for local analysis

### Combine into master file:
```
slovak_patents_master.csv
├── patent_number
├── application_date
├── title
├── slovak_assignee
├── chinese_involvement (Y/N)
├── technology_domain
├── risk_level (1-5)
└── notes
```

## Expected Insights

Based on patterns in similar countries:
- 50-100 Slovak patents with Chinese co-inventors
- 10-20 patents transferred to Chinese entities
- 200+ Chinese patents citing Slovak research
- Concentration in automotive, materials science
- Growing trend 2020-2025

## Automated Monitoring Setup

### Create saved queries for:
1. New Slovak-Chinese co-inventions (weekly)
2. Patent assignments to China (monthly)
3. Citation patterns (quarterly)
4. Technology domain shifts (quarterly)

### Alert triggers:
- Any patent in quantum/AI with China involvement
- Assignment to PLA-linked entities
- Sudden spike in co-inventions
- New technology domains appearing

---
**Note**: BigQuery requires Google Cloud account (free tier available). After running queries, provide CSV exports for detailed analysis.
