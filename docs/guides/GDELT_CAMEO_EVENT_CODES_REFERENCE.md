# GDELT CAMEO Event Codes - Complete Reference
## Conflict and Mediation Event Observations (CAMEO) Framework

**Purpose:** Identify which event codes are relevant for documenting China-Europe technology exploitation

**Current Focus:** Codes we're already using
**Review Needed:** Codes marked with ⭐ may be relevant to add

---

## Currently Used Event Codes

These are the codes we're currently querying in GDELT:

| Code | Event Type | Usage | Intelligence Value |
|------|------------|-------|-------------------|
| **030** | Express intent to cooperate | ✅ Using | Early warning of agreements |
| **040** | Consult | ✅ Using | Diplomatic consultations |
| **042** | Make a visit | ✅ Using | Official visits timeline |
| **043** | Engage in diplomatic cooperation | ✅ Using | Active cooperation |
| **045** | Engage in material cooperation | ✅ Using | Infrastructure projects |
| **046** | Receive material cooperation | ✅ Using | Infrastructure/investment received |
| **051** | Cooperate economically | ✅ Using | Trade/investment events |
| **061** | Cooperate on science/technology | ✅ Using | **CRITICAL** - Technology transfer |
| **075** | Sign formal agreement | ✅ Using | **HIGHEST VALUE** - Legal commitments |
| **111** | Praise or endorse | ✅ Using (multilateral only) | Diplomatic alignment |
| **120** | Reject | ✅ Using (multilateral only) | Policy conflicts |
| **130** | Threaten | ✅ Using (multilateral only) | Coercive diplomacy |
| **140** | Protest | ✅ Using (multilateral only) | Diplomatic tensions |

---

## Complete CAMEO Event Code Taxonomy

### QUAD CLASS 01: MAKE PUBLIC STATEMENT

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 010 | Make statement, not specified below | ⭐ Maybe | General announcements |
| 011 | Decline comment | ❌ No | Not actionable |
| 012 | Make pessimistic comment | ❌ No | Sentiment, not events |
| 013 | Make optimistic comment | ❌ No | Sentiment, not events |
| 014 | Consider policy option | ⭐ **YES** | **Pre-agreement signals** |
| 015 | Acknowledge or claim responsibility | ❌ No | Post-event only |
| 016 | Deny responsibility | ❌ No | Not relevant |
| 017 | Engage in symbolic act | ⭐ Maybe | Ceremonial events (flag raising, etc.) |
| 018 | Make empathetic comment | ❌ No | Sentiment only |
| 019 | Express accord | ⭐ Maybe | Agreement in principle |

**RECOMMENDATION:** Add **014** (Consider policy option) - captures pre-agreement deliberations

---

### QUAD CLASS 02: APPEAL

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 020 | Make an appeal or request, not specified | ❌ No | Too vague |
| 021 | Appeal for material cooperation | ⭐ **YES** | **Requests for aid/investment** |
| 0211 | Appeal for economic cooperation | ⭐ **YES** | **Trade deal requests** |
| 0212 | Appeal for military cooperation | ⭐ **YES** | **Defense cooperation requests** |
| 0213 | Appeal for humanitarian cooperation | ❌ No | Not our focus |
| 0214 | Appeal for military aid | ⭐ **YES** | **Defense technology transfer** |
| 022 | Appeal for diplomatic cooperation | ⭐ Maybe | Diplomatic outreach |
| 023 | Appeal for aid | ⭐ **YES** | **Investment/funding requests** |
| 0231 | Appeal for economic aid | ⭐ **YES** | **BRI funding requests** |
| 0232 | Appeal for military aid | ⭐ **YES** | **Defense aid requests** |
| 0233 | Appeal for humanitarian aid | ❌ No | Not our focus |
| 0234 | Appeal for technical or material aid | ⭐ **YES** | **CRITICAL - Technology aid requests** |
| 024 | Appeal for political reform | ❌ No | Domestic politics |
| 025 | Appeal to yield | ❌ No | Coercive, not cooperative |
| 026 | Appeal to others to meet or negotiate | ⭐ Maybe | Pre-negotiation signals |
| 027 | Appeal to others to settle dispute | ❌ No | Conflict resolution |
| 028 | Appeal to engage in or accept mediation | ❌ No | Conflict resolution |

