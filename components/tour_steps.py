# components/tour_steps.py

"""
Tour step definitions for the Antarctica NZ 2026-27 map.

Nine-step tour on the (single) map page. One tour tab — `map`. The
FEATURE_STATIONS dict is kept empty for schema parity — the season
map has no pan-to-hero-point moments; sidebar sections are scrolled
into view via `scroll_to` instead.

Step schema (matches the EBR/phyto lineage so `build_tour_steps_meta()`
stays generic):
    {
        "target":      str  — id of the element to anchor to,
        "title":       str  — H4 heading text,
        "body":        str | list — one sentence rendered in the popup body.
                                    Lists let you interleave inline icons
                                    (html.Span chips) with text so the
                                    tour matches on-screen controls
                                    visually.
        "position":    str  — one of "center" | "top" | "bottom" | "left" | "right",
        "offset_x":    int  — px shift after positioning; optional,
        "offset_y":    int  — px shift after positioning; optional,
        "scroll_to":   str  — id to scrollIntoView; optional,
        "hero_station": str — key in FEATURE_STATIONS to pan the map to; optional,
        "pan_to":      dict — direct {lat, lon, zoom} pan; optional,
        "spotlight":   bool — dim scrim behind popup on this step,
    }
"""

from dash import html


# No pan-to-station moments in the season map.
FEATURE_STATIONS = {}


def _icon(variant: str):
    """Inline chip-style icon that mirrors the corresponding map control.

    variant: one of "globe", "layers", "ruler", "marker".
    See assets/style.css → .tour-icon* for the SVG data URIs.
    """
    return html.Span(
        className=f"tour-icon tour-icon--{variant}",
        **{"aria-hidden": "true"},
    )


MAP_STEPS = [
    {
        "target": "ol-map",
        "title": [
            "Welcome to the New Zealand",
            html.Br(),
            "Science Activity Dashboard",
        ],
        "body": (
            "This map shows planned science activities, active instruments and "
            "field camp sites supported by Antarctica New Zealand"
        ),
        "position": "center",
        "spotlight": True,
        "width": 440,
    },
    {
        "target": "section-science-events",
        "title": "Planned Science Activities",
        "body": (
            "Toggle science activities (K-codes) on and off here. Activities "
            "with multiple sites can be expanded — pick individual locations, "
            "or use Select all / Deselect all above."
        ),
        "position": "right",
        "offset_x": 12,
    },
    {
        "target": "section-locations",
        "title": "Locations",
        "body": (
            "Aggregate layers for well-known sites like Arrival Heights and "
            "Scott Base. Handy when several events share a location"
        ),
        "position": "right",
        "offset_x": 12,
        "offset_y": -80,
        "scroll_to": "section-locations",
    },
    {
        "target": "section-instruments",
        "title": "Instruments",
        "body": (
            "Instruments deployed across the continent — Active (green), "
            "Offline, or scheduled for removal. Expand Active and pick an "
            "event to see only that team's equipment."
        ),
        "position": "right",
        "offset_x": 12,
        "scroll_to": "section-instruments",
    },
    {
        "target": "section-camp-sites",
        "title": "Camp Sites",
        "body": (
            "Historical field camps from the last three seasons — useful "
            "context when planning new deployments in familiar areas."
        ),
        "position": "right",
        "offset_x": 12,
        "offset_y": 80,
        "scroll_to": "section-camp-sites",
    },
    {
        "target": "basemaps-control",
        "title": "Basemaps",
        "body": [
            "Change basemaps ",
            _icon("globe")
        ],
        "position": "left",
        "offset_x": -12,
        "width": 360,
    },
    {
        "target": "overlays-control",
        "title": "Overlay layers",
        "body": [
            "Add layers ",
            _icon("layers"),
            " to toggle Antarctic Specially Protected Areas "
            "(ASPA, pink) and Specially Managed Areas (ASMA, amber) — "
            "helpful for planning around protected zones. Hover a polygon "
            "for its name and area.",
        ],
        "position": "left",
        "offset_x": -12,
        "width": 360,
    },
    {
        "target": "ruler-control",
        "title": "Measure distances",
        "body": [
            "Measure distances with the ruler ",
            _icon("ruler"),
            " , click points on the map to draw a path. "
            "The running total shows in kilometres — double-click to finish "
            "the measurement.",
        ],
        "position": "left",
        "offset_x": -12,
        "width": 360,
    },
    {
        "target": "ol-map",
        "title": "Click any marker",
        "body": [
            "Select a marker ",
            _icon("marker"),
            "  on the map to see event details — site name, principal "
            "investigator, contact, coordinates, and links to more "
            "information. That's the tour — enjoy exploring.",
        ],
        "position": "center",
        "spotlight": True,
    },
]


__all__ = ["FEATURE_STATIONS", "MAP_STEPS"]
