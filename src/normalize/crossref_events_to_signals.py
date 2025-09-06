import argparse, json
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS

CATEG = "Bibliometrics/Attention"


def normalize(raw_dir: Path) -> list[list[str]]:
    rows = []
    for p in sorted(raw_dir.glob("event_*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                ev = json.loads(line)
            except Exception:
                continue
            date = ev.get("occurred_at") or ev.get("timestamp") or ""
            link = ev.get("obj_id") or ev.get("subj_id") or ""
            desc = ev.get("relation_type_id") or ev.get("source_id") or "Crossref Event"
            rid = f"SIG-{abs(hash((p.name, date, desc))) % (10**10):010d}"
            rows.append([rid, CATEG, "Event spike", desc, "review", "Analyst", str(date)])
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    args = ap.parse_args()

    processed = processed_path(args.country, "signals.csv")
    headers = SCHEMAS["signals.csv"]

    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=crossref_event") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No Event Data raw for {args.country}; wrote empty signals.csv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    rows = normalize(raw_dir)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")