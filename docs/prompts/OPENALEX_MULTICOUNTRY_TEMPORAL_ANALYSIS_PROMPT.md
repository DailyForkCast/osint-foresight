# OpenAlex Multi-Country Temporal Analysis Prompt

## 🎯 OBJECTIVE
Conduct comprehensive multi-country temporal analysis of China's research collaborations using the 422GB OpenAlex dataset, following the same rigorous methodology successfully applied to TED procurement data.

## 🌍 COUNTRIES OF INTEREST (Expanded Beyond EU)

### Core Analysis Countries (60+)
```python
countries_of_interest = {
    # EU Core (G7 members)
    "DE": "Germany", "FR": "France", "IT": "Italy", "ES": "Spain",
    "NL": "Netherlands", "BE": "Belgium", "LU": "Luxembourg",

    # EU Nordic
    "SE": "Sweden", "DK": "Denmark", "FI": "Finland", "NO": "Norway", "IS": "Iceland",

    # EU Central/Eastern (China's 17+1 Initiative)
    "PL": "Poland", "CZ": "Czech Republic", "SK": "Slovakia",
    "HU": "Hungary", "RO": "Romania", "BG": "Bulgaria",
    "HR": "Croatia", "SI": "Slovenia", "EE": "Estonia",
    "LV": "Latvia", "LT": "Lithuania",

    # EU Mediterranean
    "GR": "Greece", "CY": "Cyprus", "MT": "Malta", "PT": "Portugal",

    # EU Other
    "AT": "Austria", "IE": "Ireland", "CH": "Switzerland", "GB": "United Kingdom",

    # EU Candidates & Balkans
    "AL": "Albania", "MK": "North Macedonia", "RS": "Serbia", "ME": "Montenegro",
    "BA": "Bosnia and Herzegovina", "TR": "Turkey", "UA": "Ukraine", "XK": "Kosovo",

    # European Non-EU Strategic
    "GE": "Georgia", "AM": "Armenia",

    # European Territories
    "FO": "Faroe Islands", "GL": "Greenland",

    # Five Eyes Intelligence Alliance
    "US": "United States", "CA": "Canada", "AU": "Australia", "NZ": "New Zealand",

    # Key Asian Partners/Competitors
    "JP": "Japan", "KR": "South Korea", "SG": "Singapore", "TW": "Taiwan",
    "IN": "India", "TH": "Thailand", "MY": "Malaysia", "VN": "Vietnam",

    # Middle East Strategic Partners
    "IL": "Israel", "AE": "United Arab Emirates", "SA": "Saudi Arabia",

    # Latin America (Belt & Road)
    "BR": "Brazil", "MX": "Mexico", "AR": "Argentina", "CL": "Chile",

    # Africa (Belt & Road)
    "ZA": "South Africa", "EG": "Egypt", "KE": "Kenya", "NG": "Nigeria",

    # Russia and Strategic Partners
    "RU": "Russia", "BY": "Belarus", "KZ": "Kazakhstan",

    # Target Country
    "CN": "China"
}
```

## 📊 ANALYSIS FRAMEWORK

### 1. **Temporal Periods (2000-2025)**
```python
temporal_periods = {
    "pre_bri_baseline_2000_2012": {
        "years": list(range(2000, 2013)),
        "description": "Pre-Belt & Road baseline research patterns",
        "context": "Normal academic collaboration before strategic initiatives"
    },
    "bri_launch_2013_2016": {
        "years": list(range(2013, 2017)),
        "description": "Belt & Road Initiative launch period",
        "context": "Strategic research partnerships begin"
    },
    "expansion_2017_2019": {
        "years": list(range(2017, 2020)),
        "description": "Peak expansion and investment period",
        "context": "Maximum Chinese research collaboration growth"
    },
    "trade_war_2020_2021": {
        "years": [2020, 2021],
        "description": "Trade tensions and COVID period",
        "context": "Restrictions and supply chain awareness"
    },
    "decoupling_2022_2025": {
        "years": list(range(2022, 2026)),
        "description": "Technology decoupling and restrictions",
        "context": "Research restrictions and partner shifting"
    }
}
```

