import argparse, json
from collections import defaultdict
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS
from ..utils.standards import wg_sector_map

# We infer roles from document meta: authors (editors), WG chairs (via group data not always present in doc).
# For a first pass, count editors as "editor" role and everyone else as "member".

ROLE_MAP = {"editor": "editor", "chair": "chair", "rapporteur": "rapporteur", "member": "member"}


def extract_roles(doc: dict):
    roles = []
    # Editors (doc authors sometimes labeled with role="editor" in datatracker output)
    for a in doc.get("authors", []) or []:
        role = (a.get("role") or "").lower()
        name = a.get("name") or a.get("person", {}).get("name", "")
        if not name:
            continue
        if role == "editor":
            roles.append("editor")
        else:
            roles.append("member")
    if not roles:
        roles.append("member")
    return roles


def normalize(raw_dir: Path) -> list[list[str]]:
    rows = []
    sector_map = wg_sector_map()
    for p in sorted(raw_dir.glob("ietf_*.jsonl")):
        acr = p.stem.split("_",1)[1]
        sector = sector_map.get(acr.lower(), "")
        roles_counter = defaultdict(int)
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
            except Exception:
                continue
            for r in extract_roles(d):
                roles_counter[r] += 1
        # summarize as one row per WG+role
        for role, count in roles_counter.items():
            rid = f"IETF-{hash((acr, role)) & 0xffffffff:08x}"
            rows.append([
                rid, "IETF", acr, ROLE_MAP.get(role, "member"), "", "",  # ballots unknown (leave blank)
                1 if count else 0,  # streak_quarters: coarse placeholder (we can compute from draft dates later)
                f"https://datatracker.ietf.org/wg/{acr}/about/",  # link
                0.7  # confidence baseline
            ])
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    args = ap.parse_args()

    processed = processed_path(args.country, "standards_roles.tsv")
    headers = SCHEMAS["standards_roles.tsv"]

    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=ietf") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No IETF raw for {args.country}; wrote empty standards_roles.tsv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    rows = normalize(raw_dir)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")