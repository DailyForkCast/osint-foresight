Below is a single, copy‑paste **micro‑prompt** to run Phase 7R with a rigorous red‑team review. It preserves the original goals (assumptions check, adversarial stress‑test) and adds explicit detection for **contradictions, unsupported assertions, bias (incl. racism‑rooted cues), and coverage gaps**. It also aligns with prior phases’ evidence discipline (signals‑only sanctions/legal with US‑person exclusions).

---

# Run Phase 7R — Assumption Check & Red‑Team Review for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 7R — Red‑Team Review (reports/country=<ISO2>/phase-7r_redteam.md)"
- The canvas must contain **ONLY final file content** (Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table appears twice — (1) Markdown and (2) a fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>","zh"]** where relevant; toggles { include_export_controls: true, include_us_natsec_8cats: true }.
- If source material is thin, still render a complete review with explicit unknowns and a punch‑list of fixes.

---

## What to produce (sections)
1) **Front‑matter** — title, author, date.
2) **Tables** — Assumptions, Contradictions, UnsupportedAssertions, CoverageGaps, BiasAudit, SensitivityLanguage, FixesBacklog, Optional Vignettes, DecisionLog.
3) **Quality & ethics notes** — evidence tiers, US‑person exclusions, neutrality & non‑stigmatizing language, reproducibility/diffability.
4) **Comprehensive Red‑Team Narrative** — structured critique that integrates findings and proposes concrete, solo‑doable fixes.
5) **3–5 Bullet Executive Summary** — decision‑useful close.

---

## TSV outputs (return each as Markdown table + `# excel-tsv`)

### A) Assumptions.tsv (traceable claims to test)
```
# excel-tsv
assumption_id	statement	phase_ref	evidence_ids	justification	confidence_prior_LMH	redteam_test	result	confidence_posterior_LMH	change_note
```

### B) Contradictions.tsv (clashing evidence or logic)
```
# excel-tsv
contradiction_id	description	where_observed	phase_refs	affected_outputs	evidence_ids	severity_1to3	proposed_resolution
```

### C) UnsupportedAssertions.tsv (assertions with little/no evidence)
```
# excel-tsv
assertion_id	statement	phase_ref	evidence_present	evidence_needed	risk_if_wrong	proposed_action
```

### D) CoverageGaps.tsv (thin/absent segments)
```
# excel-tsv
gap_id	domain	missing_signal	why_it_matters	free_source_to_try	manual_step	owner	eta
```

### E) BiasAudit.tsv (bias, incl. racism‑rooted or stereotype leakage)
```
# excel-tsv
issue_id	location	bias_type	cue_text	why_problematic	impact	mitigation	status
```
- **bias_type** ∈ {racism_rooted, ethnic_stereotype, nationality_blur, selection_bias, keyword_bias, language_bias, confirmation_bias, anchoring, other}

### F) SensitivityLanguage.tsv (stigmatizing/loaded wording)
```
# excel-tsv
line_id	location	text_snippet	concern	proposed_neutral_rewrite
```

### G) FixesBacklog.tsv (ranked, solo‑doable)
```
# excel-tsv
fix_id	description	category	phase_ref	cost_hours	skill_level_1to3	dependency	priority_1to5	owner	due_date	status
```
- **category** ∈ {data_pull, normalization, narrative_rewrite, verification, legal_check, standards_check, taxonomy_tune, visualization}

### H) Vignettes.tsv (optional critique mini‑cases, 0–3)
```
# excel-tsv
vignette_id	title	actor_set	mechanisms	year_range	sector	what_happened	why_concerning	links	falsification_or_mitigation
```
- Use vignettes only if they clarify a contradiction or an over‑confident call. If none, omit.

### I) DecisionLog.tsv (publishability & caveats)
```
# excel-tsv
entry_id	question	decision	caveats	owner	date
```

---

## Quality & ethics (print as bullet list)
- **Evidence tiers & neutrality:** prefer primary/official sources; mark tier; state uncertainty. Avoid speculative language; use signal vs proof framing.
- **Sanctions/legal overlay (signals‑only):** if referenced from previous phases, keep as signals; **exclude American citizens/persons entirely** from any hits or narrative.
- **Bias & racism safeguards:** actively search for **racism‑rooted** or ethnic/national stereotype cues; replace with neutral, evidence‑anchored phrasing.
- **Keyword & language bias:** check EN/<local>/ZH term sets; ensure non‑English portals weren’t skipped; log gaps.
- **Double counting & survivorship bias:** verify that the same relationship wasn’t counted via multiple mechanisms; log any inflation.
- **Reproducibility:** any corrections should be traceable to files/lines/IDs; where feasible reference **EvidenceRegister** anchors (Phase 0).

---

## Comprehensive Red‑Team Narrative (write this)
Construct a pragmatic critique that a single analyst can act on. Organize as follows:

### 1) Highest‑Impact Weaknesses (4–8 bullets)
- List the weaknesses most likely to change conclusions (e.g., reliance on Tier‑3 proxies; missing accreditation CSV; ambiguous partner identity; over‑reliance on one consortium; lack of non‑English sources).

### 2) Assumptions Under Test
- Highlight the **top 5 assumptions** driving Phases 2/2S/3/4/5/6/7C/8 conclusions. For each: current confidence, red‑team test, what would falsify it, and the **cost to test** (hours; free sources only where possible).

### 3) Contradictions & Conflicts
- Describe the most material contradictions across phases (e.g., Phase 2 maturity vs Phase 5 asymmetry; Phase 7C posture vs Phase 4 funding reality). Propose a resolution path (which data to pull, which narrative to amend).

### 4) Bias & Sensitivity Review
- Call out **racism‑rooted** or stereotype risks; rewrite any loaded phrasing; ensure motives are not ascribed to national/ethnic identity; keep focus on **observed mechanisms and evidence**.
- Document **keyword/language bias** and what additional non‑English search terms or portals would correct it.

### 5) Coverage Gaps → Fix Plan
- Enumerate the biggest **coverage gaps** by domain/phase. For each, list a **free source** to try, a **manual step** that a solo analyst can do, and a small **Make/VS Code task** if available.

### 6) Confidence Re‑scoring
- After applying tests and planned fixes, adjust **confidence** up/down for major calls (Phase 2 maturity bands; Phase 7C interest levels; Phase 6 top risks). Make adjustments explicit in **Assumptions.tsv**.

### 7) Publishability & Caveats
- Decide whether the current snapshot is **fit for public release**; if not, list the **blocking fixes** and expected time to remediate (use FixesBacklog.tsv).

### 8) 3–5 Bullet Executive Summary
- End with crisp bullets summarizing **what changed** in confidence, **what remains uncertain**, and **what the next 1–2 actions** should be.

---

## Next Data Boost (close the report)
Provide **one** pragmatic action (e.g., “Add non‑English search terms to Phase 2 keyword sets, re‑pull standards rosters, and re‑score sector maturity; log changes in Assumptions.tsv”).

---

**Run now for <COUNTRY>/<ISO2> and return the complete Phase 7R report per the contract above.**

