"""
Add data validation to key sheets - v45.1
Safe formatting enhancement - no formula changes
"""
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation

print("="*80)
print("ADDING DATA VALIDATION - V45.1")
print("="*80)

# Load v45
print("\nLoading v45...")
wb = openpyxl.load_workbook('2025-10-26-Tracker-v45.xlsx')

print("\n" + "="*80)
print("1. MASTER_PROJECTS - STATUS, PRIORITY, FISCAL YEAR")
print("="*80)

ws_master = wb['Master_Projects']

# Status dropdown (column E)
print("\nAdding Status dropdown (E2:E201)...")
dv_status = DataValidation(
    type="list",
    formula1='Config_Lists!$A$2:$A$10',
    allow_blank=True,
    showDropDown=True
)
dv_status.error = 'Invalid Status'
dv_status.errorTitle = 'Invalid Entry'
dv_status.prompt = 'Select from list'
dv_status.promptTitle = 'Project Status'
ws_master.add_data_validation(dv_status)
dv_status.add('E2:E201')
print("  Added: Status dropdown")

# Priority dropdown (column F)
print("\nAdding Priority dropdown (F2:F201)...")
dv_priority = DataValidation(
    type="list",
    formula1='Config_Lists!$B$2:$B$5',
    allow_blank=True,
    showDropDown=True
)
dv_priority.error = 'Invalid Priority'
dv_priority.errorTitle = 'Invalid Entry'
dv_priority.prompt = 'Select from list'
dv_priority.promptTitle = 'Project Priority'
ws_master.add_data_validation(dv_priority)
dv_priority.add('F2:F201')
print("  Added: Priority dropdown")

# Fiscal Year dropdown (column A)
print("\nAdding Fiscal Year dropdown (A2:A201)...")
dv_fy = DataValidation(
    type="list",
    formula1='"FY2024,FY2025,FY2026,FY2027,FY2028"',
    allow_blank=True,
    showDropDown=True
)
dv_fy.error = 'Invalid Fiscal Year'
dv_fy.errorTitle = 'Invalid Entry'
dv_fy.prompt = 'Select from list'
dv_fy.promptTitle = 'Fiscal Year'
ws_master.add_data_validation(dv_fy)
dv_fy.add('A2:A201')
print("  Added: Fiscal Year dropdown")

print("\n" + "="*80)
print("2. COUNTRY_DASHBOARD - COUNTRY SELECTOR")
print("="*80)

ws_country = wb['Country_Dashboard']

# Country dropdown (B2)
print("\nAdding Country dropdown (B2)...")
# Use direct reference since table references don't work in data validation formulas
dv_country = DataValidation(
    type="list",
    formula1='Country_Regions!$A$2:$A$79',
    allow_blank=False,
    showDropDown=True
)
dv_country.error = 'Invalid Country Code'
dv_country.errorTitle = 'Invalid Entry'
dv_country.prompt = 'Select country code'
dv_country.promptTitle = 'Country'
ws_country.add_data_validation(dv_country)
dv_country.add('B2')
print("  Added: Country dropdown")

print("\n" + "="*80)
print("3. SPOTLIGHT_PMWORKSPACE - PROJECT ID SELECTOR")
print("="*80)

ws_spotlight = wb['Spotlight_PMWorkspace']

# Project ID dropdown (B2)
print("\nAdding Project ID dropdown (B2)...")
dv_project = DataValidation(
    type="list",
    formula1='Master_Projects!$B$2:$B$201',
    allow_blank=False,
    showDropDown=True
)
dv_project.error = 'Invalid Project ID'
dv_project.errorTitle = 'Invalid Entry'
dv_project.prompt = 'Select project ID'
dv_project.promptTitle = 'Project'
ws_spotlight.add_data_validation(dv_project)
dv_project.add('B2')
print("  Added: Project ID dropdown")

print("\n" + "="*80)
print("4. COUNTRY_BUDGETS - UNIQUE_ID AND COUNTRY_CODE")
print("="*80)

ws_budgets = wb['Country_Budgets']

# Unique_ID dropdown (column B)
print("\nAdding Unique_ID dropdown (B2:B1001)...")
dv_budget_id = DataValidation(
    type="list",
    formula1='Master_Projects!$B$2:$B$201',
    allow_blank=True,
    showDropDown=True
)
dv_budget_id.error = 'Invalid Project ID'
dv_budget_id.errorTitle = 'Invalid Entry'
dv_budget_id.prompt = 'Select project ID'
dv_budget_id.promptTitle = 'Project'
ws_budgets.add_data_validation(dv_budget_id)
dv_budget_id.add('B2:B1001')
print("  Added: Unique_ID dropdown")

# Country_Code dropdown (column D) - will auto-populate from formula, but add validation for manual entry
print("\nAdding Country_Code validation (D2:D1001)...")
dv_budget_country = DataValidation(
    type="list",
    formula1='Country_Regions!$A$2:$A$79',
    allow_blank=True,
    showDropDown=True
)
dv_budget_country.error = 'Invalid Country Code'
dv_budget_country.errorTitle = 'Invalid Entry'
dv_budget_country.prompt = 'Auto-populated or select'
dv_budget_country.promptTitle = 'Country Code'
ws_budgets.add_data_validation(dv_budget_country)
dv_budget_country.add('D2:D1001')
print("  Added: Country_Code validation")

