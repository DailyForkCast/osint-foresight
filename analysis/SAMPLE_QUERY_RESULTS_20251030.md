# Sample Query Results - Master Database Analysis
**Execution Date**: 2025-10-30 11:57:41
**Database**: F:/OSINT_WAREHOUSE/osint_master.db

---

## Executive Summary

- **Total Queries Executed**: 10
- **Successful**: 10
- **Failed**: 0
- **Total Rows Returned**: 104

---

## Query 1: China-Related Research Output (2020-2025)

**Description**: Temporal analysis of China-related research publications and datasets

**Execution Time**: 1.019s

**Rows Returned**: 6

**Sample Results** (first 10 rows):

```
1. (2025, 122, 107, 14)
2. (2024, 493, 447, 43)
3. (2023, 523, 507, 15)
4. (2022, 474, 416, 56)
5. (2021, 67, 65, 2)
6. (2020, 36, 25, 10)
```

**SQL Query:**
```sql

            SELECT
                year,
                COUNT(*) as total_publications,
                COUNT(CASE WHEN type = 'publication' THEN 1 END) as publications,
                COUNT(CASE WHEN type = 'dataset' THEN 1 END) as datasets
            FROM openaire_research
            WHERE china_related = 1 AND year >= 2020
            GROUP BY year
            ORDER BY year DESC
            
```

---

## Query 2: Research Trends - China vs Total (2015-2025)

**Description**: Year-over-year comparison showing China-related percentage of all research

**Execution Time**: 0.291s

**Rows Returned**: 11

**Sample Results** (first 10 rows):

```
1. (2025, 6898, 122, 1.77)
2. (2024, 14163, 493, 3.48)
3. (2023, 18379, 523, 2.85)
4. (2022, 17510, 474, 2.71)
5. (2021, 11516, 67, 0.58)
6. (2020, 10782, 36, 0.33)
7. (2019, 6213, 23, 0.37)
8. (2018, 4727, 18, 0.38)
9. (2017, 4539, 14, 0.31)
10. (2016, 4315, 30, 0.7)
```

**SQL Query:**
```sql

            SELECT
                year,
                COUNT(*) as total_research,
                SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) as china_related,
                ROUND(SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as china_pct
            FROM openaire_research
            WHERE year >= 2015 AND year <= 2025
            GROUP BY year
            ORDER BY year DESC
            
```

---

## Query 3: Top Countries by China Collaboration Volume

**Description**: Identifies primary research collaboration partners with China

**Execution Time**: 0.602s

**Rows Returned**: 1

**Sample Results** (first 10 rows):

```
1. ('HK', 508)
```

**SQL Query:**
```sql

            SELECT
                primary_country,
                COUNT(*) as collaboration_count
            FROM openaire_collaborations
            WHERE is_china_collaboration = 1
              AND primary_country IS NOT NULL
              AND primary_country <> ''
            GROUP BY primary_country
            ORDER BY collaboration_count DESC
            LIMIT 20
            
```

---

## Query 4: GLEIF Chinese Entity Distribution by Region

**Description**: Legal entities registered with LEI across Chinese territories

**Execution Time**: 11.505s

**Rows Returned**: 4

**Sample Results** (first 10 rows):

```
1. ('CN', 106890, 5)
2. ('HK', 11833, 5)
3. ('TW', 1655, 5)
4. ('MO', 98, 4)
```

**SQL Query:**
```sql

            SELECT
                legal_address_country,
                COUNT(*) as entity_count,
                COUNT(DISTINCT entity_category) as distinct_categories
            FROM gleif_entities
            WHERE legal_address_country IN ('CN', 'HK', 'MO', 'TW')
            GROUP BY legal_address_country
            ORDER BY entity_count DESC
            
```

---

## Query 5: Chinese Entities on Sanctions Lists

**Description**: Count and categorization of Chinese entities appearing on sanctions lists

**Execution Time**: 0.247s

**Rows Returned**: 7

**Sample Results** (first 10 rows):

```
1. ('CSV_Entity', 3553)
2. ('LegalEntity', 1751)
3. ('Address', 1590)
4. ('Identification', 113)
5. ('Organization', 95)
6. ('Passport', 69)
7. ('Person', 6)
```

**SQL Query:**
```sql

            SELECT
                entity_type,
                COUNT(*) as entity_count
            FROM opensanctions_entities
            WHERE china_related = 1
            GROUP BY entity_type
            ORDER BY entity_count DESC
            
```

