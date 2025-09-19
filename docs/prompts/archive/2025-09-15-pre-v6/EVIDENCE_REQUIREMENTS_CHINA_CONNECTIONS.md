# Evidence Requirements for China Connection Claims

## Fundamental Rule

**No speculation without evidence. Period.**

Every claim about China connections must be:
- **Verifiable**: Can be independently checked
- **Specific**: Names, dates, amounts, locations
- **Sourced**: Document reference with page/section
- **Current**: Dated within reasonable timeframe
- **Proportional**: Claim matches evidence strength

## Evidence Hierarchy

### Tier 1: Direct Evidence (Highest Value)
- Official company filings (annual reports, SEC filings)
- Government documents (CFIUS reports, EU screening decisions)
- Contracts and agreements (when publicly available)
- Court documents and legal filings
- Official press releases from named entities

### Tier 2: Authoritative Reporting
- Major news outlets with named sources
- Think tank reports with methodology
- Academic papers with peer review
- Industry reports from recognized firms
- Government-funded research studies

### Tier 3: Indirect Evidence (Use Cautiously)
- LinkedIn profiles and employment data
- Conference attendance lists
- Patent filings and citations
- Trade show exhibitions
- Social media from official accounts

### Tier 4: Circumstantial (Not Sufficient Alone)
- Timing correlations
- Technical similarities
- Personnel movements
- Capability developments

## Required Evidence Format

### For Each China Connection Claim:

```json
{
  "claim": "[Specific assertion]",
  "confidence_level": "HIGH|MEDIUM|LOW",
  "evidence_tier": "1|2|3|4",
  "evidence": {
    "primary_source": {
      "type": "annual_report|news|paper|patent|etc",
      "title": "Full document title",
      "author": "Organization or individual",
      "date": "YYYY-MM-DD",
      "url": "Direct link to document",
      "page": "Specific page or section",
      "quote": "Exact quote supporting claim",
      "accessed": "YYYY-MM-DD"
    },
    "corroborating_sources": [
      {
        "type": "",
        "title": "",
        "url": "",
        "relevance": "How this supports primary source"
      }
    ]
  },
  "limitations": [
    "What this evidence does NOT prove",
    "Alternative explanations possible"
  ],
  "exploitation_pathway": {
    "mechanism": "How China could exploit this connection",
    "probability": "Assessment based on evidence",
    "timeline": "Immediate|Near-term|Long-term"
  }
}
```

## Examples of Good vs Bad Evidence

### ❌ BAD: Speculation Without Evidence

**Claim**: "Leonardo probably has extensive China operations"
**Problem**: No evidence, uses "probably"
**Fix**: Search for specific evidence of Leonardo China operations

**Claim**: "Any Chinese investment in Italian tech compromises US security"
**Problem**: Too broad, no specific pathway
**Fix**: Identify specific investment, technology, and transfer mechanism

### ✅ GOOD: Evidence-Based Claims

**Claim**: "Leonardo maintains Beijing representative office"
```json
{
  "evidence": {
    "primary_source": {
      "type": "annual_report",
      "title": "Leonardo Annual Report 2023",
      "date": "2024-03-15",
      "url": "https://leonardo.com/reports/2023",
      "page": "47",
      "quote": "Representative office in Beijing supporting civilian helicopter sales",
      "accessed": "2025-09-14"
    }
  },
  "limitations": ["Civilian focus stated, military involvement unknown"],
  "exploitation_pathway": {
    "mechanism": "Dual-use helicopter technology exposure",
    "probability": "MEDIUM - civilian tech has military applications",
    "timeline": "Long-term"
  }
}
```

### ✅ GOOD: Proportional Claims

**Claim**: "ChemChina acquired Pirelli, demonstrating Chinese interest in Italian industrial technology"
```json
{
  "evidence": {
    "primary_source": {
      "type": "news",
      "title": "ChemChina completes $7.9 billion acquisition of Pirelli",
      "author": "Financial Times",
      "date": "2015-10-06",
      "url": "https://www.ft.com/content/...",
      "quote": "ChemChina completes largest Chinese acquisition in Italy"
    }
  },
  "limitations": ["Single sector (tires), not indicative of all industries"],
  "exploitation_pathway": {
    "mechanism": "Technology transfer in materials and manufacturing",
    "probability": "HIGH - completed acquisition allows full access",
    "timeline": "Immediate"
  }
}
```

## Search Strategy for Evidence

### Phase 1: Direct Documentation
```
site:leonardo.com China OR Beijing OR Shanghai
site:sec.gov "Leonardo DRS" China
filetype:pdf "Leonardo" "China" annual report
```

### Phase 2: Government Records
```
site:cfius.gov Italy China technology
site:europa.eu "foreign direct investment" Italy China
site:mise.gov.it "golden power" China
```

### Phase 3: Authoritative Analysis
```
site:csis.org Italy China technology
site:merics.org Italy China investment
site:brookings.edu "Belt and Road" Italy
```

### Phase 4: Trade and Patent Data
```
site:patents.google.com assignee:Leonardo cited_by:country:CN
site:comtrade.un.org Italy China "high technology"
```

## Red Lines: What NOT to Claim

### Never Say Without Evidence:
- "Automatically compromises" - Nothing is automatic
- "Certainly" or "Definitely" - Unless 100% proven
- "All" or "Every" - Avoid absolutes
- "Secretly" or "Covertly" - If it's secret, how do you know?
- "Obviously" - If obvious, show the evidence

### Never Assume:
- Civilian cooperation means military involvement
- Chinese investment means technology transfer
- Presence means penetration
- Capability means intent
- Correlation means causation

## Quality Control Checklist

Before making any China connection claim, verify:

- [ ] Do I have at least Tier 2 evidence?
- [ ] Is my source less than 2 years old?
- [ ] Can someone verify this independently?
- [ ] Have I stated what I DON'T know?
- [ ] Is my claim proportional to evidence strength?
- [ ] Have I avoided speculation words?
- [ ] Have I provided the exact quote?
- [ ] Is the URL direct to the document?
- [ ] Have I noted access date?
- [ ] Have I described the exploitation pathway?

## Evidence Gaps to Track

When evidence is insufficient, document the gap:

```json
{
  "intelligence_gap": "[What we need to know]",
  "current_evidence": "[What we have]",
  "evidence_needed": "[What would answer the question]",
  "collection_actions": [
    "Specific search to conduct",
    "Document to obtain",
    "Database to check"
  ],
  "priority": "HIGH|MEDIUM|LOW",
  "estimated_effort": "Hours|Days|Weeks"
}
```

## The Bottom Line

**Better to say "Unknown - investigation needed" than to speculate.**

Every China connection claim should be defensible in court, briefable to leadership, and withstand scrutiny from skeptics. If you wouldn't bet your reputation on it, don't claim it.

Remember: Our adversaries read our assessments. Speculation without evidence undermines credibility and provides ammunition for dismissing legitimate concerns.

**Standard**: Would this evidence convince a skeptical decision-maker to take action?

If no, get better evidence or acknowledge the limitation.
