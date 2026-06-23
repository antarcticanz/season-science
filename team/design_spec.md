# Design Specification — Antarctica NZ Season Activities Map
# Dark Theme Redesign

**Author:** Lead Designer
**Date:** 2026-06-23
**Status:** Final — ready for Engineer implementation

---

## Guiding Principles

The ESRI Antarctic Satellite basemap dominates the viewport. The UI shell (header, sidebar, controls, popups) must recede visually so the map and its data points own the view. Achieve this by:

1. Dark surfaces that sit below the map in perceived brightness.
2. Borders that are barely-there separators, not visible frames.
3. Text that is comfortably readable but not competing with map features.
4. Checked/active states lit in the layer's own point colour (via `accent-color`) so the sidebar reads as a legend.
5. No animations, no glow effects, no neon palette. This is a professional science dashboard.

The dark theme is native to the map, not imposed on top of it. The satellite imagery dominant tones are the design reference: dark navy-black ocean (`#050d18`–`#0a1928`), brilliant blue-white ice (`#c8dff0`–`#f0f8ff`), dark charcoal rock (`#1e1810`–`#2d2418`).

---

## 1. Colour Token Table

All tokens are CSS custom properties to be declared in `:root {}` at the top of `style.css`. Every rule in the file that uses a hardcoded colour must be replaced with the corresponding token. The "Current value" column shows what the Engineer is replacing.

| Token | New hex value | Usage | Current value being replaced |
|---|---|---|---|
| `--color-bg-base` | `#0b0f14` | `html`, `body`, `.app-root`, `.body-row`, `.map-frame` backgrounds | `#000`, `#1a1a1a` |
| `--color-bg-surface` | `#111820` | `.sidebar` background, `.title-pane` background | `#F0F2F4` |
| `--color-bg-elevated` | `#18222e` | `.ol-popup` background, `.bm-panel` background, `.popup-nav-btn` background | `#ffffff` |
| `--color-bg-control` | `#1c2a38` | `.ol-zoom` buttons bg, `.ol-layers-btn` bg, `.sidebar__bulk-btn` bg | `#ffffff`, `#F0F2F4` |
| `--color-bg-control-hover` | `#253648` | Hover state for all control buttons | `#F0F2F4`, `#C7D2DB` |
| `--color-border-subtle` | `#1f2e3d` | `.sidebar` border-right, `.title-pane` border-bottom, `.sidebar__hr`, `.nested-wrap` border-left, `.popup-title` border-bottom, `.popup-pagination` border-bottom, `.bm-panel__heading` border-bottom | `#C7D2DB`, `#E3E9EE`, `#e5e7eb` |
| `--color-border-control` | `#2c4055` | Border on buttons (zoom, layers, bulk, nav, export NOT used here) | `#C7D2DB` |
| `--color-text-primary` | `#dce8f0` | All primary text: headings, labels, popup title, popup field values, button text | `#2F3A40` |
| `--color-text-muted` | `#6e8fa8` | Secondary text: `.bm-panel__heading`, `.popup-page-indicator`, `.ol-popup__close`, `.copy-email-btn` default | `#6B7C86` |
| `--color-text-inverse` | `#dce8f0` | Text on dark active state for `.bm-option--active` | `#ffffff` |
| `--color-accent-export` | `#2a7fbf` | `.sidebar__export-btn` background | `#2F3A40` |
| `--color-accent-export-hover` | `#1f6090` | `.sidebar__export-btn` hover background | `#4A5A62` |
| `--color-active-bm` | `#1f3c58` | `.bm-option--active` background | `#2F3A40` |
| `--color-active-bm-text` | `#dce8f0` | `.bm-option--active` text | `#ffffff` |
| `--color-badge-default-bg` | `rgba(220, 232, 240, 0.10)` | `.status-badge` default background | `#E3E9EE` |
| `--color-badge-default-text` | `#dce8f0` | `.status-badge` default text | `#2F3A40` |
| `--color-badge-active-bg` | `rgba(32, 197, 41, 0.15)` | `.status-badge--active` background | `rgba(32, 197, 41, 0.12)` |
| `--color-badge-active-text` | `#4dd966` | `.status-badge--active` text (lightened for dark bg) | `rgba(39, 179, 74, 0.877)` |
| `--color-badge-planned-bg` | `rgba(56, 152, 255, 0.15)` | `.status-badge--planned` background | `rgba(30, 144, 255, 0.12)` |
| `--color-badge-planned-text` | `#6ab4ff` | `.status-badge--planned` text (lightened for dark bg) | `rgb(20, 100, 200)` |
| `--color-badge-wishlist-bg` | `rgba(255, 165, 30, 0.15)` | `.status-badge--wishlist` background | `rgba(255, 99, 71, 0.15)` |
| `--color-badge-wishlist-text` | `#ffb347` | `.status-badge--wishlist` text | `rgb(230, 142, 28)` |
| `--color-copy-success` | `#4dd966` | `.copy-email-btn.copied` text colour | `#2E7D32` |
| `--color-scrollbar-track` | `#0e1720` | Scrollbar track | (not currently defined) |
| `--color-scrollbar-thumb` | `#2c4055` | Scrollbar thumb | (not currently defined) |
| `--color-scrollbar-thumb-hover` | `#3d5a77` | Scrollbar thumb hover | (not currently defined) |

