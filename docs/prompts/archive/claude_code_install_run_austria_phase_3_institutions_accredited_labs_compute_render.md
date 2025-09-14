Below is a single, copy‑paste canvas for Claude Code. It **installs** the Phase‑3 compute script, **runs** it for Austria, and prints tight logs. Deterministic writes; no pushes.

---

# Claude Code — Install & Run Phase 3 (Austria, AT)

## Guardrails
- Deterministic writes only; **do not** `git push`.
- If the script below differs from local files, **overwrite** it.
- After install, **run** it for `AT` and print the `WRITE …` confirmation line.

## Step A — Create/overwrite `src/analysis/phase3_institutions.py`
Write this file **verbatim**:

```python
# src/analysis/phase3_institutions.py
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


# Helper readers (CSV then TSV fallback)
def _read_any(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    for sep in [",", "\t"]:
        try:
            return pd.read_csv(path, sep=sep)
        except Exception:
            continue
    return pd.DataFrame()


def _norm(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def _present(df: pd.DataFrame) -> str:
    return f"yes (rows={len(df)})" if not df.empty else "no"


def _md_table(rows: List[List[str]], widths: int) -> str:
    if not rows:
        return "| " + " | ".join(["–"] * widths) + " |\n"
    return "\n".join(["| " + " | ".join(map(str, r)) + " |" for r in rows]) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="ISO2 e.g. AT")
    ap.add_argument("--out", default=None, help="Override output path")
    args = ap.parse_args()

    CC = args.country.upper()
    ensure_template(CC, "phase-3_institutions.md")

    base = Path("data/processed") / f"country={CC}"
    inst = _norm(_read_any(base / "institutions.csv"))
    rel = _norm(_read_any(base / "relationships.csv"))
    std = _norm(_read_any(base / "standards_roles.tsv"))
    cer = _norm(_read_any(base / "cer_master.csv"))

    # Column hygiene for institutions
    # Expected tolerant columns: name, country, org_type, is_lab, accreditation_id, scope, city
    if not inst.empty:
        for col in ["name", "country", "org_type", "is_lab", "accreditation_id", "scope", "city"]:
            if col not in inst.columns:
                inst[col] = None
        # limit to country
        if "country" in inst.columns:
            inst = inst[(inst["country"].fillna("").str.upper() == CC)]

    # Derive quick summaries
    counts_by_type: List[List[str]] = []
    if not inst.empty:
        grp = inst.groupby(inst["org_type"].fillna("(unknown)"))
        counts_by_type = [[k, str(v.size)] for k, v in grp["name"].count().items()]
        counts_by_type = sorted(counts_by_type, key=lambda x: int(x[1]), reverse=True)

    # Accredited labs snapshot (top 10)
    labs_rows: List[List[str]] = []
    if not inst.empty and ("is_lab" in inst.columns):
        labs = inst[(inst["is_lab"].astype(str).str.lower().isin(["1", "true", "yes"])) | (inst["accreditation_id"].notna())]
        if not labs.empty:
            cols = [c for c in ["name", "accreditation_id", "scope", "city"] if c in labs.columns]
            labs = labs[cols].fillna("–").head(10)
            labs_rows = labs.values.tolist()

    # Standards-linked orgs (exact org name match on std.org_name)
    std_rows: List[List[str]] = []
    if not std.empty:
        std_cols = [c for c in ["wg", "role", "person_name", "org_name", "sector_hint"] if c in std.columns]
        st = std[std_cols].copy()
        if not st.empty:
            st["org_name_n"] = st["org_name"].astype(str).str.strip().str.lower()
            inst_n = inst[["name"]].copy() if not inst.empty else pd.DataFrame({"name": []})
            inst_n["name_n"] = inst_n["name"].astype(str).str.strip().str.lower()
            joined = st.merge(inst_n, left_on="org_name_n", right_on="name_n", how="left")
            st = st.fillna("–").head(10)
            for _, r in st.iterrows():
                std_rows.append([
                    r.get("wg", "–"),
                    r.get("role", "–"),
                    r.get("person_name", "–"),
                    r.get("org_name", "–"),
                    r.get("sector_hint", "–"),
                ])

    # Relationship coverage by institution (top 10 by edges)
    rel_rows: List[List[str]] = []
    if not rel.empty and "counterpart_name" in rel.columns:
        rel["counterpart_name_n"] = rel["counterpart_name"].astype(str).str.strip().str.lower()
        top = rel.groupby(["counterpart_name_n"]).size().rename("n").reset_index()
        top = top.sort_values("n", ascending=False).head(10)
        for _, r in top.iterrows():
            rel_rows.append([r["counterpart_name_n"], str(int(r["n"]))])

    # CER-lite snapshot
    cer_rows: List[List[str]] = []
    if not cer.empty:
        amb_count = int(cer[cer.get("ambiguous", 0).astype(str).isin(["1", "true", "True"])].shape[0]) if "ambiguous" in cer.columns else 0
        cer_rows = [[str(len(cer)), str(amb_count)]]

    # Build markdown
    out: List[str] = []
    out.append("---")
    out.append("title: \"Phase 3 — Institutions & Accredited Labs (Austria)\"")
    out.append("author: Analyst")
    out.append("date: \"<AUTO>\"")
    out.append("---\n")

    out.append("## Data presence")
    out.append(f"- institutions.csv: {_present(inst)}")
    out.append(f"- relationships.csv: {_present(rel)}")
    out.append(f"- standards_roles.tsv: {_present(std)}")
    out.append(f"- cer_master.csv: {_present(cer)}\n")

    out.append("## Institutional Map (counts by type)")
    out.append("| Org type | Count |")
    out.append("|---|---:|")
    out.append(_md_table(counts_by_type, 2))

    out.append("\n## Accredited Labs (top 10)")
    out.append("| Name | Accreditation ID | Scope | City |")
    out.append("|---|---|---|---|")
    out.append(_md_table(labs_rows, 4))

    out.append("\n## Standards‑linked Organizations (sample)")
    out.append("| WG/SDO | Role | Person | Organization | Sector hint |")
    out.append("|---|---|---|---|---|")
    out.append(_md_table(std_rows, 5))

    out.append("\n## Relationship Coverage (top counterparts in Phase‑2 edges)")
    out.append("| Organization (normalized) | Edge count |")
    out.append("|---|---:|")
    out.append(_md_table(rel_rows, 2))

    out.append("\n## CER‑lite Snapshot")
    out.append("| Canonical entities | Ambiguous entities |")
    out.append("|---:|---:|")
    out.append(_md_table(cer_rows, 2))

    # Narrative (short)
    bullets: List[str] = []
    if counts_by_type:
        bullets.append("Institutional map renders; consider adding accreditation CSV to strengthen lab visibility.")
    if labs_rows:
        bullets.append("Accredited labs present; verify scope texts and tie them to sectors in Phase‑2.")
    if std_rows:
        bullets.append("Standards‑linked orgs detected (supports Knowledge pillar).")
    if rel_rows:
        bullets.append("Phase‑2 edges include identifiable institutions; use CER‑lite to improve naming.")
    if not bullets:
        bullets.append("No institutions data yet — drop a minimal CSV to render this phase.")

    out.append("\n## Narrative Snapshot")
    for b in bullets[:5]:
        out.append(f"- {b}")

    out.append("\n## Minimal CSV (drop‑in) — if you have 10 minutes")
    out.append("Add `data/raw/source=accreditation/country=%s/date=<YYYY-MM-DD>/labs.csv` with header:" % CC)
    out.append("\n```")
    out.append("name,country,accreditation_id,scope,city,is_lab")
    out.append("```")
    out.append("Then run `make normalize-all COUNTRY=%s` and rebuild." % CC)

    # Write
    out_path = Path(args.out) if args.out else Path("reports") / f"country={CC}" / "phase-3_institutions.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"WRITE {out_path}")


if __name__ == "__main__":
    main()
```

## Step B — Run Phase 3 for Austria
Execute:
```bash
python -m src.analysis.phase3_institutions --country AT
```
Expected output:
```
WRITE reports/country=AT/phase-3_institutions.md
```

## Step C — (Optional) commit locally (no push)
```bash
git add src/analysis/phase3_institutions.py reports/country=AT/phase-3_institutions.md
git commit -m "feat(AT/phase-3): compute Institutions & Accredited Labs snapshot"
```

## Final log
Print:
```
OK: Phase 3 computed & written for AT
```