**RECOMMENDATION:** Add **021, 0211, 0212, 0214, 023, 0231, 0234** - These capture requests that precede formal agreements

---

### QUAD CLASS 03: EXPRESS INTENT TO COOPERATE

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 030 | Express intent to cooperate, not specified | ✅ **USING** | Already tracked |
| 031 | Express intent to engage in material cooperation | ✅ **USING** | Already tracked (should add explicitly) |
| 0311 | Express intent to cooperate economically | ⭐ **YES** | **Pre-economic agreement** |
| 0312 | Express intent to cooperate militarily | ⭐ **YES** | **Defense cooperation intent** |
| 0313 | Express intent to cooperate on intelligence | ⭐ **YES** | **Intelligence sharing intent** |
| 0314 | Express intent to cooperate on judiciary/law enforcement | ❌ No | Not our focus |
| 032 | Express intent to provide material aid | ⭐ **YES** | **Aid/investment promises** |
| 033 | Express intent to engage in diplomatic cooperation | ⭐ Maybe | Diplomatic signals |
| 034 | Express intent to provide military aid | ⭐ **YES** | **Defense aid promises** |
| 035 | Express intent to provide economic aid | ⭐ **YES** | **BRI funding promises** |
| 036 | Express intent to meet or negotiate | ✅ **USING** | Already tracked |
| 037 | Express intent to settle dispute | ❌ No | Conflict resolution |
| 038 | Express intent to accept mediation | ❌ No | Conflict resolution |
| 039 | Express intent to mediate | ❌ No | Conflict resolution |

**RECOMMENDATION:** Add **0311, 0312, 0313, 032, 034, 035** - Intent signals before formal actions

---

### QUAD CLASS 04: CONSULT

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 040 | Consult, not specified | ✅ **USING** | Already tracked |
| 041 | Discuss by telephone | ❌ No | Method not important |
| 042 | Make a visit | ✅ **USING** | Already tracked |
| 043 | Host a visit | ⭐ **YES** | **Receiving delegations** |
| 044 | Meet at a 'third' location | ⭐ **YES** | **Neutral ground summits** |
| 045 | Mediate | ❌ No | Conflict resolution |
| 046 | Engage in negotiation | ⭐ **YES** | **Active negotiations** |

**RECOMMENDATION:** Add **043, 044, 046** - Meeting/negotiation details

---

### QUAD CLASS 05: ENGAGE IN DIPLOMATIC COOPERATION

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 050 | Engage in diplomatic cooperation, not specified | ✅ **USING** | Already tracked |
| 051 | Praise or endorse | ✅ **USING** | Already tracked |
| 052 | Defend verbally | ❌ No | Reactive statement |
| 053 | Rally support on behalf of | ⭐ Maybe | Coalition building |
| 054 | Grant diplomatic recognition | ⭐ **YES** | **Official recognition events** |
| 055 | Apologize | ❌ No | Reactive only |
| 056 | Forgive | ❌ No | Not relevant |
| 057 | Sign formal agreement | ✅ **USING** | **Already tracked (Code 075 duplicate?)** |

**NOTE:** Code 057 appears to be same as 075 - verify which is correct

**RECOMMENDATION:** Add **054** (Diplomatic recognition) - important for Kosovo, Taiwan issues

---

### QUAD CLASS 06: ENGAGE IN MATERIAL COOPERATION

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 060 | Cooperate, not specified | ⭐ Maybe | General cooperation catch-all |
| 061 | Cooperate economically | ✅ **USING** | **Already tracked (should be 051?)** |
| 062 | Cooperate militarily | ⭐ **YES** | **Defense cooperation events** |
| 063 | Engage in judicial cooperation | ❌ No | Not our focus |
| 064 | Share intelligence or information | ⭐ **YES** | **Intelligence sharing events** |

**NOTE:** Code confusion - we're using 061 for "science/technology cooperation" but CAMEO lists it as "cooperate economically"
**CRITICAL:** Verify CAMEO version being used by GDELT

**RECOMMENDATION:** Add **062, 064** - Defense and intelligence cooperation

---

### QUAD CLASS 07: PROVIDE AID

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 070 | Provide aid, not specified | ⭐ **YES** | **General aid provision** |
| 071 | Provide economic aid | ⭐ **YES** | **BRI funding, grants** |
| 072 | Provide military aid | ⭐ **YES** | **Defense aid, equipment** |
| 073 | Provide humanitarian aid | ❌ No | Not our focus |
| 074 | Provide military protection or peacekeeping | ❌ No | Security operations |
| 075 | Grant asylum | ❌ No | Not relevant |

