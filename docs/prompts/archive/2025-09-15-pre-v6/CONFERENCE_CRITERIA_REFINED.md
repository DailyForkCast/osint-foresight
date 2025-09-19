# Conference International Scale Criteria - Refined
## Targeted Approach for 44-Country Analysis

**Version:** 2.0
**Date:** 2025-09-14
**Purpose:** Nuanced criteria focusing on our 44 target countries with China weighting

---

## 🎯 Core Principle

**"A 3-country conference with US, Target Country, and China is MORE important than a 50-country conference without China."**

We care about:
- Conferences IN our 44 countries
- Conferences ATTENDED BY our 44 countries
- Especially when China is also present
- Even small specialized meetings if the right players are there

---

## 📊 REFINED INTERNATIONAL SCALE CRITERIA

### Tier 1: CRITICAL Events

```yaml
tier_1_critical:
  criteria_options:  # ANY of these qualify

    option_a_china_triangle:
      countries_minimum: 3
      required_presence:
        - target_country: true  # One of our 44
        - china: true
        - us_or_major_ally: true
      examples:
        - "US-Italy-China quantum workshop (3 countries but critical)"
        - "Netherlands-China-Taiwan semiconductor meeting (explosive mix)"
        - "Israel-China-US cybersecurity summit (small but sensitive)"

    option_b_regional_flagship:
      countries_minimum: 8
      requirements:
        - location: "In one of our 44 countries"
        - china_presence: "Confirmed delegation/sponsors"
        - sensitive_tech: true
      examples:
        - "European Quantum Conference in Vienna (12 countries inc. China)"
        - "Baltic Space Conference (8 countries, China observing)"

    option_c_specialized_high_risk:
      countries_minimum: 5
      requirements:
        - dual_use_focus: true
        - china_substantial: ">20% of participants OR major sponsor"
        - cutting_edge: "TRL 6-8 technologies"
      examples:
        - "Hypersonics Materials Workshop (5 countries, 30% Chinese)"
        - "Military AI Ethics Conference (6 countries, China co-sponsor)"

    option_d_standards_influence:
      countries_minimum: 4
      requirements:
        - standards_body: true
        - china_voting_member: true
        - affects_target_country: true
      examples:
        - "6G Standards Working Group (US, EU, China, Korea)"
        - "Quantum Encryption Standards (US, UK, China, Canada)"
```

### Tier 2: HIGH Priority Events

```yaml
tier_2_high:
  criteria_options:

    option_a_modest_international:
      countries_minimum: 8
      requirements:
        - no_china_confirmation: "But China attendance possible"
        - relevant_tech: true
        - target_country_strong: "Major presence"

    option_b_bilateral_plus:
      countries_minimum: 2
      requirements:
        - both_from_44: true
        - china_interest_documented: "Known collection priority"
        - sensitive_domain: true
      examples:
        - "France-Germany quantum computing summit"
        - "Japan-Australia rare earths conference"

    option_c_regional_specialized:
      countries_minimum: 5
      requirements:
        - regional_focus: "EU, NATO, Five Eyes, etc."
        - china_observers: "Even if not official"
        - emerging_tech: true
```

### Tier 3: MEDIUM Priority Events

```yaml
tier_3_medium:
  criteria:
    - countries_minimum: 3
    - requirements:
        - established_tech: "TRL 9"
        - limited_china_interest: "No significant presence"
        - academic_focus: "Not industry-heavy"
```

---

## 🌍 44-COUNTRY FOCUS ADJUSTMENTS

### Our Target Countries (For Reference)
```yaml
target_44_countries:
  five_eyes: ["USA", "UK", "Canada", "Australia", "New Zealand"]

  europe_nato:
    - Western: ["France", "Germany", "Italy", "Spain", "Netherlands", "Belgium"]
    - Nordic: ["Norway", "Sweden", "Finland", "Denmark", "Iceland"]
    - Central: ["Poland", "Czechia", "Hungary", "Slovakia", "Romania", "Bulgaria"]
    - Baltic: ["Estonia", "Latvia", "Lithuania"]
    - Other: ["Portugal", "Greece", "Turkey", "Luxembourg"]

  europe_non_nato: ["Austria", "Switzerland", "Ireland"]

  asia_pacific: ["Japan", "South Korea", "Taiwan", "Singapore", "India", "Malaysia", "Thailand", "Philippines", "Indonesia", "Vietnam"]

  middle_east: ["Israel", "UAE", "Saudi Arabia"]

  americas: ["Mexico", "Brazil", "Chile"]
```

### Geographic Weighting

```python
def calculate_conference_priority(event):
    """
    Refined scoring based on 44-country focus
    """

    # Base score from country participation
    if event.location in target_44_countries:
        location_score = 2.0
    else:
        location_score = 1.0

    # Count relevant countries
    relevant_countries = 0
    china_present = False
    us_present = False

    for country in event.participating_countries:
        if country in target_44_countries:
            relevant_countries += 1
        if country == "China":
            china_present = True
        if country == "USA":
            us_present = True

    # Apply refined criteria
    if china_present:
        if relevant_countries >= 2:  # China + 2 from our 44
            return "TIER_1_CRITICAL"
        elif relevant_countries >= 1:  # China + 1 from our 44
            return "TIER_2_HIGH"

    if relevant_countries >= 8:
        return "TIER_1_CRITICAL"
    elif relevant_countries >= 5:
        return "TIER_2_HIGH"
    elif relevant_countries >= 3:
        return "TIER_3_MEDIUM"
    else:
        return "TIER_4_LOW"
```

