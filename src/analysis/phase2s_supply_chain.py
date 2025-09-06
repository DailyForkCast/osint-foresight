# src/analysis/phase2s_supply_chain.py
"""
Minimal, robust renderer for Phase 2S — Supply Chain Security Snapshot.
- Works even when inputs are missing (writes a valid skeleton report).
- Uses defensive CSV parsing and tolerant column name detection.
- Writes to: reports/country=<ISO2>/phase-2s_supply_chain.md

Inputs (all optional — report must still render):
  data/processed/country=<ISO2>/relationships.csv
  data/processed/country=<ISO2>/mechanism_incidents.tsv
  data/processed/country=<ISO2>/sanctions_hits.csv

Heuristics (stub, safe defaults):
- Knowledge pillar ≈ CN collaboration edges in relationships.csv.
- Technology pillar ≈ incidents in mechanism_incidents.tsv (any mechanism).
- Finance pillar ≈ incidents where mechanism_family suggests corporate/ownership links.
- Materials, Logistics left blank unless user later adds trade/port CSVs (Phase 2S manual boosts).
- Chokepoints: for each sector, top 1–3 CN counterparts; single-source if unique CN partner count == 1.

Usage:
  python -m src.analysis.phase2s_supply_chain --country PT
"""
from __future__ import annotations
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple
from src.utils.reporting import ensure_template

# ----------------- helpers -----------------

def read_csv_rows(path: Path, delimiter: str | None = None) -> List[dict]:
    if not path.exists():
        return []
    # Try sniffing delimiter if not provided
    if delimiter is None:
        sample = path.read_text(encoding="utf-8", errors="ignore")[:5000]
        try:
            dialect = csv.Sniffer().sniff(sample)
            delim = dialect.delimiter
        except Exception:
            delim = "," if path.suffix.lower() == ".csv" else "\t"
    else:
        delim = delimiter
    rows: List[dict] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        for r in reader:
            rows.append({k or "": (v or "").strip() for k, v in r.items()})
    return rows


def pick(colnames: List[str], *cands: str) -> str | None:
    lmap = {c.lower(): c for c in colnames}
    for c in cands:
        if c.lower() in lmap:
            return lmap[c.lower()]
    return None


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


# ----------------- main logic -----------------

