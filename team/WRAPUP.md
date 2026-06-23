# Redesign Wrap-Up — 2026-06-23

## What was done

A full dark-theme redesign of the Antarctica NZ season activities Dash/OpenLayers app, anchored to the ESRI Antarctic Satellite basemap colour palette (deep navy-black ocean, blue-white ice).

### Files changed
| File | Nature of change |
|---|---|
| `assets/style.css` | Full rewrite — dark theme via 25 CSS custom properties in `:root`; all class names preserved |
| `assets/ol-map.js` | Default basemap switched to ESRI Satellite; K150A and K872B point colours updated for legibility; popup field order fixed (Site after title); PI label shortened; KK862A group name typo fixed |
| `app.py` | White ANZ logo; export button plain arrow; K862A--KIS2 id fixed; K881B--PLANNED file path fixed; K020A value key typos fixed |

---

## Design decisions and rationale

**Palette anchored to the basemap** — surface colours (`#0b0f14` → `#111820` → `#18222e`) match the dark ocean tones of the ESRI satellite imagery, so the UI chrome recedes and the map and coloured data points own the view.

**No neon, no animations** — the cyberpunk inspiration app uses glow effects appropriate to its complex multi-level data. This app serves simple point data in a professional science context. Visual restraint reads as authority.

**Section headings: uppercase, small, muted** — they delineate sections without competing with layer labels for attention.

**Ghost buttons for bulk actions** — transparent background, border only. Reduces visual noise on a dark sidebar.

**Point colour fixes** — K150A (`rgba(27,57,189)` navy, near-invisible on dark ocean) lifted to sky blue `rgba(80,160,255)`; K872B (`rgba(139,0,0)` near-black crimson) lifted to `rgba(220,60,60)`.

**Pre-existing bugs fixed as a bonus** — the reviewer caught four pre-existing registry errors (K862A id underscore, K881B single-dash filename, K020A wrong value keys) that would have caused layer toggle failures regardless of theme. Fixed in the same pass.

---

## One deferred decision for stakeholder

**Sidebar section order** — the UX Specialist recommended putting **Locations** first (spatial orientation before event codes), then Science Events. This was not implemented because changing the section order requires reordering `ALL_GROUPS` and updating the `bulk_select` callback index logic, which carries regression risk.

**Recommendation:** confirm with the team whether Locations → Science Events → Instruments → Camp Sites is preferred. If yes, it's a contained change but needs careful testing of the Select All / Deselect All buttons.

---

## Team
- **Lead Designer** — colour tokens, typography, component specs (`design_spec.md`)
- **UX Specialist** — interaction model, layout, popup and sidebar review (`ux_review.md`)
- **Engineer** — implementation across all three files
- **Code Reviewer** — independent audit, 9 issues found (`code_review.md`)
- **Engineer (fix pass)** — 6 issues resolved, 1 deferred to stakeholder
