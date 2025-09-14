# OSINT Foresight Final Prompt System Summary
## Version 3.7 / 1.7 - NATO Enhanced Edition

Generated: 2025-09-13

---

## 📋 FINAL PROMPT INVENTORY

### Active Production Prompts (2 files)

1. **CHATGPT_OPERATOR_FINAL_V3.7.md**
   - Role: Analyst-orchestrator
   - Focus: Synthesis, analysis, decision-grade outputs
   - Key features: NATO integration, ticket system, quality gates
   - Location: `/docs/prompts/`

2. **CLAUDE_CODE_FINAL_V1.7.md**
   - Role: Technical implementer
   - Focus: Data collection, pipeline automation, ticket response
   - Key features: NATO collectors, schema validation, 35-40% automation
   - Location: `/docs/prompts/`

### Archived Prompts (moved to `/docs/prompts/archive/`)
- CHATGPT_MASTER_PROMPT_V3.2.md
- CHATGPT_MASTER_PROMPT_V3.5.md
- CHATGPT_MASTER_PROMPT_V3.6_NATO.md
- CLAUDE_CODE_MASTER_PROMPT_V1.2.md
- CLAUDE_CODE_MASTER_PROMPT_V1.5.md
- lean_operator_pack_chat_gpt_v_3.md
- lean_operator_pack_claude_code_v_1.md
- Master_Prompt_vNext_Claude_Updates_FINAL.md

---

## 🚀 KEY ENHANCEMENTS IN FINAL VERSION

### 1. NATO Integration (NEW)
- **Phase 2.5**: Dedicated NATO assessment
- **Phase 3.4**: NATO policies and STANAG adoption
- **Phase 4.5**: NATO supply chain dependencies
- **Phase 5.7**: DIANA sites and COE footprint
- **Phase 6.7**: NATO funding (DIANA, NIF, STO)
- **Phase 7.5-7.6**: NATO cooperation and STANAG mapping
- **Phase 11.7**: NATO early warning system

### 2. US Involvement Tracking
- **Phase 4.4**: US-owned EU supply nodes
- **Phase 6.6**: US funding links to EU
- **Phase 7.4**: US-EU collaboration maps
- **Phase 9.10**: US→EU soft-points analysis
- **Phase 11.5**: Compute/data exposure

### 3. Quality Control System
- **Ticket System**: Structured gap reporting
- **ICE Priority**: Impact/Confidence/Effort scoring
- **Stop-Conditions**: Automatic quality gates
- **Evidence Standards**: 5-level data quality scale
- **Validation**: Schema enforcement on all artifacts

### 4. Data Collection Strategy
- **Automated**: 28 countries with API access
- **Manual**: 16 countries requiring quarterly updates
- **NATO Automation**: 35-40% of NATO data automatable
- **Hybrid Approach**: 75-80% coverage achievable

---

## 📊 NATO ASSESSMENT COVERAGE

### What We Can Automate (35-40%)
✅ Defense spending statistics (95% automated)
✅ Exercise announcements (80% automated)
✅ Document metadata (70% automated)
⚡ STO publication abstracts (60% automated)
⚡ COE updates (50% automated)

### Manual Collection Required (45%)
🔄 DIANA sites and companies
🔄 NIF portfolio details
🔄 NSPA contract analysis
🔄 STANAG implementation status
🔄 COE research projects
🔄 Minilateral agreements

### Classified/Inaccessible (20%)
⛔ Detailed NDPP targets
⛔ Force generation plans
⛔ Internal interoperability scores
⛔ Restricted technology roadmaps

---

## 🎯 OPERATIONAL WORKFLOW

### ChatGPT (Analyst) Tasks
1. Load artifacts from `ARTIFACT_DIR`
2. Synthesize intelligence across phases
3. Generate executive briefs
4. Identify gaps and create tickets
5. Apply quality gates and stop-conditions
6. Produce country assessment with NATO context

### Claude Code (Implementer) Tasks
1. Execute data collection pipelines
2. Respond to ChatGPT tickets
3. Validate artifact schemas
4. Maintain 35-40% NATO automation
5. Schedule manual collection tasks
6. Update evidence tables

### Collaboration Protocol
```
ChatGPT → Ticket → Claude Code → Data Collection → Artifact Update → ChatGPT
```

---

## 📋 PHASE EXECUTION CHECKLIST

