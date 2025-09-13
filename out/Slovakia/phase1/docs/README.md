# Phase 1 OSINT Data Collection - Slovakia
**Generated: 2025-01-10**
**Timeframe: 2018-2025 (extended from 2015 where data available)**

## Executive Summary

This Phase 1 OSINT data collection addresses six critical gaps in Slovakia's R&D landscape understanding:
1. R&D budget allocations by institution
2. Chinese funding in Slovak research  
3. Dual-use research project proxies
4. Technology transfer statistics
5. Foreign researcher numbers and origins
6. Industry R&D investment data

Data was collected through web searches, with some limitations due to policy restrictions on certain China-related queries.

## Methodology

### Data Collection Approach
- **Primary Sources**: Eurostat, OECD, Slovak government agencies (APVV, VEGA, KEGA, SAS, CVTI SR)
- **Secondary Sources**: Previous phase reports, public databases, news sources
- **Languages Used**: English (primary), Slovak terms for targeted searches
- **Timeframe**: 2018-2025 (expanded from original 2015+ requirement)

### Search Restrictions Encountered
- **China Cooperation Details**: Some searches for Slovakia-China research cooperation were blocked by Claude Code usage policy
- **Mitigation**: Used data from Phase 1 report which identified 113 partnerships, including 25 with PLA-linked institutions

## Data Quality and Limitations

### Gap 1: R&D Budget Allocations
- **Coverage**: Partial - aggregate data available, institution-level detail limited
- **Quality**: Medium - relies on aggregate statistics from Eurostat and agency reports
- **Key Finding**: €551M Recovery Plan R&D allocation (2022-2026), SAS budget ~€60M annually

### Gap 2: Chinese Funding Mapping
- **Coverage**: Limited - based on Phase 1 report findings
- **Quality**: Medium - identified partnerships but amounts often unavailable
- **Key Finding**: 3 Confucius Institutes, multiple PLA-linked partnerships, Huawei contracts

### Gap 3: Dual-Use Research Proxies
- **Coverage**: Framework level - eligibility confirmed, specific projects not identified
- **Quality**: Low - proxy nature, no specific Slovak projects found
- **Key Finding**: Slovakia eligible for EDF (€8B budget 2021-2027) and NATO SPS programs

### Gap 4: Technology Transfer Statistics
- **Coverage**: Sparse - limited recent data
- **Quality**: Low - mostly older data (2016) or infrastructure metrics
- **Key Finding**: NITT SK project (€8.2M, 2010-2014), 11 PATLIB centers operational

### Gap 5: Foreign Researchers
- **Coverage**: Context available, specific counts limited
- **Quality**: Medium - percentages available, absolute numbers missing
- **Key Finding**: Foreign citizens only 1.2% of population, 51.6% researchers in HE sector

### Gap 6: Industry R&D (BERD)
- **Coverage**: Sectoral percentages, specific amounts limited
- **Quality**: Medium - structural data available, detailed breakdowns missing
- **Key Finding**: Automotive dominates (13.9% GDP), IoT market $1.2B (2024)

## Key Findings

### Funding Landscape
- Government R&D funding ~40.5% of total (2022)
- EU Recovery Plan massive injection: €6.4B total, €551M for R&D
- APVV remains main competitive funding agency (~€50M annual base)

### International Cooperation Risks
- 113 China partnerships identified (Phase 1)
- 25 partnerships with PLA-linked institutions
- 3 Confucius Institutes operational
- Low transparency in funding flows

### Technology Transfer Weakness
- Limited recent patent statistics
- No systematic TT metrics tracking
- Infrastructure exists (CVTI SR, NPTT) but data sparse
- Few spin-offs tracked

### Human Capital
- Very low foreign researcher presence (1.2% foreign citizens)
- Majority of researchers in HE sector (51.6%)
- Ukrainian researcher influx post-2022 (150+ hosted)

## Caveats and Methodological Notes

1. **Data Aggregation**: Much data only available at EU aggregate level, Slovakia-specific breakdowns often missing
2. **Time Lag**: Most recent comprehensive data from 2022, 2023-2025 often projections
3. **Institution Mapping**: Could not map budgets to specific institutions, only aggregate amounts
4. **China Data**: Direct searches blocked, relied on previous analysis
5. **Patent Data**: WIPO/EPO specific Slovak data not accessible via search
6. **Proxy Nature**: Dual-use projects identified by eligibility, not actual participation

## Files Produced

### Curated Data (CSV)
- `budgets_by_institution.csv` - 10 records, mostly aggregates
- `cn_funding_links.csv` - 9 partnerships identified
- `dual_use_projects_proxy.csv` - 9 eligibility records
- `tech_transfer_stats.csv` - 10 metrics, mixed years
- `foreign_researchers.csv` - 9 contextual records
- `berd_by_industry.csv` - 14 records, sectoral data

### Documentation
- `provenance.jsonl` - Source tracking for all data
- `README.md` - This file
- `OPEN_QUESTIONS.md` - Unresolved items requiring follow-up

## Data Usage Notes

- All amounts in EUR unless specified
- Null values indicate data not available, not zero
- Years may be inconsistent across datasets due to availability
- Confidence highest for EU-funded programs, lowest for bilateral arrangements
- China partnership data from Phase 1 (different methodology)

## Validation Status

✓ All six CSV files created with 2015+ coverage where available
✓ Provenance log complete for all sources
✓ Schemas match specification
⚠ Institution-level budget detail not achieved
⚠ China funding amounts largely unavailable
⚠ Specific dual-use projects not identified

## Next Steps

1. Request official data from Slovak authorities for institution-level budgets
2. Access CORDIS API directly for specific project data
3. Contact CVTI SR for recent tech transfer statistics
4. Explore alternative sources for China funding data
5. Query Eurostat database directly for rd_p_perscitz indicator