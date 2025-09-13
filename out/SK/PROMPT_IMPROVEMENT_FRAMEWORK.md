# Prompt Improvement Framework for OSINT Foresight Analysis

## EXECUTIVE SUMMARY

After analyzing all phases, three critical improvements would transform the assessment:
1. **Add adversarial perspective** - What would China/Gotion argue?
2. **Include uncertainty quantification** - Ranges not points, probabilities not certainties
3. **Build in validation requirements** - Every claim needs contradiction search

## IMPROVED MASTER PROMPT TEMPLATE

```markdown
# Phase X: [Phase Name] - Country Analysis

## MANDATORY REQUIREMENTS
1. For every claim, provide:
   - Primary source (with URL/citation)
   - Confidence level (Low 0-30%, Medium 31-70%, High 71-90%, Very High 91-100%)
   - Best contradictory evidence found
   - Data quality score (1-5)

2. For every risk identified, provide:
   - Probability distribution (not point estimate)
   - Time horizon
   - Mitigation cost estimate
   - Opportunity cost of mitigation

3. For every recommendation, provide:
   - Legal feasibility assessment
   - Stakeholder reaction prediction
   - Implementation cost
   - Success metrics

## SECTION 1: BASELINE ESTABLISHMENT
Before analyzing the target country, establish:
- Regional peer comparison (minimum 3 countries)
- Historical trend (10-year minimum)
- Global best practice benchmark
- Theoretical maximum/minimum bounds

## SECTION 2: MULTI-STAKEHOLDER ANALYSIS
For each finding, analyze from perspective of:
- Host government (Slovakia)
- Foreign investor (China/Gotion)
- EU institutions
- NATO allies
- Local population
- Academic community
- Business community

Include dissenting views and minority reports.

## SECTION 3: EVIDENCE COLLECTION
Required evidence hierarchy:
1. Legal documents (agreements, laws, regulations)
2. Financial filings (audited accounts, regulatory filings)
3. Government sources (official statistics, statements)
4. Multiple news sources (3+ independent sources)
5. Academic research (peer-reviewed preferred)
6. Think tank analysis (note funding sources)
7. Social media/OSINT (verify independently)

For each evidence type, note:
- Collection date
- Language of original
- Translation method if applicable
- Potential biases
- Contradictory evidence searched? (Y/N)

## SECTION 4: UNCERTAINTY QUANTIFICATION
All assessments must include:
- Confidence intervals (e.g., "€1.2B ± €200M")
- Probability ranges (e.g., "60-75% likely")
- Sensitivity analysis (what changes the conclusion?)
- Key assumptions (explicit list)
- Breaking points (what invalidates analysis?)

## SECTION 5: PREDICTIVE FRAMEWORK
Include:
- Multiple scenarios (minimum 3, with probabilities)
- Leading indicators (measurable, time-bound)
- Trigger events (specific, observable)
- Feedback loops (how system responds)
- Update mechanism (when/how to revise)

## SECTION 6: VALIDATION REQUIREMENTS
Before finalizing:
□ Red team review conducted
□ Legal feasibility checked
□ Economic impact modeled
□ Stakeholder responses gamed
□ Historical analogies examined
□ Expert review obtained (specify expertise)
```

## SPECIFIC PHASE IMPROVEMENTS

### PHASE 1 - Indicators Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Comparative Context Requirements
- Identify 3 peer countries (similar size, development, EU status)
- Calculate deviation from peer average for each indicator
- Show 10-year trend with volatility measure
- Include data quality assessment (1-5 scale per indicator)

## Contradiction Search
For each partnership/collaboration identified:
- Search for positive outcomes/benefits
- Look for Slovak success stories
- Find Chinese perspective on relationship
- Document any disputes/problems

## Confidence Scoring
Each data point must have:
- Source reliability (A-F scale)
- Information credibility (1-6 scale)
- Corroboration level (Single/Partial/Multiple)
```

### PHASE 2 - Technology Landscape Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Technology Assessment Matrix
For each technology area:
| Technology | TRL | Market Size | SK Capability | Competition | Time to Obsolescence |
|------------|-----|-------------|---------------|-------------|-------------------|
| [Include ranges and confidence levels for all values] |

## Alternative Technology Pathways
- Identify competing technologies
- Assess disruption probability
- Calculate switching costs
- Evaluate leapfrog potential

## Bidirectional Flow Analysis
- Technology FROM Slovakia to partners
- Knowledge/capability gains by Slovakia
- Net technology balance calculation
```

### PHASE 3 - Network Analysis Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Relationship Quality Metrics
Beyond existence of relationships, assess:
- Depth (funding, personnel exchange, duration)
- Productivity (outputs, patents, products)
- Asymmetry (who benefits more?)
- Alternatives (other potential partners)

## Hidden Network Analysis
- Informal relationships
- Personal connections
- Revolving door patterns
- Conference co-attendance
- Citation networks
```

### PHASE 4 - Risk Scoring Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Risk Distribution Modeling
Instead of point scores:
- Monte Carlo simulation (min 1,000 runs)
- Probability distributions for each risk
- Correlation matrix between risks
- Value at Risk (VaR) calculation
- Stress test scenarios

## Opportunity Cost Analysis
For each risk mitigation:
- Benefits foregone
- Alternative uses of resources
- Second-order effects
- Competitive disadvantage created
```

