# tour_clientside.py

"""
Tour clientside layer — ported from the EBR dashboard 2026-08-13.

Single tour tab: "map". Season Science has no map-pan story (the sidebar
drives visibility rather than a pan-to-hero sequence), so the mapbox-pan
callback is skipped. The scrollIntoView callback stays because sidebar
sections below the fold need to be brought into view.

Layers registered here:
  1. Popup content-render (server-side)
  2. Popup positioning (clientside JS)
  3. Scroll-into-view for `scroll_to` steps (clientside JS)
  4. Auto-launch on first visit (clientside JS + set_props)
  5. Keyboard listener: Esc / ← / → / Enter / Space (clientside JS)
"""

from dash import Input, Output, clientside_callback, no_update
from dash.dependencies import State

from components.tour_steps import MAP_STEPS, FEATURE_STATIONS


# ---------------------------------------------------------------------------
# 1. Popup content render (server-side)
# ---------------------------------------------------------------------------
_ROOT_VISIBLE = "aa-tour"
_ROOT_HIDDEN = "aa-tour aa-tour--hidden"
_NEXT_DEFAULT = "aa-tour__next"
_NEXT_FINISH = "aa-tour__next aa-tour__next--finish"
_SCRIM_OFF = "aa-tour__scrim"
_SCRIM_ON = "aa-tour__scrim is-visible"


def _register_content_render(app, tab: str, steps: list):
    n_steps = len(steps)

    @app.callback(
        [
            Output(f"tour-title-{tab}", "children"),
            Output(f"tour-body-text-{tab}", "children"),
            Output(f"tour-next-label-{tab}", "children"),
            Output(f"tour-next-{tab}", "className"),
            Output(f"tour-counter-{tab}", "children"),
            Output(f"tour-popup-{tab}-root", "className"),
            Output(f"tour-scrim-{tab}", "className"),
            Output(f"tour-back-{tab}", "disabled"),
        ],
        Input(f"tour-state-{tab}", "data"),
        prevent_initial_call=True,
    )
    def _render_popup(state):
        if not isinstance(state, dict):
            state = {}
        current = state.get("current_step")
        dismissed = bool(state.get("dismissed", False))

        # Hidden path.
        if current is None or dismissed:
            return (
                no_update, no_update, no_update, _NEXT_DEFAULT,
                no_update, _ROOT_HIDDEN, _SCRIM_OFF, True,
            )

        if not isinstance(current, int) or current < 0 or current >= n_steps:
            return (
                no_update, no_update, no_update, _NEXT_DEFAULT,
                no_update, _ROOT_HIDDEN, _SCRIM_OFF, True,
            )

        step = steps[current]
        is_final = current == n_steps - 1
        next_label = "FINISH" if is_final else "NEXT"
        next_class = _NEXT_FINISH if is_final else _NEXT_DEFAULT
        counter = (
            f"({n_steps}/{n_steps}) ✓" if is_final
            else f"({current + 1}/{n_steps})"
        )
        scrim_class = _SCRIM_ON if step.get("spotlight") else _SCRIM_OFF
        back_disabled = current == 0

        return (
            step["title"],
            step["body"],
            next_label,
            next_class,
            counter,
            _ROOT_VISIBLE,
            scrim_class,
            back_disabled,
        )


