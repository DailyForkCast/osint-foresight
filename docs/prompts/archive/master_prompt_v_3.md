# Master Prompt v3.1 (MCF‑enabled)

> **Purpose:** A complete, execution‑ready OSINT + analysis framework for dual‑use research security with a dedicated **PRC Military‑Civil Fusion (MCF)** module, stricter sourcing, unambiguous scales, compact JSON outputs per phase, adversary simulation, and early‑warning design.
>
> **Model stance:** Analyze, don’t advocate. Note uncertainty. When evidence is weak, halt and surface gaps instead of speculating.

---

## RUN CONTEXT (set before each run)
```
COUNTRY = {{country_name}}
TIMEFRAME = {{2015–present}}
HORIZONS = {{2y,5y,10y}}
LANG = {{EN + local + zh-CN}}   # Work natively in EN. When source is local/中文, cite lang and summarize in EN.
POLICY_WINDOW = {{2019–2025 inclusive}}  # Use this window when extracting/reviewing policy docs
ARTIFACT_DIR = {{./artifacts/{{COUNTRY}}}}  # Where Claude Code saves JSON/CSV artifacts for ingestion
```

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

**Ingestion rule:** If an artifact exists in `ARTIFACT_DIR`, **load and summarize** it first; only compute from scratch if missing.

### TOGGLES
```
TOGGLES = {
  INCLUDE_MCF: true,                 # Add full Phase 2.5 below
  INCLUDE_EXPORT_CONTROLS: true,     # Map export‑control + research integrity hooks where relevant
  INCLUDE_FINANCE_VECTORS: true,     # VC/PE/LP, grants, procurement, compute credits, cloud, etc.
  INCLUDE_SUPPLY_CHAIN: true,        # Tooling, reagents, EDA/CAD, specialized parts, logistics signals
  INCLUDE_ADVERSARY_SIM: true        # Inject dedicated adversary simulation micro‑phase
}
```

### CITATION RULES (mandatory)
- Corroborate **moderate+** claims with **≥2 independent sources**; include URL + publication date.
- Prefer primary/official docs; record **language** (EN/local/中文) and **translation caveats**.
- **Freshness window:** prioritize items **≤36 months** old unless historical context is required.
- Every non‑obvious claim gets an inline citation pointer in the evidence table.

### SCALES (use consistently)
- **Probability:** Low **10–30%**, Medium **30–60%**, High **60–90%**.
- **Confidence:** Low **30–60%**, Medium **60–80%**, High **80–95%**.
- **Data Quality (1–5):** 1=rumor/uncorroborated; 2=single low‑cred source; 3=mixed/secondary; 4=multi independent secondary/partial primary; 5=primary official or multi‑source convergence.

### PROHIBITED / STOP CONDITIONS
- If evidence is **insufficient**, **halt** that sub‑task and output **OpenQuestions** + **Next‑Best‑Data** instead of conjecture.
- Flag contradictions explicitly.

### UNIVERSAL OUTPUT STYLE
- Keep prose tight and skimmable. Use bullets. For JSON blocks, conform exactly to requested schema.
- When a phase requires both prose + JSON, **put JSON last** under a heading **Output (JSON)**.
- Word caps: **≤180 words** per scenario or finding where noted.

### EVIDENCE TABLE (use/append throughout)
```
| ClaimID | Claim (≤25w) | SourceURL | PubDate | Lang | Corroboration (Y/N/Partial) | Contradiction? | Probability | Confidence | DataQuality(1–5) |
```

---

## PHASE 0 — Setup & Scope
**Task:** Confirm scope, tech domains, and constraints. Define what success looks like.

**Deliver:**
- Scope notes (country context, key sectors, stakeholders).
- Assumptions + constraints.
- Initial risk hypotheses (≤5 bullets).

**Output (JSON):**
```json
{
  "scope": {"country":"{{COUNTRY}}","timeframe":"2015–present","domains":["AI","quantum","semiconductors","biotech","space","advanced materials","autonomy","sensing","maritime","smart city"]},
  "assumptions":["..."],
  "constraints":["..."],
  "initial_hypotheses":["<=25 words each, up to 5"]
}
```

---

## PHASE 1 — Baseline Landscape (Actors, Policies, Infrastructure)
**Task:** Establish who/what matters domestically and internationally.

**Include:** government actors, funders, institutes/universities/labs, major programs, relevant laws/strategies, key infrastructure, known partnerships (EU/NATO/others), disclosure regimes; **policies enacted/updated **2019–2025 (inclusive)**.**

**Output (JSON):**
```json
{
  "actors": [{"name":"","type":"ministry|agency|SOE|university|institute|company","aka":["中文名","alias"],"notes":"<=25w"}],
  "funders": [{"name":"","type":"public|private|sovereign|foundation","programs":[""],"intl_links":["EU|NATO|..."]}],
  "policies":[{"title":"","year":2023,"summary":"<=25w","link":""}],
"policy_window_note":"Include policies enacted/updated 2019–2025 inclusive"
  "infrastructure":[{"asset":"","domain":"","role":"","risk_note":"<=25w"}]
}
```

