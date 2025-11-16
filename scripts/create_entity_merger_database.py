#!/usr/bin/env python3
"""
create_entity_merger_database.py - Entity Merger Tracking Database

Creates and populates a database table tracking PRC SOE mergers and other
major corporate consolidations affecting US government contracting entities.

Purpose:
- Track legacy entity names to current parent companies
- Understand merger timelines and corporate lineage
- Support entity lookup during detection/analysis
- Enable historical contract attribution to current owners

Schema:
- entity_mergers: Main merger tracking table
- entity_aliases: Name variations for lookup
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class EntityMergerDatabase:
    """Create and manage entity merger tracking database"""

    def __init__(self, db_path="F:/OSINT_WAREHOUSE/osint_master.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"[OK] Connected to: {self.db_path}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")

    def create_schema(self):
        """Create entity merger tracking tables"""
        print("\n" + "="*80)
        print("CREATING ENTITY MERGER TRACKING SCHEMA")
        print("="*80)

        cursor = self.conn.cursor()

        # Main merger tracking table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entity_mergers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            legacy_entity_name TEXT NOT NULL,
            legacy_entity_type TEXT,
            merger_date DATE NOT NULL,
            merged_into TEXT NOT NULL,
            current_parent TEXT NOT NULL,
            parent_country TEXT,
            parent_ownership TEXT,
            parent_tier TEXT,
            merger_type TEXT,
            strategic_sector TEXT,
            pre_merger_rank INTEGER,
            post_merger_rank INTEGER,
            notes TEXT,
            source TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("[OK] Created table: entity_mergers")

        # Entity aliases for lookup
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entity_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_name TEXT NOT NULL,
            alias TEXT NOT NULL,
            alias_type TEXT,
            current_parent TEXT NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(alias)
        )
        """)
        print("[OK] Created table: entity_aliases")

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_legacy_entity ON entity_mergers(legacy_entity_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_current_parent ON entity_mergers(current_parent)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_merger_date ON entity_mergers(merger_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alias ON entity_aliases(alias)")
        print("[OK] Created indexes")

        self.conn.commit()

    def populate_cosco_merger(self):
        """Populate COSCO Shipping merger (2016)"""
        print("\n" + "="*80)
        print("POPULATING: COSCO SHIPPING MERGER (2016)")
        print("="*80)

        cursor = self.conn.cursor()

        # China Shipping Development (our contracts)
        cursor.execute("""
        INSERT OR REPLACE INTO entity_mergers (
            legacy_entity_name,
            legacy_entity_type,
            merger_date,
            merged_into,
            current_parent,
            parent_country,
            parent_ownership,
            parent_tier,
            merger_type,
            strategic_sector,
            pre_merger_rank,
            post_merger_rank,
            notes,
            source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'China Shipping Development Co., Ltd.',
            'Subsidiary',
            '2016-02-18',
            'China COSCO Shipping Corporation',
            'China COSCO Shipping Corporation',
            'China',
            'State-Owned Enterprise',
            'TIER_1',
            'State-directed consolidation',
            'Maritime logistics',
            7,  # China Shipping Group was #7 globally
            4,  # COSCO Shipping became #4 globally
            'Involved in DPRK HFO transport contracts (2008-2011) and Military Sealift Command charters. Part of China Shipping Group pre-merger.',
            'USAspending.gov records + open source research'
        ))

        # Dalian Ocean Shipping (also in our contracts)
        cursor.execute("""
        INSERT OR REPLACE INTO entity_mergers (
            legacy_entity_name,
            legacy_entity_type,
            merger_date,
            merged_into,
            current_parent,
            parent_country,
            parent_ownership,
            parent_tier,
            merger_type,
            strategic_sector,
            pre_merger_rank,
            post_merger_rank,
            notes,
            source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'Dalian Ocean Shipping Company',
            'Subsidiary',
            '2016-02-18',
            'China COSCO Shipping Corporation',
            'China COSCO Shipping Corporation',
            'China',
            'State-Owned Enterprise',
            'TIER_1',
            'State-directed consolidation',
            'Maritime logistics',
            6,  # COSCO Group was #6 globally
            4,  # COSCO Shipping became #4 globally
            'Involved in DPRK HFO transport contract (2008). Part of COSCO Group (China Ocean Shipping Company) pre-merger. Dalian Port operations.',
            'USAspending.gov records + open source research'
        ))

        # China Ocean Shipping (Group) Company (parent)
        cursor.execute("""
        INSERT OR REPLACE INTO entity_mergers (
            legacy_entity_name,
            legacy_entity_type,
            merger_date,
            merged_into,
            current_parent,
            parent_country,
            parent_ownership,
            parent_tier,
            merger_type,
            strategic_sector,
            pre_merger_rank,
            post_merger_rank,
            notes,
            source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'China Ocean Shipping (Group) Company',
            'Parent Company',
            '2016-02-18',
            'China COSCO Shipping Corporation',
            'China COSCO Shipping Corporation',
            'China',
            'State-Owned Enterprise',
            'TIER_1',
            'State-directed consolidation',
            'Maritime logistics',
            6,
            4,
            'Pre-merger name for COSCO Group. Merged with China Shipping Group to form COSCO Shipping Corporation.',
            'Open source research'
        ))

        # Aliases for lookup
        aliases = [
            ('China Shipping Development Co., Ltd.', 'CHINA SHIPPING DEVELOPMENT'),
            ('China Shipping Development Co., Ltd.', 'CHINA SHIPPING DEVELOPMENT CO.'),
            ('China Shipping Development Co., Ltd.', 'CHINA SHIPPING DEVELOPMENT CO., LTD.'),
            ('China Shipping Development Co., Ltd.', 'CSD'),
            ('Dalian Ocean Shipping Company', 'DALIAN OCEAN SHIPPING'),
            ('Dalian Ocean Shipping Company', 'DALIAN OCEAN SHIPPING COMPANY'),
            ('China Ocean Shipping (Group) Company', 'CHINA OCEAN SHIPPING'),
            ('China Ocean Shipping (Group) Company', 'CHINA OCEAN SHIPPING GROUP'),
            ('China Ocean Shipping (Group) Company', 'COSCO GROUP'),
            ('China Ocean Shipping (Group) Company', 'COSCO'),
        ]

        for entity, alias in aliases:
            cursor.execute("""
            INSERT OR IGNORE INTO entity_aliases (entity_name, alias, alias_type, current_parent)
            VALUES (?, ?, ?, ?)
            """, (entity, alias, 'Name variation', 'China COSCO Shipping Corporation'))

        print("[OK] Populated COSCO/China Shipping merger data")
        print(f"  - 3 legacy entities")
        print(f"  - 10 aliases")

        self.conn.commit()

    def populate_crrc_merger(self):
        """Populate CRRC Corporation merger (2015)"""
        print("\n" + "="*80)
        print("POPULATING: CRRC CORPORATION MERGER (2015)")
        print("="*80)

        cursor = self.conn.cursor()

        # China South Locomotive & Rolling Stock (our contracts)
        cursor.execute("""
        INSERT OR REPLACE INTO entity_mergers (
            legacy_entity_name,
            legacy_entity_type,
            merger_date,
            merged_into,
            current_parent,
            parent_country,
            parent_ownership,
            parent_tier,
            merger_type,
            strategic_sector,
            pre_merger_rank,
            post_merger_rank,
            notes,
            source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'China South Locomotive & Rolling Stock Industry (Group) Corp',
            'Parent Company',
            '2015-06-01',
            'CRRC Corporation Limited',
            'CRRC Corporation Limited',
            'China',
            'State-Owned Enterprise',
            'TIER_1',
            'Absorption merger (equal)',
            'Rail equipment manufacturing',
            2,  # CSR was major player
            1,  # CRRC became world's largest
            'Pre-merger parent company (CSR). Identified in USAspending contracts. Banned from US FTA contracts in 2020.',
            'USAspending.gov records + open source research'
        ))

        # China North Locomotive & Rolling Stock (CNR)
        cursor.execute("""
        INSERT OR REPLACE INTO entity_mergers (
            legacy_entity_name,
            legacy_entity_type,
            merger_date,
            merged_into,
            current_parent,
            parent_country,
            parent_ownership,
            parent_tier,
            merger_type,
            strategic_sector,
            pre_merger_rank,
            post_merger_rank,
            notes,
            source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'China CNR Corporation Ltd.',
            'Parent Company',
            '2015-06-01',
            'CRRC Corporation Limited',
            'CRRC Corporation Limited',
            'China',
            'State-Owned Enterprise',
            'TIER_1',
            'Absorption merger (equal)',
            'Rail equipment manufacturing',
            2,
            1,
            'Pre-merger parent company (CNR). Merged with CSR to form CRRC. Banned from US FTA contracts in 2020.',
            'Open source research'
        ))

        # Aliases
        aliases = [
            ('China South Locomotive & Rolling Stock Industry (Group) Corp', 'CHINA SOUTH LOCOMOTIVE'),
            ('China South Locomotive & Rolling Stock Industry (Group) Corp', 'CSR'),
            ('China South Locomotive & Rolling Stock Industry (Group) Corp', 'CHINA SOUTH LOCOMOTIVE & ROLLING STOCK'),
            ('China CNR Corporation Ltd.', 'CHINA NORTH LOCOMOTIVE'),
            ('China CNR Corporation Ltd.', 'CNR'),
            ('China CNR Corporation Ltd.', 'CHINA CNR'),
        ]

        for entity, alias in aliases:
            cursor.execute("""
            INSERT OR IGNORE INTO entity_aliases (entity_name, alias, alias_type, current_parent)
            VALUES (?, ?, ?, ?)
            """, (entity, alias, 'Name variation', 'CRRC Corporation Limited'))

        print("[OK] Populated CRRC merger data")
        print(f"  - 2 legacy entities")
        print(f"  - 6 aliases")

        self.conn.commit()

    def populate_additional_mergers(self):
        """Populate other notable PRC SOE mergers"""
        print("\n" + "="*80)
        print("POPULATING: OTHER NOTABLE PRC SOE MERGERS")
        print("="*80)

        cursor = self.conn.cursor()

        # China Railway Jianchang Engine (part of China Railway Group)
        cursor.execute("""
        INSERT OR REPLACE INTO entity_mergers (
            legacy_entity_name,
            legacy_entity_type,
            merger_date,
            merged_into,
            current_parent,
            parent_country,
            parent_ownership,
            parent_tier,
            merger_type,
            strategic_sector,
            pre_merger_rank,
            post_merger_rank,
            notes,
            source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'China Railway Jianchang Engine',
            'Subsidiary',
            '2000-01-01',  # Approximate - China Railway Group formed 2000
            'China Railway Group Limited',
            'China Railway Group Limited',
            'China',
            'State-Owned Enterprise',
            'TIER_1',
            'Government restructuring',
            'Construction / Railway infrastructure',
            None,
            None,
            'PRC construction/railway firm operating in Africa (Tanzania). Part of China Railway Group state-controlled sector.',
            'USAspending.gov records + open source research'
        ))

        # Aliases
        cursor.execute("""
        INSERT OR IGNORE INTO entity_aliases (entity_name, alias, alias_type, current_parent)
        VALUES (?, ?, ?, ?)
        """, ('China Railway Jianchang Engine', 'CHINA RAILWAY JIANCHANG ENGINE', 'Exact name', 'China Railway Group Limited'))

        print("[OK] Populated additional merger data")
        print(f"  - 1 entity")
        print(f"  - 1 alias")

        self.conn.commit()

    def generate_lookup_function(self):
        """Create SQL function for entity lookup"""
        print("\n" + "="*80)
        print("CREATING LOOKUP HELPERS")
        print("="*80)

        cursor = self.conn.cursor()

        # Create view for easy lookup
        cursor.execute("""
        CREATE VIEW IF NOT EXISTS v_entity_lookup AS
        SELECT
            e.legacy_entity_name,
            e.current_parent,
            e.parent_tier,
            e.merger_date,
            e.strategic_sector,
            e.notes,
            GROUP_CONCAT(a.alias, '; ') as aliases
        FROM entity_mergers e
        LEFT JOIN entity_aliases a ON e.legacy_entity_name = a.entity_name
        GROUP BY e.legacy_entity_name
        """)

        print("[OK] Created view: v_entity_lookup")

        self.conn.commit()

    def print_summary(self):
        """Print summary of populated data"""
        print("\n" + "="*80)
        print("DATABASE POPULATION SUMMARY")
        print("="*80)

        cursor = self.conn.cursor()

        # Count mergers
        cursor.execute("SELECT COUNT(*) FROM entity_mergers")
        merger_count = cursor.fetchone()[0]

        # Count aliases
        cursor.execute("SELECT COUNT(*) FROM entity_aliases")
        alias_count = cursor.fetchone()[0]

        # Group by current parent
        cursor.execute("""
        SELECT current_parent, COUNT(*) as count
        FROM entity_mergers
        GROUP BY current_parent
        ORDER BY count DESC
        """)
        by_parent = cursor.fetchall()

        # Group by strategic sector
        cursor.execute("""
        SELECT strategic_sector, COUNT(*) as count
        FROM entity_mergers
        GROUP BY strategic_sector
        ORDER BY count DESC
        """)
        by_sector = cursor.fetchall()

        print(f"\nTotal legacy entities tracked: {merger_count}")
        print(f"Total aliases registered: {alias_count}")

        print(f"\nBy Current Parent:")
        for parent, count in by_parent:
            print(f"  {parent}: {count} legacy entities")

        print(f"\nBy Strategic Sector:")
        for sector, count in by_sector:
            print(f"  {sector}: {count} entities")

        print("\n" + "="*80)

    def demo_lookup(self):
        """Demonstrate entity lookup"""
        print("\n" + "="*80)
        print("ENTITY LOOKUP DEMONSTRATION")
        print("="*80)

        cursor = self.conn.cursor()

        test_queries = [
            "CHINA SHIPPING DEVELOPMENT",
            "CHINA SOUTH LOCOMOTIVE",
            "DALIAN OCEAN SHIPPING",
            "COSCO",
        ]

        for query in test_queries:
            print(f"\nLookup: '{query}'")

            # Try alias lookup
            cursor.execute("""
            SELECT entity_name, current_parent
            FROM entity_aliases
            WHERE alias LIKE ?
            """, (f"%{query}%",))

            results = cursor.fetchall()

            if results:
                for entity, parent in results:
                    print(f"  -> {entity}")
                    print(f"     Current Parent: {parent}")
            else:
                print(f"  -> No matches found")

    def run(self):
        """Execute full database creation process"""
        print("="*80)
        print("ENTITY MERGER TRACKING DATABASE CREATION")
        print("="*80)
        print(f"Database: {self.db_path}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        self.connect()

        try:
            self.create_schema()
            self.populate_cosco_merger()
            self.populate_crrc_merger()
            self.populate_additional_mergers()
            self.generate_lookup_function()
            self.print_summary()
            self.demo_lookup()

            print("\n" + "="*80)
            print("DATABASE CREATION COMPLETE")
            print("="*80)

        finally:
            self.close()


def main():
    creator = EntityMergerDatabase()
    creator.run()


if __name__ == "__main__":
    main()
