# Language and Tone Standards

**Version:** 1.0
**Date:** 2025-11-02
**Status:** MANDATORY - All Project Documentation

---

## Overview

All analysis, documentation, and reporting in the OSINT Foresight project must maintain **neutral, professional language**. This standard is aligned with our Zero Fabrication Protocol and Intelligence Community tradecraft standards.

---

## Core Principles

### 1. NO EDITORIALIZING
**Present facts without emotional commentary**

❌ BAD: "This crisis reveals China's aggressive strategy"
✅ GOOD: "Events increased 89% during this period"

### 2. NO SENSATIONALIZING
**Avoid dramatic language**

Prohibited terms:
- "Crisis begins", "Crisis erupts"
- "Smoking gun", "Bombshell finding"
- "Explosive revelations"
- "Shocking discovery"
- "Devastating impact"
- "Alarming trends"

### 3. USE NEUTRAL TERMS

**Approved ✅ vs. Prohibited ❌ Terminology:**

| Context | ✅ Use This | ❌ Not This |
|---------|------------|-------------|
| Analysis type | Event analysis | Crisis analysis |
| Time periods | Peak activity month | Peak crisis month |
| Economic events | Economic measures | Economic coercion |
| Relationship status | Relationship strengthening/weakening | Relationship deterioration/collapse |
| Partnership status | Partnership expanded/reduced | Partnership deteriorated/flourished |
| Trade changes | Trade volumes increased/decreased | Trade collapsed/boomed |
| Event increases | Events increased | Crisis erupted |
| Significant patterns | Notable patterns | Alarming trends |
| Cooperation levels | Cooperation increased/decreased | Cooperation shattered/thrived |
| Engagement | Engagement expanded/contracted | Engagement severed/blossomed |

### 4. DIRECTIONAL LANGUAGE - ACCEPTABLE NEUTRAL TERMS

**You CAN indicate direction using factual, neutral terms:**

**For Strengthening/Positive Direction:**
- ✅ "Relationship strengthening" (observable increase in cooperation events)
- ✅ "Partnership expanded" (measurable increase in activities)
- ✅ "Cooperation increased" (higher event counts)
- ✅ "Engagement deepened" (more frequent interactions)
- ✅ "Ties strengthened" (increase in bilateral activities)

**For Weakening/Negative Direction:**
- ✅ "Relationship weakening" (observable decrease in cooperation events)
- ✅ "Partnership reduced" (measurable decrease in activities)
- ✅ "Cooperation decreased" (lower event counts)
- ✅ "Engagement contracted" (less frequent interactions)
- ✅ "Ties reduced" (decrease in bilateral activities)

**AVOID Emotional Directional Terms:**
- ❌ "Relationship collapsed/shattered/destroyed" → Use "weakened significantly" or "decreased [X]%"
- ❌ "Partnership flourished/blossomed/thrived" → Use "expanded" or "increased [X]%"
- ❌ "Ties severed/broken/ruptured" → Use "reduced" or "minimal activity observed"
- ❌ "Cooperation evaporated/vanished" → Use "decreased to minimal levels"

**Key Principle:** Pair direction with measurement when possible
- ✅ "Cooperation decreased 89.3%" (direction + measurement)
- ✅ "Partnership expanded with 47 new joint projects" (direction + evidence)
- ✅ "Engagement contracted from 1,209 to 129 events" (direction + specific data)

---

## Examples of Compliant Language

### ✅ CORRECT - Neutral, Factual

**Research Collaboration:**
- "Research collaboration decreased 89.3% in 2021"
- "Partnership contracted from 1,209 works in 2020 to 129 works in 2021"
- "Academic cooperation weakened significantly during this period"
- "This represents a reduction of 1,080 works"

**GDELT Events:**
- "GDELT recorded 707 relationship-weakening events in December 2021"
- "Event codes 161 (reduce diplomatic relations) increased during this period"
- "Total bilateral activity peaked at 1,338 events in December 2021"
- "Diplomatic engagement contracted following the November announcement"

**Trade Data:**
- "Trade volumes decreased 45% in Q1 2022"
- "Import/export levels weakened during this period"
- "Bilateral trade contracted from $X to $Y"
- "Commercial engagement decreased during the measured interval"

**Economic Measures:**
- "Code 191 (impose blockade) was recorded on December 31, 2021"
- "Economic measures events increased to 102 during the period"
- "Sanction-related event codes increased in Q4 2021"
- "Economic cooperation decreased as measured by event frequency"

**Relationship Direction:**
- "Lithuania-China relationship weakening observed in GDELT data"
- "Cooperation indicators decreased across multiple categories"
- "Engagement contracted following policy changes"
- "Bilateral ties reduced from 2021 peak levels"

### ❌ INCORRECT - Emotional, Sensationalized

**Research Collaboration:**
- ❌ "Research collaboration COLLAPSED in devastating blow"
- ❌ "Academic ties SEVERED as crisis exploded"
- ❌ "Shocking 89% drop reveals China's brutal retaliation"

**GDELT Events:**
- ❌ "Crisis ERUPTS with 707 hostile actions"
- ❌ "Smoking gun: China BREAKS relations in explosive December"
- ❌ "Alarming spike shows relationship in freefall"

**Trade Data:**
- ❌ "Trade COLLAPSES in economic warfare"
- ❌ "Devastating blockade CRIPPLES Lithuania"
- ❌ "China's BRUTAL economic assault revealed"

**Economic Measures:**
- ❌ "Bombshell: China WEAPONIZES trade"
- ❌ "Shocking blockade proves China's aggressive tactics"
- ❌ "Economic coercion ESCALATES in coordinated attack"

---

## Principle: Let the Data Speak

**Good analysis presents facts and lets readers draw conclusions.**

