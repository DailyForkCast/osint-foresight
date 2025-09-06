import argparse, json, re
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS

# Minimal mapping helpers -------------------------------------------------

def extract_year(rec):
    for k in ("publicationYear","year","startDate","endDate"):
        v = rec.get(k)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and re.match(r"^\d{4}$", v):
            return int(v)
    return ""


def orgs_from(rec):
    # OpenAIRE records tend to have organizations list in several fields; be tolerant
    orgs = []
    for k in ("relOrganizations", "organizations", "affiliations"):
        v = rec.get(k)
        if isinstance(v, list):
            for o in v:
                name = (o.get("title") or o.get("name") or "").strip()
                country = (o.get("country") or o.get("countryCode") or "").strip()
                if name:
                    orgs.append((name, country))
    return orgs

# ------------------------------------------------------------------------

def normalize(country: str, raw_dir: Path) -> list[list[str]]:
    rows = []
    for p in sorted(raw_dir.glob("openaire_*_p*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except Exception:
                continue
            orgs = orgs_from(rec)
            countries = {c for (_, c) in orgs}
            if not (country in countries and "CN" in countries):
                continue
            # pick a partner entity (first CN org encountered)
            partner = next((n for (n, c) in orgs if c == "CN"), "Unknown CN partner")
            start_yr = extract_year(rec)
            collab_type = "project" if "project" in p.name else "co-publication"
            rid = f"OAIR-{hash((partner, start_yr, collab_type)) & 0xffffffff:08x}"
            rows.append([
                rid,
                "CN",
                partner,
                collab_type,
                start_yr or "",
                1,                 # intensity_0_3 (baseline; later we aggregate)
                "two-way",
                "AI/HPC/Data",    # sector default for this first pass
                "",
                "",
                "M",
                "OpenAIRE co-activity",
                ""
            ])
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None, help="Override raw dir path")
    args = ap.parse_args()

    processed = processed_path(args.country, "relationships.csv")
    headers = SCHEMAS["relationships.csv"]

    # Locate most recent date partition under raw
    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=openaire") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No OpenAIRE raw found for {args.country}; wrote empty relationships.csv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    rows = normalize(args.country.upper(), raw_dir)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")