Research & write Phase 3 — Institutions & Accredited Labs for <COUNTRY NAME> (<ISO2>).

Scope & rules
- Years: 2015–2025. Looser matchers ON.
- You MUST browse authoritative sources and CITE them (web.run).
- Prioritize the national accreditation body and official institute/lab directories.

What to search (authoritative examples)
- National Accreditation Body (e.g., Akkreditierung Austria / UKAS / DAkkS): ISO/IEC 17025/17020 directories, scopes, cities.
- National research agency portals listing institutes and centers.
- Top universities/labs pages (institutes, research centers).
- Standards organizations (national SDO membership pages) to link orgs in standards roles.

Extract (create tiny tables)
- institutions.csv (append-ready):
  name, country, org_type, is_lab, accreditation_id, scope, city
- standards_roles.tsv (if found): wg, role, person_name, org_name, country, sector_hint
- relationships.csv (optional): sector, counterpart_name, counterpart_country, collab_type, year (if institutional partnerships are shown)

Computation & narrative
- Counts by org_type; top 10 accredited labs (name, accreditation_id, scope, city).
- Standards-linked organizations sample (up to 10).
- Relationship coverage: top institutions appearing in Phase-2 edges.
- 3–5 bullets; include one clear “how to add accreditation CSV” note.

Output contract
- Create a new canvas titled EXACTLY:
  "Write <COUNTRY NAME> Phase 3 — Institutions & Accredited Labs (reports/country=<ISO2>/phase-3_institutions.md)"
- The canvas must contain ONLY the final markdown with front-matter; include any extracted append-ready TSV/CSV snippets in code blocks; cite sources inline.
