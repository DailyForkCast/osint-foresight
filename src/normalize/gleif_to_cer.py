import argparse, json
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS

# cer_master.csv headers expected by our schema registry (id,name_en,name_local,country,lei,ror,registry_ids,aliases;confidence)
# institutions.csv headers include accreditation fields; we fill identity only here.


def normalize_lei(raw_dir: Path):
    rows_cer = {}
    rows_inst = {}
    for p in sorted(raw_dir.glob("gleif_leis_p*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                it = json.loads(line)
            except Exception:
                continue
            lei = (it.get("id") or "").strip()
            attrs = (it.get("attributes") or {})
            name = (attrs.get("entity", {}).get("legalName", {}).get("name") or "").strip()
            country = (attrs.get("entity", {}).get("legalAddress", {}).get("country") or "").strip()
            # CER master
            rows_cer[lei] = [lei, name, "", country, lei, "", "", "", 0.8]
            # institutions
            rows_inst[lei] = [lei, name, country, "", "", "", "", ""]
    return list(rows_cer.values()), list(rows_inst.values())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    args = ap.parse_args()

    # Output paths
    cer_p = processed_path(args.country, "cer_master.csv")
    inst_p = processed_path(args.country, "institutions.csv")
    cer_headers = SCHEMAS["cer_master.csv"]
    inst_headers = SCHEMAS["institutions.csv"]

    # Locate raw dir
    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=gleif") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(cer_p, cer_headers, [])
            write_table(inst_p, inst_headers, [])
            print(f"No GLEIF raw for {args.country}; wrote empty cer_master & institutions")
            raise SystemExit(0)
        raw_dir = parts[-1]

    cer_rows, inst_rows = normalize_lei(raw_dir)
    write_table(cer_p, cer_headers, cer_rows)
    write_table(inst_p, inst_headers, inst_rows)
    print(f"Wrote {cer_p} and {inst_p}")