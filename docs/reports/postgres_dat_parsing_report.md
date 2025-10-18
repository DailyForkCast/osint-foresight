# PostgreSQL .dat Files Parsing Report

Generated: 2025-09-25T14:43:13.362141

## Summary

- Files found: 66
- Files parsed: 45
- Total rows extracted: 9,397,541
- Parse errors: 0

## Table Structures Found

### int.duns
- Columns: 21
  - awardee_or_recipient_uniqu: text
  - legal_business_name: text
  - ultimate_parent_unique_ide: text
  - ultimate_parent_legal_enti: text
  - broker_duns_id: text

### int.transaction_delta
- Columns: 5
  - transaction_id: bigint
  - NOT: NULL
  - created_at: timestamp
  - with: time
  - zone: NOT

### public.agency
- Columns: 15
  - id: integer
  - NOT: NULL
  - create_date: timestamp
  - with: time
  - zone: NOT

### public.subtier_agency
- Columns: 13
  - subtier_agency_id: integer
  - NOT: NULL
  - create_date: timestamp
  - with: time
  - zone: NOT

### public.toptier_agency
- Columns: 18
  - toptier_agency_id: integer
  - NOT: NULL
  - create_date: timestamp
  - with: time
  - zone: NOT

### public.appropriation_account_balances
- Columns: 43
  - data_source: text
  - appropriation_account_balances_id: integer
  - NOT: NULL
  - budget_authority_unobligated_balance_brought_forward_fyb: numeric(23,2)
  - adjustments_to_unobligated_balance_brought_forward_cpe: numeric(23,2)

### public.auth_group
- Columns: 4
  - id: integer
  - NOT: NULL
  - name: character
  - NOT: NULL

### public.auth_group_permissions
- Columns: 6
  - id: integer
  - NOT: NULL
  - group_id: integer
  - NOT: NULL
  - permission_id: integer

### public.auth_permission
- Columns: 8
  - id: integer
  - NOT: NULL
  - name: character
  - NOT: NULL
  - content_type_id: integer

### public.auth_user
- Columns: 23
  - id: integer
  - NOT: NULL
  - password: character
  - NOT: NULL
  - last_login: timestamp

## Data Insights

- Total tables processed: 45
- Total data rows: 9,397,541

### Data Patterns Found

- **financial_values**: 792 instances
  - 1
  - 2
  - 3
- **dates**: 257 instances
  - 2018-01-31 19:51:40.561521+00
  - 2018-01-31 19:51:41.094525+00
  - 2018-01-31 19:51:41.274193+00
- **possible_orgs**: 287 instances
  - Department of Labor
  - Commodity Futures Trading Commission
  - Federal Permitting Improvement Steering Council

## Next Steps

1. Consider restoring to PostgreSQL for full access
2. Focus on specific tables of interest
3. Build targeted extractors for key data types
