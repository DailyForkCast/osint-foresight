# arXiv + OpenAIRE Temporal Analysis (v2 - Schema Corrected)
**Generated**: 2025-10-30 18:44:16
**Master Database**: F:/OSINT_WAREHOUSE/osint_master.db
**arXiv Database**: C:/Projects/OSINT-Foresight/data/kaggle_arxiv_processing.db

---

## Executive Summary

- **Total Queries**: 10
- **Successful**: 10
- **Failed**: 0

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

**Rows Returned**: 1

**Results**:

```
(1990, 2025, 1442797, 36)
```

**SQL**:
```sql

            SELECT
                MIN(submission_year) as earliest_year,
                MAX(submission_year) as latest_year,
                COUNT(*) as total_papers,
                COUNT(DISTINCT submission_year) as distinct_years
            FROM arxiv.kaggle_arxiv_papers
            WHERE submission_year IS NOT NULL
            
```

---

## Arxiv Temporal Trends

**Description**: arXiv paper output by year (2015-2025)

**Rows Returned**: 11

**Results**:

```
(2025, 95391)
(2024, 118383)
(2023, 105109)
(2022, 93946)
(2021, 92355)
(2020, 90567)
(2019, 77574)
(2018, 69673)
(2017, 60754)
(2016, 56153)
(2015, 52565)
```

**SQL**:
```sql

            SELECT
                submission_year as year,
                COUNT(*) as total_papers
            FROM arxiv.kaggle_arxiv_papers
            WHERE submission_year >= 2015 AND submission_year <= 2025
              AND submission_year IS NOT NULL
            GROUP BY submission_year
            ORDER BY submission_year DESC
            
```

---

## Arxiv Technology Temporal

**Description**: arXiv papers by technology domain (2015-2025)

**Rows Returned**: 99

**Results**:

```
(2025, 'AI', 50560)
(2025, 'Semiconductors', 33188)
(2025, 'Space', 19735)
(2025, 'Energy', 18156)
(2025, 'Quantum', 13283)
(2025, 'Neuroscience', 11596)
(2025, 'Smart_City', 7641)
(2025, 'Advanced_Materials', 6768)
(2025, 'Biotechnology', 2342)
(2024, 'AI', 61928)
(2024, 'Semiconductors', 39610)
(2024, 'Space', 24479)
(2024, 'Energy', 22582)
(2024, 'Quantum', 16586)
(2024, 'Neuroscience', 15233)
(2024, 'Smart_City', 9294)
(2024, 'Advanced_Materials', 8718)
(2024, 'Biotechnology', 3021)
(2023, 'AI', 51365)
(2023, 'Semiconductors', 36669)
(2023, 'Space', 23040)
(2023, 'Energy', 20785)
(2023, 'Quantum', 15154)
(2023, 'Neuroscience', 14454)
(2023, 'Advanced_Materials', 8628)
(2023, 'Smart_City', 7964)
(2023, 'Biotechnology', 2799)
(2022, 'AI', 42521)
(2022, 'Semiconductors', 34480)
(2022, 'Space', 22016)
(2022, 'Energy', 19085)
(2022, 'Quantum', 14136)
(2022, 'Neuroscience', 13684)
(2022, 'Advanced_Materials', 8052)
(2022, 'Smart_City', 6930)
(2022, 'Biotechnology', 2624)
(2021, 'AI', 39697)
(2021, 'Semiconductors', 34568)
(2021, 'Space', 21858)
(2021, 'Energy', 19435)
(2021, 'Quantum', 14221)
(2021, 'Neuroscience', 13688)
(2021, 'Advanced_Materials', 8761)
(2021, 'Smart_City', 7135)
(2021, 'Biotechnology', 3084)
(2020, 'AI', 36221)
(2020, 'Semiconductors', 34546)
(2020, 'Space', 22010)
(2020, 'Energy', 19547)
(2020, 'Quantum', 13796)
```

**SQL**:
```sql

            SELECT
                p.submission_year as year,
                t.technology_domain,
                COUNT(*) as paper_count
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_technology t ON p.arxiv_id = t.arxiv_id
            WHERE p.submission_year >= 2015 AND p.submission_year <= 2025
              AND p.submission_year IS NOT NULL
              AND t.technology_domain IS NOT NULL
            GROUP BY p.submission_year, t.technology_domain
            ORDER BY p.submission_year DESC, paper_count DESC
            
```

---

## Arxiv China Indicators

**Description**: Identify China-related papers in arXiv by author affiliations

**Rows Returned**: 11

**Results**:

```
(2025, 12)
(2024, 19)
(2023, 18)
(2022, 26)
(2021, 21)
(2020, 20)
(2019, 12)
(2018, 14)
(2017, 9)
(2016, 12)
(2015, 20)
```

