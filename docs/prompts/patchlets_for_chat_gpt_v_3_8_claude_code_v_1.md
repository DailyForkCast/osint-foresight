# Patchlets for ChatGPT v3.8 & Claude Code v1.8 — Red‑Team v2

**Purpose:** Drop‑in edits to strengthen compliance, coverage, normalization, and QA loops. Copy/paste into the operator prompt files and Claude Code repo. Designed for zero‑budget, 100% legal OSINT.

---

## A) ChatGPT Operator v3.8 — New TOGGLES & PHASES (paste into Run Context)

```yaml
TOGGLES:
  INCLUDE_COMPLIANCE_GUARDRAILS: true    # enable TOS/robots/archiving checks
  INCLUDE_NAME_VARIANTS: true            # enable local/zh-CN transliteration expansion
  INCLUDE_PROCUREMENT_FEEDS: true        # enable national/EU tender feeds
  INCLUDE_ROLE_ENSEMBLE: true            # enable Librarian/Mapper/Checker/Adversary/Editor flow
```

### New Phases (append to phase list)

```yaml
Phase 1A — Compliance Map
  Goal: Block non‑compliant collection; record domain‑level compliance state.
  Inputs: country, source_list (proposed URLs/domains)
  Outputs: compliance_map.json, tos_whitelist.csv, robots_log.json
  Rules:
    - Only fetch from domains greenlisted in tos_whitelist.csv
    - Respect robots.txt; if disallowed, create a Data Ticket and skip
    - For any “critical” claim source, require archive_url (e.g., Wayback/Perma) alongside exact_url

Phase 3B — Name Variant Expansion
  Goal: Expand person/org/department names to local language + zh‑CN (where relevant) and common transliterations.
  Outputs: name_variants.csv with columns: entity_id, kind{person|org|dept}, lang, form, source, note
  Rules: include pinyin spaced/unspaced, simplified/traditional, hyphen and spacing variants; reuse across phases.

Phase 4C — Procurement Feeds
  Goal: Add public tender feeds and procurement award ledgers to inputs.
  Outputs: procurement_feeds.json (feed_url, country_scope, format{RSS|HTML|CSV|API}, parser_notes)
  Rules: no scraping of disallowed portals; manual capture allowed with citation screenshots; focus on EU TED + national mirrors.

Phase 6C — COI & Integrity Signals
  Goal: Capture research integrity risk signals.
  Outputs: coi_integrity_signals.json (author_id, signal{retraction|dual_affil|undisclosed_funding|ban|watchlist}, evidence_url, date, notes)
  Rules: evidence‑link required; no allegation without a published source.

Phase 9B — Deception Indicators
  Goal: Flag adversarial deception patterns (front orgs, cloned sites, staged PRs).
  Outputs: phase09_sub12_deception_indicators.json (pattern, org_id, indicator, evidence_url, confidence)
  Rules: use conservative confidence; require at least two independent indicators for High.
```

---

## B) ChatGPT Operator v3.8 — Role Ensemble Block (insert under "Process")

```markdown
# ROLE ENSEMBLE (if INCLUDE_ROLE_ENSEMBLE)
- Librarian → plans sources; emits phase01_sources.json, updates tos_whitelist.csv
- Mapper → normalizes to ROR/LEI/ORCID; emits *_normalized.json
- Checker → validates schemas, citations, and compliance; emits *_validation.json + rejects[]
- Adversary → red‑teams claims & sources; emits adversary_notes.md + risk deltas
- Editor → produces exec briefs; cross‑links to artifacts; notes residual unknowns

Run 2–3 short independent passes for high‑stakes claims (MCF links, supply overlaps). Checker reconciles divergences and appends a “consistency_note” to each claim.
```

---

## C) ChatGPT Operator v3.8 — Schema‑First & No‑Drop Enforcement (append to QA section)

```markdown
- JSON SCHEMA VALIDATION: For every artifact, validate keys and types. If normalization fails, DO NOT drop the item. Place it in rejects[] with reason and minimal raw fields.
- NO‑DROP RULE: If department resolution fails, record org‑level node with dept_id=null and confidence=Low. Create a Data Ticket for follow‑up.
- EVIDENCE PRIOR: Add data_quality_prior in {1..5}. Compute decision_readiness as function(probability, confidence, data_quality_prior).
```

