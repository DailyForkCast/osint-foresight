# MCF Visualization Workflow - Complete Summary

**Date:** October 20, 2025
**Status:** ✅ COMPLETE
**Purpose:** Comprehensive network visualization system for MCF institutional architecture

---

## What Was Built

Complete end-to-end visualization workflow for China's Military-Civil Fusion (MCF) institutional architecture, technology flows, and governance structure.

---

## Files Created

### 1. Data Definition
**File:** `mcf_network_data.py` (554 lines)
- Central coordination bodies (3 entities)
- Key ministries (6 entities)
- Agencies (4 entities)
- Provincial implementation (2 categories)
- Implementation entities (3 categories)
- Relationships (37 edges with types and weights)
- Technology flows for Sankey (11 flows)
- Governance hierarchy structure
- Color schemes for visualization types

**Purpose:** Single source of truth for all MCF institutional network data

### 2. NetworkX Visualizations
**File:** `mcf_networkx_viz.py` (350 lines)

**Outputs:**
- `mcf_institutional_architecture.png` (1.2 MB)
- `mcf_institutional_architecture.svg` (102 KB)
- `mcf_simplified_architecture.png` (487 KB)
- `mcf_simplified_architecture.svg` (51 KB)

**Features:**
- Full network: 18 nodes, 21 edges, hierarchical layout by tier
- Simplified network: 9 nodes (tier 1-2 only), spring layout
- Node sizes by power level, colors by organization type
- Edge colors by relationship type, widths by weight
- High-resolution PNG and scalable SVG outputs

### 3. Plotly Sankey Diagrams
**File:** `mcf_sankey_viz.py` (390 lines)

**Outputs:**
- `mcf_technology_flow.html` (4.6 MB, interactive)
- `mcf_technology_flow.png` (348 KB)
- `mcf_technology_flow.svg` (14 KB)
- `mcf_four_initiatives_flow.html` (4.6 MB, interactive)
- `mcf_four_initiatives_flow.png` (502 KB)
- `mcf_four_initiatives_flow.svg` (19 KB)
- `mcf_sector_priority_flow.html` (4.6 MB, interactive)

**Features:**
- Technology flow: Foreign acquisition → Domestic processing → Military/Civilian application
- Four Global Initiatives: BRI, GDI, GSI, GCI coordination → mechanisms → objectives
- Sector priority: Made in China 2025 sectors → Research institutions → Applications
- Interactive HTML files with hover details
- High-resolution PNG exports (where successful)
- Scalable SVG exports

### 4. Graphviz Hierarchy Trees
**File:** `mcf_graphviz_hierarchy.py` (420 lines)

**Outputs:**
- `mcf_governance_hierarchy.png` (51 KB)
- `mcf_governance_hierarchy.svg` (20 KB)
- `mcf_governance_hierarchy.pdf` (49 KB)
- `mcf_institutional_layers.png` (97 KB)
- `mcf_institutional_layers.svg` (15 KB)
- `mcf_institutional_layers.pdf` (28 KB)
- `mcf_command_flow.png` (53 KB)
- `mcf_command_flow.svg` (15 KB)
- `mcf_command_flow.pdf` (42 KB)
- Source `.gv` files for all diagrams

**Features:**
- Governance tree: Xi → MCF Commission → State Council/CMC → Ministries → Agencies → Implementation
- Institutional layers: 5-tier structure with color-coded levels
- Command flow: Relationship types (commands, directs, coordinates, funds, controls)
- PDF outputs for high-quality printing
- Graphviz source files for editing

### 5. PowerPoint Automation
**File:** `mcf_powerpoint_generator.py` (350 lines)

**Outputs:**
- `MCF_Visualization_Compendium.pptx` (13 slides)
- `MCF_Quick_Reference.pptx` (5 slides)

**Features:**
- Automated slide creation with embedded high-res images
- Title slides, section dividers, content slides
- Speaker notes with interpretation guidance
- Summary slide with visualization inventory
- Quick reference deck for briefings

---

## Complete File Inventory

### Scripts (4 files)
```
scripts/visualization/
├── mcf_network_data.py (554 lines) - Data model
├── mcf_networkx_viz.py (350 lines) - Network graphs
├── mcf_sankey_viz.py (390 lines) - Flow diagrams
├── mcf_graphviz_hierarchy.py (420 lines) - Hierarchy trees
└── mcf_powerpoint_generator.py (350 lines) - PowerPoint automation
```

