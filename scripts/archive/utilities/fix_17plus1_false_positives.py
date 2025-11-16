#!/usr/bin/env python3
"""
Fix 17+1 Initiative False Positives
Clear bus seating capacity false positives and update pattern
"""

import sqlite3
from pathlib import Path

db_path = Path("F:/OSINT_WAREHOUSE/osint_master.db")

print("\n" + "="*80)
print("FIXING 17+1 INITIATIVE FALSE POSITIVES")
print("="*80)
print()

conn = sqlite3.connect(db_path, timeout=60.0)
cursor = conn.cursor()

# Count current 17+1 contracts
current_count = cursor.execute("""
    SELECT COUNT(*) FROM ted_contracts_production
    WHERE influence_category = '17PLUS1_INITIATIVE'
""").fetchone()[0]

print(f"Current 17+1 Initiative contracts: {current_count}")
print()

# Clear 17+1 categorization (all are bus seating capacity false positives)
print("Clearing 17+1 false positives (bus seating capacity)...")
cursor.execute("""
    UPDATE ted_contracts_production
    SET influence_category = NULL,
        influence_priority = NULL,
        influence_patterns = NULL
    WHERE influence_category = '17PLUS1_INITIATIVE'
""")

cleared = cursor.rowcount
conn.commit()

print(f"Cleared {cleared} false positive contracts")
print()

# Verify
remaining = cursor.execute("""
    SELECT COUNT(*) FROM ted_contracts_production
    WHERE influence_category = '17PLUS1_INITIATIVE'
""").fetchone()[0]

print(f"Remaining 17+1 contracts: {remaining}")
print()

conn.close()

print("="*80)
print("CLEANUP COMPLETE")
print("="*80)
print()
print("Summary:")
print(f"  False Positives Cleared: {cleared}")
print(f"  Pattern Updated: require China/CEEC context")
print()
print("Note: The corrected 17+1 pattern is now in reprocess_full_ted_database.py")
print("      It requires 'China', 'CEEC', or full phrase 'Seventeen Plus One'")
print("      Standalone '17+1' (bus seating) will no longer match")
print()
