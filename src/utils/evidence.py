from pathlib import Path
from datetime import datetime
import csv

ROOT = Path(__file__).resolve().parents[2]

EVIDENCE_HEADERS = [
    "evidence_id","source_name","source_url","captured_at_iso","filter_params","language",
    "source_tier(A/B/C)","reliability_note","stale_flag(>18m|>36m)","screenshot_path","country"
]

def evidence_path() -> Path:
    p = ROOT / "evidence" / "register_v2.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        with p.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(EVIDENCE_HEADERS)
    return p

_def_ts = lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z"

def append_row(source_name: str, source_url: str, country: str, filter_params: str, screenshot_path: str = ""):
    p = evidence_path()
    eid = f"EV-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    row = [eid, source_name, source_url, _def_ts(), filter_params, "EN", "A", "", "", screenshot_path, country]
    with p.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    return eid