#!/usr/bin/env python3
"""
Think Tank Global Collector - State Management Module

Handles atomic state commits with lock files for incremental collection.
State file: F:/ThinkTank_Sweeps/STATE/thinktanks_state.json
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class StateManager:
    """Manages incremental collection state with atomic commits and locking."""

    STATE_DIR = Path("F:/ThinkTank_Sweeps/STATE")
    STATE_FILE = STATE_DIR / "thinktanks_state.json"
    LOCK_FILE = STATE_DIR / ".lock"
    TEMP_FILE = STATE_DIR / "thinktanks_state.tmp"
    LOCK_TIMEOUT_HOURS = 6

    INITIAL_STATE = {
        "version": "1.0",
        "last_global_run_iso": None,
        "regions": {
            "US_CAN": {
                "forward_watermark_iso": None,
                "backfill_pointer_year": 2024,
                "sources": {}
            },
            "EUROPE": {
                "forward_watermark_iso": None,
                "backfill_pointer_year": 2024,
                "sources": {}
            },
            "APAC": {
                "forward_watermark_iso": None,
                "backfill_pointer_year": 2024,
                "sources": {}
            },
            "ARCTIC": {
                "forward_watermark_iso": None,
                "backfill_pointer_year": 2024,
                "sources": {}
            }
        }
    }

    def __init__(self):
        """Initialize state manager and ensure directories exist."""
        self.STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.state: Dict[str, Any] = {}
        self.lock_acquired = False

    def acquire_lock(self) -> bool:
        """
        Acquire lock file. Returns True if successful, False if stale lock detected.
        Raises exception if active lock exists.
        """
        if self.LOCK_FILE.exists():
            # Check if lock is stale
            lock_age_seconds = time.time() - self.LOCK_FILE.stat().st_mtime
            lock_age_hours = lock_age_seconds / 3600

            if lock_age_hours > self.LOCK_TIMEOUT_HOURS:
                logging.error(f"Stale lock detected (age: {lock_age_hours:.1f}h > {self.LOCK_TIMEOUT_HOURS}h)")
                return False
            else:
                raise RuntimeError(
                    f"Active lock exists (age: {lock_age_hours:.1f}h). "
                    f"Another process may be running."
                )

        # Create lock file
        try:
            self.LOCK_FILE.write_text(json.dumps({
                "pid": os.getpid(),
                "timestamp_iso": datetime.now(timezone.utc).isoformat(),
                "hostname": os.environ.get("COMPUTERNAME", "unknown")
            }, indent=2))
            self.lock_acquired = True
            logging.info(f"Lock acquired: {self.LOCK_FILE}")
            return True
        except Exception as e:
            logging.error(f"Failed to acquire lock: {e}")
            raise

    def release_lock(self):
        """Release lock file."""
        if self.lock_acquired and self.LOCK_FILE.exists():
            try:
                self.LOCK_FILE.unlink()
                self.lock_acquired = False
                logging.info("Lock released")
            except Exception as e:
                logging.error(f"Failed to release lock: {e}")

    def load_state(self) -> Dict[str, Any]:
        """Load state from disk. Initialize if missing."""
        if not self.STATE_FILE.exists():
            logging.info("State file not found, initializing with defaults")
            self.state = self.INITIAL_STATE.copy()
            self.save_state()  # Create initial state file
        else:
            try:
                with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
                logging.info(f"State loaded from {self.STATE_FILE}")
            except Exception as e:
                logging.error(f"Failed to load state: {e}")
                raise

        return self.state

    def save_state(self):
        """
        Atomically save state to disk using temp file + fsync + atomic rename.
        This prevents corruption if process is interrupted.
        """
        try:
            # Update timestamp
            self.state["last_global_run_iso"] = datetime.now(timezone.utc).isoformat()

            # Write to temporary file
            with open(self.TEMP_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())  # Ensure written to disk

            # Atomic rename (POSIX guarantees atomicity)
            self.TEMP_FILE.replace(self.STATE_FILE)
            logging.info(f"State saved atomically to {self.STATE_FILE}")

        except Exception as e:
            logging.error(f"Failed to save state: {e}")
            if self.TEMP_FILE.exists():
                self.TEMP_FILE.unlink()
            raise

    def get_region_state(self, region: str) -> Dict[str, Any]:
        """Get state for a specific region."""
        if region not in self.state.get("regions", {}):
            raise ValueError(f"Unknown region: {region}. Valid: {list(self.state.get('regions', {}).keys())}")
        return self.state["regions"][region]

    def update_region_watermark(self, region: str, new_watermark: str):
        """Update forward watermark for a region."""
        if region not in self.state["regions"]:
            raise ValueError(f"Unknown region: {region}")

        self.state["regions"][region]["forward_watermark_iso"] = new_watermark
        logging.info(f"Updated {region} watermark to {new_watermark}")

    def decrement_backfill_pointer(self, region: str):
        """Decrement backfill year pointer (e.g., 2024 -> 2023)."""
        if region not in self.state["regions"]:
            raise ValueError(f"Unknown region: {region}")

        current_year = self.state["regions"][region]["backfill_pointer_year"]
        if current_year > 2010:  # Don't go below 2010
            self.state["regions"][region]["backfill_pointer_year"] = current_year - 1
            logging.info(f"Decremented {region} backfill pointer: {current_year} -> {current_year - 1}")
        else:
            logging.info(f"{region} backfill complete (reached 2010)")

    def update_source_metadata(self, region: str, source_domain: str, metadata: Dict[str, Any]):
        """Update metadata for a specific source within a region."""
        if region not in self.state["regions"]:
            raise ValueError(f"Unknown region: {region}")

        if "sources" not in self.state["regions"][region]:
            self.state["regions"][region]["sources"] = {}

        self.state["regions"][region]["sources"][source_domain] = {
            **metadata,
            "last_updated_iso": datetime.now(timezone.utc).isoformat()
        }

    def get_time_windows(self, region: str) -> Dict[str, Any]:
        """
        Calculate Lane A (forward) and Lane B (backfill) time windows for a region.

        Returns:
            {
                "lane_a": {"start": "2025-01-01", "end": "2025-10-12"},
                "lane_b": {"year": 2024}
            }
        """
        region_state = self.get_region_state(region)

        # Lane A (Forward): from max('2025-01-01', watermark) to now
        watermark = region_state.get("forward_watermark_iso")
        lane_a_start = max(
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime.fromisoformat(watermark) if watermark else datetime(2025, 1, 1, tzinfo=timezone.utc)
        )
        lane_a_end = datetime.now(timezone.utc)

        # Lane B (Backfill): exactly the backfill_pointer_year
        lane_b_year = region_state.get("backfill_pointer_year", 2024)

        return {
            "lane_a": {
                "start": lane_a_start.isoformat(),
                "end": lane_a_end.isoformat()
            },
            "lane_b": {
                "year": lane_b_year,
                "start": f"{lane_b_year}-01-01T00:00:00Z",
                "end": f"{lane_b_year}-12-31T23:59:59Z"
            }
        }

    def create_run_journal(self, region: str, run_data: Dict[str, Any]) -> Path:
        """Create run journal for tracking individual runs."""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        journal_file = self.STATE_DIR / f"run_journal_{region}_{date_str}.json"

        with open(journal_file, 'w', encoding='utf-8') as f:
            json.dump(run_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Run journal created: {journal_file}")
        return journal_file

    def __enter__(self):
        """Context manager entry: acquire lock and load state."""
        if not self.acquire_lock():
            raise RuntimeError("Cannot acquire lock (stale lock detected)")
        self.load_state()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: release lock."""
        self.release_lock()
        return False  # Don't suppress exceptions


# Example usage
if __name__ == "__main__":
    # Test state management
    with StateManager() as sm:
        state = sm.load_state()
        print(json.dumps(state, indent=2))

        # Test time window calculation
        for region in ["US_CAN", "EUROPE", "APAC", "ARCTIC"]:
            windows = sm.get_time_windows(region)
            print(f"\n{region} Time Windows:")
            print(json.dumps(windows, indent=2))
