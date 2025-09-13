# Lean Operator Pack — ChatGPT v3.1 (MCF‑enabled)

Minimal operator version for rapid reuse across countries.

---

## RUN CONTEXT
```
COUNTRY = {{country_name}}
TIMEFRAME = {{2015–present}}
HORIZONS = {{2y,5y,10y}}
LANG = {{EN + local + zh-CN}}
POLICY_WINDOW = {{2019–2025 inclusive}}
ARTIFACT_DIR = {{./artifacts/{{COUNTRY}}}}
```

---

## ARTIFACT CONTRACTS (Claude Code ↔ ChatGPT)
- Phase 1 Baseline: `phase1_baseline.json`
- Phase 2 Links & Standards: `phase2_links.json`, `standards_activity.json`
- Phase 2.5 MCF: `phase2_5_mcf.json`
- Supply Chain & Procurement Signals: `supply_chain_map.json`, `procurement_signals.csv`
- Phase 3 Risks: `phase3_risks.json`
- Phase 4 Vectors & Controls: `phase4_vectors.json`, `funding_controls_map.json`
- Phase 5 Scenarios: `phase5_scenarios.json`
- Phase 6 EWS: `phase6_ews.json`
- Phase 7C Concepts: `phase7c_concepts.json`
- Phase 7R Recommendations: `phase7r_recommendations.json`
- Phase 8 Implementation: `phase8_implementation.json`
- Adversary Simulation: `adversary_plan.json`

**Ingestion rule:** If an artifact exists in `ARTIFACT_DIR`, load/summarize it first; only compute if missing.

---

## JSON OUTPUT SHAPES (by phase)

### Phase 0 — Setup & Scope
```json
{
  "scope": {"country":"{{COUNTRY}}","timeframe":"2015–present","domains":["AI","quantum","semiconductors","biotech","space","advanced materials","autonomy","sensing","maritime","smart city"]},
  "assumptions":["..."],
  "constraints":["..."],
  "initial_hypotheses":["<=25w each, up to 5"]
}
```

### Phase 1 — Baseline Landscape
```json
{
  "actors": [{"name":"","type":"ministry|agency|SOE|university|institute|company","aka":["中文名","alias"],"notes":"<=25w"}],
  "funders": [{"name":"","type":"public|private|sovereign|foundation","programs":[""],"intl_links":["EU|NATO|..."]}],
  "policies":[{"title":"","year":2024,"summary":"<=25w","link":""}],
  "infrastructure":[{"asset":"","domain":"","role":"","risk_note":"<=25w"}]
}
```

### Phase 2 — Collaboration & Linkages
```json
{
  "links": [{"entity_a":"","entity_b":"","tie":"coauth|funding|MoU|standards|talent","start":"YYYY-MM","domain":"","evidence_url":"","confidence":"Med"}],
  "intl_partners":[{"country":"","org":"","domain":"","notes":"<=20w"}],
  "standards_activity":[{"body":"ISO|IEC|IEEE|ETSI|3GPP|ITU","wg":"","topic":"","role":"member|rapporteur|editor"}]
}
```

### Phase 2.5 — PRC Military‑Civil Fusion (MCF)
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

### Phase 3 — Risks & Vulnerabilities
```json
{
  "risks": [
    {
      "name":"",
      "domain":"AI|semis|quantum|biotech|space|materials|autonomy|sensing|maritime|smart city",
      "mechanism":"<=30w (who→what→how→to what end)",
      "prob":"30-60%",
      "impact":"High",
      "horizon":"5y",
      "indicators":["<=10w","<=10w"],
      "uncertainty":"<=20w"
    }
  ]
}
```

### Phase 4 — Acquisition & Finance Vectors
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

### Phase 5 — Scenarios & Foresight
```json
{
  "scenarios": [
    {"name":"Baseline","prob":"40-50%","drivers":[""],"indicators":["numeric or ratio"],"timeline":"2026–2029","summary":"<=180w"}
  ]
}
```

### Phase 6 — Early‑Warning System
```json
{
  "ews": {
    "metrics":[{"name":"","source":"","threshold":"","cadence":"weekly|monthly","owner":"role"}],
    "playbook":[{"trigger":"metric>threshold","action":"notify|investigate|pause collaboration","notes":"<=18w"}]
  }
}
```

### Phase 7C — Capacity‑Building Concepts
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

### Phase 7R — Recommendations & Roadmap Hooks
```json
{
  "recommendations": [
    {"id":"R1","what":"<=20w","who":"owner","when":"near|mid|long","cost":"$|$$|$$$","risk_addressed":"risk_id"}
  ],
  "open_questions":["<=20w each"],
  "next_best_data":["<=20w each"]
}
```

### Phase 8 — Implementation Plan
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

---

## EVIDENCE TABLE (CSV columns)
```
ClaimID,Claim (<=25w),SourceURL,PubDate,Lang,Corroboration (Y/N/Partial),Contradiction? (Y/N),Probability,Confidence,DataQuality (1–5)
```

