# Master Prompt v3.4 (MCF‑enabled with Phase 9 & 10)

> **Purpose:** A complete, execution‑ready OSINT + analysis framework for dual‑use research security with a dedicated **PRC Military‑Civil Fusion (MCF)** module, stricter sourcing, unambiguous scales, compact JSON outputs per phase, adversary simulation, early‑warning design, and complete closeout procedures.
>
> **Model stance:** Analyze, don't advocate. Note uncertainty. When evidence is weak, halt and surface gaps instead of speculating.

---

## RUN CONTEXT (set before each run)
```
COUNTRY = {{country_name}}
TIMEFRAME = {{2015–present}}
HORIZONS = {{2y,5y,10y}}
LANG = {{EN + local + zh-CN}}   # Work natively in EN. When source is local/中文, cite lang and summarize in EN.
```

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

**Include:** government actors, funders, institutes/universities/labs, major programs, relevant laws/strategies, key infrastructure, known partnerships (EU/NATO/others), disclosure regimes.

**Output (JSON):**
```json
{
  "actors": [{"name":"","type":"ministry|agency|SOE|university|institute|company","aka":["中文名","alias"],"notes":"<=25w"}],
  "funders": [{"name":"","type":"public|private|sovereign|foundation","programs":[""],"intl_links":["EU|NATO|..."]}],
  "policies":[{"title":"","year":2023,"summary":"<=25w","link":""}],
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
- SOEs, defense primes, private "champions," universities/institutes, joint labs, front companies. Track **AKA/中文名** and role.

### 4) Acquisition Mechanisms (tag each item)
- **Licit:** joint research, standards, open funding, IP licensing, equipment purchases.
- **Gray zone:** talent programs, undisclosed affiliations/dual appointments, paper→prototype, "civilian" labs with defense end‑use.
- **Illicit:** export‑control circumvention, straw buyers, cyber theft, end‑use misstatement, sanctions evasion.

### 5) Target Tech Taxonomy
- Map to broader domains; assess maturity in **{{COUNTRY}}**, attractiveness to MCF, barriers, recent signals.

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
  "mechanisms":[{"type":"licit|gray|illicit","tech":"","event":"<=18w","date":"YYYY-MM","evidence_url":"","confidence":"Med"}],
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

**Deliver:** dashboard metric list, data sources, collection cadence, alert thresholds, ownership (who watches), and "playbook" actions.

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

## PHASE 9 — Foresight & Early Warning (2y/5y/10y)
**Task:** Forecast technology trajectories, geopolitical shifts, market dynamics with probabilistic scenarios and early warning indicators.

**For each horizon:**
- Technology maturation pathways
- Convergence possibilities  
- Structural shifts
- Wild cards (low prob, high impact)
- Observable indicators with thresholds

**Additional elements to strengthen Phase 9:**
- **Technology readiness levels (TRL)** progression estimates
- **Regulatory evolution** predictions (standards, controls, disclosure requirements)
- **Talent pipeline** forecasts (graduation rates, skill gaps, migration patterns)
- **Infrastructure dependencies** (compute, facilities, test beds)
- **Geopolitical scenarios** affecting tech access
- **Climate/sustainability** impacts on tech priorities
- **Social acceptance** trajectories for emerging tech

**Output (JSON):**
```json
{
  "foresight": {
    "2y": {
      "trends": [{"tech":"","trajectory":"<=25w","prob":"60-80%","indicators":["<=15w"],"trl_progression":"3→5"}],
      "risks": [{"risk":"","prob":"30-60%","trigger":"<=20w","early_signals":["<=10w"]}],
      "opportunities": [{"opp":"","enablers":["<=10w"],"barriers":["<=10w"],"window":"Q3_2026-Q2_2027"}],
      "regulatory": [{"change":"","jurisdiction":"","impact":"<=20w","prob":"50-70%"}]
    },
    "5y": {
      "convergences": [{"domains":["AI","quantum"],"outcome":"<=25w","prob":"40-60%","dependencies":["<=15w"]}],
      "structural_shifts": [{"shift":"","drivers":["<=15w"],"impacts":["<=15w"],"irreversibility":"high|med|low"}],
      "decision_points": [{"decision":"","date":"YYYY","implications":"<=25w","path_dependency":"<=15w"}],
      "talent": [{"gap":"","magnitude":"# people","mitigation_time":"years","source":"domestic|import"}]
    },
    "10y": {
      "paradigms": [{"shift":"","prob":"20-40%","precursors":["<=15w"],"tipping_point":"<=20w"}],
      "wild_cards": [{"event":"","prob":"5-20%","impact":"catastrophic|severe|moderate","early_signals":["<=15w"],"mitigation":"<=20w"}],
      "strategic_positioning": [{"domain":"","options":["specialize","partner","divest"],"rationale":"<=30w","dependencies":["<=15w"]}],
      "sustainability": [{"factor":"climate|resource|social","impact_on_tech":"<=25w","adaptation_needed":"<=20w"}]
    },
    "monitoring": {
      "leading": [{"indicator":"","source":"","threshold":"","lead_time":"6-12mo","collection_method":"api|scrape|manual"}],
      "coincident": [{"indicator":"","source":"","frequency":"daily|weekly|monthly","alert_mechanism":"email|dashboard|sms"}],
      "lagging": [{"indicator":"","source":"","confirms":"","validation_period":"3-6mo"}],
      "weak_signals": [{"signal":"","detection_method":"<=15w","interpretation":"<=20w","action_trigger":"<=15w"}]
    }
  }
}
```

---

## PHASE 10 — Go-Live & Closeout
**Task:** Final packaging, governance handoff, implementation readiness, and post-implementation review setup.

**Deliverables:**
- Executive decision package
- Implementation tracker with RACI matrix
- Risk heatmap with mitigation status
- Monitoring dashboard specification
- Governance structure & charter
- Success criteria & KPIs
- Post-implementation review schedule
- Knowledge transfer package
- Continuity planning

**Additional elements for complete Phase 10:**
- **Change management** plan
- **Communication strategy** (internal/external)
- **Contingency protocols** for critical failures
- **Lessons learned** capture process
- **Archive requirements** for documentation
- **Legal/compliance** sign-offs needed
- **Budget reconciliation** and future funding needs
- **Stakeholder acceptance** criteria

**Output (JSON):**
```json
{
  "closeout": {
    "decision_package": {
      "decisions_required": [{"decision":"<=25w","owner":"","deadline":"YYYY-MM-DD","options":["<=15w"],"recommendation":"<=20w"}],
      "policy_instruments": [{"instrument":"<=20w","status":"draft|approved|enacted","owner":"","enforcement":"<=15w"}],
      "resource_requirements": [{"type":"budget|personnel|infrastructure","amount":"","justification":"<=25w","approval_status":"pending|approved"}],
      "dependencies": [{"dependency":"<=15w","criticality":"high|med|low","mitigation":"<=20w"}]
    },
    "governance": {
      "structure": [{"body":"board|committee|wg","chair":"","members":[""],"cadence":"weekly|monthly|quarterly","charter_ref":""}],
      "escalation": [{"level":"operational|tactical|strategic","trigger":"<=20w","owner":"","sla":"hours|days"}],
      "reporting": [{"report":"","frequency":"","audience":"","format":"dashboard|memo|briefing","distribution":"<=15w"}],
      "decision_rights": [{"decision_type":"<=15w","authority":"","consultation_required":[""],"documentation":"<=10w"}]
    },
    "success_metrics": {
      "kpis": [{"metric":"","baseline":"","target":"","timeline":"","owner":"","measurement_method":"<=20w"}],
      "milestones": [{"milestone":"<=20w","date":"YYYY-MM-DD","criteria":"<=25w","verification":"","contingency":"<=20w"}],
      "risk_tolerance": [{"risk":"","acceptable_level":"","review_trigger":"","escalation":"<=15w"}],
      "benefits_realization": [{"benefit":"<=20w","measure":"","timeline":"","owner":"","tracking":"<=15w"}]
    },
    "handover": {
      "deliverables": [{"item":"","format":"","location":"","owner":"","retention_period":""}],
      "training": [{"audience":"","content":"<=25w","duration":"hours|days","completion_by":"YYYY-MM-DD","certification":"Y|N"}],
      "support": [{"type":"helpdesk|consultation|review","duration":"30|60|90 days","provider":"","sla":"<=15w"}],
      "knowledge_transfer": [{"topic":"<=15w","method":"documentation|workshop|shadowing","recipient":"","completion":"YYYY-MM-DD"}]
    },
    "pir_schedule": {
      "reviews": [{"timing":"T+30|T+90|T+180 days","scope":"<=25w","owner":"","deliverable":"","stakeholders":[""]}],
      "criteria": [{"criterion":"<=20w","measurement":"","threshold":"","action_if_unmet":"<=20w"}],
      "adjustments": [{"trigger":"<=20w","process":"<=25w","approver":"","documentation":"<=15w"}],
      "lessons_learned": [{"category":"process|technical|organizational","capture_method":"<=20w","repository":"","access":"<=10w"}]
    },
    "continuity": {
      "succession": [{"role":"","primary":"","backup":"","handover_period":"days"}],
      "documentation": [{"doc_type":"","location":"","update_frequency":"","owner":""}],
      "contingency": [{"scenario":"<=20w","response":"<=25w","activation":"<=15w","communication":"<=15w"}],
      "archive": [{"content":"","format":"","location":"","retention":"years","destruction_date":"YYYY-MM"}]
    }
  }
}
```

---

## ADVERSARY SIMULATION (MCF Planner in {{COUNTRY}})
*(Enabled when `INCLUDE_ADVERSARY_SIM:true`; cross‑reference Phases 3–6)*

**Task:** "If I were an MCF planner targeting {{COUNTRY}} in domain X, how would I proceed?"

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
- **Pattern identification / Trend analysis:** Specify the test (e.g., Mann‑Kendall, t‑test). Provide N, p‑value or effect size; if not applicable, state "descriptive only".
- **Internationally competitive:** Competitive **globally** or **regionally vs peer economies** (state which). Explain why that still matters for talent/targeting.

---

## ANNEX C — JSON Field Reference (Quick)
- **prob:** one of the probability bands (string).  
- **confidence:** one of Low/Med/High.  
- **DataQuality:** integer 1–5.

---

## WORKFLOW NOTES
1) Execute phases sequentially. 2) Keep the Evidence Table growing. 3) When a toggle is **false**, skip that block and note the skip in output. 4) When gaps block progress, return **OpenQuestions** and **Next‑Best‑Data**.

---

## FINAL PACKAGE (per run)
- Phase outputs (JSON) concatenated.  
- Evidence Table.  
- 1‑page executive summary (≤250 words) highlighting **top 3 risks**, **top 3 recommendations**, **two biggest unknowns**, and **immediate actions required**.