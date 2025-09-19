# Conference Data Collection Template
## Structured Format for Event Intelligence 2020-2030

**Version:** 1.1
**Date:** 2025-09-14
**Purpose:** Standardized data collection for international tech events
**Temporal Coverage:** Historical (2020-2024), Current (2025), Future (2026-2030)

---

## 📊 JSON SCHEMA FOR CONFERENCE DATA

```json
{
  "schema_version": "1.0",
  "event_record": {
    "event_id": "UUID",
    "basic_information": {
      "name": "Full event name",
      "acronym": "Short name/acronym",
      "series": "Annual/Biennial/One-time",
      "iteration": "e.g., 37th Annual",
      "dates": {
        "start": "YYYY-MM-DD",
        "end": "YYYY-MM-DD",
        "workshops": "Pre/post conference dates",
        "virtual_available": "YYYY-MM-DD to YYYY-MM-DD"
      },
      "location": {
        "venue": "Convention center/hotel name",
        "city": "City name",
        "country": "Country",
        "online_component": true/false,
        "hybrid_format": true/false
      },
      "size": {
        "expected_attendance": 0,
        "actual_attendance": 0,
        "countries_represented": 0,
        "exhibitors": 0,
        "speakers": 0,
        "papers_presented": 0
      },
      "website": "https://...",
      "archived_years": ["2020", "2021", "2022", "2023", "2024"]
    },

    "organizers": {
      "primary_organizer": {
        "name": "Organization name",
        "type": "Industry/Academic/Government/NGO",
        "country": "HQ country",
        "website": "https://..."
      },
      "co_organizers": [
        {
          "name": "",
          "type": "",
          "country": ""
        }
      ],
      "committees": {
        "program_chair": {
          "name": "Person name",
          "affiliation": "Organization",
          "country": "Country",
          "clearance_suspected": true/false
        },
        "steering_committee": [
          {
            "name": "",
            "affiliation": "",
            "country": "",
            "note": "Former DARPA PM, etc."
          }
        ]
      }
    },

    "technology_focus": {
      "primary_domain": "Space/AI/Quantum/Defense/etc",
      "technical_tracks": [
        "Track name and description"
      ],
      "sensitive_topics": [
        {
          "topic": "Hypersonic materials",
          "sessions": 3,
          "risk_level": "CRITICAL",
          "dual_use": true
        }
      ],
      "workshops": [
        {
          "title": "Workshop name",
          "hands_on": true/false,
          "materials_provided": "Code/Data/Hardware",
          "export_controlled": true/false
        }
      ],
      "demonstrations": [
        {
          "technology": "What's being demoed",
          "company": "Who's demoing",
          "classification": "Public/Restricted",
          "recording_allowed": true/false
        }
      ]
    },

    "participants": {
      "keynote_speakers": [
        {
          "name": "Speaker name",
          "title": "Professional title",
          "organization": "Affiliation",
          "country": "Country",
          "topic": "Presentation topic",
          "sensitivity": "LOW/MEDIUM/HIGH/CRITICAL",
          "chinese_connections": "Known connections if any"
        }
      ],
      "sponsors": {
        "platinum": [
          {
            "company": "Company name",
            "country": "HQ country",
            "amount": "$X if known",
            "booth_size": "Square meters",
            "chinese_investment": true/false
          }
        ],
        "gold": [],
        "silver": [],
        "bronze": [],
        "exhibitors": [
          {
            "company": "",
            "products_displayed": [],
            "live_demos": true/false,
            "recruitment": true/false
          }
        ]
      },
      "attendee_analysis": {
        "total": 0,
        "by_country": {
          "USA": 0,
          "China": 0,
          "Russia": 0,
          "Iran": 0,
          "Others": {}
        },
        "by_sector": {
          "industry": 0,
          "academia": 0,
          "government": 0,
          "military": 0,
          "venture_capital": 0
        },
        "notable_organizations": [
          {
            "name": "Organization",
            "country": "Country",
            "attendee_count": 0,
            "concern_level": "LOW/MEDIUM/HIGH",
            "reason": "Why concerning"
          }
        ]
      }
    },

    "china_presence": {
      "overall_assessment": "MINIMAL/MODERATE/SIGNIFICANT/HEAVY",
      "official_delegation": {
        "present": true/false,
        "size": 0,
        "leader": "Name and title",
        "organizations": []
      },
      "companies": [
        {
          "name": "Company name",
          "type": "SOE/Private/Military-linked",
          "representatives": 0,
          "booth": true/false,
          "sponsorship_level": "Level or none",
          "recruitment": true/false
        }
      ],
      "universities": [
        {
          "name": "University name",
          "attendees": 0,
          "papers": 0,
          "seven_sons": true/false,
          "military_civil_fusion": true/false
        }
      ],
      "individuals_of_concern": [
        {
          "name": "If known",
          "affiliation": "Organization",
          "role": "Researcher/Executive/Intelligence",
          "previous_incidents": "Description",
          "collection_methods": "Observed behaviors"
        }
      ],
      "paper_statistics": {
        "total_chinese_papers": 0,
        "percentage_of_conference": 0,
        "top_topics": [],
        "collaboration_papers": 0,
        "us_china_joint": 0
      }
    },

    "us_presence": {
      "government_agencies": [
        {
          "agency": "DOD/DOE/NASA/DARPA/etc",
          "representatives": 0,
          "official_capacity": true/false,
          "presentations": 0,
          "recruitment": true/false
        }
      ],
      "defense_contractors": [
        {
          "company": "Company name",
          "representatives": 0,
          "cleared_personnel": "Likely number",
          "technologies_discussed": [],
          "export_controlled": true/false
        }
      ],
      "universities": [
        {
          "name": "University",
          "researchers": 0,
          "students": 0,
          "sensitive_research": [],
          "federal_funding": true/false
        }
      ],
      "startups": [
        {
          "name": "Startup name",
          "technology": "What they do",
          "funding_stage": "Seed/A/B/C",
          "investors": [],
          "dual_use": true/false
        }
      ]
    },

    "intelligence_concerns": {
      "tech_transfer_risk": "LOW/MEDIUM/HIGH/CRITICAL",
      "specific_risks": [
        {
          "risk_type": "Algorithm disclosure/Hardware specs/Process details",
          "mechanism": "Presentation/Demo/Conversation",
          "likelihood": "UNLIKELY/POSSIBLE/LIKELY/CERTAIN",
          "impact": "Description of potential impact"
        }
      ],
      "collection_indicators": [
        {
          "indicator": "Systematic poster photography",
          "observed": true/false,
          "date": "When observed",
          "actors": "Who was doing it"
        }
      ],
      "recruitment_activity": [
        {
          "target_profile": "AI researchers/Engineers/etc",
          "approaching_entities": [],
          "methods": "Job fairs/Direct approach/LinkedIn",
          "packages_offered": "3x salary, etc."
        }
      ],
      "follow_up_risks": [
        "Lab visit requests expected",
        "Collaboration proposals likely",
        "Funding offers anticipated"
      ]
    },

    "historical_incidents": [
      {
        "year": "YYYY",
        "incident": "Description",
        "actors": "Who was involved",
        "outcome": "What happened",
        "mitigation": "Response if any"
      }
    ],

    "proceedings_and_materials": {
      "proceedings_published": true/false,
      "access_level": "Open/Paywall/Restricted",
      "url": "Where to find",
      "videos_available": true/false,
      "slides_distributed": true/false,
      "code_repositories": [],
      "datasets_shared": [],
      "export_control_review": true/false
    },

    "social_and_networking": {
      "official_app": "App name if exists",
      "attendee_list_available": true/false,
      "networking_events": [
        {
          "type": "Reception/Dinner/Breakfast",
          "sponsor": "Who pays",
          "invitation_only": true/false,
          "significance": "Why it matters"
        }
      ],
      "side_meetings": [
        {
          "type": "Bilateral/Consortium/Standards",
          "participants": [],
          "topics": [],
          "outcomes": []
        }
      ]
    },

    "future_iterations": {
      "confirmed_future": {  // 2025-2027
        "2025": {
          "dates": "YYYY-MM-DD",
          "location": "City, Country",
          "registration_open": "YYYY-MM-DD",
          "status": "CONFIRMED/TENTATIVE"
        },
        "2026": {
          "dates": "YYYY-MM-DD or Q1/Q2/Q3/Q4",
          "location": "City, Country or TBD",
          "confidence": "HIGH/MEDIUM/LOW"
        },
        "2027": {
          "dates": "Estimated period",
          "location": "Likely city based on rotation",
          "confidence": "Pattern-based prediction"
        }
      },
      "projected_future": {  // 2028-2030
        "2028": {
          "likelihood": "CERTAIN/PROBABLE/POSSIBLE",
          "basis": "Annual pattern/Technology maturation",
          "notes": "Reasoning for projection"
        },
        "2029": {
          "likelihood": "PROBABLE/POSSIBLE/SPECULATIVE",
          "basis": "Historical pattern/Industry roadmap",
          "notes": "Key assumptions"
        },
        "2030": {
          "likelihood": "POSSIBLE/SPECULATIVE",
          "basis": "Long-term planning/Technology prediction",
          "notes": "Major uncertainties"
        }
      },
      "monitoring_requirements": [
        "Track registration numbers",
        "Monitor speaker announcements",
        "Watch for Chinese delegation size",
        "Check sponsor changes",
        "Venue booking confirmations",
        "Organizing committee formation",
        "Multi-year sponsor agreements"
      ]
    },

    "assessment": {
      "overall_risk": "LOW/MEDIUM/HIGH/CRITICAL",
      "value_for_china": "Technology access value 1-10",
      "us_vulnerability": "Exposure level 1-10",
      "mitigation_effectiveness": "Current measures 1-10",
      "priority_for_monitoring": "LOW/MEDIUM/HIGH/URGENT",
      "key_findings": [
        "Main takeaway 1",
        "Main takeaway 2",
        "Main takeaway 3"
      ],
      "recommendations": [
        "Suggested action 1",
        "Suggested action 2"
      ]
    },

    "data_sources": [
      {
        "type": "Website/Report/Interview/OSINT",
        "source": "Specific source",
        "date_accessed": "YYYY-MM-DD",
        "reliability": "A-F rating",
        "notes": "Any caveats"
      }
    ],

    "metadata": {
      "record_created": "YYYY-MM-DD",
      "last_updated": "YYYY-MM-DD",
      "analyst": "Analyst ID",
      "version": "1.0",
      "classification": "UNCLASSIFIED",
      "handling": "TLP:WHITE"
    }
  }
}
```

