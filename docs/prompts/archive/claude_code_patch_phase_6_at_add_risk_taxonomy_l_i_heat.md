# Claude Code — Patch Phase 6 (AT): Add Risk Taxonomy + L×I Heat

**Target file:** `reports/country=AT/phase-6_risk.md`

**Goal:** Insert a succinct **Risk Taxonomy & Red Flags** section and a **Likelihood × Impact (L×I) Heat** table. This mirrors the Portugal narrative and makes the scoring auditable.

---

## Steps
1) **Open** `reports/country=AT/phase-6_risk.md`.
2) **Find anchor** line that starts with `## B) Scoring Rubric`.
3) **Insert the following blocks *after* that rubric section** and *before* `## C) Risk Register`:

```markdown
## Risk Taxonomy & Red Flags (quick reference)
| vector_id | name | typical red flags | quick checks |
|---|---|---|---|
| RV1 | Standards leverage | recurring editorship; agenda‑setting drafts | Datatracker roles/acks; draft adoption
| RV2 | HPC/Compute access | opaque allocations; exclusive MoUs | allocation notes; program minutes
| RV3 | RF/EMC/RED benches | sudden scope growth; sensitive client mix | 17025/17065 scopes; equipment lists
| RV4 | Time/Frequency & GNSS | GNSS simulation; SAASM‑adjacent terms | scope granularity; vendor PR
| RV5 | Advanced Mfg/NDT | exotic alloys/AM certification | 17020 scopes; ISO 9712 signals
| RV6 | JV/Equity/Control | BO shifts to opaque shells | LEI/OC merges; registry deltas
| RV7 | PRC doctrine alignment | tight overlap with PRC roadmaps | policy refs; partner nexus
| RV8 | Sanctions/legal (non‑US) | list hits on partners/intermediaries | EU/UK/CA/AU/NZ/UN lists; date+URL

## Likelihood × Impact Heat (snapshot)
Use 1–5 **Impact** and 1–5 **Likelihood**; compute cell score = Impact × Likelihood. 1–6 = Low, 8–12 = Medium, 15–25 = High. (Keep as a living snapshot.)

| vector_id | impact_1to5 | likelihood_1to5 | cell | band |
|---:|---:|---:|---:|---|
| RV2 | 4 | 2 | 8 | Medium
| RV1 | 3 | 2 | 6 | Low
| RV3 | 3 | 2 | 6 | Low
| RV4 | 3 | 1 | 3 | Low
| RV6 | 5 | 1 | 5 | Low

> Update values as evidence lands; the **Risk Register** remains the source of truth.
```

4) **Save** the file.
5) **Commit:** `chore(AT/P6): add risk taxonomy + L×I heat snapshot`

**Optional follow‑up:** If the rubric heading differs, search for `## Scoring Rubric` and place the block immediately after it.
