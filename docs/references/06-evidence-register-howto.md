# Evidence Register v2 — How to Log

**CSV headers:**
```
evidence_id,source_name,source_url,captured_at_iso,filter_params,language,source_tier(A/B/C),reliability_note,stale_flag(>18m|>36m),screenshot_path,country
```

**What goes in each field:**
- `filter_params` — exact query string or API params used (copy‑pasteable)
- `screenshot_path` — path under `evidence/screenshots/` proving the filter & timestamp
- `source_tier` — A=primary/official, B=reputable aggregator, C=secondary/blog
- `stale_flag` — compute from `captured_at_iso` or source's last updated date

**Example row:**
```
EV-2025-09-05-0001,OpenAIRE Graph,https://api.openaire.eu/v1/graph/search/researchProducts,2025-09-05T12:34:56Z,"relOrganizationCountryCode=PT,CN&title=(AI OR HPC)",EN,A,,>18m,evidence/screenshots/EV-2025-09-05-0001.png,PT
```