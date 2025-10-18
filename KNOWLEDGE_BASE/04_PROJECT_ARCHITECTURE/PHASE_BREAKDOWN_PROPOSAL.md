# PHASE BREAKDOWN PROPOSAL
**Breaking Complex Phases into Manageable Sub-Tasks**
**Date:** 2025-09-19

---

## 🎯 WHY BREAK DOWN PHASES?

### Current Problem:
- Phases are too large/complex
- LLMs lose track of requirements
- Easy to skip verification steps
- Fabrication can slip in

### Solution:
- Smaller, focused sub-phases
- Each with specific output
- Clear verification gates
- No room for fabrication

---

## 🔄 PROPOSED PHASE BREAKDOWN

### Phase 2: Technology Indicators → 5 Sub-phases

```yaml
OLD_PHASE_2:
  scope: "All technology landscape analysis"
  problem: "Too broad, easy to fabricate"

NEW_PHASE_2_BREAKDOWN:

  2.1_data_inventory:
    objective: "List available data sources"
    output: "Sources with access status"
    verification: "Can we access each?"
    no_fabrication: "Only list what exists"

  2.2_academic_analysis:
    objective: "Process OpenAlex/papers"
    input: "Specific database/files"
    output: "Paper counts by field"
    verification: "Recompute command for each count"
    maximum: "1000 papers per batch"

  2.3_patent_analysis:
    objective: "Process patent databases"
    input: "USPTO/EPO exports"
    output: "Patent counts by assignee"
    verification: "SQL query for each number"
    maximum: "500 patents per batch"

  2.4_integration:
    objective: "Combine 2.2 and 2.3"
    input: "Previous outputs only"
    output: "Technology overlap matrix"
    verification: "Trace each cell to source"

  2.5_validation:
    objective: "Verify all claims"
    input: "2.4 output"
    output: "Validated technology landscape"
    checklist: "Every number sourced"
```

### Phase 3: Institutional Landscape → 4 Sub-phases

```yaml
PHASE_3_BREAKDOWN:

  3.1_entity_extraction:
    objective: "List all entities mentioned"
    input: "Specific sources"
    output: "Entity list with source"
    rule: "No entities without source"

  3.2_relationship_mapping:
    objective: "Document known relationships"
    input: "3.1 entities"
    output: "Relationship pairs with evidence"
    rule: "No assumed relationships"

  3.3_verification:
    objective: "Verify each relationship"
    input: "3.2 pairs"
    method: "Check second source"
    output: "Verified relationships only"

  3.4_network_assembly:
    objective: "Build network from verified"
    input: "3.3 verified only"
    output: "Network with confidence scores"
    rule: "Unverified marked clearly"
```

### Phase 4: Supply Chain → 6 Sub-phases

```yaml
PHASE_4_BREAKDOWN:

  4.1_procurement_data:
    objective: "Gather procurement records"
    sources: "TED, USAspending"
    output: "Contract list"
    verify: "Each contract number real"

  4.2_supplier_identification:
    objective: "Extract supplier names"
    input: "4.1 contracts"
    output: "Supplier list with contracts"
    verify: "Trace to contract"

  4.3_tier_classification:
    objective: "Classify supplier tiers"
    input: "4.2 suppliers"
    method: "By contract value/type"
    output: "Tiered supplier list"

  4.4_dependency_analysis:
    objective: "Identify dependencies"
    input: "4.3 tiers"
    method: "Single source analysis"
    output: "Critical dependencies"

  4.5_china_connections:
    objective: "Find China links"
    input: "4.2 suppliers"
    method: "Name matching + verification"
    output: "Verified China connections only"

  4.6_risk_assessment:
    objective: "Assess supply risk"
    input: "4.4 + 4.5"
    output: "Risk matrix with evidence"
    verify: "Each risk traced to data"
```

---

## ✅ BENEFITS OF BREAKDOWN

### 1. **Focused Attention**
- LLM handles one task at a time
- Less context to track
- Fewer requirements to remember

### 2. **Clear Verification**
- Each sub-phase has specific output
- Easy to verify completeness
- No ambiguity about requirements

### 3. **Prevents Fabrication**
- Smaller scope = less temptation
- Clear input/output requirements
- Verification at each step

### 4. **Better Error Recovery**
- Failure isolated to sub-phase
- Don't lose entire phase work
- Clear restart points

### 5. **Progress Tracking**
- See completion percentage
- Identify bottlenecks
- Celebrate small wins

---

## 📋 IMPLEMENTATION RULES

### Every Sub-phase Must Have:

```yaml
SUB_PHASE_TEMPLATE:
  number: "X.Y format"
  name: "Descriptive title"
  objective: "One clear goal"
  input: "Specific data sources"
  process: "Exact steps"
  output: "Defined deliverable"
  verification: "How to check"
  maximum: "Batch size limit"

  anti_fabrication:
    - "What NOT to do"
    - "What to output if no data"
    - "Verification requirement"

  example_output: "Sample of expected result"
```

### Gate Between Sub-phases:

```yaml
VERIFICATION_GATE:
  before_proceeding:
    - All outputs documented?
    - All sources cited?
    - All numbers verified?
    - INSUFFICIENT_EVIDENCE used?
    - Self-verification complete?

  if_any_no:
    action: "Cannot proceed to next sub-phase"
    requirement: "Fix issues first"
```

---

## 🎯 RECOMMENDED APPROACH

### Phase Execution:

1. **Start sub-phase**
   - Read specific requirements
   - Identify available data
   - Note what's missing

2. **Process data**
   - Follow exact steps
   - Document everything
   - Use INSUFFICIENT_EVIDENCE

3. **Verify output**
   - Self-check claims
   - Trace to sources
   - Remove unsupported

4. **Gate check**
   - Meet all requirements?
   - If yes: proceed
   - If no: fix and retry

5. **Next sub-phase**
   - Use previous output as input
   - Don't recreate/assume
   - Build incrementally

---

## 💡 KEY INSIGHT

**Better to have 10 small successes than 1 large failure.**

Each sub-phase is:
- Achievable
- Verifiable
- Focused
- Documented

This makes fabrication nearly impossible and quality much higher.