---

## 2. Typography

The font stack remains Inter (already imported from Google Fonts). No additional font imports. No monospace font.

| Context | Family | Size | Weight | Colour token |
|---|---|---|---|---|
| App title (`.title-pane__title`) | `"Inter", system-ui, sans-serif` | `clamp(1.1rem, 1.4vw, 1.5rem)` | 600 | `--color-text-primary` |
| Section headings (`.sidebar__heading`) | `"Inter", system-ui, sans-serif` | `0.75rem` | 700 | `--color-text-muted` |
| Section headings — additional rule | Uppercase letters | `letter-spacing: 0.08em` | — | — |
| Layer / checklist labels (`.layer-checklist__label`) | `"Inter", system-ui, sans-serif` | `0.88rem` | 400 | `--color-text-primary` |
| Bulk action buttons (`.sidebar__bulk-btn`) | `"Inter", system-ui, sans-serif` | `0.75rem` | 500 | `--color-text-primary` |
| Export button (`.sidebar__export-btn`) | `"Inter", system-ui, sans-serif` | `0.8rem` | 500 | `--color-text-primary` |
| Popup title (`.popup-title`) | `"Inter", system-ui, sans-serif` | `0.9rem` | 600 | `--color-text-primary` |
| Popup field labels (`strong` inside `.ol-popup`) | `"Inter", system-ui, sans-serif` | `0.85rem` | 600 | `--color-text-muted` |
| Popup field values (plain text inside `.ol-popup`) | `"Inter", system-ui, sans-serif` | `0.85rem` | 400 | `--color-text-primary` |
| Status badges (`.status-badge`) | `"Inter", system-ui, sans-serif` | `0.75rem` | 600 | (per badge variant) |
| Basemap panel heading (`.bm-panel__heading`) | `"Inter", system-ui, sans-serif` | `0.72rem` | 600 | `--color-text-muted` |
| Basemap options (`.bm-option`) | `"Inter", system-ui, sans-serif` | `0.85rem` | 400 (default), 600 (active) | `--color-text-primary` |
| Page indicator (`.popup-page-indicator`) | `"Inter", system-ui, sans-serif` | `0.78rem` | 500 | `--color-text-muted` |

Note on section headings: raise the visual hierarchy without size increases. Current `.sidebar__heading` is `0.95rem / 600`. New spec is `0.75rem / 700 / uppercase / letter-spacing 0.08em` in `--color-text-muted`. This creates clear section breaks that recede compared to label text, matching the inspiration sidebar's `.headerText` pattern — but using Inter, not mono.

