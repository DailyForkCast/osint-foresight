import argparse
from ..utils.io import reports_path
from ..utils.reporting import ensure_template

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    ensure_template(args.country.upper(), "phase-9_posture.md")
    out = reports_path(args.country, "phase-9_prc_interest.md")
    out.write_text("# Phase 9 — PRC Interest & MCF Acquisition Assessment\n\n(Stub narrative)\n", encoding="utf-8")
    print(f"Wrote {out}")
