Below is a copy‑paste prompt for Claude Code. It will **append or create** Austria‑specific watchlist entries in `queries/policy/watchlist.yaml` safely and idempotently.

---

# Claude Code — Update `queries/policy/watchlist.yaml` with Austria entries
**Goal:** Ensure the following AT entries exist in `queries/policy/watchlist.yaml`. If the file doesn’t exist, create it. If entries with the same `name` already exist, **replace** those blocks with the versions below (idempotent update). Preserve all other existing items.

**Then print:** `UPDATED queries/policy/watchlist.yaml (AT entries upserted)`

### Entries to upsert (YAML)
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

**Implementation notes for Claude Code:**
1. If `queries/policy/watchlist.yaml` is missing, create it with only the entries above.
2. If present, parse as YAML list; for each entry above, find any list item with the same `name` and replace it; if not found, append.
3. Keep YAML formatting neat (list at root). Do **not** remove unrelated items.
4. Save the file and print the one‑line confirmation.

