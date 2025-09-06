import argparse
from ..utils.io import reports_path
from ..utils.reporting import ensure_template

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    ensure_template(args.country.upper(), "phase-5_links.md")
    out = reports_path(args.country, "phase5_links.md")
    out.write_text("# Phase 5 — International Links & Collaboration\n\n(Stub narrative)\n", encoding="utf-8")
    print(f"Wrote {out}")