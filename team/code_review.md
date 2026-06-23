# Code Review — Dark Theme Redesign
**Reviewer:** Code Reviewer
**Date:** 2026-06-23
**Files audited:** `assets/style.css`, `assets/ol-map.js`, `app.py`
**Spec refs:** `team/design_spec.md`, `team/ux_review.md`

---

## PASS Items — Confirmed Correct

- All 25 CSS custom-property tokens in `:root` match the spec colour table exactly (values and names).
- Global scrollbar rules use `var()` tokens; applied at page scope, not scoped to `.sidebar`.
- `.sidebar` includes Firefox `scrollbar-color` / `scrollbar-width` in addition to webkit rules.
- Every component background, border, and text colour uses a token, with zero raw hex values outside `:root` except the three spec-sanctioned exceptions (`#ffffff` on export button, `#ffffff` on label hover, `#7FDBFF` accent-color fallback).
- `.sidebar__hr--export` margin reduced from 20px to 12px per UX recommendation 8.
- `!important` usage on zoom buttons is intentional and matches spec (overriding OL defaults).
- All CSS class names are preserved exactly as listed in spec section 5 Must-not-change.
- Default basemap: `baseLayers.forEach((l) => l.setVisible(l.get("basemap-id") === "esri_imagery"))` — correct predicate form per spec. (ol-map.js line 546)
- `activeBasemapId` initialised to `"esri_imagery"`. (ol-map.js line 569)
- K150A fill updated to `rgba(80, 160, 255, 0.9)` — correct per spec. (ol-map.js line 211)
- K872B--ACTIVE and K872B--PLANNED both updated to `rgba(220, 60, 60, 0.95)` — correct per spec. (ol-map.js lines 275, 283)
- `escapeHtml()` function present and applied to all user-data values before innerHTML insertion — XSS mitigated.
- Logo src changed to `ANZ_Logo_Horizontal_Badge_White_RGB.png` in `app.py`. (line 540)
- Export button label is `↓ Export visible layers as GeoJSON` using a plain Unicode arrow (U+2193), not the emoji U+2B07. (app.py line 605)
- `.popup-nav-btn` correctly uses `color-bg-control` and `color-border-control` tokens.
- `.bm-panel` and `.bm-panel__heading` correctly styled with tokens.
- `.status-badge` variants all use correct token pairs.
- `.layer-checklist--nested .dash-checkbox` now has `padding: 3px 0 !important` — UX item 10c addressed.
- White stroke (`color: "white"`) retained in `makeScaledPointStyle`.

---

## ISSUES

### Issue 1 — MAJOR | Popup field order does not follow UX recommendation
**File:** `assets/ol-map.js`, lines 677–698 (`renderFeaturePage`)

**Observed order:** pagination → title → Event → Status → Description → **Site** → PI → Email

**Required order (ux_review.md §6):** pagination → title → **Site** → Event → Status → Description → PI → Email

The "Site" field (`siteNameEsc`) is rendered after Description, not immediately after the title. The UX review is explicit: Site should be grouped with the title as a sub-location identifier. This is a high-priority UX recommendation that was left unimplemented.

**Recommended fix:** Move the `siteNameEsc` block from after `measurementEsc` to directly after the `popup-title` div in `renderFeaturePage`.

---

### Issue 2 — MAJOR | "Principal Investigator" label not shortened to "PI:"
**File:** `assets/ol-map.js`, line 687

**Current:** `<div class="popup-pi"><strong>Principal Investigator:</strong> ${piEsc}</div>`

**Required (ux_review.md §6, point 2):** Label should be `PI:` to save horizontal space at 0.85rem in a 360px popup.

This is a high-priority UX fix rated "Low effort" in the summary table. It was not implemented.

**Recommended fix:** Change `Principal Investigator:` to `PI:` in the popup HTML template.

---

### Issue 3 — MAJOR | Sidebar section order does not match UX recommendation
**File:** `app.py`, lines 553–599

**Observed order in layout:** Science Events → Locations → Instruments → Camp Sites

**Required order (ux_review.md §1):** Locations → Science Events → Instruments → Camp Sites

The UX review rates this Medium priority with Low effort. Science Events appears first in the sidebar, leaving users without spatial orientation anchors (Locations) before encountering the K-code event list. The spec note in `app.py` line 401 even comments "Combined dict used by all callbacks — science first, locations second" indicating the Engineer was aware of the conflict but did not resolve it.

**Recommended fix:** In `app.layout`, reorder the sidebar children so that the Locations heading and `build_location_sidebar()` block appear first, followed by the Science Events heading + bulk actions + `build_sidebar()` block. The `ALL_GROUPS` ordering in callbacks does not affect UI ordering — it is safe to reorder the layout independently.

---

### Issue 4 — MINOR | `K862A--CIR` group name has a typo in ol-map.js
**File:** `assets/ol-map.js`, line 249

**Current:** `group: "KK862A - ApRES & GNSS"` (double K)

**Expected:** `"K862A - ApRES & GNSS"` (matches K862A--KIS2 and K862A--KIS3 entries)

