#!/usr/bin/env python3
"""
Query BigQuery for ACTUAL event counts (no limit)
Compare to our collected counts to determine data loss percentage
"""

from google.cloud import bigquery
import json

print("=" * 80)
print("BIGQUERY ACTUAL EVENT COUNTS - Data Loss Assessment")
print("=" * 80)

# Initialize BigQuery client
client = bigquery.Client()

# Query for actual counts per month (no limit)
query = """
SELECT
    CAST(SQLDATE/100 AS INT64) as month,
    COUNT(*) as actual_events
FROM `gdelt-bq.gdeltv2.events`
WHERE (Actor1CountryCode = 'CHN' OR Actor2CountryCode = 'CHN')
  AND SQLDATE BETWEEN 20210701 AND 20211231
GROUP BY month
ORDER BY month
"""

print("\nQuerying BigQuery for actual China event counts (Jul-Dec 2021)...")
print("This query has NO LIMIT - will count ALL events\n")

query_job = client.query(query)
results = query_job.result()

# Our collected counts
collected = {
    202107: 100636,
    202108: 101175,
    202109: 100490,
    202110: 101390,
    202111: 101323,
    202112: 100000
}

total_actual = 0
total_collected = sum(collected.values())
total_missing = 0

print("MONTH       | ACTUAL (BigQuery) | COLLECTED (Us) | MISSING | DATA LOSS")
print("-" * 80)

results_data = []

for row in results:
    month = int(row.month)
    actual = row.actual_events
    our_count = collected.get(month, 0)
    missing = actual - our_count
    loss_pct = (missing / actual * 100) if actual > 0 else 0

    total_actual += actual
    total_missing += missing

    month_names = {
        202107: "July 2021  ",
        202108: "August 2021",
        202109: "Sept 2021  ",
        202110: "Oct 2021   ",
        202111: "Nov 2021   ",
        202112: "Dec 2021   "
    }

    month_name = month_names.get(month, str(month))
    status = "[OK]" if loss_pct < 1 else "[DATA LOSS]"

    print(f"{month_name} | {actual:>17,} | {our_count:>14,} | {missing:>7,} | {loss_pct:>5.1f}% {status}")

    results_data.append({
        "month": month,
        "actual": actual,
        "collected": our_count,
        "missing": missing,
        "loss_percentage": round(loss_pct, 2)
    })

print("-" * 80)
total_loss_pct = (total_missing / total_actual * 100) if total_actual > 0 else 0
print(f"TOTAL      | {total_actual:>17,} | {total_collected:>14,} | {total_missing:>7,} | {total_loss_pct:>5.1f}%")
print("=" * 80)

# Assessment
print("\nASSESSMENT:")
if total_loss_pct < 1:
    print("[OK] EXCELLENT: Data loss < 1% - current collection is nearly complete")
elif total_loss_pct < 5:
    print("[WARNING] ACCEPTABLE: Data loss < 5% - minor gaps, acceptable for most analyses")
elif total_loss_pct < 10:
    print("[WARNING] CONCERNING: Data loss 5-10% - significant gaps, re-collection recommended")
else:
    print("[CRITICAL] Data loss > 10% - major gaps, re-collection REQUIRED")

print(f"\nTOTAL MISSING: {total_missing:,} events ({total_loss_pct:.1f}% data loss)")

# Save results
report = {
    "query_timestamp": "2025-11-02",
    "date_range": "July-December 2021",
    "total_actual_events": total_actual,
    "total_collected_events": total_collected,
    "total_missing_events": total_missing,
    "data_loss_percentage": round(total_loss_pct, 2),
    "by_month": results_data
}

with open("analysis/bigquery_actual_counts_20251102.json", "w") as f:
    json.dump(report, f, indent=2)

print(f"\nReport saved to: analysis/bigquery_actual_counts_20251102.json")
