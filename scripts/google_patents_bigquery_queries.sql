-- Google Patents BigQuery Analysis Queries
-- For China technology transfer and collaboration patterns
-- Dataset: patents-public-data

-- ============================================
-- Query 1: China Co-Inventions with Tracked Countries (2000-2025)
-- ============================================
WITH china_patents AS (
  SELECT
    p.publication_number,
    p.family_id,
    EXTRACT(YEAR FROM p.publication_date) as year,
    p.title_localized[SAFE_OFFSET(0)].text as title,
    p.abstract_localized[SAFE_OFFSET(0)].text as abstract,
    p.inventor_harmonized,
    p.assignee_harmonized,
    p.priority_date,
    p.application_date,
    p.publication_date,
    p.cpc[SAFE_OFFSET(0)].code as primary_cpc
  FROM
    `patents-public-data.patents.publications` p
  WHERE
    p.country_code = 'CN'
    AND EXTRACT(YEAR FROM p.publication_date) BETWEEN 2000 AND 2025
),
inventor_countries AS (
  SELECT DISTINCT
    cp.publication_number,
    cp.year,
    cp.title,
    inv.name,
    inv.country_code as inventor_country
  FROM
    china_patents cp,
    UNNEST(cp.inventor_harmonized) as inv
  WHERE
    inv.country_code IS NOT NULL
)
SELECT
  year,
  inventor_country,
  COUNT(DISTINCT publication_number) as patent_count,
  ARRAY_AGG(DISTINCT title LIMIT 5) as sample_titles
FROM
  inventor_countries
WHERE
  inventor_country IN ('US','DE','FR','IT','ES','NL','BE','SE','DK','FI','NO','PL','CZ','SK','HU','RO','BG','HR','SI','EE','LV','LT','GR','CY','MT','PT','AT','IE','CH','GB','TR','UA','CA','AU','NZ','JP','KR','SG','TW','IN','IL','BR','RU')
GROUP BY
  year, inventor_country
ORDER BY
  year DESC, patent_count DESC;

-- ============================================
-- Query 2: Dual-Use Technology Detection
-- ============================================
WITH china_tech_patents AS (
  SELECT
    p.publication_number,
    p.family_id,
    EXTRACT(YEAR FROM p.publication_date) as year,
    p.title_localized[SAFE_OFFSET(0)].text as title,
    p.abstract_localized[SAFE_OFFSET(0)].text as abstract,
    p.assignee_harmonized,
    p.cpc,
    CASE
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%quantum comput%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%qubit%'
        THEN 'quantum_computing'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%artificial intelligence%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%machine learning%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%neural network%'
        THEN 'ai_ml'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%semiconductor%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%integrated circuit%'
        THEN 'semiconductors'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%hypersonic%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%missile%'
        THEN 'hypersonics'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%5g%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%6g%'
        THEN '5g_6g'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%biotechnology%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%crispr%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%synthetic bio%'
        THEN 'biotechnology'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%advanced material%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%metamaterial%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%graphene%'
        THEN 'advanced_materials'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%autonomous%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%unmanned%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%drone%'
        THEN 'autonomous_systems'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%clean energy%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%battery%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%solar%'
        THEN 'clean_energy'
      WHEN LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%space technolog%'
        OR LOWER(CONCAT(p.title_localized[SAFE_OFFSET(0)].text, ' ', p.abstract_localized[SAFE_OFFSET(0)].text)) LIKE '%satellite%'
        THEN 'space_technology'
      ELSE NULL
    END as technology_category
  FROM
    `patents-public-data.patents.publications` p
  WHERE
    p.country_code = 'CN'
    AND EXTRACT(YEAR FROM p.publication_date) BETWEEN 2000 AND 2025
)
SELECT
  year,
  technology_category,
  COUNT(DISTINCT publication_number) as patent_count,
  COUNT(DISTINCT family_id) as family_count
FROM
  china_tech_patents
WHERE
  technology_category IS NOT NULL
GROUP BY
  year, technology_category
ORDER BY
  year DESC, patent_count DESC;

-- ============================================
-- Query 3: Top Chinese Assignees with Foreign Collaborations
-- ============================================
WITH china_foreign_collab AS (
  SELECT
    p.publication_number,
    p.family_id,
    EXTRACT(YEAR FROM p.publication_date) as year,
    p.title_localized[SAFE_OFFSET(0)].text as title,
    assignee.name as assignee_name,
    assignee.country_code as assignee_country,
    ARRAY_AGG(DISTINCT inv.country_code IGNORE NULLS) as inventor_countries
  FROM
    `patents-public-data.patents.publications` p,
    UNNEST(p.assignee_harmonized) as assignee,
    UNNEST(p.inventor_harmonized) as inv
  WHERE
    p.country_code = 'CN'
    AND EXTRACT(YEAR FROM p.publication_date) BETWEEN 2015 AND 2025
    AND assignee.country_code = 'CN'
  GROUP BY
    p.publication_number, p.family_id, year, title, assignee_name, assignee_country
  HAVING
    ARRAY_LENGTH(inventor_countries) > 1
    AND 'CN' IN UNNEST(inventor_countries)
    AND EXISTS (
      SELECT 1 FROM UNNEST(inventor_countries) AS country
      WHERE country != 'CN'
    )
)
SELECT
  assignee_name,
  COUNT(DISTINCT publication_number) as patent_count,
  ARRAY_AGG(DISTINCT country ORDER BY country) as partner_countries
