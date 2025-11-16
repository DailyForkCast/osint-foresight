#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract TED 295 flagged contracts properly
"""

import pandas as pd
import json

excel_file = "c:/Projects/OSINT - Foresight/analysis/TED_295_FLAGGED_CONTRACTS_MANUAL_REVIEW.xlsx"

print("Reading Excel file with proper encoding...")

# Read all sheets
xl_file = pd.ExcelFile(excel_file)
print(f"Sheets found: {xl_file.sheet_names}")

all_data = {}

for sheet_name in xl_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    all_data[sheet_name] = df
    print(f"\n{sheet_name}: {len(df)} records")

# Focus on "All Contracts" sheet
df = all_data['All Contracts']

print(f"\n{'='*80}")
print(f"TED 295 FLAGGED CONTRACTS - STRUCTURE")
print(f"{'='*80}")
print(f"Total records: {len(df)}")
print(f"\nColumns:")
for col in df.columns:
    print(f"  - {col}")

# Get unique contractors
print(f"\n{'='*80}")
print(f"UNIQUE CONTRACTORS")
print(f"{'='*80}")
unique_contractors = df['contractor_name'].value_counts()
print(f"Total unique: {len(unique_contractors)}\n")
print("Top 30:")
for i, (contractor, count) in enumerate(unique_contractors.head(30).items(), 1):
    print(f"{i:3}. {contractor[:65]:<65} ({count:2} contracts)")

# Check confidence levels
if 'confidence' in df.columns:
    print(f"\n{'='*80}")
    print(f"CONFIDENCE DISTRIBUTION")
    print(f"{'='*80}")
    confidence_counts = df['confidence'].value_counts()
    for conf, count in confidence_counts.items():
        print(f"  {conf}: {count} contracts")

# Check flag reasons
if 'flag_reason' in df.columns:
    print(f"\n{'='*80}")
    print(f"FLAG REASON DISTRIBUTION")
    print(f"{'='*80}")
    flag_counts = df['flag_reason'].value_counts()
    for reason, count in flag_counts.items():
        if pd.notna(reason):
            print(f"  {reason}: {count} contracts")

# Check chinese_related column
if 'is_chinese_related' in df.columns:
    print(f"\n{'='*80}")
    print(f"CHINESE RELATED STATUS")
    print(f"{'='*80}")
    chinese_counts = df['is_chinese_related'].value_counts()
    for status, count in chinese_counts.items():
        print(f"  {status}: {count} contracts")

# Save to CSV
csv_file = "analysis/TED_295_ALL_CONTRACTS.csv"
df.to_csv(csv_file, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
print(f"\n{'='*80}")
print(f"Saved to: {csv_file}")
print(f"{'='*80}")

# Create summary with actual contractor names
summary = {
    'total_contracts': len(df),
    'unique_contractors': len(unique_contractors),
    'top_30_contractors': [
        {'name': name, 'contract_count': int(count)}
        for name, count in unique_contractors.head(30).items()
    ],
    'all_contractors': [
        {'name': name, 'contract_count': int(count)}
        for name, count in unique_contractors.items()
    ]
}

if 'confidence' in df.columns:
    summary['confidence_distribution'] = df['confidence'].value_counts().to_dict()

if 'flag_reason' in df.columns:
    summary['flag_reasons'] = df['flag_reason'].value_counts().to_dict()

# Save JSON
with open('analysis/TED_295_CONTRACTORS_LIST.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"\nContractor list saved to: analysis/TED_295_CONTRACTORS_LIST.json")

# Show sample records
print(f"\n{'='*80}")
print(f"SAMPLE RECORDS (First 5)")
print(f"{'='*80}\n")
for idx, row in df.head(5).iterrows():
    print(f"Record {idx + 1}:")
    print(f"  Contractor: {row['contractor_name']}")
    print(f"  Country: {row['contractor_country']}")
    print(f"  Confidence: {row.get('confidence', 'N/A')}")
    print(f"  Flag Reason: {row.get('flag_reason', 'N/A')}")
    if pd.notna(row.get('chinese_indicators')):
        print(f"  Chinese Indicators: {row['chinese_indicators']}")
    print()