### 2. **Critical Technology Categories**
```python
dual_use_technologies = {
    "artificial_intelligence": {
        "keywords": ["artificial intelligence", "machine learning", "deep learning", "neural network", "computer vision", "natural language processing"],
        "risk_level": "CRITICAL",
        "strategic_importance": "Foundational technology for military and surveillance"
    },
    "quantum_computing": {
        "keywords": ["quantum computing", "quantum communication", "quantum cryptography", "quantum algorithm", "quantum entanglement"],
        "risk_level": "CRITICAL",
        "strategic_importance": "Next-generation encryption and computing"
    },
    "semiconductors": {
        "keywords": ["semiconductor", "microprocessor", "integrated circuit", "chip design", "lithography", "silicon wafer"],
        "risk_level": "CRITICAL",
        "strategic_importance": "Foundation of all digital technology"
    },
    "biotechnology": {
        "keywords": ["biotechnology", "genetic engineering", "CRISPR", "gene therapy", "bioweapons", "synthetic biology"],
        "risk_level": "HIGH",
        "strategic_importance": "Dual-use medical and weapons applications"
    },
    "aerospace": {
        "keywords": ["aerospace", "satellite", "rocket", "missile", "space technology", "launch vehicle", "hypersonic"],
        "risk_level": "HIGH",
        "strategic_importance": "Military and space applications"
    },
    "nuclear_technology": {
        "keywords": ["nuclear reactor", "uranium enrichment", "nuclear fuel", "fusion", "fission", "radioactive"],
        "risk_level": "CRITICAL",
        "strategic_importance": "Weapons and energy applications"
    },
    "telecommunications": {
        "keywords": ["5G", "6G", "wireless communication", "telecommunications", "network infrastructure", "fiber optic"],
        "risk_level": "HIGH",
        "strategic_importance": "Critical infrastructure and surveillance"
    },
    "cybersecurity": {
        "keywords": ["cybersecurity", "encryption", "cryptography", "network security", "malware", "cyber warfare"],
        "risk_level": "HIGH",
        "strategic_importance": "National security and defense"
    },
    "advanced_materials": {
        "keywords": ["graphene", "carbon nanotube", "metamaterial", "superconductor", "smart material", "composites"],
        "risk_level": "MEDIUM",
        "strategic_importance": "Next-generation manufacturing and defense"
    },
    "energy_storage": {
        "keywords": ["battery technology", "energy storage", "lithium ion", "fuel cell", "supercapacitor"],
        "risk_level": "MEDIUM",
        "strategic_importance": "Critical for military and infrastructure"
    }
}
```

### 3. **Research Collaboration Patterns to Detect**
```python
collaboration_patterns = {
    "talent_acquisition": {
        "indicators": ["visiting scholar", "joint PhD", "postdoc exchange", "faculty hire"],
        "risk": "Brain drain and knowledge transfer"
    },
    "technology_transfer": {
        "indicators": ["patent collaboration", "licensing agreement", "joint patent", "technology sharing"],
        "risk": "Dual-use technology acquisition"
    },
    "strategic_partnerships": {
        "indicators": ["belt and road", "BRI", "sister university", "Confucius Institute"],
        "risk": "Influence operations and strategic positioning"
    },
    "funding_influence": {
        "indicators": ["China funding", "Chinese grant", "NSFC", "CAS funding"],
        "risk": "Research direction influence"
    },
    "institution_building": {
        "indicators": ["joint institute", "research center", "collaboration agreement"],
        "risk": "Long-term institutional capture"
    }
}
```

## 🔧 TECHNICAL IMPLEMENTATION

