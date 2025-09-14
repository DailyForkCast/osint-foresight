# src/analysis/phase4_supply_chain.py
from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Dict

try:
    import pandas as pd
except Exception:
    print("ERROR: pandas is required. Try `pip install -r requirements.txt`.")
    raise

from src.utils.reporting import ensure_template

PILLAR_ORDER = ["Knowledge", "Technology", "Materials", "Finance", "Logistics"]

# Collab type → pillar(s) heuristic (extendable)
COLLAB_TO_PILLARS: Dict[str, List[str]] = {
    "co-publication": ["Knowledge"],
    "co-project": ["Knowledge", "Technology"],
    "infrastructure": ["Technology", "Logistics"],
    "procurement": ["Logistics", "Finance"],
    "investment": ["Finance"],
    "licensing": ["Technology", "Finance"],
    "training": ["Knowledge"],
    "workshop": ["Knowledge"],
}


def _read_any(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    # Try CSV, then TSV
    for sep in [",", "\t"]:
        try:
            return pd.read_csv(path, sep=sep)
        except Exception:
            continue
    return pd.DataFrame()


def _present(df: pd.DataFrame) -> str:
    return f"yes (rows={len(df)})" if not df.empty else "no"


def _norm(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="ISO2 e.g. AT")
    ap.add_argument("--out", default=None, help="Override output path")
    args = ap.parse_args()

    cc = args.country.upper()
    ensure_template(cc, "phase-4_supply_chain.md")

    base = Path("data/processed") / f"country={cc}"
    rel = _norm(_read_any(base / "relationships.csv"))
    mech = _norm(_read_any(base / "mechanism_incidents.tsv"))
    sanc = _norm(_read_any(base / "sanctions_hits.csv"))
    cer = _norm(_read_any(base / "cer_master.csv"))

    # Year filter for relationships
    if not rel.empty and "year" in rel.columns:
        rel["year"] = pd.to_numeric(rel["year"], errors="coerce")
        rel = rel[(rel["year"] >= 2015) & (rel["year"] <= 2025)]

    # Column presence defaults
    for col in ["sector", "counterpart_name", "counterpart_country", "collab_type"]:
        if col not in rel.columns and not rel.empty:
            rel[col] = None

    # Pillar expansion
    def map_pillars(s: str) -> List[str]:
        if not isinstance(s, str):
            return ["Knowledge"]  # conservative default
        s2 = s.strip().lower()
        return COLLAB_TO_PILLARS.get(s2, ["Knowledge"])  # default Knowledge

    # Compute per-sector metrics
    sectors = sorted(rel["sector"].dropna().unique().tolist()) if not rel.empty and "sector" in rel.columns else []

    # Pillar counts per sector
    pillar_rows = []
    if sectors:
        for sec in sectors:
            sub = rel[rel["sector"] == sec]
            counts = {p: 0 for p in PILLAR_ORDER}
            for _, r in sub.iterrows():
                for p in map_pillars(r.get("collab_type", "")):
                    counts[p] = counts.get(p, 0) + 1
            pillar_rows.append([sec] + [counts[p] for p in PILLAR_ORDER])

    # PRC exposure
    prc_rows = []
    if sectors:
        for sec in sectors:
            sub = rel[rel["sector"] == sec]
            tot = len(sub)
            cn = len(sub[(sub.get("counterpart_country") == "CN")]) if tot else 0
            share = (cn / tot) if tot else 0.0
            # Top PRC counterparts (2 max)
            tops = "–"
            if cn > 0:
                g = sub[sub["counterpart_country"] == "CN"].groupby("counterpart_name").size().sort_values(ascending=False)
                tops = ", ".join(g.head(2).index.tolist()) if not g.empty else "–"
            prc_rows.append([sec, str(cn), f"{share:.2f}", tops])

    # Sanctions overlay (exact‑match on name)
    sanc_rows = []
    sanc_names = set()
    if not sanc.empty and "name" in sanc.columns:
        sanc_names = set(sanc["name"].dropna().str.lower().unique())
    if sectors and sanc_names:
        for sec in sectors:
            sub = rel[rel["sector"] == sec]
            hits = 0
            for nm in sub.get("counterpart_name", pd.Series(dtype=str)).dropna().str.lower().tolist():
                if nm in sanc_names:
                    hits += 1
            sanc_rows.append([sec, str(hits)])

    # Mechanisms summary
    mech_table = []
    if not mech.empty and {"sector", "mechanism_family"}.issubset(mech.columns):
        m = mech.groupby(["sector", "mechanism_family"]).size().rename("n").reset_index()
        # take top 2 families per sector
        for sec in sorted(m["sector"].dropna().unique().tolist()):
            top = m[m["sector"] == sec].sort_values("n", ascending=False).head(2)
            for _, r in top.iterrows():
                mech_table.append([sec, r["mechanism_family"], str(int(r["n"]))])

    # Build markdown
    out = []
    out.append("---")
    out.append("title: \"Phase 4 — Supply Chain Security (Austria)\"")
    out.append("author: Analyst")
    out.append("date: \"<AUTO>\"")
    out.append("---\n")

    out.append("## Data presence")
    out.append(f"- relationships.csv: {_present(rel)}")
    out.append(f"- mechanism_incidents.tsv: {_present(mech)}")
    out.append(f"- sanctions_hits.csv: {_present(sanc)}")
    out.append(f"- cer_master.csv: {_present(cer)}\n")

    out.append("## Sector Exposure Summary")
    out.append("| Sector | K | T | M | F | L | PRC edges | PRC share | Top PRC counterpart(s) |")
    out.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    if pillar_rows:
        # join with PRC rows by sector
        prc_map = {r[0]: r[1:] for r in prc_rows}
        for row in pillar_rows:
            sec, k, t, m, f, l = row[0], row[1], row[2], row[3], row[4], row[5]
            prc_vals = prc_map.get(sec, ["0", "0.00", "–"])  # cn, share, tops
            out.append(f"| {sec} | {k} | {t} | {m} | {f} | {l} | {prc_vals[0]} | {prc_vals[1]} | {prc_vals[2]} |")
    else:
        out.append("| – | – | – | – | – | – | – | – | – |")

    out.append("\n**Pillars:** K=Knowledge, T=Technology, M=Materials, F=Finance, L=Logistics. Collab→pillar mapping is heuristic and conservative by default.")

    out.append("\n## Sanctions Overlay (optional)")
    out.append("| Sector | Sanctioned counterpart hits |")
    out.append("|---|---:|")
    if sanc_rows:
        for sec, hits in sanc_rows:
            out.append(f"| {sec} | {hits} |")
    else:
        out.append("| – | – |")

    out.append("\n## Mechanism Signals (if available)")
    out.append("| Sector | Mechanism family | Count |")
    out.append("|---|---|---:|")
    if mech_table:
        for sec, fam, n in mech_table:
            out.append(f"| {sec} | {fam} | {n} |")
    else:
        out.append("| – | – | – |")

    # Short narrative
    bullets = []
    if pillar_rows:
        bullets.append("HPC likely shows T+L activity via infrastructure edges; validate with procurement or facility logistics where possible.")
    if prc_rows and any(float(r[2]) > 0 for r in prc_rows):
        bullets.append("PRC exposure detected in at least one sector; apply CER‑lite before escalating any claims.")
    if sanc_rows:
        bullets.append("Sanctions overlay shows matches in some sectors; treat these as **red flags**, not dispositive proof of risk.")
    if not bullets:
        bullets.append("Current results are based on limited seeds; add one CSV (CORDIS participants or procurement) to improve fidelity.")

    out.append("\n## Narrative Snapshot")
    for b in bullets[:4]:
        out.append(f"- {b}")

    out.append("\n## Next Data Boost (one actionable)")
    out.append("Add a **procurement/tenders** CSV (2019–2025) with columns `buyer, supplier, item, date, value, sector_hint` to `data/raw/source=procurement/country=%s/date=<YYYY-MM-DD>/tenders.csv`, then run `make normalize-all COUNTRY=%s` and rebuild." % (cc, cc))

    # Write
    out_path = Path(args.out) if args.out else Path("reports") / f"country={cc}" / "phase-4_supply_chain.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"WRITE {out_path}")


if __name__ == "__main__":
    main()
