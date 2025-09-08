# Claude Code — Patch Phase X (Global): Flexible Cluster Selection (remove hard‑coded tech list)

**Targets:** `reports/country=<ISO2>/phase-x_taxonomy.md` (or your Phase X file in each country repo)

**Goal:** Replace any *hard‑coded* sector list with a **flexible, evidence‑driven cluster selection**. Keep the same headings but add selection rules + thresholds. This preserves country specificity (e.g., Iceland vs. Bulgaria) and scales naturally.

---

## Steps
1) **Open** the Phase X taxonomy/glossary file for the active country, e.g.:  
   `reports/country=AT/phase-x_taxonomy.md`

2) **Find** any references to a fixed list like “Seven Core Domains …”.

3) **Replace** that block with the following text:

```markdown
## Cluster & Subdomain Selection (Flexible, Evidence‑Driven)
We do **not** hard‑code technology clusters. Instead, we select clusters and subdomains based on country‑specific evidence and our Phase‑X keyword taxonomy.

**Selection signals (any two → include):**
- ≥ 2 recent edges in `relationships.csv` within a subdomain (last 36 months)
- ≥ 1 accredited scope in `AccreditedLabs.tsv` (or equivalent) mapping to the subdomain
- ≥ 1 standards role (`standards_roles.tsv`) relevant to the subdomain
- ≥ 1 funded program/call in `programs.csv` / `calls.tsv` tagged to the subdomain
- Narrative confirmation in official portals / policy docs (with source ID in Evidence Register)

**Suppression signals (both → exclude for now):**
- Zero structured signals above **and** no credible narrative source within the last 5 years

**Minimum/maximum:**
- Pick **4–10 clusters** total (country‑dependent) and 1–4 subdomains per cluster. If fewer than 4 meet the threshold, include the best evidence‑supported ones and mark others as **“latent”** with `notes=low_evidence`.

**Mapping method:**
- Use `queries/keywords/taxonomy.csv` (or the current taxonomy file) to map terms → clusters → subdomains. Allow multi‑tagging across clusters; don’t force uniqueness.

**Outputs:**
- `domain_maturity.tsv` with `cluster_id,subdomain,selection_reason,signals_count,notes`.
- Narrative definitions and country examples for **only** the selected clusters/subdomains.
```

4) **Save** the file.
5) **Commit:** `chore(PhaseX): make cluster selection flexible & evidence‑driven`

**Optional:** If the taxonomy keywords file doesn’t exist yet, create `queries/keywords/taxonomy.csv` with `term,cluster_id,subdomain` and keep it editable.