---

## 📋 PRIORITY CONFERENCES TO TRACK

### Must-Track Events (2024-2030)

#### Space Technology
```yaml
High_Priority:
  - name: International Astronautical Congress (IAC)
    historical:
      2020: "Virtual (COVID)"
      2021: "Dubai, UAE"
      2022: "Paris, France"
      2023: "Baku, Azerbaijan"
      2024: "Milan, Italy"
    future:
      2025: "Sydney, Australia (confirmed)"
      2026: "TBD (likely Europe)"
      2027: "TBD (likely Americas)"
      2028: "Pattern suggests Asia"
      2029: "Pattern suggests Middle East"
      2030: "Major city, 80th anniversary"
    why: "All space powers attend"

  - name: Space Symposium
    pattern: "Annual - April - Colorado Springs"
    projection: "Continues through 2030"
    china_risk: "Increasing delegation size"

  - name: Satellite Conference
    pattern: "Annual - March - Washington DC"
    projection: "Continues through 2030"
    evolution: "More focus on LEO constellations"

  - name: SmallSat Conference
    pattern: "Annual - August - Utah"
    projection: "Continues through 2030"
    emerging: "Tactical military applications growing"
```

#### AI/ML Technology
```yaml
Critical_Events:
  - name: NeurIPS 2024
    next: "December 2024 - Vancouver"
    china_papers: "~30% of submissions"

  - name: CVPR 2024
    next: "June 2024 - Seattle"
    risk: "Computer vision for targeting"

  - name: ICML 2024
    next: "July 2024 - Vienna"
    concern: "Algorithm details shared"
```

