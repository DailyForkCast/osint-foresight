"""
Fix Country_Dashboard - D2 and G2 should be labels, not formulas - v51
Move formulas to E2 and H2, update all references
"""
import openpyxl

print("="*80)
print("FIXING COUNTRY_DASHBOARD LABELS - V51")
print("="*80)

# Load v50
print("\nLoading v50...")
wb = openpyxl.load_workbook('2025-10-26-Tracker-v50.xlsx')

ws_country = wb['Country_Dashboard']

print("\n" + "="*80)
print("CURRENT STATE")
print("="*80)

print("\nRow 2 current values:")
print(f"  D2: {ws_country['D2'].value}")
print(f"  E2: {ws_country['E2'].value}")
print(f"  G2: {ws_country['G2'].value}")
print(f"  H2: {ws_country['H2'].value}")

print("\n" + "="*80)
print("FIX: REORGANIZE ROW 2")
print("="*80)

print("\nMaking D2 and G2 into labels...")

# D2 should be label "Region:"
ws_country['D2'] = 'Region:'
print("  D2: Set to 'Region:'")

# E2 should have the region formula (move from D2)
ws_country['E2'] = '=IFERROR(INDEX(T_Country_Regions[Region],MATCH(B2,T_Country_Regions[Country_Name],0)),"")'
print("  E2: Added region lookup formula")

# G2 should be label "Country Code:"
ws_country['G2'] = 'Country Code:'
print("  G2: Set to 'Country Code:'")

# H2 should have the country code formula (move from G2)
ws_country['H2'] = '=IFERROR(INDEX(T_Country_Regions[Country_Code],MATCH(B2,T_Country_Regions[Country_Name],0)),"")'
print("  H2: Added country code lookup formula")

print("\n" + "="*80)
print("UPDATING FORMULAS THAT REFERENCE G2")
print("="*80)

print("\nAll formulas that used $G$2 (country code) need to use $H$2 instead...")

# A5, B5, C5 - Budget totals
if ws_country['A5'].data_type == 'f':
    old = ws_country['A5'].value
    new = old.replace('$G$2', '$H$2')
    ws_country['A5'] = new
    print("  A5: Updated to use $H$2")

if ws_country['B5'].data_type == 'f':
    old = ws_country['B5'].value
    new = old.replace('$G$2', '$H$2')
    ws_country['B5'] = new
    print("  B5: Updated to use $H$2")

if ws_country['C5'].data_type == 'f':
    old = ws_country['C5'].value
    new = old.replace('$G$2', '$H$2')
    ws_country['C5'] = new
    print("  C5: Updated to use $H$2")

# D5 - ULO formula
if ws_country['D5'].data_type == 'f':
    print("  D5: No change needed (uses B5-C5)")

# E5 - ULO % formula
if ws_country['E5'].data_type == 'f':
    print("  E5: No change needed (uses D5/B5)")

# B6 - Number of Projects
if ws_country['B6'].data_type == 'f':
    old = ws_country['B6'].value
    new = old.replace('$G$2', '$H$2')
    ws_country['B6'] = new
    print("  B6: Updated to use $H$2")

# G6 - ULO % (if it references anything)
if ws_country['G6'].data_type == 'f':
    print("  G6: No change needed (references E5)")

# B8 - Country PM
if ws_country['B8'].data_type == 'f':
    old = ws_country['B8'].value
    new = old.replace('$G$2', '$H$2')
    ws_country['B8'] = new
    print("  B8: Updated to use $H$2")

# Project list formulas (A12:A31)
print("\n  Updating project list formulas (A12-A31)...")
updated_count = 0
for row in range(12, 32):
    cell_a = ws_country.cell(row, 1)
    if cell_a.data_type == 'f' and '$G$2' in str(cell_a.value):
        old = cell_a.value
        new = old.replace('$G$2', '$H$2')
        cell_a.value = new
        updated_count += 1

print(f"    Updated {updated_count} project formulas to use $H$2")

print("\n" + "="*80)
print("SAVING V51")
print("="*80)

wb.save('2025-10-26-Tracker-v51.xlsx')

print("\nOK - v51 created!")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nFixed Country_Dashboard row 2 layout:")

print("\n  BEFORE:")
print("    D2: [formula showing region]")
print("    E2: [empty or duplicate]")
print("    G2: [formula showing country code]")
print("    H2: [empty or duplicate]")

print("\n  AFTER:")
print("    D2: 'Region:' (label)")
print("    E2: [formula showing region]")
print("    G2: 'Country Code:' (label)")
print("    H2: [formula showing country code]")

print("\n  All formulas updated:")
print("    - Budget totals (A5, B5, C5): Now use $H$2")
print("    - Number of Projects (B6): Now uses $H$2")
print("    - Country PM (B8): Now uses $H$2")
print("    - Project list (A12-A31): Now use $H$2")

print("\nv51 ready - proper labels and formulas!")
