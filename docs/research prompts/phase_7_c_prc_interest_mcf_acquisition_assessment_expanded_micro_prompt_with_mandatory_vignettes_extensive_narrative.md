Below is a single, copy‑paste **micro‑prompt** to run Phase 7C with a comprehensive narrative and **mandatory vignettes**. It adds a structured **policy/doctrine corpus** spanning PRC, <COUNTRY>, and (where applicable) EU sources, and enforces label‑independent MCF detection.

---

# Run Phase 7C — PRC Interest & MCF Acquisition Assessment for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 7C — PRC Interest & MCF Acquisition (reports/country=<ISO2>/phase-7c_posture.md)"
- The canvas must contain **ONLY final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>","zh"]** (translate key titles/quotes as needed); toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If sources are thin, still render a complete report with clear “No data yet — watchlist added” notes.

---

## What to produce (sections)
1) **Front‑matter** — title, author, date.
2) **Tables** — InterestLadder (per sector), Mechanisms (vectors), PolicyCorpus (PRC + country + EU), Signals (salient recent items), **Vignettes (mandatory)**, Optional Tripwires.
3) **Quality & screening notes** — label‑independent MCF detection; evidence tiers; recency; language handling; sanctions/legal overlay (signals‑only; **exclude US persons entirely**); confidence discipline; falsification paths.
4) **Comprehensive Narrative** — expanded P7C‑C (see template below), including sector‑by‑sector posture, mechanisms, why it matters, and how we would corroborate.
5) **3–5 Bullet Executive Summary** — decision‑useful close.
6) **Next Data Boost** — one pragmatic action.

---

## TSV outputs (return each as Markdown table + `# excel-tsv`)

### A) InterestLadder.tsv (per sector posture)
```
# excel-tsv
sector	interest_level_L1_L3	posture_summary	primary_evidence_ids	confidence_LMH	uncertainty_note
```
- **interest_level_L1_L3**: L1 (latent), L2 (active), L3 (targeted/priority)
- **posture_summary**: 2–3 sentences (concise rationale)

### B) Mechanisms.tsv (acquisition vectors & pathways)
```
# excel-tsv
mechanism_id	sector	description	observed_in_country	anchors_evidence_ids	vector_type	confidence_LMH	notes
```
- **vector_type** ∈ {education_talent, joint_lab, JV_equity_control, minority_equity, standards_influence, IP_license, research_grant, procurement, supplier_relationship, shell_company, diaspora_network, VC_fund, conference_outreach, OSS_contributions, data_or_compute_access, logistics_route, recruiting_platform, other}

### C) PolicyCorpus.tsv (**PRC + <COUNTRY> + EU**) — **mandatory policy/doctrine capture**
```
# excel-tsv
doc_id	jurisdiction	issuer	date	doc_type	title_en	title_local_or_zh	key_quote	url	evidence_anchor_hash	sector_tags	relevance_note
```
- **doc_type** ∈ {law, regulation, policy, white_paper, non_paper, plan, guideline, press_release, speech}
- **evidence_anchor_hash**: anchor or text‑hash if available (see Phase 0 protocol)

### D) Signals.tsv (recent salient items)
```
# excel-tsv
signal_id	date	actor	what_happened	sector	mechanism	why_it_matters	link	evidence_id
```

### E) Vignettes.tsv (concern mini‑cases — **mandatory**)
```
# excel-tsv
vignette_id	title	actor_set	mechanisms	year_range	sector	what_happened	why_it_matters	links	falsification_or_mitigation	confidence_LMH
```
- Select **1–5** most concerning; if none, include a single row noting `none_observed=true` and explain why in narrative.

### F) (Optional) Tripwires.tsv (forward‑looking monitors)
```
# excel-tsv
tripwire_id	description	sector	mechanism	trigger_condition	check_cadence	suggested_data_source
```

---

## Quality & screening (print as bullet list)
- **Label‑independent MCF detection:** do **not** require the literal term *MCF*. Treat activities as **MCF‑consistent** when they align with dual‑use integration patterns. For high‑impact calls, require **≥2 independent anchors** (ownership/funding/procurement/standards/lab charter), else keep confidence low and add `uncertainty_note`.
- **Evidence tiers:** prefer primary legal/policy texts, official portals, SDO records; then authoritative think‑tanks; then reputable media. Mark tier.
- **Recency:** weight last **24–36 months**; retain older doctrine if still operative (note status).
- **Languages:** capture titles in EN + local/zh; include minimal translations of key quotes.
- **Sanctions/legal overlay:** soft‑flag signals from EU/UK/CA/AU/NZ/UN lists or relevant legal cases; **exclude American citizens/persons entirely** from hits and narrative; all such hits are **signals, not proof**.
- **Confidence discipline:** every sector posture gets **confidence_LMH** + `uncertainty_note`; every vignette gets falsification/mitigation steps.

