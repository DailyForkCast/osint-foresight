import csv, json, os, sys
from pathlib import Path
from datetime import datetime
import yaml

ROOT = Path(__file__).resolve().parents[2]

SCHEMAS = {
    "institutions.csv": [
        "id","name","aliases","country","registry_ids","ownership_notes","sectors",
        "accreditation_id","accreditation_scope","accred_issued","accred_expires",
        "facility_controls","evidence_urls"
    ],
    "programs.csv": [
        "id","program","owner","size_eur_typ","cadence","sectors","eligibility",
        "compliance_hooks","notes","url"
    ],
    "relationships.csv": [
        "id","partner_country","partner_entity","collab_type","start_yr","intensity_0_3",
        "directionality","sectors","local_leads","value_summary","risk_level","risk_notes","evidence_urls"
    ],
    "signals.csv": [
        "id","category","trigger","description","recommended_action","owner","date_logged"
    ],
    "prc_interest_signals.tsv": [
        "id","sector","signal_family","description","date","source","signal_strength_0_3",
        "evidence_mode(direct|proxy|inference)","assumption_level_0_2","why_plausible","confidence_0_1",
        "falsification_query","search_debt(y/n)","link"
    ],
    "policy_corpus.tsv": [
        "id","issuing_body_en","issuing_body_zh","doc_title","doc_type(5YP|white_paper|guideline|notice|SASAC_guidance|MIIT|provincial_plan|tender|standards_proposal)",
        "release_date(YYYY-MM-DD)","sector_tags","country_refs(explicit|regional|none)","specificity_score_0to5",
        "excerpt_key_claim","url","source_language","source_tier","confidence_0to1","evidence_id"
    ],
    "mechanism_incidents.tsv": [
        "id","sector","mechanism_family","incident_type","description","start_date","latest_activity_date",
        "counterpart_entity_en","counterpart_entity_zh","org_id_type","org_id_value","value_eur","stake_pct",
        "board_rights(y/n/unknown)","doc_link","source_tier","confidence_0to1","evidence_id"
    ],
    "standards_roles.tsv": [
        "id","body","wg","role(editor/rapporteur/chair/member)","ballots_submitted","ballots_accepted",
        "streak_quarters","link","confidence"
    ],
    "curriculum_footprints.tsv": [
        "id","university","program","seat_count","level","status(active/dormant)","notes","link"
    ],
    "posture_scoring.tsv": [
        "sector","interest_score_0_10","specificity_0_10","mechanism_0_10","friction_0_10",
        "posture_score_0_10","classification(Priority|Convenience|Mixed)","interest_top_signals",
        "evidence_mix(direct/proxy/inference %)","fragile_components(after_ablation)","uncertainty_note","evidence_id"
    ],
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def processed_path(country: str, filename: str) -> Path:
    p = ROOT / "data" / "processed" / f"country={country.upper()}" / filename
    ensure_dir(p.parent)
    return p


def reports_path(country: str, filename: str) -> Path:
    p = ROOT / "reports" / f"country={country.upper()}" / filename
    ensure_dir(p.parent)
    return p


def write_table(path: Path, headers, rows=None) -> None:
    rows = rows or []
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerows(rows)
    elif suffix == ".tsv":
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(headers)
            w.writerows(rows)
    else:
        raise ValueError(f"Unsupported table format: {suffix}")


def write_markdown(path: Path, title: str, body: str) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{body}\n")


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def main_stub(country: str, output_filename: str) -> None:
    # Helper for stubs: create an empty processed table with headers
    headers = SCHEMAS[output_filename]
    out = processed_path(country, output_filename)
    write_table(out, headers, [])
    print(f"Wrote {out.relative_to(ROOT)} (headers only)")

if __name__ == "__main__":
    print("This module provides I/O helpers; run specific phase modules instead.")