This is a pre-existing data issue but was not caught or corrected during the redesign. It will cause the K862A--CIR entry to appear under a separate group key in any future sidebar integration that mirrors the JS registry.

**Recommended fix:** Correct to `"K862A - ApRES & GNSS"` at line 249.

---

### Issue 5 — MINOR | `K862A_KIS2` id mismatch between app.py and ol-map.js
**File:** `app.py`, line 203

**In app.py:** `"id": "K862A_KIS2"` (underscore separator)
**In ol-map.js:** `"id": "K862A--KIS2"` (double-dash separator, line 229)

The `setLayerVisibility` callback matches on `layer.get("id")`. The id written by `buildLayer` from ol-map.js is `"K862A--KIS2"`, but the visibility store from app.py will write key `"K862A_KIS2"`. These strings will never match, meaning K862A Site 2 (Kamb Ice Stream) cannot be toggled off from the sidebar.

This is a pre-existing bug that was not caught or corrected during the redesign. The dark-theme implementation does not introduce it, but the review is the right place to flag it.

**Recommended fix:** Change `app.py` line 203 to `"id": "K862A--KIS2"` to match the JS registry.

---

### Issue 6 — MINOR | K881B--PLANNED file path has a single-dash typo in app.py
**File:** `app.py`, line 269

**Current:** `"file": "K881B-PLANNED.geojson"` (single dash)
**Expected:** `"K881B--PLANNED.geojson"` (double dash, consistent with naming convention and the untracked file `assets/K881B--PLANNED.geojson` visible in git status)

The fetch in ol-map.js will 404 for this layer. This is a pre-existing issue not introduced by the redesign but not corrected either.

**Recommended fix:** Change to `"K881B--PLANNED.geojson"` at app.py line 269.

---

### Issue 7 — MINOR | K020A--BUDDAH_LAKE and K020A--MINNA_BLUFF use incorrect `value` keys in app.py
**File:** `app.py`, lines 55–56 and 63–64

```python
"value": "K082A--BUDDAH_LAKE",   # line 55 — should be K020A--BUDDAH_LAKE
"value": "K082A--MINNA_BLUFF",   # line 63 — should be K020A--MINNA_BLUFF
```

The `value` field is the key that flows from Dash checklist to the visibility store and thence to `setLayerVisibility`. The JS layer `id` for these entries is `K020A--BUDDAH_LAKE` and `K020A--MINNA_BLUFF`. With `K082A--*` values, the visibility callback will never toggle these layers correctly — their IDs will never appear in the visible set. Pre-existing bug, not introduced by redesign.

**Recommended fix:** Correct values to `"K020A--BUDDAH_LAKE"` and `"K020A--MINNA_BLUFF"` respectively.

---

### Issue 8 — MINOR | `sidebar__heading` letter-spacing: spec says 0.08em, UX review says 0.12em — implementation chose spec value (correct, but note discrepancy)
**File:** `assets/style.css`, line 161

The spec (`design_spec.md` §3) specifies `letter-spacing: 0.08em`. The UX review (§2) suggests `0.12em`. The Engineer used `0.08em`, correctly deferring to the design spec as the authoritative source. No action required, but the team should align the two documents for future reference.

---

### Issue 9 — MINOR | Export button: spec says `color: #ffffff`; CSS implements exactly that but spec token table has no `--color-text-inverse-white` token for it
**File:** `assets/style.css`, line 313

`color: #ffffff` on the export button is one of the three documented raw-hex exceptions (per spec §3 export button table, which explicitly states `#ffffff`). This is correct. The comment block at the top of `:root` promises "No raw hex values appear outside this :root block" — which is true for all other rules. The three exceptions (`#ffffff` export, `#ffffff` label hover, `#7FDBFF` checkbox accent) are all spec-sanctioned and noted inline in comments. No action required; flagged for transparency.

---

## UX Compliance Table

