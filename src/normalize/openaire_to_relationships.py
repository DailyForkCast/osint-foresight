import argparse, json
from collections import Counter
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS
from ..utils.classify import primary_sector, bucket_intensity
import yaml


def load_keywords(path: Path) -> dict:
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("sectors", {}) if path.exists() else {}


def orgs_from(rec):
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


def text_blocks(rec):
    fields = []
    for k in ("title","description","subjects"):
        v = rec.get(k)
        if isinstance(v, list):
            fields.append(" ".join([str(x) for x in v]))
        elif isinstance(v, str):
            fields.append(v)
    return fields


def extract_year(rec):
    for k in ("publicationYear","year","startDate","endDate"):
        v = rec.get(k)
        try:
            if isinstance(v, int):
                return v
            if isinstance(v, str) and len(v) >= 4:
                return int(v[:4])
        except Exception:
            pass
    return ""


def normalize(country: str, raw_dir: Path, keywords_map: dict) -> list[list[str]]:
    edges = []
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
            partner = next((n for (n, c) in orgs if c == "CN" and n), "CN partner")
            sector, _ = primary_sector(text_blocks(rec), keywords_map)
            start_yr = extract_year(rec)
            collab_type = "project" if "project" in p.name else "co-publication"
            edges.append((partner, sector or "", collab_type, start_yr))

    # aggregate
    counts = Counter(edges)
    rows = []
    for (partner, sector, collab_type, start_yr), n in counts.items():
        rid = f"OAIR-{hash((partner, sector, collab_type, start_yr)) & 0xffffffff:08x}"
        rows.append([
            rid,
            "CN",
            partner,
            collab_type,
            start_yr or "",
            bucket_intensity(n),
            "two-way",
            sector or "",
            "",
            "",
            "M",
            f"OpenAIRE edges={n}",
            ""
        ])
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    ap.add_argument("--sectors-file", default="taxonomies/keywords_multilingual.yaml")
    args = ap.parse_args()

    processed = processed_path(args.country, "relationships.csv")
    headers = SCHEMAS["relationships.csv"]

    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=openaire") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No OpenAIRE raw for {args.country}; wrote empty relationships.csv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    keywords_map = load_keywords(Path(args.sectors_file))
    rows = normalize(args.country.upper(), raw_dir, keywords_map)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")