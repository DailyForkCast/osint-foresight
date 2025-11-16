import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import datetime

input_file = 'C:/Projects/OSINT-Foresight/2025-10-26-Tracker-v10.2.xlsx'
output_file = 'C:/Projects/OSINT-Foresight/2025-10-26-Tracker-v11.xlsx'

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print('='*80)
print('ADDING COMPREHENSIVE DROPDOWNS THROUGHOUT TRACKER')
print('='*80)
print()

wb = openpyxl.load_workbook(input_file, data_only=False)

# ============================================================================
# SETUP: Define Named Ranges for Config_Lists
# ============================================================================

print('Step 1: Setting up Config_Lists named ranges...')
print('-'*80)

ws_config = wb['Config_Lists']

# Status list (A2:A10 based on investigation)
# Priority list (B2:B4)
# Phase list (C2:C5)

# We'll reference these directly in formulas instead of creating named ranges
# (Named ranges can be tricky with openpyxl)

print('[OK] Config_Lists reference lists identified')
print()

# ============================================================================
# MASTER_PROJECTS - Add dropdowns
# ============================================================================

print('Step 2: Master_Projects - Adding dropdowns...')
print('-'*80)

ws_projects = wb['Master_Projects']

# Status dropdown (Column E)
status_dv = DataValidation(
    type='list',
    formula1='Config_Lists!$A$2:$A$10',
    allow_blank=False,
    showDropDown=True
)
status_dv.promptTitle = 'Select Status'
status_dv.prompt = 'Choose project status'
status_dv.add('E2:E100')
ws_projects.add_data_validation(status_dv)
print('[OK] Status dropdown (Column E)')

# Priority dropdown (Column F)
priority_dv = DataValidation(
    type='list',
    formula1='Config_Lists!$B$2:$B$5',
    allow_blank=False,
    showDropDown=True
)
priority_dv.promptTitle = 'Select Priority'
priority_dv.prompt = 'Choose project priority'
priority_dv.add('F2:F100')
ws_projects.add_data_validation(priority_dv)
print('[OK] Priority dropdown (Column F)')

print()

# ============================================================================
# MILESTONES - Add dropdowns
# ============================================================================

print('Step 3: Milestones - Adding dropdowns...')
print('-'*80)

ws_milestones = wb['Milestones']

# Project_ID dropdown (Column C) - references Master_Projects Unique_ID
project_id_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
project_id_dv.promptTitle = 'Select Project'
project_id_dv.prompt = 'Choose project ID'
project_id_dv.add('C2:C200')
ws_milestones.add_data_validation(project_id_dv)
print('[OK] Project_ID dropdown (Column C)')

# Status dropdown (Column E)
milestone_status_dv = DataValidation(
    type='list',
    formula1='Config_Lists!$A$2:$A$10',
    allow_blank=False,
    showDropDown=True
)
milestone_status_dv.promptTitle = 'Select Status'
milestone_status_dv.prompt = 'Choose milestone status'
milestone_status_dv.add('E2:E200')
ws_milestones.add_data_validation(milestone_status_dv)
print('[OK] Status dropdown (Column E)')

# Phase dropdown (Column F)
phase_dv = DataValidation(
    type='list',
    formula1='Config_Lists!$C$2:$C$6',
    allow_blank=True,
    showDropDown=True
)
phase_dv.promptTitle = 'Select Phase'
phase_dv.prompt = 'Choose project phase'
phase_dv.add('F2:F200')
ws_milestones.add_data_validation(phase_dv)
print('[OK] Phase dropdown (Column F)')

# Priority dropdown (Column G)
milestone_priority_dv = DataValidation(
    type='list',
    formula1='Config_Lists!$B$2:$B$5',
    allow_blank=True,
    showDropDown=True
)
milestone_priority_dv.promptTitle = 'Select Priority'
milestone_priority_dv.prompt = 'Choose milestone priority'
milestone_priority_dv.add('G2:G200')
ws_milestones.add_data_validation(milestone_priority_dv)
print('[OK] Priority dropdown (Column G)')

print()

# ============================================================================
# EVENTS - Add dropdowns
# ============================================================================

print('Step 4: Events - Adding dropdowns...')
print('-'*80)

ws_events = wb['Events']

