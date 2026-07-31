# CareerPilot AI — Locked Design System
### Apple HIG-Inspired Specification · v1.0

> **STATUS: 🔒 LOCKED**
> This document is the single source of truth for every visual decision in CareerPilot AI. Every color, spacing value, radius, shadow, font size, and component dimension listed here is **final**. Developers must not deviate from these values without explicit approval.

---

## 1. Design Philosophy

CareerPilot follows Apple's Human Interface Guidelines (HIG) principles adapted for web:

| Principle | Apple Term | CareerPilot Application |
|---|---|---|
| **Clarity** | Content is king | Text is legible at every size. Icons are precise. Whitespace is generous. |
| **Deference** | UI helps, never competes | Cards, backgrounds, and chrome are muted. Content and data are bold. |
| **Depth** | Visual layers communicate hierarchy | Shadows + border separations create clear z-axis. Cards float above the page. |
| **Consistency** | Same action = same appearance | Buttons, badges, cards, and banners look and behave identically everywhere. |
| **Direct Manipulation** | Touch = response | Hover lifts, focus rings, and transitions give immediate visual feedback. |

---

## 2. Color Palette — LOCKED 🔒

### 2.1 Brand Colors

The primary brand color is a refined **Apple-style blue** — the same system blue used across iOS, iPadOS, and macOS.

| Token | Hex | RGB | Usage | Swatch |
|---|---|---|---|---|
| `--cp-primary` | `#007AFF` | `0, 122, 255` | Primary buttons, links, active states, accents | 🟦 |
| `--cp-primary-hover` | `#0063D1` | `0, 99, 209` | Button hover, link hover | 🟦 (darker) |
| `--cp-primary-light` | `#E5F1FF` | `229, 241, 255` | Selected row bg, active badge bg, focus tint | 🔵 (very light) |
| `--cp-primary-ring` | `rgba(0,122,255,0.12)` | — | Focus rings on inputs | — |
| `--cp-shadow-primary` | `0 1px 3px rgba(0,122,255,0.30)` | — | Primary button glow | — |

### 2.2 Semantic Colors (Apple System Colors)

Each semantic color has **5 variants**: base, light bg, border, text-on-light, and hover.

#### ✅ Success / Green
| Token | Hex | Usage |
|---|---|---|
| `--cp-success` | `#34C759` | Score gauge ≥80, positive indicators |
| `--cp-success-light` | `#E8F9ED` | Badge bg, banner bg |
| `--cp-success-border` | `#A2E4B8` | Banner border |
| `--cp-success-text` | `#1B7A34` | Text on light green bg |

#### ❌ Danger / Red
| Token | Hex | Usage |
|---|---|---|
| `--cp-danger` | `#FF3B30` | Score gauge <60, missing skills |
| `--cp-danger-light` | `#FFF0EF` | Badge bg, banner bg |
| `--cp-danger-border` | `#FFCAC6` | Banner border |
| `--cp-danger-text` | `#B71C1C` | Text on light red bg |

#### ⚠️ Warning / Orange
| Token | Hex | Usage |
|---|---|---|
| `--cp-warning` | `#FF9500` | Score gauge 60–80, caution states |
| `--cp-warning-light` | `#FFF7E5` | Badge bg, banner bg |
| `--cp-warning-border` | `#FFD480` | Banner border |
| `--cp-warning-text` | `#8B5E00` | Text on light orange bg |

#### ℹ️ Info / Blue (Tint)
| Token | Hex | Usage |
|---|---|---|
| `--cp-info-light` | `#DBEAFE` | Info badges bg |
| `--cp-info-text` | `#1E40AF` | Text on light blue bg |

#### 🟣 Purple (Accent)
| Token | Hex | Usage |
|---|---|---|
| `--cp-purple-light` | `#EDE9FE` | Purple badges bg, special features |
| `--cp-purple-text` | `#5B21B6` | Text on light purple bg |

### 2.3 Neutral Palette (Apple System Grays)

Apple uses a 6-step gray scale. CareerPilot maps to these:

