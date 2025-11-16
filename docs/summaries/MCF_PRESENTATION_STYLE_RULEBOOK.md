# MCF Presentation Style Rulebook
## Based on Analysis of MCF v2.1 (Slides 3-8)

---

## 1. SLIDE SETUP

### Dimensions
- **Slide Size:** 10.00" × 5.62" (16:9 widescreen)
- **Format:** Standard widescreen PowerPoint format
- **Orientation:** Landscape

---

## 2. TYPOGRAPHY SYSTEM

### Primary Font
- **Font Family:** Arial (used exclusively - 100% of all text)
- **Style:** Sans-serif, clean, professional

### Font Size Hierarchy
Use this established hierarchy for consistent visual organization:

#### Large Text (Titles & Major Headers)
- **21pt** - Primary slide titles (rare use, emphasis only)
- **19.5pt** - Section headers / Major headings
- **15pt** - Subheadings

#### Medium Text (Body Content)
- **14pt** - Primary body text (larger blocks)
- **13.5pt** - Secondary body text
- **12pt** - Standard body text
- **11.25pt** - Dense content areas
- **11pt** - Standard content (most common)
- **10.5pt** - Detailed information

#### Small Text (Captions & Notes)
- **9.75pt** - Captions and annotations
- **9pt** - Small labels and detailed information (ABSOLUTE MINIMUM)

> **⚠️ CRITICAL RULE: 9pt Font Minimum**
>
> **No text shall be smaller than 9pt under any circumstances.**
>
> While the original presentation used smaller sizes (6-8.25pt), this created legibility issues.
> The updated standard enforces 9pt as the absolute minimum for all text, including:
> - Fine details and annotations
> - Footnotes and labels
> - Dense data tables
> - Micro-text and supplementary information
>
> **If content doesn't fit at 9pt:** Redesign the layout, reduce content, or split across slides.

### Font Usage Guidelines
- Maintain consistency within slide types
- Use larger sizes (15-21pt) sparingly for impact
- **9pt is the absolute minimum** - never go smaller
- Medium sizes (10-14pt) form the core of body content
- Small sizes (9-10pt) should be used sparingly for dense data only

---

## 3. MULTI-FORMAT TEXT BOXES

> **⚠️ NEW RULE:** Text boxes often contain multiple items with different formatting needs.
>
> This section covers handling label-description patterns and preventing text overflow.

### Label-Description Pattern

**When to Use:**
- Multiple items in one text box
- Each item has a category/label and details
- Need visual hierarchy within the box

**Formatting Standard:**

| Element | Format | Example |
|---------|--------|---------|
| **Label** | Bold, followed by colon | **"Smart Cities:"** |
| **Description** | Regular (not bold) | "DSR + GDI integration" |

**Result:** `Smart Cities: DSR + GDI integration`

### Implementation in PowerPoint

1. Type full line: "Label: Description text"
2. Select only "Label:" portion
3. Apply bold formatting (Ctrl+B)
4. Leave description as regular weight
5. Repeat for each item

### Color Rule for Multi-Item Boxes

**Use SINGLE color per content area:**
- Dark backgrounds → white text for all content
- Light backgrounds → dark color for all content
- Use bold/regular for hierarchy, NOT different colors

**Correct Example:**
```
[Blue Background Box]
  Smart Cities: DSR + GDI integration (all white)
  Maritime: GSI + BRI ports (all white)
```

**Incorrect Example:**
```
[Blue Background Box]
  Smart Cities: DSR + GDI integration (label orange, description white)
  Maritime: GSI + BRI ports (label green, description white)
```

### Preventing Text Overflow

**Problem:** Text running past box edges, appearing cut off.

**Solution:** Calculate required box height BEFORE creating box.

#### Box Height Formula

```
Required Height = (Number of items × Line height) + Padding + Safety margin

Where:
  Line height = Font size × 1.3 ÷ 72 (converts pt to inches)
  Padding = 0.08" (top) + 0.10" (bottom) = 0.18"
  Safety margin = 20% of content height
```

#### Quick Reference Chart

For 10pt font with label-description pattern:

| Items | Minimum Height | Recommended |
|-------|----------------|-------------|
| **1** | 0.40" | 0.50" |
| **2** | 0.60" | 0.75" |
| **3** | 0.80" | 1.00" |
| **4** | 1.00" | 1.25" |
| **5** | 1.20" | 1.50" |

For 9pt font (minimum), subtract 0.05" from each value.

