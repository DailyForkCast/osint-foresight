Below is a single, copy‑paste **micro‑prompt** for ChatGPT to generate Phase 0 for any country **with a no‑screenshot evidence versioning system** that Claude Code can execute in VS Code.

---

# Run Phase 0 — Setup (watchdog/think tank) for <COUNTRY> (<ISO2>)

## Output contract
- Create a canvas titled EXACTLY:
  "Write <COUNTRY> Phase 0 — Setup (reports/country=<ISO2>/phase-0_setup.md)"
- The canvas must contain **ONLY final file content** (human‑readable Markdown + front‑matter) for that path.
- Use **Excel‑Ready Mode**: every table must be returned twice — (1) Markdown and (2) fenced block labeled `# excel-tsv` (UTF‑8 TSV).
- Assume timeframe **2015–present**, languages **["en","<local>"]**.
- If sources are thin, still render a complete report with clear “No data yet” notes.

---

## Sections to produce
1) **Front‑matter** (title, author, date).
2) **SESSION header & watchdog guardrails** — independence, reproducibility, proportionality, privacy/ethics, non‑advocacy; Happy Path & Panic Buttons (write empty‑but‑valid TSVs if a source is missing).
3) **References & Portals (seed list)** — govt/regulators; funding/programs; standards/accreditation; research/statistics/IP; trade/logistics/registries; EU/international. For each, add a one‑line **use case** and a **refresh cadence** tag.
4) **Watchlist (YAML)** — 6–8 entries with `name, url, cadence` (weekly/monthly/quarterly). Include as code block.
5) **Evidence discipline & NO‑SCREENSHOT versioning protocol** — (see protocol below). Return two TSVs:
   - `EvidenceRegister.tsv` (master index)
   - `EvidenceChanges.tsv` (delta since last run)
6) **Audit protocol** — how we re‑verify stale items (> 36 months) and target Cohen’s κ ≥ 0.7 for double‑coding.
7) **Next Data Boost** — one pragmatic, high‑ROI action.

---

## NO‑SCREENSHOT Evidence Versioning Protocol (text‑hash method)
Because Claude Code and ChatGPT cannot take screenshots, we capture **verifiable text anchors + cryptographic hashes** of page content and store a local snapshot. This produces stable, auditable evidence without images.

### A) Evidence Pack layout (per run)
Store raw and normalized text under:
```
project_root/
  data/evidence/country=<ISO2>/date=<YYYY-MM-DD>/
    raw/<slug>.<ext>            # original fetched file (HTML/PDF/TXT)
    text/<slug>.txt             # normalized plain text (see rules below)
    meta/<slug>.json            # URL, title, publisher, access_datetime_utc, mime, http_status
    hash/<slug>.sha256          # SHA256(content of text/<slug>.txt)
    manifest.json               # list of all slugs with hashes
```

### B) Text normalization rules (deterministic)
1. For HTML: strip tags; keep visible text; collapse whitespace; keep ASCII punctuation; preserve diacritics.
2. For PDF: extract via `pdftotext -layout` (or similar), then apply the same whitespace rules.
3. Lowercase **only for hashing**; keep a human‑readable copy in `text/`.
4. Save the **first 250 chars** and **a 250‑char mid‑document anchor** (character offsets) to meta for quick verification.

### C) Hashing & change detection
- Compute `sha256(text/<slug>.txt)`; compare against the **most recent previous manifest** for the same `<slug>`.
- Mark `delta_status` ∈ {`new`,`same`,`changed`,`gone`}.
- If `changed`, compute a unified diff of normalized text (or a 3‑line context diff around changed anchors) and store as `diff/<slug>.patch`.

### D) Evidence Register (master index)
Assign stable `evidence_id` = `<YYYYMMDD>-<shortslug>`. For every item, record URL, title, publisher, access time, hash, anchors, local paths, and current/previous hash + delta.

### E) Git workflow (lightweight)
- Commit `data/evidence/country=<ISO2>/date=YYYY-MM-DD/` and updated TSVs.
- Commit message template: `evidence: <ISO2> <YYYY-MM-DD> <N_new>/<N_changed>/<N_same>/<N_gone>`.

### F) Optional archival hint
- If policy allows, also paste the public URL into an archival service (e.g., Web Archive). Record the archive URL in `meta/<slug>.json` (manual step; not required).

---

## TSV Schemas (return both Markdown + `# excel-tsv`)

### 1) EvidenceRegister.tsv (master index)
Columns:
```
# excel-tsv
evidence_id	url	title	publisher	access_datetime_utc	mime_type	content_hash_sha256	first_anchor	middle_anchor	local_raw_path	local_text_path	local_meta_path	local_hash_path	previous_hash_sha256	delta_status	notes
```
- **first_anchor/middle_anchor**: 200–250‑char text snippets for human verification.
- **delta_status**: new / same / changed / gone.