| # | UX Recommendation | Status | Notes |
|---|---|---|---|
| 1 | Section reorder: Locations first, then Science Events, Instruments, Camp Sites | **Not implemented** | app.py layout retains Science Events first. Medium priority, Low effort. |
| 2 | Section heading style: uppercase, tracked, small (0.75rem), muted colour | **Implemented** | CSS matches spec. Minor discrepancy in letter-spacing (0.08em vs UX suggestion of 0.12em) — spec deferred to correctly. |
| 3 | Custom toggle dots replacing native checkboxes | **Not implemented** | Native `<input type="checkbox">` with `accent-color` retained. UX rates this High / Medium effort. Out of scope for a CSS-only pass; requires structural HTML changes. |
| 4 | Active state label dimming (checked = white, unchecked = dimmed to 40% opacity) | **Not implemented** | Labels remain flat `--color-text-primary` regardless of checked state. High priority / Low effort, CSS-only achievable via `:has(:checked)` or a class. |
| 5 | Chevron affordance (›/⌄) on expandable parent labels | **Not implemented** | No indicator of expand/collapse. Medium priority / Low effort. |
| 6 | Popup: dark background, "PI:" label, Site field before Event | **Partially implemented** | Popup dark background fully implemented. "PI:" label NOT changed (still "Principal Investigator:"). Site field order NOT changed (still after Description). |
| 7 | Bulk actions ghost treatment + Deselect all warm tint | **Partially implemented** | Buttons use `--color-bg-control` fill, not the ghost treatment the UX recommended (`background: transparent; border: rgba(255,255,255,0.18)`). The deselect warm tint is not applied — both buttons are identical. |
| 8 | Export button ghost treatment on dark theme | **Not implemented** | Export button is filled blue (`--color-accent-export`), not ghost. The spec adopted the accent-blue treatment instead; the UX and spec diverge here. The spec is authoritative — this is a spec/UX conflict, not an Engineer error. |
| 9 | Basemap switcher dark restyling | **Implemented** | Button uses `--color-bg-control`, icon via `currentColor`, panel dark. The UX suggestion to add a text label "MAP" below the icon was not implemented but is not in scope for the dark-theme CSS pass. |
| 10a | Remove redundant dividers above headings | **Not implemented** | Layout retains `hr` above every section heading. Low priority. |
| 10b | Dark scrollbar | **Implemented** | Global webkit scrollbar rules + Firefox `scrollbar-color` applied. |
| 10c | Nested checkbox hit targets (padding: 3px 0) | **Implemented** | `padding: 3px 0 !important` applied to `.dash-checkbox`. |
| 10d | Popup width on small screens | **Not implemented** | `width: 360px` fixed, no `max-width` breakpoint. Low priority. |
| 10e | Popup top-edge repositioning | **Not implemented** | No JS edge-case repositioning added. Low priority / Medium effort. |
| 10f | Load cursor feedback | **Not implemented** | No `cursor: wait` during layer fetch. Low priority. |
| 10g | Export emoji → plain arrow | **Implemented** | Label uses `↓` (U+2193 DOWNWARDS ARROW), not emoji U+2B07. |

---

## Contrast Spot-Check Table

Calculated via WCAG 2.1 relative luminance formula.

| Pair | Foreground | Background | Calculated ratio | WCAG AA (4.5:1 normal / 3:1 large) | Result |
|---|---|---|---|---|---|
| Primary text on sidebar | `#dce8f0` | `#111820` | **14.33:1** | Requires 4.5:1 | PASS |
| Primary text on popup/panel | `#dce8f0` | `#18222e` | **12.89:1** | Requires 4.5:1 | PASS |
| Muted text on sidebar (headings, indicators) | `#6e8fa8` | `#111820` | **5.24:1** | Requires 4.5:1 | PASS |
| Muted text on popup (field labels, close btn) | `#6e8fa8` | `#18222e` | **4.71:1** | Requires 4.5:1 | PASS (borderline — spec noted this; raise to `#7ba4bf` if needed) |
| Export button text on accent blue | `#ffffff` | `#2a7fbf` | **4.30:1** | Requires 4.5:1 | **FAIL** — 0.20:1 below AA threshold |

**Note on export button contrast failure:** `#ffffff` on `#2a7fbf` yields 4.30:1, which falls below the 4.5:1 AA threshold for normal-text body copy. The export button text at `0.8rem / 500 weight` is normal text, not large text (large text threshold is 18pt/24px or 14pt/19px bold). The spec's own WCAG table states 4.7:1 for this pair — that value is incorrect; the actual calculated ratio is 4.30:1. This is a Minor issue but should be noted. Raising the background to `#2d87c8` would bring the ratio to approximately 4.7:1.

**Additional ratios for reference (not in the 5-row table above):**
- Badge active text `#4dd966` on `#18222e`: 8.75:1 — PASS
- Badge planned text `#6ab4ff` on `#18222e`: 7.33:1 — PASS
- Badge wishlist text `#ffb347` on `#18222e`: 9.02:1 — PASS
- Active basemap text `#dce8f0` on `#1f3c58`: 9.13:1 — PASS
- Primary text on control button `#dce8f0` / `#1c2a38`: 11.72:1 — PASS

---

## Overall Verdict

**Ship with fixes**

The dark theme implementation is structurally sound: all colour tokens are correct, the basemap default is updated, K150A and K872B colours are fixed, XSS is mitigated, class names are preserved, and the CSS is clean with no specificity abuse. The app will load and function correctly in its primary flows.

However, three issues are significant enough to address before release:

1. **Issue 1** (popup Site field order) and **Issue 2** ("PI:" label) are both High-priority UX items rated Low effort that were not implemented. They are two-line JS changes in `ol-map.js`.
2. **Issue 3** (sidebar section order) is a Medium-priority UX item rated Low effort. Reordering the layout children in `app.py` is straightforward.
3. **Issue 5** (K862A--KIS2 id mismatch) is a functional bug — the layer cannot be toggled by the sidebar at all.
4. **Issue 6** (K881B--PLANNED 404) and **Issue 7** (K020A wrong value keys) are also functional bugs that prevent two layers from loading correctly.
5. **Contrast issue on export button** (4.30:1 vs required 4.5:1): Minor but technically a WCAG AA fail.

Issues 4–7 are pre-existing bugs not introduced by the redesign, but this review is the appropriate gate to catch them.

The Engineer should address Issues 1–7 and the export button contrast before the Phase 4 wrap-up sign-off.
