# Stakeholder ID Structure Guide
**Date:** October 26, 2025
**Version:** v4+
**File:** `2025-10-26-Tracker-v4.xlsx`

---

## 🎯 CATEGORIZED ID SYSTEM

Stakeholder IDs now use **meaningful prefixes** based on the stakeholder's primary category.

### **Priority Order (use first applicable):**

```
1. Country-Specific    → [CC]-STK-XXX
2. Multi-Country       → MC-STK-XXX
3. Regional            → [REGION]-STK-XXX
4. Thematic/Technology → [THEME]-STK-XXX
5. Project-Specific    → PRJ-XXX-STK-XXX
```

**Rule:** Use the **MOST SPECIFIC** category that applies. If a stakeholder fits multiple categories, use the **highest priority** one.

---

## 📋 CATEGORY DETAILS

### **1. Country-Specific (Highest Priority)**

**Format:** `[CC]-STK-XXX`

**When to use:**
- Stakeholder is primarily associated with ONE country
- In-country coordinators, local partners
- Government contacts for a specific country
- Country office staff

**Examples:**
- `DE-STK-001` - First Germany contact (Hans Schmidt, Berlin Office Director)
- `UK-STK-001` - First UK contact (Sarah Johnson, London Coordinator)
- `FR-STK-002` - Second France contact (Marie Dubois, Paris Program Manager)
- `IT-STK-001` - First Italy contact (Marco Rossi, Rome Tech Lead)

**How to number:**
- Sequential within each country
- DE-STK-001, DE-STK-002, DE-STK-003, etc.

**Excel Entry:**
- Stakeholder_Type: Location-Specific
- Countries: DE (single country code)
- Region: EUR (auto-derived from country)

---

### **2. Multi-Country (2nd Priority)**

**Format:** `MC-STK-XXX`

**When to use:**
- Stakeholder works across MULTIPLE specific countries (but not whole region)
- Cross-border coordinators
- Multi-country program managers
- Works in 2-10 countries specifically

**Examples:**
- `MC-STK-001` - Works across Germany, France, Italy
- `MC-STK-002` - Benelux coordinator (Belgium, Netherlands, Luxembourg)
- `MC-STK-003` - Nordic liaison (Sweden, Norway, Denmark, Finland)

**How to number:**
- Sequential across all multi-country stakeholders
- MC-STK-001, MC-STK-002, MC-STK-003, etc.

**Excel Entry:**
- Stakeholder_Type: Location-Specific
- Countries: DE, FR, IT (comma-separated)
- Region: (can leave blank or put primary region)

---

### **3. Regional (3rd Priority)**

**Format:** `[REGION]-STK-XXX`

**When to use:**
- Stakeholder responsible for ENTIRE region
- Regional directors, regional advisors
- Works across whole EUR, WHA, EAP, etc.
- Regional office staff

**Available Regions:**
- EUR (Europe)
- WHA (Western Hemisphere)
- EAP (East Asia Pacific)
- AF (Africa)
- NEA (Near East Asia)
- SCA (South Central Asia)

**Examples:**
- `EUR-STK-001` - European Regional Director
- `WHA-STK-001` - Western Hemisphere Program Manager
- `EAP-STK-002` - Second Asia-Pacific advisor
- `AF-STK-001` - Africa Regional Coordinator

**How to number:**
- Sequential within each region
- EUR-STK-001, EUR-STK-002, EUR-STK-003, etc.

**Excel Entry:**
- Stakeholder_Type: Regional
- Region: EUR (or WHA, EAP, etc.)
- Countries: (leave blank or list key countries)

---

### **4. Thematic/Technology (4th Priority)**

**Format:** `[THEME]-STK-XXX`

**When to use:**
- Subject matter experts (not tied to location/project)
- Cross-cutting theme leads
- Technology specialists
- Works on specific theme across all projects/locations

**Common Themes:**
- CYBER (Cybersecurity)
- AI (Artificial Intelligence / Machine Learning)
- CLIMATE (Climate Tech)
- ENERGY (Energy/Power)
- HEALTH (Healthcare/Medical)
- FINANCE (Financial Tech)
- DEFENSE (Defense/Military)
- TRADE (Trade/Commerce)
- SPACE (Space Technology)
- QUANTUM (Quantum Computing)

**Examples:**
- `CYBER-STK-001` - Chief Cybersecurity Advisor
- `AI-STK-001` - AI/ML Subject Matter Expert
- `CLIMATE-STK-002` - Second Climate Tech Specialist
- `QUANTUM-STK-001` - Quantum Computing Expert

**How to number:**
- Sequential within each theme
- CYBER-STK-001, CYBER-STK-002, CYBER-STK-003, etc.

**Excel Entry:**
- Stakeholder_Type: Thematic
- Theme: Cybersecurity (or AI/ML, Climate Tech, etc.)
- Region: (can be blank or global)
- Countries: (usually blank)

---

### **5. Project-Specific (Lowest Priority)**

**Format:** `PRJ-XXX-STK-XXX`

**When to use:**
- Stakeholder tied to ONE specific project
- Project managers, technical leads
- Implementation partners for specific project
- Use ONLY if not better categorized above

**Examples:**
- `PRJ-001-STK-001` - Digital Transform Project Tech Lead
- `PRJ-003-STK-002` - Second stakeholder on Project 003
- `PRJ-007-STK-001` - Border Security Project Manager

**How to number:**
- Sequential within each project
- PRJ-001-STK-001, PRJ-001-STK-002, etc.