**NOTE:** Code 075 listed here as "Grant asylum" but we're using it for "Sign formal agreement" - VERIFY CAMEO version

**RECOMMENDATION:** Add **070, 071, 072** - Aid provision is critical for BRI tracking

---

### QUAD CLASS 08: YIELD

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 080 | Yield, not specified | ❌ No | Capitulation events |
| 081 | Ease administrative sanctions | ⭐ **YES** | **Sanctions relief** |
| 0811 | Ease political dissent | ❌ No | Domestic politics |
| 0812 | Ease restrictions on political freedoms | ❌ No | Domestic politics |
| 0813 | Ease ban on political parties or politicians | ❌ No | Domestic politics |
| 0814 | Ease curfew | ❌ No | Security operations |
| 0815 | Ease state of emergency or martial law | ❌ No | Security operations |
| 082 | Ease economic sanctions, boycott, or embargo | ⭐ **YES** | **CRITICAL - Trade restrictions** |
| 083 | Ease popular dissent | ❌ No | Domestic politics |
| 084 | Return, release persons or property | ⭐ Maybe | Prisoner exchanges, asset returns |
| 0841 | Return, release person(s) | ⭐ Maybe | Prisoner/detainee releases |
| 0842 | Return, release property | ⭐ Maybe | Asset seizure reversals |
| 085 | Ease military blockade | ❌ No | Military operations |
| 086 | Ease military occupation | ❌ No | Military operations |
| 087 | Retreat or surrender militarily | ❌ No | Military operations |

**RECOMMENDATION:** Add **081, 082** - Sanctions/restrictions relief is critical for tracking policy changes

---

### QUAD CLASS 09: INVESTIGATE

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 090 | Investigate, not specified | ⭐ **YES** | **Investigations into entities** |
| 091 | Investigate crime, corruption | ⭐ **YES** | **Corporate/official investigations** |
| 092 | Investigate human rights abuses | ❌ No | Not our primary focus |
| 093 | Investigate military action | ❌ No | Military focus |
| 094 | Investigate war crimes | ❌ No | War crimes focus |

**RECOMMENDATION:** Add **090, 091** - Corporate investigations (Huawei 5G bans, etc.)

---

### QUAD CLASS 10: DEMAND

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 100 | Demand, not specified | ⭐ Maybe | General demands |
| 101 | Demand information, investigation | ⭐ Maybe | Transparency demands |
| 102 | Demand policy support | ⭐ Maybe | Policy alignment demands |
| 103 | Demand aid, protection, or peacekeeping | ❌ No | Aid requests |
| 104 | Demand political reform | ❌ No | Domestic politics |
| 105 | Demand change in leadership | ❌ No | Regime change |
| 106 | Demand policy change | ⭐ **YES** | **Policy change demands (5G bans, etc.)** |
| 107 | Demand that target yields | ❌ No | Coercive |
| 108 | Demand de-escalation of military engagement | ❌ No | Military focus |

**RECOMMENDATION:** Add **106** - Policy demands (e.g., "EU demands China change Xinjiang policy")

---

### QUAD CLASS 11: DISAPPROVE

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 110 | Disapprove, not specified | ⭐ Maybe | General disapproval |
| 111 | Criticize or denounce | ⭐ **YES** | **Public criticism events** |
| 112 | Accuse, not specified | ⭐ **YES** | **Accusations (IP theft, espionage)** |
| 1121 | Accuse of crime, corruption | ⭐ **YES** | **Corporate crime accusations** |
| 1122 | Accuse of human rights abuses | ⭐ Maybe | HR accusations |
| 1123 | Accuse of aggression | ⭐ Maybe | Territorial disputes |
| 1124 | Accuse of war crimes | ❌ No | War crimes |
| 1125 | Accuse of espionage, treason | ⭐ **YES** | **CRITICAL - Spy accusations** |
| 113 | Rally opposition against | ⭐ Maybe | Coalition building |
| 114 | Complain officially | ⭐ **YES** | **Official complaints (WTO, etc.)** |
| 115 | Bring lawsuit against | ⭐ **YES** | **CRITICAL - Legal actions** |
| 116 | Find guilty or liable (legally) | ⭐ **YES** | **CRITICAL - Court verdicts** |