| Token | Hex | Apple Equivalent | Usage |
|---|---|---|---|
| `--cp-text` | `#1C1C1E` | Label (Primary) | Headlines, primary text |
| `--cp-text-secondary` | `#636366` | Label (Secondary) | Subtitles, descriptions, body copy |
| `--cp-text-muted` | `#AEAEB2` | Label (Tertiary) | Placeholders, disabled states, captions |
| `--cp-text-quaternary` | `#C7C7CC` | Label (Quaternary) | Very subtle hints, watermarks |
| `--cp-border` | `#D1D1D6` | Separator (Opaque) | Card borders, dividers, input borders |
| `--cp-border-hover` | `#66B2FF` | — | Input focus border, hover highlight |
| `--cp-bg` | `#F2F2F7` | System Grouped Background | Page background |
| `--cp-bg-card` | `#FFFFFF` | System Background | Card surfaces, input backgrounds |
| `--cp-bg-secondary` | `#F9F9FB` | Secondary System Grouped Bg | Alternate row, secondary cards |

### 2.4 Gradient Definitions

| Name | CSS | Usage |
|---|---|---|
| **Page ambient (top-right)** | `radial-gradient(circle, rgba(0,122,255,0.06), transparent 70%)` | `.stApp::before` |
| **Page ambient (bottom-left)** | `radial-gradient(circle, rgba(88,86,214,0.05), transparent 70%)` | `.stApp::after` |
| **Success gradient card** | `linear-gradient(135deg, #ECFDF5, #E8F9ED)` | `.cp-success-gradient` |
| **Mentor gradient card** | `linear-gradient(135deg, #EFF6FF, #DBEAFE)` | `.cp-mentor-card` |

### 2.5 Streamlit Theme Sync

These values must match in `.streamlit/config.toml`:

```toml
[theme]
base = "light"
primaryColor = "#007AFF"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F2F2F7"
textColor = "#1C1C1E"
font = "sans serif"
```

---

## 3. Typography — LOCKED 🔒

### 3.1 Font Stack

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display',
             'SF Pro Text', 'Segoe UI', 'Helvetica Neue', sans-serif;
```

Inter is the web equivalent of Apple's SF Pro. It shares the same optical sizes, variable weight axis, and tabular numerals.

**Google Fonts import:**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
```

### 3.2 Type Scale (4-pt Grid Aligned)

Every font size snaps to a 4-point baseline grid. Line heights are calculated to maintain vertical rhythm.

| Name | Size | Weight | Line-Height | Letter-Spacing | Usage |
|---|---|---|---|---|---|
| **Display** | `2.5rem` (40px) | 800 | `1.15` (46px) | `-0.025em` | Landing hero headline only |
| **H1** | `2rem` (32px) | 700 | `1.2` (38px) | `-0.022em` | Page titles |
| **H2** | `1.5rem` (24px) | 700 | `1.25` (30px) | `-0.018em` | Section headings |
| **H3** | `1.25rem` (20px) | 600 | `1.3` (26px) | `-0.015em` | Card titles, sub-sections |
| **H4** | `1.0625rem` (17px) | 600 | `1.35` (23px) | `-0.01em` | Small headings |
| **Body** | `0.9375rem` (15px) | 400 | `1.6` (24px) | `0` | Default paragraph text |
| **Body Small** | `0.875rem` (14px) | 400 | `1.55` (22px) | `0` | Secondary text, descriptions |
| **Caption** | `0.8125rem` (13px) | 500 | `1.45` (19px) | `0.01em` | Captions, hints, timestamps |
| **Overline** | `0.75rem` (12px) | 700 | `1.4` (17px) | `0.06em` | Step labels, badge text, metric labels (uppercase) |
| **Micro** | `0.6875rem` (11px) | 500 | `1.35` (15px) | `0.02em` | Privacy notes, file size hints |

### 3.3 Typography Rules

1. **Headings:** Always `color: var(--cp-text)`. Never gray.
2. **Body text:** `color: var(--cp-text-secondary)`.
3. **Accent words in headings:** Use `color: var(--cp-primary)` via a `<span>`.
4. **Numeric data:** Use `font-variant-numeric: tabular-nums` for metrics/scores so digits align.
5. **Uppercase text:** Only for overline labels (step tracker, metric labels, badge text). Never for headings or body.