---

## D) Claude Code v1.8 — Compliance & QA Enhancements (new/updated modules)

> **Add these files/functions to the repo.** Wire the compliance gate to run before any network fetch.

```python
# compliance/robots.py
import urllib.robotparser as urp
from urllib.parse import urlparse
from datetime import datetime
import json

ROBOTS_LOG = 'robots_log.json'

_cache = {}

def _load_log():
    try:
        with open(ROBOTS_LOG,'r',encoding='utf-8') as f: return json.load(f)
    except Exception:
        return {}

def _save_log(data):
    with open(ROBOTS_LOG,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)


def check_domain_ok(url:str, ua='ClaudeCodeBot') -> dict:
    """Return {'allowed': bool, 'reason': str, 'robots_cached': str}
    Also updates robots_log.json per domain.
    """
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    log = _load_log()
    if domain in _cache:
        allowed = _cache[domain]
    else:
        rp = urp.RobotFileParser()
        rp.set_url(domain + '/robots.txt')
        try:
            rp.read()
            allowed = rp.can_fetch(ua, url)
        except Exception:
            allowed = True  # default permissive if robots.txt not reachable
        _cache[domain] = allowed
    log[domain] = {
        'checked_at': datetime.utcnow().isoformat()+'Z',
        'allowed_example': url,
        'allowed': bool(allowed)
    }
    _save_log(log)
    return {'allowed': bool(allowed), 'reason': 'robots.txt check', 'robots_cached': domain+'/robots.txt'}
```

```python
# validators/compliance.py
import csv, json
from urllib.parse import urlparse
from compliance.robots import check_domain_ok

TOS_WHITELIST = 'tos_whitelist.csv'


def _domain(url):
    p = urlparse(url)
    return p.netloc.lower()


def enforce_compliance(artifact:dict, critical:bool=False):
    """Raise RuntimeError if any source url violates whitelist/robots.
       Require archive_url for critical items.
    """
    # Load whitelist
    wl = set()
    try:
        with open(TOS_WHITELIST, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                wl.add(row['domain'].lower())
    except Exception:
        pass

    for item in artifact.get('items', []):
        url = item.get('exact_url') or ''
        if not url: continue
        dom = _domain(url)
        if wl and dom not in wl:
            raise RuntimeError(f'Domain not whitelisted: {dom}')
        chk = check_domain_ok(url)
        if not chk['allowed']:
            raise RuntimeError(f'Blocked by robots: {url}')
        if critical and not item.get('archive_url'):
            raise RuntimeError(f'Missing archive_url for critical source: {url}')
```

```python
# collectors/name_variants.py
import itertools

def build_name_variants(entities:list, langs=['EN','local','zh-CN']):
    """entities: [{'entity_id','kind','name','lang','aliases':[],'script': 'Latn|Hans|Hant'}]
    returns list of variants including pinyin/hyphen/spacing forms.
    """
    out = []
    for e in entities:
        base = [e['name']] + e.get('aliases', [])
        forms = set()
        for b in base:
            forms.add(b)
            forms.add(b.replace('-', ' '))
            forms.add(b.replace(' ', ''))
        # (Optional) add pinyin conversions here if available upstream
        for f in forms:
            out.append({
                'entity_id': e['entity_id'], 'kind': e['kind'],
                'lang': e.get('lang','EN'), 'form': f, 'source': 'rulegen', 'note': ''
            })
    return out
```

```python
# pipeline/hooks.py
from validators.compliance import enforce_compliance


def pre_fetch_gate(artifact:dict, critical=False):
    enforce_compliance(artifact, critical=critical)

# call pre_fetch_gate(...) before any network fetch in collectors
```

---

## E) Claude Code v1.8 — Standards & Dept Confidence (replace placeholders)

