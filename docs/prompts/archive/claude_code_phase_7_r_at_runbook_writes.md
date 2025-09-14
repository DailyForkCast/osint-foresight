# Claude Code — Phase 7R (Austria, AT) — Runbook & Writes

## Goal
Create the **Assumption Check & Red‑Team Review** artifacts for Austria. Capture assumptions, contradictions, gaps, weak assertions, bias notes, alternative hypotheses, stress tests, and a short verdict. Keep all legal/sanctions mentions as **signals only** and **exclude US persons**.

## 0) Paths
- Country: `AT`
- Report: `reports/country=AT/phase-7r_redteam.md`
- Data dir: `data/processed/country=AT/`

## 1) Save the Phase‑7R report
- Write the companion canvas **“Write Austria Phase 7R — Assumption Check & Red‑Team Review (reports/country=AT/phase-7r_redteam.md)”** to that exact path. Create directories as needed.

## 2) Scaffold TSVs (idempotent)
Create these files with headers; include a `notes` column where appropriate. If empty, add one `no_data_yet=true` row.

- `data/processed/country=AT/p7r_assumptions.tsv`
  Columns: `assumption_id,statement,phase_origin,basis,impact_if_wrong,confidence_LMH,notes`

- `data/processed/country=AT/p7r_contradictions.tsv`
  Columns: `claim_id,claim_text,source_a,source_b,why_in_tension,status,notes`

- `data/processed/country=AT/p7r_gaps.tsv`
  Columns: `gap_id,domain,why_it_matters,how_to_close,effort_1to3,notes`

- `data/processed/country=AT/p7r_weak_assertions.tsv`
  Columns: `assertion_id,text,current_evidence,needed_evidence,priority_1to3,notes`

- `data/processed/country=AT/p7r_bias.tsv`
  Columns: `bias_id,bias_type,description,mitigation,notes`

- `data/processed/country=AT/p7r_hypotheses.tsv`
  Columns: `hid,hypothesis,plausibility_LMH,discriminator_test,data_needed,notes`

- `data/processed/country=AT/p7r_stresstests.tsv`
  Columns: `sid,scenario,expected_observables,implications,trigger_to_watch,notes`

- `data/processed/country=AT/p7r_actions.tsv`
  Columns: `aid,action,owner,due_by,status,notes`

## 3) Populate from prior phases
- Pull assumptions from **executive summaries** and **narratives** in Phases 2/2S/3/4/5/6/7C.
- Log contradictions where event signals clash with capacity evidence.
- Convert Phase‑6 **risk deltas** and Phase‑7C **MO plausibility** into testable hypotheses and stress tests.

## 4) Evidence Register discipline
Append any policy/portal/scope PDFs to `data/evidence_register.tsv` with:
`id,country,type,title,issuer_or_site,url,retrieved_at,sha256,anchor_hash,notes`.

## 5) Health & report tasks
```
make health COUNTRY=AT
make reports-init COUNTRY=AT
```

## 6) Commit
`feat(AT): phase‑7R red‑team — assumptions, contradictions, gaps, weak assertions, biases, hypotheses, stress tests`

---

### Optional VS Code task: phase‑7r:bootstrap
```jsonc
{
  "label": "phase-7r:bootstrap",
  "type": "shell",
  "command": "python",
  "args": [
    "-c",
    "import os; p='data/processed/country=${input:countryCode}'; os.makedirs(p, exist_ok=True);\n"+
    "open(p+'/p7r_assumptions.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7r_contradictions.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7r_gaps.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7r_weak_assertions.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7r_bias.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7r_hypotheses.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7r_stresstests.tsv','a+',encoding='utf-8').close();\n"+
    "open(p+'/p7r_actions.tsv','a+',encoding='utf-8').close(); print('ok')"
  ],
  "problemMatcher": []
}
```

### Notes
- Keep all sanctions/legal references as **signals only** and **exclude US persons**.
- Use short, testable phrasing for hypotheses and stress tests so they drive collection, not debate.