# Project_ID dropdown (Column B)
events_project_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
events_project_dv.promptTitle = 'Select Project'
events_project_dv.prompt = 'Choose project ID'
events_project_dv.add('B2:B200')
ws_events.add_data_validation(events_project_dv)
print('[OK] Project_ID dropdown (Column B)')

# Event_Type dropdown (Column C)
event_type_dv = DataValidation(
    type='list',
    formula1='"Conference,Meeting,Workshop,Training,Site Visit,Other"',
    allow_blank=False,
    showDropDown=True
)
event_type_dv.promptTitle = 'Select Event Type'
event_type_dv.prompt = 'Choose type of event'
event_type_dv.add('C2:C200')
ws_events.add_data_validation(event_type_dv)
print('[OK] Event_Type dropdown (Column C)')

print()

# ============================================================================
# RISK_REGISTER - Add dropdowns
# ============================================================================

print('Step 5: Risk_Register - Adding dropdowns...')
print('-'*80)

ws_risks = wb['Risk_Register']

# Project_ID dropdown (Column C)
risks_project_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
risks_project_dv.promptTitle = 'Select Project'
risks_project_dv.prompt = 'Choose project ID'
risks_project_dv.add('C2:C200')
ws_risks.add_data_validation(risks_project_dv)
print('[OK] Project_ID dropdown (Column C)')

# Probability dropdown (Column D)
probability_dv = DataValidation(
    type='list',
    formula1='"Low,Medium,High"',
    allow_blank=False,
    showDropDown=True
)
probability_dv.promptTitle = 'Select Probability'
probability_dv.prompt = 'Choose risk probability'
probability_dv.add('D2:D200')
ws_risks.add_data_validation(probability_dv)
print('[OK] Probability dropdown (Column D)')

# Impact dropdown (Column E)
impact_dv = DataValidation(
    type='list',
    formula1='"Low,Medium,High"',
    allow_blank=False,
    showDropDown=True
)
impact_dv.promptTitle = 'Select Impact'
impact_dv.prompt = 'Choose risk impact'
impact_dv.add('E2:E200')
ws_risks.add_data_validation(impact_dv)
print('[OK] Impact dropdown (Column E)')

# Status dropdown (Column H)
risk_status_dv = DataValidation(
    type='list',
    formula1='"Open,Mitigated,Closed,Monitoring"',
    allow_blank=False,
    showDropDown=True
)
risk_status_dv.promptTitle = 'Select Status'
risk_status_dv.prompt = 'Choose risk status'
risk_status_dv.add('H2:H200')
ws_risks.add_data_validation(risk_status_dv)
print('[OK] Status dropdown (Column H)')

print()

# ============================================================================
# DECISION_LOG - Add dropdowns
# ============================================================================

print('Step 6: Decision_Log - Adding dropdowns...')
print('-'*80)

ws_decisions = wb['Decision_Log']

# Project_ID dropdown (Column C)
decisions_project_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
decisions_project_dv.promptTitle = 'Select Project'
decisions_project_dv.prompt = 'Choose project ID'
decisions_project_dv.add('C2:C200')
ws_decisions.add_data_validation(decisions_project_dv)
print('[OK] Project_ID dropdown (Column C)')

# Status dropdown (Column G)
decision_status_dv = DataValidation(
    type='list',
    formula1='"Proposed,Approved,Rejected,Implemented"',
    allow_blank=False,
    showDropDown=True
)
decision_status_dv.promptTitle = 'Select Status'
decision_status_dv.prompt = 'Choose decision status'
decision_status_dv.add('G2:G200')
ws_decisions.add_data_validation(decision_status_dv)
print('[OK] Status dropdown (Column G)')

print()

# ============================================================================
# STAKEHOLDERS - Add dropdowns
# ============================================================================

print('Step 7: Stakeholders - Adding dropdowns...')
print('-'*80)

ws_stakeholders = wb['Stakeholders']

# Stakeholder_Type dropdown (Column K)
stakeholder_type_dv = DataValidation(
    type='list',
    formula1='"Government,Private Sector,Academia,NGO,Media,Other"',
    allow_blank=False,
    showDropDown=True
)
stakeholder_type_dv.promptTitle = 'Select Type'
stakeholder_type_dv.prompt = 'Choose stakeholder type'
stakeholder_type_dv.add('K2:K200')
ws_stakeholders.add_data_validation(stakeholder_type_dv)
print('[OK] Stakeholder_Type dropdown (Column K)')

