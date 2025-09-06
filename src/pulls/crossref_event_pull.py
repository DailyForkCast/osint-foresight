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