**RECOMMENDATION:** Add **111, 112, 1121, 1125, 114, 115, 116** - Conflicts, accusations, legal actions

---

### QUAD CLASS 12: REJECT

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 120 | Reject, not specified | ✅ **USING** | Already tracked |
| 121 | Reject proposal to meet, discuss, or negotiate | ⭐ **YES** | **Negotiation breakdowns** |
| 122 | Reject material cooperation | ⭐ **YES** | **Rejected agreements/partnerships** |
| 1221 | Reject economic cooperation | ⭐ **YES** | **Trade deal rejections** |
| 1222 | Reject military cooperation | ⭐ **YES** | **Defense partnership rejections** |
| 1223 | Reject judicial cooperation | ❌ No | Legal cooperation |
| 1224 | Reject intelligence cooperation | ⭐ **YES** | **Intel sharing rejections** |
| 123 | Reject request or demand for material aid | ⭐ Maybe | Aid rejections |
| 124 | Reject request or demand for political reform | ❌ No | Domestic politics |
| 125 | Reject request or demand to change leadership | ❌ No | Regime change |
| 126 | Reject request or demand for policy change | ⭐ **YES** | **Policy demand rejections** |
| 127 | Reject request or demand to de-escalate military operations | ❌ No | Military operations |

**RECOMMENDATION:** Add **121, 122, 1221, 1222, 1224, 126** - Rejection events show failed negotiations

---

### QUAD CLASS 13: THREATEN

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 130 | Threaten, not specified | ✅ **USING** | Already tracked |
| 131 | Threaten non-force specified below | ⭐ Maybe | General threats |
| 1311 | Threaten to reduce or stop aid | ⭐ **YES** | **Aid/investment threats** |
| 1312 | Threaten to boycott, embargo, or sanction | ⭐ **YES** | **CRITICAL - Trade war threats** |
| 1313 | Threaten to reduce or break relations | ⭐ **YES** | **Diplomatic threat escalation** |
| 132 | Threaten with administrative sanctions | ⭐ **YES** | **Regulatory threats (5G bans)** |
| 133 | Threaten with political dissent, protest | ❌ No | Domestic politics |
| 134 | Threaten with restrictions on political freedoms | ❌ No | Domestic politics |
| 135 | Threaten with economic sanctions, boycott, or embargo | ⭐ **YES** | **CRITICAL - Sanctions threats** |
| 136 | Threaten with military force | ❌ No | Military threats |
| 137 | Threaten with occupation | ❌ No | Military occupation |
| 138 | Threaten unconventional violence | ❌ No | Terrorism/unconventional |

**RECOMMENDATION:** Add **1311, 1312, 1313, 132, 135** - Coercive economic diplomacy

---

### QUAD CLASS 14: PROTEST

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 140 | Engage in political dissent, not specified | ✅ **USING** | Already tracked |
| 141 | Demonstrate or rally | ⭐ Maybe | Public protests |
| 1411 | Demonstrate for leadership change | ❌ No | Regime change |
| 1412 | Demonstrate for policy change | ⭐ Maybe | Policy protests |
| 1413 | Demonstrate for rights | ⭐ Maybe | HR protests |
| 1414 | Demonstrate for change in institutions, regime | ❌ No | System change |
| 142 | Conduct hunger strike | ❌ No | Extreme protest |
| 143 | Conduct strike or boycott | ⭐ **YES** | **Economic boycotts** |
| 1431 | Conduct strike or boycott for leadership change | ❌ No | Political strikes |
| 1432 | Conduct strike or boycott for policy change | ⭐ **YES** | **Policy boycotts** |
| 1433 | Conduct strike or boycott for rights | ❌ No | Rights strikes |
| 1434 | Conduct strike or boycott for change in institutions, regime | ❌ No | System change |
| 144 | Obstruct passage, block | ⭐ Maybe | Physical obstruction |
| 1441 | Obstruct passage to demand leadership change | ❌ No | Political blockades |
| 1442 | Obstruct passage to demand policy change | ⭐ Maybe | Policy blockades |
| 1443 | Obstruct passage to demand rights | ❌ No | Rights blockades |
| 1444 | Obstruct passage to demand change in institutions, regime | ❌ No | System change |
| 145 | Protest violently, riot | ❌ No | Violence |