print("\n" + "="*80)
print("5. MILESTONES - STATUS DROPDOWN")
print("="*80)

ws_milestones = wb['Milestones']

# Status dropdown (column E)
print("\nAdding Status dropdown (E2:E100)...")
dv_ms_status = DataValidation(
    type="list",
    formula1='"Not Started,In Progress,Complete,On Hold,Cancelled"',
    allow_blank=True,
    showDropDown=True
)
dv_ms_status.error = 'Invalid Status'
dv_ms_status.errorTitle = 'Invalid Entry'
dv_ms_status.prompt = 'Select from list'
dv_ms_status.promptTitle = 'Milestone Status'
ws_milestones.add_data_validation(dv_ms_status)
dv_ms_status.add('E2:E100')
print("  Added: Milestone Status dropdown")

# Unique_ID dropdown (column C)
print("\nAdding Unique_ID dropdown (C2:C100)...")
dv_ms_project = DataValidation(
    type="list",
    formula1='Master_Projects!$B$2:$B$201',
    allow_blank=True,
    showDropDown=True
)
dv_ms_project.error = 'Invalid Project ID'
dv_ms_project.errorTitle = 'Invalid Entry'
dv_ms_project.prompt = 'Select project ID'
dv_ms_project.promptTitle = 'Project'
ws_milestones.add_data_validation(dv_ms_project)
dv_ms_project.add('C2:C100')
print("  Added: Unique_ID dropdown")

print("\n" + "="*80)
print("6. EVENTS - EVENT_TYPE AND UNIQUE_ID")
print("="*80)

ws_events = wb['Events']

# Event_Type dropdown (column C)
print("\nAdding Event_Type dropdown (C2:C100)...")
dv_event_type = DataValidation(
    type="list",
    formula1='"Meeting,Review,Presentation,Training,Workshop,Conference,Other"',
    allow_blank=True,
    showDropDown=True
)
dv_event_type.error = 'Invalid Event Type'
dv_event_type.errorTitle = 'Invalid Entry'
dv_event_type.prompt = 'Select from list'
dv_event_type.promptTitle = 'Event Type'
ws_events.add_data_validation(dv_event_type)
dv_event_type.add('C2:C100')
print("  Added: Event_Type dropdown")

# Unique_ID dropdown (column B)
print("\nAdding Unique_ID dropdown (B2:B100)...")
dv_event_project = DataValidation(
    type="list",
    formula1='Master_Projects!$B$2:$B$201',
    allow_blank=True,
    showDropDown=True
)
dv_event_project.error = 'Invalid Project ID'
dv_event_project.errorTitle = 'Invalid Entry'
dv_event_project.prompt = 'Select project ID'
dv_event_project.promptTitle = 'Project'
ws_events.add_data_validation(dv_event_project)
dv_event_project.add('B2:B100')
print("  Added: Unique_ID dropdown")

print("\n" + "="*80)
print("7. PROJECT_DELIVERABLES - STATUS AND TYPE")
print("="*80)

ws_deliverables = wb['Project_Deliverables']

# Status dropdown (column E)
print("\nAdding Status dropdown (E2:E100)...")
dv_deliv_status = DataValidation(
    type="list",
    formula1='"Not Started,In Progress,Completed,On Hold,Cancelled"',
    allow_blank=True,
    showDropDown=True
)
dv_deliv_status.error = 'Invalid Status'
dv_deliv_status.errorTitle = 'Invalid Entry'
dv_deliv_status.prompt = 'Select from list'
dv_deliv_status.promptTitle = 'Deliverable Status'
ws_deliverables.add_data_validation(dv_deliv_status)
dv_deliv_status.add('E2:E100')
print("  Added: Status dropdown")

# Deliverable_Type dropdown (column C)
print("\nAdding Deliverable_Type dropdown (C2:C100)...")
dv_deliv_type = DataValidation(
    type="list",
    formula1='"Document,Software Release,Report,Presentation,Training,Hardware,Other"',
    allow_blank=True,
    showDropDown=True
)
dv_deliv_type.error = 'Invalid Type'
dv_deliv_type.errorTitle = 'Invalid Entry'
dv_deliv_type.prompt = 'Select from list'
dv_deliv_type.promptTitle = 'Deliverable Type'
ws_deliverables.add_data_validation(dv_deliv_type)
dv_deliv_type.add('C2:C100')
print("  Added: Deliverable_Type dropdown")