# Location_Country dropdown (Column F)
stakeholder_country_dv = DataValidation(
    type='list',
    formula1='Country_Regions!$A$2:$A$79',
    allow_blank=True,
    showDropDown=True
)
stakeholder_country_dv.promptTitle = 'Select Country'
stakeholder_country_dv.prompt = 'Choose country code'
stakeholder_country_dv.add('F2:F200')
ws_stakeholders.add_data_validation(stakeholder_country_dv)
print('[OK] Location_Country dropdown (Column F)')

print()

# ============================================================================
# PROJECT_DELIVERABLES - Add dropdowns
# ============================================================================

print('Step 8: Project_Deliverables - Adding dropdowns...')
print('-'*80)

ws_deliverables = wb['Project_Deliverables']

# Project_ID dropdown (Column A)
deliverables_project_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
deliverables_project_dv.promptTitle = 'Select Project'
deliverables_project_dv.prompt = 'Choose project ID'
deliverables_project_dv.add('A2:A200')
ws_deliverables.add_data_validation(deliverables_project_dv)
print('[OK] Project_ID dropdown (Column A)')

# Deliverable_Type dropdown (Column C)
deliverable_type_dv = DataValidation(
    type='list',
    formula1='"Report,Presentation,Training,Software,Data,Documentation,Other"',
    allow_blank=True,
    showDropDown=True
)
deliverable_type_dv.promptTitle = 'Select Type'
deliverable_type_dv.prompt = 'Choose deliverable type'
deliverable_type_dv.add('C2:C200')
ws_deliverables.add_data_validation(deliverable_type_dv)
print('[OK] Deliverable_Type dropdown (Column C)')

# Status dropdown (Column E)
deliverable_status_dv = DataValidation(
    type='list',
    formula1='"Not Started,In Progress,Under Review,Completed,Cancelled"',
    allow_blank=False,
    showDropDown=True
)
deliverable_status_dv.promptTitle = 'Select Status'
deliverable_status_dv.prompt = 'Choose deliverable status'
deliverable_status_dv.add('E2:E200')
ws_deliverables.add_data_validation(deliverable_status_dv)
print('[OK] Status dropdown (Column E)')

print()

# ============================================================================
# PROJECT_AUDIENCES - Add dropdowns
# ============================================================================

print('Step 9: Project_Audiences - Adding dropdowns...')
print('-'*80)

ws_audiences = wb['Project_Audiences']

# Project_ID dropdown (Column A)
audiences_project_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
audiences_project_dv.promptTitle = 'Select Project'
audiences_project_dv.prompt = 'Choose project ID'
audiences_project_dv.add('A2:A200')
ws_audiences.add_data_validation(audiences_project_dv)
print('[OK] Project_ID dropdown (Column A)')

# Audience_Type dropdown (Column B)
audience_type_dv = DataValidation(
    type='list',
    formula1='"Government Officials,Private Sector,Academia,Civil Society,Media,General Public,Other"',
    allow_blank=False,
    showDropDown=True
)
audience_type_dv.promptTitle = 'Select Audience Type'
audience_type_dv.prompt = 'Choose target audience'
audience_type_dv.add('B2:B200')
ws_audiences.add_data_validation(audience_type_dv)
print('[OK] Audience_Type dropdown (Column B)')

# Priority dropdown (Column E)
audience_priority_dv = DataValidation(
    type='list',
    formula1='"High,Medium,Low"',
    allow_blank=True,
    showDropDown=True
)
audience_priority_dv.promptTitle = 'Select Priority'
audience_priority_dv.prompt = 'Choose audience priority'
audience_priority_dv.add('E2:E200')
ws_audiences.add_data_validation(audience_priority_dv)
print('[OK] Priority dropdown (Column E)')

print()

# ============================================================================
# PROJECT_PRODUCTS - Add dropdowns
# ============================================================================

print('Step 10: Project_Products - Adding dropdowns...')
print('-'*80)

ws_products = wb['Project_Products']

# Project_ID dropdown (Column A)
products_project_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
products_project_dv.promptTitle = 'Select Project'
products_project_dv.prompt = 'Choose project ID'
products_project_dv.add('A2:A200')
ws_products.add_data_validation(products_project_dv)
print('[OK] Project_ID dropdown (Column A)')

