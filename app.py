import re
from dash import Dash, html, dcc, Input, Output, ALL, ctx, no_update

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
        "id": "arrival_heights",
        "group": "Arrival Heights",
        "file": "arrival_heights.geojson",
        "status": "Active",
        "value": "arrival_heights",
        "visible": False
    },
    {
        "id": "pyramid_trough",
        "group": "Pyramid Trough",
        "file": "PYRAMID_TROUGH.geojson",
        "status": "Planned",
        "value": "pyramid_trough",
        "visible": False
    },
    {
        "id": "scott_base",
        "group": "Scott Base",
        "file": "scott_base.geojson",
        "status": "Active",
        "value": "scott_base",
        "visible": False
    },
    {
        "id": "K020A--BUDDAH_LAKE",
        "group": "K020A - Virus Dispersal",
        "file": "K020A--BUDDAH_LAKE.geojson",
        "status": "Buddah Lake",
        "value": "K020A--BUDDAH_LAKE",
        "visible": True,
    },
    {
        "id": "K020A--MINNA_BLUFF",
        "group": "K020A - Virus Dispersal",
        "file": "K020A--MINNA_BLUFF.geojson",
        "status": "Minna Bluff",
        "value": "K020A--MINNA_BLUFF",
        "visible": True,
    },
    {
        "id": "K020A--PYRAMID_TROUGH",
        "group": "K020A - Virus Dispersal",
        "file": "K020A--PYRAMID_TROUGH.geojson",
        "status": "Pyramid Trough",
        "value": "K020A--PYRAMID_TROUGH",
        "visible": True,
    },
    {
        "id": "K022A",
        "group": "K022A - Mount Erebus",
        "file": "K022A.geojson",
        "status": "Planned",
        "value": "K022A",
        "visible": True,
    },
    {
        "id": "K026A--PYRAMID_TROUGH",
        "group": "K026A - Ecosystem Mapping",
        "file": "K026A--PYRAMID_TROUGH.geojson",
        "status": "Pyramid Trough",
        "value": "K026A--PYRAMID_TROUGH",
        "visible": True,
    },
    {
        "id": "K044A",
        "group": "K044A - Ice Cores",
        "file": "K044A.geojson",
        "status": "Planned",
        "value": "K044A",
        "visible": True,
    },
    {
        "id": "K053A",
        "group": "K053A - Pack-Ice Survey",
        "file": "K053A.geojson",
        "status": "Planned",
        "value": "K053A",
        "visible": True,
    },
    {
        "id": "K055A--SCOTT_BASE",
        "group": "K055A - Atmospheric Dynamics",
        "file": "K055A--SCOTT_BASE.geojson",
        "status": "Scott Base",
        "value": "K055A--SCOTT_BASE",
        "visible": True,
    },
    {
        "id": "K060A--SCOTT_BASE",
        "group": "K060A - VLF Sensors",
        "file": "K060A--SCOTT_BASE.geojson",
        "status": "Scott Base",
        "value": "K060A--SCOTT_BASE",
        "visible": True,
    },
    {
        "id": "K060A--ARRIVAL_HEIGHTS",
        "group": "K060A - VLF Sensors",
        "file": "K060A--ARRIVAL_HEIGHTS.geojson",
        "status": "Arrival Heights",
        "value": "K060A--ARRIVAL_HEIGHTS",
        "visible": True,
    },
    {
        "id": "K082A--BLOOD_FALLS",
        "group": "K082A - Seafloor Seeps",
        "file": "K082A--BLOOD_FALLS.geojson",
        "status": "Blood Falls",
        "value": "K082A--BLOOD_FALLS",
        "visible": True,
    },
    {
        "id": "K082A--CAPE_EVANS",
        "group": "K082A - Seafloor Seeps",
        "file": "K082A--CAPE_EVANS.geojson",
        "status": "Cape Evans",
        "value": "K082A--CAPE_EVANS",
        "visible": True,
    },
    {
        "id": "K082A--GRANITE_HARBOUR",
        "group": "K082A - Seafloor Seeps",
        "file": "K082A--GRANITE_HARBOUR.geojson",
        "status": "Granite Harbour",
        "value": "K082A--GRANITE_HARBOUR",
        "visible": True,
    },
    {
        "id": "K082A--LAKE_FRYXELL",
        "group": "K082A - Seafloor Seeps",
        "file": "K082A--LAKE_FRYXELL.geojson",
        "status": "Lake Fryxell",
        "value": "K082A--LAKE_FRYXELL",
        "visible": True,
    },
    {
        "id": "K082A--MCMURDO_SOUND",
        "group": "K082A - Seafloor Seeps",
        "file": "K082A--MCMURDO_SOUND.geojson",
        "status": "McMurdo Sound",
        "value": "K082A--MCMURDO_SOUND",
        "visible": True,
    },
    {
        "id": "K082A--NEW_HARBOUR",
        "group": "K082A - Seafloor Seeps",
        "file": "K082A--NEW_HARBOUR.geojson",
        "status": "New Harbour",
        "value": "K082A--NEW_HARBOUR",
        "visible": True,
    },
    {
        "id": "K085A--SCOTT_BASE",
        "group": "K085A - Atmospheric Composition",
        "file": "K085A--SCOTT_BASE.geojson",
        "status": "Scott Base",
        "value": "K085A--SCOTT_BASE",
        "visible": True,
    },
    {
        "id": "K085A--ARRIVAL_HEIGHTS",
        "group": "K085A - Atmospheric Composition",
        "file": "K085A--ARRIVAL_HEIGHTS.geojson",
        "status": "Arrival Heights",
        "value": "K085A--ARRIVAL_HEIGHTS",
        "visible": True,
    },
    {
        "id": "K089A--SCOTT_BASE",
        "group": "K089A - AWS",
        "file": "K089A--SCOTT_BASE.geojson",
        "status": "Scott Base",
        "value": "K089A--SCOTT_BASE",
        "visible": True,
    },
    {
        "id": "K089A--ARRIVAL_HEIGHTS",
        "group": "K089A - AWS",
        "file": "K089A--ARRIVAL_HEIGHTS.geojson",
        "status": "Arrival Heights",
        "value": "K089A--ARRIVAL_HEIGHTS",
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
        "id": "K150A",
        "group": "K150A - GNSS & Tide Gauge",
        "file": "K150A.geojson",
        "status": "Active",
        "value": "K150A",
        "visible": True,
    },
    {
        "id": "K150B",
        "group": "K150B - SouthPAN",
        "file": "K150B.geojson",
        "status": "Planned",
        "value": "K150B",
        "visible": True,
    },
    {
        "id": "K170A",
        "group": "K170A - AHT",
        "file": "K170A.geojson",
        "status": "Active",
        "value": "K170A",
        "visible": True,
    },
    {
        "id": "K850A",
        "group": "K850A - Penguin Census",
        "file": "K850A.geojson",
        "status": "Planned",
        "value": "K850A",
        "visible": True,
    },
    {
        "id": "K862A--KIS2",
        "group": "K862A - ApRES & GNSS",
        "file": "K862A--KIS2.geojson",
        "status": "Kamb Ice Stream Site 2",
        "value": "K862A--KIS2",
        "visible": True,
    },
    {
        "id": "K862A--KIS3",
        "group": "K862A - ApRES & GNSS",
        "file": "K862A--KIS3.geojson",
        "status": "Kamb Ice Stream Site 3",
        "value": "K862A--KIS3",
        "visible": True,
    },
    {
        "id": "K862A--CIR",
        "group": "K862A - ApRES & GNSS",
        "file": "K862A--CIR.geojson",
        "status": "Crary Ice Rise",
        "value": "K862A--CIR",
        "visible": True,
    },
    {
        "id": "K865A--ACTIVE",
        "group": "K865A - GNSS",
        "file": "K865A--ACTIVE.geojson",
        "status": "Active",
        "value": "K865A--ACTIVE",
        "visible": True,
    },
    {
        "id": "K865A--PLANNED",
        "group": "K865A - GNSS",
        "file": "K865A--PLANNED.geojson",
        "status": "Planned",
        "value": "K865A--PLANNED",
        "visible": True,
    },
    {
        "id": "K872B--ACTIVE",
        "group": "K872B - ApRES",
        "file": "K872B--ACTIVE.geojson",
        "status": "Active",
        "value": "K872B--ACTIVE",
        "visible": True,
    },
    {
        "id": "K872B--PLANNED",
        "group": "K872B - ApRES",
        "file": "K872B--PLANNED.geojson",
        "status": "Planned",
        "value": "K872B--PLANNED",
        "visible": True,
    },
    {
        "id": "K881B--ACTIVE",
        "group": "K881B - AWS",
        "file": "K881B--ACTIVE.geojson",
        "status": "Active",
        "value": "K881B--ACTIVE",
        "visible": True,
    },
    {
        "id": "K881B--PLANNED",
        "group": "K881B - AWS",
        "file": "K881B--PLANNED.geojson",
        "status": "Planned",
        "value": "K881B--PLANNED",
        "visible": True,
    },
    {
        "id": "K891A--ACTIVE",
        "group": "K891A - Sea Ice",
        "file": "K891A--ACTIVE.geojson",
        "status": "Active",
        "value": "K891A--ACTIVE",
        "visible": True,
    },
    {
        "id": "K891A--PLANNED",
        "group": "K891A - Sea Ice",
        "file": "K891A--PLANNED.geojson",
        "status": "Planned",
        "value": "K891A--PLANNED",
        "visible": True,
    },
    {
        "id": "K893A--COMMONWEALTH_GLACIER",
        "group": "K893A - Super Site",
        "file": "K893A--COMMONWEALTH_GLACIER.geojson",
        "status": "Commonwealth Glacier",
        "value": "K893A--COMMONWEALTH_GLACIER",
        "visible": True,
    },
    {
        "id": "K893A--LOWER_WRIGHT_GLACIER",
        "group": "K893A - Super Site",
        "file": "K893A--LOWER_WRIGHT_GLACIER.geojson",
        "status": "Lower Wright Glacier",
        "value": "K893A--LOWER_WRIGHT_GLACIER",
        "visible": True,
    },
    {
        "id": "K893A--PYRAMID_TROUGH",
        "group": "K893A - Super Site",
        "file": "K893A--PYRAMID_TROUGH.geojson",
        "status": "Pyramid Trough",
        "value": "K893A--PYRAMID_TROUGH",
        "visible": True,
    },
    {
        "id": "K894A",
        "group": "K894A - Terrestrial Survey",
        "file": "K894A.geojson",
        "status": "Planned",
        "value": "K894A",
        "visible": True,
    },
    {
        "id": "asp_planned",
        "group": "Tangaroa - ASP Moorings",
        "file": "ASP_MOORINGS-PLANNED_2027.geojson",
        "status": "Planned",
        "value": "asp_planned",
        "visible": True,
    },
]

