# Claude Code — Patch Phase 5 (AT): Add “Method & Scoring” Block

**Target file:** `reports/country=AT/phase-5_links.md`

**Goal:** Insert a new **“Method & Scoring”** subsection near the top (after *Scope & Inputs*), standardizing sources, intensity scoring, risk heuristics, and an EW signals checklist.

---

## Steps
1) **Open** `reports/country=AT/phase-5_links.md`.
2) **Find anchor** line that starts with `## A) Link Types Tracked`.
3) **Insert the following block *above* that anchor** (i.e., right after the *Scope & Inputs* section):

```markdown
## Method & Scoring (how we read the edges)
**Source classes:**
- *Primary structured:* relationships.csv, standards_roles.tsv, programs.csv, grant_partners.tsv
- *Primary narrative:* official portals, SDO rosters/acks, facility MoUs, conference programs
- *Secondary narrative:* press, institutional blogs, reputable trade media

**Collaboration intensity (0–3):** 0=none/dated, 1=single weak edge, 2=recent multi‑edge or strong single, 3=recent multi‑edge + diverse types.

**Risk read (L/M/H):**
- **Low:** transparent governance, symmetric benefits, no sensitive subdomain
- **Medium:** some asymmetry, sensitive subdomain, or elevated access path (compute/testbeds)
- **High:** persistent asymmetry **and** sensitive mechanisms (timing/GNSS/EMC) with weak controls

**Heuristics used:** diversity of link types; recency; partner posture; standards roles; bench confirmation via accreditation scopes.

**Early‑warning signals (checklist):**
- Role elevation in IETF/ETSI (authors → editors/chairs)
- New MoUs for compute/testbed access (EuroHPC/VSC)
- Ownership/beneficial‑owner changes (LEI/OpenCorporates)
- Rapid growth in AT‑participant CORDIS wins in sensitive topics
```

4) **Save** the file.
5) **Commit:** `chore(AT/P5): add Method & Scoring block to standardize edge reading`

**Optional follow‑up:** If headings differ, place the block immediately after the line: `## Scope & Inputs`. If neither anchor is present, append to the top after front‑matter.
