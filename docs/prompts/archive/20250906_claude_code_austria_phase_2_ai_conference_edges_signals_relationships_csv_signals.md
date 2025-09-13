Below is a copy‑paste prompt for Claude Code. It **upserts** Austria (AT) Phase‑2 enrichments derived from authoritative conference sources. It will add AI co‑authorship edges (relationships.csv) and signals (signals.csv). No pushes.

---

# Claude Code — Upsert AT AI conference edges & signals
**Goal:** Add concrete AI collaboration edges and event signals for Austria (AT) using NeurIPS/ICLR evidence.

## Guardrails
- Idempotent upsert using natural keys.
- **Do not push** to remote; local write only.
- Create headers if files are missing.
- Natural keys:
  - `data/processed/country=AT/relationships.csv`: `(sector, counterpart_name, collab_type, year)`
  - `data/processed/country=AT/signals.csv`: `(window, signal_summary)`

## Evidence (for commit message / traceability)
- **NeurIPS 2023 (paper)** — *Meta‑learning families of plasticity rules in recurrent spiking networks*, shows **Institute of Science and Technology Austria (ISTA)** with co‑authors from University of Tübingen, Max Planck (Tübingen), VIB‑NERF (Belgium), imec (Belgium). citeturn0search15
- **NeurIPS 2022 (paper)** — *Optimal Brain Compression*, **IST Austria & Neural Magic (US)**. citeturn0search16
- **NeurIPS 2023 (competition track)** — TU Wien involved (ROAD‑R 2023) with University of Oxford et al. (organizational co‑project). citeturn0search0
- **ICLR 2024 in Vienna** — major AI venue hosted in Austria (momentum signal). citeturn0search2

---

## 1) Upsert `data/processed/country=AT/relationships.csv`
Append or replace the following rows (CSV, comma‑separated). If the file doesn’t exist, create it with the header below.

**Header (ensure present):**
```
sector,counterpart_name,counterpart_country,collab_type,year
```

**Rows to upsert:**
```
AI,University of Tübingen,DE,co-publication,2023
AI,Max Planck Institute (Tübingen),DE,co-publication,2023
AI,VIB-NERF,BE,co-publication,2023
AI,imec,BE,co-publication,2023
AI,Neural Magic,US,co-publication,2022
AI,University of Oxford,GB,co-project (competition),2023
```

After writing, print:
```
UPDATED data/processed/country=AT/relationships.csv
```

---

## 2) Upsert `data/processed/country=AT/signals.csv`
Append or replace the following rows (CSV). Create with header if missing.

**Header (ensure present):**
```
window,signal_summary,likely_driver
```

**Rows to upsert:**
```
2024-05,ICLR 2024 hosted in Vienna (Austria),International AI community presence
2023-12,TU Wien visible at NeurIPS 2023 (competition track),Benchmarking & methods community presence
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
OK: appended AI conference edges & signals for AT; ready to view Phase 2
```

