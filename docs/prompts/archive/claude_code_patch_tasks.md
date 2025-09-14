# Claude Code — Patch .vscode/tasks.json (add `phase-8:bootstrap`) + add `src/utils/phase8_bootstrap.py`

## 1) Update `.vscode/tasks.json`
Append the **input** (if not present) and the **task** below. Keep JSON valid; use JSONC comments only where allowed.

```jsonc
{
  // ...existing tasks.json...
  "version": "2.0.0",
  "inputs": [
    // ensure this exists once globally
    {
      "id": "countryCode",
      "type": "promptString",
      "description": "ISO‑2 country code (e.g., AT)",
      "default": "AT"
    }
  ],
  "tasks": [
    // ...existing tasks...
    {
      "label": "phase-8:bootstrap",
      "type": "shell",
      "command": "python",
      "args": [
        "-m", "src.utils.phase8_bootstrap",
        "--country", "${input:countryCode}"
      ],
      "problemMatcher": []
    }
  ]
}
```

## 2) Create `src/utils/phase8_bootstrap.py`
```python
# src/utils/phase8_bootstrap.py
from pathlib import Path
import argparse

def touch(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")

TSV_LIST = [
    "p8_baseline.tsv",
    "p8_scenarios.tsv",
    "p8_wildcards.tsv",
    "p8_ewi.tsv",
    "p8_targeting.tsv",
    "p8_interventions.tsv",
]

HEADERS = {
    "p8_baseline.tsv": "cluster_id\tcluster_name\t2027_outlook_0_3\t2030_outlook_0_3\t2035_outlook_0_3\tdrivers\tdrags\tconfidence_LMH\tnotes\n",
    "p8_scenarios.tsv": "scenario_id\thorizon\tscenario_family\ttitle\tshort_path\timplications\tconfidence_LMH\tnotes\n",
    "p8_wildcards.tsv": "wildcard_id\thorizon\ttitle\ttrigger\tfirst_order_effect\tsecond_order_effect\tnotes\n",
    "p8_ewi.tsv": "indicator_id\tindicator\tthreshold\tfavours_scenario\tcollection_plan\tsource_hint\tnotes\n",
    "p8_targeting.tsv": "cluster_id\tmechanism\t2y_attraction_0_3\t5y_attraction_0_3\t10y_attraction_0_3\trationale\tnotes\n",
    "p8_interventions.tsv": "intervention_id\tclass\twhat\twhy_linked_to_evidence\teffort_1to3\towner_hint\tnotes\n",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="ISO‑2 country code, e.g., AT")
    args = ap.parse_args()

    base = Path("data/processed") / f"country={args.country}"
    base.mkdir(parents=True, exist_ok=True)

    for name in TSV_LIST:
        p = base / name
        if not p.exists() or p.stat().st_size == 0:
            p.write_text(HEADERS[name], encoding="utf-8")
        else:
            # keep existing content
            pass
    print(f"phase-8 bootstrap ok → {base}")

if __name__ == "__main__":
    main()
```

## 3) Test from VS Code
- **Command Palette →** `Run Task` → `phase-8:bootstrap` → enter `AT` → verify files in `data/processed/country=AT/`.

## 4) Commit
`chore(tasks): add phase-8:bootstrap task + utils helper`
