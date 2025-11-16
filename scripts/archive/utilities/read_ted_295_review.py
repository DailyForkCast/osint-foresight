#!/usr/bin/env python3
"""
Read the TED 295 flagged contracts manual review Excel file
"""

import pandas as pd
import json

excel_file = "c:/Projects/OSINT - Foresight/analysis/TED_295_FLAGGED_CONTRACTS_MANUAL_REVIEW.xlsx"

print("Reading Excel file...")
try:
    # Try reading the Excel file
    df = pd.read_excel(excel_file)

    print(f"\n{'='*80}")
    print(f"TED 295 FLAGGED CONTRACTS - MANUAL REVIEW")
    print(f"{'='*80}")
    print(f"\nTotal records: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    print(f"\n{'='*80}")
    print("FIRST 20 RECORDS:")
    print(f"{'='*80}\n")
    print(df.head(20).to_string())

    # Get unique contractors
    if 'contractor_name' in df.columns:
        unique_contractors = df['contractor_name'].value_counts()
        print(f"\n{'='*80}")
        print(f"UNIQUE CONTRACTORS (Top 30):")
        print(f"{'='*80}\n")
        for contractor, count in unique_contractors.head(30).items():
            print(f"{contractor:<70} ({count:3} contracts)")

        print(f"\nTotal unique contractors: {len(unique_contractors)}")

    # Check for review columns
    review_cols = [col for col in df.columns if 'review' in col.lower() or 'decision' in col.lower() or 'notes' in col.lower()]
    if review_cols:
        print(f"\n{'='*80}")
        print(f"REVIEW COLUMNS FOUND:")
        print(f"{'='*80}")
        for col in review_cols:
            print(f"  - {col}")
            if df[col].notna().any():
                print(f"    Has data: {df[col].notna().sum()} records")

    # Save to CSV for easier viewing
    csv_file = "analysis/TED_295_FLAGGED_CONTRACTS_EXTRACTED.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"\n{'='*80}")
    print(f"Extracted to CSV: {csv_file}")
    print(f"{'='*80}")

    # Save summary as JSON
    summary = {
        'total_records': len(df),
        'columns': list(df.columns),
        'unique_contractors': len(unique_contractors) if 'contractor_name' in df.columns else None,
        'top_contractors': unique_contractors.head(50).to_dict() if 'contractor_name' in df.columns else None
    }

    with open('analysis/TED_295_SUMMARY.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

except Exception as e:
    print(f"Error reading Excel file: {e}")
    print("\nTrying to get sheet names...")
    try:
        xl_file = pd.ExcelFile(excel_file)
        print(f"Sheet names: {xl_file.sheet_names}")

        for sheet in xl_file.sheet_names:
            print(f"\n{'='*80}")
            print(f"Sheet: {sheet}")
            print(f"{'='*80}")
            df = pd.read_excel(excel_file, sheet_name=sheet)
            print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
            print(df.head(10).to_string())
    except Exception as e2:
        print(f"Error: {e2}")
