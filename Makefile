# Makefile — Merged (original + expanded)
# CLI parity with VS Code tasks; no default COUNTRY. Usage examples:
#   make pull COUNTRY=SE
#   make normalize-all COUNTRY=SE
#   make build COUNTRY=SE
#   make build-all COUNTRY=SE

SHELL := /bin/bash

# ---- Guard: require COUNTRY and disallow CHOOSE ----
.PHONY: guard-country
guard-country:
	@if [ -z "$(COUNTRY)" ] || [ "$(COUNTRY)" = "CHOOSE" ]; then \
	  echo "Please set COUNTRY=<ISO2> (e.g., COUNTRY=PT) and not CHOOSE."; \
	  exit 2; \
	fi

# ---------------- Pulls ----------------
.PHONY: pull pull-openaire pull-crossref pull-crossref-affil pull-eventdata pull-ietf pull-gleif pull-opencorp pull-patents pull-cordis-online pull-cordis-offline

# Meta-pull: the core online pulls most phases rely on
pull: guard-country pull-openaire pull-crossref pull-ietf pull-gleif

# Your original
pull-openaire: guard-country
	python -m src.pulls.openaire_pull --country $(COUNTRY) --years 2015-2025 --out data/raw/source=openaire/country=$(COUNTRY)

# Crossref — keep your query-file workflow, with a safe fallback to affiliation-mode if QUERY_FILE is missing
# Usage:
#   make pull-crossref COUNTRY=SE QUERY_FILE=queries/crossref/ai_hpc_oe.json
pull-crossref: guard-country
	if [ -n "$(QUERY_FILE)" ] && [ -f "$(QUERY_FILE)" ]; then \
	  python -m src.pulls.crossref_pull --country $(COUNTRY) --query-file "$(QUERY_FILE)" --out data/raw/source=crossref/country=$(COUNTRY); \
	else \
	  echo "[info] QUERY_FILE not provided/found; using affiliation-mode (2015–2025)."; \
	  python -m src.pulls.crossref_pull --country $(COUNTRY) --years 2015-2025 --out data/raw/source=crossref/country=$(COUNTRY); \
	fi

# Optional: explicit affiliation-mode target
pull-crossref-affil: guard-country
	python -m src.pulls.crossref_pull --country $(COUNTRY) --years 2015-2025 --out data/raw/source=crossref/country=$(COUNTRY)

# Crossref Event Data (signals); limit configurable
# Usage: make pull-eventdata COUNTRY=SE LIMIT=200
LIMIT ?= 200
pull-eventdata: guard-country
	python -m src.pulls.crossref_event_pull --country $(COUNTRY) --out data/raw/source=crossref_event/country=$(COUNTRY) --limit_dois $(LIMIT)

pull-ietf: guard-country
	python -m src.pulls.ietf_pull --country $(COUNTRY) --groups-file queries/ietf/wg_list.txt --out data/raw/source=ietf/country=$(COUNTRY)

pull-gleif: guard-country
	python -m src.pulls.gleif_pull --country $(COUNTRY) --out data/raw/source=gleif/country=$(COUNTRY)

# Additional sources (optional but wired-up in tasks/normalizers)
pull-opencorp: guard-country
	python -m src.pulls.opencorporates_pull --country $(COUNTRY) --out data/raw/source=opencorporates/country=$(COUNTRY)

pull-patents: guard-country
	python -m src.pulls.patents_pull --country $(COUNTRY) --years 2015-2025 --out data/raw/source=patents/country=$(COUNTRY)

pull-cordis-online: guard-country
	python -m src.pulls.cordis_pull --country $(COUNTRY) --out data/raw/source=cordis/country=$(COUNTRY) --mode online

# Example: make pull-cordis-offline COUNTRY=PT CSV=/path/to/cordis_participants.csv
pull-cordis-offline: guard-country
	@if [ -z "$(CSV)" ]; then echo "Provide CSV=/path/to/cordis_participants.csv"; exit 2; fi
	python -m src.pulls.cordis_pull --country $(COUNTRY) --out data/raw/source=cordis/country=$(COUNTRY) --mode offline --source_file "$(CSV)"

# ---------------- Normalization ----------------
.PHONY: normalize normalize-all normalize-cordis

# Your original set (kept as-is)
normalize: guard-country
	python -m src.normalize.openaire_to_relationships --country $(COUNTRY)
	python -m src.normalize.crossref_to_relationships --country $(COUNTRY)
	python -m src.normalize.ietf_to_standards_roles --country $(COUNTRY)
	python -m src.normalize.gleif_to_cer --country $(COUNTRY)

# Full normalization chain including signals & additional sources
normalize-all: guard-country
	python -m src.normalize.openaire_to_relationships --country $(COUNTRY) && \
	python -m src.normalize.crossref_to_relationships --country $(COUNTRY) && \
	python -m src.normalize.crossref_events_to_signals --country $(COUNTRY) && \
	python -m src.normalize.ietf_to_standards_roles --country $(COUNTRY) && \
	python -m src.normalize.gleif_to_cer --country $(COUNTRY) && \
	python -m src.normalize.opencorp_to_mechanisms --country $(COUNTRY) && \
	python -m src.normalize.patents_to_mechanisms --country $(COUNTRY) && \
	python -m src.normalize.cordis_to_programs --country $(COUNTRY) && \
	python -m src.normalize.cordis_to_relationships --country $(COUNTRY)

normalize-cordis: guard-country
	python -m src.normalize.cordis_to_programs --country $(COUNTRY) && \
	python -m src.normalize.cordis_to_relationships --country $(COUNTRY)

# ---------------- Build Reports ----------------
.PHONY: build build-all reports help

# Your original build (phases 2,5,7C)
build: guard-country normalize
	python -m src.analysis.phase2_landscape --country $(COUNTRY)
	python -m src.analysis.phase5_links --country $(COUNTRY)
	python -m src.analysis.phase7c_posture --country $(COUNTRY)

# Full build across 2–8
build-all: guard-country normalize-all
	python -m src.analysis.phase2_landscape --country $(COUNTRY) && \
	python -m src.analysis.phase3_institutions --country $(COUNTRY) && \
	python -m src.analysis.phase4_funders --country $(COUNTRY) && \
	python -m src.analysis.phase5_links --country $(COUNTRY) && \
	python -m src.analysis.phase6_risk --country $(COUNTRY) && \
	python -m src.analysis.phase7c_posture --country $(COUNTRY) && \
	python -m src.analysis.phase8_foresight --country $(COUNTRY)

reports: build
	@echo "Reports generated under reports/country=$(COUNTRY)/"

# ---------------- Convenience ----------------
help:
	@echo "Targets:"; \
	echo "  pull (openaire, crossref, ietf, gleif)"; \
	echo "  pull-openaire / pull-crossref [/ pull-crossref-affil] / pull-eventdata / pull-ietf / pull-gleif / pull-opencorp / pull-patents"; \
	echo "  pull-cordis-online / pull-cordis-offline CSV=/path/to/file.csv"; \
	echo "  normalize (original set) / normalize-all (full chain) / normalize-cordis"; \
	echo "  build (2,5,7C) / build-all (2–8) / reports"; \
	echo "Use: make <target> COUNTRY=<ISO2> [QUERY_FILE=... LIMIT=...]";