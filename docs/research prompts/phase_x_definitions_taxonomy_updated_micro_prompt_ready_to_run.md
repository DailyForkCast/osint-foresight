Below is a single, copy‑paste **micro‑prompt** for ChatGPT to generate Phase X for any country. It merges the Master Prompt directives with the new **country‑tunable selection rules, thresholds, scoring, and safeguards**.

---

# Run Phase X — Definitions & Taxonomy for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase X — Definitions & Taxonomy (reports/country=<ISO2>/phase-x_taxonomy.md)"
- The canvas must contain **ONLY the final file content** (human‑readable Markdown + front‑matter) for that path.
- Include **Excel‑Ready Mode**: any table must be returned twice — (1) Markdown table **and** (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- If data is thin, still render a complete report with a short “No data yet — watchlist added” note.
- Assume timeframe **2015–present**, languages **["en","<local>"]**, toggles { include_export_controls: true, include_us_natsec_8cats: true }.

## What to produce (sections)
1) **Front‑matter** (title, author, date).
2) **Glossary of key dual‑use terms** — concise, country‑agnostic.
3) **Sector taxonomy** — **6–10 clusters** with **3–6 subdomains** each (country‑tuned via rules below).
4) **Competitiveness bands** — criteria for Global Leader / Global Challenger / Regional Leader / Regionally Competitive (short rubric).
5) **8‑Cats mapping** (if toggle ON) — map relevant clusters to US NatSec 8 categories.
6) **Coverage safeguards & watchlist** — catch‑all buckets + promotion/demotion rules.
7) **Appendix: Extended examples** — keep the main body readable; park the long list here.

## How to choose clusters (data‑driven, country‑specific)
Start from a global **candidate menu** (AI/ML/Autonomy; HPC & Edge Compute; Semiconductors & Photonics; PNT/Sensing; Comms & Networking; Space/EO/Robotics; Advanced Materials & Manufacturing; Cyber & Crypto; Biosecurity & Biotech [toggle]; Energy/Cryogenics/Thermal [toggle]).

**Include a cluster if it meets ≥2 of these in the last 5–10 years:**
- ≥ **N1** relevant **relationships** edges (co‑publication, co‑project, infrastructure, procurement, investment, licensing, training).
- ≥ **N2** **standards roles** (WG authors/editors/chairs) by domestic orgs/persons.
- ≥ **N3** credible **institutions** (labs/testbeds/centers) with capacity signals or accreditation.
- ≥ 1 **signature facility/event** (e.g., national HPC, major conference hosted, test range).
- **Policy salience** (named in national/EU strategies or recurring calls).
- **Export‑control salience** (recurring appearance in annexes/advisories; *signal, not proof*).

**Solo‑friendly defaults (tune for small states):** N1=5, N2=2, N3=2. For very small ecosystems, you may halve these.

## How to choose subdomains (scored, but concise)
For each selected cluster, score candidate subdomains:
```
SubdomainScore = 0.4·Activity + 0.3·Capability + 0.2·Standards + 0.1·Policy
```
- **Activity:** recent edges & signals.
- **Capability:** institutions/testbeds/accreditations.
- **Standards:** WG roles/items mapped to the subdomain.
- **Policy:** explicit mentions in national/EU programs/roadmaps.

Pick the **top 3–6 subdomains** per cluster. In the **main body**, show only **1–2 exemplar technologies** per subdomain (most salient). Put all other examples in the **Appendix/Extended examples**.

## Coverage safeguards (don’t miss important tech)
- **Catch‑alls:** per‑cluster *Emerging/Frontier (watchlist)* and *Other strategic tech (to triage)*.
- **Triangulation pass:** sweep standards rosters (IETF/ETSI/ISO/IEC/OGC/CCSDS/ITU), accreditation/testbed portals, and CORDIS participants by sector keywords. If a subdomain hits **two** of the three, add it to Appendix (or promote later).
- **Policy backstop:** if newly prioritized by government/EU, add to Appendix with a “policy‑only” tag until more evidence arrives.
- **Legal/export backstop:** if a subdomain recurs in export‑control annexes or legal/sanctions vignettes (Phases 2S/6/7C), keep it visible (Appendix at minimum), even if counts are low.

## Promotion/Demotion rules (refresh logic)
- **Promote**: any Appendix subdomain appearing in **≥2 evidence types** (e.g., standards + facility) at next refresh.
- **Demote**: any main‑list subdomain with **zero** new evidence in 24 months.

## Competitiveness rubric (short)
- **Global Leader**: multi‑indicator strength (edges, institutions, standards), export salience, repeat flagship facility/event, cross‑border demand.
- **Global Challenger**: strong in 2–3 indicators, clear growth or standards foothold.
- **Regional Leader**: regionally outsized footprint in 1–2 indicators; limited global depth.
- **Regionally Competitive**: present but thin; watchlist for growth.

## 8‑Cats mapping (if ON)
Map clusters/subdomains to the US NatSec 8 categories with **short justifications**. If ambiguous, mark “unclear” and park in Appendix.

## Tables to output
### A. Taxonomy master (country‑specific)
- Markdown table **and** `# excel-tsv` with columns:
```
# excel-tsv
cluster_id	cluster_name	subdomain_id	subdomain_name	status	selection_evidence	score_activity	score_capability	score_standards	score_policy	notes
```
- **status** ∈ {main, appendix, watchlist}
- **selection_evidence**: short tags like `edges+standards+labs`, `policy+standards`, etc.

### B. Extended examples (appendix)
- Markdown table **and** `# excel-tsv` with columns:
```
# excel-tsv
cluster_id	subdomain_id	example_tech	citation	url
```

## Writing/narrative requirements
- **Glossary & taxonomy narrative** must be concise and source‑anchored (link authoritative definers).
- For each **cluster**, add a 2–3 sentence blurb explaining **why it was selected** (tie to indicators/evidence) and name **1–2 exemplar technologies** per subdomain in the main body.
- Close with a **“Data that would strengthen this taxonomy”** note (e.g., accreditation CSV, CORDIS participants slice, standards minutes) and a **refresh cadence** line (annual; faster if policy shocks occur).

## Transparency note
- Show **top‑3 matched keywords** used to detect each subdomain (retrieval transparency).
- If thresholds were tuned (e.g., halved for small states), state it explicitly.

## Degrade gracefully
- If evidence is thin, keep clusters but park most subdomains in **watchlist**; populate Appendix rows with policy‑only tags; add a specific Next Data Boost.

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase X report per the contract above.**