def build_report(ccode: str) -> str:
    proc_dir = Path("data/processed") / f"country={ccode}"
    rel_p = proc_dir / "relationships.csv"
    mech_p = proc_dir / "mechanism_incidents.tsv"
    sanc_p = proc_dir / "sanctions_hits.csv"

    rel_rows = read_csv_rows(rel_p)
    mech_rows = read_csv_rows(mech_p)  # tsv will be sniffed
    sanc_rows = read_csv_rows(sanc_p)

    # Column resolution (tolerant)
    rel_cols = rel_rows[0].keys() if rel_rows else []
    sector_col = pick(list(rel_cols), "sectors", "sector", "Sector")
    partner_col = pick(list(rel_cols), "partner_entity", "counterpart_name", "partner", "entity", "name")
    country_col = pick(list(rel_cols), "partner_country", "counterpart_country", "country")

    # Aggregate CN knowledge links per sector
    knowledge_counts: Counter[str] = Counter()
    cn_partners_by_sector: Dict[str, Counter[str]] = defaultdict(Counter)
    if rel_rows and sector_col and country_col and partner_col:
        for r in rel_rows:
            sec = r.get(sector_col, "") or "(unknown)"
            cty = (r.get(country_col, "") or "").upper()
            if cty == "CN":
                knowledge_counts[sec] += 1
                partner = r.get(partner_col, "") or "(unknown)"
                cn_partners_by_sector[sec][partner] += 1

    # Technology & Finance approximations from mechanism incidents
    mech_cols = mech_rows[0].keys() if mech_rows else []
    m_sector_col = pick(list(mech_cols), "sector", "Sector")
    m_family_col = pick(list(mech_cols), "mechanism_family")

    tech_counts: Counter[str] = Counter()
    finance_counts: Counter[str] = Counter()
    if mech_rows:
        for r in mech_rows:
            sec = (r.get(m_sector_col, "") or "(unknown)") if m_sector_col else "(unknown)"
            fam = (r.get(m_family_col, "") or "").lower()
            # Count any incident under technology; refine later when families are richer
            tech_counts[sec] += 1
            if any(k in fam for k in ["corporate", "ownership", "equity", "board", "officer", "investment", "funding"]):
                finance_counts[sec] += 1

    # Sanctions (simple listing)
    sanc_hits = sanc_rows  # already parsed

    # Assemble Pillars Overview table rows
    sectors = set(knowledge_counts) | set(tech_counts) | set(finance_counts)
    if not sectors:
        sectors = {"(no data)"}
    table_rows = []
    for sec in sorted(sectors):
        materials = ""  # left blank until trade CSV added
        knowledge = str(knowledge_counts.get(sec, 0))
        technology = str(tech_counts.get(sec, 0))
        finance = str(finance_counts.get(sec, 0))
        logistics = ""  # left blank until port/AIS CSV added
        table_rows.append([sec, materials, knowledge, technology, finance, logistics])

    # Chokepoints table (top counterparts and single/multi-source)
    chokepoints = []
    for sec, ctr in sorted(cn_partners_by_sector.items()):
        if not ctr:
            continue
        top = ", ".join([name for name, _ in ctr.most_common(3)])
        uniq = len(ctr)
        sm = "single-source" if uniq == 1 else "multi-source"
        chokepoints.append([sec, "Knowledge", top, sm, "relationships.csv"])

    # Render markdown
    lines: List[str] = []
    lines.append("---")
    lines.append(f"title: Phase 2S — Supply Chain Security Snapshot ({ccode})")
    lines.append("author: Analyst")
    lines.append("---\n")
    lines.append("## Pillars Overview")
    lines.append("| Sector | Materials | Knowledge | Technology | Finance | Logistics |")
    lines.append("|---|---|---|---|---|---|")
    for row in table_rows:
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## Chokepoints")
    lines.append("| Sector | Pillar | Top Counterpart(s) | Single/Multi-source | Evidence |")
    lines.append("|---|---|---|---|---|")
    if chokepoints:
        for row in chokepoints:
            lines.append("| " + " | ".join(row) + " |")
    else:
        lines.append("| (none) |  |  |  |  |")

    lines.append("\n## Sanctions/Prohibitions (if screened)")
    lines.append("| Entity | List | Date | Link |")
    lines.append("|---|---|---|---|")
    if sanc_hits:
        # Try to pick columns defensively
        sh_cols = sanc_hits[0].keys()
        name_col = pick(list(sh_cols), "partner_name", "name") or "name"
        list_col = pick(list(sh_cols), "matched_list", "list") or "list"
        date_col = pick(list(sh_cols), "listed_on") or "listed_on"
        url_col = pick(list(sh_cols), "url") or "url"
        for r in sanc_hits[:100]:  # cap rows for readability
            lines.append(f"| {r.get(name_col,'')} | {r.get(list_col,'')} | {r.get(date_col,'')} | {r.get(url_col,'')} |")
    else:
        lines.append("| (no screening data) |  |  |  |")

    lines.append("\n## Narrative (5–8 bullets)")
    # Minimal scaffold with dynamic hints
    hint = "At present, Materials/Logistics columns are empty until trade or port CSVs are added."
    lines.extend([
        f"- Snapshot based on existing collaboration/incidents data for {ccode}.",
        f"- Knowledge pillar counts reflect CN-linked edges in relationships.csv.",
        f"- Technology/Finance approximations derive from mechanism_incidents.tsv (families subject to refinement).",
        f"- {hint}",
    ])

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()

    ccode = args.country.upper()
    ensure_template(ccode, "phase-2s_supply_chain.md")
    out = Path("reports") / f"country={ccode}" / "phase-2s_supply_chain.md"
    ensure_dir(out)
    md = build_report(ccode)
    out.write_text(md, encoding="utf-8")
    print(f"WROTE {out}")


if __name__ == "__main__":
    main()