# -------------------------------------------------------------------
# CAMP SITE REGISTRY
#
# One entry per season GeoJSON file. The checklist label is the season
# string (e.g. "2024-25") and each entry maps to a single layer id.
# -------------------------------------------------------------------
CAMP_REGISTRY = [
    {
        "id": "CAMPSITES-2324",
        "file": "CAMPSITES-2324.geojson",
        "season": "2023-24",
        "value": "CAMPSITES-2324",
        "visible": False,
    },
    {
        "id": "CAMPSITES-2425",
        "file": "CAMPSITES-2425.geojson",
        "season": "2024-25",
        "value": "CAMPSITES-2425",
        "visible": False,
    },
    {
        "id": "CAMPSITES-2526",
        "file": "CAMPSITES-2526.geojson",
        "season": "2025-26",
        "value": "CAMPSITES-2526",
        "visible": False,
    },
]

CAMP_DEFAULT_VISIBILITY = {e["id"]: e["visible"] for e in CAMP_REGISTRY}

# -------------------------------------------------------------------
# INSTRUMENTS REGISTRY
#
# Cross-cutting views that aggregate features from science event files.
# -------------------------------------------------------------------
INSTRUMENTS_REGISTRY = [
    {
        "id": "instruments_active",
        "file": "INSTALLATIONS_ACTIVE.geojson",
        "label": "Active",
        "value": "instruments_active",
        "visible": False,
    },
    {
        "id": "instruments_decommissioned",
        "file": "INSTALLATIONS_DEACTIVATED.geojson",
        "label": "Planned Removal",
        "value": "instruments_decommissioned",
        "visible": False,
    },
]

