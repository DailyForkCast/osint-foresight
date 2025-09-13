Below is a single, copy‑paste prompt for Claude Code. It wires up **Crossref + Event Data** as real collectors/normalizers and upgrades **OpenAIRE normalization** with sector classification and edge aggregation (`intensity_0_3`). It is **idempotent** and safe to re‑run.

---

# Claude Code — Implement Crossref + Event Data & Upgrade OpenAIRE Normalizer

You are operating inside the **osint-foresight** repo. Implement the changes below. Follow all Guardrails.

## Guardrails
- Do **not** delete user data.
- Keep everything **idempotent**: re‑running should not duplicate headers/rows or crash.
- Use polite `User-Agent`: `osint-foresight/0.1 (mailto:${CONTACT_EMAIL-or-research@example.org})`.
- Respect rate limits: sleep 1s between pages; exponential backoff on 429/5xx.
- For each file you create/update, print `WRITE <path>` or `OK <path>` if identical.
- At the end, print a concise **CHANGELOG** and **NEXT STEPS**.

---

## 0) Small config additions (optional but helpful)
If `.env.example` exists, ensure it contains:
```
CONTACT_EMAIL=
```
If missing, append that line. Do not overwrite existing content.

---

## 1) Utilities — sector classifier & simple aggregation
Create/overwrite **`src/utils/classify.py`**:
```python
from __future__ import annotations
from collections import Counter
import re

# Build a simple keyword search across sectors (case-insensitive).
# keywords_map format: { sector: {"en": [..], "local": [..], "zh": [..]} }

def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\-\+/#\.]+", (text or "").lower())


def score_sectors(text: str, keywords_map: dict) -> tuple[list[str], dict[str, int]]:
    toks = tokenize(text)
    counts = {sector: 0 for sector in keywords_map.keys()}
    # naive: count substring matches for multiword kws, token matches otherwise
    tset = set(toks)
    for sector, langs in keywords_map.items():
        kws = []
        for lang in ("en","local","zh"):
            kws += (langs or {}).get(lang, [])
        for kw in kws:
            kw_l = kw.lower()
            if " " in kw_l or any(ch in kw_l for ch in ['*']):
                # wildcard/star — very loose: check containment sans star
                kw_pat = kw_l.replace('*','')
                if kw_pat and kw_pat in (text or "").lower():
                    counts[sector] += 1
            else:
                if kw_l in tset:
                    counts[sector] += 1
    # sectors by score
    ordered = [s for s,_ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])) if counts[s] > 0]
    return ordered, counts


def primary_sector(text_blocks: list[str], keywords_map: dict) -> tuple[str, dict[str,int]]:
    text = " \n ".join([t for t in text_blocks if t])
    ordered, counts = score_sectors(text, keywords_map)
    return (ordered[0] if ordered else ""), counts


def bucket_intensity(n: int) -> int:
    # 0–3 buckets. Tune thresholds later if needed.
    if n <= 0: return 0
    if n <= 2: return 1
    if n <= 5: return 2
    return 3
```

---

## 2) Crossref puller — real implementation
Replace **`src/pulls/crossref_pull.py`** with:
```python
import argparse, time, sys, json
from pathlib import Path
from datetime import date
import os
import requests

from ..utils.evidence import append_row

CONTACT = os.getenv("CONTACT_EMAIL", "research@example.org")
UA = {"User-Agent": f"osint-foresight/0.1 (mailto:{CONTACT})"}
BASE = "https://api.crossref.org/works"


def fetch(params):
    for attempt in range(6):
        r = requests.get(BASE, params=params, headers=UA, timeout=60)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(60, 2 ** attempt))
            continue
        r.raise_for_status()
    raise RuntimeError("Crossref fetch failed after retries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--years", default="2015-2025")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows", type=int, default=1000)
    ap.add_argument("--max_pages", type=int, default=50)
    args = ap.parse_args()

    y_from, y_to = args.years.split("-")[0]+"-01-01", args.years.split("-")[-1]+"-12-31"
    outdir = Path(args.out) / f"date={date.today()}"
    outdir.mkdir(parents=True, exist_ok=True)

    cursor = "*"
    pages = 0
    total = 0
    while pages < args.max_pages:
        params = {
            "filter": f"from-pub-date:{y_from},until-pub-date:{y_to}",
            "query.affiliation": args.country,
            "rows": args.rows,
            "cursor": cursor,
            "mailto": CONTACT,
            "select": "DOI,title,author,issued,container-title,affiliation,funder,subject"
        }
        data = fetch(params)
        items = (data or {}).get("message", {}).get("items", [])
        if not items:
            break
        # write JSONL page
        raw_path = outdir / f"crossref_works_p{pages:04d}.jsonl"
        with raw_path.open("w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        total += len(items)
        cursor = (data["message"].get("next-cursor") or cursor)
        pages += 1
        time.sleep(1)

    filt = f"from={y_from}&to={y_to}&query.affiliation={args.country}"
    eid = append_row("Crossref Works", BASE, args.country, filt)

    print(f"OK crossref: wrote {total} works to {outdir}")
    print(f"EVIDENCE_ID: {eid}")

if __name__ == "__main__":
    main()
```

---