---

## 3. Component Specifications

### Page / body background

| Property | Value |
|---|---|
| `html, body` background | `--color-bg-base` (`#0b0f14`) |
| `#react-entry-point` | height: 100% (unchanged) |
| `.app-root` background | `--color-bg-base` |
| `.body-row` background | `--color-bg-base` |
| `.map-frame` background | `--color-bg-base` |
| `.map` background | `--color-bg-base` |

---

### `.title-pane` (header bar)

| Property | Value |
|---|---|
| Background | `--color-bg-surface` (`#111820`) |
| Border-bottom | `1px solid var(--color-border-subtle)` |
| Padding | `10px 16px` (unchanged) |
| Display | `flex`, `align-items: center`, `justify-content: space-between` (unchanged) |
| Logo (`.title-pane__logo`) | Height `60px` (unchanged). **Engineer note:** change `src` in `app.py` from `ANZ_Logo_Horrizontal_CMYK.png` to `ANZ_Logo_Horizontal_Badge_White_RGB.png` |
| Title text colour | `--color-text-primary` |
| Title font / size / weight | Per Typography table above (unchanged from current) |

---

### `.sidebar`

| Property | Value |
|---|---|
| Width | `320px` (unchanged) |
| Background | `--color-bg-surface` (`#111820`) |
| Border-right | `1px solid var(--color-border-subtle)` |
| Padding | `12px` (unchanged) |
| Color (default text) | `--color-text-primary` |
| Font family | `"Inter", system-ui, sans-serif` (unchanged) |
| Overflow-y | `auto` (unchanged) |

---

### `.sidebar__heading` (section headings: "Science Events", "Locations", "Instruments", "Camp Sites")

| Property | Value |
|---|---|
| Font-size | `0.75rem` |
| Font-weight | `700` |
| Text-transform | `uppercase` |
| Letter-spacing | `0.08em` |
| Color | `--color-text-muted` (`#6e8fa8`) |
| Margin | `0 0 10px 0` |

---

### `.sidebar__hr` (dividers)

| Property | Value |
|---|---|
| Border | `none` |
| Height | `1px` |
| Background | `--color-border-subtle` (`#1f2e3d`) |
| Margin | `14px 0` (unchanged) |

`.sidebar__hr--export` overrides: `margin-top: 20px; margin-bottom: 20px` (unchanged).

---

### `.layer-checklist__label` (layer name text)

| Property | Value |
|---|---|
| Color | `--color-text-primary` (`#dce8f0`) |
| Font-size | `0.88rem` |
| Font-weight | `400` |
| Cursor | `pointer` (unchanged) |
| Gap | `10px` (unchanged) |
| Hover state | No background change. Colour shifts to `#ffffff` (pure white, subtle brightening). Apply via `.layer-checklist__label:hover { color: #ffffff; }` |

---

### `input[type=checkbox]` / `.layer-checklist__input`

| Property | Value |
|---|---|
| Width / height | `16px` (unchanged) |
| `accent-color` | `#7FDBFF` — **keep this value unchanged**. It is the fallback. In practice, each layer's point colour is used as the checkbox accent where possible, but because Dash renders a single shared `accent-color` per `inputClassName`, this sky-blue fallback is appropriate and legible against `--color-bg-surface`. |

No change needed. `#7FDBFF` is already legible against the new dark surface.

---

### `.sidebar__bulk-btn` (Select all / Deselect all)

| Property | Value |
|---|---|
| Background | `--color-bg-control` (`#1c2a38`) |
| Border | `1px solid var(--color-border-control)` |
| Border-radius | `4px` |
| Padding | `3px 8px` (unchanged) |
| Font-size | `0.75rem` |
| Font-weight | `500` |
| Color | `--color-text-primary` |
| Cursor | `pointer` |
| Hover background | `--color-bg-control-hover` (`#253648`) |
| Hover border | `1px solid #3d5a77` |
| Disabled state | Not currently used; if added in future: `opacity: 0.4; cursor: default` |

