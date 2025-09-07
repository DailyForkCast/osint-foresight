Research & write Phase 2 — Technology Landscape & Maturity for <COUNTRY NAME> (<ISO2>).

Scope & rules
- Years: 2015–2025. Looser matchers ON.
- You MUST browse authoritative sources and CITE them (web.run).
- Degrade gracefully if a slice is thin; still render full report.

What to search (authoritative examples)
- Standards & WGs: IETF Datatracker, ISO/IEC/ITU, the national SDO site.
- Conferences: NeurIPS/ICLR/ICML, CVPR/ICRA, SC/ISC (HPC), SPIE/OSA, DATE/ISSCC (semis), ECOC/CLEO (comms).
- Universities/labs: top national tech universities, academy institutes.
- National programs: R&I agency portals, roadmaps, EuroHPC/EuroCC pages.
- Procurement/HPC: TOP500/Green500 notes, national HPC center pages.
- Patents (for themes only): Espacenet/Patentscope/Google Patents.

Extract (create tiny structured tables inside the canvas)
- relationships.csv rows (append-ready):
  sector, counterpart_name, counterpart_country, collab_type, year
- standards_roles.tsv rows (append-ready):
  wg, role, person_name, org_name, country, sector_hint
- signals.csv rows (append-ready):
  window, signal_summary, likely_driver

Computation & narrative
- Compute sector intensity_0_3 (quartiles across non-zero sectors) and momentum (2015–18 / 2019–22 / 2023–25).
- Top counterparts per sector (max 2) and flag consortium skew if top1_share>0.5.
- 3–5 bullets: what stands out, where evidence is thin, and one Next Data Boost.

Output contract
- Create a new canvas titled EXACTLY:
  "Write <COUNTRY NAME> Phase 2 — Technology Landscape (reports/country=<ISO2>/phase-2_landscape.md)"
- The canvas must contain ONLY the final markdown for that file, with front-matter (title, author, date) and the filled tables AND the extracted TSV/CSV snippets (in code blocks) that I found, clearly labeled for copy-in.
- Include web citations inline for every non-obvious factual claim.