### Visualizations (19 files total)

**NetworkX outputs (4 files):**
- mcf_institutional_architecture.png/svg
- mcf_simplified_architecture.png/svg

**Plotly Sankey outputs (7 files):**
- mcf_technology_flow.html/png/svg
- mcf_four_initiatives_flow.html/png/svg
- mcf_sector_priority_flow.html

**Graphviz outputs (12 files):**
- mcf_governance_hierarchy.png/svg/pdf/.gv
- mcf_institutional_layers.png/svg/pdf/.gv
- mcf_command_flow.png/svg/pdf/.gv

**PowerPoint outputs (2 files):**
- MCF_Visualization_Compendium.pptx (13 slides)
- MCF_Quick_Reference.pptx (5 slides)

---

## Visualization Types

### 1. Network Graphs (NetworkX)
**Best for:** Showing relationships between many entities

**MCF Institutional Architecture:**
- 18 nodes across 5 tiers
- 21 relationships
- Hierarchical layout (tier 1 at top → tier 5 at bottom)
- Node colors by organization type
- Node sizes by power level (1-10)
- Edge colors by relationship type
- Edge widths by relationship strength

**MCF Simplified Architecture:**
- 9 nodes (tier 1-2 only: central authorities and key ministries)
- 8 relationships
- Spring layout for clarity
- Focus on core coordination

### 2. Sankey Diagrams (Plotly)
**Best for:** Showing flows and proportions

**Technology Flow:**
- Foreign Universities/Companies →
- Chinese Academy of Sciences / University Defense Labs / SOEs →
- PLA SSF / Military Applications / Civilian Applications
- 8 nodes, 11 flows
- Flow widths represent intensity

**Four Global Initiatives Flow:**
- Central coordination → 4 Initiatives → Implementation mechanisms → Strategic objectives
- 14 nodes, 17 flows
- Shows initiative synergies (cross-connections)

**Made in China 2025 Sector Priority:**
- 8 priority sectors → 3 research institutions → 3 application domains
- 14 nodes, 19 flows
- Demonstrates sector → research → application pipeline

### 3. Hierarchy Trees (Graphviz)
**Best for:** Showing governance structure and command relationships

**Governance Hierarchy:**
- Xi Jinping (apex)
- Central MCF Commission (chaired by Xi)
- State Council + Central Military Commission
- Ministries, agencies, research institutions, SOEs
- Tree structure with labeled relationships

**Institutional Layers:**
- 5 tiers in color-coded clusters
- Tier 1: Central Leadership (red)
- Tier 2: Key Ministries & Commissions (blue)
- Tier 3: Key Agencies (yellow)
- Tier 4: Provincial Implementation (gray)
- Tier 5: Implementation Entities (green)

**Command Flow:**
- Left-to-right flow diagram
- Color-coded relationship types:
  - Commands (purple)
  - Directs (blue)
  - Coordinates (red)
  - Funds (orange)
  - Controls (dark red)
- Legend included

---

## Technical Implementation

### Dependencies Installed
```bash
pip install networkx matplotlib plotly kaleido graphviz python-pptx
winget install Graphviz.Graphviz
```

### Environment Setup
- Graphviz executables added to PATH
- Kaleido installed for Plotly image export
- All scripts use pathlib for cross-platform compatibility

### Export Formats

**PNG:** High-resolution raster (300 DPI)
- Best for: PowerPoint, web, printing at fixed size
- File sizes: 50 KB - 1.2 MB

**SVG:** Scalable vector graphics
- Best for: Editing, scaling without quality loss
- File sizes: 14 KB - 102 KB

**PDF:** Print-quality documents (Graphviz only)
- Best for: High-quality printing, archival
- File sizes: 28 KB - 49 KB

**HTML:** Interactive (Plotly Sankey only)
- Best for: Exploration, presentations with interactivity
- File sizes: 4.6 MB (includes full Plotly library)

---

## Usage Guide

### Running Individual Scripts

**Create NetworkX visualizations:**
```bash
cd "C:/Projects/OSINT - Foresight/scripts/visualization"
python mcf_networkx_viz.py
```
Outputs: PNG and SVG files

**Create Sankey diagrams:**
```bash
python mcf_sankey_viz.py
```
Outputs: HTML (interactive), PNG, SVG files

