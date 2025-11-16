"""
Detailed scan of Spotlight_PMWorkspace rows 17-46
"""
import openpyxl

wb = openpyxl.load_workbook('2025-10-26-Tracker-v18.xlsx', data_only=True)

print("="*80)
print("SPOTLIGHT_PMWORKSPACE - DETAILED LAYOUT")
print("="*80)

ws = wb['Spotlight_PMWorkspace']

print("\nRows 1-46 (columns A-H):")
print(f"{'Row':<5} {'A':<25} {'B':<20} {'C':<15} {'D':<15} {'E':<15} {'F':<15} {'G':<15} {'H':<15}")
print("-"*140)

for row in range(1, 47):
    vals = []
    for col in range(1, 9):
        val = ws.cell(row, col).value or ""
        val_str = str(val)[:13] if val else ""
        vals.append(val_str)

    print(f"{row:<5} {vals[0]:<25} {vals[1]:<20} {vals[2]:<15} {vals[3]:<15} {vals[4]:<15} {vals[5]:<15} {vals[6]:<15} {vals[7]:<15}")