### 2) EvidenceChanges.tsv (delta since last run)
Columns:
```
# excel-tsv
evidence_id	url	change_type	prev_hash	new_hash	diff_path	comment
```
- Include only rows where `delta_status ∈ {changed, gone, new}`.

---

## Narrative block to include (Phase 0)
- **Watchdog overview:** 1–2 paragraphs on the country’s open‑source posture, the key portals we will rely on, and the cadence of refresh.
- **Versioning rationale:** 1 paragraph on why **text‑hash + anchors** provides durable, auditable evidence without screenshots; limitations (dynamic pages, localization) and mitigation (anchors + meta.json + diffs).

---

## Watchlist YAML (example format to render)
```
- name: National R&I agency portal
  url: https://<example>
  cadence: monthly
- name: National accreditation directory (ISO/IEC 17025)
  url: https://<example>
  cadence: quarterly
- name: EU Funding & Tenders (country filter)
  url: https://<example>
  cadence: weekly
- name: IETF Datatracker (WG roles, country orgs)
  url: https://datatracker.ietf.org/
  cadence: monthly
- name: OFAC/EU/UK consolidated sanctions portals
  url: https://ofac.treasury.gov/; https://www.sanctionsmap.eu/; https://www.gov.uk/government/collections/financial-sanctions-regime-specific-consolidated-list
  cadence: weekly
```
*(The report should render a country‑specific version of the above.)*

---

## Next Data Boost (close the report)
Suggest **one** high‑ROI action (e.g., “Seed the Evidence Pack with 5 priority portals and commit hashes”).

---

## Automation helpers (optional) — VS Code tasks + Python helper
> Use these to implement the **no‑screenshot evidence versioning** workflow directly from VS Code. Claude Code can create these files verbatim.

### 1) Save this Python helper
**Path:** `scripts/evidence_hash.py`
```python
#!/usr/bin/env python3
import argparse, csv, hashlib, json, os, sys
from pathlib import Path
from datetime import datetime
import difflib

COLS_REG = [
  "evidence_id","url","title","publisher","access_datetime_utc","mime_type",
  "content_hash_sha256","first_anchor","middle_anchor","local_raw_path",
  "local_text_path","local_meta_path","local_hash_path","previous_hash_sha256",
  "delta_status","notes",
]
COLS_CHG = ["evidence_id","url","change_type","prev_hash","new_hash","diff_path","comment"]

def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}

def write_tsv(rows, cols, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='	', lineterminator='
')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

def latest_prev_dir(base: Path, current_date: str):
    # find most recent date folder older than current_date
    if not base.exists():
        return None
    dates = []
    for p in base.glob('date=*'):
        d = p.name.split('=',1)[1]
        if d < current_date:
            dates.append(d)
    if not dates:
        return None
    return base / f"date={sorted(dates)[-1]}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--country', required=True, help='ISO2 country code e.g., AT')
    ap.add_argument('--date', required=False, help='YYYY-MM-DD (default: today)')
    ap.add_argument('--base', default='data/evidence', help='base evidence dir')
    args = ap.parse_args()

    today = datetime.utcnow().strftime('%Y-%m-%d')
    date = args.date or today

    base = Path(args.base) / f"country={args.country}"
    cur_dir = base / f"date={date}"
    text_dir = cur_dir / 'text'
    meta_dir = cur_dir / 'meta'
    raw_dir  = cur_dir / 'raw'
    hash_dir = cur_dir / 'hash'
    diff_dir = cur_dir / 'diff'
    for d in (text_dir, meta_dir, raw_dir, hash_dir, diff_dir):
        d.mkdir(parents=True, exist_ok=True)

    prev_dir = latest_prev_dir(base, date)
    prev_manifest = {}
    if prev_dir and (prev_dir / 'manifest.json').exists():
        prev_manifest = json.loads((prev_dir / 'manifest.json').read_text(encoding='utf-8'))

    # current manifest we will write
    manifest = {}

    rows_reg = []
    rows_chg = []

    # index previous hashes by slug for quick lookup
    prev_hashes = prev_manifest.get('hashes', {}) if isinstance(prev_manifest, dict) else {}

    # iterate current text files
    for txt in sorted(text_dir.glob('*.txt')):
        slug = txt.stem
        text = txt.read_text(encoding='utf-8', errors='ignore')
        first_anchor = text[:250].replace('
',' ')[:250]
        mid_start = max(0, (len(text)//2) - 125)
        middle_anchor = text[mid_start:mid_start+250].replace('
',' ')[:250]

        h = sha256_path(txt)
        (hash_dir / f"{slug}.sha256").write_text(h + "
", encoding='utf-8')

        meta = load_json(meta_dir / f"{slug}.json")
        url = meta.get('url','')
        title = meta.get('title','')
        publisher = meta.get('publisher','')
        access_dt = meta.get('access_datetime_utc','')
        mime = meta.get('mime','') or meta.get('mime_type','')

        prev_hash = prev_hashes.get(slug, '')
        if not prev_hash:
            delta = 'new'
        elif prev_hash == h:
            delta = 'same'
        else:
            delta = 'changed'

        evidence_id = f"{date.replace('-','')}-{slug[:12]}"

        rows_reg.append({
            "evidence_id": evidence_id,
            "url": url,
            "title": title,
            "publisher": publisher,
            "access_datetime_utc": access_dt,
            "mime_type": mime,
            "content_hash_sha256": h,
            "first_anchor": first_anchor,
            "middle_anchor": middle_anchor,
            "local_raw_path": str((raw_dir / f"{slug}").with_suffix('.html')),
            "local_text_path": str(txt),
            "local_meta_path": str(meta_dir / f"{slug}.json"),
            "local_hash_path": str(hash_dir / f"{slug}.sha256"),
            "previous_hash_sha256": prev_hash,
            "delta_status": delta,
            "notes": meta.get('notes',''),
        })

        if delta == 'changed':
            diff_path = diff_dir / f"{slug}.patch"
            prev_txt = prev_dir / 'text' / f"{slug}.txt" if prev_dir else None
            prev_text = prev_txt.read_text(encoding='utf-8', errors='ignore') if (prev_txt and prev_txt.exists()) else ''
            ud = difflib.unified_diff(
                prev_text.splitlines(), text.splitlines(),
                fromfile=f"prev/{slug}.txt", tofile=f"cur/{slug}.txt", lineterm=''
            )
            diff_path.write_text('
'.join(ud) + '
', encoding='utf-8')
            rows_chg.append({
                "evidence_id": evidence_id, "url": url, "change_type": "changed",
                "prev_hash": prev_hash, "new_hash": h, "diff_path": str(diff_path), "comment": ''
            })
        elif delta == 'new':
            rows_chg.append({
                "evidence_id": evidence_id, "url": url, "change_type": "new",
                "prev_hash": '', "new_hash": h, "diff_path": '', "comment": ''
            })

        manifest.setdefault('hashes', {})[slug] = h

    # mark 'gone' items (present before, missing now)
    for slug, ph in prev_hashes.items():
        if not (text_dir / f"{slug}.txt").exists():
            evidence_id = f"{date.replace('-','')}-{slug[:12]}"
            url = ''
            rows_chg.append({
                "evidence_id": evidence_id, "url": url, "change_type": "gone",
                "prev_hash": ph, "new_hash": '', "diff_path": '', "comment": ''
            })

    # write TSVs next to report path convention
    out_dir = Path(f"reports/country={args.country}")
    out_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(rows_reg, COLS_REG, out_dir / 'EvidenceRegister.tsv')
    write_tsv(rows_chg, COLS_CHG, out_dir / 'EvidenceChanges.tsv')

    # write manifest
    (cur_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"Wrote {len(rows_reg)} EvidenceRegister rows and {len(rows_chg)} EvidenceChanges rows.")

if __name__ == '__main__':
    sys.exit(main())
```