**SQL**:
```sql

            SELECT
                p.submission_year as year,
                COUNT(DISTINCT p.arxiv_id) as papers_with_china_authors
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_authors a ON p.arxiv_id = a.arxiv_id
            WHERE (
                a.inferred_country IN ('CN', 'HK', 'TW', 'MO')
                OR LOWER(a.inferred_affiliation) LIKE '%china%'
                OR LOWER(a.inferred_affiliation) LIKE '%chinese%'
                OR LOWER(a.inferred_affiliation) LIKE '%beijing%'
                OR LOWER(a.inferred_affiliation) LIKE '%shanghai%'
                OR LOWER(a.inferred_affiliation) LIKE '%tsinghua%'
                OR LOWER(a.inferred_affiliation) LIKE '%peking university%'
            )
            AND p.submission_year >= 2015 AND p.submission_year <= 2025
            AND p.submission_year IS NOT NULL
            GROUP BY p.submission_year
            ORDER BY p.submission_year DESC
            
```

---

## Combined Dataset Stats

**Description**: Combined OpenAIRE + arXiv coverage statistics

**Rows Returned**: 2

**Results**:

```
('OpenAIRE', 156221, 0, 9999, 2292)
('arXiv', 1442797, 1990, 2025, None)
```

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
                MIN(submission_year) as earliest_year,
                MAX(submission_year) as latest_year,
                NULL as china_related_records
            FROM arxiv.kaggle_arxiv_papers
            WHERE submission_year IS NOT NULL
            
```

---

## Yoy Growth Comparison

**Description**: Year-over-year growth rates: OpenAIRE vs arXiv

**Rows Returned**: 11

**Results**:

```
(2025, 6898, 95391, 6.66, 10.45)
(2024, 14163, 118383, 13.68, 12.97)
(2023, 18379, 105109, 17.76, 11.52)
(2022, 17510, 93946, 16.92, 10.3)
(2021, 11516, 92355, 11.13, 10.12)
(2020, 10782, 90567, 10.42, 9.93)
(2019, 6213, 77574, 6.0, 8.5)
(2018, 4727, 69673, 4.57, 7.64)
(2017, 4539, 60754, 4.39, 6.66)
(2016, 4315, 56153, 4.17, 6.15)
(2015, 4455, 52565, 4.3, 5.76)
```

**SQL**:
```sql

            WITH openaire_yearly AS (
                SELECT year, COUNT(*) as count
                FROM openaire_research
                WHERE year >= 2015 AND year <= 2025
                GROUP BY year
            ),
            arxiv_yearly AS (
                SELECT submission_year as year, COUNT(*) as count
                FROM arxiv.kaggle_arxiv_papers
                WHERE submission_year >= 2015 AND submission_year <= 2025
                  AND submission_year IS NOT NULL
                GROUP BY submission_year
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

**Rows Returned**: 20

**Results**:

```
('cs.LG', 105044, 6)
('cs.CV', 80678, 6)
('cs.AI', 69386, 6)
('quant-ph', 48989, 6)
('cs.CL', 48155, 6)
('gr-qc', 33489, 6)
('astro-ph.GA', 31573, 6)
('hep-th', 28451, 6)
('hep-ph', 28149, 6)
('astro-ph.HE', 26417, 6)
('cs.RO', 23250, 6)
('astro-ph.CO', 22839, 6)
('cond-mat.mtrl-sci', 22804, 6)
('astro-ph.SR', 22622, 6)
('cond-mat.mes-hall', 21338, 6)
('stat.ML', 20765, 6)
('eess.SP', 16785, 6)
('cond-mat.str-el', 15185, 6)
('astro-ph.IM', 13781, 6)
('astro-ph.EP', 13710, 6)
```

**SQL**:
```sql

            SELECT
                c.category,
                COUNT(DISTINCT p.arxiv_id) as paper_count,
                COUNT(DISTINCT p.submission_year) as years_active
            FROM arxiv.kaggle_arxiv_papers p
            JOIN arxiv.kaggle_arxiv_categories c ON p.arxiv_id = c.arxiv_id
            WHERE p.submission_year >= 2020 AND p.submission_year <= 2025
              AND p.submission_year IS NOT NULL
              AND c.category IS NOT NULL
            GROUP BY c.category
            ORDER BY paper_count DESC
            LIMIT 20
            
```

---

## China Research Growth

**Description**: China-related research growth: OpenAIRE baseline

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

**Rows Returned**: 9

**Results**:

```
('Semiconductors', 588846, 40.81)
('Space', 424215, 29.4)
('AI', 413219, 28.64)
('Energy', 309182, 21.43)
('Quantum', 271118, 18.79)
('Advanced_Materials', 163992, 11.37)
('Neuroscience', 128581, 8.91)
('Smart_City', 77864, 5.4)
('Biotechnology', 40212, 2.79)
```

**SQL**:
```sql

            SELECT
                technology_domain,
                COUNT(DISTINCT arxiv_id) as papers,
                ROUND(COUNT(DISTINCT arxiv_id) * 100.0 / (SELECT COUNT(DISTINCT arxiv_id) FROM arxiv.kaggle_arxiv_technology), 2) as pct
            FROM arxiv.kaggle_arxiv_technology
            WHERE technology_domain IS NOT NULL
            GROUP BY technology_domain
            ORDER BY papers DESC
            LIMIT 15
            
```

---

