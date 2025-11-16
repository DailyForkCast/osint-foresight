#!/usr/bin/env python3
"""
Deep Investigation: Missing European Countries
Why are ROU, SVN, BIH, MNE, KOS missing from China bilateral events?
"""
import sqlite3

conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_master.db')
cursor = conn.cursor()

MISSING = {
    'ROU': 'Romania',
    'SVN': 'Slovenia',
    'BIH': 'Bosnia and Herzegovina',
    'MNE': 'Montenegro',
    'KOS': 'Kosovo'
}

print("\n" + "=" * 100)
print("DEEP DIVE INVESTIGATION: MISSING EUROPEAN COUNTRIES")
print("=" * 100)
print("\nInvestigating: Romania (ROU), Slovenia (SVN), Bosnia (BIH), Montenegro (MNE), Kosovo (KOS)")
print("=" * 100)

for code, name in MISSING.items():
    print(f"\n{'='*100}")
    print(f"INVESTIGATING: {name} ({code})")
    print("=" * 100)

    # Test 1: Check if country appears ANYWHERE in database
    print(f"\n1. DOES {code} EXIST IN DATABASE AT ALL?")
    print("-" * 100)

    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE actor1_country_code = ? OR actor2_country_code = ?
    ''', (code, code))
    total_count = cursor.fetchone()[0]
    print(f"   Total events with {code} (any context): {total_count:,}")

    if total_count == 0:
        print(f"   [NO] {code} does NOT appear in database at all!")
        print(f"   -> Possible reasons:")
        print(f"      1. Collection never included this country code")
        print(f"      2. GDELT uses different code for this country")
        print(f"      3. Very low media coverage for this country")
        continue
    else:
        print(f"   [YES] {code} EXISTS in database!")

    # Test 2: Check Actor1 vs Actor2 distribution
    print(f"\n2. ACTOR DISTRIBUTION")
    print("-" * 100)

    cursor.execute('SELECT COUNT(*) FROM gdelt_events WHERE actor1_country_code = ?', (code,))
    actor1_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM gdelt_events WHERE actor2_country_code = ?', (code,))
    actor2_count = cursor.fetchone()[0]

    print(f"   {code} as Actor1: {actor1_count:,} events")
    print(f"   {code} as Actor2: {actor2_count:,} events")

    # Test 3: Check specifically with China
    print(f"\n3. EVENTS WITH CHINA")
    print("-" * 100)

    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE (actor1_country_code = ? AND actor2_country_code = 'CHN')
           OR (actor1_country_code = 'CHN' AND actor2_country_code = ?)
    ''', (code, code))
    china_bilateral = cursor.fetchone()[0]

    print(f"   {code}-China bilateral: {china_bilateral:,} events")

    if china_bilateral == 0:
        print(f"   [NO] NO bilateral events with China!")
        print(f"   -> But country exists in database with {total_count:,} total events")
        print(f"   -> Possible reasons:")
        print(f"      1. China not involved in {name} media coverage")
        print(f"      2. Events exist but outside our date range (2020-2025)")
        print(f"      3. China events involve other actors")
    else:
        print(f"   [YES] Has {china_bilateral:,} bilateral events with China!")
        print(f"   -> This SHOULD have appeared in our breakdown!")
        print(f"   -> INVESTIGATION NEEDED: Why didn't our query catch this?")

    # Test 4: Check date range
    print(f"\n4. DATE RANGE CHECK")
    print("-" * 100)

    cursor.execute('''
        SELECT MIN(sqldate), MAX(sqldate), COUNT(*)
        FROM gdelt_events
        WHERE (actor1_country_code = ? OR actor2_country_code = ?)
    ''', (code, code))
    min_date, max_date, count = cursor.fetchone()

    print(f"   First event: {min_date}")
    print(f"   Last event: {max_date}")
    print(f"   Total events: {count:,}")

    # Check if any in our target range (2020-2025)
    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE (actor1_country_code = ? OR actor2_country_code = ?)
          AND sqldate >= 20200101
          AND sqldate <= 20251231
    ''', (code, code))
    in_range = cursor.fetchone()[0]

    print(f"   Events in 2020-2025 range: {in_range:,}")

    if in_range == 0:
        print(f"   [NO] NO events in our target date range!")
        print(f"   -> All events are outside 2020-2025")

    # Test 5: Sample events
    if total_count > 0:
        print(f"\n5. SAMPLE EVENTS")
        print("-" * 100)

        cursor.execute('''
            SELECT sqldate, actor1_country_code, actor1_name, actor2_country_code, actor2_name, event_code
            FROM gdelt_events
            WHERE actor1_country_code = ? OR actor2_country_code = ?
            ORDER BY sqldate DESC
            LIMIT 5
        ''', (code, code))

        samples = cursor.fetchall()
        if samples:
            for date, a1code, a1name, a2code, a2name, evcode in samples:
                print(f"   {date}: {a1code}/{a1name[:30]} <-> {a2code}/{a2name[:30]} (Event: {evcode})")
        else:
            print(f"   No sample events available")

    # Test 6: Check with China specifically in date range
    if china_bilateral == 0:
        print(f"\n6. DETAILED CHINA SEARCH (ALL TIME)")
        print("-" * 100)

        cursor.execute('''
            SELECT COUNT(*), MIN(sqldate), MAX(sqldate)
            FROM gdelt_events
            WHERE (actor1_country_code = ? AND actor2_country_code = 'CHN')
        ''', (code,))
        a1_count, a1_min, a1_max = cursor.fetchone()

        cursor.execute('''
            SELECT COUNT(*), MIN(sqldate), MAX(sqldate)
            FROM gdelt_events
            WHERE (actor1_country_code = 'CHN' AND actor2_country_code = ?)
        ''', (code,))
        a2_count, a2_min, a2_max = cursor.fetchone()

        print(f"   {code} as Actor1, China as Actor2: {a1_count:,} events ({a1_min} to {a1_max})")
        print(f"   China as Actor1, {code} as Actor2: {a2_count:,} events ({a2_min} to {a2_max})")

# Summary
print("\n" + "=" * 100)
print("INVESTIGATION SUMMARY")
print("=" * 100)

for code, name in MISSING.items():
    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE actor1_country_code = ? OR actor2_country_code = ?
    ''', (code, code))
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE ((actor1_country_code = ? AND actor2_country_code = 'CHN')
           OR (actor1_country_code = 'CHN' AND actor2_country_code = ?))
    ''', (code, code))
    china = cursor.fetchone()[0]

    cursor.execute('''
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE (actor1_country_code = ? OR actor2_country_code = ?)
          AND sqldate >= 20200101
    ''', (code, code))
    recent = cursor.fetchone()[0]

    status = "MISSING" if china == 0 else "FOUND"
    print(f"\n{name:30} ({code})")
    print(f"  Total events (all time): {total:,}")
    print(f"  Events since 2020: {recent:,}")
    print(f"  China bilateral: {china:,}")
    print(f"  Status: {status}")

print("\n" + "=" * 100)
