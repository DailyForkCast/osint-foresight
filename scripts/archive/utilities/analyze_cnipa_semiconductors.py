#!/usr/bin/env python3
"""
CNIPA Semiconductor Patent Analysis - Made in China 2025 Impact
Test if semiconductor-specific growth reaches 340%
Semiconductors were highest priority in MIC2025 (7 high-priority mentions)
"""

from google.cloud import bigquery
from datetime import datetime
import json

def analyze_semiconductor_growth():
    """
    Analyze CNIPA semiconductor patent growth pre/post Made in China 2025
    CPC H01L = Semiconductor devices; Electric solid state devices not otherwise provided for
    """
    print("=" * 80)
    print("CNIPA SEMICONDUCTOR PATENT ANALYSIS - MADE IN CHINA 2025")
    print("=" * 80)
    print("\nTechnology: Semiconductors (CPC H01L)")
    print("Methodology: Filing dates (not grant dates)")
    print("Pre-policy:  2011-01-01 to 2015-05-07")
    print("Post-policy: 2015-05-08 to 2025-09-30")
    print("\n" + "=" * 80)

    client = bigquery.Client()

    # Query for semiconductor patents (CPC H01L)
    query = """
    WITH semiconductor_patents AS (
        SELECT
            filing_date,
            CASE
                WHEN filing_date >= 20110101 AND filing_date < 20150508 THEN 'pre_policy'
                WHEN filing_date >= 20150508 AND filing_date <= 20250930 THEN 'post_policy'
            END as period
        FROM `patents-public-data.patents.publications`,
            UNNEST(cpc) as cpc_code
        WHERE country_code = 'CN'
            AND filing_date IS NOT NULL
            AND cpc_code.code LIKE 'H01L%'
            AND (
                (filing_date >= 20110101 AND filing_date < 20150508) OR
                (filing_date >= 20150508 AND filing_date <= 20250930)
            )
    ),
    period_counts AS (
        SELECT
            period,
            COUNT(*) as patent_count
        FROM semiconductor_patents
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
        FROM period_counts
    )
    SELECT
        period,
        patent_count,
        annualized_rate
    FROM period_stats
    ORDER BY period
    """

    print("\n[STEP 1] Querying CNIPA semiconductor patents (CPC H01L)...")
    print("This may take 2-3 minutes (scanning CPC classifications)...")

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
        print("RESULTS - SEMICONDUCTOR PATENT GROWTH")
        print("=" * 80)

        print(f"\n[PRE-POLICY: 2011-2015]")
        print(f"  Total semiconductor patents: {pre_count:,}")
        print(f"  Period: 4.35 years")
        print(f"  Annualized rate: {pre_rate:,.0f} patents/year")

        print(f"\n[POST-POLICY: 2015-2025]")
        print(f"  Total semiconductor patents: {post_count:,}")
        print(f"  Period: 10.40 years")
        print(f"  Annualized rate: {post_rate:,.0f} patents/year")

        print(f"\n[GROWTH CALCULATION]")
        print(f"  Growth rate: {growth_rate:.1f}%")
        print(f"  Absolute increase: {post_rate - pre_rate:,.0f} patents/year")

        print("\n" + "=" * 80)
        print("COMPARISON TO OVERALL CNIPA AND USPTO")
        print("=" * 80)

        print(f"\n[OVERALL CNIPA]")
        print(f"  Pre-policy:  1,626,662 patents/year")
        print(f"  Post-policy: 3,829,309 patents/year")
        print(f"  Growth rate: 135.4%")

        print(f"\n[SEMICONDUCTOR CNIPA]")
        print(f"  Pre-policy:  {pre_rate:,.0f} patents/year")
        print(f"  Post-policy: {post_rate:,.0f} patents/year")
        print(f"  Growth rate: {growth_rate:.1f}%")

        print(f"\n[USPTO (overall)]")
        print(f"  Pre-policy:  39,960 patents/year")
        print(f"  Post-policy: 44,478 patents/year")
        print(f"  Growth rate: 11.3%")

        # Calculate sector-specific boost
        overall_cnipa_growth = 135.4
        sector_boost = growth_rate - overall_cnipa_growth

        print(f"\n[SECTOR-SPECIFIC EFFECT]")
        print(f"  Semiconductor growth: {growth_rate:.1f}%")
        print(f"  Overall CNIPA growth: {overall_cnipa_growth}%")
        print(f"  Sector boost: {sector_boost:+.1f} percentage points")

        if sector_boost > 0:
            print(f"  >>> Semiconductors outperformed overall CNIPA by {sector_boost:.1f} pp")
        else:
            print(f"  >>> Semiconductors underperformed overall CNIPA by {abs(sector_boost):.1f} pp")

        print("\n" + "=" * 80)
        print("HYPOTHESIS TEST: 340% CLAIM")
        print("=" * 80)

        if growth_rate >= 340:
            print(f"\n  >>> HYPOTHESIS CONFIRMED! <<<")
            print(f"  Semiconductors show {growth_rate:.1f}% growth (>= 340%)")
            print(f"  The 340% claim refers to CNIPA semiconductor patents!")
        elif growth_rate >= 300:
            print(f"\n  >>> HYPOTHESIS STRONGLY SUPPORTED! <<<")
            print(f"  Semiconductors show {growth_rate:.1f}% growth (close to 340%)")
            print(f"  Within rounding/methodology margin of error")
        elif growth_rate >= 250:
            print(f"\n  >>> HYPOTHESIS PARTIALLY SUPPORTED <<<")
            print(f"  Semiconductors show {growth_rate:.1f}% growth")
            print(f"  Higher than overall CNIPA (135%) but short of 340%")
        else:
            print(f"\n  >>> HYPOTHESIS NOT CONFIRMED <<<")
            print(f"  Semiconductors show {growth_rate:.1f}% growth")
            print(f"  Similar to overall CNIPA, not exceptional")

        # Market share analysis
        pre_share = (pre_rate / 1626662) * 100
        post_share = (post_rate / 3829309) * 100

        print(f"\n[SEMICONDUCTOR MARKET SHARE]")
        print(f"  Pre-policy:  {pre_share:.1f}% of all CNIPA patents")
        print(f"  Post-policy: {post_share:.1f}% of all CNIPA patents")
        print(f"  Change: {post_share - pre_share:+.1f} percentage points")

        if post_share > pre_share:
            print(f"  >>> Semiconductors INCREASED as share of total filings")
        else:
            print(f"  >>> Semiconductors DECREASED as share of total filings")

        # Save results
        results_data = {
            "analysis_date": datetime.now().isoformat(),
            "dataset": "CNIPA semiconductors (CPC H01L)",
            "methodology": "Filing dates (not grant dates)",
            "pre_policy": {
                "period": "2011-01-01 to 2015-05-07",
                "total_patents": pre_count,
                "years": 4.35,
                "annualized_rate": int(pre_rate),
                "market_share_pct": round(pre_share, 1)
            },
            "post_policy": {
                "period": "2015-05-08 to 2025-09-30",
                "total_patents": post_count,
                "years": 10.40,
                "annualized_rate": int(post_rate),
                "market_share_pct": round(post_share, 1)
            },
            "growth": {
                "rate_percent": round(growth_rate, 1),
                "absolute_increase": int(post_rate - pre_rate),
                "sector_boost_vs_overall": round(sector_boost, 1)
            },
            "comparison": {
                "overall_cnipa": 135.4,
                "semiconductor_cnipa": round(growth_rate, 1),
                "uspto_overall": 11.3
            },
            "hypothesis_340_percent": {
                "claim": "340%",
                "actual": f"{growth_rate:.1f}%",
                "confirmed": growth_rate >= 340,
                "strongly_supported": growth_rate >= 300,
                "partially_supported": growth_rate >= 250
            },
            "query_statistics": {
                "bytes_processed": query_job.total_bytes_processed,
                "bytes_billed": query_job.total_bytes_billed,
                "cost_usd": round((query_job.total_bytes_billed / 1e12) * 5, 4)
            }
        }

        output_file = "analysis/cnipa_semiconductors_mic2025.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"\n[OUTPUT]")
        print(f"  Results saved to: {output_file}")

        return results_data

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    results = analyze_semiconductor_growth()

    if results:
        print("\n" + "=" * 80)
        print("SEMICONDUCTOR ANALYSIS COMPLETE")
        print("=" * 80)

        growth = results['growth']['rate_percent']

        if growth >= 340:
            print(f"\n*** BREAKTHROUGH FINDING ***")
            print(f"Semiconductor CNIPA patents show {growth}% growth!")
            print(f"This CONFIRMS the 340% claim!")
        elif growth >= 300:
            print(f"\n*** STRONG EVIDENCE ***")
            print(f"Semiconductor CNIPA patents show {growth}% growth!")
            print(f"This is very close to 340% claim!")
        elif growth >= 250:
            print(f"\n*** PARTIAL CONFIRMATION ***")
            print(f"Semiconductor CNIPA patents show {growth}% growth!")
            print(f"Higher than overall but short of 340%.")
        else:
            print(f"\n*** RESULT ***")
            print(f"Semiconductor CNIPA patents show {growth}% growth.")

        print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
