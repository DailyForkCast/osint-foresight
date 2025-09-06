#!/usr/bin/env bash
set -euo pipefail
ISO2=${1:? "Usage: new_country.sh <ISO2> <Name> <Years>"}
NAME=${2:? "Country name e.g. Portugal"}
YEARS=${3:-"2015-2025"}
mkdir -p countries/$ISO2 reports/country=$ISO2 data/interim/country=$ISO2 data/processed/country=$ISO2 \
         data/raw/source=openaire/country=$ISO2 data/raw/source=crossref/country=$ISO2 \
         data/raw/source=crossref_event/country=$ISO2 data/raw/source=ietf/country=$ISO2 \
         data/raw/source=gleif/country=$ISO2 data/raw/source=opencorporates/country=$ISO2 \
         data/raw/source=patents/country=$ISO2
cat > countries/$ISO2/country.yaml <<YAML
country: $NAME
iso2: $ISO2
years: "$YEARS"
toggles:
  export_controls: EU_2021_821
  us_natsec_8: true
sectors: []
YAML
cat > countries/$ISO2/notes.md <<MD
# $NAME — Working Notes
- Open questions:
- Manual TODOs:
MD