---

## PHASE 2 — Collaboration & Linkages (Domestic/Intl)
**Task:** Map research collaborations, co‑authorships, joint labs/MoUs, talent flows, standards body participation, grant/program linkages.

**Output (JSON):**
```json
{
  "links": [{"entity_a":"","entity_b":"","tie":"coauth|funding|MoU|standards|talent","start":"YYYY-MM","domain":"","evidence_url":"","confidence":"Med"}],
  "intl_partners":[{"country":"","org":"","domain":"","notes":"<=20w"}],
  "standards_activity":[{"body":"ISO|IEC|3GPP|ITU|IEEE|ETSI|CEN/CENELEC","wg":"","topic":"","role":"member|rapporteur|editor"}]
}
```

---

## PHASE 2.5 — **PRC Military‑Civil Fusion (MCF) — Dual‑Use Acquisition Lens**
*(Enabled when `INCLUDE_MCF:true`)*

### 1) Motivations & Doctrine
- Objectives (economic, security, tech parity), doctrinal anchors, S&T planning linkages. Rate **Confidence** and **Data Quality**.

### 2) Policy & Governance Framework
- National → provincial → institutional bodies; implementation pathways (funding, standards, procurement).

### 3) Actor & Network Map (Entity Resolution)
- SOEs, defense primes, private “champions,” universities/institutes, joint labs, front companies. Track **AKA/中文名** and role.

### 4) Acquisition Mechanisms (tag each item)
- **Licit:** joint research, standards, open funding, IP licensing, equipment purchases.
- **Gray zone:** talent programs, undisclosed affiliations/dual appointments, paper→prototype, “civilian” labs with defense end‑use.
- **Illicit:** export‑control circumvention, straw buyers, cyber theft, end‑use misstatement, sanctions evasion.

### 5) Target Tech Taxonomy
- Map to broader domains; assess maturity in **{{COUNTRY}}**, attractiveness to MCF, barriers, recent signals.
  - **Maturity:** choose scale (nascent|emerging|established) **or** TRL 1–9; state which you used.
  - **Attractiveness:** Low|Med|High + 1–2 drivers (e.g., PLA demand, supply gaps).
  - **Barriers:** up to 3 (export controls, capex, talent, IP regime, standards).
  - **Recent signals:** 2–3 concrete items with **evidence_url** and **YYYY‑MM**.

### 6) Progress to Date
- Notable projects, patents, co‑authorships, procurement trails, shipments, standards proposals; outcomes.

### 7) Early‑Warning Indicators (with thresholds)
- Examples: spikes in co‑authorships with MCF‑linked labs; repeat specialized equipment orders to proxies; sudden niche WG activity.

### 8) 2y/5y/10y Predictions
- Vectors likely to expand; choke points; expected policy shifts. Include **Prob** + **Confidence**.

### 9) Evidence & Gaps
- Append to Evidence Table; list contradictions; produce OpenQuestions + Next‑Best‑Data.

**Output (JSON):**
```json
{
  "mcf_summary":"<=120 words",
  "actors":[{"name":"","aka":["中文名"],"role":"SOE|university|front","links":[{"to":"","type":"funding|lab|board|ownership","evidence_url":""}]}],
  $1
  "tech_taxonomy":[{"tech":"","maturity":"nascent|emerging|established","maturity_metric":{"TRL":7},"attractiveness":"Low|Med|High","barriers":[""],"signals":[{"what":"<=10w","date":"YYYY-MM","evidence_url":""}]}],
  "indicators":[{"indicator":"","threshold":"numeric/qual band","status":"rising|stable|declining"}],
  "predictions":[{"horizon":"2y|5y|10y","claim":"<=25w","prob":"40-60%","confidence":"Med"}],
  "gaps":["<=20w each" ]
}
```

---

## PHASE 3 — Risks & Vulnerabilities (Per Domain)
**Task:** Identify concrete risk items with causal pathways.

**For each risk (cap: 6):**
- **Mechanism** (who → what → how → to what end) in **one sentence**.
- **Probability**, **Impact (Low/Med/High)**, **Horizon (2y/5y/10y)**, **Uncertainty** (key unknowns).
- **Indicators** (1–2 numeric if possible).

**Output (JSON):**
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

---

## PHASE 4 — Acquisition & Finance Vectors (+ Export/Integrity Hooks)
**Task:** Trace pathways enabling access: funding, equity/LP, grant programs, standards, procurement/brokers, compute credits/cloud, training/talent, IP licensing; include **export‑control** and **research integrity** (disclosure/COI) touch‑points.

**Output (JSON):**
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

---

## PHASE 5 — Scenarios & Foresight
**Task:** Build **≤4** distinct scenarios with unique branching points.

