# src/utils/cer_lite.py
"""
CER‑lite: deterministic name+country canonicalization to reduce duplicates.
- Reads data/processed/country=<ISO2>/relationships.csv (if present).
- Normalizes names (lowercase, strip punctuation & legal suffixes, squeeze spaces).
- Emits a mapping and a partners table with an `ambiguous` flag.

Outputs:
  data/processed/country=<ISO2>/partners_cerlite.csv
    columns: canonical_name,country,alias,ambiguous

CLI:
  python -m src.utils.cer_lite --country SE
"""
from __future__ import annotations
import argparse, csv, re
from pathlib import Path
from typing import Dict, List, Tuple

LEGAL_SUFFIX = re.compile(r"\b(inc|ltd|limited|sa|ab|ag|gmbh|oy|as|srl|spa|plc|bv|sas|s\.a\.?|oyj|aps|kft|a\.?s\.?|s\.r\.l\.|s\.p\.a\.)\b", re.I)
PUNCT = re.compile(r"[^\w\s]", re.U)
WS = re.compile(r"\s+")


def norm(s: str) -> str:
    s = s or ""
    s = s.strip().lower()
    s = LEGAL_SUFFIX.sub("", s)
    s = PUNCT.sub(" ", s)
    s = WS.sub(" ", s)
    return s.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    cc = args.country.upper()

    proc = Path("data/processed") / f"country={cc}"
    rel = proc / "relationships.csv"
    out = proc / "partners_cerlite.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    headers = ["canonical_name","country","alias","ambiguous"]
    rows: List[List[str]] = []

    if not rel.exists():
        with out.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(headers)
        print(f"No relationships.csv for {cc}; wrote empty partners_cerlite.csv")
        return

    with rel.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        name_key = next((k for k in reader.fieldnames or [] if k.lower() in ("partner_entity","counterpart_name","partner","entity","name")), None)
        country_key = next((k for k in reader.fieldnames or [] if k.lower() in ("partner_country","counterpart_country","country")), None)
        if not name_key or not country_key:
            with out.open("w", encoding="utf-8", newline="") as g:
                csv.writer(g).writerow(headers)
            print(f"Could not resolve name/country columns; wrote empty partners_cerlite.csv")
            return
        # Build alias buckets by (norm_name, country)
        buckets: Dict[Tuple[str,str], List[str]] = {}
        for r in reader:
            n = norm(r.get(name_key, ""))
            c = (r.get(country_key, "") or "").upper()
            if not n:
                continue
            buckets.setdefault((n,c), []).append(r.get(name_key, ""))

    # Determine canonical_name = longest alias string (heuristic)
    for (n,c), aliases in buckets.items():
        canonical = max(aliases, key=len)
        # ambiguous if multiple distinct aliases mapped to same canonical key
        ambiguous = 1 if len(set(a.lower() for a in aliases)) > 1 else 0
        for a in sorted(set(aliases)):
            rows.append([canonical, c, a, str(ambiguous)])

    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"Wrote {out} ({len(rows)} rows)")

if __name__ == "__main__":
    main()