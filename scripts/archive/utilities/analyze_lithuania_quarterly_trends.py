#!/usr/bin/env python3
"""
Analyze Lithuania-China Quarterly Publication Trends
Shows when crisis impact becomes visible with publication lag
"""

import requests
import json
from collections import defaultdict
from datetime import datetime

print("=" * 80)
print("LITHUANIA-CHINA QUARTERLY PUBLICATION ANALYSIS")
print("=" * 80)

# Fetch all Lithuania-China works from 2021-2025
all_works = []
page = 1
per_page = 200

print("\nFetching data from OpenAlex API...")

while True:
    url = f"https://api.openalex.org/works?filter=institutions.country_code:LT,authorships.institutions.country_code:CN,from_publication_date:2021-01-01,to_publication_date:2025-12-31&per-page={per_page}&page={page}"

    response = requests.get(url)
    data = response.json()

    results = data.get('results', [])
    if not results:
        break

    all_works.extend(results)
    print(f"  Page {page}: {len(results)} works (Total: {len(all_works)})")

    page += 1

    # Safety limit
    if page > 10:
        break

print(f"\nTotal works collected: {len(all_works)}")

# Analyze by quarter
quarterly = defaultdict(int)

for work in all_works:
    pub_date = work.get('publication_date')
    if not pub_date:
        continue

    try:
        date = datetime.strptime(pub_date, '%Y-%m-%d')
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        key = f"{year}-Q{quarter}"
        quarterly[key] += 1
    except:
        continue

# Sort and display
print("\n" + "=" * 80)
print("QUARTERLY PUBLICATION TRENDS")
print("=" * 80)

quarters = sorted(quarterly.keys())

# Calculate quarterly averages
q_data = {}
for q in quarters:
    q_data[q] = quarterly[q]

# Display with analysis
print(f"\n{'Quarter':<12} {'Works':<10} {'Change':<12} {'% Change':<12} {'Context'}")
print("-" * 80)

prev_count = None
for i, q in enumerate(quarters):
    count = q_data[q]

    # Calculate change
    if prev_count is not None:
        change = count - prev_count
        pct_change = (change / prev_count * 100) if prev_count > 0 else 0
        change_str = f"{change:+d}"
        pct_str = f"{pct_change:+.1f}%"
    else:
        change_str = "-"
        pct_str = "-"

    # Context
    year, qtr = q.split('-')
    if year == '2021' and qtr in ['Q3', 'Q4']:
        context = "CRISIS PERIOD (Jul-Dec)"
    elif year == '2023' and qtr == 'Q1':
        context = "Backlog peak?"
    elif year == '2024':
        context = "Lagged impact visible"
    elif year == '2025':
        context = "Continued decline"
    else:
        context = ""

    print(f"{q:<12} {count:<10} {change_str:<12} {pct_str:<12} {context}")

    prev_count = count

# Annual summaries
print("\n" + "=" * 80)
print("ANNUAL SUMMARIES (from quarterly data)")
print("=" * 80)

annual = defaultdict(int)
for q, count in q_data.items():
    year = q.split('-')[0]
    annual[year] += count

prev_year_count = None
for year in sorted(annual.keys()):
    count = annual[year]

    if prev_year_count is not None:
        change = count - prev_year_count
        pct_change = (change / prev_year_count * 100) if prev_year_count > 0 else 0
        print(f"{year}: {count:3d} works ({change:+3d}, {pct_change:+5.1f}%)")
    else:
        print(f"{year}: {count:3d} works (baseline)")

    prev_year_count = count

# Key findings
print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)

# Compare Q3-Q4 2021 (crisis) to Q3-Q4 2023 (2-year lag)
q3q4_2021 = q_data.get('2021-Q3', 0) + q_data.get('2021-Q4', 0)
q3q4_2023 = q_data.get('2023-Q3', 0) + q_data.get('2023-Q4', 0)

print(f"\n1. IMMEDIATE IMPACT (Q3-Q4 2021 vs Q3-Q4 2023):")
print(f"   2021 Q3-Q4: {q3q4_2021} works (crisis period)")
print(f"   2023 Q3-Q4: {q3q4_2023} works (2-year lag)")
if q3q4_2021 > 0:
    print(f"   Change: {((q3q4_2023 - q3q4_2021) / q3q4_2021 * 100):+.1f}% (expected: minimal - pipeline effect)")

# Compare 2022 vs 2024 (full year, 2-year lag)
y_2022 = annual.get('2022', 0)
y_2024 = annual.get('2024', 0)

print(f"\n2. LAGGED IMPACT (2022 vs 2024):")
print(f"   2022: {y_2022} works (1 year post-crisis)")
print(f"   2024: {y_2024} works (3 years post-crisis)")
if y_2022 > 0:
    print(f"   Change: {((y_2024 - y_2022) / y_2022 * 100):+.1f}% (expected: significant decline)")

# Peak quarter
max_q = max(q_data.items(), key=lambda x: x[1])
print(f"\n3. PEAK QUARTER: {max_q[0]} with {max_q[1]} works")

# Current trend (last 4 quarters)
recent_qs = sorted(quarters)[-4:]
recent_avg = sum(q_data[q] for q in recent_qs) / 4
print(f"\n4. RECENT TREND (last 4 quarters):")
print(f"   Quarters: {', '.join(recent_qs)}")
print(f"   Average: {recent_avg:.1f} works/quarter")

print("\n" + "=" * 80)

# Save detailed data
output = {
    "analysis_date": "2025-11-02",
    "data_source": "OpenAlex API",
    "total_works_2021_2025": len(all_works),
    "quarterly_data": dict(q_data),
    "annual_summary": dict(annual),
    "key_findings": {
        "crisis_period_q3q4_2021": q3q4_2021,
        "two_year_lag_q3q4_2023": q3q4_2023,
        "baseline_year_2022": y_2022,
        "impact_year_2024": y_2024,
        "peak_quarter": max_q[0],
        "peak_count": max_q[1]
    }
}

with open('analysis/lithuania_quarterly_analysis_20251102.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Detailed data saved to: analysis/lithuania_quarterly_analysis_20251102.json")
print("=" * 80)
