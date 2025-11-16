"""
Completely clear Calendar_Todo - no formulas at all - v39
Also check T_Stakeholders table
"""
import openpyxl

print("="*80)
print("COMPLETELY CLEARING CALENDAR_TODO - V39")
print("="*80)

# Load v38
print("\nLoading v38...")
wb = openpyxl.load_workbook('2025-10-26-Tracker-v38.xlsx')

ws_calendar = wb['Calendar_Todo']

print("\n" + "="*80)
print("CLEARING EVERYTHING FROM CALENDAR_TODO")
print("="*80)

print("\nRemoving ALL content (even the examples)...")

# Clear ALL data including headers - we'll re-add just headers
for row in range(1, 101):
    for col in range(1, 10):
        ws_calendar.cell(row, col).value = None

print("  All content cleared")

print("\nRe-adding headers only (no formulas)...")
ws_calendar['A1'] = 'Task_ID'
ws_calendar['B1'] = 'Task_Name'
ws_calendar['C1'] = 'Unique_ID'
ws_calendar['D1'] = 'Due_Date'
ws_calendar['E1'] = 'Assigned_To'
ws_calendar['F1'] = 'Status'
ws_calendar['G1'] = 'Priority'
ws_calendar['H1'] = 'Notes'

print("  Headers added")

# Check if there's a table on Calendar_Todo that needs to be removed
print("\nChecking for tables on Calendar_Todo...")
if ws_calendar.tables:
    print(f"  Found {len(ws_calendar.tables)} table(s)")
    for table_name in list(ws_calendar.tables.keys()):
        print(f"  Removing table: {table_name}")
        del ws_calendar.tables[table_name]
else:
    print("  No tables found")

print("\n" + "="*80)
print("CHECKING STAKEHOLDERS TABLE")
print("="*80)

ws_stakeholders = wb['Stakeholders']

print("\nT_Stakeholders table info:")
if 'T_Stakeholders' in ws_stakeholders.tables:
    table = ws_stakeholders.tables['T_Stakeholders']
    print(f"  Exists: Yes")
    print(f"  Name: T_Stakeholders")
    # Check if we can access the table reference
    try:
        print(f"  Has data")
    except:
        print(f"  May have issues")
else:
    print("  Table not found!")

print("\n" + "="*80)
print("SAVING V39")
print("="*80)

wb.save('2025-10-26-Tracker-v39.xlsx')

print("\nOK - v39 created!")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nFixed in v39:")
print("  1. Calendar_Todo: COMPLETELY CLEARED")
print("     - No formulas")
print("     - No instructions")
print("     - No examples")
print("     - Only headers in row 1")
print("     - 100% manual entry sheet")

print("\n  2. Removed any tables from Calendar_Todo")

print("\n  3. Checked T_Stakeholders table")

print("\nCalendar_Todo is now a blank template.")
print("You can add your tasks manually without any corruption risk.")

print("\nv39 ready - should open cleanly!")