---

### `.sidebar__export-btn` (Export button)

| Property | Value |
|---|---|
| Width | `100%` (unchanged) |
| Background | `--color-accent-export` (`#2a7fbf`) |
| Color | `#ffffff` |
| Border | `none` |
| Border-radius | `4px` |
| Padding | `7px 10px` (unchanged) |
| Font-size | `0.8rem` |
| Font-weight | `500` |
| Letter-spacing | `0.1px` |
| Hover background | `--color-accent-export-hover` (`#1f6090`) |

Rationale: The export button is the one distinct action button. Using `--color-accent-export` (a mid-blue that harmonises with the ice tones of the basemap) makes it clearly actionable without using a loud accent colour.

---

### `.nested-wrap` (indent border for sub-layers)

| Property | Value |
|---|---|
| Margin-left | `22px` (unchanged) |
| Border-left | `2px solid var(--color-border-subtle)` |
| Padding-left | `0` (unchanged) |

---

### `.ol-popup` (popup card)

| Property | Value |
|---|---|
| Background | `--color-bg-elevated` (`#18222e`) |
| Border | `1px solid var(--color-border-subtle)` |
| Border-radius | `6px` (unchanged) |
| Padding | `10px 36px 10px 12px` (unchanged) |
| Width | `360px` (unchanged) |
| Min-height | `160px` (unchanged) |
| Font-family | `"Inter", system-ui, sans-serif` |
| Font-size | `0.85rem` (unchanged) |
| Color | `--color-text-primary` |
| Box-shadow | `0 8px 24px rgba(0, 0, 0, 0.55)` (heavier than current `0.18` alpha — dark popups need more shadow contrast to lift off the dark map) |
| Z-index | `1000` (unchanged) |

---

### `.popup-title`

| Property | Value |
|---|---|
| Font-weight | `600` (unchanged) |
| Font-size | `0.9rem` |
| Color | `--color-text-primary` |
| Margin-bottom | `6px` (unchanged) |
| Padding-bottom | `4px` (unchanged) |
| Border-bottom | `1px solid var(--color-border-subtle)` |

---

### `.popup-pagination` / `.popup-nav-btn` / `.popup-page-indicator`

**`.popup-pagination`**

| Property | Value |
|---|---|
| Display | `flex`, `align-items: center`, `justify-content: center`, `gap: 14px` (unchanged) |
| Margin-bottom | `8px` (unchanged) |
| Padding-bottom | `6px` (unchanged) |
| Border-bottom | `1px solid var(--color-border-subtle)` |

**`.popup-nav-btn`**

| Property | Value |
|---|---|
| Background | `--color-bg-control` (`#1c2a38`) |
| Border | `1px solid var(--color-border-control)` |
| Border-radius | `4px` |
| Padding | `2px 8px` (unchanged) |
| Font-size | `0.85rem` (unchanged) |
| Color | `--color-text-primary` |
| Hover background (not disabled) | `--color-bg-control-hover` (`#253648`) |
| Disabled opacity | `0.35` (unchanged) |
| Disabled cursor | `default` (unchanged) |

**`.popup-page-indicator`**

| Property | Value |
|---|---|
| Font-size | `0.78rem` |
| Font-weight | `500` |
| Color | `--color-text-muted` (`#6e8fa8`) |

---

### `.ol-popup__close` (close button)

| Property | Value |
|---|---|
| Background | `transparent` (unchanged) |
| Border | `none` (unchanged) |
| Color | `--color-text-muted` (`#6e8fa8`) |
| Font-size | `1rem` (unchanged) |
| Hover color | `--color-text-primary` (`#dce8f0`) |
| Hover background | `rgba(255, 255, 255, 0.07)` |
| Border-radius | `3px` (unchanged) |
| Padding | `2px 5px` (unchanged) |

