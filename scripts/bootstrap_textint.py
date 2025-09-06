#!/usr/bin/env python3
# scripts/bootstrap_textint.py
"""
Create local Text Intelligence prompt files under /prompts/textint/ and a minimal
country policy watchlist at /queries/policy/watchlist.yaml.

- Idempotent: will not overwrite existing files unless --overwrite is passed.
- Safe logs: prints CREATED/OK/OVERWRITE for each file.

Usage:
  python scripts/bootstrap_textint.py --country SE
  python scripts/bootstrap_textint.py --country NO --overwrite

Outputs:
  prompts/textint/
    00_quick_triage.md
    01_policy_snapshot.md
    02_mechanisms_controls.md
    03_quotes.md
    04_specificity_to_7c.md
    05_controls_to_phase6.md
    06_scs_levers_map.md
    07_contradictions.md
    08_policy_brief_onepager.md
  queries/policy/watchlist.yaml
"""
from __future__ import annotations
import argparse
from pathlib import Path

PROMPTS: dict[str, str] = {
    "00_quick_triage.md": (
        "# Quick Triage (10 minutes)\n\n"
        "> Paste an excerpt from a policy/white paper. Return: (1) what this is (type/issuer),\n"
        "> (2) top three points, (3) concrete mechanisms/controls, (4) SCS pillar relevance\n"
        "> (Materials/Knowledge/Technology/Finance/Logistics), (5) a 2‑sentence summary.\n"
    ),
    "01_policy_snapshot.md": (
        "# Policy Snapshot (single TSV row)\n\n"
        "Output one TSV row with fields (tab‑separated; leave unknowns blank; summary ≤500 chars):\n"
        "source_id\ttitle\tissuer\tissuer_level\tpub_date\turl\tlang\tcountry_scope\tpolicy_domain\t"
        "sectors\tinstruments\tmaturity\tstance_prc_mcf\tenforcement_tools\ttime_horizon\treview_cycle\t"
        "credibility_1_5\tconfidence\tsummary\n\n"
        "Credibility rubric: 5=law/reg; 4=official strategy/circular; 3=para‑official; 2=independent think‑tank; 1=media/blog.\n"
    ),
    "02_mechanisms_controls.md": (
        "# Mechanisms & Controls (claims TSV)\n\n"
        "Extract concrete claims as TSV rows:\n"
        "source_id\tclaim_id\tpage\tparagraph\tclaim_text\tclaim_type\tsectors\tscs_pillars\tmechanisms\t"
        "controls\tevidence_refs\tconfidence\n\n"
        "claim_type ∈ {mechanism, control, funding, standardization, restriction, capacity_building}.\n"
    ),
    "03_quotes.md": (
        "# Quote Capture (verbatim with cites)\n\n"
        "Extract 3–10 quotes (≤300 chars) with page number and relevance tag. TSV columns:\n"
        "source_id\tpage\tquote\tcontext\trelevance\tsectors\tscs_pillars\n"
    ),
    "04_specificity_to_7c.md": (
        "# Specificity to 7C (policy alignment)\n\n"
        "Build a table: sector → specificity contribution (0–5) with a one‑line justification citing the policy.\n"
    ),
    "05_controls_to_phase6.md": (
        "# Controls to Phase 6 (risk mitigations)\n\n"
        "Convert controls into Phase‑6 mitigations: control, risk vector, sector, SCS pillar, implementation burden (low/med/high), one‑line how‑to for SMEs/universities.\n"
    ),
    "06_scs_levers_map.md": (
        "# SCS Levers Map (Phase 2S)\n\n"
        "Map each assertion to SCS pillars; list named entities, leverage path (e.g., JV, beneficial ownership, standards route, logistics corridor), and a confidence note.\n"
    ),
    "07_contradictions.md": (
        "# Contradiction & Tension Finder\n\n"
        "Compare with past policy_assertions.tsv excerpts. List 'Potential Contradictions' and 'Resolution Ideas' (authority/recency).\n"
    ),
    "08_policy_brief_onepager.md": (
        "# One‑Pager Policy Brief\n\n"
        "Produce: (a) 5 bullets of what matters, (b) 3 mechanisms + 3 controls with sectors/pillars,\n"
        "(c) a 6‑row sector→specificity table, (d) 3 trackable tripwires from our processed tables.\n"
    ),
}

WATCHLIST_TMPL = """# Minimal policy/narrative watchlist (low‑cadence refreshes)
# Cadence is a hint for occasional rechecks; most docs are stable once ingested.
- name: Ministry of Industry and Information Technology (MIIT) notices
  cadence: quarterly
  country: CN
  notes: policy/standards/MCF
  url: https://www.miit.gov.cn/
- name: US Treasury / OFAC updates
  cadence: weekly
  country: US
  notes: sanctions lists
  url: https://ofac.treasury.gov/sanctions-lists
- name: European Commission — DG TRADE (export controls / dual-use)
  cadence: quarterly
  country: EU
  notes: guidance / regulations
  url: https://policy.trade.ec.europa.eu/index_en
- name: National Accreditation Body — {COUNTRY}
  cadence: annual
  country: {COUNTRY}
  notes: ISO/IEC 17025/17020 accredited labs directory
  url: ""
- name: National Think Tank — {COUNTRY}
  cadence: semiannual
  country: {COUNTRY}
  notes: AI/HPC/critical-tech reports
  url: ""
- name: Standards bodies (IETF / ISO / IEC / ITU) — liaison updates
  cadence: quarterly
  country: multi
  notes: standards roadmaps / roles / ballots
  url: https://datatracker.ietf.org/
- name: BIS Entity/MEU/UVL lists
  cadence: weekly
  country: US
  notes: export restrictions
  url: https://www.bis.doc.gov/
"""


def write_file(path: Path, content: str, overwrite: bool = False) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return f"OK       {path}"
    path.write_text(content, encoding="utf-8")
    return ("OVERWRITE " if path.exists() and overwrite else "CREATED  ") + str(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="ISO2 code to personalize watchlist entries (e.g., SE)")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files if present")
    args = ap.parse_args()

    iso = args.country.upper()

    # 1) Prompts directory
    prompts_dir = Path("prompts/textint")
    logs = []
    for fname, body in PROMPTS.items():
        logs.append(write_file(prompts_dir / fname, body, overwrite=args.overwrite))

    # 2) Watchlist
    qdir = Path("queries/policy")
    watchlist = WATCHLIST_TMPL.replace("{COUNTRY}", iso)
    logs.append(write_file(qdir / "watchlist.yaml", watchlist, overwrite=args.overwrite))

    print("\n".join(logs))
    print("\nDone. Text Intelligence prompts and watchlist are in place.")


if __name__ == "__main__":
    main()