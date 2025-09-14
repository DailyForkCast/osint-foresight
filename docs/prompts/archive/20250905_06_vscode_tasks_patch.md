Below is a **drop‑in replacement** for `.vscode/tasks.json` that:
- keeps the **CHOOSE** sentinel (no default country),
- adds **CORDIS** pulls (online + offline),
- adds a **normalize:cordis** helper task,
- updates **normalize:all** to include `cordis_to_programs`, `cordis_to_relationships`, and `crossref_events_to_signals`,
- preserves all existing tasks and Windows PowerShell guards.

> Paste this content into `.vscode/tasks.json` (replacing the entire file). It's idempotent. Nothing runs until you pick a real country.

```json
{
  "version": "2.0.0",
  "options": { "shell": { "executable": "/bin/bash", "args": ["-lc"] } },
  "tasks": [
    {
      "label": "pull:openaire",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.openaire_pull --country ${input:country} --years 2015-2025 --out data/raw/source=openaire/country=${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.openaire_pull --country ${input:country} --years 2015-2025 --out data/raw/source=openaire/country=${input:country}"
      },
      "problemMatcher": []
    },
    {
      "label": "pull:crossref",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.crossref_pull --country ${input:country} --years 2015-2025 --out data/raw/source=crossref/country=${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.crossref_pull --country ${input:country} --years 2015-2025 --out data/raw/source=crossref/country=${input:country}"
      },
      "problemMatcher": []
    },
    {
      "label": "pull:crossref:event-data",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.crossref_event_pull --country ${input:country} --out data/raw/source=crossref_event/country=${input:country} --limit_dois 200",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.crossref_event_pull --country ${input:country} --out data/raw/source=crossref_event/country=${input:country} --limit_dois 200"
      },
      "problemMatcher": []
    },
    {
      "label": "pull:ietf",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.ietf_pull --country ${input:country} --groups-file queries/ietf/wg_list.txt --out data/raw/source=ietf/country=${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.ietf_pull --country ${input:country} --groups-file queries/ietf/wg_list.txt --out data/raw/source=ietf/country=${input:country}"
      },
      "problemMatcher": []
    },
    {
      "label": "pull:gleif",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.gleif_pull --country ${input:country} --out data/raw/source=gleif/country=${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.gleif_pull --country ${input:country} --out data/raw/source=gleif/country=${input:country}"
      },
      "problemMatcher": []
    },
    {
      "label": "pull:opencorporates",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.opencorporates_pull --country ${input:country} --api-token $OPENCORP_TOKEN --out data/raw/source=opencorporates/country=${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.opencorporates_pull --country ${input:country} --api-token $env:OPENCORP_TOKEN --out data/raw/source=opencorporates/country=${input:country}"
      },
      "problemMatcher": []
    },
    {
      "label": "pull:patents",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.patents_pull --country ${input:country} --years 2015-2025 --out data/raw/source=patents/country=${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.patents_pull --country ${input:country} --years 2015-2025 --out data/raw/source=patents/country=${input:country}"
      },
      "problemMatcher": []
    },

    {
      "label": "pull:cordis (online)",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.cordis_pull --country ${input:country} --out data/raw/source=cordis/country=${input:country} --mode online",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.cordis_pull --country ${input:country} --out data/raw/source=cordis/country=${input:country} --mode online"
      },
      "problemMatcher": []
    },
    {
      "label": "pull:cordis (offline)",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.pulls.cordis_pull --country ${input:country} --out data/raw/source=cordis/country=${input:country} --mode offline --source_file '${input:cordis_csv}'",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.pulls.cordis_pull --country ${input:country} --out data/raw/source=cordis/country=${input:country} --mode offline --source_file '${input:cordis_csv}'"
      },
      "problemMatcher": []
    },

    {
      "label": "normalize:cordis",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.normalize.cordis_to_programs --country ${input:country} && python -m src.normalize.cordis_to_relationships --country ${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.normalize.cordis_to_programs --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.cordis_to_relationships --country ${input:country}"
      },
      "problemMatcher": []
    },

    {
      "label": "normalize:all",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.normalize.openaire_to_relationships --country ${input:country} && python -m src.normalize.crossref_to_relationships --country ${input:country} && python -m src.normalize.crossref_events_to_signals --country ${input:country} && python -m src.normalize.ietf_to_standards_roles --country ${input:country} && python -m src.normalize.gleif_to_cer --country ${input:country} && python -m src.normalize.opencorp_to_mechanisms --country ${input:country} && python -m src.normalize.patents_to_mechanisms --country ${input:country} && python -m src.normalize.cordis_to_programs --country ${input:country} && python -m src.normalize.cordis_to_relationships --country ${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.normalize.openaire_to_relationships --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.crossref_to_relationships --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.crossref_events_to_signals --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.ietf_to_standards_roles --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.gleif_to_cer --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.opencorp_to_mechanisms --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.patents_to_mechanisms --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.cordis_to_programs --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.normalize.cordis_to_relationships --country ${input:country}"
      },
      "problemMatcher": []
    },

    {
      "label": "build:phases",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python -m src.analysis.phase2_landscape --country ${input:country} && python -m src.analysis.phase3_institutions --country ${input:country} && python -m src.analysis.phase4_funders --country ${input:country} && python -m src.analysis.phase5_links --country ${input:country} && python -m src.analysis.phase6_risk --country ${input:country} && python -m src.analysis.phase7c_posture --country ${input:country} && python -m src.analysis.phase8_foresight --country ${input:country}",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python -m src.analysis.phase2_landscape --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.analysis.phase3_institutions --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.analysis.phase4_funders --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.analysis.phase5_links --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.analysis.phase6_risk --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.analysis.phase7c_posture --country ${input:country}; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; python -m src.analysis.phase8_foresight --country ${input:country}"
      },
      "problemMatcher": []
    },

    {
      "label": "report:all",
      "type": "shell",
      "command": "c='${input:country}'; if [ \"$c\" = 'CHOOSE' ]; then echo 'Please select a valid ISO2 country code.'; exit 2; fi; python - <<'PY'\nfrom src.analysis import phase2_landscape, phase3_institutions, phase4_funders, phase5_links, phase6_risk, phase7c_posture, phase8_foresight\n# Each module writes its own markdown report under reports/country=${'${input:country}'}\nPY",
      "windows": {
        "command": "$c='${input:country}'; if ($c -eq 'CHOOSE') { Write-Host 'Please select a valid ISO2 country code.'; exit 2 }; python - <<'PY'\nfrom src.analysis import phase2_landscape, phase3_institutions, phase4_funders, phase5_links, phase6_risk, phase7c_posture, phase8_foresight\n# Each module writes its own markdown report under reports/country=${'${input:country}'}\nPY"
      },
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "country",
      "type": "pickString",
      "description": "ISO2 country code",
      "options": [
        "CHOOSE",
        "AL","AM","AT","AZ","BE","BG","CH","CY","CZ","DE","DK","EE","ES","FI","FR","GB",
        "GE","GR","HR","HU","IE","IS","IT","LT","LU","LV","MK","MT","NL","NO","PL","PT",
        "RO","RS","SE","SI","SK","TR"
      ]
    },
    {
      "id": "cordis_csv",
      "type": "promptString",
      "description": "Path to exported CORDIS participants CSV (for pull:cordis offline)",
      "default": ""
    }
  ]
}
