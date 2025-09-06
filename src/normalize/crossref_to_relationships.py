import argparse, json, re
from collections import defaultdict, Counter
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS
from ..utils.classify import primary_sector, bucket_intensity
import yaml

CN_PAT = re.compile(r"\b(china|prc|beijing|shanghai|shenzhen|中国|中國)\b", re.I)


def load_keywords(path: Path) -> dict:
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("sectors", {}) if path.exists() else {}


def is_cn_affil(affil_list: list) -> bool:
    s = " ".join([a.get("name","") if isinstance(a, dict) else str(a) for a in (affil_list or [])])
    return bool(CN_PAT.search(s))


def affil_text(item) -> str:
    parts = []
    for a in item.get("affiliation", []) or []:
        if isinstance(a, dict):
            parts.append(a.get("name",""))
        else:
            parts.append(str(a))
    return " ; ".join([p for p in parts if p])


def extract_cn_partner(item) -> str:
    for a in item.get("affiliation", []) or []:
        name = (a.get("name") if isinstance(a, dict) else str(a)).strip()
        if name and CN_PAT.search(name):
            return name
    return "Chinese affiliation"


def year_of(item) -> int|str:
    try:
        date_parts = (item.get("issued", {}) or {}).get("date-parts", [[None]])[0]
        return date_parts[0] or ""
    except Exception:
        return ""


def normalize(country: str, raw_dir: Path, keywords_map: dict) -> list[list[str]]:
    edges = []
    for p in sorted(raw_dir.glob("crossref_works_p*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                it = json.loads(line)
            except Exception:
                continue
            # require both COUNTRY and CN in affiliations
            aff = it.get("affiliation", [])
            if not aff or not is_cn_affil({"affiliation": aff}["affiliation"]):
                continue
            # primary sector via title+container+subject
            title = (" ".join(it.get("title", [])) or "").strip()
            container = (" ".join(it.get("container-title", [])) or "").strip()
            subject = (" ".join(it.get("subject", [])) or "").strip()
            sector, _ = primary_sector([title, container, subject], keywords_map)
            partner = extract_cn_partner(it)
            start_yr = year_of(it)
            edges.append((partner, sector or "", start_yr))

    # aggregate edges
    counter = Counter(edges)
    rows = []
    for (partner, sector, start_yr), n in counter.items():
        rid = f"CRF-{hash((partner, sector, start_yr)) & 0xffffffff:08x}"
        rows.append([
            rid,
            "CN",
            partner,
            "co-publication",
            start_yr or "",
            bucket_intensity(n),
            "two-way",
            sector or "",
            "",
            "",
            "M",
            f"Crossref co-author edges={n}",
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
        root = Path("data/raw/source=crossref") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No Crossref raw for {args.country}; wrote empty relationships.csv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    keywords_map = load_keywords(Path(args.sectors_file))
    rows = normalize(args.country.upper(), raw_dir, keywords_map)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")