---

## 4. Spacing System — LOCKED 🔒

### 4.1 Base Unit

**Base unit: `4px`**. All spacing values are multiples of 4px, following Apple's 4-pt grid.

### 4.2 Spacing Scale

| Token | Value | Shorthand | Usage Examples |
|---|---|---|---|
| `--space-0` | `0px` | `0` | Reset |
| `--space-1` | `4px` | `xs` | Icon-to-text gaps in tight layouts |
| `--space-2` | `8px` | `sm` | Badge padding (vertical), inline gaps |
| `--space-3` | `12px` | `md` | Input padding, small card gaps |
| `--space-4` | `16px` | `base` | Default element spacing, card internal gaps |
| `--space-5` | `20px` | `lg` | Card padding (sides), section bottom margins |
| `--space-6` | `24px` | `xl` | Between card groups, heading → content |
| `--space-8` | `32px` | `2xl` | Page section separators |
| `--space-10` | `40px` | `3xl` | Hero area padding, major section gaps |
| `--space-12` | `48px` | `4xl` | Page top/bottom padding |
| `--space-16` | `64px` | `5xl` | Landing hero spacing |

### 4.3 Component Spacing (Locked Dimensions)

| Component | Padding | Margin-Bottom | Gap (if flex/grid) |
|---|---|---|---|
| **Card (`.cp-card`)** | `24px 28px` (top/bottom, left/right) | `20px` | — |
| **Status Banner** | `16px 20px` | `16px` | — |
| **Badge** | `5px 14px` | — | `4px 6px` (margin between badges) |
| **Button (Primary)** | `0 28px` (height: `48px`) | — | — |
| **Button (Small)** | `0 20px` (height: `36px`) | — | — |
| **Input Field** | `12px 16px` | — | — |
| **Navbar** | `12px 0` | `32px` | — |
| **Step Tracker** | — | `24px` | `8px` between bars |
| **Metric Value** | `8px` | — | — |
| **Decision Card** | `28px` | — | — |
| **Gradient Card** | `32px` | `20px` | — |
| **Compare Grid** | `20px` | — | `16px` between panels |

### 4.4 Layout Constraints

| Constraint | Value | Reason |
|---|---|---|
| **Max content width** | `1200px` | Readability on wide screens |
| **Card max-width** | `none` (fills container) | Cards stretch to column |
| **Column gap** | `16px` (Streamlit default) | Standard Streamlit grid |
| **Page padding-top** | `16px` | Minimal after navbar |
| **Page padding-bottom** | `48px` | Breathing room at footer |

---

## 5. Corner Radius — LOCKED 🔒

Apple uses continuous (squircle) corners. On the web, we approximate with `border-radius`.

| Token | Value | Usage |
|---|---|---|
| `--cp-radius-xs` | `6px` | Inline code blocks, micro-badges |
| `--cp-radius-sm` | `10px` | Input fields, sidebar nav buttons |
| `--cp-radius-md` | `14px` | Status banners, expanders, tabs |
| `--cp-radius-lg` | `20px` | Cards, modals, dialogs |
| `--cp-radius-xl` | `24px` | Landing hero cards, glassmorphic overlays |
| `--cp-radius-full` | `999px` | Buttons, badges, progress bars, toggles |

### Radius Rules

1. **Buttons:** Always `999px` (full pill).
2. **Cards:** Always `20px`.
3. **Inputs:** Always `10px`.
4. **Badges:** Always `999px`.
5. **Nested elements:** Inner radius = outer radius − padding. (e.g., card at 20px with 24px padding → inner element can be 14px or less.)

---

## 6. Shadow & Elevation — LOCKED 🔒

Shadows follow Apple's layered shadow model: a tight shadow for definition + a broad ambient shadow.

