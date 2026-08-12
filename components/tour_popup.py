# components/tour_popup.py

"""
Tour popup DOM factory — ported from the EBR dashboard 2026-08-13.

Season Science is single-page, so only ONE tour tab is exposed: "map".
The tab parameter is kept so a second tour can be added later without a
structural rewrite.

Stable ids (per-tab, suffix = tab arg):
  tour-popup-{tab}-root, tour-title-{tab}, tour-body-{tab},
  tour-body-text-{tab}, tour-skip-{tab}, tour-close-{tab},
  tour-exit-{tab}, tour-back-{tab}, tour-next-{tab},
  tour-next-label-{tab}, tour-counter-{tab}, tour-tail-{tab},
  tour-scrim-{tab}.

CSS contract (see assets/style.css — .aa-tour* block):
  .aa-tour, .aa-tour--hidden, .aa-tour__header, .aa-tour__title,
  .aa-tour__close, .aa-tour__body, .aa-tour__footer, .aa-tour__exit,
  .aa-tour__back, .aa-tour__next, .aa-tour__next--finish,
  .aa-tour__tail (+ --top/--bottom/--left/--right), .aa-tour__scrim.

ARIA: role="dialog", aria-modal="false", no focus trap.
"""

from dash import html


_VALID_TABS = ("map",)


def tour_popup(tab: str):
    """Return `[popup_root, scrim]` for a given tour tab."""
    if tab not in _VALID_TABS:
        raise ValueError(
            f"tour_popup(tab): tab must be one of {_VALID_TABS}, got {tab!r}"
        )

    header = html.Div(
        className="aa-tour__header",
        children=[
            html.H4("", id=f"tour-title-{tab}", className="aa-tour__title"),
            html.A(
                "Skip tour",
                id=f"tour-skip-{tab}",
                role="button",
                tabIndex=0,
                style={
                    "cursor": "pointer",
                    "color": "var(--color-text-muted)",
                    "fontSize": "13px",
                    "textDecoration": "underline",
                    "whiteSpace": "nowrap",
                },
            ),
            html.Button(
                "×",
                id=f"tour-close-{tab}",
                className="aa-tour__close",
                n_clicks=0,
                **{"aria-label": "Close tour"},
            ),
        ],
    )

    body = html.Div(
        id=f"tour-body-{tab}",
        className="aa-tour__body",
        children=[html.P("", id=f"tour-body-text-{tab}")],
    )

    footer = html.Div(
        className="aa-tour__footer",
        children=[
            html.Button(
                "BACK",
                id=f"tour-back-{tab}",
                className="aa-tour__back",
                n_clicks=0,
                disabled=True,
            ),
            html.Button(
                children=[
                    html.Span("NEXT", id=f"tour-next-label-{tab}"),
                    html.Span(" ", **{"aria-hidden": "true"}),
                    html.Span("(0/0)", id=f"tour-counter-{tab}"),
                ],
                id=f"tour-next-{tab}",
                className="aa-tour__next",
                n_clicks=0,
            ),
        ],
    )

    tail = html.Div(id=f"tour-tail-{tab}", className="aa-tour__tail")

    popup_root = html.Div(
        id=f"tour-popup-{tab}-root",
        className="aa-tour aa-tour--hidden",
        role="dialog",
        tabIndex=-1,
        **{
            "aria-modal": "false",
            "aria-labelledby": f"tour-title-{tab}",
            "aria-describedby": f"tour-body-{tab}",
        },
        children=[header, body, footer, tail],
    )

    scrim = html.Div(
        id=f"tour-scrim-{tab}",
        className="aa-tour__scrim",
        **{"aria-hidden": "true"},
    )

    return [popup_root, scrim]
