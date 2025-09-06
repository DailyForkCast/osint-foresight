import argparse, csv
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS

# Expect a participants CSV with fields like: projectID, acronym, title, startDate, endDate, fundingScheme, ecMaxContribution, orgName, orgCountry, role, etc.


def normalize(country: str, raw_dir: Path):
    prows = {}  # programs keyed by (scheme)
    for p in [raw_dir/"cordis_participants.csv"]:
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                scheme = (r.get("fundingScheme") or r.get("FrameworkProgramme") or "").strip()
                if not scheme:
                    continue
                # programs.csv minimal fields: id, name, owner, instrument_type, url, notes
                key = scheme
                if key not in prows:
                    prows[key] = [key, scheme, "EU", "grant", "", "CORDIS"]
    return list(prows.values())

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    args = ap.parse_args()

    processed = processed_path(args.country, "programs.csv")
    headers = SCHEMAS["programs.csv"]

    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=cordis") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No CORDIS raw for {args.country}; wrote empty programs.csv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    rows = normalize(args.country.upper(), raw_dir)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")