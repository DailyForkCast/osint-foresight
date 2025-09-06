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