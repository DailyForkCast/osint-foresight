# USPTO Intelligence Requirements for OSINT Analysis

**Date:** September 18, 2025
**Purpose:** Define what USPTO patent data is relevant for technology transfer and dual-use research
**Focus:** Objective identification of technology relationships without bias

---

## Executive Summary

USPTO patent data provides critical intelligence on technology development, international collaborations, and potential dual-use concerns. This document defines specific data requirements for objective analysis.

---

## 1. KEY DATA ELEMENTS TO EXTRACT

### Patent Metadata
- **Patent Number & Date:** Timing of innovation
- **Title & Abstract:** Technology description
- **CPC Classifications:** Technical categories
- **Claims:** Specific technical innovations

### Entity Information
- **Inventors:** Names, locations, affiliations
- **Assignees:** Organizations holding rights
- **Geographic Data:** Countries of inventors/assignees
- **Assignment History:** Ownership transfers

### Collaboration Indicators
- **Co-inventors:** Cross-border partnerships
- **Joint Assignees:** Organizational collaborations
- **Citation Networks:** Technology dependencies
- **Patent Families:** International filings

---

## 2. TECHNOLOGY CATEGORIES OF INTEREST

### Based on CPC (Cooperative Patent Classification)

#### Advanced Materials
- **B82**: Nanotechnology
- **C01B**: Non-metallic elements (graphene, etc.)
- **C22**: Metallurgy, ferrous/non-ferrous alloys

#### Computing & AI
- **G06N**: Machine learning systems
- **G06F**: Data processing
- **H04L**: Digital communications

#### Biotechnology
- **C12N**: Microorganisms, genetic engineering
- **C07K**: Peptides, proteins
- **A61K**: Medical preparations

#### Energy Systems
- **H01M**: Batteries, fuel cells
- **H02J**: Power supply circuits
- **F03D**: Wind motors

#### Semiconductors
- **H01L**: Semiconductor devices
- **H10**: Semiconductor memories
- **G03F**: Photolithography

#### Quantum Technologies
- **G06N10**: Quantum computing
- **H04B10**: Quantum communications
- **G01**: Quantum sensing

---

## 3. SEARCH QUERIES FOR SLOVAKIA ANALYSIS

### Primary Searches

```sql
-- Slovak inventors or assignees
(inventor_country:SK OR assignee_country:SK)
AND patent_date:[2020-01-01 TO 2025-12-31]

-- Slovak-China collaborations
((inventor_country:SK OR assignee_country:SK)
AND (inventor_country:CN OR assignee_country:CN))

-- Slovak technology areas
(inventor_country:SK OR assignee_country:SK)
AND cpc_section:(G OR H)  -- Electronics/Physics

-- Slovak universities
assignee_organization:("Slovak Technical University" OR
                      "Comenius University" OR
                      "Technical University of Košice")
```

### Technology Transfer Indicators
1. **Assignment transfers** from universities to companies
2. **Foreign assignees** with Slovak inventors
3. **Joint patents** between Slovak and foreign entities
4. **Citation patterns** showing technology flow

---

## 4. DUAL-USE TECHNOLOGY IDENTIFICATION

### Objective Criteria for Dual-Use Assessment

#### Technical Specifications to Extract:
- **Performance metrics** (speed, accuracy, power)
- **Material compositions**
- **Process parameters**
- **System architectures**

#### Application Domain Analysis:
- Stated use cases in patent
- Technical specifications alignment
- Citation to/from defense contractors
- Government interest statements

### Example Analysis Framework:
```python
# Objective dual-use assessment
patent_data = {
    "title": "High-frequency radar signal processing",
    "cpc_codes": ["G01S", "H04B"],  # Radar, transmission
    "assignee": "University XYZ",
    "specifications": {
        "frequency_range": "24-77 GHz",
        "resolution": "1mm",
        "processing_speed": "real-time"
    }
}

# Document technical capabilities without speculation
civilian_applications = ["Automotive radar", "Weather monitoring"]
technical_capabilities = ["Long-range detection", "Multi-target tracking"]
```

