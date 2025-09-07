Research & write Phase 1 — Indicators & Data Sources for <COUNTRY NAME> (<ISO2>).

Scope & rules
- Years: 2015–2025. Looser matchers ON.
- You MAY browse to verify country-specific nuances (cite if you add claims), but focus on defining stable indicator contracts that render even with sparse data.

What to include
- Data Inventory: expected processed files under `data/processed/country=<ISO2>/` (relationships.csv, signals.csv, standards_roles.tsv, cer_master.csv, institutions.csv, mechanism_incidents.tsv, programs.csv, sanctions_hits.csv, policy_*.tsv).
- Core Indicator table: for each file, list indicator families, which phases use them, and short notes (guardrails, ambiguity handling).
- Column contracts (tolerant schemas) for each file (include minimal required columns and allow blanks).
- Minimal Collection Plan (“happy path”): pull → normalize → build commands.
- Narrative snapshot: how the later phases will use these indicators; what will still render if inputs are missing.
- One “Next Data Boost” suggestion (e.g., “add CORDIS participants CSV slice”).
- If you add any country-specific assertions (e.g., a national agency nuance), CITE them.

Output contract
- Create a new canvas titled EXACTLY:
  "Write <COUNTRY NAME> Phase 1 — Indicators & Data Sources (reports/country=<ISO2>/phase-1_indicators.md)"
- The canvas must contain ONLY the final Markdown with front-matter (title, author, date).
- Do not include instructions or changelogs inside the file.
- Assume templates may be missing; still produce a complete, human-readable report (add clear “No data yet” notes where relevant).
