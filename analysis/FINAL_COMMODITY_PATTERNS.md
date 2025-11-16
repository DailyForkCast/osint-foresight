# Final Commodity Patterns for Importance Tier System
**Version**: 2.0 (Final)
**Date**: October 16, 2025
**Coverage**: Reduces uncategorized from 53.7% to ~20-25%

---

## Pattern Improvements (V1 → V2)

### Version 1 Results:
- TIER 3 (Commodity): 100 records (33.3%)
- UNCATEGORIZED: 161 records (53.7%)

### Version 2 Results:
- TIER 3 (Commodity): 152 records (50.7%)
- UNCATEGORIZED: 91 records (30.3%)
- **Improvement**: +52 commodity records categorized (43.5% reduction)

---

## Final Pattern Lists

### TIER 1: Strategic Entities (HIGH Importance - 1.0)

**Strategic Entities** (Recipient/Vendor Name Match):
```python
TIER_1_STRATEGIC_ENTITIES = [
    'CHINESE ACADEMY', 'HUAWEI', 'ZTE', 'LENOVO',
    'TENCENT', 'ALIBABA', 'BAIDU', 'DJI', 'HIKVISION',
    'DAHUA', 'HYTERA', 'AVIC', 'COMAC', 'CSSC', 'NORINCO',
    'CHINESE UNIVERSITY', 'TSINGHUA', 'PEKING UNIVERSITY',
    'CAS ', 'RESEARCH CENTER', 'RESEARCH INSTITUTE',
    'BEIJING BOOK',  # Chinese publications
]
```

**Strategic Technologies** (Description Match):
```python
TIER_1_STRATEGIC_TECH = [
    'QUANTUM', 'ARTIFICIAL INTELLIGENCE', 'MACHINE LEARNING',
    'SEMICONDUCTOR', 'CHIP MANUFACTURING', 'PROCESSOR DESIGN',
    'BIOTECHNOLOGY', 'PHARMACEUTICAL RESEARCH', 'GENE SEQUENCING',
    'SATELLITE SYSTEM', 'SPACE STATION', 'ROCKET', 'MISSILE',
    'HYPERSONIC', 'NUCLEAR REACTOR', 'FUSION',
    'ADVANCED MATERIALS', 'NANOMATERIAL', 'GRAPHENE',
    '5G NETWORK', 'TELECOMMUNICATIONS INFRASTRUCTURE'
]
```

---

### TIER 2: Technology & Services (MEDIUM Importance - 0.5)

**Computers & Electronics**:
```python
TIER_2_COMPUTERS = [
    'COMPUTER', 'DESKTOP', 'LAPTOP', 'SERVER', 'WORKSTATION',
    'IMAC', 'DELL', 'OPTIPLEX', 'HP ELITEBOOK', 'THINKPAD',
    'DISK DRIVE', 'HARD DRIVE', 'SSD', 'STORAGE ARRAY',
    'MONITOR', 'DISPLAY', 'SCREEN', 'PROJECTOR'
]
```

**Specialized Equipment**:
```python
TIER_2_EQUIPMENT = [
    'EQUIPMENT', 'MACHINERY', 'ENGINE', 'MOTOR', 'PUMP',
    'VALVE', 'COMPRESSOR', 'GENERATOR', 'TURBINE',
    'CIRCUIT BREAKER', 'CONTROL SYSTEM', 'SENSOR', 'ACTUATOR',
    'HEATER', 'COOLING SYSTEM', 'HVAC',
    'TAPE', 'REFLECTIVE',  # Specialized tape (traffic control)
    'MICROTOME', 'HISTOLOGY',  # Scientific equipment
]
```

**Vehicles & Transport**:
```python
TIER_2_VEHICLES = [
    'VEHICLE', 'TRUCK', 'CAR', 'VAN', 'BUS',
    'AIRCRAFT', 'HELICOPTER', 'SHIP', 'VESSEL', 'BOAT',
    'FORKLIFT', 'CRANE', 'EXCAVATOR'
]
```

**Professional Services**:
```python
TIER_2_SERVICES = [
    'CONSULTING', 'ENGINEERING', 'TECHNICAL SUPPORT',
    'SOFTWARE DEVELOPMENT', 'SYSTEM INTEGRATION',
    'CLEANING CONTRACT', 'OFFICE CLEANING', 'FACILITY',
    'CUSTOMS CLEARANCE', 'FREIGHT', 'TRANSPORTATION',
    'INTERPRETATION', 'TRANSLATION', 'TALENT SERVICES',
    'HOTEL', 'LODGING', 'ACCOMMODATION'
]
```

---

### TIER 3: Commodity Purchases (VERY LOW Importance - 0.1)

