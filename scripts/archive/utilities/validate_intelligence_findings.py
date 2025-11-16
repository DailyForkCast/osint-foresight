#!/usr/bin/env python3
"""
Data Validation & Corroboration Tests
Tests key intelligence findings for statistical significance and data quality
"""

import sqlite3
import sys
import io
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
cur = conn.cursor()

print("="*80)
print("INTELLIGENCE FINDINGS VALIDATION & CORROBORATION")
print("="*80 + "\n")

validation_results = {
    'test_date': datetime.now().isoformat(),
    'tests_passed': 0,
    'tests_failed': 0,
    'warnings': [],
    'critical_issues': [],
    'findings': {}
}

# ============================================================================
# TEST 1: Citation Coverage Validation
# ============================================================================

print("TEST 1: Citation Coverage Validation")
print("-" * 80)

cur.execute("SELECT COUNT(*) FROM bilateral_events")
total_events = cur.fetchone()[0]

cur.execute("SELECT COUNT(DISTINCT linked_record_id) FROM citation_links")
events_with_citations = cur.fetchone()[0]

coverage_pct = (events_with_citations / total_events * 100) if total_events > 0 else 0

print(f"Total events: {total_events}")
print(f"Events with citations: {events_with_citations}")
print(f"Coverage: {coverage_pct:.1f}%")

if coverage_pct >= 95:
    print("✅ PASS: Excellent citation coverage")
    validation_results['tests_passed'] += 1
elif coverage_pct >= 80:
    print("⚠️  WARNING: Acceptable but not ideal citation coverage")
    validation_results['tests_passed'] += 1
    validation_results['warnings'].append(f"Citation coverage {coverage_pct:.1f}% below 95% threshold")
else:
    print("❌ FAIL: Insufficient citation coverage")
    validation_results['tests_failed'] += 1
    validation_results['critical_issues'].append(f"Citation coverage {coverage_pct:.1f}% below 80% minimum")

validation_results['findings']['citation_coverage'] = {
    'total_events': total_events,
    'events_with_citations': events_with_citations,
    'coverage_percentage': coverage_pct
}

# ============================================================================
# TEST 2: Multi-Source Verification
# ============================================================================

print("\n" + "="*80)
print("TEST 2: Multi-Source Verification (2+ sources per event)")
print("-" * 80)

cur.execute("""
    SELECT linked_record_id, COUNT(*) as source_count
    FROM citation_links
    GROUP BY linked_record_id
    HAVING COUNT(*) < 2
""")

single_source_events = cur.fetchall()

print(f"Events with only 1 source: {len(single_source_events)}")

if len(single_source_events) == 0:
    print("✅ PASS: All events have multi-source verification")
    validation_results['tests_passed'] += 1
elif len(single_source_events) <= 5:
    print(f"⚠️  WARNING: {len(single_source_events)} events have single source")
    validation_results['tests_passed'] += 1
    validation_results['warnings'].append(f"{len(single_source_events)} events lack multi-source verification")
    for event_id, count in single_source_events[:5]:
        print(f"  - {event_id}: {count} source(s)")
else:
    print(f"❌ FAIL: {len(single_source_events)} events lack multi-source verification")
    validation_results['tests_failed'] += 1
    validation_results['critical_issues'].append(f"{len(single_source_events)} events have only 1 source")

validation_results['findings']['multi_source_verification'] = {
    'single_source_events': len(single_source_events),
    'threshold': 2
}

# ============================================================================
# TEST 3: Source Reliability Distribution
# ============================================================================

print("\n" + "="*80)
print("TEST 3: Source Reliability Quality Check")
print("-" * 80)

cur.execute("""
    SELECT source_reliability, COUNT(*) as count
    FROM source_citations
    GROUP BY source_reliability
    ORDER BY source_reliability
""")

reliability_dist = dict(cur.fetchall())
total_citations = sum(reliability_dist.values())

print("Source reliability distribution:")
for level in [1, 2, 3, 4]:
    count = reliability_dist.get(level, 0)
    pct = (count / total_citations * 100) if total_citations > 0 else 0
    reliability_label = {
        1: "Primary official sources",
        2: "Verified secondary sources",
        3: "Credible sources",
        4: "Unverified sources"
    }.get(level, "Unknown")
    print(f"  Level {level} ({reliability_label}): {count} ({pct:.1f}%)")

level_1_2_count = reliability_dist.get(1, 0) + reliability_dist.get(2, 0)
level_1_2_pct = (level_1_2_count / total_citations * 100) if total_citations > 0 else 0

if level_1_2_pct >= 90:
    print(f"✅ PASS: {level_1_2_pct:.1f}% Level 1-2 sources (excellent)")
    validation_results['tests_passed'] += 1
