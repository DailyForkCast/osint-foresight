import argparse, json, re
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS

CN_PAT = re.compile(r"\b(china|prc|beijing|shanghai|shenzhen|hong\s*kong|中国|中國)\b", re.I)


def normalize(country: str, raw_dir: Path) -> list[list[str]]:
    rows = []
    idx = 0
    for p in sorted(raw_dir.glob("opencorporates_*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                wrap = json.loads(line)
                c = wrap.get("company") or wrap
            except Exception:
                continue
            name = (c.get("name") or "").strip()
            num = (c.get("company_number") or "").strip()
            juris = (c.get("jurisdiction_code") or "").upper()
            desc = (c.get("restricted_for_marketing") and "restricted") or ""
            # Look for CN ties in name or previous names
            text = " ".join([name] + [n.get("name","") for n in (c.get("previous_names") or [])])
            if not CN_PAT.search(text):
                continue
            idx += 1
            rid = f"OC-{idx:06d}"
            rows.append([
                rid,
                "",                 # sector (left blank; filled via join later)
                "Corporate Links",  # mechanism_family
                "company_match",     # incident_type (heuristic)
                f"Company name mentions CN marker: {name}",
                (c.get("incorporation_date") or ""),
                "",
                name,
                "",
                "oc_company_number",
                f"{juris}:{num}",
                "",
                "",
                c.get("opencorporates_url") or "",
                "B",
                0.5,
                ""
            ])
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    args = ap.parse_args()

    processed = processed_path(args.country, "mechanism_incidents.tsv")
    headers = SCHEMAS["mechanism_incidents.tsv"]

    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=opencorporates") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No OpenCorporates raw for {args.country}; wrote empty mechanism_incidents.tsv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    rows = normalize(args.country.upper(), raw_dir)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")