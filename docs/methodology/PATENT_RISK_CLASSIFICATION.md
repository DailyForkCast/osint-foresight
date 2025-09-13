# Patent Technology Risk Classification Framework
**Generated: 2025-01-10**
**Purpose: Identify critical technologies regardless of volume**

## CRITICAL INSIGHT
**One quantum computing patent with China is worse than 100 textile manufacturing patents**

## TECHNOLOGY RISK TIERS

### TIER 1: CRITICAL (Any collaboration = immediate alert)
```
QUANTUM TECHNOLOGIES
- IPC: G06N 10/* (Quantum computing)
- IPC: H04L 9/08 (Quantum cryptography)
- IPC: H04B 10/70 (Quantum communication)
- Risk: Breaking all current encryption, strategic advantage
- Action: IMMEDIATE FREEZE required

MILITARY/DEFENSE
- IPC: F41* (Weapons)
- IPC: F42* (Ammunition, explosives)
- IPC: B63G* (Submarines)
- IPC: B64G* (Spacecraft)
- Risk: Direct military application
- Action: Potential legal violations, immediate review

NUCLEAR
- IPC: G21* (Nuclear physics/engineering)
- IPC: G01T* (Nuclear radiation measurement)
- Risk: Nuclear weapons, energy security
- Action: Export control violation likely

ADVANCED AI/ML
- IPC: G06N 3/* (Neural networks)
- IPC: G06N 20/* (Machine learning)
- Risk: Surveillance, autonomous weapons, strategic AI
- Action: Dual-use assessment required
```

### TIER 2: HIGH RISK (>5 patents = concern, >10 = critical)
```
SEMICONDUCTORS/CHIPS
- IPC: H01L* (Semiconductor devices)
- IPC: H03K* (Pulse technique)
- IPC: G03F 7/* (Photolithography)
- Risk: Chip independence, supply chain
- Specific concern: EUV lithography, <7nm processes

AEROSPACE
- IPC: B64C* (Aeroplanes, helicopters)
- IPC: F02K* (Jet propulsion)
- IPC: G01S 19/* (Satellite navigation)
- Risk: Dual-use, military aviation

BIOTECHNOLOGY
- IPC: C12N 15/* (Genetic engineering)
- IPC: C12Q 1/68 (DNA/RNA analysis)
- IPC: A61K 38/* (Medicinal peptides)
- Risk: Bioweapons, pandemic preparedness

CYBERSECURITY
- IPC: H04L 9/* (Cryptography)
- IPC: G06F 21/* (Security arrangements)
- Risk: Critical infrastructure protection

HYPERSONICS/MATERIALS
- IPC: C04B 35/* (Ceramic compositions)
- IPC: C22C* (Alloys)
- Keywords: "hypersonic", "ablative", "ultra-high temperature"
- Risk: Missile technology
```

### TIER 3: MODERATE RISK (Context dependent)
```
5G/6G COMMUNICATIONS
- IPC: H04W* (Wireless networks)
- IPC: H04B 7/* (Radio transmission)
- Risk: Infrastructure dependency

ADVANCED MANUFACTURING
- IPC: B33Y* (Additive manufacturing/3D printing)
- IPC: B23K* (Laser processing)
- Risk: Dual-use manufacturing

ENERGY STORAGE
- IPC: H01M* (Batteries, fuel cells)
- IPC: H02J* (Energy storage systems)
- Risk: Critical infrastructure

ROBOTICS/AUTOMATION
- IPC: B25J* (Manipulators, robots)
- IPC: G05B 19/* (Automation control)
- Risk: Industrial espionage, automation warfare
```

### TIER 4: STANDARD MONITORING
```
- Consumer electronics
- Traditional manufacturing
- Agriculture (unless genetic)
- Textiles
- Construction methods
```

## CRITICAL PATENT PATTERNS TO FLAG

### Pattern 1: Technology Hopping
```
SIGNAL: Same inventors moving across technology domains
EXAMPLE: Battery expert → Suddenly quantum patents
RISK: Knowledge transfer beyond stated field
```

### Pattern 2: Rapid Assignment Changes
```
SIGNAL: Patent filed by university → Assigned to Chinese entity within 6 months
EXAMPLE: Slovak uni files → Beijing company owns
RISK: Pre-arranged technology transfer
```

### Pattern 3: Citation Cascades
```
SIGNAL: One patent heavily cited by Chinese entities
EXAMPLE: 1 Slovak patent → 50+ Chinese patents cite it
RISK: Technology being built upon extensively
```

### Pattern 4: Family Expansion
```
SIGNAL: Simple patent → Massive family in China
EXAMPLE: 1 EU patent → 20+ Chinese variants
RISK: Technology being weaponized/commercialized
```

## SPECIFIC KEYWORDS TO ALWAYS FLAG