---

## Query 6: GLEIF Relationship Network Scale

**Description**: Volume of corporate relationships by relationship type

**Execution Time**: 0.097s

**Rows Returned**: 6

**Sample Results** (first 10 rows):

```
1. ('IS_FUND-MANAGED_BY', 139734)
2. ('IS_ULTIMATELY_CONSOLIDATED_BY', 129873)
3. ('IS_DIRECTLY_CONSOLIDATED_BY', 123815)
4. ('IS_SUBFUND_OF', 68130)
5. ('IS_INTERNATIONAL_BRANCH_OF', 1777)
6. ('IS_FEEDER_TO', 1236)
```

**SQL Query:**
```sql

            SELECT
                relationship_type,
                COUNT(*) as relationship_count
            FROM gleif_relationships
            WHERE relationship_type IS NOT NULL
            GROUP BY relationship_type
            ORDER BY relationship_count DESC
            LIMIT 15
            
```

---

## Query 7: GLEIF Global Entity Distribution (Top 20 Countries)

**Description**: Legal entity counts by country - shows where LEI registration is most common

**Execution Time**: 0.256s

**Rows Returned**: 20

**Sample Results** (first 10 rows):

```
1. ('US', 333697)
2. ('IN', 300830)
3. ('IT', 235254)
4. ('DE', 234824)
5. ('GB', 215767)
6. ('ES', 179613)
7. ('NL', 174800)
8. ('FR', 166298)
9. ('SE', 111797)
10. ('DK', 107404)
```

**SQL Query:**
```sql

            SELECT
                legal_address_country as country,
                COUNT(*) as entity_count
            FROM gleif_entities
            WHERE legal_address_country IS NOT NULL
            GROUP BY legal_address_country
            ORDER BY entity_count DESC
            LIMIT 20
            
```

---

## Query 8: China-Related Research by Type

**Description**: Distribution of publication types in China-related research

**Execution Time**: 0.019s

**Rows Returned**: 4

**Sample Results** (first 10 rows):

```
1. ('publication', 2136, 93.19)
2. ('dataset', 148, 6.46)
3. ('other', 7, 0.31)
4. ('software', 1, 0.04)
```

**SQL Query:**
```sql

            SELECT
                type,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM openaire_research WHERE china_related = 1), 2) as percentage
            FROM openaire_research
            WHERE china_related = 1
            GROUP BY type
            ORDER BY count DESC
            
```

---

## Query 9: Sanctions List Geographic Distribution

**Description**: Countries with most entities on sanctions lists

**Execution Time**: 0.032s

**Rows Returned**: 20

**Sample Results** (first 10 rows):

```
1. ('[]', 36995)
2. ("['us']", 25519)
3. ("['ru']", 7595)
4. ("['ch']", 6374)
5. ("['eu']", 5540)
6. ("['gb']", 5317)
7. ("['cn']", 3379)
8. ("['au']", 3299)
9. ("['jp']", 2721)
10. ("['ir']", 2598)
```

**SQL Query:**
```sql

            SELECT
                countries,
                COUNT(*) as entity_count
            FROM opensanctions_entities
            WHERE countries IS NOT NULL
              AND countries <> ''
            GROUP BY countries
            ORDER BY entity_count DESC
            LIMIT 20
            
```

---

## Query 10: Recent China-Related Research (2024-2025)

**Description**: Most recent research publications involving China

**Execution Time**: 0.001s

**Rows Returned**: 25

**Sample Results** (first 10 rows):

```
1. (2025, 'HK', 'publication', 107)
2. (2025, 'HK', 'publication', 117)
3. (2025, 'HK', 'publication', 96)
4. (2025, 'HK', 'publication', 143)
5. (2025, 'HK', 'publication', 141)
6. (2025, 'HK', 'publication', 109)
7. (2025, 'HK', 'publication', 63)
8. (2025, 'HK', 'publication', 84)
9. (2025, 'HK', 'publication', 121)
10. (2025, 'HK', 'publication', 48)
```

**SQL Query:**
```sql

            SELECT
                year,
                countries,
                type,
                LENGTH(title) as title_length
            FROM openaire_research
            WHERE china_related = 1
              AND year >= 2024
            ORDER BY year DESC
            LIMIT 25
            
```

---