### Processing Requirements
```python
# Hardware requirements (from TED success)
minimum_requirements = {
    "ram": "32GB minimum for streaming processing",
    "storage": "422GB OpenAlex data at F:/OSINT_Backups/openalex/data/",
    "processing": "Streaming architecture (line-by-line, not full file load)",
    "checkpoint": "Resume from existing 1.2M record checkpoint"
}

# Data format
openalex_format = {
    "location": "F:/OSINT_Backups/openalex/data/",
    "format": "JSONL (newline-delimited JSON)",
    "structure": "One paper per line",
    "size": "422GB total",
    "status": "0.5% processed (Germany-China only)"
}
```

### Zero Fabrication Requirements
```python
verification_requirements = {
    "source_verification": "Every finding must trace to specific JSONL line",
    "reproduction_commands": "Provide exact grep/jq commands to verify findings",
    "evidence_extraction": "Include actual paper titles, DOIs, author affiliations",
    "integrity_checks": "SHA256 verification of source files",
    "no_interpolation": "Never estimate or fill missing data"
}
```

## 📋 ANALYSIS TASKS

### Phase 1: Infrastructure Setup
1. **Update OpenAlex processor for multi-country analysis**
   - Extend beyond Germany-China to all countries of interest
   - Add temporal period detection (2000-2025)
   - Implement dual-use technology classification
   - Add collaboration pattern detection

2. **Create country-specific tracking**
   - Individual country collaboration profiles
   - Cross-country comparison matrices
   - Temporal progression tracking per country

### Phase 2: Temporal Analysis
1. **Process by time periods**
   - Pre-BRI baseline (2000-2012)
   - BRI launch (2013-2016)
   - Expansion (2017-2019)
   - Trade war (2020-2021)
   - Decoupling (2022-2025)

2. **Detect temporal patterns**
   - Research collaboration growth/decline
   - Technology focus shifts
   - Institution relationship changes
   - Author migration patterns

### Phase 3: Technology Risk Assessment
1. **Dual-use technology mapping**
   - AI/ML collaboration intensity
   - Quantum computing partnerships
   - Semiconductor research sharing
   - Biotechnology joint projects

2. **Strategic pattern detection**
   - Technology transfer evidence
   - Talent acquisition patterns
   - Funding influence mapping
   - Institution building timeline

### Phase 4: Comparative Analysis
1. **Cross-country patterns**
   - Which countries most exposed to China collaboration?
   - How do Five Eyes compare to EU countries?
   - Are there coordinated research campaigns?
   - Regional variation analysis (Nordic vs. Central EU vs. Mediterranean)

2. **Temporal comparison**
   - How did collaboration patterns change post-2013 (BRI)?
   - Impact of 2020 trade tensions
   - Evidence of research decoupling 2022+

## 📊 OUTPUT STRUCTURE

### Directory Organization
```
data/processed/openalex_multicountry_temporal/
├── by_country/
│   ├── US_china/                    ← US-China collaborations
│   ├── DE_china/                    ← Germany-China collaborations
│   ├── [ALL_COUNTRIES]_china/       ← Each country's China partnerships
│   └── comparative_analysis.json    ← Cross-country comparison
├── by_period/
│   ├── pre_bri_2000_2012/          ← Baseline period analysis
│   ├── bri_launch_2013_2016/       ← BRI launch period
│   ├── expansion_2017_2019/        ← Peak collaboration period
│   ├── trade_war_2020_2021/        ← Tension period
│   └── decoupling_2022_2025/       ← Current restrictions period
├── by_technology/
│   ├── artificial_intelligence/     ← AI collaboration analysis
│   ├── quantum_computing/          ← Quantum research partnerships
│   ├── semiconductors/             ← Chip research collaboration
│   └── [ALL_TECH_CATEGORIES]/      ← Each technology area
├── patterns/
│   ├── talent_acquisition.json     ← Scholar/researcher movement
│   ├── technology_transfer.json    ← Tech sharing evidence
│   ├── strategic_partnerships.json ← Institutional relationships
│   └── funding_influence.json      ← Chinese funding patterns
├── networks/
│   ├── collaboration_graph.gexf    ← Network visualization data
│   └── temporal_evolution.json     ← How networks changed over time
├── analysis/
│   ├── EXECUTIVE_BRIEFING.md       ← High-level findings
│   ├── COUNTRY_RISK_RANKING.json  ← Countries by exposure level
│   ├── TECHNOLOGY_RISK_MATRIX.json ← Tech areas by risk level
│   └── TEMPORAL_ANALYSIS_REPORT.md ← Timeline patterns
└── verification/
    ├── findings_verification.json   ← Every finding with grep commands
    └── integrity_check.json         ← Processing verification
```

