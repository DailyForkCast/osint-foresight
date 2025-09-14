# Claude Code — Patch Phase 4 (AT): Add Funding Flow Sketch + Compliance Hooks

**Target file:** `reports/country=AT/phase-4_funders.md`

**Goal:** Insert a **“Funding Flow Sketch”** narrative and a **“Compliance Hooks”** subsection. These make the write‑up consistent with our Portugal narrative and ground risk in concrete EU instruments.

---

## Steps
1) **Open** `reports/country=AT/phase-4_funders.md`.
2) **Find anchor** line that starts with `## A) Funder Registry`.
3) **Insert the following two blocks *above* that anchor** (i.e., right after *Scope & Inputs*):

```markdown
## Funding Flow Sketch (EU → national → institutional → private)
**EU layer** (Horizon Europe/EuroHPC JU) sets cross‑border priorities and shapes consortia behavior.
**National layer** (FFG/FWF/aws + ministries) translates into thematic calls, basic research, and SME instruments.
**Institutional layer** (universities/RTOs) converts awards into labs, benches, and standards contributions.
**Private layer** (suppliers/SMEs) operationalizes adoption via capex/loans/guarantees.

This flow determines **who** collaborates, **what** gets built, and **where** capability consolidates. We map instruments → programs → partners to reveal vectors and asymmetries.

## Compliance Hooks (record where applicable)
- **EU 2021/821 (Dual‑Use Reg.)**: export‑control intersections in funded topics/work packages
- **NIS2 / information security**: governance for data, code, and infrastructure
- **FDI screening**: constraints on ownership/control of recipients or key suppliers
- **Research integrity / DPIA / data governance**: handling of sensitive datasets and cross‑border access

> *Tables note:* when available, add `compliance_hooks` tags to program/call rows in `programs.csv`/`calls.tsv` (e.g., `export_control;NIS2;FDI;DPIA`).
```

4) **Save** the file.
5) **Commit:** `chore(AT/P4): add Funding Flow Sketch + Compliance Hooks narrative`

**Optional follow‑up:** If the anchor differs, place blocks after `## Scope & Inputs`. If absent, insert after front‑matter.
