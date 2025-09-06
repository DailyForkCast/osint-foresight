# FAQ & Troubleshooting

**Q: I ran a VS Code task and nothing happened.**
A: With the CHOOSE sentinel in the country picker, you must pick a real ISO2 code.

**Q: API rate limits / 429s?**
A: Add sleeps/backoff; for Crossref, include a polite `mailto` parameter; cache pages to `data/raw/`.

**Q: OPS auth errors?**
A: Verify `EPO_OPS_KEY`/`EPO_OPS_SECRET` in `.env.local`. Some endpoints require OAuth vs. basic key usage.

**Q: BigQuery access?**
A: Ensure a `GCP_PROJECT` exists and billing is enabled (public data is free to query up to monthly limits). If using service accounts, set `GOOGLE_APPLICATION_CREDENTIALS`.

**Q: PATENTSCOPE export fails?**
A: Reduce result size with tighter years/CPC; export CSV in smaller batches, then merge during normalization.