| Token | Value | Elevation | Usage |
|---|---|---|---|
| `--cp-shadow-none` | `none` | 0 | Flat elements, disabled states |
| `--cp-shadow-xs` | `0 1px 2px rgba(0,0,0,0.04)` | 1 | Badges on hover, subtle lift |
| `--cp-shadow-sm` | `0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.03)` | 2 | Cards at rest, inputs |
| `--cp-shadow-md` | `0 4px 16px rgba(0,0,0,0.07), 0 8px 24px rgba(0,0,0,0.04)` | 3 | Cards on hover, popovers |
| `--cp-shadow-lg` | `0 8px 32px rgba(0,0,0,0.10), 0 16px 48px rgba(0,0,0,0.06)` | 4 | Modals, floating panels |
| `--cp-shadow-primary` | `0 2px 8px rgba(0,122,255,0.25)` | — | Primary button at rest |
| `--cp-shadow-primary-hover` | `0 4px 14px rgba(0,122,255,0.35)` | — | Primary button on hover |

### Elevation Rules

1. **Page background** = Elevation 0 (no shadow).
2. **Cards at rest** = Elevation 2 (`--cp-shadow-sm`).
3. **Cards on hover** = Elevation 3 (`--cp-shadow-md`), transition `0.25s ease`.
4. **Modals/overlays** = Elevation 4 (`--cp-shadow-lg`).
5. **Primary buttons** always have `--cp-shadow-primary` at rest.

---

## 7. Iconography — LOCKED 🔒

### 7.1 Emoji Icons

CareerPilot uses native emoji as icons (no icon library dependency). This matches Apple's approach of system symbols.

| Context | Locked Emojis |
|---|---|
| **Score ≥ 75 (success)** | 🎉 |
| **Score < 75 (guidance)** | 🧭 |
| **Assessment/Interview** | 📋 |
| **Jobs/Career** | 💼 |
| **Learning/Plan** | 🎯 📚 |
| **Project** | 🚀 |
| **Progress** | 📈 |
| **Privacy** | 🔒 |
| **Aptitude** | 🧮 |
| **Verbal** | 🗣️ |
| **Reasoning** | 🧩 |
| **Technical** | 🛠️ |
| **Coding** | 💻 |
| **Matched skill** | ✅ |
| **Missing skill** | ❌ |
| **New skill** | 🆕 |
| **AI-generated** | 🤖 |

### 7.2 SVG Logo

The CareerPilot logo is an inline SVG: 32×32px blue rounded square with a white circle and blue diamond.

```
Dimensions: 32 × 32px
Outer: rounded rect, fill #007AFF, rx 8
Inner: circle cx=16 cy=16 r=8, fill white, opacity 0.9
Center: diamond path, fill #007AFF
```

---

## 8. Motion & Animation — LOCKED 🔒

Apple uses subtle, physics-based animations. CareerPilot uses CSS-only equivalents.

### 8.1 Timing

| Property | Value | Usage |
|---|---|---|
| **Default easing** | `ease` | All transitions |
| **Spring-like easing** | `cubic-bezier(0.25, 0.46, 0.45, 0.94)` | Entrance animations |
| **Button/hover transition** | `0.2s ease` | All interactive hover states |
| **Card hover transition** | `0.25s ease` | Shadow + transform transitions |
| **Entrance animation** | `0.5s ease forwards` | Page content fade-in |

### 8.2 Keyframes

| Name | From | To | Class |
|---|---|---|---|
| `fadeInUp` | `opacity:0; translateY(12px)` | `opacity:1; translateY(0)` | `.cp-animate-in` |
| `slideInLeft` | `opacity:0; translateX(-20px)` | `opacity:1; translateX(0)` | `.cp-animate-in-left` |
| `slideInRight` | `opacity:0; translateX(20px)` | `opacity:1; translateX(0)` | `.cp-animate-in-right` |
| `fadeIn` | `opacity:0` | `opacity:1` | (utility) |

### 8.3 Interactive Feedback

| Interaction | Response | Value |
|---|---|---|
| **Button hover** | Lift + shadow increase | `translateY(-1px)` + `--cp-shadow-primary-hover` |
| **Card hover** | Shadow increase | `--cp-shadow-sm` → `--cp-shadow-md` |
| **Badge hover** | Subtle lift | `translateY(-1px)` |
| **Input focus** | Blue ring | `box-shadow: 0 0 0 3px var(--cp-primary-ring)` |
| **Input hover** | Border color change | `border-color: var(--cp-border-hover)` |
| **Disabled elements** | Dim | `opacity: 0.5; cursor: not-allowed` |

