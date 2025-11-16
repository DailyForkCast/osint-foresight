"""
Analyze NULL Data to Strategically Expand Keywords and Topics

This script analyzes the NULL data captured during V5 concurrent processing to:
1. Identify topic patterns that passed but missed keyword matching
2. Identify keyword patterns that passed but failed topic validation
3. Extract patterns from strategic institution works that failed both
4. Generate recommendations for keyword/topic expansion
"""

import sqlite3
import json
from pathlib import Path
from collections import Counter, defaultdict
import re

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")
OUTPUT_DIR = Path("C:/Projects/OSINT - Foresight/analysis")

def analyze_keyword_gaps():
    """
    Analyze works that FAILED keyword matching but PASSED topic validation
    These reveal gaps in our keyword coverage
    """

    print("\n" + "="*80)
    print("ANALYZING KEYWORD GAPS (Topic Pass + Keyword Fail)")
    print("="*80)

    conn = sqlite3.connect(str(DB_PATH))

    # Check if NULL tables exist
    tables = conn.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name LIKE '%null%'
    """).fetchall()

    if not tables:
        print("[WARN] No NULL data tables found. V5 concurrent processing may not have created them.")
        conn.close()
        return {}

    print(f"\n[OK] Found NULL data tables: {[t[0] for t in tables]}")

    # Query keyword fails with topic passes
    try:
        results = conn.execute("""
            SELECT technology_domain, matched_topic, COUNT(*) as count
            FROM openalex_null_keyword_fails
            GROUP BY technology_domain, matched_topic
            ORDER BY technology_domain, count DESC
        """).fetchall()

        if not results:
            print("[WARN] No data in openalex_null_keyword_fails table")
            conn.close()
            return {}

        # Organize by technology
        gaps_by_tech = defaultdict(list)

        for tech, topic, count in results:
            gaps_by_tech[tech].append({
                'topic': topic,
                'count': count
            })

        # Print analysis
        print(f"\n[OK] Found {len(results)} topic patterns that passed but missed keywords")
        print(f"\nTop Keyword Gaps by Technology:")
        print("-" * 80)

        for tech in sorted(gaps_by_tech.keys()):
            print(f"\n{tech}:")
            top_gaps = gaps_by_tech[tech][:10]  # Top 10 per tech
            for gap in top_gaps:
                print(f"  • {gap['topic']}: {gap['count']} missed works")

        conn.close()
        return gaps_by_tech

    except Exception as e:
        print(f"[ERROR] Failed to query keyword gaps: {e}")
        conn.close()
        return {}

def analyze_topic_gaps():
    """
    Analyze works that PASSED keyword matching but FAILED topic validation
    These reveal potential false positives or missing topic patterns
    """

    print("\n" + "="*80)
    print("ANALYZING TOPIC GAPS (Keyword Pass + Topic Fail)")
    print("="*80)

    conn = sqlite3.connect(str(DB_PATH))

    try:
        results = conn.execute("""
            SELECT technology_domain, matched_keyword, actual_topics, COUNT(*) as count
            FROM openalex_null_topic_fails
            GROUP BY technology_domain, matched_keyword
            ORDER BY technology_domain, count DESC
        """).fetchall()

        if not results:
            print("[WARN] No data in openalex_null_topic_fails table")
            conn.close()
            return {}

        # Organize by technology
        gaps_by_tech = defaultdict(list)

        for tech, keyword, topics, count in results:
            gaps_by_tech[tech].append({
                'keyword': keyword,
                'topics': topics,
                'count': count
            })

        # Print analysis
        print(f"\n[OK] Found {len(results)} keyword patterns that passed but failed topics")
        print(f"\nTop Topic Gaps by Technology:")
        print("-" * 80)

        for tech in sorted(gaps_by_tech.keys()):
            print(f"\n{tech}:")
            top_gaps = gaps_by_tech[tech][:10]  # Top 10 per tech
            for gap in top_gaps:
                topics_preview = gap['topics'][:100] if gap['topics'] else 'None'
                print(f"  • Keyword '{gap['keyword']}' matched {gap['count']} works")
                print(f"    Actual topics: {topics_preview}...")

        conn.close()
        return gaps_by_tech

    except Exception as e:
        print(f"[ERROR] Failed to query topic gaps: {e}")
        conn.close()
        return {}

def analyze_strategic_institution_misses():
    """
    Analyze works from strategic institutions that failed BOTH validations
    These are completely missed strategic works
    """

    print("\n" + "="*80)
    print("ANALYZING STRATEGIC INSTITUTION MISSES (Both Failed)")
    print("="*80)

    conn = sqlite3.connect(str(DB_PATH))

    try:
        results = conn.execute("""
            SELECT institution_name, institution_country, all_topics, COUNT(*) as count
            FROM openalex_null_strategic_institution
            GROUP BY institution_name, institution_country
            ORDER BY count DESC
            LIMIT 50
        """).fetchall()

        if not results:
            print("[WARN] No data in openalex_null_strategic_institution table")
            conn.close()
            return {}

        print(f"\n[OK] Found {len(results)} strategic institutions with missed works")
        print(f"\nTop Strategic Institutions with Missed Works:")
        print("-" * 80)

        misses = []

        for inst, country, topics, count in results:
            misses.append({
                'institution': inst,
                'country': country,
                'topics': topics,
                'count': count
            })

            topics_preview = topics[:100] if topics else 'None'
            print(f"  • {inst} ({country}): {count} missed works")
            print(f"    Sample topics: {topics_preview}...")

        conn.close()
        return misses

    except Exception as e:
        print(f"[ERROR] Failed to query strategic institution misses: {e}")
        conn.close()
        return {}

def extract_keyword_recommendations(keyword_gaps):
    """
    Extract new keyword recommendations from topic patterns
    """

    print("\n" + "="*80)
    print("EXTRACTING KEYWORD RECOMMENDATIONS")
    print("="*80)

    recommendations = defaultdict(set)

    for tech, gaps in keyword_gaps.items():
        # Extract key terms from topic names
        for gap in gaps[:20]:  # Top 20 per tech
            topic = gap['topic'].lower()

            # Extract significant terms (3+ chars, not common words)
            words = re.findall(r'\b\w{3,}\b', topic)

            common_words = {
                'the', 'and', 'for', 'with', 'from', 'using', 'based',
                'study', 'research', 'analysis', 'application', 'method'
            }

            for word in words:
                if word not in common_words:
                    recommendations[tech].add(word)

    print("\nRecommended New Keywords by Technology:")
    print("-" * 80)

    for tech in sorted(recommendations.keys()):
        keywords = sorted(recommendations[tech])[:15]  # Top 15 per tech
        print(f"\n{tech}:")
        print(f"  {', '.join(keywords)}")

    return recommendations

def generate_expansion_report(keyword_gaps, topic_gaps, strategic_misses, keyword_recommendations):
    """
    Generate comprehensive expansion report
    """

    report = {
        'analysis_date': '2025-10-13',
        'source': 'V5 Concurrent NULL Data Analysis',
        'summary': {
            'total_keyword_gaps': sum(len(gaps) for gaps in keyword_gaps.values()),
            'total_topic_gaps': sum(len(gaps) for gaps in topic_gaps.values()),
            'total_strategic_misses': len(strategic_misses),
            'technologies_analyzed': list(keyword_gaps.keys())
        },
        'keyword_gaps_by_tech': {
            tech: [
                {'topic': gap['topic'], 'count': gap['count']}
                for gap in gaps[:20]
            ]
            for tech, gaps in keyword_gaps.items()
        },
        'keyword_recommendations_by_tech': {
            tech: sorted(keywords)[:15]
            for tech, keywords in keyword_recommendations.items()
        },
        'strategic_institution_misses': strategic_misses[:30],
        'recommendations': {
            'immediate_actions': [
                'Add recommended keywords to Stage 1 patterns',
                'Add missing topic patterns to Stage 2 validation',
                'Review strategic institution works for domain relevance',
                'Rerun V4 with expanded patterns'
            ],
            'expected_improvement': '2-3x increase in works collected while maintaining precision'
        }
    }

    # Save report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "NULL_DATA_EXPANSION_ANALYSIS.json"

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n[OK] Expansion report saved to: {report_path}")

    return report

def main():
    """Main analysis pipeline"""

    print("="*80)
    print("NULL DATA ANALYSIS FOR STRATEGIC KEYWORD/TOPIC EXPANSION")
    print("="*80)

    # Step 1: Analyze keyword gaps
    keyword_gaps = analyze_keyword_gaps()

    # Step 2: Analyze topic gaps
    topic_gaps = analyze_topic_gaps()

    # Step 3: Analyze strategic institution misses
    strategic_misses = analyze_strategic_institution_misses()

    # Step 4: Extract keyword recommendations
    keyword_recommendations = extract_keyword_recommendations(keyword_gaps)

    # Step 5: Generate expansion report
    report = generate_expansion_report(
        keyword_gaps,
        topic_gaps,
        strategic_misses,
        keyword_recommendations
    )

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nSummary:")
    print(f"  Keyword gaps identified: {report['summary']['total_keyword_gaps']}")
    print(f"  Topic gaps identified: {report['summary']['total_topic_gaps']}")
    print(f"  Strategic misses: {report['summary']['total_strategic_misses']}")
    print(f"\nNext steps:")
    print(f"  1. Review expansion report: {OUTPUT_DIR / 'NULL_DATA_EXPANSION_ANALYSIS.json'}")
    print(f"  2. Apply keyword recommendations to config files")
    print(f"  3. Rerun V4 with expanded patterns")
    print()

if __name__ == '__main__':
    main()
