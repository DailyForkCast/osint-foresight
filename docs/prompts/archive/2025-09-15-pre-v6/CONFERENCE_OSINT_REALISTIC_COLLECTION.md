# Conference OSINT Realistic Collection Framework
## What We Can Actually Find in Open Sources

**Version:** 1.0
**Date:** 2025-09-14
**Purpose:** Focus on collectible open-source conference intelligence

---

## 🎯 Reality Check

**"We can't see the hotel bar deals, but we CAN see who was in the same city at the same time."**

Open source won't show us credential harvesting or poaching attempts, but it WILL show us the opportunity structure that enables them.

---

## 📊 ACTUALLY COLLECTIBLE CONFERENCE DATA

### Level 1: Easily Available (Public)

```python
easily_collected = {
    "conference_basics": {
        "dates_location": "Conference website",
        "registration_fees": "Published rates",
        "agenda_program": "Session schedules",
        "keynote_speakers": "Names and bios",
        "sponsor_list": "Logos and tiers",
        "exhibitor_list": "Company booths"
    },

    "documented_attendance": {
        "press_releases": "Company X attending/sponsoring",
        "linkedin_posts": "Excited to speak at...",
        "twitter_photos": "Great panel at #Conference2024",
        "company_blogs": "Our team at Conference",
        "university_news": "Professor presents at..."
    },

    "content_artifacts": {
        "presentation_titles": "Program listings",
        "abstract_books": "Published abstracts",
        "author_lists": "Paper contributors",
        "poster_titles": "Session listings",
        "workshop_descriptions": "Training content"
    },

    "post_event_materials": {
        "proceedings": "IEEE, ACM, SPIE databases",
        "slide_decks": "SlideShare, conference sites",
        "videos": "YouTube, Vimeo recordings",
        "photos": "Official galleries",
        "attendee_testimonials": "Blog posts, LinkedIn"
    }
}
```

### Level 2: Findable with Effort

```python
requires_searching = {
    "attendance_patterns": {
        "repeat_attendees": "Cross-reference multiple years",
        "delegation_sizes": "Count LinkedIn posts/photos",
        "organization_presence": "Aggregate individual attendance",
        "travel_patterns": "Social media geotags"
    },

    "collaboration_indicators": {
        "co_authored_papers": "Multiple affiliations",
        "joint_presentations": "Shared speaking slots",
        "panel_compositions": "Who sat together",
        "workshop_instructors": "Teaching together"
    },

    "meeting_evidence": {
        "bilateral_announcements": "Side meeting press releases",
        "mou_signings": "Ceremony photos/news",
        "partnership_launches": "Timed announcements",
        "investment_deals": "Post-conference PRs"
    },

    "technology_reveals": {
        "demo_descriptions": "What was shown",
        "capability_claims": "Marketing materials",
        "roadmap_discussions": "Keynote content",
        "problem_statements": "Research challenges discussed"
    }
}
```

### Level 3: Inferrable from Patterns

```python
pattern_analysis = {
    "co_location_analysis": {
        "overlapping_attendance": "Same people, same events",
        "sequential_meetings": "Conference hopping patterns",
        "cluster_formation": "Groups traveling together"
    },

    "topic_evolution": {
        "session_growth": "AI sessions 2→5→12 over 3 years",
        "new_tracks": "Quantum track appears 2023",
        "speaker_shifts": "Academia → Industry speakers"
    },

    "competitive_dynamics": {
        "parallel_sessions": "China-focused vs US-focused",
        "competing_announcements": "Product launch timing",
        "talent_movement": "Speaker affiliation changes"
    },

    "investment_signals": {
        "sponsor_upgrades": "Silver → Gold → Platinum",
        "booth_sizes": "10sqm → 50sqm → 100sqm",
        "delegation_growth": "2 people → 10 people → 30 people"
    }
}
```

---

## 🔍 REALISTIC CHINA INDICATORS (Open Source)

### What We CAN Collect:

```json
{
  "visible_indicators": {
    "attendance_metrics": {
      "chinese_authors": "Count on proceedings",
      "chinese_affiliations": "Speaker/author lists",
      "chinese_companies": "Sponsor/exhibitor lists",
      "chinese_delegations": "Group photos/news"
    },

    "content_analysis": {
      "paper_topics": "What China's presenting on",
      "question_patterns": "Q&A session recordings",
      "demo_participation": "What they're showing",
      "workshop_attendance": "Training registrations"
    },

    "relationship_mapping": {
      "co_authorships": "Joint papers",
      "panel_participation": "Shared platforms",
      "sponsor_patterns": "Who China sponsors with",
      "sequential_attendance": "Conference paths"
    },

    "temporal_patterns": {
      "first_appearance": "When China entered domain",
      "growth_rate": "Delegation size over time",
      "topic_evolution": "Changing focus areas",
      "geographic_expansion": "New conference participation"
    }
  }
}
```