### 8.4 Animation Rules

1. **Never exceed 0.5s** for any animation.
2. **Never animate layout-triggering properties** (width, height, top, left) — only `transform` and `opacity`.
3. **Entrance animations play once** (`forwards` fill mode).
4. **No animations on reduced-motion preference:** Add `@media (prefers-reduced-motion: reduce)` to disable.

---

## 9. Component Specifications — LOCKED 🔒

### 9.1 Buttons

#### Primary Button
```
Height:           48px
Padding:          0 28px
Border-Radius:    999px (full pill)
Background:       var(--cp-primary)         → #007AFF
Background Hover: var(--cp-primary-hover)   → #0063D1
Text Color:       #FFFFFF
Font-Size:        0.9375rem (15px)
Font-Weight:      600
Border:           none
Shadow:           var(--cp-shadow-primary)
Shadow Hover:     var(--cp-shadow-primary-hover)
Transform Hover:  translateY(-1px)
Transition:       all 0.2s ease
```

#### Secondary Button
```
Height:           48px
Padding:          0 28px
Border-Radius:    999px
Background:       var(--cp-bg-card)          → #FFFFFF
Background Hover: var(--cp-primary-light)    → #E5F1FF
Text Color:       var(--cp-text-secondary)   → #636366
Text Color Hover: var(--cp-primary)          → #007AFF
Border:           1.5px solid var(--cp-border)
Border Hover:     1.5px solid var(--cp-primary)
Shadow:           none
Transition:       all 0.2s ease
```

#### Disabled Button
```
Opacity:          0.5
Cursor:           not-allowed
Transform:        none (no hover lift)
```

---

### 9.2 Cards

#### Standard Card (`.cp-card`)
```
Background:       var(--cp-bg-card)          → #FFFFFF
Border:           1px solid var(--cp-border) → #D1D1D6
Border-Radius:    var(--cp-radius-lg)        → 20px
Padding:          24px 28px
Margin-Bottom:    20px
Shadow Rest:      var(--cp-shadow-sm)
Shadow Hover:     var(--cp-shadow-md)
Transition:       box-shadow 0.25s ease, transform 0.2s ease
```

#### Glassmorphic Card (`.cp-card-glass`)
```
Background:       rgba(255, 255, 255, 0.85)
Backdrop-Filter:  blur(12px)
Border:           1px solid rgba(255, 255, 255, 0.5)
All other props:  Same as standard card
```

---

### 9.3 Badges

```
Display:          inline-block
Padding:          5px 14px
Border-Radius:    999px (full pill)
Font-Size:        0.8125rem (13px)
Font-Weight:      600
Margin:           3px 6px 3px 0
Hover:            translateY(-1px)
Transition:       transform 0.15s ease
```

