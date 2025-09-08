# Claude Code — Patch Phase 2 (AT): Dynamic Domain Narratives (no fixed list) + IP/Standards bullets

**Target file:** `reports/country=AT/phase-2_landscape.md`

**Goal:** Replace any fixed domain list with a **dynamic section** that renders narratives only for **selected clusters/subdomains** (from Phase X rules). Add per‑domain **IP/Patent posture** and **Standards‑shift signals** bullets.

---

## Steps
1) **Open** `reports/country=AT/phase-2_landscape.md`.
2) **Find** the section that enumerates domains/clusters. If it presumes a fixed set, we will make it dynamic.
3) **Insert** the following block **after** the main landscape intro (or replace the fixed list block):

```markdown
## P2-D: Dynamic Domain Narratives (selected by evidence)
We render domains only if they meet Phase‑X selection rules (see Phase X: *Cluster & Subdomain Selection*). For each selected domain, include:

**Template per selected domain/subdomain**
- **Why it matters here (120–150 words):** role in national capability; concrete country examples.
- **Evidence anchors:** which selection signals were triggered (edges, scopes, standards, programs, narrative).
- **IP/Patent posture:** any visible patent spikes, disputes, or licensing asymmetries (if none, note `no_signal`).
- **Standards‑shift signals:** venue activity (e.g., IETF/ETSI/3GPP) and role deltas to watch.
- **MCF label‑independent cues:** function‑over‑label (timing/GNSS/EMC, testbeds, compute access) as applicable.

> If a domain is noteworthy but under‑evidenced, include it as **latent** (short paragraph, `notes=low_evidence`).
```

4) **Save** the file.
5) **Commit:** `chore(AT/P2): switch to dynamic domain narratives + add IP/standards bullets`

**Note:** Keep existing tables (e.g., `relationships.csv` excerpts). This patch only changes the narrative structure.