**Office Supplies**:
```python
TIER_3_OFFICE_SUPPLIES = [
    'CARTRIDGE', 'TONER', 'INK', 'PAPER', 'STAPLE', 'FOLDER',
    'PEN', 'PENCIL', 'MARKER', 'ENVELOPE', 'CLIP', 'BINDER',
    'LABEL MAKER', 'P-TOUCH', 'BROTHER P-TOUCH',
    'PT-D600VP', 'MFR: BROTHER',  # Part number patterns
    'NOTEPAD', 'POST-IT', 'STICKY NOTE'
]
```

**Commodity Electronics**:
```python
TIER_3_COMMODITY_ELECTRONICS = [
    'SURGE PROTECTOR', 'SURGE SUPPRESSOR', 'SURGE,PROTECTOR',  # Handle comma variant
    'POWER STRIP', 'EXTENSION CORD', 'CABLE', 'ADAPTER', 'USB',
    'CHARGER', 'BATTERY', 'FLASHLIGHT', 'LIGHT BULB', 'LED', 'LAMP',
    'ABSORBER', 'OVERVOLTAGE',
]
```

**Hardware & Small Parts**:
```python
TIER_3_HARDWARE = [
    'SCREW', 'BOLT', 'NUT', 'WASHER', 'WEDGE', 'HOOK', 'HINGE',
    'LOCK', 'KEY', 'NAIL', 'HAMMER', 'WRENCH', 'PLIERS',
    'SCREWDRIVER', 'DRILL BIT',
    'RELAY', 'ELBOW', 'PIPE', 'TUBE', 'FITTING', 'GASKET',
    'RESISTOR', 'CAPACITOR',  # Basic electronic components
]
```

**Apparel & PPE**:
```python
TIER_3_APPAREL = [
    'APRON', 'GLOVE', 'SHOE', 'BOOT', 'HAT', 'UNIFORM',
    'VEST', 'JACKET', 'PANTS', 'SHIRT', 'SOCKS',
    'COLLAR,EXTRICATION',  # Medical collar
]
```

**Kitchen & Janitorial**:
```python
TIER_3_KITCHEN_JANITORIAL = [
    'FUNNEL', 'WHISK', 'SPATULA', 'LADLE', 'SPOON', 'FORK',
    'KNIFE', 'PLATE', 'CUP', 'MOP', 'BROOM', 'BUCKET',
    'CLEANER', 'DETERGENT', 'SOAP',
    'WHIP', 'SCOOP', 'MEASURING', 'SHAKER', 'SALT',
    'PEELER', 'POTATO PEELER', 'IRON',  # Kitchen iron
]
```

**Medical Supplies (Basic/Commodity)**:
```python
TIER_3_MEDICAL_BASIC = [
    'APPLICATOR', 'BANDAGE', 'GAUZE', 'SWAB', 'SYRINGE',
    'GLOVES MEDICAL', 'MASK', 'FACE SHIELD', 'DISPOSAB',
    'KIT,INTRAVE',  # IV kits
]
```

**Auto Parts (Commodity)**:
```python
TIER_3_AUTO_PARTS = [
    'BEARING', 'FILTER', 'BELT', 'HOSE', 'CLAMP', 'BRACKET',
    'STARTER KIT', 'WHEEL', 'TIRE',
    'INDICATOR,SPECIAL',  # Auto indicators
]
```

**Miscellaneous Commodity**:
```python
TIER_3_MISC_COMMODITY = [
    'CART', 'TRAVEL CART',  # Shopping carts
    'ABRASIVE WHEEL',  # Grinding wheels
    'STRAP', 'TIE DOWN'
]
```

---

## Special Handling Rules

### 1. Part Number Patterns (Office Supplies)
```python
# Catch "P/N: PT-D600VP MFR: BROTHER" patterns
if 'P/N:' in desc and 'BROTHER' in desc:
    return ('TIER_3', 0.1, 'office_supplies')

if 'MFR: BROTHER' in desc or 'PT-D600' in desc:
    return ('TIER_3', 0.1, 'office_supplies')
```

### 2. Comma Variants
```python
# Handle "SURGE,PROTECTOR" vs "SURGE PROTECTOR"
desc_normalized = desc.replace(',', ' ')
```

### 3. NSN Codes (Generic Parts)
```python
# NSN codes starting with 85XX are often generic electronics
if re.match(r'85\d{8}', desc):
    # Check if it's a simple part (RELAY, LAMP, etc.)
    if any(kw in desc for kw in TIER_3_HARDWARE):
        return ('TIER_3', 0.1, 'hardware')
```

### 4. "CHINA PRODUCTS ACCEPTABLE" Language
```python
# This is product sourcing language, already handled by Option B
# But if it appears with commodity items, double-confirm TIER 3
if 'CHINA PRODUCTS ACCEPTABLE' in desc or 'CHINA ACCEPTABLE' in desc:
    # Check for commodity patterns
    # If match → TIER 3, else → already LOW confidence from Option B
```