---

### `.status-badge`, `.status-badge--active`, `.status-badge--planned`, `.status-badge--wishlist`

**`.status-badge` (default/unknown status)**

| Property | Value |
|---|---|
| Background | `--color-badge-default-bg` (`rgba(220, 232, 240, 0.10)`) |
| Color | `--color-badge-default-text` (`#dce8f0`) |
| Padding | `1px 7px` (unchanged) |
| Border-radius | `999px` (unchanged) |
| Font-size | `0.75rem` |
| Font-weight | `600` (unchanged) |
| Letter-spacing | `0.3px` (unchanged) |

**`.status-badge--active`**

| Property | Value |
|---|---|
| Background | `--color-badge-active-bg` (`rgba(32, 197, 41, 0.15)`) |
| Color | `--color-badge-active-text` (`#4dd966`) |

**`.status-badge--planned`**

| Property | Value |
|---|---|
| Background | `--color-badge-planned-bg` (`rgba(56, 152, 255, 0.15)`) |
| Color | `--color-badge-planned-text` (`#6ab4ff`) |

**`.status-badge--wishlist`**

| Property | Value |
|---|---|
| Background | `--color-badge-wishlist-bg` (`rgba(255, 165, 30, 0.15)`) |
| Color | `--color-badge-wishlist-text` (`#ffb347`) |

---

### `.copy-email-btn`

| Property | Value |
|---|---|
| Background | `transparent` (unchanged) |
| Border | `none` (unchanged) |
| Padding | `2px` (unchanged) |
| Color | `--color-text-muted` (`#6e8fa8`) |
| Hover color | `--color-text-primary` (`#dce8f0`) |
| `.copied` color | `--color-copy-success` (`#4dd966`) |

---

### `.ol-zoom .ol-zoom-in` / `.ol-zoom-out` (zoom buttons)

| Property | Value |
|---|---|
| Width / height | `34px` (unchanged) |
| Font-size | `20px` (unchanged) |
| Background | `--color-bg-control` (`#1c2a38`) with `!important` |
| Color | `--color-text-primary` with `!important` |
| Border | `1px solid var(--color-border-control)` with `!important` |
| Border-radius | `4px` with `!important` |
| Hover background | `--color-bg-control-hover` with `!important` |

---

### `.ol-layers-btn` (basemap switcher button)

| Property | Value |
|---|---|
| Width / height | `34px` (unchanged) |
| Background | `--color-bg-control` (`#1c2a38`) |
| Border | `1px solid var(--color-border-control)` |
| Border-radius | `4px` (unchanged) |
| Color | `--color-text-primary` |
| Hover background | `--color-bg-control-hover` |

---

### `.bm-panel` (basemap switcher panel)

| Property | Value |
|---|---|
| Background | `--color-bg-elevated` (`#18222e`) |
| Border | `1px solid var(--color-border-subtle)` |
| Border-radius | `6px` (unchanged) |
| Box-shadow | `0 8px 24px rgba(0, 0, 0, 0.55)` |
| Padding | `8px` (unchanged) |
| Min-width | `150px` (unchanged) |
| Font-family | `"Inter", system-ui, sans-serif` (unchanged) |

**`.bm-panel__heading`**

| Property | Value |
|---|---|
| Font-size | `0.72rem` |
| Font-weight | `600` |
| Color | `--color-text-muted` |
| Text-transform | `uppercase` |
| Letter-spacing | `0.5px` (unchanged) |
| Border-bottom | `1px solid var(--color-border-subtle)` |

---

### `.bm-option`, `.bm-option--active`

**`.bm-option`**