---

## 🚨 SPECIAL CASES & EXCEPTIONS

### Small But Critical

```yaml
upgrade_to_critical:

  trilateral_tensions:
    description: "Any 3-country meeting with specific combinations"
    examples:
      - "Taiwan-Netherlands-China (semiconductor tensions)"
      - "Ukraine-Turkey-China (drone technology)"
      - "Israel-UAE-China (surveillance tech)"

  closed_door_workshops:
    description: "Small, invitation-only with right mix"
    indicators:
      - "No public registration"
      - "Government or corporate hosted"
      - "China sends senior delegation"
    example: "Quantum encryption workshop - 4 countries, by invitation"

  standards_critical_mass:
    description: "Few countries but control standards"
    example: "US-China-Korea-Japan 6G meeting (4 countries, 80% of patents)"
```

### Large But Less Important

```yaml
downgrade_despite_size:

  trade_shows:
    description: "Large attendance but mostly commercial"
    unless: "Specific dual-use exhibits"

  academic_theory:
    description: "Many countries but far from application"
    unless: "China sending implementation teams"

  legacy_tech:
    description: "International but mature technology"
    unless: "China seeking specific capabilities"
```

---

## 📈 CHINA PRESENCE MULTIPLIERS

### When China Presence Changes Everything

```python
def apply_china_multiplier(event):
    """
    China presence dramatically changes importance
    """

    china_indicators = {
        "official_delegation": 3.0,  # Government-led
        "platinum_sponsor": 2.5,     # Major financial commitment
        "keynote_speaker": 2.0,      # Influence position
        "track_chair": 2.0,          # Controls content
        "10+_papers": 1.8,           # Significant research presence
        "exhibitor": 1.5,            # Commercial presence
        "attendee_only": 1.2         # Minimal but present
    }

    # Find highest level of China engagement
    max_multiplier = 1.0
    for indicator, multiplier in china_indicators.items():
        if event.has_indicator(indicator):
            max_multiplier = max(max_multiplier, multiplier)

    # Apply to base score
    if event.country_count < 8:
        # Small conferences get bigger boost from China
        return event.base_score * max_multiplier * 1.5
    else:
        return event.base_score * max_multiplier
```

---

## 🎯 PRACTICAL EXAMPLES

### Tier 1 Despite Small Size

```yaml
examples_small_but_critical:

  - event: "Advanced Semiconductor Metrology Workshop"
    countries: 4  # Netherlands, US, Taiwan, China
    why_critical: "ASML, TSMC, and Chinese participants together"

  - event: "Arctic Dual-Use Technology Symposium"
    countries: 5  # Norway, Canada, US, Russia, China
    why_critical: "Military implications, rare access"

  - event: "Quantum Communications Standards"
    countries: 3  # US, EU (as entity), China
    why_critical: "Will determine encryption future"
```

### Not Tier 1 Despite Large Size

```yaml
examples_large_but_lower:

  - event: "World Renewable Energy Congress"
    countries: 45
    why_not_critical: "No China focus on our sensitive areas"

  - event: "International Manufacturing Expo"
    countries: 30
    why_not_critical: "Mostly commercial, mature tech"
```

---

## 📊 COLLECTION PRIORITIES BY SCALE

### For Small International (3-7 countries)
```yaml
collection_focus:
  - identify: "Why these specific countries"
  - verify: "China's specific interest"
  - track: "Bilateral side meetings"
  - monitor: "Follow-on collaboration"
```

### For Medium International (8-15 countries)
```yaml
collection_focus:
  - map: "Which of our 44 attending"
  - assess: "China's delegation composition"
  - document: "Technology focus areas"
  - analyze: "Network formation"
```

### For Large International (16+ countries)
```yaml
collection_focus:
  - filter: "Relevant sessions only"
  - target: "China + our 44 interactions"
  - prioritize: "Dual-use content"
  - efficiency: "Don't collect everything"
```

---

## ✅ REVISED CLASSIFICATION MATRIX

```python
def classify_conference_refined(event):
    """
    Refined classification for 44-country focus
    """

    # Quick paths to Tier 1
    if event.has_china and event.country_count >= 3:
        if event.has_target_country and event.has_us:
            return "TIER_1_CRITICAL"  # Triangle complete

    if event.in_target_country and event.has_china:
        if event.sensitive_tech:
            return "TIER_1_CRITICAL"  # In our territory

    # Standard evaluation
    relevant_countries = count_44_countries(event)

    if event.has_china:
        threshold = 3  # Lower bar with China
    else:
        threshold = 8  # Higher bar without

    if relevant_countries >= threshold:
        return "TIER_1_CRITICAL"
    elif relevant_countries >= threshold * 0.6:
        return "TIER_2_HIGH"
    else:
        return "TIER_3_MEDIUM"
```

---

## REMEMBER

**Small + China + Target Country = Critical**

**Location matters: IN our 44 countries gets priority**

**China presence is a force multiplier, not a requirement**

**3 countries with the right mix > 30 countries without**

**Focus on quality of interaction, not quantity of attendance**
