import re
import json
import os
from collections import OrderedDict
from flask import jsonify
from dash import Dash, html, dcc, Input, Output, State, ALL, ctx, no_update

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
        "file": "ARRIVAL_HEIGHTS.geojson",
        "status": "Active",
        "value": "arrival_heights",
        "visible": False
    },
    {
        "id": "CRARY_ICE_RISE",
        "group": "Crary Ice Rise",
        "file": "CRARY_ICE_RISE.geojson",
        "status": "Active",
        "value": "CRARY_ICE_RISE",
        "visible": False
    },
    {
        "id": "KAMB_ICE_STREAM",
        "group": "Kamb Ice Stream",
        "file": "KAMB_ICE_STREAM.geojson",
        "status": "Active",
        "value": "KAMB_ICE_STREAM",
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
        "file": "SCOTT_BASE.geojson",
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
        "id": "K022A--PLANNED",
        "group": "K022A - Mount Erebus",
        "file": "K022A--PLANNED.geojson",
        "status": "Planned",
        "value": "K022A--PLANNED",
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
        "id": "K026A--LAKE_FRYXELL",
        "group": "K026A - Ecosystem Mapping",
        "file": "K026A--LAKE_FRYXELL.geojson",
        "status": "Lake Fryxell",
        "value": "K026A--LAKE_FRYXELL",
        "visible": True,
    },
    {
        "id": "K044A--PLANNED",
        "group": "K044A - Ice Cores",
        "file": "K044A--PLANNED.geojson",
        "status": "Planned",
        "value": "K044A--PLANNED",
        "visible": True,
    },
    {
        "id": "K053A--PLANNED",
        "group": "K053A - Pack-Ice Survey",
        "file": "K053A--PLANNED.geojson",
        "status": "Planned",
        "value": "K053A--PLANNED",
        "visible": True,
    },
    {
        "id": "K055A--PLANNED",
        "group": "K055A - Atmospheric Dynamics",
        "file": "K055A--PLANNED.geojson",
        "status": "Planned",
        "value": "K055A--PLANNED",
        "visible": True,
    },
    {
        "id": "K060A--PLANNED",
        "group": "K060A - VLF Sensors",
        "file": "K060A--PLANNED.geojson",
        "status": "Planned",
        "value": "K060A--PLANNED",
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
        "id": "K085A--PLANNED",
        "group": "K085A - Atmospheric Composition",
        "file": "K085A--PLANNED.geojson",
        "status": "Planned",
        "value": "K085A--PLANNED",
        "visible": True,
    },
    {
        "id": "K089A--PLANNED",
        "group": "K089A - AWS",
        "file": "K089A--PLANNED.geojson",
        "status": "Planned",
        "value": "K089A--PLANNED",
        "visible": True,
    },
    {
        "id": "K102A--PLANNED",
        "group": "K102A - Geomagnetic",
        "file": "K102A--PLANNED.geojson",
        "status": "Planned",
        "value": "K102A--PLANNED",
        "visible": True,
    },
    {
        "id": "K150A--PLANNED",
        "group": "K150A - GNSS & Tide Gauge",
        "file": "K150A--PLANNED.geojson",
        "status": "Planned",
        "value": "K150A--PLANNED",
        "visible": True,
    },
    {
        "id": "K150B--PLANNED",
        "group": "K150B - SouthPAN",
        "file": "K150B--PLANNED.geojson",
        "status": "Planned",
        "value": "K150B--PLANNED",
        "visible": True,
    },
    {
        "id": "K170A--PLANNED",
        "group": "K170A - AHT",
        "file": "K170A--PLANNED.geojson",
        "status": "Planned",
        "value": "K170A--PLANNED",
        "visible": True,
    },
    {
        "id": "K500A--PLANNED",
        "group": "K500A - PAMS",
        "file": "K500A--PLANNED.geojson",
        "status": "Planned",
        "value": "K500A--PLANNED",
        "visible": True,
    },
    {
        "id": "K850A--PLANNED",
        "group": "K850A - Penguin Census",
        "file": "K850A--PLANNED.geojson",
        "status": "Planned",
        "value": "K850A--PLANNED",
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
        "id": "K872B--PLANNED",
        "group": "K872B - ApRES",
        "file": "K872B--PLANNED.geojson",
        "status": "Planned",
        "value": "K872B--PLANNED",
        "visible": True,
    },
    {
        "id": "K881B--PLANNED",
        "group": "K881B - AWS",
        "file": "K881B--PLANNED.geojson",
        "status": "Planned Removal",
        "value": "K881B--PLANNED",
        "visible": True,
    },
    {
        "id": "K882B--PLANNED",
        "group": "K882B - Hauwai",
        "file": "K882B--PLANNED.geojson",
        "status": "Planned",
        "value": "K882B--PLANNED",
        "visible": True,
    },
    {
        "id": "K884A--PLANNED",
        "group": "K884A - Sponges",
        "file": "K884A--PLANNED.geojson",
        "status": "Planned",
        "value": "K884A--PLANNED",
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
        "id": "K894A--PLANNED",
        "group": "K894A - Terrestrial Survey",
        "file": "K894A--PLANNED.geojson",
        "status": "Planned",
        "value": "K894A--PLANNED",
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

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def _load_geojson(filename):
    try:
        with open(os.path.join(_ASSETS_DIR, filename), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"type": "FeatureCollection", "features": []}

_EVENT_CODE_MAP = {}
for _entry in LAYER_REGISTRY:
    _grp = _entry.get("group", "")
    if " - " in _grp:
        _code, _name = _grp.split(" - ", 1)
        _code = _code.strip()
        if _code not in _EVENT_CODE_MAP:
            _EVENT_CODE_MAP[_code] = _name.strip()
# Events not derivable from LAYER_REGISTRY group names
_EVENT_CODE_MAP.setdefault("K862A", "GNSS & ApRES")
_EVENT_CODE_MAP.setdefault("K500A", "PAMS")

_ACTIVE_FC = _load_geojson("INSTALLATIONS_ACTIVE.geojson")
_ACTIVE_FEATURES = _ACTIVE_FC.get("features", [])

_ACTIVE_BY_EVENT = OrderedDict()
for _f in _ACTIVE_FEATURES:
    _code = _f.get("properties", {}).get("event") or ""
    _ACTIVE_BY_EVENT.setdefault(_code, []).append(_f)

_OFFLINE_FEATURES = []
_OFFLINE_EVENTS = OrderedDict()
for _entry in LAYER_REGISTRY:
    if _entry["id"] in {"scott_base", "arrival_heights", "pyramid_trough"}:
        continue
    _data = _load_geojson(_entry["file"])
    for _f in _data.get("features", []):
        if (_f.get("properties", {}).get("status") or "").lower() == "offline":
            _code = _f.get("properties", {}).get("event") or ""
            _OFFLINE_EVENTS.setdefault(_code, []).append(_f)
            _OFFLINE_FEATURES.append(_f)

def _has_planned(filename):
    data = _load_geojson(filename)
    return any(
        (f.get("properties", {}).get("status") or "").lower() == "planned"
        for f in data.get("features", [])
    )

_PLANNED_IDS = {
    e["id"] for e in LAYER_REGISTRY
    if e["id"] not in {"scott_base", "arrival_heights", "pyramid_trough"}
    and _has_planned(e["file"])
}

CAMP_DEFAULT_VISIBILITY = {e["id"]: e["visible"] for e in CAMP_REGISTRY}


def _get_groups(registry):
    groups = {}
    for entry in registry:
        groups.setdefault(entry["group"], []).append(entry)
    return groups


_RAW_GROUPS = _get_groups(LAYER_REGISTRY)
_LOCATION_IDS = {"scott_base", "arrival_heights", "pyramid_trough", "KAMB_ICE_STREAM", "CRARY_ICE_RISE"}

_PLANNED_SCIENCE_GROUPS = {}
for _g, _entries in _RAW_GROUPS.items():
    if any(x["id"] in _LOCATION_IDS for x in _entries):
        continue
    _planned_entries = [e for e in _entries if e["id"] in _PLANNED_IDS]
    if _planned_entries:
        _PLANNED_SCIENCE_GROUPS[_g] = _planned_entries

SCIENCE_GROUPS = _PLANNED_SCIENCE_GROUPS
LOCATION_GROUPS = {g: e for g, e in _RAW_GROUPS.items()
                   if any(x["id"] in _LOCATION_IDS for x in e)}
ALL_GROUPS = {**SCIENCE_GROUPS, **LOCATION_GROUPS}


def _active_label(code):
    if not code:
        return "Unassigned"
    name = _EVENT_CODE_MAP.get(code)
    return f"{code} - {name}" if name else code

_ACTIVE_INSTR_ENTRIES = [
    {
        "id": f"active__{code or 'unassigned'}",
        "group": "Active",
        "status": _active_label(code),
        "value": f"active__{code or 'unassigned'}",
        "visible": False,
    }
    for code in sorted(_ACTIVE_BY_EVENT.keys())
]

_OFFLINE_INSTR_ENTRIES = [
    {
        "id": f"offline__{code or 'unassigned'}",
        "group": "Offline",
        "status": _active_label(code),
        "value": f"offline__{code or 'unassigned'}",
        "visible": False,
    }
    for code in sorted(_OFFLINE_EVENTS.keys())
]

INSTR_GROUPS = OrderedDict()
if _ACTIVE_INSTR_ENTRIES:
    INSTR_GROUPS["Active"] = _ACTIVE_INSTR_ENTRIES
if _OFFLINE_INSTR_ENTRIES:
    INSTR_GROUPS["Offline"] = _OFFLINE_INSTR_ENTRIES
INSTR_GROUPS["Planned Removal"] = [
    {
        "id": "instruments_decommissioned",
        "group": "Planned Removal",
        "status": "Planned Removal",
        "value": "instruments_decommissioned",
        "visible": False,
    }
]

_ALL_SIDEBAR_GROUPS = {**ALL_GROUPS, **INSTR_GROUPS}

DEFAULT_VISIBILITY = {
    **{e["id"]: e["visible"] for e in LAYER_REGISTRY},
    **CAMP_DEFAULT_VISIBILITY,
    "instruments_active": False,
    "instruments_offline": False,
    "instruments_decommissioned": False,
    "__active_events__": [],
}


def _slug(group_name):
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


@server.route("/assets/computed/offline.geojson")
def computed_offline():
    return jsonify({"type": "FeatureCollection", "features": _OFFLINE_FEATURES})


# -------------------------------------------------------------------
# Sidebar builder — driven entirely by LAYER_REGISTRY
# -------------------------------------------------------------------
def _build_group_divs(groups, group_extras=None):
    group_extras = group_extras or {}
    group_divs = []

    for group_name, entries in groups.items():
        default_children = [e["value"] for e in entries if e["visible"]]
        multi = len(entries) > 1

        children_checklist = dcc.Checklist(
            id=_children_id(group_name),
            options=[{"label": e["status"], "value": e["value"]} for e in entries],
            value=default_children,
            className="layer-checklist layer-checklist--nested",
            inputClassName="layer-checklist__input",
            labelClassName="layer-checklist__label",
        )

        wrap_children = [children_checklist] + (group_extras.get(group_name) or [])

        group_divs.append(html.Div([
            dcc.Checklist(
                id=_parent_id(group_name),
                options=[{"label": group_name, "value": group_name}],
                value=[group_name] if any(e["visible"] for e in entries) else [],
                className="layer-checklist",
                inputClassName="layer-checklist__input",
                labelClassName="layer-checklist__label",
            ),
            html.Div(
                wrap_children,
                id=_wrap_id(group_name),
                className="nested-wrap",
                style={"display": "none"},
            ),
        ]))

    return group_divs


def build_sidebar():
    return _build_group_divs(SCIENCE_GROUPS, group_extras={
        "K082A - Seafloor Seeps": [
            html.Div(
                html.Button(
                    "Clear filter",
                    id="btn-k082a-clear",
                    className="sidebar__bulk-btn sidebar__bulk-btn--sm",
                ),
                className="sidebar__nested-actions",
            )
        ]
    })


def build_location_sidebar():
    return _build_group_divs(LOCATION_GROUPS)


def build_camp_sidebar():
    default_values = [e["value"] for e in CAMP_REGISTRY if e["visible"]]
    return dcc.Checklist(
        id="camp-checklist",
        options=[{"label": e["season"], "value": e["value"]} for e in CAMP_REGISTRY],
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
                html.Img(
                    src="/assets/ANZ_Logo_Horizontal_Badge_White_RGB.png",
                    className="title-pane__logo",
                ),
                html.Button(
                    [
                        html.Span("ⓘ", className="title-pane__info-icon"),
                        "About",
                    ],
                    id="btn-info",
                    className="title-pane__info-btn",
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
                        html.Div("Planned Science Events 2026-27", className="sidebar__heading"),

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

                        html.Div([
                            html.Div("Locations", className="sidebar__heading sidebar__heading--section"),
                            html.Div([
                                html.Button("All",  id="btn-loc-select-all",   className="sidebar__bulk-btn sidebar__bulk-btn--sm"),
                                html.Button("None", id="btn-loc-deselect-all", className="sidebar__bulk-btn sidebar__bulk-btn--sm"),
                            ], className="sidebar__bulk-actions sidebar__bulk-actions--compact"),
                        ], className="sidebar__section-header"),

                        html.Hr(className="sidebar__hr"),

                        *build_location_sidebar(),

                        html.Hr(className="sidebar__hr"),

                        html.Div([
                            html.Div("Instruments", className="sidebar__heading sidebar__heading--section"),
                            html.Div([
                                html.Button("All",  id="btn-instr-select-all",   className="sidebar__bulk-btn sidebar__bulk-btn--sm"),
                                html.Button("None", id="btn-instr-deselect-all", className="sidebar__bulk-btn sidebar__bulk-btn--sm"),
                            ], className="sidebar__bulk-actions sidebar__bulk-actions--compact"),
                        ], className="sidebar__section-header"),

                        html.Hr(className="sidebar__hr"),

                        *_build_group_divs(INSTR_GROUPS, group_extras={
                            "Active": [
                                html.Div(
                                    html.Button(
                                        "Clear filter",
                                        id="btn-active-clear",
                                        className="sidebar__bulk-btn sidebar__bulk-btn--sm",
                                    ),
                                    className="sidebar__nested-actions",
                                )
                            ]
                        }),

                        html.Hr(className="sidebar__hr"),

                        html.Div([
                            html.Div("Camp Sites", className="sidebar__heading sidebar__heading--section"),
                            html.Div([
                                html.Button("All",  id="btn-camp-select-all",   className="sidebar__bulk-btn sidebar__bulk-btn--sm"),
                                html.Button("None", id="btn-camp-deselect-all", className="sidebar__bulk-btn sidebar__bulk-btn--sm"),
                            ], className="sidebar__bulk-actions sidebar__bulk-actions--compact"),
                        ], className="sidebar__section-header"),

                        html.Hr(className="sidebar__hr"),

                        build_camp_sidebar(),

                        html.Hr(className="sidebar__hr sidebar__hr--export"),

                        html.Div(
                            html.Button(
                                "↓ Export visible layers as GeoJSON",
                                id="btn-export-geojson",
                                className="sidebar__export-btn",
                            ),
                            className="sidebar__export-wrap",
                        ),
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

        html.Div(
            html.Div(
                [
                    html.Button("✕", id="btn-info-close", className="info-modal__close"),
                    html.H2("About this map", className="info-modal__title"),
                    html.Div([
                        html.P(
                            "This interactive map shows Antarctica New Zealand supported science "
                            "activities and instruments for the 2026–27 season.",
                            className="info-modal__para",
                        ),
                        html.P(
                            "Use the sidebar to explore planned science events by location and site, "
                            "view active and offline instruments grouped by event, and browse "
                            "historical field camp sites.",
                            className="info-modal__para",
                        ),
                        html.P(
                            "Click any point on the map to view its details. Use the layer switcher "
                            "(top-right) to toggle between satellite basemaps, or the ruler tool to measure distances.",
                            className="info-modal__para",
                        ),
                    ], className="info-modal__body"),
                ],
                className="info-modal__inner",
            ),
            id="info-modal",
            className="info-modal",
            style={"display": "none"},
        ),

        html.Div(id="js-sink", style={"display": "none"}),

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

instr_parent_inputs    = [Input(_parent_id(g),   "value") for g in INSTR_GROUPS]
instr_children_inputs  = [Input(_children_id(g), "value") for g in INSTR_GROUPS]


# -------------------------------------------------------------------
# Science Events: Select all / Deselect all
# Only controls science layer parents + children
# -------------------------------------------------------------------
@app.callback(
    science_parent_outputs,
    Input("btn-select-all",   "n_clicks"),
    Input("btn-deselect-all", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_select(n_select, n_deselect):
    selecting = ctx.triggered_id == "btn-select-all"
    return [[g] if selecting else [] for g in SCIENCE_GROUPS]


location_parent_outputs = [Output(_parent_id(g), "value") for g in LOCATION_GROUPS]

instr_parent_outputs_bulk   = [Output(_parent_id(g),   "value")                      for g in INSTR_GROUPS]
instr_children_outputs_bulk = [Output(_children_id(g), "value", allow_duplicate=True) for g in INSTR_GROUPS]


@app.callback(
    location_parent_outputs,
    Input("btn-loc-select-all",   "n_clicks"),
    Input("btn-loc-deselect-all", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_select_location(n_sel, n_desel):
    selecting = ctx.triggered_id == "btn-loc-select-all"
    return [[g] if selecting else [] for g in LOCATION_GROUPS]


@app.callback(
    instr_parent_outputs_bulk + instr_children_outputs_bulk,
    Input("btn-instr-select-all",   "n_clicks"),
    Input("btn-instr-deselect-all", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_select_instruments(n_sel, n_desel):
    selecting = ctx.triggered_id == "btn-instr-select-all"
    parent_vals = [[g] if selecting else [] for g in INSTR_GROUPS]
    children_vals = [
        [e["value"] for e in entries] if selecting else []
        for entries in INSTR_GROUPS.values()
    ]
    return parent_vals + children_vals


@app.callback(
    Output("camp-checklist", "value"),
    Input("btn-camp-select-all",   "n_clicks"),
    Input("btn-camp-deselect-all", "n_clicks"),
    prevent_initial_call=True,
)
def bulk_select_camp(n_sel, n_desel):
    if ctx.triggered_id == "btn-camp-select-all":
        return [e["value"] for e in CAMP_REGISTRY]
    return []


@app.callback(
    Output(_children_id("Active"), "value", allow_duplicate=True),
    Input("btn-active-clear", "n_clicks"),
    prevent_initial_call=True,
)
def clear_active_children(_):
    return []


@app.callback(
    Output(_children_id("K082A - Seafloor Seeps"), "value", allow_duplicate=True),
    Input("btn-k082a-clear", "n_clicks"),
    prevent_initial_call=True,
)
def clear_k082a_children(_):
    return []


# -------------------------------------------------------------------
# Compute {layer_id: bool} visibility map → Store
# -------------------------------------------------------------------
@app.callback(
    Output("layer-visibility-store", "data"),
    all_parent_inputs + all_children_inputs +
    instr_parent_inputs + instr_children_inputs + [
        Input("camp-checklist", "value"),
    ],
)
def compute_visibility(*args):
    n = len(ALL_GROUPS)
    m = len(INSTR_GROUPS)
    parent_values   = args[:n]
    children_values = args[n:2*n]
    instr_parents   = args[2*n:2*n+m]
    instr_children  = args[2*n+m:2*n+2*m]
    camp_values     = args[2*n+2*m] or []

    visibility = {}

    for i, (group_name, entries) in enumerate(ALL_GROUPS.items()):
        parent_on      = bool(parent_values[i] and group_name in parent_values[i])
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

    for i, (group_name, entries) in enumerate(INSTR_GROUPS.items()):
        parent_on      = bool(instr_parents[i] and group_name in instr_parents[i])
        active_children = instr_children[i] or []

        if group_name == "Active":
            visibility["instruments_active"] = parent_on
            if parent_on and active_children:
                visibility["__active_events__"] = [
                    v.replace("active__", "", 1) for v in active_children
                ]
            else:
                visibility["__active_events__"] = []
        elif group_name == "Offline":
            visibility["instruments_offline"] = parent_on
        else:
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

    return visibility


# -------------------------------------------------------------------
# Show/hide nested wrap when parent is toggled
# -------------------------------------------------------------------
@app.callback(
    [o for g, entries in _ALL_SIDEBAR_GROUPS.items() for o in (
        Output(_children_id(g), "disabled"),
        Output(_children_id(g), "value", allow_duplicate=True),
        Output(_wrap_id(g), "style"),
    )],
    [Input(_parent_id(g), "value") for g in _ALL_SIDEBAR_GROUPS],
    [State(_children_id(g), "value") for g in _ALL_SIDEBAR_GROUPS],
    prevent_initial_call=True,
)
def toggle_nested(*args):
    n = len(_ALL_SIDEBAR_GROUPS)
    parent_values    = args[:n]
    current_children = args[n:2*n]
    result = []
    is_bulk = len(ctx.triggered or []) > 1
    for i, (group_name, entries) in enumerate(_ALL_SIDEBAR_GROUPS.items()):
        parent_on = bool(parent_values[i] and group_name in parent_values[i])
        multi = len(entries) > 1
        cur = current_children[i] or []
        result.append(not parent_on)
        if not is_bulk and parent_on and not cur and multi:
            result.append([e["value"] for e in entries])
        else:
            result.append(no_update)
        if is_bulk and parent_on:
            result.append(no_update)
        elif multi and parent_on:
            result.append({"display": "block"})
        else:
            result.append({"display": "none"})
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
# -------------------------------------------------------------------
_ALL_LAYER_FILES = {
    e["id"]: e["file"]
    for e in LAYER_REGISTRY + CAMP_REGISTRY
    if "file" in e
}
_ALL_LAYER_FILES["instruments_active"] = "INSTALLATIONS_ACTIVE.geojson"
_ALL_LAYER_FILES["instruments_offline"] = "computed/offline.geojson"
_ALL_LAYER_FILES["instruments_decommissioned"] = "INSTALLATIONS_DEACTIVATED.geojson"

app.clientside_callback(
    f"""
    function(n_clicks, visibilityData) {{
        if (!n_clicks || !visibilityData) return window.dash_clientside.no_update;

        const fileMap = {json.dumps(_ALL_LAYER_FILES)};

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
# Info modal open/close
# -------------------------------------------------------------------
app.clientside_callback(
    """
    function(openClicks, closeClicks) {
        const triggered = (window.dash_clientside.callback_context.triggered || [])[0];
        if (!triggered) return window.dash_clientside.no_update;
        if (triggered.prop_id === "btn-info.n_clicks") return {"display": "flex"};
        return {"display": "none"};
    }
    """,
    Output("info-modal", "style"),
    Input("btn-info", "n_clicks"),
    Input("btn-info-close", "n_clicks"),
    prevent_initial_call=True,
)


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
