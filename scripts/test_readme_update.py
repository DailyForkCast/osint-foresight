#!/usr/bin/env python3
"""
Test script for README update automation
Run this to test the README update without waiting 12 hours
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Force update by removing last update file
LAST_UPDATE_FILE = PROJECT_ROOT / "scripts/.readme_last_update.json"
if LAST_UPDATE_FILE.exists():
    LAST_UPDATE_FILE.unlink()
    print("Removed last update record to force update")

# Import and run update
try:
    from scripts.update_readme import main
    print("Testing README update...")
    main()
    print("Test completed successfully!")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()

# Show what changed
readme_path = PROJECT_ROOT / "README.md"
if readme_path.exists():
    print(f"\nUpdated README.md ({readme_path.stat().st_size} bytes)")
    print("Check the file to see current status")
else:
    print("README.md not found after update")