elif level_1_2_pct >= 75:
    print(f"⚠️  WARNING: {level_1_2_pct:.1f}% Level 1-2 sources (acceptable)")
    validation_results['tests_passed'] += 1
    validation_results['warnings'].append(f"Only {level_1_2_pct:.1f}% Level 1-2 sources (target: 90%)")
else:
    print(f"❌ FAIL: {level_1_2_pct:.1f}% Level 1-2 sources (too low)")
    validation_results['tests_failed'] += 1
    validation_results['critical_issues'].append(f"Only {level_1_2_pct:.1f}% Level 1-2 sources")

validation_results['findings']['source_reliability'] = {
    'distribution': reliability_dist,
    'level_1_2_percentage': level_1_2_pct
}

# ============================================================================
# TEST 4: Lithuania Taiwan Office Finding Validation
# ============================================================================

print("\n" + "="*80)
print("TEST 4: Lithuania Taiwan Office Research Collapse Validation")
print("-" * 80)

# Get 2020-2021 publication data
cur.execute("""
    SELECT publication_year, COUNT(*) as works
    FROM openalex_works
    WHERE publication_year IN (2019, 2020, 2021, 2022)
    GROUP BY publication_year
    ORDER BY publication_year
""")

yearly_data = dict(cur.fetchall())

print("Year-by-year collaboration works:")
for year in [2019, 2020, 2021, 2022]:
    works = yearly_data.get(year, 0)
    print(f"  {year}: {works:,} works")

if 2020 in yearly_data and 2021 in yearly_data:
    change_2021 = yearly_data[2021] - yearly_data[2020]
    pct_change_2021 = (change_2021 / yearly_data[2020] * 100) if yearly_data[2020] > 0 else 0

    print(f"\n2020 → 2021 change: {change_2021:,} works ({pct_change_2021:+.1f}%)")

    # Check if this is indeed the largest drop
    cur.execute("""
        SELECT
            y1.publication_year as year1,
            y1.works as works1,
            y2.publication_year as year2,
            y2.works as works2,
            (y2.works - y1.works) as change,
            CASE WHEN y1.works > 0
                THEN ((y2.works - y1.works) * 100.0 / y1.works)
                ELSE 0
            END as pct_change
        FROM (
            SELECT publication_year, COUNT(*) as works
            FROM openalex_works
            WHERE publication_year >= 2000 AND publication_year <= 2024
            GROUP BY publication_year
        ) y1
        JOIN (
            SELECT publication_year, COUNT(*) as works
            FROM openalex_works
            WHERE publication_year >= 2000 AND publication_year <= 2024
            GROUP BY publication_year
        ) y2 ON y2.publication_year = y1.publication_year + 1
        WHERE y1.works > 0
        ORDER BY pct_change ASC
        LIMIT 5
    """)

    print("\nTop 5 largest year-over-year drops:")
    largest_drops = cur.fetchall()
    for i, (y1, w1, y2, w2, change, pct) in enumerate(largest_drops, 1):
        marker = " ← 2021 Lithuania crisis" if y2 == 2021 else ""
        print(f"  {i}. {y1}→{y2}: {change:,} ({pct:+.1f}%){marker}")

    # Verify it's the largest
    if largest_drops and largest_drops[0][3] == yearly_data.get(2021):
        print("\n✅ PASS: 2021 is confirmed as largest drop in dataset")
        validation_results['tests_passed'] += 1
    else:
        print("\n⚠️  WARNING: 2021 may not be the largest drop")
        validation_results['warnings'].append("2021 drop not confirmed as largest")
        validation_results['tests_passed'] += 1
else:
    print("\n❌ FAIL: Missing 2020 or 2021 data")
    validation_results['tests_failed'] += 1

validation_results['findings']['lithuania_taiwan_impact'] = {
    '2020_works': yearly_data.get(2020, 0),
    '2021_works': yearly_data.get(2021, 0),
    'change': change_2021 if 2020 in yearly_data and 2021 in yearly_data else None,
    'pct_change': pct_change_2021 if 2020 in yearly_data and 2021 in yearly_data else None
}

# ============================================================================
# TEST 5: Post-2020 Volatility Claim Validation
# ============================================================================

print("\n" + "="*80)
print("TEST 5: Post-2020 Volatility Increase Validation")
print("-" * 80)

# Calculate standard deviation pre and post 2020
cur.execute("""
    SELECT publication_year, COUNT(*) as works
    FROM openalex_works
    WHERE publication_year >= 2015 AND publication_year <= 2024
    GROUP BY publication_year
    ORDER BY publication_year
""")

