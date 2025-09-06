import csv
from pathlib import Path
from .io import processed_path, ROOT

CER_HEADERS = [
    "cer_id","name_en","name_local","name_zh","aliases","lei","ror",
    "registry_ids(country:id;json)","country","sector_tags","confidence_0_1","provenance"
]

def ensure_cer_master() -> Path:
    p = ROOT / "cer" / "cer_master.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        with p.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CER_HEADERS)
    return p