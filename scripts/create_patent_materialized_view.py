#!/usr/bin/env python3
"""
Create Materialized View for Patent-Sector Mapping
One-time optimization for fast cross-reference queries
"""

import sys
import sqlite3
import time
from pathlib import Path
from datetime import datetime

DB_PATH = Path("F:/OSINT_WAREHOUSE/osint_master.db")

def create_materialized_view():
    """Create patent_sector_mapping table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("="*80)
    print("CREATING MATERIALIZED VIEW FOR PATENT-SECTOR MAPPING")
    print("="*80)
    print("\nThis will take ~15-20 minutes but needs to be done only once.")
    print("Future queries will be near-instant.\n")

    # Drop existing table if present
    print("[STEP 1] Dropping existing materialized view if present...")
    cursor.execute("DROP TABLE IF EXISTS patent_sector_mapping")
    conn.commit()
    print("  Done")

    # Create the materialized view
    print("\n[STEP 2] Creating materialized view (this is the slow part)...")
    print("  Processing 425,074 patents x 65.6M CPC classifications...")

    start_time = time.time()

    # Create table with sector mappings based on CPC codes
    cursor.execute("""
    CREATE TABLE patent_sector_mapping AS
    SELECT DISTINCT
        p.application_number,
        p.filing_date,
        p.grant_date,
        p.year,
        CASE
            -- Advanced Information Technology
            WHEN c.cpc_full LIKE 'H01L%' THEN 'semiconductors'
            WHEN c.cpc_full LIKE 'G06F%' THEN 'computing'
            WHEN c.cpc_full LIKE 'G06N%' THEN 'artificial_intelligence'
            WHEN c.cpc_full LIKE 'H04L%' THEN 'telecommunications'
            WHEN c.cpc_full LIKE 'H04W%' THEN 'wireless_networks'
            WHEN c.cpc_full LIKE 'G06Q%' THEN 'data_processing_business'

            -- Robotics and Automation
            WHEN c.cpc_full LIKE 'B25J%' THEN 'robotics'
            WHEN c.cpc_full LIKE 'G05B%' THEN 'control_systems'
            WHEN c.cpc_full LIKE 'B23Q%' THEN 'automated_machine_tools'

            -- Aerospace
            WHEN c.cpc_full LIKE 'B64C%' THEN 'aircraft'
            WHEN c.cpc_full LIKE 'B64D%' THEN 'aircraft_equipment'
            WHEN c.cpc_full LIKE 'B64F%' THEN 'aircraft_ground_support'
            WHEN c.cpc_full LIKE 'F02K%' THEN 'jet_propulsion'

            -- Maritime Equipment
            WHEN c.cpc_full LIKE 'B63B%' THEN 'ships'
            WHEN c.cpc_full LIKE 'B63H%' THEN 'marine_propulsion'

            -- Rail Equipment
            WHEN c.cpc_full LIKE 'B61D%' THEN 'railway_vehicles'
            WHEN c.cpc_full LIKE 'B61F%' THEN 'railway_suspension'

            -- New Energy Vehicles
            WHEN c.cpc_full LIKE 'B60L%' THEN 'electric_vehicles'
            WHEN c.cpc_full LIKE 'H01M%' THEN 'batteries'
            WHEN c.cpc_full LIKE 'B60K%' THEN 'vehicle_propulsion'

            -- Power Equipment
            WHEN c.cpc_full LIKE 'H02J%' THEN 'power_systems'
            WHEN c.cpc_full LIKE 'H02M%' THEN 'power_conversion'

            -- Agricultural Equipment
            WHEN c.cpc_full LIKE 'A01B%' THEN 'soil_working'
            WHEN c.cpc_full LIKE 'A01D%' THEN 'harvesting'

            -- New Materials
            WHEN c.cpc_full LIKE 'C01B%' THEN 'chemical_materials'
            WHEN c.cpc_full LIKE 'C08J%' THEN 'plastics_materials'
            WHEN c.cpc_full LIKE 'C23C%' THEN 'coating_materials'

            -- Biopharmaceuticals
            WHEN c.cpc_full LIKE 'A61K%' THEN 'pharmaceuticals'
            WHEN c.cpc_full LIKE 'C12N%' THEN 'biotechnology'
            WHEN c.cpc_full LIKE 'C07K%' THEN 'peptides'
            WHEN c.cpc_full LIKE 'A61P%' THEN 'therapeutic_compounds'

            -- Quantum Computing (emerging priority)
            WHEN c.cpc_full LIKE 'G06N10%' THEN 'quantum_computing'
            WHEN c.cpc_full LIKE 'B82Y%' THEN 'nanostructures_quantum'

            ELSE 'other'
        END as sector,
        c.cpc_full as cpc_code
    FROM uspto_patents_chinese p
    JOIN uspto_cpc_classifications c ON p.application_number = c.application_number
    """)

    conn.commit()
    elapsed = time.time() - start_time

    print(f"  Done in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")

    # Get statistics
    total_mappings = cursor.execute("SELECT COUNT(*) FROM patent_sector_mapping").fetchone()[0]
    unique_patents = cursor.execute("SELECT COUNT(DISTINCT application_number) FROM patent_sector_mapping").fetchone()[0]

    print(f"\n  Total mappings created: {total_mappings:,}")
    print(f"  Unique patents mapped: {unique_patents:,}")

    # Show sector distribution
    print("\n  Sector distribution:")
    sectors = cursor.execute("""
    SELECT sector, COUNT(DISTINCT application_number) as patents
    FROM patent_sector_mapping
    GROUP BY sector
    ORDER BY patents DESC
    LIMIT 15
    """).fetchall()

    for sector, count in sectors:
        print(f"    {sector:<30} {count:>8,} patents")

    # Create indexes
    print("\n[STEP 3] Creating indexes for fast queries...")

    start_time = time.time()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sector_filing ON patent_sector_mapping(sector, filing_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sector_app ON patent_sector_mapping(sector, application_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_filing_date ON patent_sector_mapping(filing_date)")
    conn.commit()

    elapsed = time.time() - start_time
    print(f"  Done in {elapsed:.1f} seconds")

    # Create aggregated sector view (MIC2025 10 sectors)
    print("\n[STEP 4] Creating MIC2025 sector aggregation view...")

    cursor.execute("DROP TABLE IF EXISTS patent_mic2025_sectors")
    cursor.execute("""
    CREATE TABLE patent_mic2025_sectors AS
    SELECT
        application_number,
        filing_date,
        year,
        CASE
            WHEN sector IN ('semiconductors', 'computing', 'artificial_intelligence',
                           'telecommunications', 'wireless_networks', 'data_processing_business')
                THEN 'advanced_information_technology'
            WHEN sector IN ('robotics', 'control_systems', 'automated_machine_tools')
                THEN 'robotics_automation'
            WHEN sector IN ('aircraft', 'aircraft_equipment', 'aircraft_ground_support', 'jet_propulsion')
                THEN 'aerospace_equipment'
            WHEN sector IN ('ships', 'marine_propulsion')
                THEN 'maritime_equipment'
            WHEN sector IN ('railway_vehicles', 'railway_suspension')
                THEN 'rail_equipment'
            WHEN sector IN ('electric_vehicles', 'batteries', 'vehicle_propulsion')
                THEN 'new_energy_vehicles'
            WHEN sector IN ('power_systems', 'power_conversion')
                THEN 'power_equipment'
            WHEN sector IN ('soil_working', 'harvesting')
                THEN 'agricultural_equipment'
            WHEN sector IN ('chemical_materials', 'plastics_materials', 'coating_materials')
                THEN 'new_materials'
            WHEN sector IN ('pharmaceuticals', 'biotechnology', 'peptides', 'therapeutic_compounds')
                THEN 'biopharmaceuticals'
            WHEN sector IN ('quantum_computing', 'nanostructures_quantum')
                THEN 'quantum_computing'
            ELSE 'non_priority'
        END as mic2025_sector
    FROM patent_sector_mapping
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mic2025_filing ON patent_mic2025_sectors(mic2025_sector, filing_date)")
    conn.commit()

    print("  Done")

    # Test query speed
    print("\n[STEP 5] Testing query performance...")

    test_queries = [
        ("Semiconductors pre-MIC2025", """
        SELECT COUNT(DISTINCT application_number)
        FROM patent_sector_mapping
        WHERE sector = 'semiconductors'
          AND filing_date >= '2011-01-01'
          AND filing_date < '2015-05-08'
        """),
        ("Semiconductors post-MIC2025", """
        SELECT COUNT(DISTINCT application_number)
        FROM patent_sector_mapping
        WHERE sector = 'semiconductors'
          AND filing_date >= '2015-05-08'
          AND filing_date <= '2020-12-31'
        """),
        ("All MIC2025 sectors", """
        SELECT mic2025_sector, COUNT(DISTINCT application_number)
        FROM patent_mic2025_sectors
        WHERE mic2025_sector != 'non_priority'
        GROUP BY mic2025_sector
        """)
    ]

    for query_name, query in test_queries:
        start_time = time.time()
        result = cursor.execute(query).fetchall()
        elapsed = time.time() - start_time
        print(f"  {query_name}: {elapsed:.3f} seconds")

    conn.close()

    print("\n" + "="*80)
    print("MATERIALIZED VIEW CREATION COMPLETE")
    print("="*80)
    print("\nThe database is now optimized for fast cross-reference queries.")
    print("Future analyses will complete in seconds instead of minutes/hours.")
    print("\nNext step: Run cross_reference_policy_patents.py")
    print("="*80)


if __name__ == "__main__":
    create_materialized_view()
