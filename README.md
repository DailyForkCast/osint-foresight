# OSINT Foresight — Multi-country Stack

This repo runs Phases 0–8 (+7C/7R/X) country by country using shared collectors, schemas and reports. Data is partitioned by `source=/country=/date=` for auditability.

## Quick start
### Option 1 — pip/venv
python3 -m venv .venv && source .venv/bin/activate && python -m pip install -U pip && pip install -r requirements.txt

### Option 2 — conda/mamba
mamba env create -f environment.yml || conda env create -f environment.yml
conda activate osint-foresight

### Configure API keys (optional)
cp .env.example .env.local
# Edit .env.local to add your API keys

### First country
chmod +x scripts/new_country.sh
./scripts/new_country.sh PT Portugal 2015-2025

### Run pipeline (stubs)
# In VS Code: Tasks → pull:openaire → normalize:all → build:phases
# Or Make: make COUNTRY=PT pull && make COUNTRY=PT build

Outputs land in `data/processed/country=PT/` and `reports/country=PT/`.

See **docs/references/** for official links, recipes, and Evidence Register how‑tos.