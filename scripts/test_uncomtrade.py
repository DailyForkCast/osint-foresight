#!/usr/bin/env python3
"""
Test UN Comtrade API with official package
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import comtradeapicall

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv('.env.local')

# Get keys
primary_key = os.getenv('UNCOMTRADE_PRIMARY_KEY')
secondary_key = os.getenv('UNCOMTRADE_SECONDARY_KEY')

print("="*80)
print("Testing UN Comtrade API with Official Package")
print("="*80)

if primary_key and primary_key != 'YOUR_PRIMARY_KEY_HERE':
    print(f"Primary key found: {primary_key[:10]}...")

    # Test the API
    try:
        print("\n[1] Testing preview endpoint (free tier)...")
        # Preview endpoint - get China's total trade for 2023
        df = comtradeapicall.previewFinalData(
            subscription_key=primary_key,
            typeCode='C',
            freqCode='A',
            clCode='HS',
            reporterCode='156',  # China
            period='2023',
            partnerCode='0',  # World
            flowCode='M,X',  # Imports and Exports
            maxRecords=10
        )

        if df is not None and not df.empty:
            print(f"[OK] Preview data retrieved: {len(df)} records")
            print(f"Sample columns: {df.columns.tolist()[:5]}")
        else:
            print("[ERROR] No preview data returned")

        print("\n[2] Testing full data endpoint (requires subscription)...")
        # Try to get actual trade data
        df2 = comtradeapicall.getFinalData(
            subscription_key=primary_key,
            typeCode='C',
            freqCode='A',
            clCode='HS',
            reporterCode='156',  # China
            period='2023',
            partnerCode='842',  # USA
            flowCode='X',  # Exports
            cmdCode='TOTAL'
        )

        if df2 is not None and not df2.empty:
            print(f"[OK] Full data retrieved: {len(df2)} records")
            print("\nSample data:")
            print(df2[['reporterDesc', 'partnerDesc', 'flowDesc', 'primaryValue']].head())
        else:
            print("[INFO] Full data not available (may require premium subscription)")

    except Exception as e:
        print(f"\n[ERROR] API test failed: {e}")

else:
    print("[ERROR] UN Comtrade API key not found in .env.local")
    print("Please add your keys to .env.local:")
    print("  UNCOMTRADE_PRIMARY_KEY=your_actual_key_here")
    print("  UNCOMTRADE_SECONDARY_KEY=your_actual_key_here")

print("\n" + "="*80)