---

## P7C‑A — Objectives (is there interest? what changes?)
- Start with **“Is there interest?”** per sector using **InterestLadder** (L1/L2/L3). Explain the **observable change** we would expect if interest deepens (e.g., move from co‑pub → standards co‑leadership → JV/equity/testbed access).

---

## P7C‑B — Policy & Doctrine Evidence (PRC + <COUNTRY> + EU) — **mandatory**
Collect **policy/white‑paper/non‑paper/guidance** and doctrine from:
1) **PRC** — national/ministerial (MIIT/MOST/MOF/State Council), provincial where relevant; SDO strategies; talent programs; export‑control guidance.
2) **<COUNTRY>** — national strategies (tech/industry/security), export‑control/FDI frameworks, standards participation strategies.
3) **EU** — applicable frameworks (Horizon Europe/EDF, standardization strategies, anti‑coercion/export regimes, investment screening guidance).
For each document, record issuer/date/type/title(s), **one key quote** (translated if needed), URL, **anchor hash** (if available), sector tags, and a 1‑line relevance note. Populate **PolicyCorpus.tsv** and reference evidence IDs in the narrative.

---

## P7C‑C — Comprehensive Narrative (extensive)
Write a **carefully crafted, information‑rich narrative** that synthesizes policy doctrine, observed mechanisms, and relationships into a sector‑by‑sector posture and acquisition view. Keep a neutral tone; explicitly mark uncertainty.

### 1) Posture by Sector (structured)
For each top sector (≤6):
- **Interest level (L1/L2/L3)** + **2–3 sentence rationale** anchored in **PolicyCorpus** + observed **Mechanisms** + recent **Signals**.
- **Primary acquisition pathways** relevant to this sector (from **Mechanisms.tsv**), explicit about *how* they would operate in <COUNTRY> (e.g., JV with RTO; minority equity in startup; standards co‑chair path; alumni placement; compute/testbed access; OSS influence; logistics/finance routes).
- **Countervailing controls** in <COUNTRY>/EU (export classification, FDI screen, procurement rules, accreditation/BO transparency) and their likely **effectiveness** (qualitative).
- **Confidence** and **what would change the call** (one observation that would raise/lower interest level).

### 2) Cross‑cutting Vectors & Patterns
- Talent channels (scholarships, recruitment platforms, visiting positions, alumni networks).
- Corporate vectors (JV/equity, shell companies, supplier relationships, venture funds).
- Standards & governance vectors (WG co‑leadership, editor roles, test method control).
- Data/compute/testbed access; facility sharing; procurement/mission pull.
- Finance/logistics (banking rails, trade corridors, free zones, freight chokepoints) drawing on Phase 2S where relevant.

### 3) Signals‑to‑Doctrine Alignment
- Show **specific linkages** from **Signals** to **PolicyCorpus** (e.g., a PRC white paper calling for X, then a standards posture or JV step consistent with X in <COUNTRY>).
- Where alignment is **absent or weak**, say so and reduce confidence.

### 4) Concern Vignettes (mandatory; 0–5 items)
- Select the **1–5 most concerning** posture items/relationships using: mechanism sensitivity, sector criticality, sanctions/legal signals (non‑US persons only), and strategic dependency.
- For each, write **~120 words**: who/what, mechanism(s), sector, why it’s concerning, evidence links/IDs, **confidence_LMH**, and **what would falsify or mitigate**.
- **If none are concerning**, state: “**No concerning posture vignettes identified** under current evidence and thresholds,” and explain briefly why.

### 5) Tripwires (forward‑looking)
- Propose **3–6 machine‑trackable tripwires** tied to mechanisms (e.g., new JV filings; standards role change; sudden recruitment surge; IP license filings; compute/testbed tenancy; BO change). Put in **Tripwires.tsv**.

---

## 3–5 Bullet Executive Summary
Provide 3–5 crisp bullets that answer: **Which sectors show interest (L2–L3)? Through which mechanisms? Why does it matter? What controls or observations will change the call?**

---

## Next Data Boost (close the report)
Suggest **one** high‑ROI action (e.g., “Populate PolicyCorpus.tsv with 5 priority PRC/<COUNTRY>/EU documents and re‑score InterestLadder with explicit doctrine anchors”).

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 7C report per the contract above.**

