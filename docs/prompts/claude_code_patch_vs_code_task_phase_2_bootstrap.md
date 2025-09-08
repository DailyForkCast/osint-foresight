# Patch: add a tiny VS Code task to bootstrap Phase 2 files (country‑aware)

## What this does
Creates a minimal helper **`src/utils/phase2_bootstrap.py`** and adds a VS Code task **`phase-2:bootstrap`** that:
- Ensures the directory `data/processed/country=<ISO2>/` exists
- (Idempotently) creates these files **with headers** if missing:
  - `domain_maturity.tsv`
  - `facilities.tsv`
  - `sanctions_hits.csv` (signals‑only; **exclude US persons** downstream)
- Optionally seeds a single `no_data_yet=true` row

---

## 1) Create helper module
**Path:** `src/utils/phase2_bootstrap.py`
```python
import argparse, csv, os, sys
from datetime import date

HEADERS = {
    "domain_maturity.tsv": ["domain_id","domain","maturity_band","rationale","key_signals","confidence_LMH","notes"],
    "facilities.tsv": ["facility","type","location","access_mode","relevance","notes"],
    "sanctions_hits.csv": ["list_name","entity_name","country","link","last_check","notes"],
}

SEED_ROWS = {
    "domain_maturity.tsv": [{"domain_id":"D0","domain":"(seed)","maturity_band":"","rationale":"","key_signals":"","confidence_LMH":"","notes":"no_data_yet=true"}],
    "facilities.tsv": [{"facility":"(seed)","type":"","location":"","access_mode":"","relevance":"","notes":"no_data_yet=true"}],
    "sanctions_hits.csv": [{"list_name":"(seed)","entity_name":"","country":"","link":"","last_check":str(date.today()),"notes":"no_data_yet=true (non‑US persons policy applies)"}],
}

def ensure_file(path, headers, seed=True):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Decide delimiter by extension
        delim = '\t' if path.endswith('.tsv') else ','
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=headers, delimiter=delim)
            w.writeheader()
            if seed:
                # Write a single seed row (empty fields filled by DictWriter)
                for row in SEED_ROWS[os.path.basename(path)]:
                    w.writerow(row)
        return True
    return False

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--country", required=True, help="ISO2 code, e.g., AT")
    p.add_argument("--no-seed", action="store_true", help="Create headers only")
    args = p.parse_args()

    base = os.path.join("data","processed",f"country={args.country}")
    created = []
    for fname in ("domain_maturity.tsv","facilities.tsv","sanctions_hits.csv"):
        path = os.path.join(base, fname)
        if ensure_file(path, HEADERS[fname], seed=not args.no_seed):
            created.append(path)
    print("Created:" if created else "All present:")
    for c in created:
        print(" - ", c)
```

---

## 2) Patch `.vscode/tasks.json`
Add (or merge) the **task** and the **input** below. If `inputs` already contains `countryCode`, reuse it.

```jsonc
{
  // … existing tasks.json …
  "version": "2.0.0",
  "tasks": [
    // … existing tasks …,
    {
      "label": "phase-2:bootstrap",
      "type": "shell",
      "command": "python",
      "args": ["-m", "src.utils.phase2_bootstrap", "--country", "${input:countryCode}"],
      "problemMatcher": [],
      "group": "none",
      "presentation": { "reveal": "always", "panel": "dedicated" }
    }
  ],
  "inputs": [
    // Reuse if it already exists in your file
    {
      "id": "countryCode",
      "type": "promptString",
      "description": "ISO2 country code (e.g., AT)",
      "default": "AT"
    }
  ]
}
```

> If your `tasks.json` already has `version`, `tasks`, or `inputs`, just insert the new entries instead of duplicating the keys.

---

## 3) Quick test
- Command Palette → **Run Task…** → `phase-2:bootstrap` → enter `AT`
- Verify these files now exist with headers (and one seed row):
  - `data/processed/country=AT/domain_maturity.tsv`
  - `data/processed/country=AT/facilities.tsv`
  - `data/processed/country=AT/sanctions_hits.csv`

Commit: `chore(AT): add phase‑2 bootstrap task + helper`