> **⚠️ CRITICAL: Account for Padding in Box Height!**
>
> **Common Error:** Creating boxes without accounting for internal padding.
>
> **Example of the problem:**
> ```
> Box height: 0.24"
> Padding (0.08" + 0.10"): -0.18"
> Available for text: 0.06" (WRONG! Can't fit any text!)
> ```
>
> **Correct calculation:**
> ```
> Need 2 lines of 9pt text: 2 × 0.163" = 0.326"
> Add padding: 0.326" + 0.18" = 0.506"
> Box height needed: 0.50" minimum
> ```
>
> **Rule:** Always add 0.18" (padding) + 20% (safety) to your text height calculation!

### Text Overflow Prevention Checklist

**Before Creating Box:**
- [ ] Count number of items needed
- [ ] Calculate required height using formula or chart
- [ ] Add 20% safety margin to height

**While Creating Box:**
- [ ] Enable word wrap (Format Shape → Text Box → Wrap text)
- [ ] Set internal padding (0.08" top, 0.10" bottom, 0.10" sides)
- [ ] Set line spacing to Multiple 1.3

**After Adding Content:**
- [ ] View at 100% zoom to verify all text visible
- [ ] Check 0.10" space exists below last line
- [ ] Verify no text touches box edges
- [ ] Test with slightly longer text if needed

**If Text Doesn't Fit:**
1. **Preferred:** Increase box height by 0.20" - 0.30"
2. **Alternative:** Shorten descriptions or use abbreviations
3. **Last Resort:** Reduce font size (never below 9pt)

### Example from Slide 9

**Domain Overlap Zones box:**
- 3 items with label-description pattern
- Font: 10pt Arial
- Box dimensions: 3.2" wide × 1.8" tall
- Format: "Label:" (bold) + " description" (regular)
- Color: White on blue background
- Result: All text visible, no overflow

**Technology Transfer Mechanisms box:**
- 3 items with label-description pattern
- Font: 10pt Arial
- Box dimensions: 3.2" wide × 1.8" tall
- Format: "Label:" (bold) + " description" (regular)
- Color: White on green background
- Result: All text visible, no overflow

### Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Box too small | Text cut off at bottom | Increase height 0.20"-0.30" |
| No bold labels | Hard to scan items | Bold labels, regular descriptions |
| Multiple colors | Looks chaotic | Single color, use bold for hierarchy |
| Font below 9pt | Violates standard | Use 9pt minimum, bigger box if needed |
| No word wrap | Text runs off side | Enable word wrap |
| Wrong vertical alignment | Text sits at bottom or bleeds | Set vertical anchor to TOP or MIDDLE |

### Vertical Alignment (CRITICAL)

> **⚠️ NEW RULE:** Text boxes must have proper vertical alignment set to prevent text from sitting at the bottom or bleeding into other boxes.

**PowerPoint Setting:** Format Shape → Text Box → Vertical alignment

**Standard Vertical Alignment Rules:**

| Box Type | Vertical Alignment | Reason |
|----------|-------------------|--------|
| **Content boxes** | TOP | Text starts at top with padding |
| **Title/Header boxes** | MIDDLE | Centers text vertically in box |
| **Single-line labels** | MIDDLE | Centers short text in container |
| **Multi-line content** | TOP | Predictable text flow from top |

**How to Set in PowerPoint:**
1. Right-click text box → Format Shape
2. Text Options → Text Box
3. Vertical alignment → Select "Top" or "Middle"

**Common Issues:**

| Issue | Cause | Fix |
|-------|-------|-----|
| Text at bottom of box | Default/Bottom alignment | Set to TOP |
| Text bleeding into box below | Box too small + wrong alignment | Set TOP + increase height |
| Title not centered in header bar | TOP alignment used | Set to MIDDLE |
| Inconsistent appearance | Mixed alignment settings | Standardize to TOP for content |

**Example from Slide 9:**

**Title in red bar:**
- Box height: Same as red bar (0.6")
- Vertical alignment: MIDDLE
- Result: Text perfectly centered in colored bar

**Initiative descriptions:**
- Box height: Calculated for content
- Vertical alignment: TOP
- Result: Text starts at top, doesn't bleed into boxes below

**Bottom section boxes:**
- Box height: Generous with safety margin
- Vertical alignment: TOP
- Result: Predictable layout, no overflow

---

## 4. SPACING AND PADDING

> **⚠️ CRITICAL ISSUE IDENTIFIED:**
>
> The original presentation has **ZERO internal padding** in text boxes, causing:
> - Text touching the bottom edge of boxes
> - Text appearing cramped and hard to read
> - Risk of text overflow/clipping
>
> **This section provides mandatory fixes to resolve these spacing issues.**

### Text Box Internal Padding (MANDATORY)

**Problem:** All text boxes in the original have 0.000" padding on all sides.

**Required Fix:** Set internal margins for ALL text boxes:

| Side | Minimum | Recommended | Purpose |
|------|---------|-------------|---------|
| **Top** | 0.05" | 0.08" | Prevents text from touching top edge |
| **Bottom** | 0.08" | **0.10"** | **CRITICAL:** Prevents text from touching bottom |
| **Left** | 0.08" | 0.10" | Breathing room on left side |
| **Right** | 0.08" | 0.10" | Breathing room on right side |

### How to Set in PowerPoint:
1. Right-click text box → **Format Shape**
2. **Text Options** → **Text Box** tab
3. Set **Internal Margins:**
   - Top: 0.08"
   - Bottom: 0.10"
   - Left: 0.10"
   - Right: 0.10"

### Line Spacing Standards

**Problem:** Original uses inflexible explicit point values for line spacing.

**Solution:** Use proportional "Multiple" line spacing:

#### Body Text (9-14pt fonts):
- **Line Spacing:** 1.2 - 1.4 (Multiple)
- Example: 10pt font → 12-14pt spacing automatically
- **Why:** Scales properly if font size changes

#### Headings (15-21pt fonts):
- **Line Spacing:** 1.1 - 1.3 (Multiple)
- Example: 18pt font → 19.8-23.4pt spacing
- **Why:** Tighter spacing for impact

**Setting in PowerPoint:**
- Format → Paragraph → Line Spacing
- Select **"Multiple"** (not "Exactly")
- Enter: 1.2, 1.3, or 1.4

### Paragraph Spacing Standards

**Problem:** Original has minimal paragraph spacing (0.2-0.6pt average).

**Required Standards:**

| Context | Space Before | Space After |
|---------|--------------|-------------|
| **Standard body paragraphs** | 6pt | 6pt |
| **After headings** | 0pt | 8-10pt |
| **Before headings** | 10-12pt | 6pt |
| **Bullet points** | 3pt | 3pt |

### Text Box to Text Box Spacing

**Problem:** Inconsistent gaps between text boxes (0.003" to 2.239").

**Required Standards:**

| Context | Gap Size | Notes |
|---------|----------|-------|
| **Between content sections** | 0.30" | Standard spacing |
| **Title to body** | 0.25" - 0.35" | Keeps title connected to content |
| **Minimum gap** | 0.20" | Never closer than this |
| **Maximum gap** | 0.50" | Avoids disconnected appearance |

### Spacing Quick Reference

```
TEXT BOX INTERNAL PADDING:
  All sides: 0.08-0.10" (6-7 pixels)
  Bottom padding is CRITICAL: 0.10" minimum

LINE SPACING:
  Body text: Multiple 1.2-1.4
  Headings: Multiple 1.1-1.3

PARAGRAPH SPACING:
  Standard: 6pt before and after
  Around headings: 10pt before, 8pt after

TEXT BOX GAPS:
  Standard: 0.30"
  Title-to-body: 0.25-0.35"
```

### Visual Representation

**INCORRECT (Original - Zero Padding):**
```
┌────────────────────┐
│Title Text Here     │ ← Touches top
│Body text starts... │ ← Touches edges
│...and ends here    │ ← Touches bottom
└────────────────────┘
```

**CORRECT (With Proper Padding):**
```
┌────────────────────┐
│                    │ ← 0.08" top padding
│  Title Text Here   │
│                    │ ← 6pt paragraph space
│  Body text starts  │
│  ...and ends here  │
│                    │ ← 0.10" bottom padding
└────────────────────┘
```

### Implementation Checklist

**For Every Text Box:**
- [ ] Set top padding: 0.08"
- [ ] Set bottom padding: 0.10" (critical!)
- [ ] Set left/right padding: 0.10"
- [ ] Change line spacing from "Exactly" to "Multiple" (1.3x)
- [ ] Add 6pt space before/after paragraphs

**Testing:**
- [ ] Text does not touch any edge of the box
- [ ] Bottom space is clearly visible
- [ ] No text overflow or clipping
- [ ] Spacing feels comfortable

---

## 5. COLOR PALETTE

### Primary Color System
The presentation uses a defined 6-color palette:

#### Core Brand Colors
1. **White:** `#ffffff` - Dominant color, backgrounds and text
   - Usage: 36 instances across slides
   - Primary use: Text on dark backgrounds, shape fills

2. **Orange:** `#f39c12` - Secondary brand color
   - Usage: 18 instances
   - Primary use: Accent elements, highlights, category markers

3. **Red:** `#c8102e` - Strong accent color
   - Usage: 13 instances
   - Primary use: Important callouts, warnings, emphasis

4. **Blue:** `#2e6ba8` - Professional accent
   - Usage: 8 instances
   - Primary use: Data visualization, professional elements

5. **Green:** `#27ae60` - Positive/growth indicator
   - Usage: 8 instances
   - Primary use: Positive metrics, growth indicators

6. **Secondary Orange:** `#e67e22` - Alternative accent
   - Usage: 2 instances (rare)
   - Primary use: Variation on primary orange

7. **Gray:** `#95a5a6` - Neutral element
   - Usage: 1 instance (rare)
   - Primary use: De-emphasized content, neutral backgrounds

8. **Dark Slate:** `#2c3e50` - Slide background
   - Usage: Slide backgrounds (e.g., Slide 9)
   - Primary use: Dark background for high-contrast presentations
   - RGB: (44, 62, 80)

### Text Color Rules
- **White (#ffffff):** Dominant text color - 190 uses
  - Use on all dark or colored backgrounds
  - Primary text for most content

- **Orange (#f39c12):** Secondary text - 15 uses
  - Highlight key terms or numbers
  - Category labels

- **Red (#c8102e):** Emphasis text - 7 uses
  - Critical information
  - Warnings or important metrics

- **Gray (#95a5a6):** De-emphasized text - 6 uses
  - Supplementary information
  - Background data

- **Green (#27ae60):** Positive indicators - 5 uses
  - Growth metrics
  - Positive outcomes

### Shape Fill Color Rules
- **White (#ffffff):** 31 uses - Most common fill
- **Red (#c8102e):** 8 uses - High-priority elements
- **Orange (#f39c12):** 7 uses - Standard accent boxes
- **Green (#27ae60):** 4 uses - Positive elements
- **Blue (#2e6ba8):** 1 use - Rare, specific purposes

### Color Usage Principles
1. White is the foundation - use liberally for text and backgrounds
2. Use colored text sparingly - white should dominate
3. Orange and red are your primary accent colors
4. Blue and green are supporting accents for specific meanings
5. Maintain color consistency for similar element types across slides

---

## 6. LAYOUT STANDARDS

### Body Text Positioning
Based on analysis of 8 major text blocks:
- **Left Margin:** 1.09" from left edge
- **Top Position:** 4.50" from top (lower half positioning)
- **Width:** 7.95" (leaves ~1" margin on right)
- **Height:** 0.48" average per text block

### Layout Principles
1. **Left Margin:** Maintain ~1" margin from left edge
2. **Right Margin:** Maintain ~1" margin from right edge (calculated from 10" width)
3. **Content Area:** 8" wide usable space for main content
4. **Vertical Positioning:** Body content typically in lower half (below 4.5" mark)

### Spacing Guidelines
- Use consistent spacing between elements
- Lower half of slide (below vertical center) is primary content area
- Upper portion reserved for headers/titles or visual elements

---

## 7. TEXT ALIGNMENT

### Alignment Distribution
- **Left Aligned:** 108 instances (primary alignment)
  - Use for: Body text, bullet points, paragraphs, data
  - Default alignment for most content

- **Center Aligned:** 90 instances (common)
  - Use for: Titles, headers, standalone labels
  - Balanced distribution suggests both are acceptable

### Alignment Rules
1. **Body content:** Default to left alignment
2. **Titles and headers:** Center or left based on slide type
3. **Data tables:** Left align for readability
4. **Labels and callouts:** Center when standalone
5. Maintain consistency within each slide

---

## 8. SHAPE AND ELEMENT USAGE

### Shape Distribution
Analyzed across 305 total shapes:

1. **Auto Shapes:** 274 instances (90%)
   - Rectangles, rounded rectangles, circles
   - Primary building blocks for all layouts
   - Use for: backgrounds, containers, dividers, callout boxes

2. **Pictures:** 29 instances (9%)
   - Photos, logos, visual elements
   - Moderate but consistent use of imagery
   - Average: 4-5 images per slide

3. **Groups:** 2 instances (1%)
   - Complex composite elements
   - Rare use - only when necessary

### Shape Usage Guidelines
- **Rectangles/boxes** are the foundation - use extensively
- **Images** should appear on most slides (4-5 per slide typical)
- Keep shapes simple - avoid complex custom shapes
- Group elements only when needed for reuse

---

## 9. SLIDE COMPLEXITY

### Shape Count Guidelines
Based on per-slide analysis:
- **Minimum:** 29 shapes (Slide 3)
- **Maximum:** 63 shapes (Slide 5)
- **Average:** ~51 shapes per slide

### Complexity Rules
1. **Standard slides:** 45-50 shapes is typical
2. **Simple slides:** 30-40 shapes minimum
3. **Complex slides:** 60+ shapes acceptable
4. **Element density:** These are data-rich, detailed slides
5. Don't shy away from complexity when showing detailed information

---

## 10. DESIGN PATTERNS & BEST PRACTICES

### Visual Hierarchy
1. **Size differentiation:** 3-4 distinct font sizes per slide
2. **Color coding:** Use consistent colors for similar element types
3. **White space:** Balance dense content with breathing room
4. **Emphasis:** Use color (red, orange) for key elements

### Consistency Rules
1. **Font:** Never deviate from Arial
2. **Colors:** Stick to the 6-color palette
3. **Alignment:** Be consistent within each slide type
4. **Spacing:** Maintain consistent margins and padding

### Content Density
- These slides support high information density
- 50+ shapes per slide is normal and acceptable
- **Small text (9-10pt minimum)** for detailed content - never smaller than 9pt
- Balance density with clear visual organization
- If content requires text smaller than 9pt, the slide needs redesign

---

## 11. QUICK REFERENCE CHECKLIST

### Before Creating a Slide:
- [ ] Slide set to 10" × 5.62" (16:9)
- [ ] Arial font selected
- [ ] Color palette reference ready
- [ ] Layout margins planned (1" on sides)
- [ ] Text box padding template ready (0.08" top, 0.10" bottom/sides)

### While Designing:
- [ ] White (#ffffff) as primary text color
- [ ] Body text between 9-14pt
- [ ] Headers between 15-21pt
- [ ] **Text box padding set:** 0.08" top, 0.10" bottom, 0.10" sides
- [ ] **Vertical alignment set:** TOP for content, MIDDLE for titles
- [ ] **Line spacing:** Multiple 1.2-1.4 (body) or 1.1-1.3 (headings)
- [ ] **Paragraph spacing:** 6pt before/after
- [ ] **Multi-item boxes:** Calculate height using formula (Section 3)
- [ ] **Label-description pattern:** Bold labels, regular descriptions
- [ ] **Word wrap enabled** on all text boxes
- [ ] Left or center alignment (consistent per element type)
- [ ] 40-60 shapes is target range
- [ ] 4-5 images if using visuals
- [ ] 0.30" gaps between text boxes

### Before Finalizing:
- [ ] Only colors from the 6-color palette used
- [ ] Font sizes follow established hierarchy
- [ ] **NO text smaller than 9pt** (critical rule)
- [ ] **Text does NOT touch bottom of any text box** (critical!)
- [ ] All text boxes have proper internal padding
- [ ] Line spacing is proportional (Multiple), not fixed (Exactly)
- [ ] Text alignment is consistent
- [ ] Spacing between elements is 0.20" minimum
- [ ] Visual hierarchy is clear

---

## 12. COLOR PALETTE REFERENCE (Copy-Paste Ready)

```
Primary White:     #ffffff (RGB: 255, 255, 255)
Primary Orange:    #f39c12 (RGB: 243, 156, 18)
Primary Red:       #c8102e (RGB: 200, 16, 46)
Professional Blue: #2e6ba8 (RGB: 46, 107, 168)
Growth Green:      #27ae60 (RGB: 39, 174, 96)
Alt Orange:        #e67e22 (RGB: 230, 126, 34)
Neutral Gray:      #95a5a6 (RGB: 149, 165, 166)
Dark Slate:        #2c3e50 (RGB: 44, 62, 80)  [Slide Background]
```

---

## 13. COMMON USE CASES

### Data-Heavy Slide
- **Font sizes:** Mix of 9pt, 9.75pt, 10.5pt for data (9pt minimum enforced)
- **Colors:** White text with orange/red highlights
- **Shapes:** 50-60+ shapes
- **Layout:** Dense but organized

### Title/Section Slide
- **Font sizes:** 19.5-21pt for title
- **Colors:** Strong color backgrounds (red, orange)
- **Alignment:** Center aligned
- **Shapes:** 30-40 shapes (simpler)

### Content Slide
- **Font sizes:** 11-14pt for body
- **Colors:** White text dominant
- **Alignment:** Left aligned for readability
- **Shapes:** 45-50 shapes (standard)

---

## END OF RULEBOOK

This style guide is derived from empirical analysis of slides 3-8 of MCF v2.1.pptx
All measurements, frequencies, and patterns are based on actual usage in the source presentation.

**When in doubt:** Reference the original slides 3-8 for visual confirmation of these patterns.
