#!/usr/bin/env python3
"""
Diagnostic script to understand why CSIS date filtering isn't working.

This script will:
1. Fetch the first 20 items from CSIS sitemap
2. Print out what dates are being returned
3. Show which items pass the date filter
"""

import sys
import yaml
from datetime import datetime, timezone
from dateutil import parser as date_parser

# Import our modules
from thinktank_base_collector import DiscoveryEngine

def main():
    # Load source rules
    with open("C:/Projects/OSINT - Foresight/config/thinktank_source_rules.yaml", 'r') as f:
        source_rules = yaml.safe_load(f)

    rules = source_rules.get("csis.org", source_rules["default"])

    # Initialize discovery engine
    engine = DiscoveryEngine("csis.org", rules)

    # Discover items (limit to first 20 for debugging)
    print("Fetching items from CSIS sitemap...")
    discovered = engine.discover_all(max_pages=40)

    print(f"\nTotal items discovered: {len(discovered)}")
    print(f"\nAnalyzing first 20 items:\n")
    print("=" * 100)

    # Define time windows (Lane A: 2025+, Lane B: 2024)
    lane_a_start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    lane_a_end = datetime.now(timezone.utc)

    matches_window = 0
    outside_window = 0
    no_date = 0

    for idx, item in enumerate(discovered[:20]):
        url = item.get("url", "")
        pub_date_str = item.get("publication_date")
        fetch_mode = item.get("fetch_mode", "")

        print(f"\n{idx+1}. URL: {url[:80]}...")
        print(f"   Fetch Mode: {fetch_mode}")
        print(f"   Raw publication_date field: {repr(pub_date_str)}")

        # Try to parse the date
        if pub_date_str:
            try:
                pub_date = date_parser.parse(pub_date_str)
                print(f"   Parsed date: {pub_date.isoformat()}")
                print(f"   Year: {pub_date.year}")

                # Check if in window
                if lane_a_start <= pub_date <= lane_a_end:
                    print(f"   ✓ IN LANE A (2025+)")
                    matches_window += 1
                elif pub_date.year == 2024:
                    print(f"   ✓ IN LANE B (2024)")
                    matches_window += 1
                else:
                    print(f"   ✗ OUTSIDE WINDOW (year {pub_date.year})")
                    outside_window += 1
            except Exception as e:
                print(f"   ERROR parsing date: {e}")
                no_date += 1
        else:
            print(f"   ✗ NO DATE in metadata")
            no_date += 1

        print("-" * 100)

    print(f"\n" + "=" * 100)
    print(f"\nSUMMARY (first 20 items):")
    print(f"  Matches time window: {matches_window}")
    print(f"  Outside time window: {outside_window}")
    print(f"  No date in metadata: {no_date}")
    print(f"\nIf pre-filtering works correctly, we should only process {matches_window + no_date} items (not all 20)")

if __name__ == "__main__":
    main()