# ---------------------------------------------------------------------------
# 2. Popup positioning (clientside JS)
# ---------------------------------------------------------------------------
_POSITIONING_JS = """
function(state, meta) {
    if (!state || state.current_step === null || state.current_step === undefined || state.dismissed) {
        return '';
    }
    const tab = '__TAB__';
    const stepIdx = state.current_step;
    if (!meta || !meta[tab]) return '';
    const targets = meta[tab].targets || [];
    const positions = meta[tab].positions || [];
    if (stepIdx < 0 || stepIdx >= targets.length) return '';

    const targetId = targets[stepIdx];
    const position = positions[stepIdx] || 'center';
    const offsetsX = meta[tab].offsets_x || [];
    const offsetsY = meta[tab].offsets_y || [];
    const dx = Number(offsetsX[stepIdx]) || 0;
    const dy = Number(offsetsY[stepIdx]) || 0;
    const popup = document.getElementById('tour-popup-' + tab + '-root');
    const tail = document.getElementById('tour-tail-' + tab);
    if (!popup) return '';

    popup.style.position = 'fixed';
    popup.style.visibility = 'visible';

    // Per-step width override (null = keep CSS default).
    const widths = meta[tab].widths || [];
    const w = widths[stepIdx];
    if (w) {
        popup.style.maxWidth = w + 'px';
        popup.style.minWidth = w + 'px';
    } else {
        popup.style.maxWidth = '';
        popup.style.minWidth = '';
    }

    requestAnimationFrame(function () {
        const targetEl = document.getElementById(targetId);
        const popupRect = popup.getBoundingClientRect();
        const popupW = popupRect.width || 360;
        const popupH = popupRect.height || 160;
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const gap = 16;

        let top, left;
        let tailDir = null;

        if (position === 'center' || !targetEl) {
            top = Math.max(8, (vh - popupH) / 2);
            left = Math.max(8, (vw - popupW) / 2);
            tailDir = null;
        } else {
            const r = targetEl.getBoundingClientRect();
            if (position === 'top') {
                top = r.top - popupH - gap;
                left = r.left + (r.width / 2) - (popupW / 2);
                tailDir = 'bottom';
            } else if (position === 'bottom') {
                top = r.bottom + gap;
                left = r.left + (r.width / 2) - (popupW / 2);
                tailDir = 'top';
            } else if (position === 'left') {
                top = r.top + (r.height / 2) - (popupH / 2);
                left = r.left - popupW - gap;
                tailDir = 'right';
            } else if (position === 'right') {
                top = r.top + (r.height / 2) - (popupH / 2);
                left = r.right + gap;
                tailDir = 'left';
            } else {
                top = Math.max(8, (vh - popupH) / 2);
                left = Math.max(8, (vw - popupW) / 2);
                tailDir = null;
            }
        }

        top += dy;
        left += dx;

        top = Math.max(8, Math.min(top, vh - popupH - 8));
        left = Math.max(8, Math.min(left, vw - popupW - 8));

        popup.style.top = top + 'px';
        popup.style.left = left + 'px';

        if (tail) {
            if (tailDir === null) {
                tail.className = 'aa-tour__tail';
                tail.style.display = 'none';
            } else {
                tail.className = 'aa-tour__tail aa-tour__tail--' + tailDir;
                tail.style.display = '';
            }
        }
    });

    return '';
}
"""


# ---------------------------------------------------------------------------
# 3. Scroll-into-view (clientside JS)
# ---------------------------------------------------------------------------
_SCROLL_JS = """
function(state, meta) {
    if (!state || state.current_step === null || state.current_step === undefined || state.dismissed) {
        return '';
    }
    const tab = 'map';
    if (!meta || !meta[tab]) return '';
    const stepIdx = state.current_step;
    const scrolls = meta[tab].scroll_to || [];
    if (stepIdx < 0 || stepIdx >= scrolls.length) return '';
    const scrollTarget = scrolls[stepIdx];
    if (!scrollTarget) return '';

    const el = document.getElementById(scrollTarget);
    if (el && el.scrollIntoView) {
        try {
            el.scrollIntoView({behavior: 'smooth', block: 'center'});
        } catch (err) {
            el.scrollIntoView();
        }
    }
    return '';
}
"""


# ---------------------------------------------------------------------------
# 4. Auto-launch signal (clientside JS)
# ---------------------------------------------------------------------------
# Season Science is single-page. We poll for the ol-map div (mounted at
# boot) to make sure the popup opens over a mounted map, not over a
# blank flash. The `first_visit` guard ensures the tour only auto-opens
# on the user's first visit in the current session.
_AUTO_LAUNCH_MAP_JS = """
function(pathname, state) {
    if (!state || !state.first_visit) return window.dash_clientside.no_update;
    if (window.__aaTourAutoLaunchMap) return window.dash_clientside.no_update;
    window.__aaTourAutoLaunchMap = true;

    const started = Date.now();
    const maxWaitMs = 15000;
    const poll = setInterval(function () {
        const el = document.getElementById('ol-map');
        // Wait until the map div is not just present but also sized —
        // ol-map.js sets width/height when it initialises the map, so
        // this proxies "map is ready" without needing an OL-specific hook.
        if (el && el.offsetWidth > 0 && el.offsetHeight > 0) {
            clearInterval(poll);
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props(
                    'tour-auto-launch-map', {data: Date.now()}
                );
            }
        } else if (Date.now() - started > maxWaitMs) {
            clearInterval(poll);
        }
    }, 100);
    return window.dash_clientside.no_update;
}
"""


