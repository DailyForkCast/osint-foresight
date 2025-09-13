Below is a copy‑paste prompt for Claude Code. It implements a real **GLEIF** puller and normalizer to update `cer_master.csv` and `institutions.csv`. It is **idempotent** and safe to re‑run.

---

# Claude Code — Implement GLEIF → `cer_master.csv` & `institutions.csv`

You are in the **osint-foresight** repo. Create/modify only the files below. Follow Guardrails.

## Guardrails
- Do **not** delete user data. Create/update listed files only.
- Keep actions **idempotent** (re‑running should not duplicate or crash).
- Use polite `User-Agent`: `osint-foresight/0.1 (mailto:${CONTACT_EMAIL-or-research@example.org})`.
- Backoff on 429/5xx with exponential sleeps.
- For every file changed, print `WRITE <path>` or `OK <path>` if identical.
- At the end, print **CHANGELOG** and **NEXT STEPS**.

---

## 1) Implement puller: **`src/pulls/gleif_pull.py`**
```python
import argparse, time
from datetime import date
from pathlib import Path
import os, requests, json

CONTACT = os.getenv("CONTACT_EMAIL", "research@example.org")
UA = {"User-Agent": f"osint-foresight/0.1 (mailto:{CONTACT})"}
BASE = "https://api.gleif.org/api/v1"

from ..utils.evidence import append_row


def get(path, params=None):
    url = f"{BASE}/{path.lstrip('/')}"
    for attempt in range(6):
        r = requests.get(url, params=params or {}, headers=UA, timeout=60)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429,500,502,503,504):
            time.sleep(min(60,2**attempt))
            continue
        r.raise_for_status()
    raise RuntimeError(f"GET failed after retries: {url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pagesize", type=int, default=200)
    ap.add_argument("--max_pages", type=int, default=200)
    args = ap.parse_args()

    outdir = Path(args.out) / f"date={date.today()}"
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) LEI records by country
    page = 1
    total = 0
    while page <= args.max_pages:
        params = {
            "filter[entity.legalAddress.country]": args.country.upper(),
            "page[number]": page,
            "page[size]": args.pagesize,
        }
        data = get("lei-records", params)
        items = data.get("data", [])
        if not items:
            break
        path = outdir / f"gleif_leis_p{page:04d}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        total += len(items)
        page += 1
        time.sleep(1)

    # 2) Optionally fetch relationships (parents/children) for first N LEIs
    rel_total = 0
    first_page = outdir / "gleif_leis_p0001.jsonl"
    leis = []
    if first_page.exists():
        for line in first_page.read_text(encoding="utf-8").splitlines():
            try:
                it = json.loads(line)
            except Exception:
                continue
            lei = (it.get("id") or "").strip()
            if lei:
                leis.append(lei)
            if len(leis) >= 200:
                break
    if leis:
        rel = get("relationships", {"filter[relationship.startNode.lei][:in]": ",".join(leis), "page[size]": 200})
        path = outdir / "gleif_relationships.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for it in rel.get("data", []) or []:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        rel_total = len(rel.get("data", []))

    eid = append_row("GLEIF API", BASE, args.country, f"country={args.country}&pagesize={args.pagesize}")
    print(f"OK gleif: wrote {total} lei records and {rel_total} relationships to {outdir}")
    print(f"EVIDENCE_ID: {eid}")

if __name__ == "__main__":
    main()
```

---

## 2) Normalizer: **`src/normalize/gleif_to_cer.py`**
```python
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
```

---

## 3) Minimal smoke test
```
python -m src.pulls.gleif_pull --country PT --out data/raw/source=gleif/country=PT --pagesize 100
python -m src.normalize.gleif_to_cer --country PT
```
Expect:
- Raw JSONL pages under `data/raw/source=gleif/country=PT/date=YYYY-MM-DD/`
- `data/processed/country=PT/cer_master.csv` and `institutions.csv` populated (identity fields)

---

## 4) Commit (optional)
```
git add -A && git commit -m "feat(gleif): pull LEIs + normalize to cer_master & institutions"
```

## 5) NEXT STEPS
- Enrich `institutions.csv` with accreditation fields from national AB CSVs
- Merge with ROR for universities (name/country join)
- Use `relationships` endpoint to add `ownership_notes` to institutions