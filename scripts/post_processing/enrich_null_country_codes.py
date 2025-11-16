#!/usr/bin/env python3
"""
GDELT NULL Country Code Enrichment
Post-processing to reduce 27% NULL rate for Actor country codes

Enrichment strategies:
1. City/Province lookup (e.g., "VILNIUS" → LTU, "BEIJING" → CHN)
2. Organization lookup (e.g., "CHINESE GOVERNMENT" → CHN)
3. Name pattern matching (e.g., "LITHUANIAN" → LTU)
"""

import sqlite3
import json
from pathlib import Path

class CountryCodeEnricher:
    """Enrich NULL country codes using city/province/organization lookups"""

    def __init__(self, master_db="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.master_db = master_db
        self.conn = None

        # City/Province → Country mappings
        self.location_map = {
            # China
            "BEIJING": "CHN",
            "SHANGHAI": "CHN",
            "GUANGZHOU": "CHN",
            "SHENZHEN": "CHN",
            "HONG KONG": "CHN",
            "TIBET": "CHN",
            "XINJIANG": "CHN",

            # Lithuania
            "VILNIUS": "LTU",
            "KAUNAS": "LTU",
            "KLAIPEDA": "LTU",
            "LITHUANIAN": "LTU",

            # Taiwan
            "TAIPEI": "TWN",
            "KAOHSIUNG": "TWN",
            "TAIWANESE": "TWN",

            # Major cities for other countries
            "MOSCOW": "RUS",
            "WASHINGTON": "USA",
            "LONDON": "GBR",
            "PARIS": "FRA",
            "BERLIN": "DEU",
            "ROME": "ITA",
            "MADRID": "ESP",
            "BRUSSELS": "BEL",
            "WARSAW": "POL",
            "TOKYO": "JPN",
            "SEOUL": "KOR",
            "NEW DELHI": "IND",
            "CANBERRA": "AUS"
        }

        # Organization patterns → Country
        self.org_patterns = {
            "CHINESE": "CHN",
            "CHINA": "CHN",
            "LITHUANIAN": "LTU",
            "LITHUANIA": "LTU",
            "TAIWAN": "TWN",
            "TAIWANESE": "TWN",
            "AMERICAN": "USA",
            "US ": "USA",
            "RUSSIAN": "RUS",
            "BRITISH": "GBR",
            "FRENCH": "FRA",
            "GERMAN": "DEU",
            "ITALIAN": "ITA",
            "SPANISH": "ESP",
            "POLISH": "POL",
            "JAPANESE": "JPN",
            "KOREAN": "KOR",
            "INDIAN": "IND",
            "AUSTRALIAN": "AUS"
        }

        self.stats = {
            "total_null_actor1": 0,
            "total_null_actor2": 0,
            "enriched_actor1": 0,
            "enriched_actor2": 0,
            "methods": {}
        }

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.master_db)

    def lookup_country_from_name(self, name: str) -> tuple:
        """
        Lookup country code from actor name

        Returns:
            (country_code, method) or (None, None)
        """
        if not name:
            return (None, None)

        name_upper = name.upper()

        # Try exact location match
        if name_upper in self.location_map:
            return (self.location_map[name_upper], "location_exact")

        # Try pattern matching
        for pattern, country in self.org_patterns.items():
            if pattern in name_upper:
                return (country, "pattern_match")

        return (None, None)

    def enrich_actor_country_codes(self, date_range_start=None, date_range_end=None):
        """
        Enrich NULL country codes for actors

        Args:
            date_range_start: YYYYMMDD (optional, for specific date range)
            date_range_end: YYYYMMDD (optional)
        """
        print("=" * 80)
        print("GDELT NULL Country Code Enrichment")
        print("=" * 80)

        # Build date filter
        date_filter = ""
        if date_range_start and date_range_end:
            date_filter = f"AND sqldate BETWEEN {date_range_start} AND {date_range_end}"
            print(f"\nDate range: {date_range_start} to {date_range_end}")

        # Count NULLs
        cur = self.conn.cursor()
        cur.execute(f"""
            SELECT
                SUM(CASE WHEN actor1_country_code IS NULL AND actor1_name IS NOT NULL THEN 1 ELSE 0 END) as null_actor1,
                SUM(CASE WHEN actor2_country_code IS NULL AND actor2_name IS NOT NULL THEN 1 ELSE 0 END) as null_actor2,
                COUNT(*) as total
            FROM gdelt_events
            WHERE 1=1 {date_filter}
        """)
        row = cur.fetchone()
        self.stats["total_null_actor1"] = row[0]
        self.stats["total_null_actor2"] = row[1]
        total_events = row[2]

        print(f"\nNULL Counts:")
        print(f"  Actor1: {self.stats['total_null_actor1']:,} / {total_events:,} ({(self.stats['total_null_actor1']/total_events*100):.1f}%)")
        print(f"  Actor2: {self.stats['total_null_actor2']:,} / {total_events:,} ({(self.stats['total_null_actor2']/total_events*100):.1f}%)")

        # Enrich Actor1
        print(f"\nEnriching Actor1 country codes...")
        cur.execute(f"""
            SELECT id, actor1_name
            FROM gdelt_events
            WHERE actor1_country_code IS NULL
              AND actor1_name IS NOT NULL
            {date_filter}
        """)

        actor1_updates = []
        for row in cur.fetchall():
            event_id, name = row
            country, method = self.lookup_country_from_name(name)
            if country:
                actor1_updates.append((country, event_id))
                self.stats["enriched_actor1"] += 1
                self.stats["methods"][method] = self.stats["methods"].get(method, 0) + 1

        if actor1_updates:
            print(f"  Updating {len(actor1_updates):,} Actor1 records...")
            self.conn.executemany(
                "UPDATE gdelt_events SET actor1_country_code = ? WHERE id = ?",
                actor1_updates
            )
            self.conn.commit()

        # Enrich Actor2
        print(f"\nEnriching Actor2 country codes...")
        cur.execute(f"""
            SELECT id, actor2_name
            FROM gdelt_events
            WHERE actor2_country_code IS NULL
              AND actor2_name IS NOT NULL
            {date_filter}
        """)

        actor2_updates = []
        for row in cur.fetchall():
            event_id, name = row
            country, method = self.lookup_country_from_name(name)
            if country:
                actor2_updates.append((country, event_id))
                self.stats["enriched_actor2"] += 1
                self.stats["methods"][method] = self.stats["methods"].get(method, 0) + 1

        if actor2_updates:
            print(f"  Updating {len(actor2_updates):,} Actor2 records...")
            self.conn.executemany(
                "UPDATE gdelt_events SET actor2_country_code = ? WHERE id = ?",
                actor2_updates
            )
            self.conn.commit()

        # Final counts (same filter as initial - only count those with names)
        cur.execute(f"""
            SELECT
                SUM(CASE WHEN actor1_country_code IS NULL AND actor1_name IS NOT NULL THEN 1 ELSE 0 END) as null_actor1,
                SUM(CASE WHEN actor2_country_code IS NULL AND actor2_name IS NOT NULL THEN 1 ELSE 0 END) as null_actor2
            FROM gdelt_events
            WHERE 1=1 {date_filter}
        """)
        row = cur.fetchone()
        final_null_actor1 = row[0]
        final_null_actor2 = row[1]

        print("\n" + "=" * 80)
        print("ENRICHMENT RESULTS")
        print("=" * 80)
        print(f"\nActor1:")
        print(f"  Before: {self.stats['total_null_actor1']:,} NULL ({(self.stats['total_null_actor1']/total_events*100):.1f}%)")
        print(f"  Enriched: {self.stats['enriched_actor1']:,}")
        print(f"  After: {final_null_actor1:,} NULL ({(final_null_actor1/total_events*100):.1f}%)")
        print(f"  Improvement: {((self.stats['total_null_actor1']-final_null_actor1)/self.stats['total_null_actor1']*100):.1f}% reduction" if self.stats['total_null_actor1'] > 0 else "")

        print(f"\nActor2:")
        print(f"  Before: {self.stats['total_null_actor2']:,} NULL ({(self.stats['total_null_actor2']/total_events*100):.1f}%)")
        print(f"  Enriched: {self.stats['enriched_actor2']:,}")
        print(f"  After: {final_null_actor2:,} NULL ({(final_null_actor2/total_events*100):.1f}%)")
        print(f"  Improvement: {((self.stats['total_null_actor2']-final_null_actor2)/self.stats['total_null_actor2']*100):.1f}% reduction" if self.stats['total_null_actor2'] > 0 else "")

        print(f"\nEnrichment Methods Used:")
        for method, count in sorted(self.stats["methods"].items(), key=lambda x: x[1], reverse=True):
            print(f"  {method}: {count:,}")

        print("=" * 80)

        # Save report
        report = {
            "timestamp": "2025-11-02",
            "date_range": {
                "start": date_range_start,
                "end": date_range_end
            },
            "total_events": total_events,
            "actor1": {
                "before_null": self.stats['total_null_actor1'],
                "enriched": self.stats['enriched_actor1'],
                "after_null": final_null_actor1,
                "improvement_pct": ((self.stats['total_null_actor1']-final_null_actor1)/self.stats['total_null_actor1']*100) if self.stats['total_null_actor1'] > 0 else 0
            },
            "actor2": {
                "before_null": self.stats['total_null_actor2'],
                "enriched": self.stats['enriched_actor2'],
                "after_null": final_null_actor2,
                "improvement_pct": ((self.stats['total_null_actor2']-final_null_actor2)/self.stats['total_null_actor2']*100) if self.stats['total_null_actor2'] > 0 else 0
            },
            "methods": self.stats["methods"]
        }

        report_path = Path("analysis/null_enrichment_report_20251102.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_path}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enrich NULL country codes in GDELT data")
    parser.add_argument("--start-date", help="Start date YYYYMMDD (optional)")
    parser.add_argument("--end-date", help="End date YYYYMMDD (optional)")

    args = parser.parse_args()

    enricher = CountryCodeEnricher()
    enricher.connect()

    try:
        enricher.enrich_actor_country_codes(args.start_date, args.end_date)
    finally:
        enricher.close()
