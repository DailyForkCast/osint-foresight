import argparse, csv
from collections import defaultdict, Counter
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS

# Build co-participation edges between COUNTRY orgs and CN orgs within the same project.


def normalize(country: str, raw_dir: Path):
    projects = defaultdict(list)  # pid -> [(orgName, orgCountry)]
    for p in [raw_dir/"cordis_participants.csv"]:
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                pid = (r.get("projectID") or r.get("ProjectID") or r.get("project_id") or "").strip()
                org = (r.get("orgName") or r.get("participantLegalName") or r.get("organisationName") or "").strip()
                cc = (r.get("orgCountry") or r.get("country") or "").strip().upper()
                if pid and org:
                    projects[pid].append((org, cc))

    # aggregate edges
    edge_counter = Counter()
    for pid, orgs in projects.items():
        have_cty = [o for o in orgs if o[1] == country.upper()]
        have_cn = [o for o in orgs if o[1] == "CN"]
        for _, _ in have_cty:
            for cn_name, _ in have_cn:
                edge_counter[(cn_name, pid)] += 1

    rows = []
    for (cn_partner, pid), n in edge_counter.items():
        rid = f"CORDIS-{abs(hash((cn_partner, pid))) % (10**8):08d}"
        rows.append([
            rid,
            "CN",
            cn_partner,
            "project",
            "",
            1 if n <= 2 else 2 if n <= 5 else 3,  # intensity bucket
            "two-way",
            "",
            "",
            "",
            "M",
            f"CORDIS co-participation n={n}",
            ""
        ])
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    args = ap.parse_args()

    processed = processed_path(args.country, "relationships.csv")
    headers = SCHEMAS["relationships.csv"]

    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=cordis") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No CORDIS raw for {args.country}; wrote empty relationships.csv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    rows = normalize(args.country.upper(), raw_dir)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")