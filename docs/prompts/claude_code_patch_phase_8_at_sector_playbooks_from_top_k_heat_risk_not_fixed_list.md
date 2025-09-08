# Claude Code — Patch Phase 8 (AT): Sector Playbooks from Top‑K (heat×risk), not fixed list

**Target file:** `reports/country=AT/phase-8_foresight.md`

**Goal:** Ensure **Sector Playbooks (≤3)** are derived dynamically from the **top‑K clusters** by a simple score (e.g., `score = capability_heat + risk_score`), not from any fixed tech list. Keep guardrails + Monday Morning section.

---

## Steps
1) **Open** `reports/country=AT/phase-8_foresight.md`.
2) **Find** the section `## Sector Playbooks (≤3)`.
3) **Replace** that subsection with the following text:

```markdown
## Sector Playbooks (≤3) — dynamic selection
Pick up to **three** sectors **dynamically** using:

**Ranking score:** `score = capability_heat_0_3 (Phase 2) + max_risk_1_3 (Phase 6)` per cluster. If `capability_heat.tsv` or `risk_register.tsv` are missing, use narrative judgment and mark `notes=heuristic`.

**For each of the top‑K sectors (K≤3), include:**
- **Rationale (5–7 sentences):** why this sector matters now (evidence anchors).
- **Leverage moves:** 2–3 realistic actions that improve safety/benefit.
- **Controls & guardrails:** export‑control interfaces, governance, and research integrity checks.
- **Allies & counterparties:** local institutions and safe international partners.
- **Success criteria:** 3 measurable outcomes (EWIs) for 12–24 months.

> The playbooks are templates for optional capacity‑building, not directives. They update when heat/risk scores change.
```

4) **Save** the file.
5) **Commit:** `chore(AT/P8): make sector playbooks dynamic (top‑K by heat×risk)`

