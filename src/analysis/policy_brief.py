# src/analysis/policy_brief.py
"""
Policy Brief (stub) — turns policy_corpus.tsv + policy_assertions.tsv into a 1-page brief.
- Renders even if inputs are missing (writes a minimal scaffold).
- Outputs: reports/country=<ISO2>/policy_brief.md

Sections:
  - Headline sources (top by credibility_1_5 then recency)
  - Mechanisms & controls (5 bullets from assertions)
  - Specificity table (sector -> specificity contribution 0–5 from corpus domain/sectors)

Usage:
  python -m src.analysis.policy_brief --country SE
"""
from __future__ import annotations
import argparse, csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from src.utils.reporting import ensure_template

CORPUS_HEADERS = [
    "source_id","title","issuer","issuer_level","pub_date","url","lang","country_scope","policy_domain","sectors","instruments","maturity","stance_prc_mcf","enforcement_tools","time_horizon","review_cycle","credibility_1_5","confidence","summary"
]
ASSERT_HEADERS = [
    "source_id","claim_id","page","paragraph","claim_text","claim_type","sectors","scs_pillars","mechanisms","controls","evidence_refs","confidence"
]


def read_tsv(path: Path, headers: List[str]) -> List[Dict[str,str]]:
    if not path.exists():
        return []
    rows: List[Dict[str,str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter='\t')
        for r in reader:
            rows.append({h: (r.get(h, "") or "").strip() for h in headers})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    cc = args.country.upper()
    ensure_template(cc, "policy_brief.md")

    proc = Path("data/processed") / f"country={cc}"
    out = Path("reports") / f"country={cc}" / "policy_brief.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    corpus = read_tsv(proc / "policy_corpus.tsv", CORPUS_HEADERS)
    asserts = read_tsv(proc / "policy_assertions.tsv", ASSERT_HEADERS)

    # Top sources by (credibility desc, pub_date desc)
    def parse_date(s: str) -> datetime:
        for fmt in ("%Y-%m-%d","%Y/%m/%d","%Y-%m","%Y/%m","%Y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        return datetime.min

    corpus_sorted = sorted(
        corpus,
        key=lambda r: (int(r.get("credibility_1_5", "0") or 0), parse_date(r.get("pub_date",""))),
        reverse=True,
    )[:10]

    # Mechanisms & controls bullets
    bullets: List[str] = []
    for r in asserts:
        if r.get("claim_type","") in ("mechanism","control","restriction","standardization","funding"):
            txt = r.get("claim_text","")
            sec = r.get("sectors","")
            pil = r.get("scs_pillars","")
            bullets.append(f"- {txt} — sectors: {sec or '-'}; pillars: {pil or '-'}")
        if len(bullets) >= 5:
            break

    # Specificity table (very simple heuristic): if sectors present in corpus rows, add +1 up to max 5
    spec: Dict[str,int] = {}
    for r in corpus:
        sectors = [s.strip() for s in (r.get("sectors","") or "").split(",") if s.strip()]
        for s in sectors:
            spec[s] = min(5, spec.get(s,0) + 1)

    # Render markdown
    lines: List[str] = []
    lines.append("---")
    lines.append(f"title: Policy Brief ({cc})")
    lines.append("author: Analyst")
    lines.append("---\n")

    lines.append("## Headline Sources (Top by credibility/recency)")
    if corpus_sorted:
        lines.append("| Cred | Date | Title | Issuer | URL |")
        lines.append("|---:|---|---|---|---|")
        for r in corpus_sorted:
            lines.append(f"| {r.get('credibility_1_5','')} | {r.get('pub_date','')} | {r.get('title','')} | {r.get('issuer','')} | {r.get('url','')} |")
    else:
        lines.append("(none)")

    lines.append("\n## Mechanisms & Controls (sample)")
    if bullets:
        lines.extend(bullets)
    else:
        lines.append("- (no assertions ingested yet)")

    lines.append("\n## Specificity Contribution (quick heuristic)")
    if spec:
        lines.append("| Sector | Specificity (0–5) |")
        lines.append("|---|---:|")
        for s, v in sorted(spec.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"| {s} | {v} |")
    else:
        lines.append("(no sector tags in corpus)")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"WROTE {out}")

if __name__ == "__main__":
    main()