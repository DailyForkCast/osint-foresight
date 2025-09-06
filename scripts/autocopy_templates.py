#!/usr/bin/env python3
# scripts/autocopy_templates.py
"""
Auto-copy report templates for a country if missing.
- Scans reports/templates/* and ensures the same filename exists under reports/country=<ISO2>/.
- Never overwrites existing files; only creates missing ones.
- Prints a concise log of actions.

Usage:
  python scripts/autocopy_templates.py --country SE
Optional:
  --templates reports/templates
  --outdir reports
"""
from __future__ import annotations
import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="ISO2 country code, e.g. SE")
    ap.add_argument("--templates", default="reports/templates", help="Templates directory")
    ap.add_argument("--outdir", default="reports", help="Reports root output directory")
    args = ap.parse_args()

    ccode = args.country.upper()
    tpl_root = Path(args.templates)
    out_root = Path(args.outdir) / f"country={ccode}"
    out_root.mkdir(parents=True, exist_ok=True)

    if not tpl_root.exists():
        print(f"[WARN] Templates directory not found: {tpl_root}")
        return

    created = 0
    skipped = 0
    for p in sorted(tpl_root.glob("*.md")):
        dst = out_root / p.name
        if dst.exists():
            skipped += 1
            print(f"OK     {dst}")
            continue
        dst.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        created += 1
        print(f"CREATE {dst}")

    print(f"Done. Created {created}, existing {skipped}.")


if __name__ == "__main__":
    main()