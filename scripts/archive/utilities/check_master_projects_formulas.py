"""
Check what formulas are currently in Master_Projects
"""
import openpyxl

wb = openpyxl.load_workbook('2025-10-26-Tracker-v18.xlsx', data_only=False)

print("="*80)
print("MASTER_PROJECTS - CURRENT FORMULAS IN ROW 2")
print("="*80)

ws = wb['Master_Projects']

columns_to_check = {
    'I': 'Days_Remaining',
    'N': 'Total_Proposed',
    'O': 'Total_Allocation',
    'P': 'Total_Obligated',
    'Q': 'Total_ULO',
    'R': 'ULO_Percent',
    'S': 'Countries',
    'T': 'Country_Count'
}

for col_letter, col_name in columns_to_check.items():
    col_num = openpyxl.utils.column_index_from_string(col_letter)
    cell = ws.cell(2, col_num)

    print(f"\n{col_letter} ({col_name}):")
    if cell.data_type == 'f':
        formula = cell.value
        print(f"  Formula: {formula}")
    else:
        print(f"  NO FORMULA - Value: {cell.value}")
        print(f"  Data type: {cell.data_type}")