INSTRUMENTS_DEFAULT_VISIBILITY = {e["id"]: e["visible"] for e in INSTRUMENTS_REGISTRY}

# -------------------------------------------------------------------
# Derived structures (computed once at startup)
# -------------------------------------------------------------------

def _get_groups(registry):
    """Group entries by 'group', preserving insertion order."""
    groups = {}
    for entry in registry:
        groups.setdefault(entry["group"], []).append(entry)
    return groups

_RAW_GROUPS = _get_groups(LAYER_REGISTRY)

# IDs that belong in the "Locations" section rather than "Science Events"
_LOCATION_IDS = {"scott_base", "arrival_heights", "pyramid_trough"}

SCIENCE_GROUPS  = {g: e for g, e in _RAW_GROUPS.items()
                   if not any(x["id"] in _LOCATION_IDS for x in e)}
LOCATION_GROUPS = {g: e for g, e in _RAW_GROUPS.items()
                   if any(x["id"] in _LOCATION_IDS for x in e)}
# Combined dict used by all callbacks — science first, locations second
ALL_GROUPS = {**SCIENCE_GROUPS, **LOCATION_GROUPS}

# Pre-compute the correct default visibility map (fixes issue 1)
DEFAULT_VISIBILITY = {
    **{e["id"]: e["visible"] for e in LAYER_REGISTRY},
    **CAMP_DEFAULT_VISIBILITY,
    **INSTRUMENTS_DEFAULT_VISIBILITY,
}


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
def _build_group_divs(groups):
    group_divs = []

    for group_name, entries in groups.items():
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
                value=[group_name] if any(e["visible"] for e in entries) else [],
                className="layer-checklist",
                inputClassName="layer-checklist__input",
                labelClassName="layer-checklist__label",
            ),
            # Nested wrap — only rendered when group has multiple statuses
            html.Div(
                children_checklist,
                id=_wrap_id(group_name),
                className="nested-wrap",
                # Collapsed on startup; toggle_nested expands on first interaction
                style={"display": "none"},
            ),
        ]))

    return group_divs


