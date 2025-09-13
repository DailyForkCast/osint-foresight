# SETUP — Environments & VS Code

## pip/venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
cp .env.example .env.local  # Add your API keys to .env.local

## conda/mamba
conda install -n base -c conda-forge mamba -y || true
mamba env create -f environment.yml || conda env create -f environment.yml
conda activate osint-foresight

## VS Code interpreter
Cmd/Ctrl+Shift+P → Python: Select Interpreter → choose `.venv` or `osint-foresight`.

## Common issues
- SSL/Certificates (macOS): `Install Certificates.command` under your Python folder.
- Proxy: export `HTTP_PROXY`/`HTTPS_PROXY` before pip/conda.
- Permissions: `chmod +x scripts/new_country.sh`.

## Pre-commit hooks (optional)
pip install pre-commit && pre-commit install