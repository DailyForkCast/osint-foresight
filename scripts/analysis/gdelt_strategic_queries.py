#!/usr/bin/env python3
"""
GDELT Strategic Intelligence Queries
Deep-dive analysis for cross-referencing and pattern detection

ZERO FABRICATION PROTOCOL COMPLIANCE:
- Data Source: F:/OSINT_WAREHOUSE/osint_master.db (gdelt_events table)
- Analysis Method: Direct SQL queries on collected GDELT data
- Output: Measurements only (sentiment scores, event counts)
- Limitations: Cannot determine causation, intent, or coordination from sentiment
- Cognitive Bias Awareness: Confirmation bias (seeing patterns we expect)

INTELLIGENCE COMMUNITY STANDARDS:
- ODNI ICD 203: Based on all available sources (GDELT events database)
- Sherman Kent: Distinguishes measurements (sentiment) from interpretations (campaigns)
- Heuer: Monitors confirmation bias, pattern-seeking

WHAT THIS SCRIPT DOES:
- Measures sentiment divergence between Chinese and Western media
- Counts cooperation events by country
- Identifies negative sentiment events
- Tracks Xi Jinping interactions

WHAT THIS SCRIPT DOES NOT DO:
- Does NOT claim "coordinated campaigns" (requires documentary evidence)
- Does NOT attribute intent (requires policy documents)
- Does NOT infer operations (requires operational intelligence)
- Reports divergence as "OBSERVED" with "CAUSE UNKNOWN"
"""

import sqlite3

db = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = db.cursor()

print('='*80)
print('STRATEGIC INTELLIGENCE ANALYSIS - DEEP DIVE QUERIES')
print('='*80)
print()

# Query 7: European Technology Cooperation Events
print('QUERY 7: EUROPEAN COUNTRIES WITH POSITIVE COOPERATION SENTIMENT')
print('(Potential Technology Transfer Risk)')
print('-'*80)
cursor.execute('''
SELECT
    CASE
        WHEN actor1_country_code = 'CHN' THEN actor2_country_code
        ELSE actor1_country_code
    END as european_country,
    COUNT(*) as cooperation_events,
    ROUND(AVG(CAST(avg_tone AS REAL)), 2) as avg_sentiment
FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    (actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL') AND actor2_country_code = 'CHN')
    OR
    (actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','HUN','CZE','POL') AND actor1_country_code = 'CHN')
  )
  AND event_code IN ('036', '040', '043', '046', '050')
  AND CAST(avg_tone AS REAL) > 0
GROUP BY european_country
ORDER BY avg_sentiment DESC
LIMIT 8
''')

results = cursor.fetchall()
if results:
    print(f"{'Country':<10} {'Events':<8} {'Sentiment':<12}")
    print('-'*35)
    for row in results:
        country, events, sentiment = row
        print(f'{country:<10} {events:<8} {sentiment:+.2f}')

print()
print()

# Query 8: Negative Events
print('QUERY 8: MOST NEGATIVE CHINA-EUROPE EVENTS (Diplomatic Tensions)')
print('-'*80)
cursor.execute('''
SELECT
    event_date,
    actor1_name,
    actor2_name,
    ROUND(CAST(avg_tone AS REAL), 2) as tone,
    source_url
FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR','POL','NLD','BEL','SWE','LTU')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR','POL','NLD','BEL','SWE','LTU')
  )
  AND CAST(avg_tone AS REAL) < -5
ORDER BY CAST(avg_tone AS REAL) ASC
LIMIT 10
''')

results = cursor.fetchall()
if results:
    print(f"{'Date':<12} {'Actor1':<20} {'Actor2':<20} {'Tone':<8}")
    print('-'*65)
    for row in results:
        date, a1, a2, tone, url = row
        a1_short = (a1 or 'N/A')[:19]
        a2_short = (a2 or 'N/A')[:19]
        print(f'{str(date):<12} {a1_short:<20} {a2_short:<20} {tone:<8.2f}')

print()
print()

# Query 9: Xi Jinping Activity
print('QUERY 9: XI JINPING ACTIVITY (Who is he engaging with?)')
print('-'*80)
cursor.execute('''
SELECT
    actor2_name,
    actor2_country_code,
    COUNT(*) as interactions,
    ROUND(AVG(CAST(avg_tone AS REAL)), 2) as avg_sentiment
FROM gdelt_events
WHERE actor1_name = 'XI JINPING'
  AND actor2_name IS NOT NULL
  AND avg_tone IS NOT NULL
GROUP BY actor2_name, actor2_country_code
ORDER BY interactions DESC
LIMIT 12
''')