---

## 5. DATA COLLECTION PRIORITIES

### Immediate (Week 1)
1. **Slovak patent landscape** (2020-2025)
2. **Top Slovak assignees** by patent count
3. **International collaborations** by country
4. **Technology distribution** by CPC code

### Short-term (Month 1)
1. **Citation network analysis**
2. **Assignment transfer patterns**
3. **Emerging technology areas**
4. **Key inventor networks**

### Ongoing Monitoring
1. **New patent applications** (weekly)
2. **Assignment changes** (monthly)
3. **International filing patterns** (quarterly)

---

## 6. ANALYSIS OUTPUTS

### Standard Reports

#### 1. Technology Landscape Report
- Patent counts by CPC category
- Trend analysis (5-year)
- Top assignees and inventors
- Geographic distribution

#### 2. Collaboration Matrix
- Country-to-country patent counts
- Joint assignee relationships
- Co-inventor networks
- Technology areas of collaboration

#### 3. Entity Profiles
- Patent portfolios by organization
- Technology focus areas
- Collaboration partners
- Assignment history

#### 4. Dual-Use Technology Assessment
- Technical specifications documented
- Stated applications from patents
- Related patent families
- Citation patterns

---

## 7. QUALITY CONTROL

### Data Validation Requirements
- **Entity disambiguation:** Verify organization names
- **Geographic verification:** Confirm country codes
- **Date consistency:** Check filing vs grant dates
- **Classification accuracy:** Validate CPC codes

### Statistical Checks
- Concentration analysis (>50% in single entity = review)
- Temporal consistency (patents before company founding = error)
- Geographic logic (inventors in likely locations)

---

## 8. INTEGRATION WITH OTHER DATA SOURCES

### Cross-Reference Opportunities

| USPTO Data | Cross-Reference With | Intelligence Value |
|------------|---------------------|-------------------|
| Patent Assignees | OpenAlex Publications | Research to commercialization |
| Inventors | LinkedIn/Web | Current affiliations |
| Technology Areas | TED Procurement | Government interest |
| Patent Citations | Academic Papers | Knowledge transfer |
| Assignment Changes | Corporate Records | M&A activity |

---

## 9. AUTOMATED MONITORING SETUP

### Python Implementation
```python
from src.pulls.uspto_open_data_client import USPTOOpenDataClient

# Weekly monitoring script
def monitor_slovak_patents():
    client = USPTOOpenDataClient()

    # Search parameters
    countries = ["SK", "CZ", "HU", "PL"]  # V4 countries
    tech_areas = ["G06N", "H01L", "C12N"]  # AI, Semiconductors, Biotech

    results = {}
    for country in countries:
        results[country] = client.search_by_country(
            country_code=country,
            start_date="2025-01-01"
        )

    return analyze_results(results)
```

---

## 10. SUCCESS METRICS

### Collection Metrics
- Patents collected: Target 10,000+ for Slovakia
- Time coverage: 2020-2025 minimum
- Update frequency: Weekly for new patents

### Analysis Quality
- Entity disambiguation rate: >95%
- Geographic accuracy: >99%
- Classification precision: >90%
- False positive rate: <1%

---

## APPENDIX: CPC Classification Reference

### Key Sections
- **A**: Human Necessities (Medical, Agriculture)
- **B**: Performing Operations (Manufacturing)
- **C**: Chemistry, Metallurgy
- **D**: Textiles, Paper
- **E**: Fixed Constructions
- **F**: Mechanical Engineering
- **G**: Physics (Computing, Instruments)
- **H**: Electricity (Electronics, Energy)

### Priority Technology Classes
- **B82Y**: Specific uses of nanostructures
- **G06N**: Machine learning/AI
- **H01L**: Semiconductor devices
- **H04B**: Transmission systems
- **C12N**: Genetic engineering

---

*This document provides objective criteria for USPTO data collection and analysis relevant to OSINT research on technology development and international collaborations.*
