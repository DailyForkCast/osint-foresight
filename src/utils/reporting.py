# src/utils/reporting.py
from __future__ import annotations
from pathlib import Path
import os

def ensure_template(country_iso: str, filename: str) -> None:
    """If reports/country=<ISO2>/<filename> is missing, copy from reports/templates/<filename>.
    Controlled by ENABLE_AUTOCOPY_TEMPLATES (default '1'). Never overwrites existing files.
    """
    if os.getenv("ENABLE_AUTOCOPY_TEMPLATES", "1") != "1":
        return
    dst = Path("reports") / f"country={country_iso}" / filename
    if dst.exists():
        return
    src = Path("reports/templates") / filename
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"AUTO-COPIED template -> {dst}")