# UX Review — Antarctica NZ Season Activities Map

**Author:** UX Specialist
**Date:** 2026-06-23
**App:** Antarctica NZ Supported Activities & Instruments — 2026-27
**Stack:** Python Dash + vanilla JS (OpenLayers)

---

## 1. Sidebar Section Order

**Current order:** Science Events → Locations → Instruments → Camp Sites

**Assessment:** The order is wrong for a scientist's mental model. Science Events is the largest, most complex section (many items with nested children) and appears first — before orientation anchors like Locations. A user who doesn't know what "K055A" or "K862A" means has no spatial context for those toggles. Instruments and Camp Sites are operationally different in character from science events; burying them at the bottom is fine, but their relative order matters.

**Recommendation:** Reorder to:

1. **Locations** — 3 items, quick orientation anchors (Scott Base, Arrival Heights, Pyramid Trough). These give users a spatial frame before they toggle anything else.
2. **Science Events** — the primary content. Now the user has orientation context.
3. **Camp Sites** — historical reference data; toggled occasionally. Correctly placed last.
4. **Instruments** — Active / Planned Removal. Currently last; move above Camp Sites as it is operationally more current.

Final order: **Locations → Science Events → Instruments → Camp Sites**

The Select All / Deselect All bulk actions move with Science Events and stay directly beneath the Science Events heading.

---

## 2. Section Heading Style

**Current:** `.sidebar__heading` is `font-size: 0.95rem`, `font-weight: 600`, `color: #2F3A40` — essentially the same weight and color as the item labels. On the existing light sidebar the sections barely register as hierarchy. On a dark sidebar this will disappear entirely.

**Recommendation:** Adopt the pattern from the inspiration sidebar's `.headerText`: small-caps or uppercase with generous letter-spacing and a muted color that reads as a label rather than content. Specific changes:

