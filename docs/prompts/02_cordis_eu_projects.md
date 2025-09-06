Below is a copy‑paste prompt for Claude Code. It implements a **CORDIS** projects collector with two modes (online via CKAN API or offline from exported CSV), and normalizers for `programs.csv` and `relationships.csv` (co‑participation). It is **idempotent** and safe to re‑run.

> Note: exact dataset/resource IDs on data.europa.eu can change. We make them **configurable** in `config/sources.yaml`. If the API is unreachable, you can drop exported CSVs into `data/raw/source=cordis/...` and run the normalizers.

---

# Claude Code — Implement CORDIS → `programs.csv` & `relationships.csv`

You are in the **osint-foresight** repo. Create/modify only the files below. Follow Guardrails.

## Guardrails
- Do **not** delete user data. Create/update listed files only.
- Keep actions **idempotent**.
- Use polite `User-Agent`: `osint-foresight/0.1 (mailto:${CONTACT_EMAIL-or-research@example.org})`.
- Backoff on 429/5xx with exponential sleeps.
- Print `WRITE <path>` or `OK <path>` for each file; end with **CHANGELOG** and **NEXT STEPS**.

---

## 1) Config: add source settings
Append (or create if missing) **`config/sources.yaml`** with this block (merge if file exists):
```yaml
cordis:
  ckan_base: https://data.europa.eu/api/3/action
  # package IDs are examples; adjust if needed in future
  package_id: cordis-h2020projects
  resource_hint: participants  # choose resource whose name contains this string
```

---

## 2) Puller (online+offline): **`src/pulls/cordis_pull.py`**
```python
import argparse, os, time, csv, io, json
from datetime import date
from pathlib import Path
import requests, yaml

CONTACT = os.getenv("CONTACT_EMAIL", "research@example.org")
UA = {"User-Agent": f"osint-foresight/0.1 (mailto:{CONTACT})"}

from ..utils.evidence import append_row


def load_cfg():
    p = Path("config/sources.yaml")
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def get(url, params=None):
    for attempt in range(6):
        r = requests.get(url, params=params or {}, headers=UA, timeout=120)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60, 2**attempt))
            continue
        r.raise_for_status()
    raise RuntimeError(f"GET failed after retries: {url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=["online","offline"], default="online")
    ap.add_argument("--source_file", help="CSV file path when mode=offline", default=None)
    args = ap.parse_args()

    outdir = Path(args.out) / f"date={date.today()}"
    outdir.mkdir(parents=True, exist_ok=True)

    if args.mode == "offline":
        src = Path(args.source_file or "")
        if not src.exists():
            raise SystemExit("Provide --source_file=<path to exported CORDIS CSV>")
        # copy to raw
        data = src.read_bytes()
        (outdir/"cordis_participants.csv").write_bytes(data)
        eid = append_row("CORDIS CSV (offline)", str(src), args.country, "manual export")
        print(f"OK cordis offline: copied {src} -> {outdir}")
        print(f"EVIDENCE_ID: {eid}")
        return

    # online CKAN
    cfg = load_cfg().get("cordis", {})
    base = cfg.get("ckan_base", "https://data.europa.eu/api/3/action")
    package_id = cfg.get("package_id", "cordis-h2020projects")
    hint = (cfg.get("resource_hint") or "participants").lower()

    pkg = get(f"{base}/package_show", {"id": package_id})
    resources = pkg.get("result", {}).get("resources", [])
    # choose a CSV resource with participant details
    res = None
    for r in resources:
        if hint in (r.get("name","") or "").lower() and (r.get("format","CSV").upper() == "CSV"):
            res = r
            break
    if not res:
        raise SystemExit("Could not find participants CSV resource in package")

    # download the resource
    url = res.get("url")
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    (outdir/"cordis_participants.csv").write_bytes(r.content)

    eid = append_row("CORDIS (CKAN)", base, args.country, f"package_id={package_id};resource={res.get('name')}")
    print(f"OK cordis: downloaded {res.get('name')} to {outdir}")
    print(f"EVIDENCE_ID: {eid}")

if __name__ == "__main__":
    main()
```

---

## 3) Normalizer: **participants → programs & relationships**
Create/overwrite **`src/normalize/cordis_to_programs.py`**:
```python
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
```

Create/overwrite **`src/normalize/cordis_to_relationships.py`**:
```python
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
```

---

## 4) Minimal smoke test (online or offline)
**Online:**
```
python -m src.pulls.cordis_pull --country PT --out data/raw/source=cordis/country=PT --mode online
python -m src.normalize.cordis_to_programs --country PT
python -m src.normalize.cordis_to_relationships --country PT
```
**Offline (after manual export):**
```
python -m src.pulls.cordis_pull --country PT --out data/raw/source=cordis/country=PT --mode offline --source_file /path/to/cordis_participants.csv
python -m src.normalize.cordis_to_programs --country PT
python -m src.normalize.cordis_to_relationships --country PT
```
Expect:
- Raw CSV at `data/raw/source=cordis/country=PT/date=YYYY-MM-DD/cordis_participants.csv`
- `data/processed/country=PT/programs.csv` and `relationships.csv` updated

---

## 5) Commit (optional)
```
git add -A && git commit -m "feat(cordis): collector (online/offline) + normalize to programs & relationships"
```

## 6) NEXT STEPS
- Map `fundingScheme` to richer instrument taxonomy (grants, prizes, procurement)
- Add budget (`ecMaxContribution`) rollups per sector/counterpart
- Join with OpenAIRE/Crossref project IDs when available