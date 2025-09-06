# LLM House Rules (Deterministic Writes)
- Write file content **verbatim** from the user's canvas.
- **Do not** summarize, reformat, or "align" to a prior style unless explicitly instructed.
- Print only `WRITE <path>` or `UPDATED <path>` confirmations.
- Do **not** run `git push` unless explicitly asked.
- Respect exact paths and case (e.g., `AT-portals.md`, not `at_portals.md`).