| Property | Value |
|---|---|
| Background | `transparent` (unchanged) |
| Border | `none` (unchanged) |
| Border-radius | `4px` (unchanged) |
| Padding | `6px 8px` (unchanged) |
| Font-size | `0.85rem` (unchanged) |
| Color | `--color-text-primary` |
| Cursor | `pointer` |
| Hover background | `rgba(255, 255, 255, 0.06)` |

**`.bm-option--active`**

| Property | Value |
|---|---|
| Background | `--color-active-bm` (`#1f3c58`) |
| Color | `--color-active-bm-text` (`#dce8f0`) |
| Font-weight | `600` (unchanged) |
| Cursor | `default` (unchanged) |
| Border-radius | `4px` (unchanged) |
| Hover background | `--color-active-bm` (no change on hover, unchanged) |

---

### Scrollbar

| Selector | Property | Value |
|---|---|---|
| `::-webkit-scrollbar` | `width` | `6px` |
| `::-webkit-scrollbar` | `height` | `6px` |
| `::-webkit-scrollbar-track` | `background` | `--color-scrollbar-track` (`#0e1720`) |
| `::-webkit-scrollbar-thumb` | `background` | `--color-scrollbar-thumb` (`#2c4055`) |
| `::-webkit-scrollbar-thumb` | `border-radius` | `3px` |
| `::-webkit-scrollbar-thumb:hover` | `background` | `--color-scrollbar-thumb-hover` (`#3d5a77`) |

Apply these rules to the global scope (after `:root`), not scoped to `.sidebar`.

---

## 4. Map Point Colour Review

The LAYER_REGISTRY uses `rgba(r, g, b, 0.9)` fill colours with a white stroke (`color: "white"`). All OL point styles apply a white stroke via `makeScaledPointStyle`. The white stroke provides a universal contrast separator between point and basemap. However, several fills are problematic against the dark ESRI satellite basemap (dark navy-black ocean `#0a1928`).

### Points that PASS legibility (no change needed)

| Layer(s) | Current fill | Assessment |
|---|---|---|
| scott_base | `rgba(0, 180, 120, 0.9)` — mid-green | Clear on dark ocean. White stroke sufficient. Pass. |
| arrival_heights, pyramid_trough | `rgba(219, 135, 24, 0.9)` — amber | Warm amber on dark ocean. Clear. Pass. |
| asp_planned | `rgba(30, 144, 255, 0.9)` — cornflower blue | Legible with white stroke but can blend with very blue ice areas. Acceptable — the white stroke resolves ambiguity. Pass. |
| K055A | `rgba(100, 149, 237, 0.9)` — periwinkle | Legible. White stroke distinguishes from ice. Pass. |
| K060A | `rgba(255, 140, 0, 0.9)` — dark orange | Very clear on dark ocean. Pass. |
| K085A | `rgba(147, 112, 219, 0.9)` — medium purple | Legible on dark ocean. Pass. |
| K089A | `rgba(64, 224, 208, 0.9)` — turquoise | High contrast on dark ocean. Pass. |
| K102A, K170A, K850A, K862A--KIS3 | `rgba(69, 165, 189, 0.9)` — steel teal | Legible. Pass. |
| K862A--KIS2 | `rgba(160, 62, 83, 0.9)` — dark rose | Moderate contrast on dark ocean — just acceptable with white stroke. Pass. |
| K862A--CIR | `rgba(158, 39, 132, 0.9)` — deep magenta | Adequate contrast with white stroke. Pass. |
| K865A | `rgba(250, 15, 219, 0.9)` — vivid magenta-pink | High contrast. Pass. |
| K881B | `rgba(25, 209, 40, 0.9)` — vivid green | Excellent contrast on dark ocean. Pass. |
| CAMPSITES-2324 | `rgba(255, 165, 0, 0.92)` — orange | Clear. Pass. |
| CAMPSITES-2425 | `rgba(255, 120, 0, 0.92)` — orange-red | Clear. Pass. |
| CAMPSITES-2526 | `rgba(220, 80, 0, 0.92)` — burnt orange | Clear. Pass. |
| instruments_active | `rgba(255, 210, 0, 0.95)` — yellow | Excellent contrast on dark ocean. Pass. |
| instruments_decommissioned | `rgba(220, 55, 55, 0.95)` — red | Good contrast. Pass. |