### What We CANNOT Collect (But Can Infer):

```json
{
  "invisible_but_inferrable": {
    "targeting": {
      "cannot_see": "Who they approached",
      "can_see": "Who changed jobs after",
      "inference": "Recruitment likely"
    },

    "collection": {
      "cannot_see": "What they photographed",
      "can_see": "Systematic attendance patterns",
      "inference": "Collection priority"
    },

    "relationships": {
      "cannot_see": "Private meetings",
      "can_see": "Joint papers 6 months later",
      "inference": "Collaboration initiated"
    },

    "technology_transfer": {
      "cannot_see": "Hallway conversations",
      "can_see": "Similar technology appears in China",
      "inference": "Knowledge transfer occurred"
    }
  }
}
```

---

## 📋 PRACTICAL COLLECTION CHECKLIST

### Pre-Conference (T-30 days)

```markdown
## Registration & Attendance
- [ ] Download attendee list (if available)
- [ ] Screenshot sponsor page
- [ ] Save speaker biographies
- [ ] Archive program PDF
- [ ] Note Chinese organizations registered

## Social Media Monitoring
- [ ] Set up hashtag tracking
- [ ] Monitor LinkedIn for "attending" posts
- [ ] Track organizer Twitter
- [ ] Set Google Alerts for conference name
- [ ] Monitor WeChat (if accessible)
```

### During Conference

```markdown
## Real-Time Collection
- [ ] Monitor Twitter/LinkedIn for live posts
- [ ] Capture keynote announcements
- [ ] Document partnership announcements
- [ ] Track press releases
- [ ] Screenshot virtual platform attendee lists

## Content Capture
- [ ] Download available presentations
- [ ] Save YouTube livestream links
- [ ] Capture session recordings
- [ ] Archive chat transcripts (virtual)
- [ ] Document Q&A sessions
```

### Post-Conference

```markdown
## Artifact Collection
- [ ] Download proceedings when published
- [ ] Collect slide decks from SlideShare
- [ ] Archive photo galleries
- [ ] Save attendee testimonials
- [ ] Document post-event reports

## Analysis Products
- [ ] Map collaboration networks
- [ ] Track job changes (3-6 months)
- [ ] Monitor follow-up publications
- [ ] Document new partnerships
- [ ] Track technology emergence
```

---

## 🎯 OPEN SOURCE GOLDMINES

### Best Sources for Conference Intel:

#### 1. **LinkedIn**
```python
linkedin_collection = {
    "rich_data": [
        "Attending Conference X posts",
        "Speaking at Conference Y announcements",
        "Panel photos with names/affiliations",
        "Great to meet [Person] at [Conference]",
        "Job changes post-conference"
    ],
    "search_queries": [
        '"Conference Name" attending',
        '"Conference Name" speaking',
        '"Conference Name" China',
        'site:linkedin.com "Conference Name" Beijing'
    ]
}
```

#### 2. **Conference Websites**
```python
official_sources = {
    "archived_data": [
        "2020-2024 programs (PDFs)",
        "Historical sponsor lists",
        "Past speaker rosters",
        "Proceedings archives"
    ],
    "current_data": [
        "Registration lists (sometimes)",
        "Program committees",
        "Confirmed speakers",
        "Sponsor tiers"
    ]
}
```

#### 3. **Twitter/X**
```python
twitter_mining = {
    "hashtags": [
        "#ConferenceName2024",
        "#ConferenceAcronym24"
    ],
    "photo_analysis": [
        "Delegation group photos",
        "Panel compositions",
        "Booth staffing",
        "Badge photos (names/affiliations)"
    ]
}
```

#### 4. **Academic Databases**
```python
academic_sources = {
    "proceedings": [
        "IEEE Xplore",
        "ACM Digital Library",
        "SPIE Digital Library",
        "ArXiv (pre-prints)"
    ],
    "valuable_data": [
        "Author affiliations",
        "Funding acknowledgments",
        "Collaboration patterns",
        "Topic clustering"
    ]
}
```

#### 5. **Company Announcements**
```python
corporate_sources = {
    "press_releases": [
        "Attending/sponsoring announcements",
        "Product launches at conference",
        "Partnership announcements",
        "Award wins"
    ],
    "blogs": [
        "Conference summaries",
        "Key takeaways posts",
        "Team photos",
        "Technology demonstrations"
    ]
}
```

