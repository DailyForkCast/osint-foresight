# OSINT Foresight - 44 Country Expansion Roadmap

## Master Country List ✅

**Total: 44 countries** documented in `config/MASTER_COUNTRY_LIST.yaml`

### Current Status
- **Active (4)**: Austria, Ireland, Portugal, Slovakia
- **Planned (40)**: All other European and neighboring countries

### Regions Covered
- 🇪🇺 **EU Members**: 27 countries
- 🌍 **EEA/EFTA**: 3 countries (Iceland, Norway, Switzerland)
- 🤝 **EU Candidates**: 7 countries (Albania, Montenegro, Serbia, etc.)
- 🌐 **Other Europe**: 5 countries (UK, Armenia, Azerbaijan, Georgia)
- 📍 **Special Cases**: Kosovo (2), Moldova (2)

---

## National Procurement Portals ✅

**Complete documentation** in `docs/references/NATIONAL_PROCUREMENT_PORTALS.md`

### Coverage by Region
- **EU/EEA (30)**: Full portal identification with URLs
- **Candidates (9)**: All major procurement systems documented  
- **Others (5)**: Including UK's complex multi-portal system

### Portal Types Identified
- **Modern e-Procurement**: TenderNed (NL), ProZorro (UA), Doffin (NO)
- **Government Integrated**: Find a Tender (UK), PLACE (FR)
- **Legacy Systems**: Smaller countries with basic functionality
- **Multi-Level**: Federal + regional portals (Germany, Belgium)

### Language & Access
- 🟢 **English Available**: 35+ portals
- 🟡 **Translation Needed**: 9 smaller countries
- 📋 **CSV Export**: 25+ modern portals
- 🔄 **API Access**: Limited (mainly TED + few national)

---

## Data Source Access Requirements ✅

**Complete analysis** in `docs/references/DATA_SOURCE_ACCESS_REQUIREMENTS.md`

### Free Sources (No Registration) - 8
- ✅ OpenAlex API, CrossRef, World Bank, OECD, Eurostat
- ✅ Working and tested
- ✅ No action needed

### Free with Registration - 6  
- ⏳ **EPO OPS** (patents): developers.epo.org
- ⏳ **ORCID** (researchers): orcid.org
- ⏳ **IETF** (standards): datatracker.ietf.org
- ⏳ **EU Login** (CORDIS bulk): ecas.ec.europa.eu

### Paid/Limited - 3
- 💰 **UN Comtrade**: $99/month for premium
- 💰 **ITC Trade Map**: Limited free tier
- ❌ **OpenCorporates**: $399+/month (excluded)

### Large Downloads - 2
- 💾 **OpenAlex Snapshot**: 300GB via AWS S3
- 💾 **Google Patents**: Via BigQuery

---

## Implementation Strategy

### Phase 1: Scale Current Framework (Months 1-2)
Apply existing analysis phases to priority countries:
```bash
# High priority EU members
for country in BE DE FR IT ES NL PL; do
    python -m src.analysis.phase0_setup --country $country
    python -m src.analysis.phase1_indicators --country $country
    # ... continue through all phases
done
```

### Phase 2: Regional Expansion (Months 3-4)
```bash
# EEA/EFTA countries
for country in NO CH IS; do
    # Full analysis pipeline
done

# EU Candidates
for country in TR UA RS AL ME; do
    # Adapted analysis for different integration levels
done
```

### Phase 3: Complete Coverage (Months 5-6)
```bash
# Remaining countries including Eastern Partnership
for country in AM AZ GE GB; do
    # Context-specific analysis
done
```

### Phase 4: Cross-Country Analysis (Month 6+)
- Regional supply chain mapping
- Technology cluster identification
- Multi-country risk assessment
- Comparative institutional analysis

---

## Resource Requirements

### Storage Scaling
- **Current**: ~10GB (4 countries)
- **All 44 countries**: ~110GB estimated
- **With OpenAlex**: +300GB
- **Solution**: F: drive + selective BigQuery

### API Rate Limits
- **OpenAlex**: 100k/day (sufficient for 44 countries)
- **World Bank**: 120/min (scaling needed)
- **CrossRef**: No issues with polite crawling
- **EPO OPS**: 20GB/month (may need optimization)

### Manual Data Collection
- **Procurement portals**: ~2 hours/country/month
- **Translation needs**: ~9 countries
- **CSV processing**: Automated via existing scripts

---

## Country Prioritization

### Tier 1: Major EU Economies (Complete First)
1. 🇩🇪 Germany - Largest EU economy
2. 🇫🇷 France - Major research hub  
3. 🇮🇹 Italy - Industrial base
4. 🇪🇸 Spain - Growing tech sector
5. 🇳🇱 Netherlands - Trade hub
6. 🇵🇱 Poland - Manufacturing center

### Tier 2: Strategic Partners
7. 🇳🇴 Norway - Energy & sovereign wealth
8. 🇨🇭 Switzerland - Financial & pharma
9. 🇺🇦 Ukraine - Post-conflict reconstruction
10. 🇹🇷 Turkey - Geographic bridge

### Tier 3: Complete Coverage
11-44. All remaining countries for comprehensive analysis

---

## Data Collection Automation

### Existing Scripts (Ready to Scale)
```bash
src/pulls/
├── cordis_pull.py        # EU research projects
├── crossref_pull.py      # Publications
├── gleif_pull.py         # Legal entities
├── ietf_pull.py          # Standards
├── openalex_pull.py      # Research data
├── comtrade_pull.py      # Trade flows (needs subscription)
└── ted_pull.py           # EU procurement (needs setup)
```

### Scaling Commands
```bash
# Automated daily pulls for all countries
make pull-all-countries

# Weekly procurement updates  
make procurement-update-all

# Monthly comprehensive update
make full-update-all
```

---

## Success Metrics

### Coverage Goals
- [ ] **44 countries**: Complete phase 0-13 analysis
- [ ] **44 procurement portals**: Monthly data extraction
- [ ] **10+ data sources**: Automated collection per country
- [ ] **Cross-country**: Comparative analysis framework

### Quality Targets
- [ ] **95% automation**: Minimal manual intervention
- [ ] **Weekly updates**: Fresh data for active monitoring
- [ ] **Multi-language**: Translation for 9+ portal-only countries
- [ ] **Standardized output**: Consistent reporting across countries

---

## Next Actions

### Immediate (This Week)
1. ✅ Master country list documented
2. ✅ Procurement portals identified  
3. ✅ Access requirements mapped
4. ⏳ Register for free API keys (EPO OPS, ORCID)

### Short Term (Next Month)
1. Scale existing scripts to Tier 1 countries
2. Set up monthly procurement portal monitoring
3. Evaluate UN Comtrade subscription need
4. Begin OpenAlex 300GB download to F: drive

### Medium Term (Months 2-6)
1. Complete all 44 countries through Phase 13
2. Implement cross-country analysis
3. Automate report generation pipeline
4. Develop regional risk assessment framework

---

*Total countries: 44*
*Current active: 4*  
*Expansion target: 10x scale increase*
*Estimated completion: 6 months*