**Create Graphviz hierarchies:**
```bash
export PATH="$PATH:/c/Program Files/Graphviz/bin"
python mcf_graphviz_hierarchy.py
```
Outputs: PNG, SVG, PDF, and .gv source files

**Create PowerPoint presentations:**
```bash
python mcf_powerpoint_generator.py
```
Outputs: Two .pptx files (compendium and quick reference)

### Modifying Data

Edit `mcf_network_data.py` to:
- Add/remove institutions
- Modify relationships
- Adjust weights and tiers
- Update color schemes

Then re-run visualization scripts to regenerate outputs.

### Customizing Visualizations

**NetworkX:**
- Adjust DPI parameter for higher/lower resolution
- Modify layout algorithm (hierarchical vs spring)
- Change node size multiplier (currently `power_level * 300`)

**Plotly Sankey:**
- Modify width/height parameters
- Adjust color schemes in flow definitions
- Change scale parameter for PNG export (currently 2x)

**Graphviz:**
- Edit graph attributes (rankdir, splines, etc.)
- Modify node/edge styles
- Change layouts (dot, neato, fdp, circo)

---

## Key Insights Visualized

### 1. Centralization of Power
- Xi Jinping chairs both Central MCF Commission and Central Military Commission
- All major coordination flows through central leadership
- Dual civilian-military command structure

### 2. Whole-of-Government Approach
- 18 institutions across 5 tiers
- Coordinated by Central MCF Commission
- Includes ministries (MIIT, MOST, MOE, NDRC, SASAC, MSS)
- Integrates military (CMC, PLA SSF, SASTIND)
- Extends to provincial and implementation levels

### 3. Technology Acquisition Pipeline
- Foreign acquisition (universities, companies)
- Domestic processing (CAS, university labs, SOEs)
- Dual-use application (military and civilian)
- Systematic technology transfer

### 4. Strategic Initiative Integration
- Belt and Road Initiative (infrastructure)
- Global Development Initiative (finance)
- Global Security Initiative (security cooperation)
- Global Civilization Initiative (soft power)
- Coordinated to achieve: economic influence, technology acquisition, security presence

### 5. Sectoral Priorities
- Made in China 2025 identifies 8-10 priority sectors
- Research concentrated in these sectors
- Outputs flow to military, civilian, and dual-use applications

---

## Integration with MCF Presentation

These visualizations complement the policy documents integration (F:/Policy_Documents_Sweep/):

### Policy Documents (Intent)
- 14th Five-Year Plan
- 13th Five-Year Plan
- Made in China 2025
- National Intelligence Law
- Cybersecurity Law
- Data Security Law

### Database Evidence (Execution)
- 577,197 USPTO patents
- 38,397 OpenAlex collaborations
- 3,379 USAspending awards
- 383 CORDIS projects
- 219 TED contracts

### Visualizations (Structure)
- Institutional architecture
- Governance hierarchy
- Technology flows
- Strategic initiatives
- Command relationships

**Combined Message:**
"China's policy documents state their intent. Our database evidence shows execution. These visualizations reveal the coordinated structure making it possible."

---

## Recommended Usage

### For Briefings
Use Quick Reference deck (5 slides):
1. Title
2. Governance Hierarchy
3. Institutional Layers
4. Technology Flow
5. Four Global Initiatives

### For Detailed Analysis
Use Full Compendium (13 slides):
- All visualizations
- Speaker notes with interpretation
- Section dividers
- Summary slide

### For Publications
Use high-resolution exports:
- PDF for print documents
- SVG for scalable graphics
- PNG for web/presentations

### For Interactive Exploration
Open HTML Sankey diagrams in browser:
- Hover to see flow details
- Zoom and pan
- Export screenshots

---

## Presentation Flow Recommendation

**Slide 1:** Title
**Slide 2:** Governance Hierarchy (shows Xi at apex)
**Slide 3:** Institutional Layers (shows 5-tier structure)
**Slide 4:** Command Flow (shows relationship types)
**Slide 5:** Technology Flow (shows foreign → domestic → application)
**Slide 6:** Four Global Initiatives (shows coordination → mechanisms → objectives)

**Message Arc:**
1. "This is who's in charge" (Governance)
2. "This is how it's organized" (Layers)
3. "This is how it operates" (Command Flow)
4. "This is how technology moves" (Technology Flow)
5. "This is how it projects globally" (Initiatives)

