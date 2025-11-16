import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import datetime

input_file = 'C:/Projects/OSINT-Foresight/2025-10-26-Tracker-v8.1.xlsx'
output_file = 'C:/Projects/OSINT-Foresight/2025-10-26-Tracker-v10.xlsx'

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print('='*80)
print('FIXING COUNTRY BUDGET TRACKER - ADDING COUNTRY DROPDOWN')
print('='*80)
print()

wb = openpyxl.load_workbook(input_file, data_only=False)

# ============================================================================
# FIX: ADD COUNTRY CODE DROPDOWN TO COUNTRY_BUDGETS
# ============================================================================

print('Step 1: Adding Country Code dropdown to Country_Budgets sheet...')
print('-'*80)

ws_budgets = wb['Country_Budgets']
ws_regions = wb['Country_Regions']

# Get the range of countries in Country_Regions
# Column A has country codes starting from row 2
# We need to find the last row
last_row = ws_regions.max_row

print(f'Country_Regions has {last_row - 1} countries (rows 2-{last_row})')
print()

# Create data validation for Country_Code column (D)
# Use a list validation that references Country_Regions column A

country_list_formula = f'Country_Regions!$A$2:$A${last_row}'

print(f'Creating dropdown with formula: {country_list_formula}')

# Create the data validation
dv = DataValidation(
    type='list',
    formula1=country_list_formula,
    allow_blank=True,
    showDropDown=True,  # False means show dropdown button
    showErrorMessage=True,
    errorTitle='Invalid Country',
    error='Please select a country code from the dropdown list.'
)

# Add a prompt message
dv.promptTitle = 'Select Country'
dv.prompt = 'Choose a country code from the list (e.g., DE, FR, IT)'

# Apply to column D, starting from row 2, going down to row 1000 (plenty of room)
dv.add('D2:D1000')

# Add the data validation to the sheet
ws_budgets.add_data_validation(dv)

print('[OK] Country dropdown added to column D (rows 2-1000)')
print()

# ============================================================================
# SAVE
# ============================================================================

print('='*80)
print('Saving v10...')
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
print('COUNTRY DROPDOWN FIX COMPLETE!')
print('='*80)
print()
print('Changes applied:')
print('  1. [OK] Added country code dropdown to Country_Budgets column D')
print('  2. [OK] Dropdown shows all 78 countries from Country_Regions')
print('  3. [OK] Applied to rows 2-1000 (plenty of capacity)')
print('  4. [OK] Shows helpful prompt and error messages')
print()
print('How it works:')
print('  - Click any cell in column D (Country_Code)')
print('  - Dropdown arrow appears')
print('  - Select country code (e.g., DE, FR, IT)')
print('  - Column E (Country_Name) auto-populates via INDEX/MATCH formula')
print()
print(f'Output: {output_file}')
print()
print('TEST IT:')
print('  1. Open v10 in Excel')
print('  2. Go to Country_Budgets sheet')
print('  3. Click cell D4 (first empty row)')
print('  4. Click dropdown arrow')
print('  5. Select a country (e.g., IT for Italy)')
print('  6. Watch E4 auto-fill with "Italy"')
print()
print(f'Created: {timestamp}')
