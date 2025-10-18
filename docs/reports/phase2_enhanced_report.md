# Phase 2: Schema Standardization Report (Enhanced)

Generated: 2025-09-24T18:00:22.699958

## Standardization Summary

| Metric | Value |
|--------|-------|
| Canonical Fields Defined | 24 |
| Sources Mapped | 10 |
| High-Viability Pairs | 0 |
| Successful Joins Executed | 0 |

## Canonical Field Categories

### Entity Fields
- **entity_id**: Unique identifier for entity
- **entity_name**: Name of organization/person
- **entity_type**: Type: organization/person/project
- **entity_country**: Country code (ISO-2)

### Temporal Fields
- **date**: Primary date field
- **start_date**: Start date of activity
- **end_date**: End date of activity
- **year**: Year of activity

### Geographic Fields
- **country**: Country name
- **country_code**: ISO country code
- **region**: Geographic region
- **city**: City name

### Financial Fields
- **amount**: Monetary amount
- **currency**: Currency code
- **funding_type**: Type of funding

### Technology Fields
- **technology**: Technology area
- **sector**: Industry sector
- **keywords**: Associated keywords

### Relationship Fields
- **partner_id**: Partner entity ID
- **partner_name**: Partner name
- **relationship_type**: Type of relationship

### Metadata Fields
- **source**: Data source
- **confidence**: Confidence score 0-100
- **last_updated**: Last update date

## Field Mapping Coverage

Average field coverage: 27.2%

### Top Mapped Sources
- **project_data_sample_001**: 61.5% coverage (8 fields mapped)
- **project_data_sample_002**: 61.5% coverage (8 fields mapped)
- **project_data_sample_003**: 61.5% coverage (8 fields mapped)
- **osint_data_sample_002**: 28.6% coverage (4 fields mapped)
- **project_data_sample_005**: 25.0% coverage (3 fields mapped)

## Joinability Matrix Summary

### High-Viability Join Pairs (>50 score)

## Data Quality Scorecards (0-100 Scale)

### Average Quality Metrics
- **Completeness**: 50.0/100
- **Consistency**: 72.9/100
- **Validity**: 85.8/100
- **Uniqueness**: 86.7/100
- **Timeliness**: 71.8/100
- **Overall**: 70.5/100

## Sample Successful Joins

## Artifacts Created

1. `canonical_fields.json` - Complete canonical field definitions
2. `joinability_matrix.csv` - Pairwise joinability scores
3. `data_quality_scorecards.json` - Quality metrics (0-100 scale)
4. `successful_joins.json` - 10 random joins per high-viability pair
5. `field_mappings.json` - Source to canonical mappings

## Phase 2 Complete ✓

Schema standardization completed with 27.2% average field coverage.
0 high-viability join pairs identified with 0 successful joins demonstrated.
