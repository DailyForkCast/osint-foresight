Below is a single, copy‑paste prompt for Claude Code. It **fixes the Austria portals file** and installs **house rules** so future runs write files deterministically (no reinterpretation, no auto‑push).

---

# Claude Code — Canonicalize `docs/references/AT-portals.md` and enforce deterministic saves

## Guardrails (follow exactly)
- **Do NOT push** to remote. Stage and commit locally only.
- **Write verbatim** content as provided. Do not summarize/“align” formats.
- If a prior file exists at a different path (`docs/references/at_portals.md`), **rename or remove** it to eliminate duplicates.
- Print a concise CHANGELOG at the end.

## Step A — Ensure canonical path & content
Write the following content **verbatim** to:
`docs/references/AT-portals.md`
(Create parent directories if missing.)

```
---
title: "Austria — References & Portals (Seed List)"
author: Analyst
date: "<AUTO>"
---

> Purpose: authoritative, mostly-stable sources to support narratives, verification, and optional manual data boosts. Keep this list short; expand only when a later phase needs it.

## Government & Regulators
- **Federal Chancellery (BKA)** — government strategies & press.
- **Ministry for Labour & Economy (BMAW)** — includes **Akkreditierung Austria** (national accreditation), export control/licensing.
- **Ministry for Climate Action, Environment, Energy, Mobility, Innovation & Technology (BMK)** — R&I policy, digital/space.
- **Ministry of Finance (BMF)** — customs/sanctions notices, public finance.
- **RTR** (Telecom/Media Regulator) — spectrum, 5G/6G, market data.
- **GovCERT Austria / CERT.at** — cybersecurity advisories.

## Funding & Programs
- **FFG** — Austrian Research Promotion Agency; national R&D calls & results.
- **aws** — Austria Wirtschaftsservice; innovation financing & guarantees.
- **BBG** — Federal procurement (Bundesbeschaffung) & e‑procurement portals.

## Standards & Accreditation
- **Akkreditierung Austria** (within BMAW) — ISO/IEC 17025/17020, etc.
- **Austrian Standards (ASI)** — EN/ISO adoptions, committees, ballots.

## Research, Statistics, IP
- **ÖAW** — Austrian Academy of Sciences (institutes & programs).
- **Statistics Austria** — R&D, trade, tech indicators.
- **Austrian Patent Office** — patents/trademarks; complements WIPO/EPO.
- Major university portals: **TU Wien**, **TU Graz**, **University of Vienna**, **JKU Linz** (research groups & labs).

## Trade, Logistics, Registries
- **Customs / Zollamt Österreich** — dual‑use guidance.
- **ÖBB Rail Cargo** — logistics flows/insights.
- **Firmenbuch** (company register) and **data.gv.at** (open data).

## EU/International (stable)
- **CORDIS** & **EU Funding & Tenders** — EU projects/programs.
- **Eurostat** — statistics.
- **UNCTAD** — trade & logistics indicators.
- **OpenSanctions** — consolidated sanctions data.
- **GLEIF** — LEI reference data.
- **IETF Datatracker** — standards roles & WGs.

---

## How to Use This Page
- Cite these sources in phase narratives for verification and context.
- When you have ~15 minutes, add **one** manual CSV from a relevant portal:
  - **Phase 3 (Institutions):** Akkreditierung Austria directory → accredited labs CSV.
  - **Phase 4 (Funders):** FFG call/program list → instruments CSV.
  - **Phase 2/5 (Landscape/Links):** CORDIS participants slice for Austria → co‑participation edges.

## Suggested Cadence
- **Quarterly:** Austrian Standards (ASI), FFG calls, IETF Datatracker highlights.
- **Semiannual:** RTR spectrum/market stats; national think‑tank reports.
- **Annual:** Akkreditierung Austria directory; Statistics Austria R&D/innovation statistics; Austrian Patent Office snapshot.

---

## Watchlist Entries (YAML snippet)
Paste into `queries/policy/watchlist.yaml` and adjust URLs as needed.

```yaml
- name: Akkreditierung Austria (BMAW) — accredited labs
  cadence: annual
  country: AT
  notes: ISO/IEC 17025/17020 directory; Phase 3 booster
  url: https://www.bmaw.gv.at/akkreditierung

- name: Austrian Standards (ASI) — committees & ballots
  cadence: quarterly
  country: AT
  notes: standards roles; Phase 2 narrative & Phase 5 context
  url: https://www.austrian-standards.at/

- name: FFG — national R&D calls & results
  cadence: quarterly
  country: AT
  notes: programs/instruments; Phase 4 booster
  url: https://www.ffg.at/

- name: RTR — telecom spectrum & market stats
  cadence: semiannual
  country: AT
  notes: 5G/6G/sectors; Phase 2/8 context
  url: https://www.rtr.at/

- name: Austrian Patent Office — patent search
  cadence: annual
  country: AT
  notes: complements WIPO/EPO; mechanisms; Phase 7C context
  url: https://www.patentamt.at/

- name: Statistics Austria — R&D/trade indicators
  cadence: annual
  country: AT
  notes: context charts; Phase 2/8 narrative
  url: https://www.statistik.at/

- name: GovCERT Austria / CERT.at
  cadence: monthly
  country: AT
  notes: cyber advisories; Phase 6 mitigation context
  url: https://www.cert.at/
```

---

## Step B — Remove/rename non‑canonical file if present
If `docs/references/at_portals.md` exists, do **one** of the following:
- If its content is now identical to the canonical version, remove it: `git rm docs/references/at_portals.md`
- Otherwise, `git mv` it to the canonical path and **overwrite** it with the content above.

## Step C — Commit locally (no push)
Run:
```bash
git add docs/references/AT-portals.md
git rm docs/references/at_portals.md 2>/dev/null || true
git commit -m "fix(refs): canonicalize Austria portals file path and freeze verbatim content"
```

## Step D — Install LLM house rules (write once)
Create/append `docs/CONTRIBUTING-LLM.md` with:
```
# LLM House Rules (Deterministic Writes)
- Write file content **verbatim** from the user’s canvas.
- **Do not** summarize, reformat, or “align” to a prior style unless explicitly instructed.
- Print only `WRITE <path>` or `UPDATED <path>` confirmations.
- Do **not** run `git push` unless explicitly asked.
- Respect exact paths and case (e.g., `AT-portals.md`, not `at_portals.md`).
```
Stage and commit:
```bash
git add docs/CONTRIBUTING-LLM.md
git commit -m "chore: add LLM deterministic write rules"
```

## Final — Print logs
Print a concise one‑line CHANGELOG like:
```
UPDATED docs/references/AT-portals.md; removed docs/references/at_portals.md; added docs/CONTRIBUTING-LLM.md
```
