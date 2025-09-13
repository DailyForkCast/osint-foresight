# Analyst Prompt Pack — Narrative Sources (Policy/White Papers)

Use these prompts with ChatGPT/Claude/Gemini to turn unstructured documents into structured facts that feed Phases 5/6/7C/2S. They're designed for a **single analyst** and work offline with pasted text.

---

## 0) Quick Triage (10 minutes per doc)
> I will paste an excerpt from a policy document. In a numbered list, tell me: (1) what this is (type/issuer), (2) top three points in plain English, (3) any concrete mechanisms or controls, (4) whether it matters for supply‑chain security (Materials/Knowledge/Technology/Finance/Logistics), (5) a 2‑sentence summary I can use later.

---

## 1) Policy Snapshot (single TSV row)
> Using the **Policy Snapshot Extractor** schema, produce **one TSV row**: source_id, title, issuer, issuer_level, pub_date, url, lang, country_scope, policy_domain, sectors (taxonomy terms), instruments, maturity, stance_prc_mcf, enforcement_tools, time_horizon, review_cycle, credibility_1_5, confidence, summary. If unknown, leave blank. Keep summary <= 500 chars.

---

## 2) Mechanisms & Controls (claims TSV)
> Extract **concrete claims** as TSV rows with fields: source_id, claim_id, page, paragraph, claim_text, claim_type (mechanism/control/funding/standardization/restriction/capacity_building), sectors, scs_pillars (Materials/Knowledge/Technology/Finance/Logistics), mechanisms, controls, evidence_refs, confidence.

---

## 3) Quote Capture (verbatim with cites)
> Extract **3–10 quotes**, <=300 chars each, with page number and a short relevance tag (e.g., MCF emphasis, export control, standards roadmap). Output TSV rows: source_id, page, quote, context, relevance, sectors, scs_pillars.

---

## 4) Specificity to 7C (policy alignment)
> Tell me how this document changes our **7C Specificity** for sectors: Does it anchor a sector policy? Indicate a concrete **mechanism** (e.g., JV incentives, standards push)? Or define a **control** (e.g., export license rules)? Return a table of sector → specificity contribution (0–5) with 1‑line justification.

---

## 5) Controls to Phase 6 (risk mitigations)
> Translate the identified controls into **Phase‑6** mitigations. For each control, provide: control name, target risk vector, sector, SCS pillar, implementation burden (low/med/high), and a one‑line "how to apply" in an SME or university.

---

## 6) SCS Levers Map (Phase 2S)
> Based on the claims, map each assertion to one or more **SCS pillars** (Materials/Knowledge/Technology/Finance/Logistics). For each pillar, list: named entities (if any), the likely path of leverage (e.g., logistics corridor, financing route), and 1 confidence note.

---

## 7) Contradiction & Tension Finder
> Compare this document's claims with previously captured `policy_assertions.tsv` excerpts I paste. List "Potential Contradictions" and "Resolution Ideas" (who is authoritative, which one is newer, how to safely phrase the uncertainty in our reports).

---

## 8) One‑Pager Policy Brief
> Generate a 1‑page brief with: (a) 5 bullets of what matters, (b) 3 mechanisms and 3 controls with sectors/SCS pillars, (c) a 6‑row table of sector → specificity (0–5) with one‑line justification, (d) 3 recommended tripwires we can track from our processed tables.

---

## Source Credibility Rubric (attach when using prompts)
- **5**: Primary law/regulation or official enforcement notice.  
- **4**: Official policy/strategy/ministerial circular.  
- **3**: Para‑official/national think tank aligned with government.  
- **2**: Independent think tank / academic.  
- **1**: Media/blog/advocacy.

## Notes for the solo analyst
- Do **one pass** per document unless it's on your watchlist; attach the TSV rows and move on.  
- Keep **confidence low** when you don't have strong cites.  
- Prefer **short quotes** with page numbers over paraphrase.  
- Use the watchlist to decide what to re‑check **quarterly/annually**.