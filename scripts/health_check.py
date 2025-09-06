#!/usr/bin/env python3
"""
Lightweight repo health checker.
- Verifies presence of expected processed tables (or empty placeholders).
- Prints last raw date partitions per source.
- Warns if any processed file is older than 30 days.
- Non‑fatal: exits 0 unless COUNTRY invalid.

Usage: python scripts/health_check.py --country SE
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from datetime import datetime, timedelta

PROCESSED_FILES = [
    "relationships.csv",
    "signals.csv",
    "standards_roles.tsv",
    "cer_master.csv",
    "institutions.csv",
    "mechanism_incidents.tsv",
    "programs.csv",
    "sanctions_hits.csv",
]

RAW_SOURCES = [
    "openaire","crossref","crossref_event","ietf","gleif","opencorporates","patents","cordis","sanctions","trade"
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()

    cc = args.country.upper()
    if len(cc) != 2:
        print("COUNTRY must be ISO2 (e.g., SE)")
        sys.exit(2)

    proc_dir = Path("data/processed") / f"country={cc}"
    if not proc_dir.exists():
        print(f"[WARN] processed dir missing: {proc_dir}")
    else:
        print(f"Processed dir: {proc_dir}")

    stale = []
    for fname in PROCESSED_FILES:
        p = proc_dir / fname
        if p.exists():
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            age = datetime.now() - mtime
            mark = "STALE" if age > timedelta(days=30) else "OK"
            print(f"  - {fname}: {mark} ({int(age.days)}d old)")
            if mark == "STALE":
                stale.append(fname)
        else:
            print(f"  - {fname}: MISSING (ok if not used)")

    print("\nLatest raw partitions:")
    for src in RAW_SOURCES:
        base = Path("data/raw") / f"source={src}" / f"country={cc}"
        parts = sorted(base.glob("date=*"))
        if parts:
            print(f"  - {src}: {parts[-1].name}")
        else:
            print(f"  - {src}: (none)")

    if stale:
        print("\n[NOTE] Consider: make pull COUNTRY=%s && make normalize-all COUNTRY=%s" % (cc, cc))

if __name__ == "__main__":
    main()