### PHASE 5 - Collaboration Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Collaboration ROI Analysis
For each collaboration:
- Inputs (funding, time, personnel)
- Outputs (papers, patents, products)
- Quality metrics (citations, impact factor)
- Commercialization success
- ROI calculation with confidence interval

## Counterfactual Analysis
- What if collaboration didn't exist?
- Alternative partners available?
- Cost of going alone?
- Lost opportunity quantification
```

### PHASE 6 - Implementation Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Implementation Reality Check
For each measure:
- Legal authority exists? (cite specific law)
- Budget available? (amount and source)
- Personnel capable? (skills and numbers)
- Timeline realistic? (precedent cases)
- Political support? (stakeholder mapping)

## Failure Mode Analysis
- How might implementation fail?
- Workarounds adversaries might use
- Unintended consequences
- Mitigation effectiveness decay rate
```

### PHASE 7C - Communications Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Message Testing Protocol
- A/B testing framework
- Audience segmentation
- Channel effectiveness
- Counter-message preparation
- Credibility assessment

## Narrative War Gaming
- Adversary counter-narratives
- Media cycle modeling
- Influencer mapping
- Information cascade risks
```

### PHASE 8 - Foresight Enhancement
```markdown
ADD TO CURRENT PROMPT:

## Dynamic Adaptation Framework
- Learning mechanisms
- Update triggers
- Course correction protocols
- Failure recognition criteria
- Exit strategies

## Long-term Trajectory Analysis
- 5-year scenarios
- 10-year implications
- Generational impacts
- Reversibility assessment
```

## NEW PHASE PROPOSALS

### PHASE 9: Red Team Contradictory Analysis
```markdown
Purpose: Systematically challenge every major conclusion

Requirements:
1. Assign devil's advocate for each finding
2. Build strongest counter-case possible
3. Find best contradictory evidence
4. Identify logical flaws
5. Challenge assumptions
6. Propose alternative interpretations

Output: Minority report with confidence levels
```

### PHASE 10: Stakeholder Perspective Analysis
```markdown
Purpose: Understand all viewpoints

For each stakeholder:
1. Interests and objectives
2. Constraints and capabilities
3. Alternative options
4. BATNA (best alternative to negotiated agreement)
5. Red lines
6. Coalition potential

Output: Stakeholder strategy matrix
```

### PHASE 11: Economic Impact Modeling
```markdown
Purpose: Quantify economic tradeoffs

Model:
1. Direct impacts (jobs, tax, investment)
2. Indirect impacts (multiplier effects)
3. Opportunity costs
4. Dynamic effects over time
5. Distribution of impacts
6. Uncertainty propagation

Output: Economic CBA with confidence bands
```

## VALIDATION PROTOCOL

### Every Analysis Must Pass:

```markdown
## Quality Gates
□ 3+ independent sources per critical claim
□ Contradictory evidence actively sought
□ Confidence intervals on all numbers
□ Legal feasibility verified
□ Economic impacts quantified
□ Stakeholder responses predicted
□ Historical analogies examined
□ Expert review obtained
□ Red team challenge completed
□ Uncertainty acknowledged throughout

## Rejection Criteria
- Single-source critical claims
- Point estimates without ranges
- Missing stakeholder perspectives
- No contradictory evidence search
- Unfalsifiable predictions
- Binary outcomes without probabilities
- Legal impossibilities
- Economic innumeracy
- Technical implausibility
```

## META-IMPROVEMENT: CONTINUOUS LEARNING

```markdown
## After Each Analysis:
1. Prediction Accuracy Review
   - What did we get right/wrong?
   - Why did we miss what we missed?
   - How can prompts improve?

2. Methodology Enhancement
   - New data sources discovered
   - Better frameworks identified
   - Prompt refinements needed

3. Capability Building
   - Skills gaps identified
   - Tool requirements
   - Network development needs

4. Knowledge Management
   - Lessons learned capture
   - Best practice documentation
   - Template updates
```

## BOTTOM LINE FOR PROMPT IMPROVEMENT

The current prompts are good at **finding risks** but need improvement in:

1. **Quantifying uncertainty** - Add probability distributions
2. **Considering alternatives** - Include opportunity costs
3. **Understanding stakeholders** - Add perspective analysis
4. **Validating feasibility** - Add legal/economic checks
5. **Predicting responses** - Add game theory elements
6. **Learning from outcomes** - Add feedback mechanisms

The single most important improvement would be adding a **"Devil's Advocate" section** to each phase where we actively argue against our own conclusions. This would:
- Increase credibility
- Improve predictions
- Identify blind spots
- Strengthen final recommendations

---
**Key Insight**: The best analysis acknowledges what it doesn't know, quantifies uncertainty, and includes dissenting views. This makes it more trustworthy and actionable than false certainty.