**RECOMMENDATION:** Add **143, 1432** - Economic boycotts (consumer boycotts of Chinese goods, etc.)

---

### QUAD CLASS 15: EXHIBIT MILITARY POSTURE

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 150-159 | Various military posture codes | ❌ No | Military focus, not our mission |

**SKIP** - Military posture not relevant to technology exploitation analysis

---

### QUAD CLASS 16: REDUCE RELATIONS

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 160 | Reduce relations, not specified | ⭐ **YES** | **Relationship deterioration** |
| 161 | Reduce or break diplomatic relations | ⭐ **YES** | **CRITICAL - Diplomatic breaks** |
| 162 | Reduce or stop material aid | ⭐ **YES** | **Aid/investment cuts** |
| 1621 | Reduce or stop economic assistance | ⭐ **YES** | **Economic aid cuts** |
| 1622 | Reduce or stop military assistance | ⭐ **YES** | **Defense aid cuts** |
| 1623 | Reduce or stop humanitarian assistance | ❌ No | Humanitarian focus |
| 163 | Halt negotiations | ⭐ **YES** | **Negotiation failures** |
| 164 | Expel or withdraw | ⭐ **YES** | **CRITICAL - Expulsions** |
| 1641 | Expel or withdraw peacekeepers | ❌ No | Peacekeeping |
| 1642 | Expel or withdraw inspectors, observers | ⭐ Maybe | Monitoring expulsions |
| 1643 | Expel or withdraw aid agencies | ❌ No | Aid focus |
| 165 | Halt mediation | ❌ No | Conflict resolution |
| 166 | Expel or deport individuals | ⭐ **YES** | **Diplomat/spy expulsions** |

**RECOMMENDATION:** Add **160, 161, 162, 1621, 1622, 163, 164, 166** - Relationship deterioration events

---

### QUAD CLASS 17: COERCE

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 170 | Coerce, not specified | ⭐ Maybe | General coercion |
| 171 | Seize or damage property | ⭐ **YES** | **Asset seizures** |
| 1711 | Confiscate property | ⭐ **YES** | **CRITICAL - Asset confiscations** |
| 1712 | Destroy property | ❌ No | Destruction events |
| 172 | Impose administrative sanctions | ⭐ **YES** | **CRITICAL - Regulatory sanctions** |
| 1721 | Impose restrictions on political freedoms | ❌ No | Domestic politics |
| 1722 | Ban political parties or politicians | ❌ No | Domestic politics |
| 1723 | Impose curfew | ❌ No | Security operations |
| 1724 | Impose state of emergency or martial law | ❌ No | Security operations |
| 173 | Arrest, detain, or charge with legal action | ⭐ **YES** | **Corporate arrests** |
| 1731 | Arrest, detain | ⭐ **YES** | **Detention events** |
| 1732 | Charge with crime | ⭐ **YES** | **Criminal charges** |
| 174 | Impose economic sanctions, boycott, or embargo | ⭐ **YES** | **CRITICAL - Sanctions imposed** |
| 175 | Use violent repression | ❌ No | Violence |

**RECOMMENDATION:** Add **171, 1711, 172, 173, 1731, 1732, 174** - Coercive actions (Huawei CFO arrest, etc.)

---

### QUAD CLASS 18: ASSAULT

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 180-186 | Various assault/attack codes | ❌ No | Violence, not our focus |

**SKIP** - Violence not relevant to technology exploitation analysis

---

### QUAD CLASS 19: FIGHT

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 190-196 | Various fighting/combat codes | ❌ No | Military combat, not our focus |

**SKIP** - Military combat not relevant

---

### QUAD CLASS 20: ENGAGE IN UNCONVENTIONAL MASS VIOLENCE

| Code | Event Type | Relevant? | Notes |
|------|------------|-----------|-------|
| 200-206 | Various mass violence codes | ❌ No | Terrorism/WMD, not our focus |

**SKIP** - Unconventional violence not relevant

---

## RECOMMENDED ADDITIONS TO QUERIES

### High Priority (Add Immediately)

**Intent/Planning Phase:**
- **014** - Consider policy option (pre-agreement signals)
- **0311** - Express intent to cooperate economically
- **0312** - Express intent to cooperate militarily
- **032** - Express intent to provide material aid
- **046** - Engage in negotiation (active negotiations)

