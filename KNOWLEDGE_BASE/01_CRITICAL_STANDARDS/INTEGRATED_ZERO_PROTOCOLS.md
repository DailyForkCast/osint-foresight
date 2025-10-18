# Integrated Zero Fabrication & Zero Assumptions Protocols
**Created:** 2025-09-21
**Purpose:** Unified enforcement of data integrity standards

---

## 🎯 Twin Protocols Working Together

### 1. Zero Fabrication Protocol
- **Focus:** Never claim data we don't have
- **Origin:** Web of Science incident (claimed 15% coverage without data)
- **Key Rule:** "If we didn't count it, we cannot claim it"

### 2. Zero Assumptions Protocol
- **Focus:** Never add interpretation to facts
- **Origin:** SEC "shell company" incident (labeled Cayman companies as shells)
- **Key Rule:** "The facts are interesting enough without embellishment"

---

## ✅ What We've Implemented

### From Zero Fabrication:
1. **Created Core Documents:**
   - Zero Fabrication Protocol with incident log
   - Verification Checklist for all outputs
   - Automated compliance checker script

2. **Updated Scripts:**
   - Added protocol headers to 7+ critical scripts
   - Removed estimation language
   - Fixed "expected" → "detected" terminology

3. **Enhanced Prompts:**
   - Added mandatory zero fabrication sections
   - Modified validation functions
   - Banned estimation terminology

### From Zero Assumptions:
1. **Terminology Guidelines:**
   - Geographic registration (not "shell companies")
   - Operational status (from filings, not interpretation)
   - Corporate structures (VIE disclosed, not "deceptive")
   - Risk assessment (factual criteria only)

2. **Classification Requirements:**
   - Must have specific quote from filing
   - Source reference required
   - Observable characteristics only
   - No added intent or motive

3. **Professional Language:**
   - "41 companies registered in Cayman Islands" ✅
   - "Network of shell companies" ❌
   - "VIE structure disclosed" ✅
   - "Deceptive structures to circumvent law" ❌

---

## 📋 Combined Compliance Checklist

### Before Analysis:
- [ ] Have actual data source access
- [ ] Can extract without interpretation
- [ ] Will report facts not assumptions

### During Analysis:
- [ ] Count/measure actual values
- [ ] Quote directly from sources
- [ ] Avoid interpretive labels
- [ ] Mark confidence levels

### After Analysis:
- [ ] Every claim traceable to source
- [ ] No fabricated statistics
- [ ] No assumed intentions
- [ ] Missing data marked as gaps

---

## 🚫 Complete List of Forbidden Terms

### Estimation Language (Fabrication):
- typically, usually, generally, normally
- likely, probably, presumably
- estimated, expected, anticipated, projected
- "reasonable to assume"
- "industry standard"
- "comparable systems suggest"

### Interpretive Language (Assumptions):
- shell company (without specific evidence)
- deceptive, suspicious, hiding
- circumventing, avoiding, evading
- network (without proven connections)
- scheme, manipulation
- red flag, warning sign (without criteria)

---

## ✅ Required Replacements

### For Numbers:
- "detected X instances"
- "found Y companies"
- "measured Z collaborations"
- "cannot determine"
- "no data available"

### For Entities:
- "registered in [jurisdiction]"
- "incorporated in [country]"
- "reports [fact] per filing"
- "disclosed [structure] in document"
- "operates in [location]"

### For Risk:
- "factor noted"
- "characteristic observed"
- "pattern detected in data"
- "filing states"
- "document shows"

---

## 📊 Value of Combined Approach

### Example - Bad Analysis (with fabrication & assumptions):
```
We estimate approximately 15% of papers have metadata (typical for
academic databases). The network of shell companies in Cayman Islands
suggests deceptive practices to hide ownership, likely representing
high risk for technology transfer.
```

### Example - Good Analysis (zero fabrication & assumptions):
```
OpenAlex data shows 2-3% of papers contain geographic metadata (based
on analysis of 422GB dataset). 41 companies are registered in Cayman
Islands according to SEC filings. 11 companies disclosed Variable
Interest Entity structures in their 20-F filings.
```

---

## 🔍 What's Still Needed

### Documentation Updates:
1. Add Zero Assumptions examples to all script headers
2. Update master prompts with interpretation guidelines
3. Create combined training materials

### Technical Implementation:
1. Enhance compliance checker to detect interpretive language
2. Add pre-commit hooks for both protocols
3. Create automated report reviewer

### Process Improvements:
1. Quarterly audit of all outputs
2. Peer review for risk assessments
3. Source verification workflow

---

## 💡 Key Insights from Integration

1. **Fabrication and assumptions often occur together**
   - Making up data leads to interpretations
   - Assumptions lead to estimated statistics

2. **Both undermine credibility equally**
   - Fabricated data destroys trust
   - Assumed intent destroys objectivity

3. **Facts alone provide sufficient value**
   - Real patterns emerge from real data
   - Verified information enables action

---

## 📝 Action Items

### Immediate:
- [x] Integrate terminology guidelines into Zero Fabrication Protocol
- [x] Add assumption examples to forbidden lists
- [x] Create this unified summary document

### Short-term:
- [ ] Update all remaining scripts with both protocols
- [ ] Train team on combined requirements
- [ ] Implement automated checking for both

### Long-term:
- [ ] Establish culture of verification
- [ ] Regular audits and improvements
- [ ] Expand to all project outputs

---

## 🎖️ Final Principle

**"Professional intelligence analysis reports facts, not fiction or fantasy."**

We provide:
- What we found (not what we think we might find)
- What it is (not what we think it means)
- What we know (not what we assume)

---

*This document integrates the Zero Fabrication Protocol (preventing data fabrication) with the Zero Assumptions Protocol (preventing interpretive assumptions) to create a comprehensive data integrity framework.*