#### Quantum Technology
```yaml
Quantum_Events:
  - name: QIP 2025
    next: "January 2025 - Location TBD"

  - name: Quantum.Tech Boston
    next: "April 2025 - Boston"

  - name: Quantum World Congress
    next: "September 2024 - Washington DC"
```

#### Defense Technology
```yaml
Defense_Shows:
  - name: Paris Air Show
    next: "June 16-22, 2025 - Le Bourget"

  - name: DSEI London
    next: "September 2025 - London"

  - name: AUSA Annual
    next: "October 2024 - Washington DC"
```

---

## 🔍 COLLECTION METHODOLOGY

### Primary Sources
1. **Conference Websites**
   - Registration data
   - Program schedules
   - Speaker lists
   - Sponsor information

2. **Social Media**
   - LinkedIn event pages
   - Twitter hashtags
   - WeChat groups (if accessible)
   - Conference apps

3. **Industry Reports**
   - Post-event summaries
   - Attendance statistics
   - Technology highlights

### Secondary Sources
1. **News Coverage**
   - Tech media reports
   - Trade publications
   - Local news (for economic impact)

2. **Participant Reports**
   - University trip reports
   - Government travel records
   - Company announcements

3. **Academic Sources**
   - Proceedings analysis
   - Citation tracking
   - Collaboration patterns

