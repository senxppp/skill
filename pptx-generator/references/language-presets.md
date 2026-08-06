# Language Presets — 中文 / English

When creating presentations, the language (`lang`) determines fonts, typography conventions, numbering/date styles, and cultural context. Always match content language to its preset.

| Parameter | Value | Default |
|-----------|-------|---------|
| `lang` | `"zh"` (Chinese) or `"en"` (English) | `"zh"` |

## Chinese Preset (`lang: "zh"`)

### Fonts

| Role | Font |
|------|------|
| Title / Heading | Microsoft YaHei Bold |
| Body text | Microsoft YaHei Regular |
| Numbers & English words mixed in CJK | Microsoft YaHei (same as CJK text) |

### Typography Conventions

- All headings use **bold** weight
- Body paragraphs use regular weight (not bold)
- Page numbers: Arabic numerals `1`, `2`, `3`...
- Bullet markers: `-` or `•` (consistent across deck)
- Date format: `YYYY年MM月DD日` (e.g., `2025年8月4日`)
- Section numbering: `01`, `02`... (Arabic with zero-pad) or Chinese numerals `一、二、三、` for formal/academic

### Cultural Context Notes

- For academic lectures, use formal tone and Chinese numeral section headers (`一、二、三`)
- For business/pitch decks, modern tone with Arabic numeral sections (`01`, `02`)
- Avoid Western-specific idioms, sports references, or holiday mentions unless intentional

---

## English Preset (`lang: "en"`)

### Fonts

| Role | Font Pairing | Example |
|------|-------------|---------|
| Title / Heading | Georgia Bold + Calibri Light body | `fontFace: "Georgia"` |
| Title / Heading | Arial Black + Arial body | `fontFace: "Arial Black"` |
| Title / Heading | Cambria Bold + Calibri body | `fontFace: "Cambria"` |
| Title / Heading | Trebuchet MS Bold + Calibri body | `fontFace: "Trebuchet MS"` |
| Title / Heading | Impact + Arial body | `fontFace: "Impact"` |
| Code / Monospace | Consolas | `fontFace: "Consolas"` |

**Always pick an interesting header/body font pairing from [design-system.md#font-reference](design-system.md#font-reference). Do NOT default to Arial everywhere.**

For code-heavy or technical decks, prefer a monospaced footer/annotation style using `fontFace: "Consolas"`.

### Typography Conventions

- Only **titles and headings** use bold. Body text is plain (never bold for emphasis).
- Page numbers: Arabic numerals `1`, `2`, `3`... right-aligned badge
- Bullet markers: `-` or custom SVG shapes (consistent across deck)
- Date format: `Month DD, YYYY` (e.g., `August 4, 2025`) or `MM/DD/YYYY`
- Numbered lists: `(1)`, `(2)` or `1.`, `2.` depending on formality
- Capitalization: Title Case for slide titles (major words capitalized); Sentence case for subtitles

### Capitalization Rules

| Element | Style | Example |
|---------|-------|---------|
| Slide title | Title Case | "Market Analysis & Growth Strategy" |
| Subtitle / Section | Sentence case | "Q3 performance review" |
| Tag / Label | UPPERCASE | "CONFIDENTIAL", "INTERNAL ONLY" |
| Navigation labels | UPPERCASE + wide tracking | "AGENDA", "NEXT STEPS" |

### Cultural Context Notes

- Business/professional: keep tone formal, data-driven, bullet-point heavy
- Creative/marketing: more narrative, larger visuals, fewer bullets
- Academic: structured citations, formal section numbering ("I.", "II.", "III.")
- Tech/startup: informal but precise, stat callouts, minimal text per slide
- Avoid culturally specific jokes or references unless the audience is specified
- Use metric units by default; add imperial conversions in brackets if international audience (e.g., `50 km (31 mi)`)

---

## Applying the Language Preset in Workflow

When following the [Creating from Scratch workflow](SKILL.md#creating-from-scratch-workflow), adjust these steps based on `lang`:

### Step 2: Select Color Palette & Fonts

After picking the palette, set the font rules:

```javascript
// For Chinese (lang: "zh")
const fontConfig = {
  fontFace: "Microsoft YaHei",
  fontFamily: "sans-serif"
};

// For English (lang: "en") — pick an interesting pairing!
const fontConfig = {
  fontFace: "Georgia",        // for titles
  fontFamily: "Calibri",      // for body
  titleFontFace: "Georgia",
  bodyFontFace: "Calibri"
};
```

### Step 5: Generate Slides

Each subagent must be told the language:

**Subagent instruction template:**

```
Language: EN (English)
Fonts: Header = Georgia, Body = Calibri
Capitalization: Title Case for slide titles
Date format: Month DD, YYYY (e.g. August 4, 2025)
Tone: Professional business
```

or

```
Language: ZH (Chinese)
Fonts: Microsoft YaHei for all text
Date format: YYYY年MM月DD日
Tone: Formal academic / Modern business (based on topic)
```

### Step 7b: QA Verification

When verifying with `python -m markitdown output.pptx`:

- **Chinese**: Check that no characters are garbled (mojibake), especially mixed CJK/Latin
- **English**: Check capitalization consistency, correct date format, proper punctuation (smart quotes vs straight quotes)

---

## Quick Reference Table

| Aspect | Chinese (`zh`) | English (`en`) |
|--------|---------------|----------------|
| Primary font | Microsoft YaHei | Varies (see below) |
| Title capitalization | N/A (no concept of cases) | Title Case |
| Body text bold? | No | No |
| Date format | YYYY年MM月DD日 | Month DD, YYYY |
| Page number | 1, 2, 3 | 1, 2, 3 |
| Section numbering | 01/02 or 一/二/三 | 01/02 or I/II/III |
| Unit system | SI/metric default | Metric + imperial conversion |
| Citation style | Author-Date or numeric | Depends on field (APA, MLA, etc.) |

### Recommended English Font Pairings

| Tone | Header | Body | When to Use |
|------|--------|------|-------------|
| Classic / Academic | Georgia | Calibri | Lectures, reports, formal papers |
| Corporate / Clean | Arial Black | Arial | Business pitches, annual reviews |
| Modern / Friendly | Calibri | Calibri Light | Internal comms, training materials |
| Bold / Attention | Cambria | Calibri | Product launches, keynote talks |
| Technical / Code | Consolas | Consolas | Engineering demos, API docs |
| Editorial / Magazine | Palatino | Garamond | Annual reports, storytelling decks |