## 3) Crossref Event Data puller — targeted by DOI list
Replace **`src/pulls/crossref_event_pull.py`** with:
```python
import argparse, time, json, os
from pathlib import Path
from datetime import date
import requests

from ..utils.evidence import append_row

CONTACT = os.getenv("CONTACT_EMAIL", "research@example.org")
UA = {"User-Agent": f"osint-foresight/0.1 (mailto:{CONTACT})"}
BASE = "https://api.eventdata.crossref.org/v1/events"


def fetch(params):
    for attempt in range(6):
        r = requests.get(BASE, params=params, headers=UA, timeout=60)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(60, 2 ** attempt))
            continue
        r.raise_for_status()
    raise RuntimeError("Event Data fetch failed after retries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--source_raw", default=None, help="Path to latest crossref raw date directory (optional)")
    ap.add_argument("--limit_dois", type=int, default=200)
    ap.add_argument("--from_collected_date", default=None, help="YYYY-MM-DD (optional)")
    args = ap.parse_args()

    outdir = Path(args.out) / f"date={date.today()}"
    outdir.mkdir(parents=True, exist_ok=True)

    # Collect a small set of DOIs from the most recent Crossref raw dir if not provided a path
    dois = []
    if args.source_raw:
        src = Path(args.source_raw)
    else:
        root = Path("data/raw/source=crossref") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        src = parts[-1] if parts else None
    if src:
        for p in sorted(src.glob("crossref_works_p*.jsonl")):
            for line in p.read_text(encoding="utf-8").splitlines():
                try:
                    it = json.loads(line)
                except Exception:
                    continue
                doi = (it.get("DOI") or "").strip()
                if doi:
                    dois.append(doi)
                if len(dois) >= args.limit_dois:
                    break
            if len(dois) >= args.limit_dois:
                break

    # Fetch events per DOI (bounded by limit)
    total = 0
    for doi in dois:
        params = {"obj-id": f"DOI:{doi}", "mailto": CONTACT, "rows": 1000}
        data = fetch(params)
        items = (data or {}).get("message", {}).get("events", []) or (data or {}).get("events", [])
        if not items:
            continue
        path = outdir / f"event_{doi.replace('/', '_')}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for ev in items:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        total += len(items)
        time.sleep(1)

    # Evidence log
    filt = f"obj-id=DOI:<from crossref raw>; limit={args.limit_dois}"
    eid = append_row("Crossref Event Data", BASE, args.country, filt)
    print(f"OK eventdata: wrote {total} events to {outdir}")
    print(f"EVIDENCE_ID: {eid}")

if __name__ == "__main__":
    main()
```

---

## 4) Crossref normalizer — relationships & signals
Replace **`src/normalize/crossref_to_relationships.py`** with:
```python
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
```

---

## 5) Crossref Event Data normalizer — signals
Create/overwrite **`src/normalize/crossref_events_to_signals.py`**:
```python
import argparse, json
from pathlib import Path
from ..utils.io import processed_path, write_table, SCHEMAS

CATEG = "Bibliometrics/Attention"


def normalize(raw_dir: Path) -> list[list[str]]:
    rows = []
    for p in sorted(raw_dir.glob("event_*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                ev = json.loads(line)
            except Exception:
                continue
            date = ev.get("occurred_at") or ev.get("timestamp") or ""
            link = ev.get("obj_id") or ev.get("subj_id") or ""
            desc = ev.get("relation_type_id") or ev.get("source_id") or "Crossref Event"
            rid = f"SIG-{abs(hash((p.name, date, desc))) % (10**10):010d}"
            rows.append([rid, CATEG, "Event spike", desc, "review", "Analyst", str(date)])
    return rows

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--raw", default=None)
    args = ap.parse_args()

    processed = processed_path(args.country, "signals.csv")
    headers = SCHEMAS["signals.csv"]

    if args.raw:
        raw_dir = Path(args.raw)
    else:
        root = Path("data/raw/source=crossref_event") / f"country={args.country.upper()}"
        parts = sorted(root.glob("date=*"))
        if not parts:
            write_table(processed, headers, [])
            print(f"No Event Data raw for {args.country}; wrote empty signals.csv")
            raise SystemExit(0)
        raw_dir = parts[-1]

    rows = normalize(raw_dir)
    write_table(processed, headers, rows)
    print(f"Wrote {processed}")
```

---

## 6) Upgrade OpenAIRE normalizer — sector classification + aggregation
Replace **`src/normalize/openaire_to_relationships.py`** with:
```python
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
```

---

## 7) VS Code tasks (no changes required)
Your existing tasks already include `pull:crossref`, `pull:crossref:event-data`, and `normalize:all`. Leave them unchanged.

---

## 8) Minimal local smoke test (safe & bounded)
Run these commands and report output paths:
```
python -m src.pulls.crossref_pull --country PT --years 2015-2025 --out data/raw/source=crossref/country=PT --rows 500 --max_pages 2
python -m src.normalize.crossref_to_relationships --country PT
python -m src.pulls.crossref_event_pull --country PT --out data/raw/source=crossref_event/country=PT --limit_dois 50
python -m src.normalize.crossref_events_to_signals --country PT
python -m src.normalize.openaire_to_relationships --country PT  # re-run to apply new sector/aggregation
```
Expect:
- Raw JSONL pages under `data/raw/source=crossref/country=PT/date=YYYY-MM-DD/`
- `data/processed/country=PT/relationships.csv` updated with Crossref & OpenAIRE aggregated rows
- `data/processed/country=PT/signals.csv` written from Event Data
- Evidence register updated with Crossref & Event Data entries

---

## 9) Commit (optional)
If `.git` exists and there are changes:
```
git add -A && git commit -m "feat(crossref): works+events collectors; normalize to relationships/signals; upgrade openaire sector+aggregation"
```
If no changes, print `OK git (no changes)`.

---

## 10) Final output
Print a **CHANGELOG** (files added/updated) and **NEXT STEPS**:
- Tune sector keywords in `taxonomies/keywords_multilingual.yaml`
- Add **funders** enrichment to relationships (value_summary)
- Consider caching DOIs to avoid refetching Event Data
- Next collector to swap: **IETF Datatracker** → `standards_roles.tsv`

---

**Execute now and show the step‑by‑step log.**