| Variant | Background | Text Color |
|---|---|---|
| `.cp-badge-good` | `--cp-success-light` (#E8F9ED) | `--cp-success-text` (#1B7A34) |
| `.cp-badge-bad` | `--cp-danger-light` (#FFF0EF) | `--cp-danger-text` (#B71C1C) |
| `.cp-badge-warn` | `--cp-warning-light` (#FFF7E5) | `--cp-warning-text` (#8B5E00) |
| `.cp-badge-info` | `--cp-info-light` (#DBEAFE) | `--cp-info-text` (#1E40AF) |
| `.cp-badge-purple` | `--cp-purple-light` (#EDE9FE) | `--cp-purple-text` (#5B21B6) |

---

### 9.4 Status Banners

```
Border-Radius:    var(--cp-radius-md)        → 14px
Padding:          16px 20px
Font-Weight:      600
Margin-Bottom:    16px
```

| Variant | Background | Border | Text Color |
|---|---|---|---|
| `.cp-status-good` | `--cp-success-light` | `1px solid --cp-success-border` | `--cp-success-text` |
| `.cp-status-bad` | `--cp-danger-light` | `1px solid --cp-danger-border` | `--cp-danger-text` |
| `.cp-status-warn` | `--cp-warning-light` | `1px solid --cp-warning-border` | `--cp-warning-text` |

---

### 9.5 Input Fields

```
Border-Radius:    var(--cp-radius-sm)        → 10px
Border:           1.5px solid var(--cp-border)
Padding:          12px 16px
Font-Size:        0.9375rem (15px)
Background:       var(--cp-bg-card)          → #FFFFFF
Transition:       all 0.2s ease

Focus:
  Border-Color:   var(--cp-primary)          → #007AFF
  Box-Shadow:     0 0 0 3px var(--cp-primary-ring)

Hover:
  Border-Color:   var(--cp-border-hover)     → #66B2FF
```

---

### 9.6 File Uploader

```
Border-Radius:    16px
Border:           2px dashed var(--cp-border)
Background:       var(--cp-bg)               → #F2F2F7
Padding:          32px

Hover:
  Border-Color:   var(--cp-primary)
  Background:     var(--cp-primary-light)
```

---

### 9.7 Score Gauge (Circular)

```
Default Size:     150 × 150px
Ring Width:       16px (calc from inner size = size - 32px)
Background Ring:  var(--cp-border)
Progress Ring:    conic-gradient(color 0deg, border 0deg)
Font-Size:        2rem (inside the circle)
Font-Weight:      800

Thresholds:
  score >= 80  →  var(--cp-success)  → #34C759 (green)
  score >= 60  →  var(--cp-warning)  → #FF9500 (orange)
  score < 60   →  var(--cp-danger)   → #FF3B30 (red)
```

---

### 9.8 Step Tracker

```
Bar Height:       4px
Bar Radius:       2px
Bar Gap:          8px
Inactive Color:   var(--cp-border)
Active Color:     var(--cp-primary)
Transition:       background 0.3s ease

Label:
  Color:          var(--cp-primary)
  Font-Size:      0.75rem (12px)
  Font-Weight:    700
  Text-Transform: uppercase
  Letter-Spacing: 0.06em
```

---

### 9.9 Navbar

```
Layout:           flex, space-between, align center
Padding:          12px 0
Margin-Bottom:    32px

Logo:
  Font-Size:      1.25rem (20px)
  Font-Weight:    800
  "Pilot" span:   color var(--cp-primary)

Nav Links:
  Gap:            28px
  Font-Size:      0.9375rem (15px)
  Font-Weight:    500
  Color:          var(--cp-text-secondary)
  Hover Color:    var(--cp-primary)

Nav Button:
  Padding:        8px 20px
  Border-Radius:  999px
  Font-Size:      0.875rem (14px)
  Font-Weight:    600

Nav Button Primary:
  Background:     var(--cp-primary)
  Color:          #FFFFFF
  Shadow:         var(--cp-shadow-primary)
```

---

### 9.10 Compare Grid

```
Layout:           CSS Grid, 2 columns, 16px gap
Margin:           16px 0

Original Panel:
  Background:     #FFF0EF (light red)
  Border:         1px solid var(--cp-danger-border)
  Border-Radius:  var(--cp-radius-md)    → 14px
  Padding:        20px

Optimized Panel:
  Background:     #E8F9ED (light green)
  Border:         1px solid #A2E4B8
  Border-Radius:  var(--cp-radius-md)    → 14px
  Padding:        20px

Label:
  Font-Size:      0.8125rem (13px)
  Font-Weight:    700
  Text-Transform: uppercase
  Letter-Spacing: 0.05em
  Original Color: #DC2626
  Optimized Color:#16A34A
```

---

### 9.11 Decision Cards

```
Background:       var(--cp-bg-card)
Border-Radius:    var(--cp-radius-lg)    → 20px
Padding:          28px
Border:           1px solid var(--cp-border)
Shadow:           var(--cp-shadow-sm)
Text-Align:       center
Height:           100% (fill parent column)

Hover:
  Transform:      translateY(-2px)
  Shadow:         var(--cp-shadow-md)

Icon Circle:
  Width/Height:   56px
  Border-Radius:  50%
  Display:        flex, center, center
  Font-Size:      1.5rem
  Margin:         0 auto 16px
```

---

### 9.12 Gradient Cards

#### Success Gradient (`.cp-success-gradient`)
```
Background:       linear-gradient(135deg, #ECFDF5, #E8F9ED)
Border:           1px solid #6EE7B7
Border-Radius:    var(--cp-radius-lg)    → 20px
Padding:          32px
Text-Align:       center
Margin-Bottom:    20px
```

#### Mentor Card (`.cp-mentor-card`)
```
Background:       linear-gradient(135deg, #EFF6FF, #DBEAFE)
Border:           1px solid var(--cp-border-hover)
Border-Radius:    var(--cp-radius-lg)    → 20px
Padding:          32px
Text-Align:       center
Margin-Bottom:    20px
```

---

## 10. Responsive Breakpoints — LOCKED 🔒

| Breakpoint | Width | Behavior |
|---|---|---|
| **Desktop** | `> 1200px` | Max-width container, 2–4 column grids |
| **Tablet** | `769px – 1200px` | Same layout, slightly tighter padding |
| **Mobile** | `≤ 768px` | Single column, navbar links hidden, compare grid stacks |

### Mobile Overrides

```css
@media (max-width: 768px) {
    .cp-nav-links              { display: none; }
    .cp-compare-grid           { grid-template-columns: 1fr; }
    h1                         { font-size: 1.75rem; }
    .block-container           { padding-left: 1rem !important;
                                 padding-right: 1rem !important; }
    [data-testid="column"]     { min-width: 100% !important; }
}
```

---

## 11. Accessibility — LOCKED 🔒

Following Apple's accessibility standards:

| Requirement | Implementation |
|---|---|
| **Color contrast** | All text-on-bg combinations meet WCAG AA (≥ 4.5:1 for body, ≥ 3:1 for large text) |
| **Focus indicators** | 3px blue ring (`--cp-primary-ring`) on all interactive elements |
| **Reduced motion** | Add `@media (prefers-reduced-motion: reduce) { .cp-animate-* { animation: none; } }` |
| **Semantic HTML** | Headings follow h1→h2→h3 hierarchy. Buttons use `<button>`, not `<div>`. |
| **Touch targets** | Minimum 44×44px (Apple HIG requirement). Buttons are 48px tall. Badges are ~30px tall but have hover margin. |

---

## 12. Complete Token Map (Copy-Paste Ready) — LOCKED 🔒

This is the exact CSS custom properties block that must be in `assets/style.css`:

```css
:root {
    /* ── Brand ── */
    --cp-primary:            #007AFF;
    --cp-primary-hover:      #0063D1;
    --cp-primary-light:      #E5F1FF;
    --cp-primary-ring:       rgba(0, 122, 255, 0.12);

    /* ── Semantic: Success ── */
    --cp-success:            #34C759;
    --cp-success-light:      #E8F9ED;
    --cp-success-border:     #A2E4B8;
    --cp-success-text:       #1B7A34;

    /* ── Semantic: Danger ── */
    --cp-danger:             #FF3B30;
    --cp-danger-light:       #FFF0EF;
    --cp-danger-border:      #FFCAC6;
    --cp-danger-text:        #B71C1C;

    /* ── Semantic: Warning ── */
    --cp-warning:            #FF9500;
    --cp-warning-light:      #FFF7E5;
    --cp-warning-border:     #FFD480;
    --cp-warning-text:       #8B5E00;

    /* ── Semantic: Info ── */
    --cp-info-light:         #DBEAFE;
    --cp-info-text:          #1E40AF;

    /* ── Semantic: Purple ── */
    --cp-purple-light:       #EDE9FE;
    --cp-purple-text:        #5B21B6;

    /* ── Neutrals (Apple System Grays) ── */
    --cp-text:               #1C1C1E;
    --cp-text-secondary:     #636366;
    --cp-text-muted:         #AEAEB2;
    --cp-text-quaternary:    #C7C7CC;
    --cp-border:             #D1D1D6;
    --cp-border-hover:       #66B2FF;
    --cp-bg:                 #F2F2F7;
    --cp-bg-card:            #FFFFFF;
    --cp-bg-secondary:       #F9F9FB;

    /* ── Radii ── */
    --cp-radius-xs:          6px;
    --cp-radius-sm:          10px;
    --cp-radius-md:          14px;
    --cp-radius-lg:          20px;
    --cp-radius-xl:          24px;
    --cp-radius-full:        999px;

    /* ── Shadows ── */
    --cp-shadow-none:        none;
    --cp-shadow-xs:          0 1px 2px rgba(0,0,0,0.04);
    --cp-shadow-sm:          0 1px 3px rgba(0,0,0,0.05),
                             0 4px 12px rgba(0,0,0,0.03);
    --cp-shadow-md:          0 4px 16px rgba(0,0,0,0.07),
                             0 8px 24px rgba(0,0,0,0.04);
    --cp-shadow-lg:          0 8px 32px rgba(0,0,0,0.10),
                             0 16px 48px rgba(0,0,0,0.06);
    --cp-shadow-primary:     0 2px 8px rgba(0,122,255,0.25);
    --cp-shadow-primary-hover: 0 4px 14px rgba(0,122,255,0.35);

    /* ── Spacing (4pt grid) ── */
    --space-1:  4px;
    --space-2:  8px;
    --space-3:  12px;
    --space-4:  16px;
    --space-5:  20px;
    --space-6:  24px;
    --space-8:  32px;
    --space-10: 40px;
    --space-12: 48px;
    --space-16: 64px;
}
```

---

## 13. Diff from Current Tokens → Locked Tokens

When implementing this spec, apply these changes to the current codebase:

| Token | Current Value | Locked Value | Reason |
|---|---|---|---|
| `--cp-primary` | `#2563EB` | `#007AFF` | Apple System Blue — universal, tested at scale |
| `--cp-primary-hover` | `#1D4ED8` | `#0063D1` | Darker Apple Blue |
| `--cp-primary-light` | `#EEF4FF` | `#E5F1FF` | Warmer, matches Apple tint |
| `--cp-success` | `#10B981` | `#34C759` | Apple System Green |
| `--cp-success-light` | `#D1FAE5` | `#E8F9ED` | Subtler tint |
| `--cp-danger` | `#EF4444` | `#FF3B30` | Apple System Red |
| `--cp-danger-light` | `#FEE2E2` | `#FFF0EF` | Warmer tint |
| `--cp-warning` | `#F59E0B` | `#FF9500` | Apple System Orange |
| `--cp-warning-light` | `#FEF3C7` | `#FFF7E5` | Cleaner tint |
| `--cp-text` | `#111827` | `#1C1C1E` | Apple Label Primary |
| `--cp-text-secondary` | `#6B7280` | `#636366` | Apple Label Secondary |
| `--cp-text-muted` | `#9CA3AF` | `#AEAEB2` | Apple Label Tertiary |
| `--cp-border` | `#E5E7EB` | `#D1D1D6` | Apple Separator (Opaque) |
| `--cp-bg` | `#F8FAFC` | `#F2F2F7` | Apple System Grouped Bg |
| `--cp-radius-sm` | `8px` | `10px` | Apple's minimum radius |
| `--cp-radius-md` | `12px` | `14px` | Consistent scale step |
| `--cp-radius-lg` | `20px` | `20px` | ✅ No change |
| `.streamlit/config.toml primaryColor` | `#2563EB` | `#007AFF` | Sync with locked primary |
| `.streamlit/config.toml backgroundColor` | `#FFFFFF` | `#FFFFFF` | ✅ No change |
| `.streamlit/config.toml secondaryBackgroundColor` | `#F8FAFC` | `#F2F2F7` | Sync with locked bg |
| `.streamlit/config.toml textColor` | `#111827` | `#1C1C1E` | Sync with locked text |

> **NEW tokens added:** `--cp-text-quaternary`, `--cp-bg-secondary`, `--cp-radius-xs`, `--cp-radius-xl`, `--cp-shadow-none`, `--cp-shadow-xs`, `--cp-shadow-lg`, `--cp-shadow-primary-hover`, `--space-*` scale.

---

> **🔒 This specification is LOCKED. Any proposed changes must be documented with rationale and approved before implementation.**
>
> **Last updated:** 2026-07-31
