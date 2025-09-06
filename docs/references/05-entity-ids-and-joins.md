# Entity IDs, Registries & Join Keys

- **LEI (GLEIF):** global legal entity identifier; use Level‑2 Relationships for parents/children.
- **ROR:** research organization registry; useful for unis/labs; join to LEI by name/country.
- **OpenCorporates:** national registry IDs, officers, corporate groupings.
- **National registries:** (e.g., Portuguese RNPC, UK Companies House, etc.) — add to `registry_ids` as `country:id` pairs.

**Join strategy:**
1) Normalize names (EN/local/ZH) and countries → attempt deterministic joins on LEI/ROR/registry id.
2) Fuzzy match remainder; assign a `cer_id`; record provenance and confidence.
3) Store in `cer/cer_master.csv`.