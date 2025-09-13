Below is a single copy‑paste prompt for Claude Code to implement **automatic template auto‑copying** inside analysis scripts. It:
1) Creates `src/utils/reporting.py` with `ensure_template()` (env‑toggleable, non‑overwriting).
2) Wires calls into high‑touch analysis modules (2, 2S, 3, 4, 5, 6, 7C, 8, policy_brief).
3) Adds an optional Makefile toggle `ENABLE_AUTOCOPY_TEMPLATES` (default ON).
4) Prints a mini CHANGELOG at the end.

Safe by default: no overwrites; only creates missing report files from `reports/templates/`.

---

## Step 1 — Create helper: `src/utils/reporting.py`
Create this new file (or overwrite if identical):
```python
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
        print(f"AUTO-COPIED template → {dst}")
```

---

## Step 2 — Wire into analysis scripts
For each of the following modules, insert the import and one call near the top of `main()` *before* writing the report:

**A) Phase 2 (landscape)** — `src/analysis/phase2_landscape.py`
```python
from src.utils.reporting import ensure_template
# inside main(), after parsing --country
ensure_template(ccode, "phase-2_landscape.md")
```

**B) Phase 2S (SCS)** — `src/analysis/phase2s_supply_chain.py` (we created earlier; patch it now)
```python
from src.utils.reporting import ensure_template
# inside main()
ensure_template(ccode, "phase-2s_supply_chain.md")
```

**C) Phase 3 (institutions)** — `src/analysis/phase3_institutions.py`
```python
from src.utils.reporting import ensure_template
ensure_template(ccode, "phase-3_institutions.md")
```

**D) Phase 4 (funders)** — `src/analysis/phase4_funders.py`
```python
from src.utils.reporting import ensure_template
ensure_template(ccode, "phase-4_funders.md")
```

**E) Phase 5 (links)** — `src/analysis/phase5_links.py`
```python
from src.utils.reporting import ensure_template
ensure_template(ccode, "phase-5_links.md")
```

**F) Phase 6 (risk)** — `src/analysis/phase6_risk.py`
```python
from src.utils.reporting import ensure_template
ensure_template(ccode, "phase-6_risk.md")
```

**G) Phase 7C (posture)** — `src/analysis/phase7c_posture.py`
```python
from src.utils.reporting import ensure_template
ensure_template(ccode, "phase-7c_posture.md")
```

**H) Phase 8 (foresight)** — `src/analysis/phase8_foresight.py`
```python
from src.utils.reporting import ensure_template
ensure_template(ccode, "phase-8_foresight.md")
```

**I) Policy brief** — `src/analysis/policy_brief.py` (we created earlier; patch it now)
```python
from src.utils.reporting import ensure_template
ensure_template(ccode, "policy_brief.md")
```

> If a given analysis module doesn’t exist yet, skip it and log `SKIP <path> (not found)`.

Implementation hint (automate the inserts):
- Open file, search for `def main()` or the existing `args = ap.parse_args()` block, and insert the two lines after the country parse (`ccode = args.country.upper()`).
- Ensure the `from src.utils.reporting import ensure_template` import is present at the top (add if missing).

---

## Step 3 — Add Makefile toggle (optional; default ON)
Append near other toggles:
```make
ENABLE_AUTOCOPY_TEMPLATES ?= 1
```
No further changes needed; the helper reads this via environment.

---

## Step 4 — Quick tests
Run the following (pick any ISO2, e.g., SE):
```bash
# Remove one report to confirm auto-copy behaviour
rm -f reports/country=SE/phase-5_links.md 2>/dev/null || true

# Phase 5 should auto-copy its template before writing
python -m src.analysis.phase5_links --country SE || true

# New countries should also work out-of-the-box
make reports-init COUNTRY=NO   # optional bulk copy
python -m src.analysis.phase2s_supply_chain --country NO
```
Expected logs include `AUTO-COPIED template → reports/country=SE/phase-5_links.md` when missing.

---

## Step 5 — Print CHANGELOG
After applying patches, print a concise list of created/modified files:
```
CREATED  src/utils/reporting.py
UPDATED  src/analysis/phase2s_supply_chain.py (ensure_template wired)
UPDATED  src/analysis/policy_brief.py (ensure_template wired)
UPDATED  src/analysis/phase2_landscape.py (ensure_template wired)
UPDATED  src/analysis/phase3_institutions.py (ensure_template wired)
UPDATED  src/analysis/phase4_funders.py (ensure_template wired)
UPDATED  src/analysis/phase5_links.py (ensure_template wired)
UPDATED  src/analysis/phase6_risk.py (ensure_template wired)
UPDATED  src/analysis/phase7c_posture.py (ensure_template wired)
UPDATED  src/analysis/phase8_foresight.py (ensure_template wired)
(If any file missing: SKIP logged above)
```

Please perform the edits now and show the step‑by‑step log.

