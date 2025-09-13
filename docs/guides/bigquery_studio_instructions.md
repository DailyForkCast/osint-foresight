# BigQuery Studio - Step-by-Step Instructions for Patent Analysis

## Step 1: Access BigQuery Studio

You're already at the right place! You should see "Welcome to BigQuery Studio"

## Step 2: Create a New Query

1. Click **"Create new"** button (or look for "+" or "Compose new query")
2. This will open a SQL editor window

## Step 3: Copy and Paste This Query

Copy this entire SQL query and paste it into the query editor:

```sql
-- Slovak-Chinese Patent Co-inventorship Analysis
-- This query finds patents with both Slovak and Chinese inventors

WITH slovak_patents AS (
    SELECT DISTINCT
        publication_number,
        SUBSTR(CAST(filing_date AS STRING), 1, 4) as filing_year,
        title.text as patent_title
    FROM `patents-public-data.patents.publications`,
        UNNEST(title_localized) as title,
        UNNEST(inventor) as inv
    WHERE inv.country_code = 'SK'
        AND filing_date >= 20180101
        AND title.language = 'en'
),
chinese_coinventors AS (
    SELECT DISTINCT
        publication_number,
        STRING_AGG(inv.name, '; ') as chinese_inventors
    FROM `patents-public-data.patents.publications`,
        UNNEST(inventor) as inv
    WHERE inv.country_code = 'CN'
    GROUP BY publication_number
)
SELECT 
    sp.publication_number,
    sp.patent_title,
    sp.filing_year,
    cc.chinese_inventors
FROM slovak_patents sp
INNER JOIN chinese_coinventors cc 
    ON sp.publication_number = cc.publication_number
ORDER BY sp.filing_year DESC
LIMIT 100
```

## Step 4: Run the Query

1. Click the **"Run"** or **"Execute"** button (usually a play button ▶️)
2. The query will process (may take 10-30 seconds)

## If You Get an Error

### "Dataset not found" or "Table not found":
Try this simpler query first to test access:

```sql
-- Test query - counts total patents
SELECT COUNT(*) as total_patents
FROM `patents-public-data.patents.publications`
WHERE country_code = 'SK'
LIMIT 10
```

### "Access Denied" or "Permission denied":
You may need to:
1. Click on **"Explore public datasets"** or **"Add data"**
2. Search for **"Google Patents Public Datasets"**
3. Click **"View dataset"**
4. This should give you access to the patents data

## Alternative: Try Sample Data First

Since you see "Try with sample data" option:

1. Click **"Try with sample data"** to understand the interface
2. Once comfortable, replace their sample query with our patent query above

## Step 5: Export Results

Once the query runs successfully:
1. Look for **"Save Results"** or **"Export"** button
2. Choose **CSV** format
3. Save the file as `slovak_chinese_patents.csv`

## Simplified Query (If Above Doesn't Work)

Try this very simple query to start:

```sql
-- Simple: Count Slovak patents by year
SELECT 
    SUBSTR(CAST(filing_date AS STRING), 1, 4) as year,
    COUNT(*) as slovak_patents
FROM `patents-public-data.patents.publications`
WHERE country_code = 'SK'
    AND filing_date >= 20180101
GROUP BY year
ORDER BY year DESC
```

## What We're Looking For

1. **Any results** = Slovak-Chinese collaboration exists
2. **10+ patents** = Significant collaboration
3. **50+ patents** = Critical technology transfer risk

## Can't Get It Working?

Alternative approaches:
1. Try **Google Patents** website directly: https://patents.google.com
   - Advanced search → Inventor country: Slovakia AND China
   
2. Try **The Lens** (free with registration): https://www.lens.org
   - Search: inventor.residence.country:"SK" AND inventor.residence.country:"CN"

3. Try **Espacenet**: https://worldwide.espacenet.com
   - Advanced search → Inventor country: SK AND CN

## Quick Test Searches

If BigQuery doesn't work, try these searches in Google Patents:
1. Search: `inventor:slovakia inventor:china after:2018`
2. Search: `assignee:"slovak university" inventor:china`
3. Search: `assignee:comenius inventor:china`

---
**Note**: The key is finding ANY patents with both Slovak and Chinese inventors - this would confirm technology transfer risk beyond the 76 joint projects we found in CORDIS.