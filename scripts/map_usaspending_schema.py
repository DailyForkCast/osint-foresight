#!/usr/bin/env python3
"""
USAspending Schema Mapper

Maps all 206 columns in USAspending PostgreSQL dump files to their proper names
and categories based on data patterns and USAspending data dictionary.

Input: F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz
Output: analysis/USASPENDING_COMPLETE_SCHEMA.md
"""

import gzip
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

# Based on USAspending data dictionary and data analysis
COLUMN_MAPPING = {
    # Transaction timestamps (0-1)
    0: ("create_date", "Timestamp", "Database record creation timestamp"),
    1: ("update_date", "Timestamp", "Database record last modified timestamp"),

    # Transaction IDs (2-8)
    2: ("transaction_id", "Transaction", "Internal database transaction ID"),
    3: ("generated_unique_award_id", "Transaction", "USAspending generated unique award identifier"),
    4: ("piid", "Transaction", "Procurement Instrument Identifier (contract number)"),
    5: ("parent_award_id", "Transaction", "Parent IDV/award identifier"),
    6: ("federal_action_obligation", "Financial", "Transaction dollar amount"),
    7: ("action_date", "Transaction", "Date of the transaction action"),
    8: ("fiscal_year", "Transaction", "Fiscal year of transaction"),

    # Funding Agency (9-20)
    9: ("funding_toptier_agency_id", "Agency", "Funding agency top-tier code"),
    10: ("funding_toptier_agency_name", "Agency", "Funding agency top-tier name"),
    11: ("funding_subtier_agency_code", "Agency", "Funding agency subtier code"),
    12: ("funding_subtier_agency_name", "Agency", "Funding agency subtier name"),
    13: ("funding_office_code", "Agency", "Funding office code"),
    14: ("funding_office_name", "Agency", "Funding office name"),

    # Awarding Agency (15-20)
    15: ("awarding_toptier_agency_id", "Agency", "Awarding agency top-tier code"),
    16: ("awarding_toptier_agency_name", "Agency", "Awarding agency top-tier name"),
    17: ("awarding_subtier_agency_code", "Agency", "Awarding agency subtier code"),
    18: ("awarding_subtier_agency_name", "Agency", "Awarding agency subtier name"),
    19: ("awarding_office_code", "Agency", "Awarding office code"),
    20: ("awarding_office_name", "Agency", "Awarding office name"),

    # Prime Recipient (21-45)
    21: ("recipient_duns", "Recipient", "Prime recipient DUNS number"),
    22: ("recipient_uei", "Recipient", "Prime recipient Unique Entity Identifier"),
    23: ("recipient_name", "Recipient", "Prime recipient legal business name"),
    24: ("recipient_doing_business_as_name", "Recipient", "Prime recipient DBA name"),
    25: ("recipient_parent_duns", "Recipient", "Prime recipient parent DUNS"),
    26: ("recipient_parent_uei", "Recipient", "Prime recipient parent UEI"),
    27: ("recipient_parent_name", "Recipient", "Prime recipient ultimate parent name"),
    28: ("recipient_location_country_code", "Location", "Prime recipient country code"),
    29: ("recipient_location_country_name", "Location", "Prime recipient country name"),
    30: ("recipient_location_state_code", "Location", "Prime recipient state code"),
    31: ("recipient_location_state_name", "Location", "Prime recipient state name"),
    32: ("recipient_location_zip_code", "Location", "Prime recipient ZIP code"),
    33: ("recipient_location_congressional_code", "Location", "Prime recipient congressional district"),
    34: ("recipient_location_county_code", "Location", "Prime recipient county code"),
    35: ("recipient_location_city_name", "Location", "Prime recipient city"),
    36: ("recipient_location_address_line1", "Location", "Prime recipient street address"),
    37: ("business_categories", "Recipient", "Business type classifications"),

    # Place of Performance (38-45)
    38: ("pop_country_code", "Location", "Place of performance country code"),
    39: ("pop_country_name", "Location", "Place of performance country name"),
    40: ("pop_state_code", "Location", "Place of performance state code"),
    41: ("pop_state_name", "Location", "Place of performance state name"),
    42: ("pop_zip_code", "Location", "Place of performance ZIP code"),
    43: ("pop_congressional_code", "Location", "Place of performance congressional district"),
    44: ("pop_city_name", "Location", "Place of performance city"),
    45: ("pop_address_line1", "Location", "Place of performance address"),

    # Award Description (46-50)
    46: ("award_description", "Description", "Description of the award/contract"),
    47: ("naics_code", "Classification", "NAICS industry classification code"),
    48: ("naics_description", "Classification", "NAICS industry description"),
    49: ("cfda_number", "Classification", "CFDA program number (grants)"),
    50: ("cfda_title", "Classification", "CFDA program title (grants)"),

    # Sub-Award Information (51-81)
    51: ("prime_award_transaction_type", "Transaction", "Sub-award or sub-grant indicator"),
    52: ("subaward_action_date_fiscal_year", "Subaward", "Sub-award fiscal year"),
    53: ("subaward_action_date_month", "Subaward", "Sub-award month"),
    54: ("subaward_number", "Subaward", "Sub-award identifier"),
    55: ("subaward_amount", "Subaward", "Sub-award dollar amount"),
    56: ("sub_action_date", "Subaward", "Sub-award action date"),
    57: ("sub_awardee_duns", "Subaward", "Sub-awardee DUNS number"),
    58: ("sub_awardee_uei", "Subaward", "Sub-awardee UEI"),
    59: ("sub_awardee_name", "Subaward", "Sub-awardee name"),
    60: ("sub_awardee_doing_business_as_name", "Subaward", "Sub-awardee DBA name"),
    61: ("sub_awardee_parent_duns", "Subaward", "Sub-awardee parent DUNS"),
    62: ("sub_awardee_parent_uei", "Subaward", "Sub-awardee parent UEI"),
    63: ("sub_awardee_parent_name", "Subaward", "Sub-awardee parent name"),
    64: ("sub_awardee_country_code", "Subaward", "Sub-awardee country code"),
    65: ("sub_awardee_country_name", "Subaward", "Sub-awardee country name"),
    66: ("sub_awardee_state_code", "Subaward", "Sub-awardee state code"),
    67: ("sub_awardee_state_name", "Subaward", "Sub-awardee state name"),
    68: ("sub_awardee_zip_code", "Subaward", "Sub-awardee ZIP code"),
    69: ("sub_awardee_congressional_code", "Subaward", "Sub-awardee congressional district"),
    70: ("sub_awardee_county_code", "Subaward", "Sub-awardee county code"),
    71: ("sub_awardee_city_name", "Subaward", "Sub-awardee city"),
    72: ("sub_awardee_address_line1", "Subaward", "Sub-awardee address"),
    73: ("sub_awardee_business_categories", "Subaward", "Sub-awardee business types"),

    # Sub-Award Place of Performance (74-81)
    74: ("sub_pop_country_code", "Subaward", "Sub-award place of performance country code"),
    75: ("sub_pop_country_name", "Subaward", "Sub-award place of performance country"),
    76: ("sub_pop_state_code", "Subaward", "Sub-award place of performance state code"),
    77: ("sub_pop_state_name", "Subaward", "Sub-award place of performance state"),
    78: ("sub_pop_zip_code", "Subaward", "Sub-award place of performance ZIP"),
    79: ("sub_pop_congressional_code", "Subaward", "Sub-award place of performance congressional district"),
    80: ("sub_pop_city_name", "Subaward", "Sub-award place of performance city"),
    81: ("sub_pop_address_line1", "Subaward", "Sub-award place of performance address"),

    # Extended Description (82-93)
    82: ("subaward_description", "Description", "Detailed sub-award description"),
    83: ("business_categories_array", "Recipient", "Business categories as array"),
    84: ("award_latest_action_date", "Transaction", "Latest action date for award"),
    85: ("award_latest_action_date_fiscal_year", "Transaction", "Latest action fiscal year"),
    86: ("award_base_action_date", "Transaction", "Base action date"),
    87: ("award_base_action_date_fiscal_year", "Transaction", "Base action fiscal year"),
    88: ("period_of_performance_start_date", "Transaction", "Performance start date"),
    89: ("period_of_performance_current_end_date", "Transaction", "Performance current end date"),
    90: ("period_of_performance_potential_end_date", "Transaction", "Performance potential end date"),
    91: ("ordering_period_end_date", "Transaction", "IDV ordering period end"),
    92: ("solicitation_date", "Transaction", "Solicitation date"),
    93: ("awarding_agency_code", "Agency", "Awarding agency code"),

    # System Fields (94-98)
    94: ("internal_id", "System", "Internal system identifier (UUID)"),
    95: ("date_signed", "Transaction", "Date contract was signed"),
    96: ("treasury_accounts_funding_this_award", "Financial", "Treasury account codes"),
    97: ("federal_accounts_funding_this_award", "Financial", "Federal account codes"),
    98: ("object_classes_funding_this_award", "Financial", "Object class codes"),

    # Additional Agency Fields (99-109)
    99: ("funding_agency_code", "Agency", "Funding agency code"),
    100: ("funding_agency_name", "Agency", "Funding agency name"),
    101: ("funding_sub_agency_code", "Agency", "Funding sub-agency code"),
    102: ("funding_sub_agency_name", "Agency", "Funding sub-agency name"),
    103: ("funding_office_code_2", "Agency", "Funding office code (duplicate)"),
    104: ("funding_office_name_2", "Agency", "Funding office name (duplicate)"),
    105: ("awarding_agency_code_2", "Agency", "Awarding agency code (duplicate)"),
    106: ("awarding_agency_name_2", "Agency", "Awarding agency name (duplicate)"),
    107: ("awarding_sub_agency_code", "Agency", "Awarding sub-agency code"),
    108: ("awarding_sub_agency_name", "Agency", "Awarding sub-agency name"),
    109: ("awarding_office_code_2", "Agency", "Awarding office code (duplicate)"),

    # Highly-Compensated Officers (110-119)
    110: ("officer_1_name", "Recipient", "Highly compensated officer #1 name"),
    111: ("officer_1_amount", "Recipient", "Highly compensated officer #1 amount"),
    112: ("officer_2_name", "Recipient", "Highly compensated officer #2 name"),
    113: ("officer_2_amount", "Recipient", "Highly compensated officer #2 amount"),
    114: ("officer_3_name", "Recipient", "Highly compensated officer #3 name"),
    115: ("officer_3_amount", "Recipient", "Highly compensated officer #3 amount"),
    116: ("officer_4_name", "Recipient", "Highly compensated officer #4 name"),
    117: ("officer_4_amount", "Recipient", "Highly compensated officer #4 amount"),
    118: ("officer_5_name", "Recipient", "Highly compensated officer #5 name"),
    119: ("officer_5_amount", "Recipient", "Highly compensated officer #5 amount"),

    # Additional IDs and Codes (120-135)
    120: ("fain", "Transaction", "Federal Award Identification Number (grants)"),
    121: ("uri", "Transaction", "URI for other awards"),
    122: ("funding_agency_code_3", "Agency", "Funding agency code (3rd instance)"),
    123: ("funding_agency_name_3", "Agency", "Funding agency name (3rd instance)"),
    124: ("funding_sub_agency_code_2", "Agency", "Funding sub-agency code (2nd instance)"),
    125: ("funding_sub_agency_name_2", "Agency", "Funding sub-agency name (2nd instance)"),
    126: ("referenced_idv_agency_iden", "Transaction", "Referenced IDV agency identifier"),
    127: ("referenced_idv_agency_desc", "Transaction", "Referenced IDV agency description"),
    128: ("naics_code_2", "Classification", "NAICS code (duplicate)"),
    129: ("cfda_number_2", "Classification", "CFDA number (duplicate)"),
    130: ("cfda_program_title", "Classification", "CFDA program title"),
    131: ("sai_number", "Classification", "SAI number"),
    132: ("type_of_contract_pricing", "Contract", "Contract pricing type"),
    133: ("type_of_contract_pricing_desc", "Contract", "Contract pricing description"),
    134: ("award_type_code", "Transaction", "Award type code"),
    135: ("award_type", "Transaction", "Award type description"),

    # Award Details (136-151)
    136: ("record_type", "Transaction", "Record type (procurement/assistance)"),
    137: ("type_of_transaction_code", "Transaction", "Transaction type code"),
    138: ("piid_2", "Transaction", "PIID (duplicate)"),
    139: ("fain_2", "Transaction", "FAIN (duplicate)"),
    140: ("total_dollars_obligated", "Financial", "Total dollars obligated"),
    141: ("base_and_exercised_options_value", "Financial", "Base + exercised options value"),
    142: ("awarding_agency_name_4", "Agency", "Awarding agency name (4th instance)"),
    143: ("awarding_agency_code_4", "Agency", "Awarding agency code (4th instance)"),
    144: ("awarding_sub_agency_name_3", "Agency", "Awarding sub-agency name (3rd instance)"),
    145: ("awarding_sub_agency_code_2", "Agency", "Awarding sub-agency code (2nd instance)"),
    146: ("funding_agency_name_4", "Agency", "Funding agency name (4th instance)"),
    147: ("funding_agency_code_4", "Agency", "Funding agency code (4th instance)"),
    148: ("funding_sub_agency_name_3", "Agency", "Funding sub-agency name (3rd instance)"),
    149: ("funding_sub_agency_code_3", "Agency", "Funding sub-agency code (3rd instance)"),
    150: ("cfda_number_3", "Classification", "CFDA number (3rd instance)"),
    151: ("cfda_title_2", "Classification", "CFDA title (2nd instance)"),

    # Transaction Details (152-164)
    152: ("fiscal_year_2", "Transaction", "Fiscal year (duplicate)"),
    153: ("total_outlays", "Financial", "Total outlays"),
    154: ("recipient_name_2", "Recipient", "Recipient name (duplicate)"),
    155: ("recipient_parent_name_2", "Recipient", "Recipient parent name (duplicate)"),
    156: ("recipient_location_state_fips", "Location", "Recipient state FIPS code"),
    157: ("business_types_array", "Recipient", "Business types as PostgreSQL array"),
    158: ("business_categories_list", "Recipient", "Business categories list"),
    159: ("prime_award_base_transaction_description", "Description", "Base transaction description"),
    160: ("type_of_contract_pricing_code", "Contract", "Contract pricing type code"),
    161: ("sam_exception", "Recipient", "SAM exception code"),
    162: ("action_type_code", "Transaction", "Action type code"),
    163: ("product_or_service_code", "Classification", "PSC code"),
    164: ("product_or_service_code_description", "Classification", "PSC description"),

    # Recipient Location Details (165-179)
    165: ("recipient_country_code_2", "Location", "Recipient country code (duplicate)"),
    166: ("recipient_country_name_2", "Location", "Recipient country name (duplicate)"),
    167: ("recipient_county_code", "Location", "Recipient county code"),
    168: ("recipient_county_name", "Location", "Recipient county name"),
    169: ("recipient_zip_4", "Location", "Recipient ZIP+4"),
    170: ("recipient_zip_last4", "Location", "Recipient ZIP last 4 digits"),
    171: ("recipient_congressional_district", "Location", "Recipient congressional district"),
    172: ("recipient_location_congressional_code_2", "Location", "Recipient congressional code (dup)"),
    173: ("pop_country_code_2", "Location", "POP country code (duplicate)"),
    174: ("pop_country_name_2", "Location", "POP country name (duplicate)"),
    175: ("pop_county_code", "Location", "POP county code"),
    176: ("pop_county_name", "Location", "POP county name"),
    177: ("pop_zip_4", "Location", "POP ZIP+4"),
    178: ("pop_zip_last4", "Location", "POP ZIP last 4 digits"),
    179: ("pop_congressional_district", "Location", "POP congressional district"),

    # Full-Text Search Vectors (180-182)
    180: ("award_description_tsvector", "Search", "Full-text search vector for award description"),
    181: ("award_ids_tsvector", "Search", "Full-text search vector for award IDs"),
    182: ("recipient_name_tsvector", "Search", "Full-text search vector for recipient name"),

    # Treasury Account Fields (183-205)
    183: ("treasury_account_identifiers", "Financial", "Treasury account identifier"),
    184: ("tas_rendering_label", "Financial", "TAS rendering label"),
    185: ("disaster_emergency_fund_code", "Financial", "Disaster/emergency fund code"),
    186: ("transaction_obligated_amount", "Financial", "Transaction obligated amount"),
    187: ("recipient_state_code", "Location", "Recipient state code (clean)"),
    188: ("recipient_state_code_2", "Location", "Recipient state code (duplicate)"),
    189: ("pop_state_code_2", "Location", "POP state code (duplicate)"),
    190: ("pop_state_code_3", "Location", "POP state code (3rd instance)"),
    191: ("recipient_county_code_2", "Location", "Recipient county code (duplicate)"),
    192: ("recipient_state_code_3", "Location", "Recipient state code (3rd instance)"),
    193: ("pop_county_code_2", "Location", "POP county code (duplicate)"),
    194: ("pop_state_code_4", "Location", "POP state code (4th instance)"),
    195: ("recipient_county_name_2", "Location", "Recipient county name (duplicate)"),
    196: ("recipient_county_code_3", "Location", "Recipient county code (3rd instance)"),
    197: ("pop_county_name_2", "Location", "POP county name (duplicate)"),
    198: ("pop_county_code_3", "Location", "POP county code (3rd instance)"),
    199: ("pop_county_name_3", "Location", "POP county name (3rd instance)"),
    200: ("treasury_account_symbol", "Financial", "Treasury account symbol (JSON array)"),
    201: ("generated_pragmatic_obligation", "System", "Generated pragmatic obligation ID"),
    202: ("original_loan_subsidy_cost", "Financial", "Original loan subsidy cost"),
    203: ("face_value_loan_guarantee", "Financial", "Face value of loan guarantee"),
    204: ("awarding_toptier_agency_code", "Agency", "Awarding top-tier agency code (clean)"),
    205: ("funding_toptier_agency_code", "Agency", "Funding top-tier agency code (clean)"),
}