```python
# scoring/weights.py
ROLE_WEIGHTS = {'editor': 3, 'rapporteur': 2, 'member': 1}
SOURCE_WEIGHTS = {'orcid': 3, 'author_affil': 2, 'inst_web': 1}

def confidence_from_sources(sources_hit:list) -> str:
    score = sum(SOURCE_WEIGHTS.get(src,1) for src in sources_hit)
    return 'High' if score >= 5 else 'Med' if score >= 3 else 'Low'
```

```python
# normalization/departments.py
from scoring.weights import confidence_from_sources

def resolve_department(evidence:list):
    """evidence: list of {'source':'orcid|author_affil|inst_web', 'dept':'...'}"""
    depts = [e.get('dept') for e in evidence if e.get('dept')]
    if not depts:
        return {'dept_id': None, 'confidence': 'Low', 'notes': 'org-level only'}
    # naive pick most frequent; real impl should ROR-match if available
    pick = max(set(depts), key=depts.count)
    conf = confidence_from_sources([e['source'] for e in evidence])
    return {'dept_id': pick, 'confidence': conf, 'notes': ''}
```

---

## F) Artifacts — Required outputs (add/confirm in both prompts)

- `compliance_map.json` — domain → compliance state
- `tos_whitelist.csv` — columns: domain, basis (API|OAI‑PMH|Open‑License|Gov‑Open‑Data)
- `robots_log.json` — per‑domain last check & example URL
- `name_variants.csv` — entity_id, kind, lang, form, source, note
- `procurement_feeds.json` — feed_url, scope, format, parser_notes
- `coi_integrity_signals.json` — author_id, signal, evidence_url, date
- `phase09_sub12_deception_indicators.json` — pattern, org_id, indicator, evidence_url, confidence
- `*_validation.json` — per‑artifact schema validation results + rejects[]

---

## G) Ground Rules (paste into Legal/TOS section)

1) **Whitelist‑first.** Only collect from domains in `tos_whitelist.csv`.
2) **Respect robots.txt.** If disallowed, no automated fetch; log in `robots_log.json` and open a Data Ticket.
3) **Manual‑only grey areas.** For sites permitting viewing but forbidding bots, allow **human-in-the-loop** capture (screenshots, citations), never automated scraping.
4) **Archival:** Critical claims require `archive_url` in addition to `exact_url`.
5) **No login/paywall bypass.** No credentialed sessions, no scraping behind auth, no rate‑limit evasion.

---

## H) Integration Checklist (Claude Code & Operator)

- [ ] Insert TOGGLES + New Phases into ChatGPT v3.8 operator file.
- [ ] Add Role Ensemble block and Schema/No‑Drop language.
- [ ] Create `compliance/robots.py`, `validators/compliance.py`, `collectors/name_variants.py`, `pipeline/hooks.py`, `scoring/weights.py`, `normalization/departments.py`.
- [ ] Wire `pre_fetch_gate()` before any collector fetch.
- [ ] Replace placeholder `role_weight=1` with `ROLE_WEIGHTS` rubric; propagate to standards artifacts.
- [ ] Add artifact emission to pipelines and validation to CI (JSON schema lint + required‑fields check).

---

## I) Minimal Test Plan (paste into repo README or /tests)

- **Robots/TOS:** Provide one allowed and one disallowed URL; expect compliant pass and blocked exception + ticket.
- **Archive Required:** Mark one artifact as critical; omit archive_url; expect failure.
- **Name Variants:** Input entities with hyphen/space variants; verify distinct outputs.
- **Dept Confidence:** Feed ORCID+author_affil+inst_web; expect High; remove ORCID; expect Med.
- **Schema Rejects:** Pass an item missing normalized keys; expect presence in rejects[] and zero silent drops.

---

## J) Operator Snippet — Data Tickets (ensure present)

```markdown
If any step fails (compliance, schema, normalization), emit a **Data Ticket** with: phase, artifact, error, source_url, suggested remediation. Do not proceed with silent drops.
```

---

**Ready for Claude Code hand‑off.** Paste sections A–C into the ChatGPT operator doc; add D–E modules to the Claude Code repo; confirm F–J across both.