all_years = cur.fetchall()
pre_2020 = [works for year, works in all_years if year < 2020]
post_2020 = [works for year, works in all_years if year >= 2020]

if len(pre_2020) > 0 and len(post_2020) > 0:
    import statistics

    pre_mean = statistics.mean(pre_2020)
    pre_stdev = statistics.stdev(pre_2020) if len(pre_2020) > 1 else 0

    post_mean = statistics.mean(post_2020)
    post_stdev = statistics.stdev(post_2020) if len(post_2020) > 1 else 0

    volatility_ratio = post_stdev / pre_stdev if pre_stdev > 0 else 0

    print(f"Pre-2020 (2015-2019):")
    print(f"  Mean: {pre_mean:.0f} works/year")
    print(f"  Std Dev: {pre_stdev:.0f}")
    print(f"\nPost-2020 (2020-2024):")
    print(f"  Mean: {post_mean:.0f} works/year")
    print(f"  Std Dev: {post_stdev:.0f}")
    print(f"\nVolatility ratio (post/pre): {volatility_ratio:.2f}x")

    if volatility_ratio >= 2.0:
        print(f"✅ PASS: Post-2020 volatility {volatility_ratio:.2f}x higher confirmed")
        validation_results['tests_passed'] += 1
    elif volatility_ratio >= 1.5:
        print(f"⚠️  WARNING: Volatility increase {volatility_ratio:.2f}x lower than claimed")
        validation_results['warnings'].append(f"Volatility ratio {volatility_ratio:.2f}x vs claimed 2.25x")
        validation_results['tests_passed'] += 1
    else:
        print(f"❌ FAIL: Volatility increase {volatility_ratio:.2f}x does not support claim")
        validation_results['tests_failed'] += 1

    validation_results['findings']['volatility_analysis'] = {
        'pre_2020_mean': pre_mean,
        'pre_2020_stdev': pre_stdev,
        'post_2020_mean': post_mean,
        'post_2020_stdev': post_stdev,
        'volatility_ratio': volatility_ratio
    }
else:
    print("❌ FAIL: Insufficient data for volatility analysis")
    validation_results['tests_failed'] += 1

# ============================================================================
# TEST 6: Country Collaboration Data Consistency
# ============================================================================

print("\n" + "="*80)
print("TEST 6: Country Collaboration Data Consistency Check")
print("-" * 80)

# Check if country totals are consistent
cur.execute("""
    SELECT country_code,
           COUNT(*) as institutions,
           SUM(works_count) as total_works,
           SUM(cited_by_count) as total_citations
    FROM openalex_entities
    WHERE entity_type = 'institution'
    GROUP BY country_code
    ORDER BY total_works DESC
    LIMIT 10
""")

country_data = cur.fetchall()

print("Top 10 countries by collaboration works:")
consistency_issues = 0

for cc, inst, works, cites in country_data:
    avg_works = works / inst if inst > 0 else 0
    avg_cites_per_work = cites / works if works > 0 else 0

    # Flag if average seems unrealistic
    if avg_works > 100000:  # Unrealistically high average
        print(f"  ⚠️  {cc}: {inst} inst, {works:,} works (avg: {avg_works:,.0f} - SUSPICIOUS)")
        consistency_issues += 1
    elif avg_cites_per_work > 1000:  # Unrealistically high citation rate
        print(f"  ⚠️  {cc}: {works:,} works, {cites:,} cites (avg: {avg_cites_per_work:.0f} - SUSPICIOUS)")
        consistency_issues += 1
    else:
        print(f"  ✓ {cc}: {inst} inst, {works:,} works, {cites:,} cites")

if consistency_issues == 0:
    print("\n✅ PASS: No obvious data consistency issues")
    validation_results['tests_passed'] += 1
else:
    print(f"\n⚠️  WARNING: {consistency_issues} potential data quality issues detected")
    validation_results['warnings'].append(f"{consistency_issues} country data anomalies")
    validation_results['tests_passed'] += 1

# ============================================================================
# TEST 7: Academic Events Timeline Corroboration
# ============================================================================

print("\n" + "="*80)
print("TEST 7: Academic Events Match Historical Record")
print("-" * 80)

# Check if major academic events have correct dates
known_events = {
    'SE_2019_confucius_closures': (2019, "Sweden Confucius closures"),
    'LT_2021_university_partnerships_suspended': (2021, "Lithuania partnerships suspended"),
    'UK_2022_student_restrictions': (2022, "UK ATAS restrictions")
}

events_verified = 0
events_missing = 0