### Materials Science Red Flags
- "metamaterial" - Stealth technology
- "graphene" + "armor" - Military applications
- "single crystal" + "turbine" - Jet engines
- "hafnium" + "carbide" - Hypersonic vehicles
- "gallium nitride" - Military radar
- "rare earth" + "magnet" - Critical dependencies

### Computing/AI Red Flags
- "neuromorphic" - Brain-like computing
- "homomorphic encryption" - Compute on encrypted data
- "federated learning" - Distributed AI
- "quantum supremacy" - Quantum advantage
- "photonic computing" - Light-based processors

### Bio/Chem Red Flags
- "gain of function" - Pandemic risk
- "CRISPR" + "human" - Genetic modification
- "synthetic biology" - Artificial life
- "neurotoxin" - Chemical weapons
- "aerosol" + "pathogen" - Bioweapon delivery

## RISK SCORING MATRIX

### Formula:
```
Risk Score = (Technology Tier × 10) + (Volume Factor) + (Pattern Bonus)

Where:
- Tier 1 = 40 points base
- Tier 2 = 30 points base  
- Tier 3 = 20 points base
- Tier 4 = 10 points base

Volume Factor:
- 1-5 patents: +5
- 6-20 patents: +10
- 21-50 patents: +15
- 50+ patents: +20

Pattern Bonus:
- Rapid assignment: +10
- Citation cascade: +10
- Technology hopping: +15
- Military institution: +20
```

### Examples:
- 1 Quantum patent = 40 + 5 + 0 = 45 (HIGH RISK)
- 100 Textile patents = 10 + 20 + 0 = 30 (MODERATE)
- 5 AI patents to PLA uni = 30 + 5 + 20 = 55 (CRITICAL)

## SLOVAKIA PATENT ANALYSIS REVISITED

From the 70 Slovak-Chinese patents, we need to know:

### Critical Questions:
1. How many are Tier 1 technologies? (Even 1 = critical)
2. How many are Tier 2? (>10 = major concern)
3. Any military/PLA assignees? (+20 to risk)
4. Any rapid assignments? (Technology transfer signal)

### Example Classification:
```
US-2021269694-A1 (from our data):
- Phosphorus-nitrogen compounds
- Flame retardants
- Complex chemical synthesis
→ TIER 2/3: Potential dual-use (aerospace/military materials)
→ Requires deeper investigation
```

## MASTER PROMPT IMPROVEMENTS NEEDED

### Add to Phase 1 (Patent Analysis):
```
PATENT TECHNOLOGY CLASSIFICATION:
For each patent found, identify:
1. IPC classification codes
2. Technology tier (1-4)
3. Keywords indicating dual-use
4. Assignee type (university/company/military)
5. Assignment changes over time
6. Citation patterns

CRITICAL TECHNOLOGIES (Auto-flag):
- Quantum (ANY amount)
- Nuclear (ANY amount)
- Weapons (ANY amount)
- AI/ML (>10 patents)
- Semiconductors (>10 patents)
- Biotech with military applications
```

### Add Risk Override Rules:
```
AUTOMATIC CRITICAL DESIGNATION:
Regardless of total percentage:
- ANY quantum computing patents with adversary
- ANY nuclear technology patents
- ANY weapons/explosives patents
- >5 patents with PLA universities
- >10 AI/semiconductor patents
- ANY "gain of function" research
```

### Patent Deep Dive Protocol:
```
For Tier 1-2 technologies:
1. Full patent text analysis
2. Inventor background check
3. Assignee investigation
4. Citation network mapping
5. Patent family analysis
6. Timeline of development
```

## REAL-WORLD EXAMPLES

### Case 1: Netherlands ASML
- Only 3 patents with Chinese co-inventors
- BUT: EUV lithography (most advanced chips)
- Result: CRITICAL - National security review

### Case 2: Australia Universities  
- 100s of papers/patents with China
- Included: Hypersonic materials, quantum
- Result: Government intervention, new laws

### Case 3: UK University
- 20 patents with Chinese military university
- Domain: Metamaterials (stealth technology)
- Result: Collaboration terminated

## KEY TAKEAWAY

**Volume matters for context, but technology domain is decisive**

Scoring must reflect:
1. **Technology criticality** (Tier 1 always critical)
2. **Volume within domain** (many Tier 2 = escalation)
3. **Specific patterns** (PLA, rapid transfer)
4. **Dual-use potential** (civilian tech → military use)

The master prompt must include technology classification as PRIMARY risk factor, with percentage/volume as SECONDARY context.

## FOR SLOVAKIA SPECIFICALLY

We found:
- 70 total patents with China
- Heavy concentration in materials/chemistry
- Need to classify each by tier
- Even 5-10 in Tier 1-2 would be CRITICAL

Recommendation: Re-analyze those 70 patents through this framework to identify the highest risks regardless of total percentage.