#!/usr/bin/env python3
"""
CNIPA Patent Analysis - Made in China 2025 Impact
Test if 340% growth claim is true for domestic Chinese patents
Using same methodology as USPTO analysis for direct comparison
"""

from google.cloud import bigquery
from datetime import datetime
import json

def analyze_cnipa_growth():
    """
    Analyze CNIPA patent growth pre/post Made in China 2025
    Same methodology as USPTO analysis for direct comparison
    """
    print("=" * 80)
    print("CNIPA PATENT ANALYSIS - MADE IN CHINA 2025 IMPACT")
    print("=" * 80)
    print("\nMethodology: Filing dates (not grant dates)")
    print("Pre-policy:  2011-01-01 to 2015-05-07")
    print("Post-policy: 2015-05-08 to 2025-09-30 (latest available)")
    print("\n" + "=" * 80)

    client = bigquery.Client()

    # Query for overall patent counts
    query = """
    WITH periods AS (
        SELECT
            CASE
                WHEN filing_date >= 20110101 AND filing_date < 20150508 THEN 'pre_policy'
                WHEN filing_date >= 20150508 AND filing_date <= 20250930 THEN 'post_policy'
            END as period,
            COUNT(*) as patent_count
        FROM `patents-public-data.patents.publications`
        WHERE country_code = 'CN'
            AND filing_date IS NOT NULL
            AND (
                (filing_date >= 20110101 AND filing_date < 20150508) OR
                (filing_date >= 20150508 AND filing_date <= 20250930)
            )
        GROUP BY period
    ),
    period_stats AS (
        SELECT
            period,
            patent_count,
            CASE
                WHEN period = 'pre_policy' THEN
                    CAST(patent_count AS FLOAT64) / ((DATE_DIFF(DATE(2015, 5, 7), DATE(2011, 1, 1), DAY)) / 365.25)
                WHEN period = 'post_policy' THEN
                    CAST(patent_count AS FLOAT64) / ((DATE_DIFF(DATE(2025, 9, 30), DATE(2015, 5, 8), DAY)) / 365.25)
            END as annualized_rate
        FROM periods
    )
    SELECT
        period,
        patent_count,
        annualized_rate
    FROM period_stats
    ORDER BY period
    """

    print("\n[STEP 1] Querying CNIPA patent counts...")
    print("This may take 1-2 minutes (scanning ~50M patents)...")

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        print(f"\n  Query completed!")
        print(f"  Bytes processed: {query_job.total_bytes_processed:,}")
        print(f"  Bytes billed: {query_job.total_bytes_billed:,}")
        print(f"  Cost estimate: ${(query_job.total_bytes_billed / 1e12) * 5:.4f}")

        # Parse results
        pre_data = [r for r in results if r['period'] == 'pre_policy'][0]
        post_data = [r for r in results if r['period'] == 'post_policy'][0]

        pre_count = pre_data['patent_count']
        post_count = post_data['patent_count']
        pre_rate = pre_data['annualized_rate']
        post_rate = post_data['annualized_rate']

        # Calculate growth
        growth_rate = ((post_rate - pre_rate) / pre_rate) * 100

        print("\n" + "=" * 80)
        print("RESULTS - CNIPA PATENT GROWTH")
        print("=" * 80)

        print(f"\n[PRE-POLICY: 2011-2015]")
        print(f"  Total patents: {pre_count:,}")
        print(f"  Period: 4.35 years")
        print(f"  Annualized rate: {pre_rate:,.0f} patents/year")

        print(f"\n[POST-POLICY: 2015-2025]")
        print(f"  Total patents: {post_count:,}")
        print(f"  Period: 10.40 years")
        print(f"  Annualized rate: {post_rate:,.0f} patents/year")

        print(f"\n[GROWTH CALCULATION]")
        print(f"  Growth rate: {growth_rate:.1f}%")
        print(f"  Absolute increase: {post_rate - pre_rate:,.0f} patents/year")

        print("\n" + "=" * 80)
        print("COMPARISON TO USPTO")
        print("=" * 80)

        print(f"\n[USPTO (from validation report)]")
        print(f"  Pre-policy:  39,960 patents/year")
        print(f"  Post-policy: 44,478 patents/year")
        print(f"  Growth rate: 11.3%")

        print(f"\n[CNIPA (this analysis)]")
        print(f"  Pre-policy:  {pre_rate:,.0f} patents/year")
        print(f"  Post-policy: {post_rate:,.0f} patents/year")
        print(f"  Growth rate: {growth_rate:.1f}%")

        print("\n" + "=" * 80)
        print("HYPOTHESIS TEST: 340% CLAIM")
        print("=" * 80)

        if growth_rate >= 300:
            print(f"\n  ✓ HYPOTHESIS CONFIRMED!")
            print(f"  CNIPA shows {growth_rate:.1f}% growth (>= 340%)")
            print(f"  The 340% claim likely refers to CNIPA data")
        elif growth_rate >= 250:
            print(f"\n  ~ HYPOTHESIS PARTIALLY SUPPORTED")
            print(f"  CNIPA shows {growth_rate:.1f}% growth (close to 340%)")
            print(f"  Claim may be rounded or use different methodology")
        else:
            print(f"\n  ✗ HYPOTHESIS NOT CONFIRMED")
            print(f"  CNIPA shows {growth_rate:.1f}% growth (< 340%)")
            print(f"  340% claim remains unexplained by CNIPA data")

        # Save results to JSON
        results_data = {
            "analysis_date": datetime.now().isoformat(),
            "dataset": "CNIPA (patents-public-data)",
            "methodology": "Filing dates (not grant dates)",
            "pre_policy": {
                "period": "2011-01-01 to 2015-05-07",
                "total_patents": pre_count,
                "years": 4.35,
                "annualized_rate": int(pre_rate)
            },
            "post_policy": {
                "period": "2015-05-08 to 2025-09-30",
                "total_patents": post_count,
                "years": 10.40,
                "annualized_rate": int(post_rate)
            },
            "growth": {
                "rate_percent": round(growth_rate, 1),
                "absolute_increase": int(post_rate - pre_rate)
            },
            "comparison_to_uspto": {
                "uspto_growth": 11.3,
                "cnipa_growth": round(growth_rate, 1),
                "cnipa_vs_uspto_multiple": round(growth_rate / 11.3, 1)
            },
            "hypothesis_340_percent": {
                "claim": "340% growth",
                "actual": f"{growth_rate:.1f}%",
                "confirmed": growth_rate >= 300
            },
            "query_statistics": {
                "bytes_processed": query_job.total_bytes_processed,
                "bytes_billed": query_job.total_bytes_billed,
                "cost_usd": round((query_job.total_bytes_billed / 1e12) * 5, 4)
            }
        }

        output_file = "analysis/cnipa_mic2025_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"\n[OUTPUT]")
        print(f"  Results saved to: {output_file}")

        return results_data

    except Exception as e:
        print(f"\nERROR: {e}")
        return None

def main():
    results = analyze_cnipa_growth()

    if results:
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

        # Print key finding
        growth = results['growth']['rate_percent']
        if growth >= 300:
            print(f"\n>>> CNIPA shows {growth}% growth - 340% claim likely refers to CNIPA! <<<")
        else:
            print(f"\n>>> CNIPA shows {growth}% growth - different from 340% claim <<<")

        print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
