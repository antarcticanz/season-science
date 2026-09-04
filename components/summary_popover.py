"""
Research-summary popover — small anchored card that opens from a per-activity
info icon in the sidebar and shows the pre-rendered summary HTML.

DOM ids (stable, referenced by clientside JS):
  summary-popover-root, summary-popover-title, summary-popover-body,
  summary-popover-close, summary-popover-tail.

CSS contract: `.aa-summary` block in assets/style.css.
"""

from dash import html


def summary_popover():
    header = html.Div(
        className="aa-summary__header",
        children=[
            html.H4("", id="summary-popover-title", className="aa-summary__title"),
            html.Button(
                "×",
                id="summary-popover-close",
                className="aa-summary__close",
                n_clicks=0,
                **{"aria-label": "Close research summary"},
            ),
        ],
    )

    body = html.Div(
        id="summary-popover-body",
        className="aa-summary__body",
    )

    tail = html.Div(id="summary-popover-tail", className="aa-summary__tail")

    return html.Div(
        id="summary-popover-root",
        className="aa-summary aa-summary--hidden",
        role="dialog",
        tabIndex=-1,
        **{
            "aria-modal": "false",
            "aria-labelledby": "summary-popover-title",
            "aria-describedby": "summary-popover-body",
        },
        children=[header, body, tail],
    )