**Each scenario (≤180 words) includes:** drivers, branch points, **1–2 numeric indicators**, implications for research security, and monitoring suggestions.

**Output (JSON):**
```json
{
  "scenarios": [
    {"name":"Baseline","prob":"40-50%","drivers":[""],"indicators":["numeric or ratio"],"timeline":"2026–2029","summary":"<=180w"}
  ]
}
```

---

## PHASE 6 — Early‑Warning System (EWS) & Monitoring Plan
**Task:** Turn indicators into a living plan with thresholds and cadence.

**Deliver:** dashboard metric list, data sources, collection cadence, alert thresholds, ownership (who watches), and “playbook” actions.

**Output (JSON):**
```json
{
  "ews": {
    "metrics":[{"name":"","source":"","threshold":"","cadence":"weekly|monthly","owner":"role"}],
    "playbook":[{"trigger":"metric>threshold","action":"notify|investigate|pause collaboration","notes":"<=18w"}]
  }
}
```

---

## PHASE 7C — Capacity‑Building Concepts (Externally Deliverable)
**Task:** Design **1–3** high‑leverage activities (workshop, red‑team/table‑top, policy sprint, monitoring sprint).

**Output (JSON):**
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

---

## PHASE 7R — Recommendations & Roadmap Hooks
**Task:** Actionable recommendations tied to risks, controls, and feasibility.

**Output (JSON):**
```json
{
  "recommendations": [
    {"id":"R1","what":"<=20w","who":"owner","when":"near|mid|long","cost":"$|$$|$$$","risk_addressed":"risk_id"}
  ],
  "open_questions":["<=20w each"],
  "next_best_data":["<=20w each"]
}
```

---

## PHASE 8 — Implementation Plan & Metrics
**Task:** Timeline, milestones, success metrics, and governance for execution by outside orgs.

**Output (JSON):**
```json
{
  "implementation": {
    "timeline":[{"milestone":"","date":"YYYY-MM","owner":"role"}],
    "metrics":[{"name":"","target":"","freq":"quarterly"}],
    "risks":[{"risk":"","mitigation":"<=18w"}]
  }
}
```

---

## ADVERSARY SIMULATION (MCF Planner in {{COUNTRY}})
*(Enabled when `INCLUDE_ADVERSARY_SIM:true`; cross‑reference Phases 3–6)*

**Task:** “If I were an MCF planner targeting {{COUNTRY}} in domain X, how would I proceed?”

**Steps:** goal selection → access vector → partner identification → front setup → funding route → data/equipment flow → exploitation path. For each step, propose a **counter‑indicator** and **countermeasure**.

**Output (JSON):**
```json
{
  "adversary_plan": [
    {"step":"goal","action":"<=12w","counter_indicator":"<=10w","countermeasure":"<=12w"}
  ]
}
```

---

## ANNEX A — Early‑Warning Indicator Categories (Universal Checklist)
- **Research ties:** co‑authorship spikes with defense‑linked orgs; repeat patterns in dual appointments.
- **Funding flows:** sudden grants/LP entries from opaque vehicles; cross‑border JV formation.
- **Standards activity:** new WG proposals in niche areas; rapporteur/editor roles.
- **Procurement & shipments:** specialized tooling/reagent orders via proxies; end‑use mismatches.
- **IP & licensing:** unusual patent assignments; license outs in sensitive domains.
- **Talent programs:** undisclosed affiliations; recruitment to targeted labs.
- **Cloud/compute:** bulk credit usage anomalies; GPU rental spikes tied to shell entities.
- **Fronts & shells:** beneficial ownership patterns; shared addresses/directors across proxies.
- **Cyber/illicit:** intrusion attempts aligned to research timelines; data exfil indicators.

---

## ANNEX B — Definitions (Operational)
- **Pattern identification / Trend analysis:** Specify the test (e.g., Mann‑Kendall, t‑test). Provide N, p‑value or effect size; if not applicable, state “descriptive only”.
- **Internationally competitive:** Competitive **globally** or **regionally vs peer economies** (state which). Explain why that still matters for talent/targeting.

---

## ANNEX C — JSON Field Reference (Quick)
- **prob:** one of the probability bands (string).
- **confidence:** one of Low/Med/High.
- **DataQuality:** integer 1–5.

---

## WORKFLOW NOTES
0) **Ingest artifacts** from `ARTIFACT_DIR` (see Artifact Contracts). Use them as ground truth inputs.
1) Execute phases sequentially when artifacts are absent or stale.
2) Keep the Evidence Table growing across phases.
3) When a toggle is **false**, skip that block and note the skip in output.
4) When gaps block progress, return **OpenQuestions** and **Next‑Best‑Data**.

---

## FINAL PACKAGE (per run)
- Phase outputs (JSON) concatenated.
- Evidence Table.
- 1‑page executive summary (≤250 words) highlighting **top 3 risks**, **top 3 recommendations**, and **two biggest unknowns**.
