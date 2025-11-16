#!/usr/bin/env python3
"""
Clear BRI False Positives
Remove all 872 false positive BRI detections before re-running with fixed pattern
"""

import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("\n" + "="*80)
print("CLEARING BRI FALSE POSITIVES")
print("="*80)
print()

conn = sqlite3.connect(db_path, timeout=30.0)  # Wait up to 30 seconds for lock
cursor = conn.cursor()

# Count current BRI contracts
current_count = cursor.execute("""
    SELECT COUNT(*) FROM ted_contracts_production
    WHERE influence_category = 'BRI_RELATED'
""").fetchone()[0]

print(f"Current BRI contracts: {current_count}")
print()

# Clear BRI categorization
print("Clearing BRI_RELATED influence category...")
cursor.execute("""
    UPDATE ted_contracts_production
    SET influence_category = NULL,
        influence_priority = NULL,
        influence_patterns = NULL
    WHERE influence_category = 'BRI_RELATED'
""")

affected = cursor.rowcount
conn.commit()

print(f"Cleared {affected} contracts")
print()

# Verify
remaining = cursor.execute("""
    SELECT COUNT(*) FROM ted_contracts_production
    WHERE influence_category = 'BRI_RELATED'
""").fetchone()[0]

print(f"Remaining BRI contracts: {remaining}")
print()

conn.close()

print("="*80)
print("CLEANUP COMPLETE")
print("="*80)