# ---------------------------------------------------------------------------
# 5. Keyboard listener (clientside JS)
# ---------------------------------------------------------------------------
_KEYBOARD_JS = """
function(pathname) {
    const tab = '__TAB__';
    const flagKey = '__aaTourKbd_' + tab;
    if (window[flagKey]) return '';
    window[flagKey] = true;

    function isSafeFocusTarget() {
        const ae = document.activeElement;
        if (!ae) return true;
        if (ae === document.body) return true;
        const tag = (ae.tagName || '').toLowerCase();
        if (tag === 'input' || tag === 'textarea' || tag === 'select') return false;
        if (ae.closest && ae.closest('.dash-dropdown')) return false;
        return true;
    }

    document.addEventListener('keydown', function (e) {
        const popup = document.getElementById('tour-popup-' + tab + '-root');
        if (!popup) return;
        const cls = popup.className || '';
        if (cls.indexOf('aa-tour--hidden') !== -1) return;
        if (!isSafeFocusTarget()) return;

        const key = e.key;
        if (key === 'Escape') {
            e.preventDefault();
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props(
                    'tour-esc-' + tab + '-signal', {data: Date.now()}
                );
            }
        } else if (key === 'ArrowRight') {
            e.preventDefault();
            const btn = document.getElementById('tour-next-' + tab);
            if (btn) btn.click();
        } else if (key === 'ArrowLeft') {
            e.preventDefault();
            const btn = document.getElementById('tour-back-' + tab);
            if (btn && !btn.disabled) btn.click();
        } else if (key === 'Enter' || key === ' ' || key === 'Spacebar') {
            const ae = document.activeElement;
            const insidePopup = popup.contains(ae);
            const onBody = ae === document.body;
            if (!insidePopup && !onBody) return;
            e.preventDefault();
            const btn = document.getElementById('tour-next-' + tab);
            if (btn) btn.click();
        }
    });
    return '';
}
"""


# ---------------------------------------------------------------------------
# tour-steps-meta payload builder
# ---------------------------------------------------------------------------
def build_tour_steps_meta():
    """Hydrate the `tour-steps-meta` Store from MAP_STEPS."""
    return {
        "map": {
            "targets": [s["target"] for s in MAP_STEPS],
            "positions": [s.get("position", "center") for s in MAP_STEPS],
            "offsets_x": [s.get("offset_x", 0) for s in MAP_STEPS],
            "offsets_y": [s.get("offset_y", 0) for s in MAP_STEPS],
            "widths": [s.get("width") for s in MAP_STEPS],
            "hero_stations": [s.get("hero_station") for s in MAP_STEPS],
            "pan_to": [s.get("pan_to") for s in MAP_STEPS],
            "scroll_to": [s.get("scroll_to") for s in MAP_STEPS],
        },
        "feature_stations": dict(FEATURE_STATIONS),
    }


TOUR_STEPS_META = build_tour_steps_meta()


# ---------------------------------------------------------------------------
# Public registrar
# ---------------------------------------------------------------------------
def register_tour_clientside(app):
    # 1. Content render.
    _register_content_render(app, "map", MAP_STEPS)

    # 2. Positioning.
    clientside_callback(
        _POSITIONING_JS.replace("__TAB__", "map"),
        Output("tour-pos-sink-map", "children"),
        Input("tour-state-map", "data"),
        State("tour-steps-meta", "data"),
        prevent_initial_call=True,
    )

    # 3. Scroll-into-view.
    clientside_callback(
        _SCROLL_JS,
        Output("tour-scroll-sink", "children"),
        Input("tour-state-map", "data"),
        State("tour-steps-meta", "data"),
        prevent_initial_call=True,
    )

    # 4. Auto-launch.
    clientside_callback(
        _AUTO_LAUNCH_MAP_JS,
        Output("tour-mount-sink-map", "children"),
        Input("url", "pathname"),
        State("tour-state-map", "data"),
    )

    # 5. Keyboard listener.
    clientside_callback(
        _KEYBOARD_JS.replace("__TAB__", "map"),
        Output("tour-kbd-sink-map", "children"),
        Input("url", "pathname"),
    )


__all__ = ["register_tour_clientside", "TOUR_STEPS_META", "build_tour_steps_meta"]
