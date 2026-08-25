# CareerPilot AI — Locked Design System
### Specification · v2.0 (Transitional)

> **STATUS: 🔒 LOCKED (CURRENTLY IN TRANSITION)**
> This document is the single source of truth for every visual decision in CareerPilot AI.
> 
> **Important Migration Context:** The application is currently in a transitional state. We are actively moving from a legacy global styling system (`assets/style.css` / `cp-*`) to a new semantic, namespaced foundation (`.cp-ui`). The `pages/landing.py` module is the reference implementation for the new design system. Other legacy pages still depend on `assets/style.css` and will be incrementally migrated.

---

## 1. Design Philosophy

CareerPilot follows Apple's Human Interface Guidelines (HIG) as an inspiration for clarity and depth, adapted for a clean, premium white/light web interface:

| Principle | Application |
|---|---|
| **Clarity** | Content is king. Text is legible at every size. Whitespace is generous. |
| **Deference** | UI helps, never competes. Cards, backgrounds, and chrome are muted (white/light grays). |
| **Depth** | Shadows and border separations create a clear hierarchy. |
| **Consistency** | Same action = same appearance. |
| **Isolation** | New custom UI is strictly namespaced inside `.cp-ui` to avoid global side-effects. |

---

## 2. Color Palette — LOCKED 🔒 (Light Theme)

The active implementation is strictly **Light Mode**. All previous dark-mode values have been deprecated and must not be used.

### 2.1 Brand Colors

The primary brand color is **CareerPilot's primary lime/green brand accent** (`#9ad013`). Apple HIG is our structural design inspiration, but our primary brand color is independent.

| Token | Hex | Usage |
|---|---|---|
| `--cp-color-primary` | `#0f172a` | Primary slate/dark accent for text/core elements |
| `--cp-color-primary-hover` | `#1e293b` | Primary hover state |
| `--cp-color-primary-light` | `#f1f5f9` | Very light slate tint for active backgrounds |
| `--cp-color-success` | `#10b981` | Core success green |
| `--cp-color-success-bg` | `#d1fae5` | Light green background |
| `--cp-color-warning` | `#f59e0b` | Core warning orange |
| `--cp-color-warning-bg` | `#fef3c7` | Light warning background |
| `--cp-color-info` | `#3b82f6` | Core info blue |
| `--cp-color-info-bg` | `#dbeafe` | Light info background |
| `--cp-color-danger` | `#ef4444` | Core danger red |
| `--cp-color-danger-bg` | `#fee2e2` | Light danger background |

*Note: The legacy lime/green color `#9ad013` remains in legacy Streamlit components, but new structural elements leverage the premium slate scale (`#0f172a`) and semantic tints for a restrained visual hierarchy.*

### 2.2 Neutral Palette (Light Surfaces)

| Token | Hex | Usage |
|---|---|---|
| `--cp-color-background` | `#ffffff` | Base page background |
| `--cp-color-surface` | `#ffffff` | Primary card surfaces |
| `--cp-color-surface-muted` | `#f8fafc` | Secondary cards, callout backgrounds |
| `--cp-color-surface-inset` | `#f1f5f9` | Deepest inset background (e.g. progress bar tracks) |
| `--cp-color-text` | `#0f172a` | Headlines, primary text |
| `--cp-color-text-secondary` | `#475569` | Subtitles, body copy |
| `--cp-color-text-muted` | `#64748b` | Captions, disabled states |
| `--cp-color-border` | `#e2e8f0` | Dividers, standard borders |
| `--cp-color-border-strong`| `#cbd5e1` | Strong borders (e.g. dashed drop zones) |

### 2.3 Streamlit Theme Sync

These values are configured in `.streamlit/config.toml` to synchronize the native Streamlit widgets with the light theme:

```toml
[theme]
base = "light"
primaryColor = "#0f172a"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#0f172a"
font = "sans serif"
```

---

## 3. Typography — LOCKED 🔒

### 3.1 Font Stack
The primary font used for the interface relies on native system fonts for maximum performance and a native feel.
**Font-Family:** `"Inter", "Segoe UI", "Roboto", "Helvetica Neue", sans-serif;`

### 3.2 Typography Rules (Namespaced)
All typography styles must be explicitly applied via classes nested within the `.cp-ui` namespace.

