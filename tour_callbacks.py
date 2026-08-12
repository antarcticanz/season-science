# tour_callbacks.py

"""
Tour callbacks — ported from the EBR dashboard 2026-08-13.

Season Science is single-page (single tour tab: "map"), so:
  * only one per-tab state callback,
  * no cross-tab dismissal risk (gotcha #2 doesn't apply),
  * the only competing overlay is the About / info modal (btn-info) —
    a single always-present close-on-overlay callback covers it.

State transitions:
  * advance:   current_step += 1   (final step → reset first_visit=False)
  * back:      max(current_step - 1, 0)
  * skip/exit/×/Esc: terminal dismiss (first_visit=False, dismissed=True)
  * auto-launch: current_step=0 iff first_visit is still True
  * chip click:  current_step=0 WITHOUT mutating first_visit
"""

from dash import Input, Output, callback_context, clientside_callback
from dash.dependencies import State
from dash.exceptions import PreventUpdate

from components.tour_steps import MAP_STEPS


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_TERMINAL_STATE = {
    "first_visit": False,
    "current_step": None,
    "dismissed": True,
}


def _coerce_state(data):
    if not isinstance(data, dict):
        data = {}
    return {
        "first_visit": bool(data.get("first_visit", True)),
        "current_step": data.get("current_step", None),
        "dismissed": bool(data.get("dismissed", False)),
    }


def _which_triggered() -> str:
    ctx = callback_context
    if not ctx.triggered:
        return ""
    return ctx.triggered[0].get("prop_id", "").split(".")[0]


# ---------------------------------------------------------------------------
# Per-tab state machine (only tab = "map")
# ---------------------------------------------------------------------------
def _make_tour_state_callback(app, tab: str, steps: list):
    n_steps = len(steps)
    store_id = f"tour-state-{tab}"
    next_id = f"tour-next-{tab}"
    back_id = f"tour-back-{tab}"
    skip_id = f"tour-skip-{tab}"
    close_id = f"tour-close-{tab}"
    esc_id = f"tour-esc-{tab}-signal"
    auto_id = f"tour-auto-launch-{tab}"

    @app.callback(
        Output(store_id, "data"),
        [
            Input(next_id, "n_clicks"),
            Input(back_id, "n_clicks"),
            Input(skip_id, "n_clicks"),
            Input(close_id, "n_clicks"),
            Input(esc_id, "data"),
            Input(auto_id, "data"),
            Input("topbar-tutorial", "n_clicks"),
        ],
        State(store_id, "data"),
        prevent_initial_call=True,
    )
    def _update_tour_state(
        _next,
        _back,
        _skip,
        _close,
        _esc,
        _auto,
        _chip,
        current,
    ):
        trigger = _which_triggered()
        if not trigger:
            raise PreventUpdate

        state = _coerce_state(current)

        # Terminal dismisses.
        if trigger in (skip_id, close_id, esc_id):
            return dict(_TERMINAL_STATE)

        # Auto-launch: only on true first-visit.
        if trigger == auto_id:
            if not state["first_visit"]:
                raise PreventUpdate
            return {
                "first_visit": True,
                "current_step": 0,
                "dismissed": False,
            }

        # Return-visit chip: open at step 0 without touching first_visit.
        if trigger == "topbar-tutorial":
            return {
                "first_visit": state["first_visit"],
                "current_step": 0,
                "dismissed": False,
            }

        # Back.
        if trigger == back_id:
            cur = state["current_step"]
            if cur is None:
                raise PreventUpdate
            return {
                "first_visit": state["first_visit"],
                "current_step": max(cur - 1, 0),
                "dismissed": False,
            }

        # Advance / FINISH.
        if trigger == next_id:
            cur = state["current_step"]
            if cur is None:
                return {
                    "first_visit": state["first_visit"],
                    "current_step": 0,
                    "dismissed": False,
                }
            nxt = cur + 1
            if nxt >= n_steps:
                return {
                    "first_visit": False,
                    "current_step": None,
                    "dismissed": False,
                }
            return {
                "first_visit": state["first_visit"],
                "current_step": nxt,
                "dismissed": False,
            }

        raise PreventUpdate

    return _update_tour_state


# ---------------------------------------------------------------------------
# Close-on-overlay — dismiss the tour when the info modal opens.
# ---------------------------------------------------------------------------
# btn-info lives in the shared title-pane (always mounted) so no per-tab
# split is needed (gotcha #3 doesn't apply). The value-guard is preserved
# defensively (gotcha #1) — Dash's clientside dispatcher can still fire
# once with n_clicks=0 on certain refresh paths despite
# `prevent_initial_call=True`.
_CLOSE_ACTIVE_TAB_JS = """
function() {
    const trig = window.dash_clientside.callback_context.triggered;
    if (!trig || trig.length === 0) return window.dash_clientside.no_update;
    if (!trig[0].value) return window.dash_clientside.no_update;

    const tab = 'map';
    const terminal = {first_visit: false, current_step: null, dismissed: true};
    if (window.dash_clientside && window.dash_clientside.set_props) {
        window.dash_clientside.set_props('tour-state-' + tab, {data: terminal});
    }
    // Belt-and-braces: hide popup + scrim in case the render callback lags.
    const popup = document.getElementById('tour-popup-' + tab + '-root');
    const scrim = document.getElementById('tour-scrim-' + tab);
    if (popup) popup.className = 'aa-tour aa-tour--hidden';
    if (scrim) scrim.className = 'aa-tour__scrim';
    return '';
}
"""


def _register_close_on_overlay(app):
    """Dismiss the tour when the About / info modal is opened."""
    clientside_callback(
        _CLOSE_ACTIVE_TAB_JS,
        Output("tour-mount-sink-map", "children", allow_duplicate=True),
        [Input("btn-info", "n_clicks")],
        prevent_initial_call=True,
    )


# ---------------------------------------------------------------------------
# Public registrar
# ---------------------------------------------------------------------------
def register_tour_callbacks(app):
    """Register the tour state machine + overlay closer."""
    _make_tour_state_callback(app, tab="map", steps=MAP_STEPS)
    _register_close_on_overlay(app)


__all__ = ["register_tour_callbacks"]