**Excel Entry:**
- Stakeholder_Type: Project-Specific
- Project_IDs: PRJ-001
- Countries: (depends on project)
- Region: (depends on project)

---

## 🔄 DECISION TREE

**How to choose the right ID:**

```
START HERE
    ↓
Is stakeholder primarily for ONE country?
    YES → Use [CC]-STK-XXX (e.g., DE-STK-001)
    NO ↓

Does stakeholder work across 2-10 specific countries?
    YES → Use MC-STK-XXX (e.g., MC-STK-001)
    NO ↓

Is stakeholder responsible for ENTIRE region?
    YES → Use [REGION]-STK-XXX (e.g., EUR-STK-001)
    NO ↓

Is stakeholder a subject matter expert / thematic lead?
    YES → Use [THEME]-STK-XXX (e.g., CYBER-STK-001)
    NO ↓

Is stakeholder tied to ONE specific project?
    YES → Use PRJ-XXX-STK-XXX (e.g., PRJ-001-STK-001)
```

---

## 📊 COMPLETE EXAMPLES

### Example 1: Germany Country Coordinator
```
Stakeholder_ID: DE-STK-001
Name: Hans Schmidt
Title: Germany Country Coordinator
Organization: Tech Solutions GmbH
Location_City: Berlin
Location_Country: Germany
Time_Zone_Offset: +1
Stakeholder_Type: Location-Specific
Countries: DE
Region: EUR
```
**Why DE-STK-001?** Primary role is Germany-specific (Country wins over Region)

---

### Example 2: European Regional Director
```
Stakeholder_ID: EUR-STK-001
Name: Sarah Johnson
Title: European Regional Director
Organization: International Tech Corp
Location_City: Brussels
Location_Country: Belgium
Stakeholder_Type: Regional
Region: EUR
Countries: (blank - covers all EUR)
```
**Why EUR-STK-001?** Responsible for entire European region

---

### Example 3: Cybersecurity Expert (Global)
```
Stakeholder_ID: CYBER-STK-001
Name: Dr. Maria Chen
Title: Chief Cybersecurity Advisor
Organization: CyberDefense Group
Stakeholder_Type: Thematic
Theme: Cybersecurity
Region: (blank - global)
```
**Why CYBER-STK-001?** Subject matter expert, not tied to specific location

---

### Example 4: Multi-Country Coordinator
```
Stakeholder_ID: MC-STK-001
Name: Jean-Pierre Dubois
Title: Benelux Coordinator
Organization: EU Partners Inc
Countries: BE, NL, LU
Region: EUR
Stakeholder_Type: Location-Specific
```
**Why MC-STK-001?** Works across 3 specific countries (Multi-Country wins over Regional)

---

### Example 5: Project Technical Lead
```
Stakeholder_ID: PRJ-001-STK-001
Name: Alex Rivera
Title: Technical Lead
Organization: DevOps Solutions
Project_IDs: PRJ-001
Stakeholder_Type: Project-Specific
```
**Why PRJ-001-STK-001?** Tied to specific project, no other categorization fits better

---

## 🎯 EDGE CASES

### Case 1: Regional Director who ALSO leads Cybersecurity
**Choose:** EUR-STK-001 (Region beats Theme in priority)
**Alternative:** Document both roles in Notes column

### Case 2: Germany contact who ALSO works on Project 001
**Choose:** DE-STK-001 (Country beats Project in priority)
**Fill in:** Project_IDs: PRJ-001 (to show connection)

### Case 3: Someone who works in 15 countries across Europe
**Choose:** EUR-STK-001 (Too many countries = Regional, not Multi-Country)

### Case 4: Someone who works in Germany AND France ONLY
**Choose:** MC-STK-001 (2 countries = Multi-Country, not Regional)

---

## 📁 WHERE TO FIND THE GUIDE

**In Excel:**
1. Open `2025-10-26-Tracker-v4.xlsx`
2. Go to **Stakeholders** sheet
3. **Hover over cell A1** (Stakeholder_ID header)
4. **Comment will appear** with ID structure guide

**In this file:**
- Keep this markdown file as reference: `STAKEHOLDER_ID_GUIDE.md`

---

## ✅ BENEFITS OF THIS SYSTEM

**1. Meaningful IDs**
- `DE-STK-001` immediately tells you it's a Germany contact
- `CYBER-STK-001` immediately tells you it's a cybersecurity expert
- Better than generic `STK-001`

**2. Easy Filtering**
- Filter all Germany contacts: `DE-STK-*`
- Filter all European regional: `EUR-STK-*`
- Filter all cybersecurity: `CYBER-STK-*`

**3. Scalable**
- Each category has its own numbering
- No conflicts between categories
- Easy to add new stakeholders

**4. Matches Your Multi-Dimensional System**
- Priority order reflects your workflow
- Country-first approach
- Supports complex relationships

**5. Consistent with Other IDs**
- Follows same pattern as PRJ-XXX-MS-XXX
- Easy to understand across the tracker

---

## 🔧 IMPLEMENTATION

**v4 Changes:**
- ✅ Stakeholder_ID comment added to cell A1
- ✅ Sample ID updated to EXAMPLE-STK-001
- ✅ Structure ready for categorized IDs

**To Use:**
1. When adding new stakeholder, follow decision tree
2. Use appropriate prefix based on priority
3. Number sequentially within category
4. Fill in all relevant columns (Countries, Region, Theme, etc.)

---

**Status:** ID structure implemented in v4 ✅
**Documentation:** Complete ✅
**Ready to Use:** YES ✅
