Research & write Phase 2S — Supply Chain Security for <COUNTRY NAME> (<ISO2>).

Scope & rules
- Years: 2015–2025. Looser matchers ON.
- You MUST browse authoritative sources and CITE them (web.run).
- Focus on five pillars: Knowledge, Technology, Materials, Finance, Logistics.

What to search (authoritative examples)
- Logistics/procurement: national procurement portal, EU TED summaries, national customs/dual-use guidance.
- Infrastructure: HPC centers, national labs, cryogenics/vacuum/photolithography suppliers, specialized fab/service vendors.
- Finance: public investment/sovereign funds/innovation banks, notable JV/MoUs press.
- Controls/sanctions: national sanctions pages, OpenSanctions summaries (secondary), enforcement advisories.
- Training/knowledge: national fellowship programs, workforce MoUs, large training workshops.

Extract (create tiny tables)
- relationships.csv (append-ready): sector, counterpart_name, counterpart_country, collab_type, year
  (Use collab_type values that map to pillars: co-publication, co-project, infrastructure, procurement, investment, licensing, training.)
- sanctions_hits.csv (optional): name, country, list, listed_on, url
- mechanism_incidents.tsv (optional): entity, country, sector, mechanism_family, year, ref
- signals.csv (optional): window, signal_summary, likely_driver

Computation & narrative
- Map collab_type→pillars (K/T/M/F/L), count per sector.
- PRC exposure: count & share of CN edges per sector; list top 1–2 CN counterparts if present.
- Sanctions overlay: matches by exact name (red-flag, not dispositive).
- 3–5 bullets: practical exposure notes + one Next Data Boost (e.g., “add tenders CSV 2019–2025”).

Output contract
- Create a new canvas titled EXACTLY:
  "Write <COUNTRY NAME> Phase 2S — Supply Chain Security (reports/country=<ISO2>/phase-2s_supply_chain.md)"
- The canvas must contain ONLY the final markdown with front-matter; include any extracted append-ready TSV/CSV snippets in code blocks; cite sources inline.
