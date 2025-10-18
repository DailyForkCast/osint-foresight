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
