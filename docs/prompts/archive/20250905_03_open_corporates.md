Below is a copy‑paste prompt for Claude Code. It implements an **OpenCorporates** collector and normalizer to write `mechanism_incidents.tsv` (JV/equity/officer/board signals). It is **idempotent** and safe to re‑run.

---

# Claude Code — Implement OpenCorporates → `mechanism_incidents.tsv`

You are in the **osint-foresight** repo. Create/modify only the files below. Follow Guardrails.

## Guardrails
- Do **not** delete user data.
- Keep actions **idempotent**.
- Use polite `User-Agent`: `osint-foresight/0.1 (mailto:${CONTACT_EMAIL-or-research@example.org})`.
- Respect API token env var: `OPENCORP_TOKEN` (read from environment).
- Backoff on 429/5xx with exponential sleeps.
- Print `WRITE <path>` or `OK <path>` for each file; end with **CHANGELOG** and **NEXT STEPS**.

---

## 1) Puller: **`src/pulls/opencorporates_pull.py`**
```python
import argparse, os, time, json
from datetime import date
from pathlib import Path
import requests, yaml

CONTACT = os.getenv("CONTACT_EMAIL", "research@example.org")
UA = {"User-Agent": f"osint-foresight/0.1 (mailto:{CONTACT})"}
BASE = "https://api.opencorporates.com/v0.4"
TOKEN = os.getenv("OPENCORP_TOKEN", "")

from ..utils.evidence import append_row


def get(path, params=None):
    url = f"{BASE}/{path.lstrip('/')}"
    params = params or {}
    if TOKEN and "api_token" not in params:
        params["api_token"] = TOKEN
    for attempt in range(6):
        r = requests.get(url, params=params, headers=UA, timeout=60)
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
    ap.add_argument("--keywords-file", default="taxonomies/keywords_multilingual.yaml")
    ap.add_argument("--per_page", type=int, default=100)
    args = ap.parse_args()

    outdir = Path(args.out) / f"date={date.today()}"
    outdir.mkdir(parents=True, exist_ok=True)

    # simple keyword expansion (english only for now)
    kws = []
    if Path(args.keywords_file).exists():
        data = yaml.safe_load(Path(args.keywords_file).read_text(encoding="utf-8")) or {}
        for sect, langs in (data.get("sectors", {})).items():
            kws += (langs or {}).get("en", [])
    if not kws:
        kws = ["semiconductor","robotics","satellite","AI","HPC"]

    total = 0
    for kw in sorted(set(kws)):
        params = {"q": kw, "country_code": args.country.upper(), "per_page": args.per_page}
        data = get("companies/search", params)
        comps = (data or {}).get("results", {}).get("companies", [])
        if not comps:
            continue
        rawp = outdir / f"opencorporates_{kw}.jsonl"
        with rawp.open("w", encoding="utf-8") as f:
            for c in comps:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        total += len(comps)
        time.sleep(1)

    eid = append_row("OpenCorporates API", BASE, args.country, f"keyword_count={len(kws)}")
    print(f"OK opencorporates: wrote {total} companies to {outdir}")
    print(f"EVIDENCE_ID: {eid}")

if __name__ == "__main__":
    main()
```

---

## 2) Normalizer: **`src/normalize/opencorp_to_mechanisms.py`**
```python
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
```

---

## 3) Minimal smoke test
```
python -m src.pulls.opencorporates_pull --country PT --out data/raw/source=opencorporates/country=PT
python -m src.normalize.opencorp_to_mechanisms --country PT
```
Expect:
- Raw JSONL keyword pages under `data/raw/source=opencorporates/country=PT/date=YYYY-MM-DD/`
- `data/processed/country=PT/mechanism_incidents.tsv` with heuristic CN-linked incidents

---

## 4) Commit (optional)
```
git add -A && git commit -m "feat(opencorporates): collector + normalize to mechanism_incidents"
```

## 5) NEXT STEPS
- Add officers search (`/officers/search`) and parse **board_rights** from titles (Director, Chair)
- Detect **JV/equity** via filings or groupings if available; enrich with registry IDs
- Deduplicate into incidents and increase `confidence_0to1` when corroborated
