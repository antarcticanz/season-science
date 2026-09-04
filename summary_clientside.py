"""
Research-summary popover — clientside layer.

Three clientside callbacks:
  1. Icon click → summary-popover-state (pattern-matching Input).
  2. State change → popover DOM (className / position / body innerHTML) and
     active-icon highlight. Positioning adapted from tour_clientside._POSITIONING_JS
     — anchored right of the icon, flips left if it would clip, clamps to viewport.
  3. Document-level listeners (Esc / click-outside / sidebar-scroll) → close.
"""

from dash import Input, Output, State, ALL, clientside_callback


# ---------------------------------------------------------------------------
# 1. Icon click → state store
# ---------------------------------------------------------------------------
_CLICK_JS = """
function(n_clicks_list, current_state, ids) {
    if (!Array.isArray(n_clicks_list) || n_clicks_list.length === 0) {
        return window.dash_clientside.no_update;
    }
    const ctx = window.dash_clientside.callback_context;
    if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
        return window.dash_clientside.no_update;
    }
    const trg = ctx.triggered[0];
    if (trg.value == null) return window.dash_clientside.no_update;

    // triggered.prop_id looks like: {"code":"K020A","type":"summary-info-btn"}.n_clicks
    let triggeredCode = null;
    try {
        const idStr = trg.prop_id.split('.').slice(0, -1).join('.');
        const idObj = JSON.parse(idStr);
        triggeredCode = idObj.code;
    } catch (e) {
        return window.dash_clientside.no_update;
    }
    if (!triggeredCode) return window.dash_clientside.no_update;

    const state = current_state || {open: false, code: null};
    // Same icon clicked again → close.
    if (state.open && state.code === triggeredCode) {
        return {open: false, code: null, ts: Date.now()};
    }
    return {open: true, code: triggeredCode, ts: Date.now()};
}
"""


# ---------------------------------------------------------------------------
# 2. State → popover render + position
# ---------------------------------------------------------------------------
_RENDER_JS = """
function(state, summaries) {
    const popup = document.getElementById('summary-popover-root');
    const titleEl = document.getElementById('summary-popover-title');
    const bodyEl = document.getElementById('summary-popover-body');
    const tail = document.getElementById('summary-popover-tail');
    if (!popup || !titleEl || !bodyEl) return '';

    // Clear any previously-active icon highlight.
    document.querySelectorAll('.sidebar__info-btn.is-active')
        .forEach(function (el) { el.classList.remove('is-active'); });

    const isOpen = state && state.open && state.code;
    if (!isOpen) {
        popup.className = 'aa-summary aa-summary--hidden';
        popup.style.visibility = 'hidden';
        return '';
    }

    const code = state.code;
    const entry = (summaries || {})[code];
    if (!entry) {
        popup.className = 'aa-summary aa-summary--hidden';
        return '';
    }

    titleEl.textContent = entry.title || code;
    bodyEl.innerHTML = entry.html || '';

    // Locate the anchor icon.
    const selector = '[data-summary-code="' + code + '"]';
    const iconEl = document.querySelector(selector);
    if (!iconEl) {
        popup.className = 'aa-summary aa-summary--hidden';
        return '';
    }
    iconEl.classList.add('is-active');

    popup.className = 'aa-summary';
    popup.style.position = 'fixed';
    popup.style.visibility = 'hidden';  // measure first, show after

    requestAnimationFrame(function () {
        const iconRect = iconEl.getBoundingClientRect();
        const popupRect = popup.getBoundingClientRect();
        const popupW = popupRect.width || 360;
        const popupH = popupRect.height || 200;
        const vw = window.innerWidth;
        const vh = window.innerHeight;
        const gap = 10;

        // Prefer right of icon; flip left if clipped.
        let left = iconRect.right + gap;
        let tailDir = 'left';
        if (left + popupW > vw - 8) {
            left = iconRect.left - popupW - gap;
            tailDir = 'right';
        }

        // Vertically: align popup so tail lines up with icon centre.
        // Tail is 20px from top of popup by default.
        const iconCenterY = iconRect.top + iconRect.height / 2;
        let top = iconCenterY - 20;
        top = Math.max(8, Math.min(top, vh - popupH - 8));

        popup.style.top = top + 'px';
        popup.style.left = left + 'px';
        popup.style.visibility = 'visible';

        if (tail) {
            tail.className = 'aa-summary__tail aa-summary__tail--' + tailDir;
            // Nudge tail to line up with icon centre.
            const tailTop = Math.max(8, Math.min(iconCenterY - top - 6, popupH - 20));
            tail.style.top = tailTop + 'px';
        }
    });

    return '';
}
"""


# ---------------------------------------------------------------------------
# 3. Document-level listeners (Esc / click-outside / scroll)
# ---------------------------------------------------------------------------
_DOC_LISTENERS_JS = """
function(pathname) {
    if (window.__aaSummaryDocWired) return '';
    window.__aaSummaryDocWired = true;

    function close() {
        if (window.dash_clientside && window.dash_clientside.set_props) {
            window.dash_clientside.set_props(
                'summary-popover-state', {data: {open: false, code: null, ts: Date.now()}}
            );
        }
    }

    // Esc
    document.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape') return;
        const popup = document.getElementById('summary-popover-root');
        if (!popup) return;
        const cls = popup.className || '';
        if (cls.indexOf('aa-summary--hidden') !== -1) return;
        // Don't hijack Esc if the tour is also open — let its handler run first.
        const tour = document.getElementById('tour-popup-map-root');
        if (tour && (tour.className || '').indexOf('aa-tour--hidden') === -1) return;
        e.preventDefault();
        close();
    });

    // Click outside
    document.addEventListener('mousedown', function (e) {
        const popup = document.getElementById('summary-popover-root');
        if (!popup) return;
        const cls = popup.className || '';
        if (cls.indexOf('aa-summary--hidden') !== -1) return;
        const t = e.target;
        if (popup.contains(t)) return;
        // Click on any info button (including the currently-open one) is
        // handled by the pattern-matching click callback — don't double-fire.
        if (t.closest && t.closest('.sidebar__info-btn')) return;
        close();
    });

    // Close button
    const closeBtn = document.getElementById('summary-popover-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function () { close(); });
    }

    // Sidebar scroll (simpler than repositioning).
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.addEventListener('scroll', function () {
            const popup = document.getElementById('summary-popover-root');
            if (!popup) return;
            const cls = popup.className || '';
            if (cls.indexOf('aa-summary--hidden') === -1) close();
        }, {passive: true});
    }

    return '';
}
"""


# ---------------------------------------------------------------------------
# Registrar
# ---------------------------------------------------------------------------
def register_summary_clientside(app):
    # 1. Icon click → state.
    clientside_callback(
        _CLICK_JS,
        Output("summary-popover-state", "data"),
        Input({"type": "summary-info-btn", "code": ALL}, "n_clicks"),
        State("summary-popover-state", "data"),
        State({"type": "summary-info-btn", "code": ALL}, "id"),
        prevent_initial_call=True,
    )

    # 2. State → render + position.
    clientside_callback(
        _RENDER_JS,
        Output("summary-render-sink", "children"),
        Input("summary-popover-state", "data"),
        State("summary-data-store", "data"),
        prevent_initial_call=False,
    )

    # 3. Document-level listeners.
    clientside_callback(
        _DOC_LISTENERS_JS,
        Output("summary-doc-sink", "children"),
        Input("url", "pathname"),
    )


__all__ = ["register_summary_clientside"]
