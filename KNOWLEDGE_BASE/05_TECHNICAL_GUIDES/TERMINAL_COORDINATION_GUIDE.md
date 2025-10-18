# Terminal Coordination Guide
## EU-Wide Data Collection Framework

**Date:** September 22, 2025
**Status:** Terminal A Complete - Ready for B, C, D
**Framework:** Following MASTER_SQL_WAREHOUSE_GUIDE.md

---

## 🎯 Terminal Assignment Framework

### Terminal A: Major EU Countries ✅ COMPLETE
**Countries:** IT, DE, FR, ES, NL
**Status:** ✅ FULLY INTEGRATED into F:/OSINT_WAREHOUSE/osint_research.db
**Results:** 14.2% China collaboration rate (exceeds 5% target)
**Documentation:** [TERMINAL_A_SUMMARY.md](../../TERMINAL_A_SUMMARY.md)

### Terminal B: Eastern Europe (Ready for Launch)
**Countries:** PL, CZ, HU, SK, RO
**Infrastructure:** Proven methodology from Terminal A
**Expected Results:** Similar 10-15% China collaboration rates

### Terminal C: Nordic/Baltic (Ready for Launch)
**Countries:** SE, DK, FI, EE, LV, LT
**Infrastructure:** Same warehouse integration approach

### Terminal D: Smaller EU States (Ready for Launch)
**Countries:** BE, LU, MT, CY, SI, HR
**Infrastructure:** Standardized collection scripts ready

---

## 🔧 Critical Technical Fix: OpenAIRE API Response Structure

### Problem Discovered
OpenAIRE API returns `results` as a **dict** where each value is a string, NOT a list of objects as initially assumed.

### Incorrect Parsing (Previous):
```python
# WRONG - Assumes results is a list
for pub in data['results']:
    china_score = self.detect_china_involvement(pub.get('title', ''))
```

### Correct Parsing (Fixed):
```python
# CORRECT - Handles dict structure
for result_id, result_content in data['results'].items():
    # result_content is the string content of the publication
    china_score = self.detect_china_involvement(result_content)
```

### Implementation Status
- ✅ Fixed in `scripts/terminal_a_eu_major_collector.py`
- ⚠️ Currently rate-limited (409 errors) but structure correction ready
- 📋 Ready for implementation in Terminals B, C, D

---

## 📊 Warehouse Integration Standards

### Database Schema Compliance
All terminals must follow F:/OSINT_WAREHOUSE/osint_research.db structure:

```sql
-- Core Tables Used
core_f_collaboration     -- Research collaborations
core_f_trade_flow        -- Strategic trade data
core_dim_organization    -- Entity information
research_session         -- Session tracking
```

### Data Quality Standards
- **China Detection Rate:** Target >5%, achieved 14.2%
- **Confidence Scoring:** 0.95 for high-quality sources
- **Provenance Tracking:** Full source_system, retrieved_at, confidence_score
- **Zero Fabrication:** All data traceable to source

### Standard Integration Pattern
```python
# 1. Collect data using corrected APIs
# 2. Apply standardized China detection
# 3. Store with proper schema compliance
# 4. Log session with confidence metrics
# 5. Verify warehouse integration
```

---

## 🚀 Terminal Launch Checklist

### Prerequisites for Any Terminal
- [ ] Warehouse database accessible: F:/OSINT_WAREHOUSE/osint_research.db
- [ ] Terminal collector script created (based on terminal_a_eu_major_collector.py)
- [ ] Country list defined per terminal assignment
- [ ] OpenAIRE API response parsing corrected
- [ ] China detection function standardized

### Launch Sequence
1. **Initialize Terminal Collector**
   ```bash
   cd "C:/Projects/OSINT - Foresight"
   python scripts/terminal_[X]_collector.py
   ```

2. **Monitor Collection Progress**
   - Check for 409 rate limiting
   - Verify China detection rates >5%
   - Monitor warehouse integration

3. **Verify Results**
   ```python
   # Check warehouse status
   conn = sqlite3.connect('F:/OSINT_WAREHOUSE/osint_research.db')
   cursor = conn.execute('SELECT source_system, COUNT(*), SUM(has_chinese_partner) FROM core_f_collaboration GROUP BY source_system')
   ```

4. **Document Session**
   - Update terminal summary document
   - Log any API issues encountered
   - Record China collaboration rates achieved

---

## 📈 Success Metrics

### Per Terminal Targets
- **Collaboration Discovery:** >5% China rate (Terminal A achieved 14.2%)
- **Data Integration:** 100% warehouse compliance
- **Quality Control:** >90% confidence scores
- **Session Logging:** Complete provenance tracking

### EU-Wide Objectives
- **Coverage:** All 27 EU countries + 3 associated
- **Methodology Consistency:** Standardized across all terminals
- **Intelligence Integration:** Cross-terminal analysis capability
- **Timeline:** Complete EU coverage within sprint

---

## ⚠️ Known Issues & Solutions

### OpenAIRE Rate Limiting (409 Errors)
- **Issue:** API currently returning 409 Too Many Requests
- **Solution:** Response structure fix ready for when access restored
- **Workaround:** CORDIS collection continues to work

### API Authentication Requirements
- **USPTO:** PatentsView API v2 deprecated (410 errors)
- **WIPO:** Non-JSON responses, authentication needed
- **Companies House UK:** API key required
- **Recommendation:** Document for future batch processing

### Schema Compatibility
- **Issue:** Collection scripts must match exact warehouse schema
- **Solution:** All Terminal A fixes applied and documented
- **Prevention:** Use INSERT OR REPLACE for all warehouse operations

---

## 🎯 Next Steps

### Immediate (Next Session)
1. Launch Terminal B (Eastern Europe) using proven methodology
2. Verify OpenAIRE structure fix works when API access restored
3. Monitor background data collection processes

### Short Term (This Week)
1. Complete Terminals C and D for full EU coverage
2. Implement cross-terminal intelligence synthesis
3. Develop EU-wide China collaboration analysis

### Medium Term (Next Sprint)
1. Integrate patent data when API access resolved
2. Expand to associated countries (Norway, Switzerland, etc.)
3. Implement automated terminal coordination

---

This guide ensures consistent, high-quality data collection across all EU terminals while maintaining the proven methodology established in Terminal A.
