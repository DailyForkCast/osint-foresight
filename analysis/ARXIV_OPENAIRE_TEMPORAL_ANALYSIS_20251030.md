# arXiv + OpenAIRE Temporal Analysis
**Generated**: 2025-10-30 18:37:51
**Master Database**: F:/OSINT_WAREHOUSE/osint_master.db
**arXiv Database**: C:/Projects/OSINT-Foresight/data/kaggle_arxiv_processing.db

---

## Executive Summary

- **Total Queries**: 10
- **Successful**: 2
- **Failed**: 8

---

## Openaire Temporal Trends

**Description**: OpenAIRE research output by year (2015-2025)

**Rows Returned**: 11

**Results**:

```
(2025, 6898, 122, 1.77)
(2024, 14163, 493, 3.48)
(2023, 18379, 523, 2.85)
(2022, 17510, 474, 2.71)
(2021, 11516, 67, 0.58)
(2020, 10782, 36, 0.33)
(2019, 6213, 23, 0.37)
(2018, 4727, 18, 0.38)
(2017, 4539, 14, 0.31)
(2016, 4315, 30, 0.7)
(2015, 4455, 18, 0.4)
```

**SQL**:
```sql

            SELECT
                year,
                COUNT(*) as total_publications,
                SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) as china_related,
                ROUND(SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as china_pct
            FROM openaire_research
            WHERE year >= 2015 AND year <= 2025
            GROUP BY year
            ORDER BY year DESC
            
```

---

## Arxiv Year Distribution

**Description**: arXiv paper publication years - check data range

**ERROR**: no such column: year

**SQL**:
```sql

            SELECT
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                COUNT(*) as total_papers,
                COUNT(DISTINCT year) as distinct_years
            FROM arxiv.kaggle_arxiv_papers
            WHERE year IS NOT NULL
            
```

---

## Arxiv Temporal Trends

**Description**: arXiv paper output by year (2015-2025)

**ERROR**: no such column: year

**SQL**:
```sql

            SELECT
                year,
                COUNT(*) as total_papers
            FROM arxiv.kaggle_arxiv_papers
            WHERE year >= 2015 AND year <= 2025
              AND year IS NOT NULL
            GROUP BY year
            ORDER BY year DESC
            
```

---

## Arxiv Technology Temporal

**Description**: arXiv papers by technology domain (2015-2025)

**ERROR**: no such column: p.year

**SQL**:
```sql

            SELECT
                p.year,
                t.technology_domain,
                COUNT(*) as paper_count
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_technology t ON p.id = t.paper_id
            WHERE p.year >= 2015 AND p.year <= 2025
              AND p.year IS NOT NULL
              AND t.technology_domain IS NOT NULL
            GROUP BY p.year, t.technology_domain
            ORDER BY p.year DESC, paper_count DESC
            
```

---

## Arxiv China Indicators

**Description**: Identify China-related papers in arXiv (author affiliations sample)

**ERROR**: no such column: p.year

**SQL**:
```sql

            SELECT
                p.year,
                COUNT(DISTINCT p.id) as papers_with_china_authors
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_authors a ON p.id = a.paper_id
            WHERE (
                LOWER(a.affiliation) LIKE '%china%'
                OR LOWER(a.affiliation) LIKE '%chinese%'
                OR LOWER(a.affiliation) LIKE '%beijing%'
                OR LOWER(a.affiliation) LIKE '%shanghai%'
                OR LOWER(a.affiliation) LIKE '%tsinghua%'
                OR LOWER(a.affiliation) LIKE '%peking university%'
            )
            AND p.year >= 2015 AND p.year <= 2025
            AND p.year IS NOT NULL
            GROUP BY p.year
            ORDER BY p.year DESC
            
```

---

## Combined Dataset Stats

**Description**: Combined OpenAIRE + arXiv coverage statistics

**ERROR**: no such column: year

**SQL**:
```sql

            SELECT
                'OpenAIRE' as source,
                COUNT(*) as total_records,
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                SUM(CASE WHEN china_related = 1 THEN 1 ELSE 0 END) as china_related_records
            FROM openaire_research
            WHERE year IS NOT NULL

            UNION ALL

            SELECT
                'arXiv' as source,
                COUNT(*) as total_records,
                MIN(year) as earliest_year,
                MAX(year) as latest_year,
                NULL as china_related_records
            FROM arxiv.kaggle_arxiv_papers
            WHERE year IS NOT NULL
            
```

---

## Yoy Growth Comparison

**Description**: Year-over-year growth rates: OpenAIRE vs arXiv

**ERROR**: no such column: year

**SQL**:
```sql

            WITH openaire_yearly AS (
                SELECT year, COUNT(*) as count
                FROM openaire_research
                WHERE year >= 2015 AND year <= 2025
                GROUP BY year
            ),
            arxiv_yearly AS (
                SELECT year, COUNT(*) as count
                FROM arxiv.kaggle_arxiv_papers
                WHERE year >= 2015 AND year <= 2025
                  AND year IS NOT NULL
                GROUP BY year
            )
            SELECT
                o.year,
                o.count as openaire_count,
                a.count as arxiv_count,
                ROUND((o.count * 100.0 / (SELECT SUM(count) FROM openaire_yearly)), 2) as openaire_pct,
                ROUND((a.count * 100.0 / (SELECT SUM(count) FROM arxiv_yearly)), 2) as arxiv_pct
            FROM openaire_yearly o
            LEFT JOIN arxiv_yearly a ON o.year = a.year
            ORDER BY o.year DESC
            
```

---

## Arxiv Top Categories Recent

**Description**: Most active arXiv categories (2020-2025)

**ERROR**: no such column: p.id

**SQL**:
```sql

            SELECT
                c.category,
                COUNT(DISTINCT p.id) as paper_count,
                COUNT(DISTINCT p.year) as years_active
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_categories c ON p.id = c.paper_id
            WHERE p.year >= 2020 AND p.year <= 2025
              AND p.year IS NOT NULL
              AND c.category IS NOT NULL
            GROUP BY c.category
            ORDER BY paper_count DESC
            LIMIT 20
            
```

---

## China Research Growth

**Description**: China-related research growth: OpenAIRE baseline vs arXiv potential

**Rows Returned**: 11

**Results**:

```
(2025, 122, 5.32)
(2024, 493, 21.51)
(2023, 523, 22.82)
(2022, 474, 20.68)
(2021, 67, 2.92)
(2020, 36, 1.57)
(2019, 23, 1.0)
(2018, 18, 0.79)
(2017, 14, 0.61)
(2016, 30, 1.31)
(2015, 18, 0.79)
```

**SQL**:
```sql

            SELECT
                year,
                COUNT(*) as openaire_china_papers,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM openaire_research WHERE china_related = 1), 2) as pct_of_total
            FROM openaire_research
            WHERE china_related = 1
              AND year >= 2015 AND year <= 2025
            GROUP BY year
            ORDER BY year DESC
            
```

---

## Technology Domain Distribution

**Description**: arXiv technology domains - strategic technology focus

**ERROR**: no such column: paper_id

**SQL**:
```sql

            SELECT
                technology_domain,
                COUNT(DISTINCT paper_id) as papers,
                ROUND(COUNT(DISTINCT paper_id) * 100.0 / (SELECT COUNT(DISTINCT paper_id) FROM arxiv.kaggle_arxiv_technology), 2) as pct
            FROM arxiv.kaggle_arxiv_technology
            WHERE technology_domain IS NOT NULL
            GROUP BY technology_domain
            ORDER BY papers DESC
            LIMIT 15
            
```

---

