# src/normalize/policy_ingest.py
"""
Policy Ingest (stub) — append-only, idempotent normalizer for narrative sources.

Reads per-document TSVs created by LLM prompts from:
  data/raw/source=policy_docs/country=<ISO2>/date=YYYY-MM-DD/
    - *_snapshot.tsv  (1 row / doc; schema: policy_corpus.tsv)
    - *_claims.tsv    (0..N rows; schema: policy_assertions.tsv)
    - *_quotes.tsv    (0..N rows; schema: policy_quotes.tsv)

Writes/updates processed tables:
  data/processed/country=<ISO2>/policy_corpus.tsv
  data/processed/country=<ISO2>/policy_assertions.tsv
  data/processed/country=<ISO2>/policy_quotes.tsv

De-duplication:
  - corpus: by source_id
  - assertions: by (source_id, claim_id)
  - quotes: by (source_id, page, quote)

Safe behavior:
  - If no raw files exist, writes headers if missing and exits 0.
  - Tolerant to blank lines and missing files.

Usage:
  python -m src.normalize.policy_ingest --country SE
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from typing import Dict, Tuple, Set

CORPUS_HEADERS = [
    "source_id","title","issuer","issuer_level","pub_date","url","lang","country_scope","policy_domain","sectors","instruments","maturity","stance_prc_mcf","enforcement_tools","time_horizon","review_cycle","credibility_1_5","confidence","summary"
]
ASSERT_HEADERS = [
    "source_id","claim_id","page","paragraph","claim_text","claim_type","sectors","scs_pillars","mechanisms","controls","evidence_refs","confidence"
]
QUOTE_HEADERS = [
    "source_id","page","quote","context","relevance","sectors","scs_pillars"
]


def ensure_table(path: Path, headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f, delimiter='\t').writerow(headers)


def read_tsv_rows(path: Path, headers: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter='\t')
        for r in reader:
            rows.append([r.get(h, "").strip() for h in headers])
    return rows


def append_unique(out_path: Path, headers: list[str], rows: list[list[str]], key_idx: Tuple[int, ...]) -> int:
    # Load existing keys
    existing: Set[Tuple[str, ...]] = set()
    buffered: list[list[str]] = []
    if out_path.exists():
        with out_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter='\t')
            hdr = next(reader, None)
            for r in reader:
                if not r:
                    continue
                k = tuple((r[i] if i < len(r) else "").strip() for i in key_idx)
                existing.add(k)
                buffered.append(r)
    # Append new unique
    added = 0
    for r in rows:
        k = tuple((r[i] if i < len(r) else "").strip() for i in key_idx)
        if k in existing:
            continue
        buffered.append(r)
        existing.add(k)
        added += 1
    # Write back
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(headers)
        w.writerows(buffered)
    return added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    cc = args.country.upper()

    raw_root = Path("data/raw/source=policy_docs") / f"country={cc}"
    date_dirs = sorted(raw_root.glob("date=*"))

    proc_root = Path("data/processed") / f"country={cc}"
    corpus_out = proc_root / "policy_corpus.tsv"
    assert_out = proc_root / "policy_assertions.tsv"
    quote_out  = proc_root / "policy_quotes.tsv"

    ensure_table(corpus_out, CORPUS_HEADERS)
    ensure_table(assert_out, ASSERT_HEADERS)
    ensure_table(quote_out,  QUOTE_HEADERS)

    total_added = {"corpus":0, "assert":0, "quote":0}

    if not date_dirs:
        print(f"No policy_docs raw for {cc}; ensured headers and exiting")
        return

    for d in date_dirs:
        for f in d.iterdir():
            if f.suffix.lower() not in (".tsv",):
                continue
            name = f.name.lower()
            if name.endswith("_snapshot.tsv"):
                rows = read_tsv_rows(f, CORPUS_HEADERS)
                total_added["corpus"] += append_unique(corpus_out, CORPUS_HEADERS, rows, (0,))  # source_id
            elif name.endswith("_claims.tsv"):
                rows = read_tsv_rows(f, ASSERT_HEADERS)
                total_added["assert"] += append_unique(assert_out, ASSERT_HEADERS, rows, (0,1))  # (source_id, claim_id)
            elif name.endswith("_quotes.tsv"):
                rows = read_tsv_rows(f, QUOTE_HEADERS)
                total_added["quote"] += append_unique(quote_out, QUOTE_HEADERS, rows, (0,1,2))  # (source_id,page,quote)

    print(f"Added corpus:{total_added['corpus']} assertions:{total_added['assert']} quotes:{total_added['quote']}")

if __name__ == "__main__":
    main()