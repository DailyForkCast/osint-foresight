#!/usr/bin/env python3
"""
Real-time dashboard for China analysis progress
"""

from pathlib import Path
from datetime import datetime
import json
import time

def show_dashboard():
    print("\033[2J\033[H")  # Clear screen
    print("=" * 80)
    print(" USASPENDING CHINA ANALYSIS DASHBOARD ".center(80, "="))
    print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".center(80))
    print("=" * 80)

    # 1. Data Status
    print("\n[1] DATA FILES STATUS")
    print("-" * 40)

    base_path = Path("F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/")
    files = ['5801', '5836', '5847', '5848', '5862']
    total_size = 0

    for name in files:
        dat_file = base_path / f"{name}.dat"
        if dat_file.exists():
            size = dat_file.stat().st_size / 1e9
            total_size += size

            # Check for PostgreSQL end marker
            with open(dat_file, 'rb') as f:
                f.seek(max(0, dat_file.stat().st_size - 100))
                complete = b'\\.' in f.read(100)

            status = "[OK]" if complete else "[!]"
            print(f"  {status} {name}.dat: {size:7.2f} GB")

    print(f"\n  Total data: {total_size:.2f} GB")

    # 2. Initial Analysis Results
    print("\n[2] INITIAL CHINA PATTERN SCAN")
    print("-" * 40)

    results_file = Path("china_pattern_analysis_results.json")
    if results_file.exists():
        with open(results_file) as f:
            results = json.load(f)

        total_china = sum(r.get('estimated_total_china_mentions', 0) for r in results.values())
        print(f"  Total China mentions: {total_china:,}")

        # File breakdown
        for file_name, data in results.items():
            if 'estimated_total_china_mentions' in data:
                mentions = data['estimated_total_china_mentions']
                pct = data.get('china_percentage', 0)
                if mentions > 0:
                    print(f"    {file_name}: {mentions:,} ({pct:.2f}% of file)")
    else:
        print("  Analysis pending...")

    # 3. Deep Dive Status
    print("\n[3] DEEP DIVE EXTRACTION (File 5848)")
    print("-" * 40)

    detailed_file = Path("china_contracts_detailed.json")
    if detailed_file.exists():
        with open(detailed_file) as f:
            detailed = json.load(f)

        stats = detailed.get('processing_stats', {})
        print(f"  Lines processed: {stats.get('lines_processed', 0):,}")
        print(f"  China records found: {stats.get('china_records_found', 0):,}")
        print(f"  High-value contracts: {stats.get('high_value_count', 0):,}")
        print(f"  Defense-related: {stats.get('defense_related', 0):,}")

        # Top entities
        top_entities = detailed.get('top_entities', {})
        if top_entities:
            print("\n  Top China Entities:")
            for entity, count in list(top_entities.items())[:5]:
                print(f"    {entity}: {count:,}")
    else:
        print("  Extraction in progress...")
        print("  (Processing 222 GB file - est. 10-15 min)")

    # 4. MCF Entity Search
    print("\n[4] MILITARY-CIVIL FUSION ENTITY SEARCH")
    print("-" * 40)

    mcf_file = Path("mcf_entity_search_results.json")
    if mcf_file.exists():
        with open(mcf_file) as f:
            mcf_results = json.load(f)

        summary = mcf_results.get('summary', {})
        print(f"  Total MCF mentions: {summary.get('total_mcf_mentions', 0):,}")
        print(f"  Critical findings: {summary.get('critical_findings_count', 0):,}")
        print(f"  Entities found: {summary.get('entities_found', 0)}")

        # Top MCF entities
        entity_totals = mcf_results.get('entity_totals', {})
        if entity_totals:
            print("\n  High-Risk Entities Detected:")
            sorted_entities = sorted(entity_totals.items(),
                                    key=lambda x: x[1].get('total', 0),
                                    reverse=True)
            for entity, info in sorted_entities[:5]:
                risk = info.get('risk', 'UNKNOWN')
                total = info.get('total', 0)
                print(f"    {entity}: {total:,} [{risk}]")
    else:
        print("  MCF search in progress...")
        print("  Searching for: Huawei, ZTE, Hikvision, DJI, etc.")

    # 5. Risk Assessment
    print("\n[5] RISK ASSESSMENT SUMMARY")
    print("-" * 40)

    risk_levels = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0
    }

    if mcf_file.exists():
        with open(mcf_file) as f:
            mcf_data = json.load(f)

        for entity, info in mcf_data.get('entity_totals', {}).items():
            risk = info.get('risk', 'UNKNOWN')
            if risk in risk_levels:
                risk_levels[risk] += info.get('total', 0)

    print(f"  CRITICAL risk mentions: {risk_levels['CRITICAL']:,}")
    print(f"  HIGH risk mentions: {risk_levels['HIGH']:,}")
    print(f"  MEDIUM risk mentions: {risk_levels['MEDIUM']:,}")

    if risk_levels['CRITICAL'] > 0:
        print("\n  [!] ALERT: Critical risk entities detected in USASpending!")
        print("      Immediate review recommended for defense/telecom contracts")

    # 6. Next Steps
    print("\n[6] RECOMMENDED ACTIONS")
    print("-" * 40)

    if detailed_file.exists() and mcf_file.exists():
        print("  1. Review critical MCF entity findings")
        print("  2. Extract full contract details for high-risk entities")
        print("  3. Cross-reference with Entity List and sanctions")
        print("  4. Generate timeline of China engagement growth")
        print("  5. Identify departments with highest China exposure")
    else:
        print("  Waiting for analysis to complete...")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    while True:
        show_dashboard()
        print("\nRefreshing in 30 seconds... (Press Ctrl+C to exit)")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            break
