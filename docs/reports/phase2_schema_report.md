# Phase 2: Schema Standardization & Joinability Analysis

Generated: 2025-09-24T17:37:07.333804

## Canonical Field Definitions

| Canonical Field | Description | Source Variations |
|----------------|-------------|-------------------|
| entity_id | Unique identifier | id, entity_id, org_id, company_id, institution_id |
| org_name | Organization name | name, organization, org_name, company_name, institution, beneficiary_name |
| country_iso | Country code | country, country_code, country_iso, iso_code, nation |
| year_month | Temporal field | date, year, publication_date, start_date, award_date |
| tech_keyword | Technology terms | keywords, technology, field, topic, domain |
| doc_id | Document ID | document_id, project_id, grant_id, contract_id, paper_id |
| china_related | China indicators | china, chinese, cn, prc, beijing, shanghai |

## Data Quality Scores (0-100)

| Source | Completeness | Total Records | Tables/Files |
|--------|--------------|---------------|--------------|
| OpenAIRE | 99.9% | 307,140 | 5 |
| CORDIS | 95.6% | 11,424 | 4 |
| CORDIS_China_Projects | 100.0% | 383 | 1 |
| Poland_China_Collab | 0.0% | 1 | 1 |

## Joinability Matrix (0-100 scores)

| Source | OpenAIRE | CORDIS | CORDIS_China_Projects | Poland_China_Collab |
|-|-|-|-|-|
| OpenAIRE | 100 | 58.3 | 50.0 | 25.0 |
| CORDIS | 0 | 100 | 75.0 | 14.9 |
| CORDIS_China_Projects | 0 | 0 | 100 | 0 |
| Poland_China_Collab | 0 | 0 | 0 | 100 |

## High-Value Join Opportunities (>60 score)

### CORDIS ↔ CORDIS_China_Projects
- **Score**: 75.0
- **Viable Join Fields**: entity_id, china_related
- **Common Fields**: entity_id, china_related


## Remediation Actions

⚠️ **Poland_China_Collab**: Low completeness (0.0%). Consider data enrichment or alternative sources.
⚠️ **CORDIS_China_Projects**: Low joinability (max 0.0%). May need entity resolution or aliasing.
⚠️ **Poland_China_Collab**: Low joinability (max 0.0%). May need entity resolution or aliasing.


## Artifacts Created

1. `phase2_schema_analysis.json` - Detailed schema mappings
2. `joinability_matrix.csv` - Joinability scores matrix
3. This report - Schema standardization documentation

## Phase 2 Complete ✓

- Canonical fields defined: 10
- Sources analyzed: 4
- Joinability pairs evaluated: 1
- Data quality assessed