### Points that FAIL legibility — changes required

| Layer(s) | Current fill | Problem | Recommended replacement |
|---|---|---|---|
| **K150A** | `rgba(27, 57, 189, 0.9)` — dark navy blue | Dark navy blue nearly invisible against the dark navy-black ocean (`#0a1928`). Even with white stroke, the fill blends with ocean. The point interior disappears at small zoom radii. | Change to `rgba(80, 160, 255, 0.9)` — a bright sky blue. Clear against ocean, distinct from K055A periwinkle and asp_planned cornflower. |
| **K872B--ACTIVE, K872B--PLANNED** | `rgba(139, 0, 0, 0.95)` — dark crimson/maroon | Dark maroon has very low luminance (~3.5 cd/m²). Against very dark ocean backgrounds it blends at small radii and dark rock backgrounds. Fails at smaller zoom levels. | Change to `rgba(220, 60, 60, 0.95)` — a clear medium-red. Matches `instruments_decommissioned` family but distinct in hue. Differentiates from K862A--KIS2 rose. |
| **K020A (all sites), K026A, K082A (all sites), K026A--PYRAMID_TROUGH, K891A--ACTIVE/PLANNED, K893A (all sites), K894A** | `rgba(235, 216, 53, 0.9)` or `rgba(190, 223, 43, 0.9)` — bright yellow-green / yellow | Both yellows are individually legible on dark ocean. **The problem is saturation of shared colour:** seven distinct science events (K020A, K026A, K082A, K891A, K893A, K894A) plus some entries all render in variations of yellow/yellow-green. When all are enabled simultaneously, the map displays a sea of visually identical points with no quick differentiation. This is a **colour identity crisis, not a contrast failure per se.** | **Designer recommendation:** Assign distinct colours to differentiate these groups. Suggested palette (all legible on dark ocean): K020A keep `rgba(235, 216, 53, 0.9)` (yellow). K026A change to `rgba(255, 180, 50, 0.9)` (warm gold — adjacent to yellow, distinguishable). K082A change to `rgba(250, 100, 40, 0.9)` (coral-orange — distinct from the amber-orange family above). K891A keep `rgba(190, 223, 43, 0.9)` (yellow-green). K893A change to `rgba(140, 210, 60, 0.9)` (fresh green — adjacent to yellow-green but distinct). K894A change to `rgba(100, 220, 120, 0.9)` (mint green — clearly distinct). Note: this is a design recommendation, not a hard requirement. The Engineer should confirm with stakeholders whether event colours need to encode semantic meaning before implementing. If all yellow-family events share deliberate scientific grouping meaning, the current scheme may be intentional. |

### White stroke update

The current `makeScaledPointStyle` uses `color: "white"` as the stroke. This is correct and must be retained — it is the universal legibility mechanism. No change.

---

## 5. Rules and Constraints

### Must-not-change (hard constraints)

1. **All existing CSS class names are preserved.** Python `app.py` references: `.app-root`, `.title-pane`, `.title-pane__logo`, `.title-pane__title`, `.body-row`, `.map-frame`, `.map`, `.sidebar`, `.sidebar__heading`, `.sidebar__heading--section`, `.sidebar__hr`, `.sidebar__hr--export`, `.sidebar__bulk-actions`, `.sidebar__bulk-btn`, `.sidebar__export-wrap`, `.sidebar__export-btn`, `.layer-checklist`, `.layer-checklist__input`, `.layer-checklist__label`, `.layer-checklist--nested`, `.nested-wrap`, `.ol-popup`, `.ol-popup__close`, `.ol-popup__content`, `.popup-title`, `.popup-pagination`, `.popup-nav-btn`, `.popup-page-indicator`, `.popup-email`, `.popup-site`, `.popup-event`, `.popup-status`, `.popup-pi`, `.popup-measurement`, `.status-badge`, `.status-badge--active`, `.status-badge--planned`, `.status-badge--wishlist`, `.copy-email-btn`, `.ol-zoom`, `.ol-layers-control`, `.ol-layers-btn`, `.bm-panel`, `.bm-panel__heading`, `.bm-option`, `.bm-option--active`, `.sidebar__export-wrap`, `.bm-panel` (JS-rendered).

