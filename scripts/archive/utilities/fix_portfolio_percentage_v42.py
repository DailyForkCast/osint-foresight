"""
Fix Portfolio_Dashboard D6 percentage - v42
"""
import openpyxl

print("="*80)
print("FIXING PORTFOLIO PERCENTAGE - V42")
print("="*80)

# Load v41
print("\nLoading v41...")
wb = openpyxl.load_workbook('2025-10-26-Tracker-v41.xlsx')

ws_portfolio = wb['Portfolio_Dashboard']

print("\n" + "="*80)
print("CHECKING D6 FORMULA")
print("="*80)

print("\nCurrent D6 formula:")
d6_formula = ws_portfolio['D6'].value
print(f"  {d6_formula}")

print("\n" + "="*80)
print("FIXING D6")
print("="*80)

print("\nProblem: Formula uses Control!B18 (Total ULO dollar amount)")
print("Fix: Should use Control!B19 (Portfolio ULO % percentage)")

new_formula = '=TEXT(Control!B19,"0%")&" Unobligated"'
ws_portfolio['D6'] = new_formula

print(f"\nNew D6 formula: {new_formula}")

print("\n" + "="*80)
print("SAVING V42")
print("="*80)

wb.save('2025-10-26-Tracker-v42.xlsx')

print("\nOK - v42 created!")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nFixed:")
print("  D6: Now references Control!B19 (Portfolio ULO %)")
print("  Old: =TEXT(Control!B18,\"0%\")&\" Unobligated\"")
print("  New: =TEXT(Control!B19,\"0%\")&\" Unobligated\"")

print("\nShould now show correct percentage like '25% Unobligated'")
print("instead of '25500000% Unobligated'")

print("\nv42 ready!")
