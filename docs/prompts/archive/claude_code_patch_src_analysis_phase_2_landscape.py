# src/analysis/phase2_landscape.py
from __future__ import annotations
import argparse
from pathlib import Path
import os
import sys
import csv
from typing import List, Tuple

try:
    import pandas as pd
except Exception as e:
    print("ERROR: pandas is required. Try `pip install -r requirements.txt`.")
    raise

from src.utils.reporting import ensure_template  # belt-and-suspenders


def _read_csv(path: Path, **kw) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, **kw)
    except Exception:
        # Try TSV fallback
        try:
            return pd.read_csv(path, sep="\t", **kw)
        except Exception:
            print(f"WARN: failed to read {path}; treating as empty")
            return pd.DataFrame()


def _present(df: pd.DataFrame) -> str:
    return "yes (rows={})".format(len(df)) if not df.empty else "no"


def _intensity_bucket(counts: pd.Series) -> pd.Series:
    # counts is per-sector edge_count. 0 => 0, otherwise quartiles 1..3
    if counts.empty:
        return counts
    nz = counts[counts > 0]
    if nz.empty:
        return counts * 0
    q1 = nz.quantile(0.25)
    q2 = nz.quantile(0.50)
    buckets = pd.Series(0, index=counts.index, dtype=int)
    buckets.loc[nz.index] = 1
    buckets.loc[nz.index & (counts <= q2)] = 2
    buckets.loc[nz.index & (counts <= q1)] = 1
    buckets.loc[nz.index & (counts > q2)] = 3
    return buckets


def _format_momentum(row) -> str:
    return f"{row['b15_18']} / {row['b19_22']} / {row['b23_25']}"


