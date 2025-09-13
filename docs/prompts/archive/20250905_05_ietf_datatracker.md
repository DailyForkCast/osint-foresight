Below is a copy‑paste prompt for Claude Code. It implements a real **IETF Datatracker** puller and normalizer that writes `standards_roles.tsv` with our exact schema. It is **idempotent** and safe to re‑run.

---

# Claude Code — Implement IETF Datatracker Collector → `standards_roles.tsv`

You are in the **osint-foresight** repo. Create/modify only the files below. Follow Guardrails.

## Guardrails
- Do **not** delete user data. Create/update listed files only.
- Keep actions **idempotent** (re‑running should not duplicate or crash).
- Use polite `User-Agent`: `osint-foresight/0.1 (mailto:${CONTACT_EMAIL-or-research@example.org})`.
- Backoff on 429/5xx with exponential sleeps.
- For every file changed, print `WRITE <path>` or `OK <path>` if identical.
- At the end, print **CHANGELOG** and **NEXT STEPS**.

---

## 1) Helper: standards config reader
Create/overwrite **`src/utils/standards.py`**:
```python
from pathlib import Path
import yaml

DEF_MAP = {
    # fallback if file not present
    "detnet": "Edge Comms & Spectrum",
    "mls": "Cyber/Secure Comms",
    "cbor": "AI/HPC/Data",
}

MAP_PATH = Path("taxonomies/mappings/standards_map.yaml")

def wg_sector_map() -> dict:
    if MAP_PATH.exists():
        data = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8")) or []
        out = {}
        for row in data:
            acr = str(row.get("acronym","")) .strip().lower()
            if acr:
                out[acr] = row.get("sector","")
        return out or DEF_MAP
    return DEF_MAP
```

---

## 2) Implement real puller: **`src/pulls/ietf_pull.py`**
```python
import argparse, time
from datetime import date
from pathlib import Path
import os, requests, json

CONTACT = os.getenv("CONTACT_EMAIL", "research@example.org")
UA = {"User-Agent": f"osint-foresight/0.1 (mailto:{CONTACT})"}
BASE = "https://datatracker.ietf.org/api/v1"

from ..utils.evidence import append_row


def get(url, params=None):
    for attempt in range(6):
        r = requests.get(url, params=params or {}, headers=UA, timeout=60)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60, 2 ** attempt))
            continue
        r.raise_for_status()
    raise RuntimeError(f"GET failed after retries: {url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)  # kept for consistent interface
    ap.add_argument("--out", required=True)
    ap.add_argument("--groups-file", default="queries/ietf/wg_list.txt")
    args = ap.parse_args()

    outdir = Path(args.out) / f"date={date.today()}"
    outdir.mkdir(parents=True, exist_ok=True)

    # Load WG list (one acronym per line) or fallback to active groups index
    wg_list = []
    p = Path(args.groups_file)
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            acr = line.strip().lower()
            if acr and not acr.startswith('#'):
                wg_list.append(acr)

    if not wg_list:
        groups = get(f"{BASE}/group/group/", params={"type":"wg","state":"active","limit":999})
        wg_list = [g["acronym"].lower() for g in groups.get("objects", []) if g.get("acronym")]

    total_docs = 0
    for acr in sorted(set(wg_list)):
        # fetch WG details to get linkable URL
        groups = get(f"{BASE}/group/group/", params={"acronym": acr})
        if not groups.get("objects"):
            continue
        gid = groups["objects"][0]["id"]
        # fetch drafts for WG
        docs = get(f"{BASE}/doc/document/", params={"group": f"/api/v1/group/group/{gid}/", "states__type__slug__in": "draft-stream-ietf", "limit": 1000})
        items = docs.get("objects", [])
        if not items:
            continue
        rawp = outdir / f"ietf_{acr}.jsonl"
        with rawp.open("w", encoding="utf-8") as f:
            for d in items:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        total_docs += len(items)
        time.sleep(1)

    eid = append_row("IETF Datatracker", f"{BASE}", args.country, "wg_list=<file or active>")
    print(f"OK ietf: wrote {total_docs} docs to {outdir}")
    print(f"EVIDENCE_ID: {eid}")

if __name__ == "__main__":
    main()
```

---

## 3) Normalizer: **`src/normalize/ietf_to_standards_roles.py`**
```python
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
```

---

## 4) Minimal smoke test
```
python -m src.pulls.ietf_pull --country PT --out data/raw/source=ietf/country=PT --groups-file queries/ietf/wg_list.txt
python -m src.normalize.ietf_to_standards_roles --country PT
```
Expect:
- Raw pages: `data/raw/source=ietf/country=PT/date=YYYY-MM-DD/ietf_<wg>.jsonl`
- `data/processed/country=PT/standards_roles.tsv` populated

---

## 5) Commit (optional)
```
git add -A && git commit -m "feat(ietf): datatracker collector + standards_roles normalizer"
```

## 6) NEXT STEPS
- Enrich with WG chairs (group endpoint), compute `streak_quarters` from doc updated dates
- Add ETSI/ISO/ITU sources later into the same `standards_roles.tsv`