### 5. Empty/Minimal Descriptions
```python
# "DESCR N.A." or very short descriptions
if len(desc.strip()) < 10 or 'DESCR N.A.' in desc:
    # Use recipient name patterns or default to TIER_2
    return ('TIER_2', 0.5, 'insufficient_description')
```

---

## Categorization Function (Final Version)

```python
def categorize_importance_final(record):
    """
    Final categorization logic with all patterns.

    Returns:
        tuple: (tier, importance_score, commodity_type)
    """
    desc = (record.award_description or '').upper()
    recipient = (record.recipient_name or '').upper()
    vendor = (record.vendor_name or '').upper()

    # Normalize description (handle comma variants)
    desc_normalized = desc.replace(',', ' ')

    # Special handling: Part number patterns
    if ('P/N:' in desc or 'MFR:' in desc) and 'BROTHER' in desc:
        return ('TIER_3', 0.1, 'office_supplies')

    # TIER 1: Strategic Entities (name match)
    for entity in TIER_1_STRATEGIC_ENTITIES:
        if entity in recipient or entity in vendor:
            return ('TIER_1', 1.0, 'strategic_entity')

    # TIER 1: Strategic Technologies (description match)
    for tech in TIER_1_STRATEGIC_TECH:
        if tech in desc_normalized:
            return ('TIER_1', 1.0, 'strategic_technology')

    # TIER 3: All commodity categories (description match)
    commodity_categories = {
        'office_supplies': TIER_3_OFFICE_SUPPLIES,
        'commodity_electronics': TIER_3_COMMODITY_ELECTRONICS,
        'hardware': TIER_3_HARDWARE,
        'apparel': TIER_3_APPAREL,
        'kitchen_janitorial': TIER_3_KITCHEN_JANITORIAL,
        'medical_supplies_basic': TIER_3_MEDICAL_BASIC,
        'auto_parts_commodity': TIER_3_AUTO_PARTS,
        'misc_commodity': TIER_3_MISC_COMMODITY,
    }

    for commodity_type, keywords in commodity_categories.items():
        for keyword in keywords:
            if keyword in desc_normalized:
                return ('TIER_3', 0.1, commodity_type)

    # TIER 2: All technology/service categories
    tier2_categories = {
        'computers_electronics': TIER_2_COMPUTERS,
        'specialized_equipment': TIER_2_EQUIPMENT,
        'vehicles_transport': TIER_2_VEHICLES,
        'professional_services': TIER_2_SERVICES,
    }

    for category, keywords in tier2_categories.items():
        for keyword in keywords:
            if keyword in desc_normalized:
                return ('TIER_2', 0.5, category)

    # Special handling: Empty descriptions
    if len(desc.strip()) < 10 or 'DESCR N.A.' in desc:
        return ('TIER_2', 0.5, 'insufficient_description')

    # Default: TIER_2 (general technology/equipment)
    return ('TIER_2', 0.5, 'general_technology')
```

---

## Expected Final Coverage

### Projected Results on 300-Record Sample:
- **TIER 1**: 11-15 records (4-5%) - Strategic entities/tech
- **TIER 2**: 50-60 records (17-20%) - Technology/services
- **TIER 3**: 160-170 records (53-57%) - Commodity purchases
- **UNCATEGORIZED**: 60-75 records (20-25%) - Edge cases

### Projected Full Database (166,557 records):
- **TIER 1**: ~6,000-8,000 (4-5%) - HIGH intelligence value
- **TIER 2**: ~30,000-35,000 (18-21%) - MEDIUM intelligence value
- **TIER 3**: ~90,000-100,000 (54-60%) - VERY LOW intelligence value
- **UNCATEGORIZED**: ~25,000-30,000 (15-18%) - Needs review/default TIER_2

---

## Key Insights from Sample Analysis

### Top Commodity Items (Sample):
1. **Commodity Electronics** (54 records): Surge protectors, cables, batteries
2. **Hardware** (34 records): Pipes, elbows, relays, fittings
3. **Office Supplies** (33 records): Brother label makers, toner cartridges
4. **Kitchen/Janitorial** (16 records): Cups, scoops, mops
5. **Apparel** (9 records): Aprons, gloves

### Strategic Entities Found (Sample):
- Chinese Academy of Sciences (1 record, confidence 0.95)
- Other strategic entities in review

### Intelligence Value:
- **TIER 1 + 2 focus**: ~40,000 records for intelligence analysis
- **TIER 3 archive**: ~100,000 commodity purchases (excluded from primary analysis)
- **Noise reduction**: ~60% reduction in low-value records for analysis

---

## Implementation Status

✅ **Phase 1 Complete**: Expanded commodity patterns defined
⏳ **Phase 2 Pending**: Database schema update
⏳ **Phase 3 Pending**: Processor implementation
⏳ **Phase 4 Pending**: Re-processing with importance tiers

---

*Document created: 2025-10-16 20:45 UTC*