def _md_table(rows: List[List[str]]) -> str:
    if not rows:
        return "| – | – | – | – | – |\n"
    return "\n".join(["| " + " | ".join(r) + " |" for r in rows]) + "\n"


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="ISO2, e.g., AT")
    ap.add_argument("--out", default=None, help="Override output path")
    args = ap.parse_args(argv)

    ccode = args.country.upper()
    # Ensure a template exists, but we will overwrite with computed content
    ensure_template(ccode, "phase-2_landscape.md")

    proc = Path("data/processed") / f"country={ccode}"
    rel_path = proc / "relationships.csv"
    sig_path = proc / "signals.csv"
    std_path = proc / "standards_roles.tsv"
    cer_path = proc / "partners_cerlite.csv"

    rel = _read_csv(rel_path)
    sig = _read_csv(sig_path)
    std = _read_csv(std_path)
    cer = _read_csv(cer_path)

    # Normalize column names
    def normcols(df):
        if df.empty:
            return df
        df.columns = [c.strip().lower() for c in df.columns]
        return df

    rel = normcols(rel)
    sig = normcols(sig)
    std = normcols(std)
    cer = normcols(cer)

    # Filter years to 2015–2025
    if not rel.empty and "year" in rel.columns:
        try:
            rel["year"] = pd.to_numeric(rel["year"], errors="coerce")
            rel = rel[(rel["year"] >= 2015) & (rel["year"] <= 2025)]
        except Exception:
            pass

    # CER-lite join (prefer canon_name if available)
    if not rel.empty and "counterpart_name" in rel.columns and not cer.empty:
        left = rel.copy()
        # Try simple exact join on raw_name==counterpart_name & country==counterpart_country
        if {"raw_name", "canon_name", "country"}.issubset(set(cer.columns)) and "counterpart_country" in left.columns:
            cer_small = cer[["raw_name", "canon_name", "country"]].dropna()
            rel = left.merge(
                cer_small,
                how="left",
                left_on=["counterpart_name", "counterpart_country"],
                right_on=["raw_name", "country"],
            )
            rel["partner_display"] = rel["canon_name"].fillna(rel["counterpart_name"])
        else:
            rel["partner_display"] = rel["counterpart_name"]
    elif not rel.empty and "counterpart_name" in rel.columns:
        rel["partner_display"] = rel["counterpart_name"]

    # Compute sector counts & momentum
    sector_rows: List[List[str]] = []
    bullet_lines: List[str] = []
    rel_present = _present(rel)
    sig_present = _present(sig)
    std_present = _present(std)
    cer_present = _present(cer)

    if not rel.empty and {"sector", "year"}.issubset(rel.columns):
        counts = rel.groupby("sector").size().rename("edge_count")
        buckets = _intensity_bucket(counts)
        # Momentum buckets
        rel["b15_18"] = ((rel["year"] >= 2015) & (rel["year"] <= 2018)).astype(int)
        rel["b19_22"] = ((rel["year"] >= 2019) & (rel["year"] <= 2022)).astype(int)
        rel["b23_25"] = ((rel["year"] >= 2023) & (rel["year"] <= 2025)).astype(int)
        mom = rel.groupby("sector").agg({"b15_18": "sum", "b19_22": "sum", "b23_25": "sum"})

        # Top counterpart per sector + consortium skew
        top_rows: List[Tuple[str, str, float]] = []
        if {"partner_display", "sector"}.issubset(rel.columns):
            grp = rel.groupby(["sector", "partner_display"]).size().rename("n").reset_index()
            for sector, g in grp.groupby("sector"):
                g2 = g.sort_values("n", ascending=False)
                top = g2.iloc[0]
                share = top["n"] / g2["n"].sum() if g2["n"].sum() > 0 else 0.0
                names = [top["partner_display"]]
                if len(g2) > 1:
                    names.append(g2.iloc[1]["partner_display"])
                top_rows.append((sector, ", ".join(names[:2]), share))
        top_df = pd.DataFrame(top_rows, columns=["sector", "tops", "share"]) if top_rows else pd.DataFrame(columns=["sector", "tops", "share"])

        df = (
            counts.to_frame()
            .join(buckets.rename("intensity"))
            .join(mom)
            .join(top_df.set_index("sector"), how="left")
            .fillna({"tops": "–", "share": 0.0})
            .reset_index()
        )
        df = df.sort_values(["intensity", "edge_count"], ascending=[False, False])

        for _, r in df.iterrows():
            sector = str(r["sector"]) if pd.notna(r["sector"]) else "–"
            intensity = str(int(r["intensity"])) if pd.notna(r["intensity"]) else "0"
            momentum = _format_momentum(r)
            tops = r["tops"] if isinstance(r["tops"], str) else "–"
            skew = "Yes (>50%)" if float(r["share"]) > 0.5 else "No"
            sector_rows.append([sector, intensity, momentum, tops, skew])

        # Narrative bullets (up to 5)
        head = df.head(3)
        for _, r in head.iterrows():
            bullet_lines.append(
                f"**{r['sector']}** shows intensity {int(r['intensity'])} with momentum {int(r['b15_18'])}/{int(r['b19_22'])}/{int(r['b23_25'])}. Top counterpart: {r['tops']}."
            )
        if (df["share"] > 0.5).any():
            dom = df.loc[df["share"] > 0.5, "sector"].tolist()
            bullet_lines.append(f"Consortium skew detected in: {', '.join(map(str, dom))} (top-1 > 50%).")
    else:
        sector_rows = []
        bullet_lines.append("No relationships.csv yet — add CORDIS/standards/project edges to improve intensity and momentum.")

    # Standards table (up to 10 rows)
    std_rows: List[List[str]] = []
    if not std.empty:
        cols = [c for c in ["wg", "role", "person_name", "org_name", "sector_hint"] if c in std.columns]
        if cols:
            s10 = std[cols].head(10).fillna("–")
            std_rows = s10.values.tolist()
    sig_rows: List[List[str]] = []
    if not sig.empty:
        for _, r in sig.head(5).iterrows():
            window = r.get("window", "–")
            summ = r.get("signal_summary", "–")
            driver = r.get("likely_driver", "–")
            sig_rows.append([str(window), str(summ), str(driver)])

    out_path = Path(args.out) if args.out else Path("reports") / f"country={ccode}" / "phase-2_landscape.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build markdown
    md = []
    md.append("---")
    md.append("title: \"Phase 2 — Technology Landscape & Maturity (Austria)\"")
    md.append("author: Analyst")
    md.append("date: \"<AUTO>\"")
    md.append("---\n")
    md.append("## Overview")
    md.append("Sector intensity, momentum, standards posture, and notable event spikes for Austria (AT), **2015–2025**. *Looser matchers ON.*\n")
    md.append("### Data presence")
    md.append(f"- relationships.csv: {rel_present}")
    md.append(f"- standards_roles.tsv: {std_present}")
    md.append(f"- signals.csv: {sig_present}")
    md.append(f"- partners_cerlite.csv: {cer_present}\n")

    md.append("---\n")
    md.append("## Sector Scorecard")
    md.append("| Sector | Intensity (0–3) | Momentum (15–18 / 19–22 / 23–25) | Top counterpart(s) | Consortium skew? |")
    md.append("|---|---:|---|---|---|")
    md.append(_md_table(sector_rows))

    md.append("**Notes:** Intensity is relative within AT; 0 = no edges, 1–3 = quartile buckets among non‑zero sectors.\n")
    md.append("---\n")

    md.append("## Standards Posture")
    if std_rows:
        md.append("| WG / SDO | Role | Person/Org | Sector hint |")
        md.append("|---|---|---|---|")
        md.append(_md_table(std_rows))
    else:
        md.append("*(No standards_roles.tsv yet — consider IETF Datatracker slice)*\n")

    md.append("---\n")
    md.append("## Event Spikes")
    if sig_rows:
        md.append("| Window | Signal summary | Likely driver |")
        md.append("|---|---|---|")
        md.append(_md_table(sig_rows))
    else:
        md.append("*(No signals.csv yet — add 1–3 milestone rows when convenient)*\n")

    md.append("---\n")
    md.append("## Narrative Snapshot")
    for b in bullet_lines[:5]:
        md.append(f"- {b}")
    if not bullet_lines:
        md.append("- (Stub narrative)")

    md.append("\n## Caveats")
    md.append("- Looser matchers can over‑include adjacent subfields; review outliers in Phase 5.")
    md.append("- Edges aggregate heterogeneous collaboration types; mechanism details live in Phase 5.\n")

    md.append("## Next Data Boost")
    md.append("Add a **CORDIS participants** slice for AT (2015–2025) to `data/raw/source=cordis/country=AT/date=<YYYY-MM-DD>/participants.csv`, then run `make normalize-all COUNTRY=AT` and rebuild.\n")

    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"WRITE {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