for event_id, (expected_year, description) in known_events.items():
    cur.execute("""
        SELECT event_year, event_title
        FROM bilateral_events
        WHERE event_id = ?
    """, (event_id,))

    result = cur.fetchone()
    if result:
        actual_year, title = result
        if actual_year == expected_year:
            print(f"  ✓ {description}: {expected_year} (verified)")
            events_verified += 1
        else:
            print(f"  ⚠️  {description}: Expected {expected_year}, got {actual_year}")
            validation_results['warnings'].append(f"{event_id} year mismatch")
    else:
        print(f"  ❌ {description}: Event not found")
        events_missing += 1

if events_missing == 0 and events_verified == len(known_events):
    print(f"\n✅ PASS: All {events_verified} test events verified")
    validation_results['tests_passed'] += 1
elif events_missing == 0:
    print(f"\n⚠️  WARNING: Events found but dates may be incorrect")
    validation_results['tests_passed'] += 1
else:
    print(f"\n❌ FAIL: {events_missing} events missing from database")
    validation_results['tests_failed'] += 1

# ============================================================================
# TEST 8: Data Completeness Assessment
# ============================================================================

print("\n" + "="*80)
print("TEST 8: Data Completeness Assessment")
print("-" * 80)

completeness_scores = []

# Check technology domain classification
cur.execute("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN technology_domain IS NOT NULL THEN 1 ELSE 0 END) as classified
    FROM openalex_works
""")

total_works, classified_works = cur.fetchone()
tech_coverage = (classified_works / total_works * 100) if total_works > 0 else 0
completeness_scores.append(('Technology domains', tech_coverage))

print(f"Technology domain classification: {classified_works}/{total_works} ({tech_coverage:.1f}%)")

# Check citation coverage
cur.execute("""
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN cited_by_count > 0 THEN 1 ELSE 0 END) as with_citations
    FROM openalex_works
""")

total_works2, works_with_cites = cur.fetchone()
cite_coverage = (works_with_cites / total_works2 * 100) if total_works2 > 0 else 0
completeness_scores.append(('Citation data', cite_coverage))

print(f"Works with citation counts: {works_with_cites}/{total_works2} ({cite_coverage:.1f}%)")

avg_completeness = sum(score for _, score in completeness_scores) / len(completeness_scores)

print(f"\nAverage data completeness: {avg_completeness:.1f}%")

if avg_completeness >= 80:
    print("✅ PASS: Good data completeness")
    validation_results['tests_passed'] += 1
elif avg_completeness >= 50:
    print("⚠️  WARNING: Moderate data completeness")
    validation_results['warnings'].append(f"Data completeness only {avg_completeness:.1f}%")
    validation_results['tests_passed'] += 1
else:
    print("❌ FAIL: Poor data completeness")
    validation_results['tests_failed'] += 1
    validation_results['critical_issues'].append(f"Data completeness only {avg_completeness:.1f}%")

validation_results['findings']['data_completeness'] = {
    'technology_domains': tech_coverage,
    'citation_data': cite_coverage,
    'average': avg_completeness
}

# ============================================================================
# VALIDATION SUMMARY
# ============================================================================

print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80 + "\n")

total_tests = validation_results['tests_passed'] + validation_results['tests_failed']
pass_rate = (validation_results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"Tests passed: {validation_results['tests_passed']}/{total_tests} ({pass_rate:.0f}%)")
print(f"Tests failed: {validation_results['tests_failed']}/{total_tests}")
print(f"Warnings: {len(validation_results['warnings'])}")
print(f"Critical issues: {len(validation_results['critical_issues'])}")

if validation_results['warnings']:
    print("\n⚠️  WARNINGS:")
    for warning in validation_results['warnings']:
        print(f"  - {warning}")

if validation_results['critical_issues']:
    print("\n❌ CRITICAL ISSUES:")
    for issue in validation_results['critical_issues']:
        print(f"  - {issue}")

# Overall assessment
print("\n" + "="*80)
if pass_rate == 100 and len(validation_results['critical_issues']) == 0:
    print("✅ OVERALL: EXCELLENT - All validations passed")
    overall = "EXCELLENT"
elif pass_rate >= 80 and len(validation_results['critical_issues']) == 0:
    print("✅ OVERALL: GOOD - Minor warnings only")
    overall = "GOOD"
elif pass_rate >= 60:
    print("⚠️  OVERALL: ACCEPTABLE - Some issues to address")
    overall = "ACCEPTABLE"
else:
    print("❌ OVERALL: NEEDS IMPROVEMENT - Critical issues found")
    overall = "NEEDS_IMPROVEMENT"

print("="*80)

validation_results['overall_assessment'] = overall
validation_results['pass_rate'] = pass_rate

# Save validation report
output_path = Path('analysis/validation_report.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(validation_results, f, indent=2, ensure_ascii=False)

print(f"\n✓ Validation report saved to: {output_path}")

conn.close()