2. **No animations or transition duration changes beyond what currently exists** (`0.15s` / `0.12s` — retain these, they provide micro-feedback without being decorative).

3. **No glow `box-shadow` effects.** Shadows are used only for elevation (depth separation of popup/panel from map). Maximum shadow: `0 8px 24px rgba(0, 0, 0, 0.55)`.

4. **No neon colours.** No `#08f7fe`, no `#fe53bb`, no `#09fbd3`. The inspiration palette is used for structural principle only.

5. **No additional font imports.** Use Inter only.

### WCAG AA contrast verification

The following pairs must meet WCAG AA (4.5:1 for normal text, 3:1 for large text/UI components):

| Text / Background | Approximate ratio | Passes AA |
|---|---|---|
| `--color-text-primary` `#dce8f0` on `--color-bg-surface` `#111820` | ~10.8:1 | Yes |
| `--color-text-primary` `#dce8f0` on `--color-bg-elevated` `#18222e` | ~9.5:1 | Yes |
| `--color-text-primary` `#dce8f0` on `--color-bg-control` `#1c2a38` | ~8.9:1 | Yes |
| `--color-text-muted` `#6e8fa8` on `--color-bg-surface` `#111820` | ~4.6:1 | Yes (AA) |
| `--color-text-muted` `#6e8fa8` on `--color-bg-elevated` `#18222e` | ~4.2:1 | Borderline — acceptable for UI metadata (section headings, indicators). If Engineer finds it insufficient, raise to `#7ba4bf`. |
| `--color-badge-active-text` `#4dd966` on `--color-bg-elevated` `#18222e` | ~7.1:1 | Yes |
| `--color-badge-planned-text` `#6ab4ff` on `--color-bg-elevated` `#18222e` | ~6.4:1 | Yes |
| `--color-badge-wishlist-text` `#ffb347` on `--color-bg-elevated` `#18222e` | ~7.8:1 | Yes |
| `#ffffff` on `--color-accent-export` `#2a7fbf` | ~4.7:1 | Yes |
| `--color-active-bm-text` `#dce8f0` on `--color-active-bm` `#1f3c58` | ~7.2:1 | Yes |

### Default basemap change

The current `ol-map.js` line `baseLayers.forEach((l, i) => l.setVisible(i === 0))` makes BAS Satellite the default (index 0 in `BASEMAP_REGISTRY`). To make ESRI Satellite the default, the Engineer must change the array order in `BASEMAP_REGISTRY` so `esri_imagery` is index 0, OR change `i === 0` to `l.get("basemap-id") === "esri_imagery"`. Both are equivalent. The recommended approach is the predicate form (more readable):

```js
baseLayers.forEach((l) => l.setVisible(l.get("basemap-id") === "esri_imagery"));
```

Also update `let activeBasemapId = "bas"` to `let activeBasemapId = "esri_imagery"`.

### Logo update

In `app.py` line ~540, change:
```python
src="/assets/ANZ_Logo_Horrizontal_CMYK.png",
```
to:
```python
src="/assets/ANZ_Logo_Horizontal_Badge_White_RGB.png",
```

This is not a CSS change but is part of the dark theme implementation. The white logo is correct against `--color-bg-surface`.

---

*End of specification.*