def analyze_schema(file_path: Path, num_samples: int = 20) -> Dict:
    """Analyze the schema by examining sample records."""

    print(f"Analyzing: {file_path}")

    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        samples = []
        for i, line in enumerate(f):
            if i >= num_samples:
                break
            fields = line.strip().split('\t')
            samples.append(fields)

    return {
        'num_columns': len(samples[0]) if samples else 0,
        'samples': samples
    }

def generate_comprehensive_documentation(analysis: Dict, output_path: Path):
    """Generate comprehensive markdown documentation."""

    num_columns = analysis['num_columns']
    samples = analysis['samples']

    # Group by category
    categories = defaultdict(list)
    for idx in range(num_columns):
        if idx in COLUMN_MAPPING:
            name, category, description = COLUMN_MAPPING[idx]
            categories[category].append((idx, name, description))
        else:
            categories['Unmapped'].append((idx, f"column_{idx}", "Unknown field"))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# USAspending Database - Complete Schema (206 Columns)\n\n")
        f.write(f"**Total Columns**: {num_columns}\n")
        f.write(f"**Analysis Date**: 2025-10-11\n")
        f.write(f"**Source**: USAspending PostgreSQL database export\n\n")

        f.write("---\n\n")
        f.write("## Executive Summary\n\n")
        f.write("This schema represents the complete structure of USAspending transaction data, ")
        f.write("which includes federal contracts, grants, loans, and other financial assistance.\n\n")

        f.write("### Key Field Categories:\n\n")
        for category in sorted(categories.keys(), key=lambda x: len(categories[x]), reverse=True):
            f.write(f"- **{category}**: {len(categories[category])} fields\n")

        f.write("\n---\n\n")
        f.write("## Table of Contents\n\n")
        for category in sorted(categories.keys()):
            anchor = category.lower().replace(' ', '-')
            f.write(f"- [{category}](#{anchor}) ({len(categories[category])} fields)\n")

        f.write("\n---\n\n")

        # Detailed sections
        for category in sorted(categories.keys()):
            f.write(f"## {category}\n\n")
            f.write(f"**Total Fields**: {len(categories[category])}\n\n")

            for idx, name, description in sorted(categories[category]):
                f.write(f"### [{idx}] `{name}`\n\n")
                f.write(f"**Description**: {description}\n\n")

                # Get sample values
                sample_values = []
                for record in samples:
                    if idx < len(record):
                        value = record[idx]
                        if value and value != '\\N' and value not in sample_values:
                            sample_values.append(value)
                            if len(sample_values) >= 3:
                                break

                if sample_values:
                    f.write("**Sample Values**:\n")
                    for value in sample_values:
                        display = value[:80] + '...' if len(value) > 80 else value
                        f.write(f"- `{display}`\n")
                    f.write("\n")
                else:
                    f.write("*No non-null values in sample*\n\n")

            f.write("---\n\n")

        # China Detection Strategy
        f.write("## China Entity Detection Strategy\n\n")
        f.write("Based on the complete schema, here are the key fields for detecting China-related transactions:\n\n")

        f.write("### Primary Detection Fields (Direct Entity Identification)\n\n")
        f.write("1. **[23] `recipient_name`** - Prime contractor/recipient name\n")
        f.write("2. **[27] `recipient_parent_name`** - Ultimate parent organization\n")
        f.write("3. **[29] `recipient_location_country_name`** - Recipient country\n")
        f.write("4. **[39] `pop_country_name`** - Where work is performed\n")
        f.write("5. **[59] `sub_awardee_name`** - Sub-contractor name\n")
        f.write("6. **[63] `sub_awardee_parent_name`** - Sub-contractor parent\n")
        f.write("7. **[65] `sub_awardee_country_name`** - Sub-contractor country\n\n")

        f.write("### Secondary Detection Fields (Context and Classification)\n\n")
        f.write("8. **[46] `award_description`** - Detailed description of award\n")
        f.write("9. **[47-48] `naics_code/description`** - Industry classification\n")
        f.write("10. **[163-164] `product_or_service_code`** - PSC classification\n")
        f.write("11. **[82] `subaward_description`** - Sub-award details\n")
        f.write("12. **[180-182] Text search vectors** - Full-text search capability\n\n")

        f.write("### Financial and Risk Assessment Fields\n\n")
        f.write("13. **[6] `federal_action_obligation`** - Transaction amount\n")
        f.write("14. **[140] `total_dollars_obligated`** - Total obligated\n")
        f.write("15. **[10/16] Agency names** - Awarding agencies (DOD, DOE, etc.)\n")
        f.write("16. **[7] `action_date`** - Transaction date\n\n")

        f.write("### Identification Fields (Cross-Reference)\n\n")
        f.write("17. **[22] `recipient_uei`** - Unique Entity Identifier\n")
        f.write("18. **[21] `recipient_duns`** - DUNS number\n")
        f.write("19. **[4] `piid`** - Procurement instrument ID\n")
        f.write("20. **[120] `fain`** - Federal award ID (grants)\n\n")

        f.write("---\n\n")
        f.write("## Processing Recommendations\n\n")
        f.write("### Multi-Field Detection Strategy\n\n")
        f.write("1. **Country Check** (Columns 29, 39, 65, 75):\n")
        f.write("   - Look for 'China', 'Hong Kong', 'PRC', 'People's Republic of China'\n")
        f.write("   - Check both recipient location AND place of performance\n")
        f.write("   - Check both prime AND sub-awardee countries\n\n")

        f.write("2. **Entity Name Check** (Columns 23, 27, 59, 63):\n")
        f.write("   - Scan for known Chinese companies (Huawei, ZTE, etc.)\n")
        f.write("   - Look for Chinese name patterns\n")
        f.write("   - Check parent companies (many use US subsidiaries)\n\n")

        f.write("3. **Description Analysis** (Columns 46, 82):\n")
        f.write("   - Search for China-related keywords\n")
        f.write("   - Identify technology sectors of interest\n")
        f.write("   - Cross-reference with sensitive NAICS/PSC codes\n\n")

        f.write("4. **Full-Text Search** (Columns 180-182):\n")
        f.write("   - Use PostgreSQL text search vectors for efficiency\n")
        f.write("   - Can search across multiple text fields simultaneously\n\n")

        f.write("### Performance Optimization\n\n")
        f.write("- **Batch Processing**: Process 100k-500k records at a time\n")
        f.write("- **Index Fields**: Country codes, recipient names, NAICS codes\n")
        f.write("- **NULL Handling**: Many fields have high NULL rates (\\N)\n")
        f.write("- **Size**: 215 GB total, ~50M+ transactions estimated\n\n")

        f.write("---\n\n")
        f.write("*Generated by USAspending Schema Mapper - 2025-10-11*\n")

def main():
    file_path = Path("F:/OSINT_DATA/USAspending/extracted_data/5876.dat.gz")
    output_path = Path("analysis/USASPENDING_COMPLETE_SCHEMA.md")

    print("USAspending Schema Mapper\n" + "="*50)

    # Analyze
    analysis = analyze_schema(file_path, num_samples=20)
    print(f"Columns detected: {analysis['num_columns']}")
    print(f"Mapped columns: {len(COLUMN_MAPPING)}")
    print(f"Unmapped columns: {analysis['num_columns'] - len(COLUMN_MAPPING)}")

    # Generate documentation
    generate_comprehensive_documentation(analysis, output_path)

    print(f"\nComplete schema documentation: {output_path}")
    print("="*50)
    print("\nNext Steps:")
    print("1. Review schema documentation")
    print("2. Design multi-field detection logic")
    print("3. Create batch processing pipeline")
    print("4. Test on sample dataset")

if __name__ == '__main__':
    main()
