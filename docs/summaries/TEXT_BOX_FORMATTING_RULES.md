# Text Box Formatting Rules - Multi-Format Text
## Critical Style Guide Addition

Based on analysis of Slide 9, here are the rules for handling complex text formatting within text boxes.

---

## ISSUE IDENTIFIED

**Problem:** Text boxes with multiple items need:
1. Different formatting for labels vs. descriptions (bold vs. regular)
2. Proper sizing to prevent text overflow
3. Consistent pattern across similar boxes

**Example from Slide 9:**
```
Domain Overlap Zones box contains:
  "Smart Cities:" (bold) + "DSR + GDI integration" (regular)
  "Maritime:" (bold) + "GSI + BRI ports" (regular)
  "Standards:" (bold) + "DSR + GSI + GAGI" (regular)
```

---

## RULE 1: Label-Description Pattern

### When to Use
Use this pattern for bulleted or list-style content within a text box:
- Multiple items in one box
- Each item has a category/label and details
- Need visual hierarchy within the box

### Formatting Standard

**Label (Category/Topic):**
- **Font weight:** Bold
- **Followed by:** Colon (:)
- **Purpose:** Draw attention, create scannable structure

**Description (Details):**
- **Font weight:** Regular (not bold)
- **Preceded by:** Space after colon
- **Purpose:** Provide information without competing with label

### Example Implementation
```
Label: Description text here
Label: Description text here
Label: Description text here
```

**PowerPoint Implementation:**
1. Type full line: "Label: Description"
2. Select only "Label:"
3. Apply bold formatting
4. Leave description as regular weight

---

## RULE 2: Font Size Within Boxes

### Current Practice (from Slide 9)
Different boxes use different sizes based on content density:

| Box Type | Font Size | Use Case |
|----------|-----------|----------|
| **Dense content** | 10pt | Multiple long items (Technology Transfer) |
| **Medium content** | 13.5pt | Moderate items (Domain Overlap) |
| **Sparse content** | 11-14pt | Few items, more space |

### New Standard (Style Guide Compliant)

**All text in content boxes must be 9pt minimum:**

| Content Density | Recommended Size | Rule |
|-----------------|------------------|------|
| **High density** (3+ items, long descriptions) | 9pt | Minimum allowed |
| **Medium density** (2-3 items, medium descriptions) | 10pt | Better readability |
| **Low density** (1-2 items, short descriptions) | 11pt | Most comfortable |

**CRITICAL:** Never go below 9pt, even for dense content.

---

## RULE 3: Preventing Text Overflow

### The Problem
Text 34 (Technology Transfer box) analysis shows:
```
Total characters: 139
Box height: 1.461"
WARNING: Long text in relatively small box
```

This causes text to run past the box edges.

### Prevention Rules

#### Step 1: Calculate Required Height
Use this formula for multi-line content:

```
Required Height = (Number of lines × Line height) + Top padding + Bottom padding

Where:
  Line height = Font size × Line spacing multiplier (1.3)
  Top padding = 0.08"
  Bottom padding = 0.10"

Example for 3 lines of 10pt text:
  Line height = 10pt × 1.3 = 13pt = 0.18"
  Total text height = 3 × 0.18" = 0.54"
  Box height needed = 0.54" + 0.08" + 0.10" = 0.72"
```

#### Step 2: Add Safety Margin
Always add 15-20% extra space to prevent overflow:

```
Final box height = Required height × 1.15 to 1.20
```

#### Step 3: Test Before Finalizing
**Checklist:**
- [ ] All text visible in box
- [ ] No text cut off at bottom
- [ ] At least 0.10" visible space below last line
- [ ] Text doesn't touch box edges

### Box Sizing Chart

For label-description pattern with 9-10pt font:

| Number of Items | Estimated Height | Notes |
|-----------------|------------------|-------|
| **1 item** | 0.40" - 0.50" | Single line + padding |
| **2 items** | 0.60" - 0.75" | Two lines + padding |
| **3 items** | 0.80" - 1.00" | Three lines + padding |
| **4 items** | 1.00" - 1.25" | Four lines + padding |
| **5+ items** | 1.25" - 1.60" | Consider splitting box |

**These are MINIMUMS - add safety margin!**

---

## RULE 4: Text Box Overflow Prevention Checklist

### Before Creating Text Box:
1. [ ] Count number of items/lines needed
2. [ ] Calculate required height using formula
3. [ ] Add 15-20% safety margin
4. [ ] Set internal padding (0.08" top, 0.10" bottom)

### While Adding Content:
5. [ ] Use label-description pattern (bold:regular)
6. [ ] Font size 9pt minimum
7. [ ] Line spacing set to Multiple 1.3
8. [ ] Word wrap enabled

### After Adding Content:
9. [ ] View at 100% zoom to check visibility
10. [ ] Verify last line has 0.10" space below it
11. [ ] Check no text touches box edges
12. [ ] Test with slightly longer text (edge case)

### If Text Doesn't Fit:
**Option A (Preferred):** Increase box height
- Add 0.15" - 0.25" to height
- Maintain aspect ratio

**Option B:** Reduce content
- Shorten descriptions
- Use abbreviations
- Split across multiple boxes

**Option C (Last Resort):** Reduce font size
- Only if already above 10pt
- Never go below 9pt
- Recalculate line spacing

---

## RULE 5: Color Within Text Boxes