- `text-transform: uppercase`
- `letter-spacing: 0.12em` (tighter than the inspiration's 0.15em to suit longer strings like "Science Events")
- `font-size: 0.7rem` — smaller than the item labels; labels are 0.95rem so headings should read smaller/quieter
- `font-weight: 600`
- Color: a mid-grey that sits clearly above the dark background but doesn't compete with item labels. On a dark sidebar (`#1A1E22` or similar), use `#7A8A92` (equivalent to the current `#6B7C86` accent). Do not use the same color as item text.
- Add `padding-top: 4px` to increase visual separation from the preceding divider

The combined effect — uppercase, tracked, small, muted — makes it unmistakable that this is a category label, not a clickable item.

---

## 3. Checkbox vs Toggle

**Current:** Standard HTML checkboxes (`<input type="checkbox">`), styled with `accent-color: #7FDBFF`. On a dark background, native checkboxes render inconsistently across browsers and OS themes: the browser chrome shows through and can appear as a white or system-grey box that clashes with a dark panel.

**Inspiration pattern:** Circular glow-toggle dot — a 22px circle with a `1.5px` border, containing an 8px filled dot. When active, the border and dot adopt the layer's own color with a `box-shadow` glow. When inactive, border is muted and dot is transparent.

**Recommendation:** Use the circular glow-toggle pattern for this app, with one important adjustment for the professional context: suppress the glow on inactive state and keep it subtle on active. The inspiration's full neon glow (`box-shadow: 0 0 6px var(--layer-color)`) is appropriate for a monitoring dashboard; for a scientific/operational tool used in meetings and planning contexts, a softer treatment reads more credibly.

Specific spec:
- Toggle circle: `width: 18px; height: 18px; border-radius: 50%; border: 1.5px solid rgba(255,255,255,0.2); background: transparent; flex-shrink: 0`
- Inner dot: `width: 8px; height: 8px; border-radius: 50%; background: transparent`
- Active state: border becomes the layer's own point color (already defined per-layer in the JS registry); inner dot fills with the same color; `box-shadow: 0 0 4px <layer-color>` (not 6px)
- Inactive state: no glow, no fill — just the faint ring

This preserves the layer-color-coding that already exists in the map and creates a direct visual link between the sidebar toggle and the dots on the map. Standard HTML checkboxes cannot do this.

**Implementation note:** Because Dash's `dcc.Checklist` renders native `<input type="checkbox">` elements, custom toggles require replacing the Dash checklist with `dcc.Store` + plain `html.Div` rows that fire clientside callbacks on click, or using a CSS-only approach with `label::before`/`label::after` to mask the native checkbox. The CSS-only approach is simpler within the existing framework: hide the native input (`opacity: 0; position: absolute`) and use `label::before` (the ring) and `label::after` (the dot), toggled via `:checked` state. No JS changes required.

---

## 4. Active State Indication

**Current:** When a parent checkbox is checked, the only visual change is the checkbox tick itself. The label color does not change. On the existing light sidebar this is readable but low-contrast. On a dark sidebar with a hidden native checkbox or custom toggle, the checked/unchecked distinction must be carried entirely by the toggle's own visual state.

**Issues identified:**
- The parent label (`layer-checklist__label`) has no color or weight change between checked and unchecked. A user glancing at the sidebar cannot quickly tell which layers are on without inspecting each toggle closely.
- Indeterminate state (some children checked, not all) is not visually distinguished from fully checked.

**Recommendations:**
- Checked parent label: `color: #FFFFFF` (full white)
- Unchecked parent label: `color: rgba(255,255,255,0.40)` — clearly dimmed
- Do not change font-weight between states; weight changes cause layout shift
- Indeterminate state (partial children checked): render the toggle ring in the layer color but leave the inner dot at 50% opacity rather than full fill. This is achievable in CSS with a `:indeterminate` pseudo-class on the native checkbox or by applying a class via the existing toggle callback.
- The nested `border-left: 2px solid #e5e7eb` on `.nested-wrap` must darken on dark theme — use `rgba(255,255,255,0.12)` instead of the current light grey which will be invisible.

---

## 5. Nested Children — Collapsed by Default

**Current:** When a parent has multiple site sub-layers (e.g. K082A - Seafloor Seeps has Blood Falls, Cape Evans, Granite Harbour, Lake Fryxell, McMurdo Sound, New Harbour), the children are hidden by default and expand on first click of the parent label. The expand/collapse is done via `style={"display": "none"}` toggled by a callback.

**Assessment:** The collapsed-by-default pattern is correct for this use case. With ~25+ parent groups, showing all children immediately would produce an unmanageably tall sidebar. Discoverability is the key risk: users must learn that parent labels are interactive beyond just toggling the checkbox.

**Issues:**
- There is no expand/collapse affordance (no chevron, no `+` indicator). A user sees a label and a checkbox; there is nothing to indicate that clicking the label expands it. This is a real discoverability gap.
- The current cursor is `pointer` on the label (correct), but on a dark theme where the label dims when unchecked, a dimmed label with pointer cursor may not be noticed.

**Recommendations:**
- Add a small chevron (`›` or `⌄`) to the right side of any parent label that has children. When collapsed: `›` pointing right. When expanded: rotated 90° pointing down. This is a CSS `transform: rotate()` on a `::after` pseudo-element; no markup changes required if the `.has-children` class is added from Python.
- The chevron color should match the label color (white when active, dimmed when inactive).
- Do not add expand/collapse per-child-item. The children themselves remain simple checkboxes.

---

## 6. Popup Usability

**Current field order:** pagination controls → title (site name) → Event → Status (badge) → Description → Site → Principal Investigator → Email

**Assessment of field order:** The order is mostly logical — name first, then administrative fields, then contact. However, there are two problems:

1. **"Site" appears after "Description"** — but `site` and `name` are related (site is the sub-location name, name is the point label). Having them separated by Description is confusing. Site should appear immediately after the title or be combined with it.

2. **"Principal Investigator" is verbose** — in a popup that must fit at `width: 360px`, "Principal Investigator:" consumes roughly 40% of the label budget. On a dark background at small size (`0.85rem`), this long label forces the value onto a second line. Shorten to "PI:" consistently. The current code already uses `props["principal investigator"]` for the data key; only the display label in the HTML template needs changing.

3. **Status badge placement** — placing Status immediately after Event is fine. The badge styling (colored pill) works well and will remain readable on a dark background provided the badge itself has adequate contrast. The `status-badge--planned` color (`color: rgb(20, 100, 200)`) will be nearly invisible on a dark popup background — this must change (see design spec for token values).

4. **Popup background** — currently white (`background: #ffffff`). On an ESRI satellite basemap (very dark), a pure-white popup is harsh and high-contrast. Recommend `background: #1C2226` with `color: #E8EDF0` and `border: 1px solid rgba(255,255,255,0.15)`. The popup close button, nav buttons, and dividers all need corresponding dark-theme updates.

5. **Camp site popup** — has only three fields (title, Event, Season). This is appropriately minimal. No changes recommended to field set.

**Recommended field order for science event popup:**
pagination → title → Site → Event → Status → Description → PI → Email

Moving Site to position 2 (directly under title) groups the two location identifiers together. All else stays.

---

## 7. Bulk Actions — Select All / Deselect All

**Current:** Two equal-width buttons in a flex row directly under the "Science Events" heading, above a horizontal rule, above the checklist items. They are styled as small secondary buttons (`font-size: 0.78rem`, light background, border).

**Assessment:** Placement is good — above the list is the correct position for actions that affect the whole list. The equal-width flex row is fine. The main issues are:

- On dark theme, `background: #F0F2F4` becomes a light rectangle that floats awkwardly over a dark sidebar.
- The two buttons look identical (same color, same weight). There is no visual distinction between a neutral "select" action and the potentially destructive "deselect" action.

**Recommendations:**
- On dark theme: both buttons should use a ghost treatment — `background: transparent; border: 1px solid rgba(255,255,255,0.18); color: rgba(255,255,255,0.65)` at rest.
- On hover: `background: rgba(255,255,255,0.07)` — a subtle highlight.
- Give "Deselect all" a slightly warmer border tint (`rgba(255,120,80,0.35)`) and text color (`rgba(255,160,130,0.85)`) to signal that it removes selections. This is a mild visual distinction, not a destructive red — appropriate for a recoverable action.
- Keep both buttons the same size; do not make one prominent.
- The `sidebar__hr` between the bulk actions and the checklist list can be removed. The 12px gap from `layer-checklist` provides sufficient separation without a rule.

---

## 8. Export Button

**Current:** Full-width dark button (`background: #2F3A40`) at the very bottom of the sidebar, below a `sidebar__hr--export` divider with extra margin above and below. Label: "⬇ Export visible layers as GeoJSON". Font size `0.8rem`.

**Assessment:** Placement at the bottom is correct — export is an infrequent secondary action. The full-width treatment is appropriate for a single action. The current dark button (`#2F3A40`) will become almost invisible on a dark sidebar because it will blend into the background.

**Recommendations:**
- On dark theme, invert the treatment: use a bordered ghost button rather than a filled button. `background: transparent; border: 1px solid rgba(255,255,255,0.25); color: rgba(255,255,255,0.75)`.
- On hover: `background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.45)`.
- Keep the download arrow icon — it is clear and correct. The emoji `⬇` will render differently across OS; consider replacing with an SVG icon (a simple 16×16 arrow-down-to-line) inserted via `html.Span` with an inline SVG, consistent with the basemap button's SVG approach.
- Keep full width. Do not change the font size.
- The extra-large top margin on `sidebar__hr--export` (`margin-top: 20px; margin-bottom: 20px`) creates an unusually large gap. On a scrollable dark sidebar this whitespace looks like an oversight. Reduce to `margin-top: 12px; margin-bottom: 12px`.

---

## 9. Basemap Switcher

**Current:** A 34×34px icon button (stacked-layers SVG) positioned at top-right of the map, below the zoom buttons. Clicking it opens a small panel to the left of the button with two options: "BAS Satellite" and "ESRI Satellite". The active option is rendered with a dark fill and checkmark. Clicking anywhere else on the map closes the panel.

**Discoverability assessment:** Moderate. The icon (three stacked polygons) is a conventional layers/basemap symbol and should be recognizable to GIS-familiar users. However:

- The button is visually identical in style to the zoom buttons, so it doesn't signal a different function category. A user might skip past it looking for a dedicated "basemap" control.
- There is no tooltip displayed by default on desktop; the `title="Switch base map"` attribute only shows on hover after ~1 second delay. First-time users will hover and click speculatively.
- The panel label "Base map" (inside the opened panel) is only visible after clicking — not before.

**Recommendations:**
- The icon and position are fine. Do not move the button.
- On dark theme, the button needs the same restyling as the zoom buttons: dark fill (`#1A1E22`), lighter border (`rgba(255,255,255,0.2)`), white icon (`color: #E8EDF0`).
- Add a visible 3-4 character text label `"MAP"` below the SVG icon inside the button, or replace the SVG with a text label entirely. Given the button is 34px tall this is tight; alternatively, increase the button to 40px to accommodate a small caption. This makes the function legible without hover.
- The panel's `right: 42px` positioning (appearing to the left of the button) is correct and avoids overflow. Keep it.
- The close-on-map-click behavior is correct. No change needed.

---

## 10. Additional UX Issues

**10a. Divider overuse**

There are currently 7 `<hr>` elements in the sidebar for 4 sections. The pattern is: heading → hr → list → hr → heading → hr → list → hr → ... Each heading is sandwiched by dividers. This is redundant — a heading is itself a section delimiter. The rules above each heading can be removed; keep only the rule below each heading (between heading and its list). This reduces visual noise and tightens the layout.

**10b. Sidebar scrollbar on dark theme**

The sidebar uses `overflow-y: auto`. Browser default scrollbars are light-themed and will show as a bright bar on a dark sidebar. Add:
```css
.sidebar::-webkit-scrollbar { width: 6px; }
.sidebar::-webkit-scrollbar-track { background: transparent; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.18); border-radius: 3px; }
.sidebar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.32); }
```
Firefox: add `scrollbar-color: rgba(255,255,255,0.18) transparent; scrollbar-width: thin;` to `.sidebar`.

**10c. Hit-target size for nested child checkboxes**

The nested children use `line-height: 1.0` and have `margin: 0 !important; padding: 0 !important` forced onto `.dash-checkbox`. This compresses the hit targets to the point where clicking adjacent to the label text fails to register. Each nested checkbox row should have at least `padding: 3px 0` to bring the clickable area to approximately 24px tall (a minimum comfortable touch/click target).

**10d. Popup width on small screens**

The popup is fixed at `width: 360px`. On a 1280px display (which is a common laptop resolution for field use), the map area is approximately 960px wide. The popup at 360px is 37.5% of the map width — acceptable. However, on a 1024px or smaller display, the 320px sidebar + 360px popup leaves only ~344px of visible map behind the popup. Consider reducing to `width: 300px; min-width: 260px` and allowing the layout to flex, or add a `max-width: min(360px, calc(100vw - 360px))` to keep it within viewport.

**10e. Popup positioning — bottom-center**

The popup uses `positioning: "bottom-center"` with `offset: [0, -12]`, meaning it appears above the clicked point. This is generally correct. However, when a point is near the top of the map view, the popup will extend off-screen. OpenLayers does not automatically reposition. The existing code does not handle this edge case. Recommendation: add a check after `popupOverlay.setPosition(evt.coordinate)` that tests whether `popupContainer.getBoundingClientRect().top < 0` and if so, sets the overlay positioning to `"top-center"` with `offset: [0, 12]`. This is a small JS addition to the existing `singleclick` handler.

**10f. No visual feedback on map click before popup renders**

Between a click and the popup appearing there is no cursor change or loading indicator. On first load, GeoJSON layers are fetched asynchronously and points may not yet be registered. A user clicking too early gets no response and no explanation. While this is transient, consider adding a brief `cursor: wait` on the map container while layers are loading, removed once all fetches resolve.

**10g. Export emoji glyph rendering**

The export button label uses the `⬇` Unicode character (U+2B07 DOWNWARDS BLACK ARROW). On Windows 11 this renders as a colored emoji glyph, not a monochrome icon, making it appear inconsistent with the rest of the UI. Replace with the SVG arrow-down pattern already used elsewhere in the codebase (e.g. the copy-email and layers-control SVG icons).

---

## Summary Priority Table

| # | Issue | Priority | Effort |
|---|-------|----------|--------|
| 2 | Section heading style (uppercase, tracked, muted) | High | Low |
| 4 | Active state label dimming (checked=white, unchecked=dimmed) | High | Low |
| 3 | Custom toggle dots replacing native checkboxes | High | Medium |
| 6 | Popup dark background + "PI:" label + Site field order | High | Low |
| 1 | Section reorder (Locations first) | Medium | Low |
| 8 | Export button ghost treatment on dark theme | Medium | Low |
| 7 | Bulk actions ghost treatment + deselect tint | Medium | Low |
| 5 | Chevron affordance on expandable parents | Medium | Low |
| 10b | Dark scrollbar | Medium | Low |
| 9 | Basemap button label/dark restyling | Medium | Low |
| 10a | Remove redundant dividers | Low | Low |
| 10c | Nested checkbox hit targets | Low | Low |
| 10d | Popup width on small screens | Low | Low |
| 10e | Popup top-edge repositioning | Low | Medium |
| 10f | Load cursor feedback | Low | Low |
| 10g | Export emoji → SVG | Low | Low |