results = cursor.fetchall()
if results:
    print(f"{'Counterpart':<30} {'Country':<8} {'Interactions':<15} {'Sentiment':<12}")
    print('-'*70)
    for row in results:
        name, country, interactions, sentiment = row
        sentiment_str = f'{sentiment:+.2f}' if sentiment else 'N/A'
        print(f'{name[:29]:<30} {country or "N/A":<8} {interactions:<15} {sentiment_str:<12}')

print()
print()

# Query 10: Media Sentiment Comparison
print('QUERY 10: CHINESE vs WESTERN MEDIA SENTIMENT COMPARISON')
print('-'*80)

# Chinese state media
cursor.execute('''
SELECT
    COUNT(*) as events,
    ROUND(AVG(CAST(avg_tone AS REAL)), 2) as avg_sentiment
FROM gdelt_events
WHERE source_url LIKE '%xinhua%'
   OR source_url LIKE '%cgtn%'
   OR source_url LIKE '%chinadaily%'
   OR source_url LIKE '%globaltimes%'
''')
chinese_media = cursor.fetchone()

# Western media
cursor.execute('''
SELECT
    COUNT(*) as events,
    ROUND(AVG(CAST(avg_tone AS REAL)), 2) as avg_sentiment
FROM gdelt_events
WHERE source_url LIKE '%reuters%'
   OR source_url LIKE '%bbc%'
   OR source_url LIKE '%nytimes%'
   OR source_url LIKE '%wsj%'
   OR source_url LIKE '%ft.com%'
   OR source_url LIKE '%guardian%'
''')
western_media = cursor.fetchone()

print(f"{'Source Type':<25} {'Events':<10} {'Avg Sentiment':<15}")
print('-'*55)

if chinese_media and chinese_media[0] > 0:
    print(f"{'Chinese State Media':<25} {chinese_media[0]:<10} {chinese_media[1]:+.2f}")
if western_media and western_media[0] > 0:
    print(f"{'Western Media':<25} {western_media[0]:<10} {western_media[1]:+.2f}")

if chinese_media and western_media and chinese_media[0] > 0 and western_media[0] > 0:
    divergence = abs(chinese_media[1] - western_media[1])
    print()
    print(f'SENTIMENT DIVERGENCE OBSERVED: {divergence:.2f} points')
    print(f'Chinese media: {chinese_media[1]:+.2f} | Western media: {western_media[1]:+.2f}')
    if divergence > 3:
        print('[OBSERVATION] Divergence exceeds 3.0 points threshold')
        print('[CAUSE] Unknown - could be editorial perspectives, audience, or other factors')

print()
print()

# Query 11: High-Impact Events for Cross-Referencing
print('QUERY 11: HIGH-IMPACT COOPERATION EVENTS FOR CROSS-REFERENCING')
print('(Investigate with OpenAlex, TED, USPTO)')
print('-'*80)
cursor.execute('''
SELECT
    event_date,
    actor1_name,
    actor2_name,
    ROUND(CAST(avg_tone AS REAL), 2) as tone,
    num_sources,
    source_url
FROM gdelt_events
WHERE (actor1_country_code = 'CHN' OR actor2_country_code = 'CHN')
  AND (
    actor1_country_code IN ('FRA','DEU','ITA','ESP','GBR')
    OR actor2_country_code IN ('FRA','DEU','ITA','ESP','GBR')
  )
  AND event_code IN ('036', '040', '043', '046', '050')
  AND CAST(num_sources AS INTEGER) >= 3
ORDER BY CAST(num_sources AS INTEGER) DESC
LIMIT 5
''')

results = cursor.fetchall()
if results:
    print(f"{'Date':<12} {'Actor1':<18} {'Actor2':<18} {'Tone':<7} {'Sources':<8}")
    print('-'*70)
    for row in results:
        date, a1, a2, tone, sources, url = row
        a1_short = (a1 or 'N/A')[:17]
        a2_short = (a2 or 'N/A')[:17]
        print(f'{str(date):<12} {a1_short:<18} {a2_short:<18} {tone:<7.2f} {sources:<8}')

    print()
    print('ACTION: Cross-reference these events with:')
    print('  - OpenAlex: Research collaborations around these dates')
    print('  - TED: Contract awards to Chinese firms')
    print('  - USPTO: Patent citations from collaborations')

db.close()

print()
print('='*80)
print('Strategic intelligence queries complete')
print('='*80)