FROM
  china_foreign_collab,
  UNNEST(inventor_countries) as country
WHERE
  country != 'CN'
  AND country IN ('US','DE','FR','IT','ES','NL','BE','SE','DK','FI','NO','PL','CZ','SK','HU','RO','BG','HR','SI','EE','LV','LT','GR','CY','MT','PT','AT','IE','CH','GB','TR','UA','CA','AU','NZ','JP','KR','SG','TW','IN','IL','BR','RU')
GROUP BY
  assignee_name
HAVING
  patent_count >= 5
ORDER BY
  patent_count DESC
LIMIT 100;

-- ============================================
-- Query 4: Temporal Analysis by Period
-- ============================================
WITH period_patents AS (
  SELECT
    p.publication_number,
    p.family_id,
    EXTRACT(YEAR FROM p.publication_date) as year,
    CASE
      WHEN EXTRACT(YEAR FROM p.publication_date) <= 2012 THEN 'pre_bri_baseline'
      WHEN EXTRACT(YEAR FROM p.publication_date) BETWEEN 2013 AND 2016 THEN 'bri_launch'
      WHEN EXTRACT(YEAR FROM p.publication_date) BETWEEN 2017 AND 2019 THEN 'expansion'
      WHEN EXTRACT(YEAR FROM p.publication_date) BETWEEN 2020 AND 2021 THEN 'trade_war'
      WHEN EXTRACT(YEAR FROM p.publication_date) >= 2022 THEN 'decoupling'
    END as period,
    p.title_localized[SAFE_OFFSET(0)].text as title,
    p.inventor_harmonized,
    p.assignee_harmonized
  FROM
    `patents-public-data.patents.publications` p
  WHERE
    p.country_code = 'CN'
    AND EXTRACT(YEAR FROM p.publication_date) BETWEEN 2000 AND 2025
),
period_collaborations AS (
  SELECT
    pp.period,
    pp.publication_number,
    inv.country_code as inventor_country
  FROM
    period_patents pp,
    UNNEST(pp.inventor_harmonized) as inv
  WHERE
    inv.country_code IS NOT NULL
    AND inv.country_code != 'CN'
    AND inv.country_code IN ('US','DE','FR','IT','ES','NL','BE','SE','DK','FI','NO','PL','CZ','SK','HU','RO','BG','HR','SI','EE','LV','LT','GR','CY','MT','PT','AT','IE','CH','GB','TR','UA','CA','AU','NZ','JP','KR','SG','TW','IN','IL','BR','RU')
)
SELECT
  period,
  inventor_country,
  COUNT(DISTINCT publication_number) as collab_count,
  ROUND(COUNT(DISTINCT publication_number) * 100.0 / SUM(COUNT(DISTINCT publication_number)) OVER (PARTITION BY period), 2) as pct_of_period
FROM
  period_collaborations
GROUP BY
  period, inventor_country
ORDER BY
  FIELD(period, 'pre_bri_baseline', 'bri_launch', 'expansion', 'trade_war', 'decoupling'),
  collab_count DESC;

-- ============================================
-- Query 5: Citation Network Analysis
-- ============================================
WITH china_citations AS (
  SELECT
    p.publication_number as citing_patent,
    p.country_code as citing_country,
    EXTRACT(YEAR FROM p.publication_date) as citing_year,
    cit.publication_number as cited_patent,
    cit_pub.country_code as cited_country,
    EXTRACT(YEAR FROM cit_pub.publication_date) as cited_year
  FROM
    `patents-public-data.patents.publications` p,
    UNNEST(p.citation) as cit,
    `patents-public-data.patents.publications` cit_pub
  WHERE
    p.country_code = 'CN'
    AND cit.publication_number = cit_pub.publication_number
    AND EXTRACT(YEAR FROM p.publication_date) BETWEEN 2015 AND 2025
    AND cit_pub.country_code IN ('US','DE','FR','IT','ES','NL','BE','SE','DK','FI','NO','PL','CZ','SK','HU','RO','BG','HR','SI','EE','LV','LT','GR','CY','MT','PT','AT','IE','CH','GB','TR','UA','CA','AU','NZ','JP','KR','SG','TW','IN','IL','BR','RU')
)
SELECT
  citing_year,
  cited_country,
  COUNT(*) as citation_count,
  AVG(citing_year - cited_year) as avg_citation_lag
FROM
  china_citations
GROUP BY
  citing_year, cited_country
ORDER BY
  citing_year DESC, citation_count DESC;
