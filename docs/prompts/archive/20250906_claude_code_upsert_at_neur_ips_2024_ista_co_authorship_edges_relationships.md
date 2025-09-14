Below is a copy‑paste prompt for Claude Code. It **upserts** Austria (AT) Phase‑2 enrichments derived from an ISTA‑authored NeurIPS 2024 paper. It will add AI co‑authorship edges (relationships.csv) and a momentum signal (signals.csv). No pushes.

---

# Claude Code — Upsert AT NeurIPS 2024 ISTA edges & signal
**Goal:** Add concrete **AI** collaboration edges for Austria (ISTA) from a NeurIPS 2024 paper with international co‑authors, plus one conference signal.

## Guardrails
- Idempotent upsert using natural keys.
- **Do not push** to remote; local write only.
- Create headers if files are missing.
- Natural keys:
  - `data/processed/country=AT/relationships.csv`: `(sector, counterpart_name, collab_type, year)`
  - `data/processed/country=AT/signals.csv`: `(window, signal_summary)`

## Evidence (for commit message / traceability)
- **NeurIPS 2024 paper:** *Identifying General Mechanism Shifts in Linear Causal Representations* — authors: Tianyu Chen (UT Austin), Kevin Bello (CMU/Chicago), **Francesco Locatello (ISTA)**, Bryon Aragam (UChicago), Pradeep Ravikumar (CMU/UT Austin). Proceedings & PDF list affiliations explicitly. citeturn4search1turn4search2

---

## 1) Upsert `data/processed/country=AT/relationships.csv`
Append or replace the following rows (CSV, comma‑separated). If the file doesn’t exist, create it with the header below.

**Header (ensure present):**
```
sector,counterpart_name,counterpart_country,collab_type,year
```

**Rows to upsert (ISTA → international co‑authors at NeurIPS 2024):**
```
AI,University of Texas at Austin,US,co-publication,2024
AI,Carnegie Mellon University,US,co-publication,2024
AI,University of Chicago,US,co-publication,2024
```

After writing, print:
```
UPDATED data/processed/country=AT/relationships.csv
```

---

## 2) Upsert `data/processed/country=AT/signals.csv`
Append or replace the following row (CSV). Create with header if missing.

**Header (ensure present):**
```
window,signal_summary,likely_driver
```

**Row to upsert:**
```
2024-12,ISTA authors co-author NeurIPS 2024 paper with US partners (UT Austin, CMU, UChicago),International AI collaboration signal
```

After writing, print:
```
UPDATED data/processed/country=AT/signals.csv
```

---

## 3) Optional: Rebuild Phase 2
Run:
```bash
make build COUNTRY=AT
```
Then print:
```
OK: appended NeurIPS 2024 ISTA co-authorship edges & signal for AT; ready to view Phase 2
```