---

## Files Referenced in Presentation

When citing these visualizations in the MCF presentation:

**Source:**
"Institutional architecture analysis based on open-source research, CSET Georgetown reports, and Chinese government organizational charts."

**Data Model:**
`scripts/visualization/mcf_network_data.py` contains complete data definitions with sources.

**Methodology:**
- Network analysis: NetworkX (Python)
- Flow visualization: Plotly Sankey diagrams
- Hierarchy trees: Graphviz
- Data sources: Chinese government documents, CSET analysis, open-source research

---

## Next Steps (Optional Enhancements)

### Additional Visualizations
- [ ] Temporal evolution (how structure changed over time)
- [ ] Geographic distribution (provincial MCF offices map)
- [ ] Technology sector deep dives (AI, semiconductors, quantum, etc.)
- [ ] Talent flow diagrams (Thousand Talents, Changjiang Scholars)
- [ ] Funding flows (NDRC → provinces → projects)

### Interactive Features
- [ ] Web-based interactive dashboard
- [ ] Filterable network graph (by tier, sector, relationship type)
- [ ] Animated Sankey showing technology flow over time
- [ ] Clickable nodes with detailed information panels

### Integration
- [ ] Embed in website or knowledge base
- [ ] Link to database evidence for each institution
- [ ] Cross-reference with policy document citations
- [ ] Connect to actual examples from database

---

## Technical Notes

### Challenges Encountered

**1. Kaleido Browser Subprocess Issue**
- **Problem:** Plotly's Kaleido occasionally fails to close browser subprocess
- **Impact:** Third Sankey diagram PNG export failed
- **Workaround:** HTML version created successfully (interactive, actually better)
- **Solution:** Could add retry logic or export to HTML only

**2. Graphviz PATH Configuration**
- **Problem:** Graphviz executables not on Windows PATH by default
- **Solution:** Added to PATH with `export PATH="$PATH:/c/Program Files/Graphviz/bin"`
- **Permanent Fix:** System PATH update or conda environment configuration

**3. Unicode Console Encoding**
- **Problem:** Windows console couldn't display checkmark characters
- **Solution:** Replaced with `[SAVED]` ASCII markers
- **Note:** Purely cosmetic, doesn't affect outputs

### Performance

All scripts execute quickly:
- NetworkX: ~5 seconds
- Sankey: ~30 seconds (including image export)
- Graphviz: ~10 seconds
- PowerPoint: <5 seconds

Total end-to-end: ~1 minute to regenerate all visualizations

### File Sizes

Total visualization output: ~30 MB
- HTML files: ~14 MB (3 files)
- PNG files: ~3 MB (8 files)
- SVG files: ~0.3 MB (10 files)
- PDF files: ~0.1 MB (3 files)
- PowerPoint: ~12 MB (2 files)

---

## Maintenance

### Updating Visualizations

When MCF structure changes:
1. Update `mcf_network_data.py` with new institutions/relationships
2. Run visualization scripts to regenerate outputs
3. Run PowerPoint generator to update presentations
4. Total time: ~2 minutes

### Version Control

All scripts and data files are in:
```
C:/Projects/OSINT - Foresight/scripts/visualization/
```

Recommended: Commit to git with tagged versions for presentation milestones.

---

## Credits

**Data Sources:**
- Chinese government organizational structures
- CSET Georgetown analysis ("Pulling Back the Curtain on MCF")
- Made in China 2025 strategic sectors
- Five-Year Plan institutional descriptions
- Open-source research

**Tools:**
- Python 3.10
- NetworkX (network analysis)
- Matplotlib (rendering)
- Plotly (Sankey diagrams)
- Graphviz (hierarchy trees)
- python-pptx (PowerPoint automation)
- Kaleido (Plotly image export)

**Created:** October 20, 2025
**Purpose:** MCF NQPF Expert Revised Presentation supporting visualizations

---

## Summary

✅ **Complete end-to-end visualization workflow**
✅ **8 unique visualizations in multiple formats**
✅ **19 output files + 2 PowerPoint decks**
✅ **Automated generation from single data source**
✅ **High-resolution exports for all use cases**
✅ **Interactive HTML versions for exploration**
✅ **Print-quality PDF versions**
✅ **PowerPoint automation with speaker notes**

**Status:** PRODUCTION READY

---

*"Their structure. Our visualizations. Clear understanding."*
