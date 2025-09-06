import argparse
from ..utils.io import reports_path

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    out = reports_path(args.country, "phase8_foresight.md")
    out.write_text("# Phase 8 — Foresight & Early Warning\n\n(Stub narrative)\n", encoding="utf-8")
    print(f"Wrote {out}")