| Class | Font Size | Weight | Line-Height | Usage |
|---|---|---|---|---|
| `.cp-text-display` | `3rem` | 800 | `1.1` | Landing hero headline only |
| `.cp-text-h1` | `2.25rem` | 700 | `1.2` | Page titles |
| `.cp-text-h2` | `1.5rem` | 600 | `1.3` | Section headings |
| `.cp-text-body` | `1rem` | 400 | `1.5` | Default paragraph text |
| `.cp-text-muted` | `0.875rem`| 400 | `1.5` | Secondary text, descriptions |

---

## 4. Spacing System — LOCKED 🔒

**Base unit:** All spacing values follow a standardized scale based on `rem` sizing.

| Token | Value | Usage |
|---|---|---|
| `--cp-space-xs` | `0.25rem` | Icon-to-text gaps |
| `--cp-space-sm` | `0.5rem` | Badge padding, tight inline gaps |
| `--cp-space-md` | `1rem` | Input padding, standard component padding |
| `--cp-space-lg` | `1.5rem` | Section gaps, outer margins |
| `--cp-space-xl` | `2rem` | Card padding (inner), major layout gaps |
| `--cp-space-2xl`| `3rem` | Large section separators |
| `--cp-space-3xl`| `4rem` | Hero area padding |

---

## 5. Corner Radius — LOCKED 🔒

| Token | Value | Usage |
|---|---|---|
| `--cp-radius-sm` | `4px` | Small elements |
| `--cp-radius-md` | `8px` | Standard inputs, inner elements |
| `--cp-radius-lg` | `12px` | Modals, panels |
| `--cp-radius-xl` | `16px` | Cards, hero containers |
| `--cp-radius-full` | `9999px` | Badges, pills, progress bars |

---

## 6. Shadow & Elevation — LOCKED 🔒

| Token | Usage |
|---|---|
| `--cp-shadow-none` | Flat elements, removed shadows |
| `--cp-shadow-subtle` | Standard cards (`0 1px 2px 0 rgba...`) |
| `--cp-shadow-medium` | Hovered cards, active states |
| `--cp-shadow-large` | Modals, major featured cards (like the landing Hero card) |

---

## 7. Iconography — LOCKED 🔒

The current implementation utilizes **centralized SVG icons**. 
- **Location:** `ui/icons.py`
- **Architecture:** Functions returning SVG strings utilizing `currentColor` for strokes.
- **Rule:** Do not rely on external icon libraries. Emojis are permitted only for basic content accents, not as the structural icon system.

---

## 8. CSS NAMESPACE RULE

The new foundation uses namespaced presentation through `.cp-ui`.

- **Custom UI components must be scoped:** All custom HTML must live inside a container with the `class="cp-ui"`.
- **New CSS must not globally bleed into legacy pages:** Never use raw element selectors like `button {}`, `h1 {}`, or `.card {}` in `styles/*.css`.
- **Legacy CSS:** `assets/style.css` remains temporarily active globally to keep unmigrated pages functioning.
- **New pages:** Must follow the new architecture relying on `styles/tokens.css` and `styles/base.css`.

---

## 9. LEGACY MIGRATION STATUS & TAILWIND

**Tailwind CSS is NOT part of the active architecture.**
- The `inject_tailwind()` function is inactive/removed.
- Tailwind CDN must NOT be introduced again.
- Do not add a Tailwind build pipeline.

**Migration Status (Transitional):**
- **Legacy UI:** Driven by `assets/style.css` and `modules/ui_components.py` (using `unsafe_allow_html`). Active on unmigrated pages (e.g., `results.py`, `upload_resume.py`).
- **New UI Foundation:** Driven by `styles/tokens.css`, `styles/base.css`, `styles/streamlit.css`, and `ui/icons.py`. Native Streamlit + `st.html()` for presentation. 
- **Reference Page:** `pages/landing.py` is fully migrated.

Do not attempt to remove the legacy system until all pages are fully migrated.

---

## 10. TOKEN AUTHORITY

1. **CSS Design Tokens (`styles/tokens.css`)** are the definitive visual source of truth.
2. **Streamlit Native Widgets** automatically inherit from `.streamlit/config.toml` (which is synced to our tokens).
3. **DO NOT global-target internal Streamlit DOM elements** to restyle widgets during this transition, as doing so will break legacy pages.

> **END OF LOCKED DESIGN SYSTEM**
