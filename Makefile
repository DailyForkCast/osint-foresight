COUNTRY ?= PT

pull: pull-openaire pull-crossref pull-ietf pull-gleif

pull-openaire:
	python -m src.pulls.openaire_pull --country $(COUNTRY) --years 2015-2025 --out data/raw/source=openaire/country=$(COUNTRY)

pull-crossref:
	python -m src.pulls.crossref_pull --country $(COUNTRY) --query-file queries/crossref/ai_hpc_oe.json --out data/raw/source=crossref/country=$(COUNTRY)

pull-ietf:
	python -m src.pulls.ietf_pull --country $(COUNTRY) --groups-file queries/ietf/wg_list.txt --out data/raw/source=ietf/country=$(COUNTRY)

pull-gleif:
	python -m src.pulls.gleif_pull --country $(COUNTRY) --out data/raw/source=gleif/country=$(COUNTRY)

normalize:
	python -m src.normalize.openaire_to_relationships --country $(COUNTRY)
	python -m src.normalize.crossref_to_relationships --country $(COUNTRY)
	python -m src.normalize.ietf_to_standards_roles --country $(COUNTRY)
	python -m src.normalize.gleif_to_cer --country $(COUNTRY)

build: normalize
	python -m src.analysis.phase2_landscape --country $(COUNTRY)
	python -m src.analysis.phase5_links --country $(COUNTRY)
	python -m src.analysis.phase7c_posture --country $(COUNTRY)

reports: build
	@echo "Reports generated under reports/country=$(COUNTRY)/"