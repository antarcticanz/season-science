import re
from dash import Dash, html, dcc, Input, Output, ALL, ctx

# -------------------------------------------------------------------
# LAYER REGISTRY
#
# Single source of truth for all map layers. Adding a new layer here
# automatically adds it to the sidebar — no other Python changes needed.
#
# Fields:
#   id      – unique per file; must match the id in ol-map.js
#   group   – sidebar parent label (e.g. event number + name)
#   status  – sidebar child label (e.g. "Active", "Wishlist", "Planned")
#   value   – checklist value string (must be unique across the registry)
#   visible – whether the layer is on by default
# -------------------------------------------------------------------
LAYER_REGISTRY = [
    {
        "id": "scott_base",
        "group": "Scott Base",
        "status": "Active",
        "value": "scott_base",
        "visible": True
    },
    {
        "id": "arrival_heights",
        "group": "Arrival Heights",
        "status": "Active",
        "value": "arrival_heights",
        "visible": True
    },
    {
        "id": "asp_planned",
        "group": "ASP Moorings",
        "file": "asp_moorings_planned_2027.geojson",
        "status": "Planned",
        "value": "asp_planned",
        "visible": True,
    },
    {
        "id": "K082A",
        "group": "K082A - Benthic Landers",
        "file": "K082A.geojson",
        "status": "Active",
        "value": "K082A",
        "visible": True,
    },
    {
        "id": "K872B",
        "group": "K872B - ApRES",
        "file": "K872B.geojson",
        "status": "Active",
        "value": "K872B_active",
        "visible": True,
    },
    {
        "id": "K872B_wishlist",
        "group": "K872B - ApRES",
        "file": "K872B_wishlist.geojson",
        "status": "Wishlist",
        "value": "K872B_wishlist",
        "visible": False,
    },
    {
        "id": "K881B",
        "group": "K881B - AWS",
        "file": "K881B.geojson",
        "status": "Active",
        "value": "K881B",
        "visible": True,
    },
    {
        "id": "K150A",
        "group": "K150A - GNSS & Tide Gauge",
        "file": "K150A.geojson",
        "status": "Active",
        "value": "K150A",
        "visible": True,
    },
    {
        "id": "K102A",
        "group": "K102A - Geomagnetic",
        "file": "K102A.geojson",
        "status": "Active",
        "value": "K102A",
        "visible": True,
    },
    {
        "id": "K862A_KIS2",
        "group": "K862A - ApRES & GNSS",
        "file": "K862A_KIS2.geojson",
        "status": "Kamb Ice Stream Site 2",
        "value": "K862A_KIS2",
        "visible": True,
    }
    ,
    {
        "id": "K862A_KIS3",
        "group": "K862A - ApRES & GNSS",
        "file": "K862A_KIS3.geojson",
        "status": "Kamb Ice Stream Site 3",
        "value": "K862A_KIS3",
        "visible": True,
    },
    {
        "id": "K862A_CIR",
        "group": "K862A - ApRES & GNSS",
        "file": "K862A_CIR.geojson",
        "status": "Crary Ice Rise",
        "value": "K862A_CIR",
        "visible": True,
    },
    {
        "id": "K865A",
        "group": "K865A - GNSS",
        "file": "K865A.geojson",
        "status": "Active",
        "value": "K865A",
        "visible": True,
    },
    {
        "id": "K891A",
        "group": "K891A - Sea Ice",
        "file": "K891A.geojson",
        "status": "Active",
        "value": "K891A",
        "visible": True,
    }
]

# -------------------------------------------------------------------
# Derived structures (computed once at startup)
# -------------------------------------------------------------------

def _get_groups(registry):
    """Group entries by 'group', preserving insertion order."""
    groups = {}
    for entry in registry:
        groups.setdefault(entry["group"], []).append(entry)
    return groups

GROUPS = _get_groups(LAYER_REGISTRY)

# Pre-compute the correct default visibility map (fixes issue 1)
DEFAULT_VISIBILITY = {e["id"]: e["visible"] for e in LAYER_REGISTRY}


def _slug(group_name):
    """Safe HTML id slug from a group name."""
    return re.sub(r'[^a-z0-9]+', '-', group_name.lower()).strip('-')

def _parent_id(group_name):   return f"parent-{_slug(group_name)}"
def _children_id(group_name): return f"children-{_slug(group_name)}"
def _wrap_id(group_name):     return f"wrap-{_slug(group_name)}"


# -------------------------------------------------------------------
# Dash application setup
# -------------------------------------------------------------------
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Antarctica New Zealand"

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <link rel="icon" type="image/png" href="/assets/favicon.png"/>
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

server = app.server


@server.route("/health", methods=["GET"])
def health():
    return "OK", 200, {"Content-Type": "text/plain"}


# -------------------------------------------------------------------
# Sidebar builder — driven entirely by LAYER_REGISTRY
# -------------------------------------------------------------------
def build_sidebar():
    group_divs = []

    for group_name, entries in GROUPS.items():
        default_children = [e["value"] for e in entries if e["visible"]]
        multi = len(entries) > 1  # only show nested children when >1 entry in group

        children_checklist = dcc.Checklist(
            id=_children_id(group_name),
            options=[{"label": e["status"], "value": e["value"]} for e in entries],
            value=default_children,
            className="layer-checklist layer-checklist--nested",
            inputClassName="layer-checklist__input",
            labelClassName="layer-checklist__label",
        )

        group_divs.append(html.Div([
            # Parent checkbox — always shown
            dcc.Checklist(
                id=_parent_id(group_name),
                options=[{"label": group_name, "value": group_name}],
                value=[group_name],
                className="layer-checklist",
                inputClassName="layer-checklist__input",
                labelClassName="layer-checklist__label",
            ),
            # Nested wrap — only rendered when group has multiple statuses
            html.Div(
                children_checklist,
                id=_wrap_id(group_name),
                className="nested-wrap",
                # Hidden entirely for single-entry groups
                style={"display": "block"} if multi else {"display": "none"},
            ),
        ]))

    return group_divs