### Example: Neutral Presentation

```
Lithuania-China Research Collaboration (2020-2021)

Data Source: OpenAlex research database
Measurement: Co-authored publications by year

2020: 1,209 works
2021: 129 works
Change: -1,080 works (-89.3%)

Context: Taiwan representative office opened in Vilnius (November 2021)
China downgraded diplomatic relations (December 2021)

Observation: This represents the largest single-year decrease in the
20-year dataset (2000-2024).
```

This presentation:
- ✅ States facts with precision
- ✅ Provides context without interpretation
- ✅ Uses neutral language throughout
- ✅ Allows readers to form their own conclusions

### Bad Example: Editorialized Presentation

```
❌ Lithuania-Taiwan Crisis DEVASTATES Academic Ties

In a SHOCKING blow to academic freedom, China's BRUTAL retaliation
against Lithuania COLLAPSED research collaboration by a DEVASTATING 89%.

This ALARMING drop from 1,209 to just 129 works reveals China's
WEAPONIZATION of academic partnerships as PUNISHMENT for Lithuania's
BRAVE stance on Taiwan.

The EXPLOSIVE December crisis saw China SEVER ties in what experts
call the most AGGRESSIVE act of academic COERCION in modern history.
```

This presentation:
- ❌ Uses emotional language
- ❌ Editorializes intent ("punishment", "brave", "coercion")
- ❌ Sensationalizes events ("devastating", "brutal", "explosive")
- ❌ Interprets rather than reports

---

## Application Areas

### 1. Script Documentation
All Python script docstrings must use neutral language.

```python
# ✅ GOOD
"""
GDELT Lithuania-China Event Analysis
Analyzes bilateral events during 2021-2022 period.
Focuses on temporal patterns and event type distribution.
"""

# ❌ BAD
"""
GDELT Lithuania-China CRISIS Analysis
Exposes China's BRUTAL coercion during Taiwan office CRISIS.
Reveals SHOCKING evidence of economic WARFARE.
"""
```

### 2. Analysis Reports
All markdown reports must present findings neutrally.

```markdown
# ✅ GOOD
## Key Findings
- Trade volume decreased 45% in Q1 2022
- GDELT recorded 707 deterioration events in December 2021
- Research collaboration decreased 89.3% in 2021

# ❌ BAD
## SHOCKING Discoveries
- Trade COLLAPSED by devastating 45%
- EXPLOSIVE 707 hostile actions in crisis month
- Academic ties SEVERED in brutal retaliation
```

### 3. README and Documentation
All project documentation must maintain professional tone.

### 4. Data Visualization Labels
Chart titles, axis labels, and annotations must be neutral.

```
# ✅ GOOD
"Lithuania-China Trade Volume (2020-2023)"
"Event Count by Month"
"Research Collaboration Trends"

# ❌ BAD
"Trade Collapse During Crisis"
"Spike in Hostile Actions"
"Academic Ties Severed"
```

### 5. Variable and Function Names
Code should use neutral terminology.

```python
# ✅ GOOD
economic_events = get_economic_measures()
peak_month = find_maximum_activity()
relationship_changes = analyze_bilateral_events()

# ❌ BAD
coercion_events = get_brutal_attacks()
crisis_peak = find_explosion_point()
relationship_collapse = analyze_hostile_acts()
```

---

## Enforcement

### Pre-Publication Checklist

Before committing analysis or documentation:

- [ ] Remove all emotional adjectives (shocking, brutal, devastating, alarming)
- [ ] Replace sensational terms with neutral equivalents (use substitution table above)
- [ ] Check that claims are presented as data observations, not interpretations
- [ ] Verify that context is provided without editorializing
- [ ] Ensure readers can draw their own conclusions

### Review Process

All analysis undergoes tone review:

1. **Self-Review:** Author checks against this guide
2. **Peer Review:** Second reviewer verifies neutral language
3. **Final Check:** Compare against examples in this document

### Incident Tracking

Violations are tracked in `docs/LANGUAGE_TONE_VIOLATIONS.md` (similar to Zero Fabrication Protocol incidents).

---

## Related Standards

This standard complements:

- **[Zero Fabrication Protocol](docs/ZERO_FABRICATION_PROTOCOL.md)** - No fabrication of data
- **Language and Tone Standards** (this document) - No editorialization of presentation
- **[Verification Checklist](docs/ZERO_FABRICATION_VERIFICATION_CHECKLIST.md)** - Pre-publication requirements

Together these ensure:
- Data integrity (Zero Fabrication)
- Presentation objectivity (Language Standards)
- Complete verification (Checklist)

---

## Quick Reference Card

**Remember:**
1. Present data, not opinions
2. Measure changes, don't interpret motives
3. Use neutral verbs (increased, decreased, changed)
4. Avoid emotional adjectives (brutal, shocking, alarming)
5. **USE directional language** (strengthening/weakening, expanded/contracted, increased/decreased)
6. **AVOID dramatic direction** (collapsed, shattered, flourished, thrived)
7. Let readers draw conclusions

**Directional Language Quick Guide:**
- ✅ "Relationship weakening" / ❌ "Relationship collapsed"
- ✅ "Partnership expanded" / ❌ "Partnership flourished"
- ✅ "Cooperation decreased 89%" / ❌ "Cooperation evaporated"
- ✅ "Engagement contracted" / ❌ "Ties severed"

**When in doubt, ask:**
- "Am I stating a fact or an opinion?"
- "Would this language appear in a scientific paper?"
- "Could I defend this wording to a peer reviewer?"
- "Does my directional term include measurement or evidence?"

---

**Status:** ✅ ACTIVE
**Compliance:** MANDATORY
**Version:** 1.0
**Last Updated:** 2025-11-02