### Finding Structure
```json
{
    "paper_id": "https://openalex.org/W1234567890",
    "title": "Quantum Computing Applications in Cryptography",
    "publication_year": 2019,
    "countries_collaborating": ["US", "CN"],
    "institutions": {
        "US": ["MIT", "Stanford University"],
        "CN": ["Tsinghua University", "Chinese Academy of Sciences"]
    },
    "authors_by_country": {
        "US": ["John Smith (MIT)", "Jane Doe (Stanford)"],
        "CN": ["Li Wei (Tsinghua)", "Zhang Ming (CAS)"]
    },
    "technology_categories": ["quantum_computing", "cybersecurity"],
    "collaboration_patterns": ["joint_research", "co_authorship"],
    "risk_assessment": {
        "technology_risk": "CRITICAL",
        "collaboration_risk": "HIGH",
        "strategic_concern": "Quantum cryptography dual-use potential"
    },
    "temporal_context": {
        "period": "expansion_2017_2019",
        "pre_bri_baseline": false,
        "post_restrictions": false
    },
    "verification": {
        "source_file": "F:/OSINT_Backups/openalex/data/works_part_00001.jsonl",
        "line_number": 1247893,
        "extraction_command": "sed -n '1247893p' works_part_00001.jsonl | jq '.title'",
        "doi": "10.1038/nature12345",
        "openalex_url": "https://openalex.org/W1234567890"
    }
}
```

## 🎯 SUCCESS METRICS

### Quantitative Targets
- **Countries analyzed:** All 50+ countries of interest
- **Time coverage:** 2000-2025 (25 years)
- **Technology categories:** 10 dual-use areas
- **Collaboration types:** 5 pattern categories
- **Verification rate:** 100% of findings verifiable

### Strategic Intelligence Goals
1. **Map China's global research influence network**
2. **Identify technology transfer vulnerabilities by country**
3. **Track temporal evolution of strategic partnerships**
4. **Assess current decoupling effectiveness**
5. **Predict future collaboration patterns**

## 🚨 CRITICAL REQUIREMENTS

### Zero Fabrication Protocol
- **Source verification:** Every finding traceable to specific JSONL line
- **Reproduction commands:** Exact bash/jq commands for each finding
- **Evidence integrity:** Complete paper metadata, not summaries
- **No interpolation:** Return `INSUFFICIENT_EVIDENCE` for missing data
- **Checkpoint resumption:** Build on existing 1.2M record processing

### Processing Approach
1. **Stream processing:** Process line-by-line, never load full files
2. **Checkpoint frequent:** Save progress every 100K records
3. **Parallel processing:** Multi-country analysis simultaneously
4. **Memory management:** 32GB RAM requirement for streaming
5. **Error handling:** Graceful handling of malformed JSON

## 🎬 EXECUTION COMMAND

```bash
# Create the multi-country OpenAlex processor
python scripts/create_openalex_multicountry_processor.py

# Run the analysis
python scripts/process_openalex_multicountry_temporal.py --resume-checkpoint --countries-all --periods 2000-2025 --technologies dual-use-all

# Generate reports
python scripts/generate_openalex_strategic_intelligence_report.py
```

---

**SUCCESS CRITERIA:** Successfully replicate TED's multi-country temporal analysis methodology for OpenAlex, producing verified China collaboration intelligence across 50+ countries, 25 years, and 10 critical technology areas with zero fabrication and complete verification.

**DELIVERABLE:** Comprehensive strategic intelligence report on China's global research influence network with country-by-country risk assessments and temporal analysis of collaboration evolution.