def build_sidebar():
    return _build_group_divs(SCIENCE_GROUPS)


def build_location_sidebar():
    return _build_group_divs(LOCATION_GROUPS)


def build_camp_sidebar():
    """Build the Camp Sites checklist — one checkbox per season."""
    default_values = [e["value"] for e in CAMP_REGISTRY if e["visible"]]
    return dcc.Checklist(
        id="camp-checklist",
        options=[{"label": e["season"], "value": e["value"]} for e in CAMP_REGISTRY],
        value=default_values,
        className="layer-checklist",
        inputClassName="layer-checklist__input",
        labelClassName="layer-checklist__label",
    )


def build_instruments_sidebar():
    """Build the Instruments checklist — Active and Planned Removal."""
    default_values = [e["value"] for e in INSTRUMENTS_REGISTRY if e["visible"]]
    return dcc.Checklist(
        id="instruments-checklist",
        options=[{"label": e["label"], "value": e["value"]} for e in INSTRUMENTS_REGISTRY],
        value=default_values,
        className="layer-checklist",
        inputClassName="layer-checklist__input",
        labelClassName="layer-checklist__label",
    )


app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.H1(
                    "Antarctica NZ Supported Activities & Instruments - 2026-27",
                    className="title-pane__title",
                ),
                html.Img(
                    src="/assets/ANZ_Logo_Horizontal_Badge_White_RGB.png",
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

                        # Science Events: Select all / Deselect all
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

                        html.Div("Locations", className="sidebar__heading sidebar__heading--section"),

                        html.Hr(className="sidebar__hr"),

                        *build_location_sidebar(),

                        html.Hr(className="sidebar__hr"),

                        html.Div("Instruments", className="sidebar__heading sidebar__heading--section"),

                        html.Hr(className="sidebar__hr"),

                        build_instruments_sidebar(),

                        html.Hr(className="sidebar__hr"),

                        html.Div("Camp Sites", className="sidebar__heading sidebar__heading--section"),

                        html.Hr(className="sidebar__hr"),

                        build_camp_sidebar(),

                        html.Hr(className="sidebar__hr sidebar__hr--export"),

                        # Export GeoJSON button
                        html.Div(
                            html.Button(
                                "↓ Export visible layers as GeoJSON",
                                id="btn-export-geojson",
                                className="sidebar__export-btn",
                            ),
                            className="sidebar__export-wrap",
                        ),
                        # Hidden anchor used by the clientside callback to trigger download
                        html.A(id="export-download-link", style={"display": "none"}),
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
all_parent_inputs    = [Input(_parent_id(g),   "value") for g in ALL_GROUPS]
all_children_inputs  = [Input(_children_id(g), "value") for g in ALL_GROUPS]
all_parent_outputs   = [Output(_parent_id(g),   "value") for g in ALL_GROUPS]
all_children_outputs = [Output(_children_id(g), "value") for g in ALL_GROUPS]

science_parent_outputs   = [Output(_parent_id(g),   "value") for g in SCIENCE_GROUPS]
science_children_outputs = [Output(_children_id(g), "value") for g in SCIENCE_GROUPS]


# -------------------------------------------------------------------
# Science Events: Select all / Deselect all
# Only controls science layer parents + children
# -------------------------------------------------------------------
@app.callback(
    science_parent_outputs + science_children_outputs,
    Input("btn-select-all",   "n_clicks"),
    Input("btn-deselect-all", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_select(n_select, n_deselect):
    selecting = ctx.triggered_id == "btn-select-all"
    science_parent_vals = [[g] if selecting else [] for g in SCIENCE_GROUPS]
    science_children_vals = [
        [e["value"] for e in entries] if selecting else []
        for entries in SCIENCE_GROUPS.values()
    ]
    return science_parent_vals + science_children_vals





# -------------------------------------------------------------------
# Compute {layer_id: bool} visibility map → Store
# -------------------------------------------------------------------
@app.callback(
    Output("layer-visibility-store", "data"),
    all_parent_inputs + all_children_inputs + [
        Input("camp-checklist", "value"),
        Input("instruments-checklist", "value"),
    ],
)
def compute_visibility(*args):
    n = len(ALL_GROUPS)
    parent_values      = args[:n]
    children_values    = args[n:2*n]
    camp_values        = args[2*n] or []
    instruments_values = args[2*n + 1] or []

    visibility = {}
    for i, (group_name, entries) in enumerate(ALL_GROUPS.items()):
        parent_on       = bool(parent_values[i] and group_name in parent_values[i])
        active_children = children_values[i] or []

        for entry in entries:
            if len(entries) == 1:
                visibility[entry["id"]] = parent_on
            else:
                if not parent_on:
                    visibility[entry["id"]] = False
                elif not active_children:
                    visibility[entry["id"]] = True
                else:
                    visibility[entry["id"]] = entry["value"] in active_children

    for entry in CAMP_REGISTRY:
        visibility[entry["id"]] = entry["value"] in camp_values

    for entry in INSTRUMENTS_REGISTRY:
        visibility[entry["id"]] = entry["value"] in instruments_values

    # When an aggregate layer is on, suppress its event sub-layers to avoid
    # duplicate features rendering at the same point.
    if visibility.get("pyramid_trough"):
        for layer_id in (
            "K020A--PYRAMID_TROUGH",
            "K026A--PYRAMID_TROUGH",
            "K893A--PYRAMID_TROUGH",
        ):
            visibility[layer_id] = False

    if visibility.get("scott_base"):
        for layer_id in (
            "K055A--SCOTT_BASE",
            "K060A--SCOTT_BASE",
            "K085A--SCOTT_BASE",
            "K089A--SCOTT_BASE",
        ):
            visibility[layer_id] = False

    if visibility.get("arrival_heights"):
        for layer_id in (
            "K060A--ARRIVAL_HEIGHTS",
            "K085A--ARRIVAL_HEIGHTS",
            "K089A--ARRIVAL_HEIGHTS",
        ):
            visibility[layer_id] = False

    return visibility


# -------------------------------------------------------------------
# Show/hide nested wrap when parent is toggled (only for multi-entry groups)
# -------------------------------------------------------------------
@app.callback(
    [o for g, entries in ALL_GROUPS.items() for o in (
        Output(_children_id(g), "disabled"),
        Output(_wrap_id(g), "style"),
    )],
    all_parent_inputs,
    prevent_initial_call=True,
)
def toggle_nested(*parent_values):
    result = []
    for i, (group_name, entries) in enumerate(ALL_GROUPS.items()):
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
# Export GeoJSON — clientside, fetches visible layer files in-browser
# and triggers a blob download with all visible features merged.
# -------------------------------------------------------------------

# Build the JS-side registry of all layer files so the clientside
# callback knows which file to fetch for each layer id.
_ALL_LAYER_FILES = {
    e["id"]: e["file"]
    for e in LAYER_REGISTRY + CAMP_REGISTRY + INSTRUMENTS_REGISTRY
    if "file" in e
}

app.clientside_callback(
    f"""
    function(n_clicks, visibilityData) {{
        if (!n_clicks || !visibilityData) return window.dash_clientside.no_update;

        const fileMap = {_ALL_LAYER_FILES};

        const visibleIds = Object.entries(visibilityData)
            .filter(([id, vis]) => vis && fileMap[id])
            .map(([id]) => id);

        if (visibleIds.length === 0) {{
            alert("No visible layers to export.");
            return window.dash_clientside.no_update;
        }}

        Promise.all(
            visibleIds.map(id =>
                fetch("/assets/" + fileMap[id])
                    .then(r => r.ok ? r.json() : null)
                    .catch(() => null)
            )
        ).then(results => {{
            const features = [];
            results.forEach(fc => {{
                if (fc && fc.features) features.push(...fc.features);
            }});
            const merged = {{
                type: "FeatureCollection",
                features: features
            }};
            const blob = new Blob(
                [JSON.stringify(merged, null, 2)],
                {{type: "application/geo+json"}}
            );
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "antarcticanz_activity_locations.geojson";
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {{ URL.revokeObjectURL(url); a.remove(); }}, 1000);
        }});

        return window.dash_clientside.no_update;
    }}
    """,
    Output("export-download-link", "href"),
    Input("btn-export-geojson", "n_clicks"),
    Input("layer-visibility-store", "data"),
    prevent_initial_call=True,
)


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
