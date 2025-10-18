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