# Project_ID dropdown (column A)
print("\nAdding Project_ID dropdown (A2:A100)...")
dv_deliv_project = DataValidation(
    type="list",
    formula1='Master_Projects!$B$2:$B$201',
    allow_blank=True,
    showDropDown=True
)
dv_deliv_project.error = 'Invalid Project ID'
dv_deliv_project.errorTitle = 'Invalid Entry'
dv_deliv_project.prompt = 'Select project ID'
dv_deliv_project.promptTitle = 'Project'
ws_deliverables.add_data_validation(dv_deliv_project)
dv_deliv_project.add('A2:A100')
print("  Added: Project_ID dropdown")

print("\n" + "="*80)
print("8. STAKEHOLDERS - COUNTRY VALIDATION")
print("="*80)

ws_stakeholders = wb['Stakeholders']

# Location_Country dropdown (column E)
print("\nAdding Location_Country dropdown (E2:E100)...")
dv_stake_country = DataValidation(
    type="list",
    formula1='Country_Regions!$B$2:$B$79',
    allow_blank=True,
    showDropDown=True
)
dv_stake_country.error = 'Invalid Country'
dv_stake_country.errorTitle = 'Invalid Entry'
dv_stake_country.prompt = 'Select from list'
dv_stake_country.promptTitle = 'Country'
ws_stakeholders.add_data_validation(dv_stake_country)
dv_stake_country.add('E2:E100')
print("  Added: Location_Country dropdown")

print("\n" + "="*80)
print("9. CALENDAR_TODO - STATUS AND ASSIGNED_TO")
print("="*80)

ws_calendar = wb['Calendar_Todo']

# Status dropdown (column F)
print("\nAdding Status dropdown (F2:F100)...")
dv_cal_status = DataValidation(
    type="list",
    formula1='"Not Started,In Progress,Completed,On Hold,Cancelled"',
    allow_blank=True,
    showDropDown=True
)
dv_cal_status.error = 'Invalid Status'
dv_cal_status.errorTitle = 'Invalid Entry'
dv_cal_status.prompt = 'Select from list'
dv_cal_status.promptTitle = 'Task Status'
ws_calendar.add_data_validation(dv_cal_status)
dv_cal_status.add('F2:F100')
print("  Added: Status dropdown")

# Priority dropdown (column G)
print("\nAdding Priority dropdown (G2:G100)...")
dv_cal_priority = DataValidation(
    type="list",
    formula1='Config_Lists!$B$2:$B$5',
    allow_blank=True,
    showDropDown=True
)
dv_cal_priority.error = 'Invalid Priority'
dv_cal_priority.errorTitle = 'Invalid Entry'
dv_cal_priority.prompt = 'Select from list'
dv_cal_priority.promptTitle = 'Priority'
ws_calendar.add_data_validation(dv_cal_priority)
dv_cal_priority.add('G2:G100')
print("  Added: Priority dropdown")

# Unique_ID dropdown (column C)
print("\nAdding Unique_ID dropdown (C2:C100)...")
dv_cal_project = DataValidation(
    type="list",
    formula1='Master_Projects!$B$2:$B$201',
    allow_blank=True,
    showDropDown=True
)
dv_cal_project.error = 'Invalid Project ID'
dv_cal_project.errorTitle = 'Invalid Entry'
dv_cal_project.prompt = 'Select project ID (optional)'
dv_cal_project.promptTitle = 'Project'
ws_calendar.add_data_validation(dv_cal_project)
dv_cal_project.add('C2:C100')
print("  Added: Unique_ID dropdown")

print("\n" + "="*80)
print("SAVING V45.1")
print("="*80)

wb.save('2025-10-26-Tracker-v45.1.xlsx')

print("\nOK - v45.1 created!")

print("\n" + "="*80)
print("SUMMARY - DATA VALIDATION ADDED")
print("="*80)

print("\n✓ Master_Projects:")
print("  - Status dropdown (E2:E201)")
print("  - Priority dropdown (F2:F201)")
print("  - Fiscal Year dropdown (A2:A201)")

print("\n✓ Country_Dashboard:")
print("  - Country selector dropdown (B2)")

print("\n✓ Spotlight_PMWorkspace:")
print("  - Project ID selector dropdown (B2)")

print("\n✓ Country_Budgets:")
print("  - Unique_ID dropdown (B2:B1001)")
print("  - Country_Code validation (D2:D1001)")

print("\n✓ Milestones:")
print("  - Status dropdown (E2:E100)")
print("  - Unique_ID dropdown (C2:C100)")

print("\n✓ Events:")
print("  - Event_Type dropdown (C2:C100)")
print("  - Unique_ID dropdown (B2:B100)")

print("\n✓ Project_Deliverables:")
print("  - Status dropdown (E2:E100)")
print("  - Deliverable_Type dropdown (C2:C100)")
print("  - Project_ID dropdown (A2:A100)")

print("\n✓ Stakeholders:")
print("  - Location_Country dropdown (E2:E100)")

print("\n✓ Calendar_Todo:")
print("  - Status dropdown (F2:F100)")
print("  - Priority dropdown (G2:G100)")
print("  - Unique_ID dropdown (C2:C100)")

print("\n" + "="*80)
print("All data validation added successfully!")
print("You'll see dropdown arrows when you select validated cells.")
print("v45.1 ready!")
print("="*80)
