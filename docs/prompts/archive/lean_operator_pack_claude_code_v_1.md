# Lean Operator Pack — Claude Code v1.1

Minimal operator version aligned to ChatGPT v3.1. Focus: variable header, artifact contracts, and JSON shapes for all outputs.

---

## RUN CONTEXT (sync with ChatGPT)
```
COUNTRY = {{country_name}}
TIMEFRAME = {{2015–present}}
HORIZONS = {{2y,5y,10y}}
LANG = {{EN + local + zh-CN}}
POLICY_WINDOW = {{2019–2025 inclusive}}
ARTIFACT_DIR = {{./artifacts/{{COUNTRY}}}}
```

Shared scales (contract):
- Probability: "10-30%" | "30-60%" | "60-90%"
- Confidence: "Low" | "Med" | "High"
- DataQuality: 1–5

Evidence table columns (CSV):
```
ClaimID,Claim,SourceURL,PubDate,Lang,Corroboration,Contradiction,Probability,Confidence,DataQuality
```

---

## ARTIFACT CONTRACTS (file outputs)
- `phase1_baseline.json`
- `phase2_links.json`, `standards_activity.json`
- `phase2_5_mcf.json`
- `supply_chain_map.json`, `procurement_signals.csv`
- `phase3_risks.json`
- `phase4_vectors.json`, `funding_controls_map.json`
- `phase5_scenarios.json`
- `phase6_ews.json`
- `phase7c_concepts.json`
- `phase7r_recommendations.json`
- `phase8_implementation.json`
- `adversary_plan.json`
- `evidence_master.csv`, `validation_report.txt`

---

## JSON SHAPES (write exactly)

### Phase 1 — Baseline
```json
{
  "actors": [{"name":"","type":"ministry|agency|SOE|university|institute|company","aka":["中文名","alias"],"notes":"<=25w"}],
  "funders": [{"name":"","type":"public|private|sovereign|foundation","programs":[""],"intl_links":["EU|NATO|..."]}],
  "policies":[{"title":"","year":2024,"summary":"<=25w","link":""}],
  "infrastructure":[{"asset":"","domain":"","role":"","risk_note":"<=25w"}]
}
```

### Phase 2 — Links & Standards
```json
{
  "links": [{"entity_a":"","entity_b":"","tie":"coauth|funding|MoU|standards|talent","start":"YYYY-MM","domain":"","evidence_url":"","confidence":"Med"}],
  "intl_partners":[{"country":"","org":"","domain":"","notes":"<=20w"}],
  "standards_activity":[{"body":"ISO|IEC|IEEE|ETSI|3GPP|ITU","wg":"","topic":"","role":"member|rapporteur|editor"}]
}
```

### Phase 2.5 — MCF
```json
{
  "mcf_summary":"<=120 words",
  "actors":[{"name":"","aka":["中文名"],"role":"SOE|university|front","links":[{"to":"","type":"funding|lab|board|ownership","evidence_url":""}]}],
  "mechanisms":[{"type":"licit|gray|illicit","tech":"","event":"<=18w","date":"YYYY-MM","evidence_url":"","confidence":"Med"}],
  "indicators":[{"indicator":"","threshold":"numeric/qual band","status":"rising|stable|declining"}],
  "predictions":[{"horizon":"2y|5y|10y","claim":"<=25w","prob":"40-60%","confidence":"Med"}],
  "tech_taxonomy":[{"tech":"","maturity":"nascent|emerging|established","maturity_metric":{"TRL":7},"attractiveness":"Low|Med|High","barriers":[""],"signals":[{"what":"<=10w","date":"YYYY-MM","evidence_url":""}]}],
  "gaps":["<=20w each" ]
}
```

### Phase 3 — Risks
```json
{
  "risks": [
    {
      "name":"",
      "domain":"AI|semis|quantum|biotech|space|materials|autonomy|sensing|maritime|smart city",
      "mechanism":"<=30w",
      "prob":"30-60%",
      "impact":"High",
      "horizon":"5y",
      "indicators":["<=10w","<=10w"],
      "uncertainty":"<=20w"
    }
  ]
}
```

### Phase 4 — Vectors & Controls
```json
{
  "vectors": [{
    "type":"talent|standards|vc|lp|grant|procurement|cloud|ip_license|broker|shell_importer",
    "entities":[""],
    "jurisdictions":[""],
    "controls_hooks":["NSPM-33|EU|ITAR|EAR|other"],
    "notes":"<=25w",
    "evidence_url":""
  }]
}
```

### Phase 5 — Scenarios
```json
{
  "scenarios": [
    {"name":"Baseline","prob":"40-50%","drivers":[""],"indicators":["numeric or ratio"],"timeline":"2026–2029","summary":"<=180w"}
  ]
}
```

### Phase 6 — EWS
```json
{
  "ews": {
    "metrics":[{"name":"","source":"","threshold":"","cadence":"weekly|monthly","owner":"role"}],
    "playbook":[{"trigger":"metric>threshold","action":"notify|investigate|pause collaboration","notes":"<=18w"}]
  }
}
```

### Phase 7C — Concepts
```json
{
  "concepts": [
    {
      "type":"workshop|red_team|policy_sprint|table_top",
      "title":"",
      "audiences":["gov","university","institute","industry"],
      "length":"0.5–3 days",
      "goals":[""],
      "outcomes":[""],
      "inputs_needed":["docs|datasets"],
      "follow_on":"<=20w"
    }
  ]
}
```

### Phase 7R — Recommendations
```json
{
  "recommendations": [
    {"id":"R1","what":"<=20w","who":"owner","when":"near|mid|long","cost":"$|$$|$$$","risk_addressed":"risk_id"}
  ],
  "open_questions":["<=20w each"],
  "next_best_data":["<=20w each"]
}
```

### Phase 8 — Implementation
```json
{
  "implementation": {
    "timeline":[{"milestone":"","date":"YYYY-MM","owner":"role"}],
    "metrics":[{"name":"","target":"","freq":"quarterly"}],
    "risks":[{"risk":"","mitigation":"<=18w"}]
  }
}
```

### Adversary Simulation
```json
{
  "adversary_plan": [
    {"step":"goal","action":"<=12w","counter_indicator":"<=10w","countermeasure":"<=12w"}
  ]
}
```