### Current Practice
Slide 9 uses **single color per box**:
- Domain Overlap: White (#ffffff) throughout
- Technology Transfer: White (#ffffff) throughout

### New Standard

**For content boxes with dark backgrounds:**
- Use white (#ffffff) for ALL text
- Use bold/regular weight for hierarchy (NOT different colors)

**For content boxes with light backgrounds:**
- Use dark colors from palette for ALL text
- Same rule: bold/regular for hierarchy

**Exception:** Title/header can use accent color, content remains one color

### Example (Correct)
```
[Blue Background Box]
  "Smart Cities:" (white, bold) + "DSR + GDI integration" (white, regular)
  "Maritime:" (white, bold) + "GSI + BRI ports" (white, regular)
```

### Example (Incorrect)
```
[Blue Background Box]
  "Smart Cities:" (orange, bold) + "DSR + GDI integration" (white, regular)
  "Maritime:" (green, bold) + "GSI + BRI ports" (white, regular)
```

**Why:** Multiple colors in one content box creates visual chaos.

---

## IMPLEMENTATION GUIDE

### PowerPoint Setup for Label-Description Boxes

#### 1. Create Text Box
- Width: Based on content (typically 1.5" - 3.5")
- Height: Use calculation formula + safety margin
- Internal padding: 0.08" top, 0.10" bottom, 0.10" sides

#### 2. Set Text Frame Properties
- **Word wrap:** ON (enabled)
- **Auto size:** None (fixed size)
- **Vertical alignment:** Top
- **Line spacing:** Multiple 1.3

#### 3. Add Content
For each item:
```
1. Type: "Label: Description text here"
2. Press Enter for next item
3. Repeat for all items
```

#### 4. Format Labels
```
1. Select first label text + colon (e.g., "Smart Cities:")
2. Apply: Bold
3. Repeat for each label
4. Leave descriptions as regular weight
```

#### 5. Verify
- Check all text visible
- Ensure 0.10" space at bottom
- Verify bold formatting on labels only

---

## COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Box Too Small
**Problem:** Text cut off at bottom
**Solution:** Increase height by 0.20" - 0.30"

### ❌ Mistake 2: No Bold Formatting
**Problem:** All text same weight, hard to scan
**Solution:** Bold the labels, keep descriptions regular

### ❌ Mistake 3: Inconsistent Font Sizes
**Problem:** Different sizes for different items in same box
**Solution:** Use one size for entire box content

### ❌ Mistake 4: Multiple Colors in Content
**Problem:** Rainbow effect, looks unprofessional
**Solution:** One color for all content, use bold for hierarchy

### ❌ Mistake 5: Font Below 9pt
**Problem:** Violates readability standard
**Solution:** Use 9pt minimum, increase box size if needed

---

## SLIDE 9 SPECIFIC STANDARDS

### Domain Overlap Zones Box
```
Dimensions: 3.2" wide × 1.7" tall (minimum)
Font: Arial 10pt (or 9pt if space constrained)
Color: White (#ffffff) on blue background
Pattern: 3 items with label-description
Format: "Label:" (bold) + " description" (regular)
Spacing: 6pt between items
```

### Technology Transfer Mechanisms Box
```
Dimensions: 3.2" wide × 1.7" tall (minimum)
Font: Arial 10pt (or 9pt if space constrained)
Color: White (#ffffff) on green background
Pattern: 3 items with label-description
Format: "Label:" (bold) + " description" (regular)
Spacing: 6pt between items
```

### Initiative Boxes (DSR, GSI, etc.)
```
Each box:
  Width: 1.76"
  Height: 0.52" for description area
  Font: Arial 9pt minimum
  Color: Respective accent color on white
  Format: Plain text, center aligned
```

---

## QUICK REFERENCE

### Text Box Sizing Formula
```
Height = (Lines × Font_Size × 1.3 ÷ 72) + 0.08" + 0.10" + 20% safety
```

### Formatting Pattern
```
"Label:" → Bold, accent or white color
" Description" → Regular, same color
```

### Overflow Prevention
```
1. Calculate required height
2. Add 20% safety margin
3. Set proper internal padding
4. Enable word wrap
5. Test with actual content
6. Add space if needed
```

---

## VALIDATION CHECKLIST

Use this to verify text boxes meet standards:

### Box Setup
- [ ] Height calculated using formula
- [ ] 20% safety margin added
- [ ] Internal padding: 0.08" top, 0.10" bottom, 0.10" sides
- [ ] Word wrap enabled
- [ ] Line spacing: Multiple 1.3

### Content Formatting
- [ ] All text 9pt or larger
- [ ] Labels are bold
- [ ] Descriptions are regular weight
- [ ] Single color throughout content
- [ ] 6pt spacing between items

### Overflow Check
- [ ] All text visible
- [ ] 0.10" space below last line
- [ ] No text touching edges
- [ ] Tested at 100% zoom
- [ ] Looks professional

---

## SUMMARY

**Key Rules:**
1. Use bold for labels, regular for descriptions
2. 9pt font minimum always
3. Calculate box height with formula
4. Add 20% safety margin
5. Single color per content area
6. Enable word wrap
7. Test for overflow before finalizing

**Most Common Fix:**
If text overflows → Increase box height by 0.20" - 0.30"

**Never:**
- Go below 9pt font
- Use multiple colors in content
- Let text touch box edges
- Skip padding settings
