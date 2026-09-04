# components/about_sidebar.py

"""
About sidebar — right-hand slide-out pane.

Ported from EBR's `study_details_sidebar` (2026-08-13). Same DOM structure
and .aa-sidebar / .aa-sd-* class family, adapted to season-science tokens
and content.

Toggling: `btn-info` in the title-pane opens; `about-sidebar-close-btn`
closes. The clientside callback in app.py flips `.about-sidebar-open`
on `.app-root`; CSS shrinks `.body-row` right-padding to make room while
the pane slides in from translateX(100%) → translateX(0).
"""

from dash import html


INTRO = (
    "This interactive map shows planned science activities, active instruments "
    "and field camp sites supported by Antarctica New Zealand for the "
    "2026–27 season. Use the sidebar and map controls to explore "
    "what's happening on the ice."
)


# Section 1 — Overview: what the data represents.
OVERVIEW = [
    {
        "title": "Multi-year science programme",
        "body": (
            "Each K-code is a distinct science event supported this season "
            "— spanning ice cores, penguin census, atmospheric "
            "monitoring, and everything in between."
        ),
    },
    {
        "title": "Ross Dependency observation network",
        "body": (
            "Automated weather stations, GNSS receivers, ApRES ice-radar "
            "and seafloor moorings run year-round. Active instruments are "
            "shown in green; offline in orange."
        ),
    },
    {
        "title": "Field logistics context",
        "body": (
            "Historical camp sites from recent seasons help scope new "
            "deployments — fuel caches, hut availability and access "
            "windows all trace back to these locations."
        ),
    },
    {
        "title": "Specially protected and managed areas",
        "body": (
            "Antarctic Treaty ASPA (Specially Protected) and ASMA "
            "(Specially Managed) boundaries are available as overlays so "
            "planning respects the treaty framework."
        ),
    },
]


# Section 2 — Use the map: how to interact.
USE_THE_MAP = [
    {
        "title": "Filter with the sidebar",
        "body": (
            "Toggle events, locations, instruments and camp sites "
            "individually. Expand any group with multiple sites to pick "
            "specific locations, or use Select all / Deselect all shortcuts."
        ),
    },
    {
        "title": "Click any marker",
        "body": (
            "Every point reveals event name, principal investigator, "
            "contact email, coordinates and links to the ANTCAT metadata "
            "record when available. Multi-status sites merge into one card."
        ),
    },
    {
        "title": "Switch basemaps and overlays",
        "body": (
            "The globe button switches satellite imagery (ESRI, BAS, "
            "Landcare RAMP/REMA). The layers button toggles ASPA/ASMA "
            "overlays — hover any polygon for its name and area."
        ),
    },
    {
        "title": "Measure and export",
        "body": (
            "The ruler tool sums click-to-click distances in kilometres. "
            "The Export button at the bottom of the sidebar downloads "
            "every currently-visible feature as a single GeoJSON file."
        ),
    },
]


def _metric_tile(metric: dict) -> html.Div:
    """Big-number tile with label + hint. No dbc — plain Div."""
    return html.Div(
        [
            html.Div(metric["value"], className="aa-sd-tile__value"),
            html.Div(metric["label"], className="aa-sd-tile__label"),
            html.Div(metric["hint"], className="aa-sd-tile__hint"),
        ],
        className="aa-sd-tile",
    )


def _accent_card(index: int, item: dict, variant: str) -> html.Div:
    """Numbered accent card. `variant` selects the coloured bar/badge."""
    badge = html.Span(f"{index:02d}", className="aa-sd-card__badge")
    return html.Div(
        [
            html.Span(className="aa-sd-card__bar"),
            html.Div(
                [
                    html.Div(
                        [badge, html.H6(item["title"], className="aa-sd-card__title")],
                        className="aa-sd-card__head",
                    ),
                    html.P(item["body"], className="aa-sd-card__body"),
                ],
                className="aa-sd-card__inner",
            ),
        ],
        className=f"aa-sd-card aa-sd-card--{variant}",
    )


def _section(eyebrow: str, heading: str, items: list, variant: str) -> html.Section:
    cards = [_accent_card(i + 1, item, variant) for i, item in enumerate(items)]
    return html.Section(
        [
            html.Div(
                [
                    html.Span(eyebrow, className="aa-sd-section__eyebrow"),
                    html.H5(heading, className="aa-sd-section__heading"),
                ],
                className="aa-sd-section__head",
            ),
            html.Div(cards, className="aa-sd-section__cards"),
        ],
        className=f"aa-sd-section aa-sd-section--{variant}",
    )


def about_sidebar(
    planned_events: int,
    active_instruments: int,
    protected_areas: int = 148,
) -> html.Aside:
    """Fixed right-hand pane; visibility class-toggled on `.app-root`."""

    metrics = [
        {
            "value": str(planned_events),
            "label": "Planned science activities",
            "hint": "K-codes with field activity this season",
        },
        {
            "value": str(active_instruments),
            "label": "Active instruments",
            "hint": "Instruments deployed in the Ross Dependency",
        },
        {
            "value": str(protected_areas),
            "label": "Protected areas",
            "hint": "Antarctic Specially Protected Areas + Antarctic Specially Managed Areas available as overlays",
        },
    ]

    header = html.Div(
        [
            html.Span("About this map", className="aa-sidebar__header-title"),
            html.Button(
                [
                    html.Span("✕", **{"aria-hidden": "true"}),
                    html.Span("Close", className="visually-hidden"),
                ],
                id="about-sidebar-close-btn",
                n_clicks=0,
                className="aa-sidebar__close",
                **{"aria-label": "Close About"},
            ),
        ],
        className="aa-sidebar__header",
    )

    body = html.Div(
        [
            html.P(INTRO, className="aa-sd-intro"),
            html.Div([_metric_tile(m) for m in metrics], className="aa-sd-tiles"),
            html.Small(
                "Snapshot of the season as configured",
                className="aa-sd-tiles__caption",
            ),
            _section(
                eyebrow="Overview",
                heading="What you're looking at",
                items=OVERVIEW,
                variant="blue",
            ),
            _section(
                eyebrow="Interact",
                heading="Use the map",
                items=USE_THE_MAP,
                variant="green",
            ),
            html.Div(
                html.Small(
                    [
                        "New here? Try ",
                        html.Strong("Take the tutorial"),
                        " in the top bar for a guided walk-through.",
                    ],
                    className="aa-sd-footnote",
                ),
                className="aa-sd-footnote-wrap",
            ),
        ],
        className="aa-sidebar__scroll",
    )

    return html.Aside(
        [header, body],
        id="about-sidebar",
        className="aa-sidebar aa-sidebar--about",
        **{"aria-label": "About", "aria-hidden": "true"},
    )
