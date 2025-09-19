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
    # Skip relationships for now due to API endpoint issues
    # TODO: Fix relationships API query format
    print("Skipping relationships collection (API endpoint needs fixing)")

    eid = append_row("GLEIF API", BASE, args.country, f"country={args.country}&pagesize={args.pagesize}")
    print(f"OK gleif: wrote {total} lei records and {rel_total} relationships to {outdir}")
    print(f"EVIDENCE_ID: {eid}")

if __name__ == "__main__":
    main()