---

## 📊 ANALYSIS TEMPLATES

### Chinese Presence Assessment (From Open Sources)

```json
{
  "conference": "SPIE Photonics West 2024",
  "chinese_footprint": {
    "quantitative": {
      "papers": 89,
      "authors": 234,
      "organizations": 47,
      "sponsors": 3,
      "exhibitors": 12
    },
    "qualitative": {
      "paper_topics": [
        "Quantum dots (15 papers)",
        "Photonic chips (23 papers)",
        "LIDAR (8 papers)"
      ],
      "key_organizations": [
        "Chinese Academy of Sciences (31 papers)",
        "Tsinghua University (18 papers)",
        "Huawei (Platinum sponsor)"
      ],
      "collaboration_patterns": [
        "12 papers with US co-authors",
        "5 papers with European partners"
      ]
    },
    "temporal_analysis": {
      "vs_2023": "+34% papers",
      "vs_2022": "+67% papers",
      "trend": "Accelerating presence"
    },
    "areas_of_focus": {
      "primary": "Photonic integrated circuits",
      "secondary": "Quantum optics",
      "emerging": "Neuromorphic photonics"
    }
  }
}
```

### Technology Disclosure Tracking

```json
{
  "conference": "NeurIPS 2024",
  "technology_reveals": {
    "from_papers": [
      {
        "title": "Scalable Transformer Architecture",
        "authors": "MIT + Beijing Institute",
        "key_disclosure": "Training efficiency improvement 10x",
        "dual_use_potential": "Drone swarm coordination"
      }
    ],
    "from_demos": [
      {
        "company": "Startup X",
        "technology": "Edge AI processor",
        "performance_claimed": "1 TOPS/watt",
        "china_interest": "3 Chinese VCs attended demo"
      }
    ],
    "from_talks": [
      {
        "speaker": "DARPA PM",
        "topic": "AI Assurance",
        "disclosure": "Current challenges in verification",
        "value_to_adversary": "Reveals US capability gaps"
      }
    ]
  }
}
```

---

## 💡 REALISTIC INTELLIGENCE PRODUCTS

### What We Can Produce from Open Sources:

1. **Chinese Organization Conference Footprint**
   - Which Chinese entities attend which conferences
   - Paper submission patterns
   - Sponsorship trends
   - Collaboration networks

2. **Technology Emergence Tracking**
   - New topics appearing in programs
   - Shift from academic to commercial
   - Geographic spread of capabilities

3. **Relationship Mapping**
   - Co-authorship networks
   - Panel participation patterns
   - Sponsor relationships
   - Sequential conference attendance

4. **Temporal Analysis**
   - Conference growth patterns
   - Topic evolution
   - Speaker affiliation changes
   - Sponsor progression

5. **Risk Indicators**
   - Dual-use technology presentations
   - Military-civil fusion participants
   - Sensitive topic clustering
   - Strategic technology focus

---

## ✅ ACTIONABLE COLLECTION PLAN

### For Each Target Conference:

```python
def collect_conference_osint(conference_name, year):
    """
    Realistic open source collection plan
    """

    collection_tasks = {
        "immediate": {
            "website_archive": "Full site crawl",
            "program_pdf": "Download and parse",
            "speaker_list": "Extract names/affiliations",
            "sponsor_page": "Screenshot and document"
        },

        "social_media": {
            "linkedin": f'"{conference_name}" AND (China OR Beijing OR Shanghai)',
            "twitter": f"#{conference_name}{year} lang:en OR lang:zh",
            "youtube": f'"{conference_name}" {year} keynote OR panel'
        },

        "proceedings": {
            "database": "Identify where published",
            "chinese_papers": "Count and categorize",
            "collaboration": "Map joint authorship",
            "topics": "Cluster by subject"
        },

        "analysis": {
            "attendance_size": "Estimate from social media",
            "chinese_percentage": "Calculate from authors",
            "technology_focus": "Identify from abstracts",
            "relationship_patterns": "Map from co-appearance"
        },

        "products": {
            "summary_report": "Chinese presence assessment",
            "technology_tracker": "Sensitive disclosures",
            "relationship_map": "Collaboration network",
            "trend_analysis": "Multi-year patterns"
        }
    }

    return collection_tasks
```

---

## REMEMBER

**We can't see the espionage, but we can see the opportunity structure.**

**Open source shows who was where, when, and discussing what.**

**Pattern analysis reveals priorities even without seeing collection.**

**Today's co-author is tomorrow's technology transfer channel.**

**The absence of open source may itself be an indicator.**
