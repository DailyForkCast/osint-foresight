# ChatGPT — Run Narrative Fills (AT, flexible domains)

**When to run:** After Claude Code applies the three patches:
- Phase X: Flexible Cluster Selection
- Phase 2: Dynamic Domain Narratives
- Phase 8: Dynamic Sector Playbooks

**Country:** Austria (AT) · **Years:** 2015–2025 · **Languages:** en, de

**Inputs (if present):** `relationships.csv`, `AccreditedLabs.tsv`, `standards_roles.tsv`, `programs.csv`, `calls.tsv`, `international_links.tsv`, `capability_heat.tsv`, `risk_register.tsv`, prior report markdowns under `reports/country=AT/`.

**Guardrails:** Neutral tone; signals ≠ proof; label‑independent MCF reasoning; exclude US persons in legal/sanctions mentions.

---

## Tasks for ChatGPT
1) **Phase X (taxonomy/glossary)**
   - Using the flexible rules, select **4–10 clusters** and **1–4 subdomains** each; write a short **selection rationale** per cluster.  
   - Generate/refresh `domain_maturity.tsv` with `cluster_id,subdomain,selection_reason,signals_count,notes` and update the Phase X narrative accordingly.

2) **Phase 2 (landscape)**
   - For each **selected** cluster/subdomain, write the **120–150 word** narrative + bullets for **Evidence anchors**, **IP/Patent posture**, **Standards‑shift signals**, and **MCF label‑independent cues**.
   - If evidence is thin, mark the domain as **latent** with `notes=low_evidence` and still provide a short paragraph.

3) **Phase 8 (foresight)**
   - Compute the **top‑K (≤3)** clusters by `capability_heat + max_risk` (or narrative heuristic if tables are missing).  
   - Draft **Sector Playbooks** for each: rationale, leverage moves, controls & guardrails, allies & counterparties, success criteria (3 EWIs).  
   - Keep the **Monday Morning** checklist intact.

**Citations:** Use free/open sources for narrative lifts; cite inline and add to Evidence Register when new.

**Output:** Edit the three report files in place—no extra files. Keep existing TSV snippets and headings.