# -------------------------------------------------------------------
# Application layout
# -------------------------------------------------------------------
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1(
                    "Antarctica NZ Supported Instruments & Activities 2026-27",
                    className="title-pane__title",
                ),
                html.Img(
                    src="/assets/ANZ_Logo_Horrizontal_CMYK.png",
                    className="title-pane__logo",
                ),
            ],
            className="title-pane",
        ),

        # Body
        html.Div(
            [
                # Sidebar — fully dynamic from LAYER_REGISTRY
                html.Div(
                    [
                        html.Div("Science Events", className="sidebar__heading"),

                        # Select all / Deselect all buttons
                        html.Div(
                            [
                                html.Button(
                                    "Select all",
                                    id="btn-select-all",
                                    className="sidebar__bulk-btn",
                                ),
                                html.Button(
                                    "Deselect all",
                                    id="btn-deselect-all",
                                    className="sidebar__bulk-btn",
                                ),
                            ],
                            className="sidebar__bulk-actions",
                        ),

                        html.Hr(className="sidebar__hr"),

                        *build_sidebar(),

                        html.Hr(className="sidebar__hr"),
                    ],
                    className="sidebar",
                ),

                # Map
                html.Div(
                    html.Div(id="ol-map", className="map"),
                    className="map-frame",
                ),
            ],
            className="body-row",
        ),

        html.Div(id="js-sink", style={"display": "none"}),

        # Initialised with DEFAULT_VISIBILITY so the map is correct on first load
        # before any user interaction fires a callback (fixes issue 1)
        dcc.Store(id="layer-visibility-store", data=DEFAULT_VISIBILITY),
    ],
    className="app-root",
)


# -------------------------------------------------------------------
# Callback inputs — derived from registry, never written by hand
# -------------------------------------------------------------------
all_parent_inputs    = [Input(_parent_id(g),   "value") for g in GROUPS]
all_children_inputs  = [Input(_children_id(g), "value") for g in GROUPS]
all_parent_outputs   = [Output(_parent_id(g),   "value") for g in GROUPS]
all_children_outputs = [Output(_children_id(g), "value") for g in GROUPS]


# -------------------------------------------------------------------
# Select all / Deselect all (issue 3)
# Sets every parent and every children checklist in one callback
# -------------------------------------------------------------------
@app.callback(
    all_parent_outputs + all_children_outputs,
    Input("btn-select-all",   "n_clicks"),
    Input("btn-deselect-all", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_select(n_select, n_deselect):
    selecting = ctx.triggered_id == "btn-select-all"

    parent_vals   = [[g] if selecting else [] for g in GROUPS]
    children_vals = [
        [e["value"] for e in entries] if selecting else []
        for entries in GROUPS.values()
    ]
    return parent_vals + children_vals


# -------------------------------------------------------------------
# Compute {layer_id: bool} visibility map → Store
# -------------------------------------------------------------------
@app.callback(
    Output("layer-visibility-store", "data"),
    all_parent_inputs + all_children_inputs,
)
def compute_visibility(*args):
    n = len(GROUPS)
    parent_values   = args[:n]
    children_values = args[n:]

    visibility = {}
    for i, (group_name, entries) in enumerate(GROUPS.items()):
        parent_on       = bool(parent_values[i] and group_name in parent_values[i])
        active_children = children_values[i] or []

        for entry in entries:
            if len(entries) == 1:
                # Single-entry group: no child checkbox visible, parent drives it directly
                visibility[entry["id"]] = parent_on
            else:
                visibility[entry["id"]] = parent_on and entry["value"] in active_children

    return visibility


# -------------------------------------------------------------------
# Show/hide nested wrap when parent is toggled (only for multi-entry groups)
# -------------------------------------------------------------------
@app.callback(
    [o for g, entries in GROUPS.items() for o in (
        Output(_children_id(g), "disabled"),
        Output(_wrap_id(g), "style"),
    )],
    all_parent_inputs,
)
def toggle_nested(*parent_values):
    result = []
    for i, (group_name, entries) in enumerate(GROUPS.items()):
        parent_on = bool(parent_values[i] and group_name in parent_values[i])
        multi = len(entries) > 1
        result.append(not parent_on)
        # Only ever show the wrap for multi-entry groups
        result.append(
            {"display": "block"} if (multi and parent_on) else {"display": "none"}
        )
    return result


# -------------------------------------------------------------------
# Clientside: push visibility state to OL map
# -------------------------------------------------------------------
app.clientside_callback(
    """
    function(visibilityData) {
        if (!visibilityData) return "no-data";

        function applyVisibility() {
            if (!window.setLayerVisibility || !window.__ol_map__) {
                // OL map not ready yet — retry in 100ms
                setTimeout(applyVisibility, 100);
                return;
            }
            Object.entries(visibilityData).forEach(function([layerId, visible]) {
                window.setLayerVisibility(layerId, visible);
            });
        }

        applyVisibility();
        return "layers-updated";
    }
    """,
    Output("js-sink", "children"),
    Input("layer-visibility-store", "data"),
)


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