### 2) Add VS Code tasks (append to `.vscode/tasks.json`)
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "evidence:init-run-folder",
      "type": "shell",
      "command": "python - <<'PY'
from pathlib import Path; import sys, datetime
import json
country='${input:country}'
from datetime import datetime
date='${input:date}' or datetime.utcnow().strftime('%Y-%m-%d')
base=Path('data/evidence')/f'country={country}'/f'date={date}'
for sub in ['raw','text','meta','hash','diff']:
    (base/sub).mkdir(parents=True, exist_ok=True)
print(f'Initialized {base}')
PY",
      "problemMatcher": []
    },
    {
      "label": "evidence:hash",
      "type": "shell",
      "command": "python scripts/evidence_hash.py --country ${input:country} --date ${input:date}",
      "group": { "kind": "build", "isDefault": false },
      "problemMatcher": []
    }
  ],
  "inputs": [
    { "id": "country", "type": "promptString", "description": "ISO2 country (e.g., AT)", "default": "AT" },
    { "id": "date", "type": "promptString", "description": "Run date YYYY-MM-DD (blank=today)", "default": "" }
  ]
}
```

> Optional Makefile target (place in `Makefile`):
```make
EVIDENCE_DATE ?= $(shell date -u +%F)
evidence:
	python scripts/evidence_hash.py --country $(COUNTRY) --date $(EVIDENCE_DATE)
```

**How to use:**
- Run `evidence:init-run-folder` to create the date folder.
- Drop any fetched raw files to `raw/` and normalized text to `text/` with matching slugs; put minimal meta JSONs in `meta/`.
- Run `evidence:hash` to compute hashes and write `EvidenceRegister.tsv` + `EvidenceChanges.tsv`.
- Commit `data/evidence/...` and `reports/country=<ISO2>/*.tsv` with the message: `evidence: <ISO2> <YYYY-MM-DD> <N_new>/<N_changed>/<N_same>/<N_gone>`.

---

**This section does not change the report content.** It provides ready-to-use automation that implements the versioning protocol described above.

