#!/usr/bin/env python3
"""Collect December 2021 with 100k limit"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "collectors"))

from gdelt_bigquery_collector import GDELTCollector

collector = GDELTCollector(
    master_db="F:/OSINT_WAREHOUSE/osint_master.db",
    use_bigquery=True
)

print("Re-collecting December 2021 with 100,000 event limit...")

collector.connect()
collector.create_tables()
collector.setup_bigquery()

# Collect with 100k limit
collector.collect_china_events("20211201", "20211231", batch_size=100000)

print(f"December 2021: {collector.stats['events_collected']:,} events collected")

collector.conn.close()
