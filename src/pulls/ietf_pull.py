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