# Product_Category dropdown (Column C)
product_category_dv = DataValidation(
    type='list',
    formula1='"Software,Hardware,Service,Training,Report,Dataset,Other"',
    allow_blank=True,
    showDropDown=True
)
product_category_dv.promptTitle = 'Select Category'
product_category_dv.prompt = 'Choose product category'
product_category_dv.add('C2:C200')
ws_products.add_data_validation(product_category_dv)
print('[OK] Product_Category dropdown (Column C)')

# Product_Status dropdown (Column D)
product_status_dv = DataValidation(
    type='list',
    formula1='"Planning,Development,Testing,Released,Deprecated"',
    allow_blank=True,
    showDropDown=True
)
product_status_dv.promptTitle = 'Select Status'
product_status_dv.prompt = 'Choose product status'
product_status_dv.add('D2:D200')
ws_products.add_data_validation(product_status_dv)
print('[OK] Product_Status dropdown (Column D)')

print()

# ============================================================================
# PROJECT_TECHNOLOGIES - Add dropdowns
# ============================================================================

print('Step 11: Project_Technologies - Adding dropdowns...')
print('-'*80)

ws_technologies = wb['Project_Technologies']

# Project_ID dropdown (Column A)
tech_project_dv = DataValidation(
    type='list',
    formula1='Master_Projects!$B$2:$B$100',
    allow_blank=False,
    showDropDown=True
)
tech_project_dv.promptTitle = 'Select Project'
tech_project_dv.prompt = 'Choose project ID'
tech_project_dv.add('A2:A200')
ws_technologies.add_data_validation(tech_project_dv)
print('[OK] Project_ID dropdown (Column A)')

# Category dropdown (Column C)
tech_category_dv = DataValidation(
    type='list',
    formula1='"Infrastructure,AI/ML,Cloud,Security,Data,Networking,Software,Other"',
    allow_blank=True,
    showDropDown=True
)
tech_category_dv.promptTitle = 'Select Category'
tech_category_dv.prompt = 'Choose technology category'
tech_category_dv.add('C2:C200')
ws_technologies.add_data_validation(tech_category_dv)
print('[OK] Category dropdown (Column C)')

# Status dropdown (Column D)
tech_status_dv = DataValidation(
    type='list',
    formula1='"Proposed,In Use,Deprecated,Planned"',
    allow_blank=True,
    showDropDown=True
)
tech_status_dv.promptTitle = 'Select Status'
tech_status_dv.prompt = 'Choose technology status'
tech_status_dv.add('D2:D200')
ws_technologies.add_data_validation(tech_status_dv)
print('[OK] Status dropdown (Column D)')

print()

# ============================================================================
# SAVE
# ============================================================================

print('='*80)
print('Saving v11...')
print()

try:
    wb.save(output_file)
    wb.close()
    print('[OK] File saved successfully!')
except Exception as e:
    print(f'[ERROR] Failed to save: {e}')
    exit(1)

print()
print('='*80)
print('COMPREHENSIVE DROPDOWNS COMPLETE!')
print('='*80)
print()
print('Dropdowns added to:')
print('  1. [OK] Master_Projects - Status, Priority')
print('  2. [OK] Milestones - Project_ID, Status, Phase, Priority')
print('  3. [OK] Events - Project_ID, Event_Type')
print('  4. [OK] Risk_Register - Project_ID, Probability, Impact, Status')
print('  5. [OK] Decision_Log - Project_ID, Status')
print('  6. [OK] Stakeholders - Type, Country')
print('  7. [OK] Project_Deliverables - Project_ID, Type, Status')
print('  8. [OK] Project_Audiences - Project_ID, Type, Priority')
print('  9. [OK] Project_Products - Project_ID, Category, Status')
print(' 10. [OK] Project_Technologies - Project_ID, Category, Status')
print()
print('Benefits:')
print('  - Prevents typos and data entry errors')
print('  - Ensures consistency across all records')
print('  - Faster data entry (select instead of type)')
print('  - All dropdowns reference master lists')
print()
print(f'Output: {output_file}')
print(f'Created: {timestamp}')
print()
print('Ready for testing!')