---

## 📊 AUTOMATED TRACKING

### Web Scraping Targets
```python
conference_sources = {
    "aggregators": [
        "https://www.conference-service.com",
        "https://www.allconferences.com",
        "https://conferencealerts.com"
    ],
    "sector_specific": {
        "space": [
            "https://www.spaceindustry.com/events",
            "https://spacenews.com/events"
        ],
        "ai_ml": [
            "https://www.ml-conferences.com",
            "https://neurips.cc",
            "https://cvpr.org"
        ],
        "defense": [
            "https://www.defense-exhibitions.com",
            "https://www.janes.com/events"
        ]
    },
    "registration_platforms": [
        "eventbrite.com",
        "cvent.com",
        "regonline.com"
    ]
}
```

### Alert Configuration
```python
monitoring_alerts = {
    "keywords": [
        "[Conference Name] + China",
        "[Conference Name] + delegation",
        "[Conference Name] + sponsors",
        "[Conference Name] + program"
    ],
    "timing": {
        "T-6months": "Registration opens",
        "T-3months": "Program published",
        "T-1month": "Final attendee push",
        "T+1week": "Post-event reports"
    }
}
```

---

## ✅ INTEGRATION WITH PHASES

### Phase 0: Scoping
- Identify sector-relevant conferences
- Map historical participation
- Flag upcoming events

### Phase 3: Technology Landscape
- Which companies attend which events?
- Technology demonstrations planned
- Speaking slots and topics

### Phase 5: Institutions
- University conference participation
- Research presentations
- Student attendance

### Phase 7: International Links
- Joint delegation patterns
- Bilateral meetings at events
- MOU signings

### Phase 8: Risk Assessment
- Conference as tech transfer vector
- Specific vulnerabilities exposed
- Mitigation recommendations

---

## REMEMBER

**Every major conference is an intelligence collection opportunity.**

**Track patterns across multiple events, not just single conferences.**

**The attendee list is as valuable as the technical program.**

**Side events and social hours are where the real exchanges happen.**

**A conference badge is a license to collect.**