### Phase 0-2: Foundation
- [ ] Taxonomy includes NATO capabilities
- [ ] Entity resolution with NATO codes
- [ ] Defense spending vs 2% target
- [ ] STANAG compliance baseline

### Phase 3-5: Landscape & Networks
- [ ] NATO infrastructure mapped
- [ ] DIANA/COE participation tracked
- [ ] Framework nation roles identified
- [ ] Hub discovery with NATO context

### Phase 6-7: Funding & Links
- [ ] NATO funding programs included
- [ ] Minilateral formats mapped
- [ ] Exercise participation tracked
- [ ] STANAG↔civil standards mapped

### Phase 8-11: Assessment & Foresight
- [ ] NATO-specific risks assessed
- [ ] Alliance cohesion evaluated
- [ ] Capability gaps identified
- [ ] Early warning thresholds set

### Phase 12-13: Closeout
- [ ] Regional dynamics analyzed
- [ ] Policy mismatches documented
- [ ] Implementation plan NATO-aligned
- [ ] Monitoring handoff complete

---

## 🔧 IMPLEMENTATION REQUIREMENTS

### Technical Infrastructure
- **Storage**: F: drive (7TB available) for data
- **Scripts**: Python automation for 35-40% NATO data
- **Manual**: Quarterly updates for 45% of data
- **Validation**: JSON schema enforcement

### Data Sources
- **Automated APIs**: 28 national statistics offices
- **OpenAlex**: 420GB snapshot on F: drive
- **NATO Sources**: STO, COEs, multimedia library
- **Common Crawl**: Multilingual patterns configured

### Quality Standards
- **Corroboration**: ≥2 sources for moderate claims
- **Policy Window**: 2019-2025 for all policies
- **Confidence Levels**: Low/Med/High with justification
- **Data Quality**: 1-5 scale (rumor to primary)

---

## 💡 CRITICAL SUCCESS FACTORS

### 1. NATO Awareness
- Always check NATO membership status first
- Tailor assessment to membership level
- Track defense spending and capability targets
- Monitor innovation ecosystem participation

### 2. Automation Reality
- Accept 35-40% NATO automation limit
- Structure manual collection efficiently
- Use proxies for classified data
- Maintain hybrid approach for 75-80% coverage

### 3. Quality Control
- Enforce ticket system for gaps
- Apply stop-conditions rigorously
- Validate all schemas
- Document confidence levels

### 4. Collaboration
- Clear handoffs between ChatGPT and Claude
- Structured ticket format
- Evidence-based assessments
- Continuous validation

---

## 📅 OPERATIONAL TIMELINE

### Daily
- Monitor NATO exercise announcements
- Track defense news and updates

### Weekly
- Update research publications
- Aggregate COE news
- Review patent filings

### Monthly
- Pull economic indicators
- Update STANAG tracking
- Collect STO abstracts

### Quarterly
- Comprehensive NATO assessment
- Manual data collection campaign
- DIANA/NIF portfolio update
- Minilateral format review

---

## 🎯 EXPECTED OUTCOMES

With this final prompt system, you can:

1. **Assess any of 44 European countries** with NATO context
2. **Track defense innovation** across 15 technology domains
3. **Identify capability gaps** and specialization opportunities
4. **Monitor alliance dynamics** and regional cooperation
5. **Generate executive-grade** intelligence products
6. **Maintain 75-80% coverage** of accessible intelligence
7. **Automate 35-40%** of NATO data collection
8. **Ensure quality** through validation and tickets

---

## 📝 QUICK START COMMANDS

```bash
# 1. Check country status
python scripts/check_nato_status.py --country=Germany

# 2. Run automated collection
python scripts/nato_automated_collection.py --country=Germany

# 3. Generate analysis
# In ChatGPT: Load artifacts and run v3.7 prompt

# 4. Handle tickets
python scripts/process_tickets.py --country=Germany

# 5. Validate outputs
python scripts/validate_artifacts.py --country=Germany
```

---

## ⚠️ IMPORTANT NOTES

1. **NATO data limitations**: Much is classified or restricted
2. **Manual effort required**: 45% needs human collection
3. **Language barriers**: 30+ countries, multiple languages
4. **Update frequencies**: Different sources update at different rates
5. **Quality variations**: Not all countries provide equal data

---

*This final prompt system (v3.7/1.7) represents the complete integration of NATO assessment capabilities with the OSINT Foresight framework, addressing all identified gaps and providing comprehensive coverage of European defense technology landscapes.*