**Aid/Investment:**
- **070** - Provide aid (general)
- **071** - Provide economic aid (BRI funding)
- **072** - Provide military aid (defense aid)
- **0234** - Appeal for technical or material aid

**Policy Actions:**
- **081** - Ease administrative sanctions (sanctions relief)
- **082** - Ease economic sanctions (trade restrictions lifted)
- **106** - Demand policy change (5G ban demands, etc.)

**Conflicts/Accusations:**
- **111** - Criticize or denounce (public criticism)
- **112** - Accuse (general accusations)
- **1125** - Accuse of espionage (spy accusations)
- **115** - Bring lawsuit against (legal actions)
- **116** - Find guilty or liable (court verdicts)

**Coercive Actions:**
- **172** - Impose administrative sanctions (regulatory actions)
- **174** - Impose economic sanctions (sanctions imposed)
- **1711** - Confiscate property (asset seizures)
- **173** - Arrest/detain/charge (Huawei CFO, etc.)

**Relationship Changes:**
- **160** - Reduce relations (deterioration)
- **161** - Reduce/break diplomatic relations (breaks)
- **162** - Reduce/stop material aid (aid cuts)
- **163** - Halt negotiations (negotiation failures)
- **164** - Expel or withdraw (expulsions)
- **166** - Expel/deport individuals (diplomat expulsions)

**Threats:**
- **1311** - Threaten to reduce/stop aid
- **1312** - Threaten to boycott/embargo/sanction
- **1313** - Threaten to reduce/break relations
- **135** - Threaten with economic sanctions

### Medium Priority (Add if valuable)

- **021** - Appeal for material cooperation
- **043** - Host a visit
- **044** - Meet at third location
- **054** - Grant diplomatic recognition
- **062** - Cooperate militarily
- **064** - Share intelligence/information
- **090/091** - Investigate crime/corruption
- **114** - Complain officially
- **121** - Reject proposal to meet
- **122** - Reject material cooperation
- **143** - Conduct strike or boycott

---

## Event Code Priority Matrix

### Tier 1: CRITICAL (Must Have)
These document legally binding commitments and technology transfer:

- **075** - Sign formal agreement ✅ USING
- **061** - Science/technology cooperation ✅ USING
- **071** - Provide economic aid (BRI)
- **072** - Provide military aid
- **0234** - Appeal for technical aid

### Tier 2: HIGH VALUE (Should Have)
These document policy changes and conflicts:

- **014** - Consider policy option
- **046** - Engage in negotiation
- **081/082** - Ease sanctions
- **106** - Demand policy change
- **111/112** - Criticize/Accuse
- **115/116** - Lawsuit/Verdict
- **172/174** - Impose sanctions
- **160-166** - Reduce relations

### Tier 3: CONTEXT (Nice to Have)
These provide timeline context:

- **042** - Make a visit ✅ USING
- **043/044** - Host visit/Meet
- **051** - Cooperate economically ✅ USING
- **062** - Cooperate militarily
- **090/091** - Investigate

### Tier 4: ALREADY USING
- **030, 040, 042, 043, 045, 046, 051, 061, 075** ✅
- **111, 120, 130, 140** ✅ (multilateral only)

---

## Critical Note on Code Confusion

**ISSUE DISCOVERED:** The CAMEO codes we're using don't match standard CAMEO taxonomy:

| Code | We Think It Means | CAMEO Says It Means | Resolution Needed |
|------|-------------------|---------------------|-------------------|
| **061** | Science/technology cooperation | Cooperate economically | **VERIFY GDELT VERSION** |
| **051** | Cooperate economically | Praise or endorse | **VERIFY GDELT VERSION** |
| **075** | Sign formal agreement | Grant asylum | **VERIFY GDELT VERSION** |

**ACTION REQUIRED:** Verify which CAMEO version GDELT actually uses. GDELT may use a modified version.

---

## Next Steps

1. **Verify CAMEO version** - Check GDELT documentation for actual code meanings
2. **Test high-priority codes** - Run queries for codes 014, 071, 072, 081, 082, 106, 111-116, 172-174
3. **Validate results** - Ensure new codes capture relevant events
4. **Update queries** - Add validated codes to comprehensive query script
5. **Document findings** - Create intelligence reports from expanded event coverage

---

**Document Status:** Ready for review
**Next Action:** Review this list and identify which codes to add to queries
**Estimated Expansion:** Adding recommended codes could increase event capture by 200-300%
