from dash import Dash, html, dcc, Input, Output, State

# -------------------------------------------------------------------
# Dash application setup
# -------------------------------------------------------------------
app = Dash(__name__)
app.title = "Antarctica New Zealand"

# Add favicon manually
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
# Application layout
# -------------------------------------------------------------------
app.layout = html.Div(
    [
        # Header
        html.Div(
            [
                html.Img(
                    src="/assets/ANZ_Logo_Horrizontal_CMYK.png",
                    className="title-pane__logo",
                ),
                html.H1(
                    "Science Activities 26/27 Season",
                    className="title-pane__title",
                ),
            ],
            className="title-pane",
        ),

        # Body
        html.Div(
            [
                # Sidebar
                html.Div(
                    [
                        html.Div("Science Events",
                                 className="sidebar__heading"),

                        # -----------------------------
                        # ApRES Group
                        # -----------------------------
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="apres-parent",
                                    options=[
                                        {"label": "K872B – ApRES Sites", "value": "apres"}],
                                    value=["apres"],
                                    className="layer-checklist",
                                    inputClassName="layer-checklist__input",
                                    labelClassName="layer-checklist__label",
                                ),
                                html.Div(
                                    [
                                        dcc.Checklist(
                                            id="apres-status",
                                            options=[
                                                {"label": "Active",
                                                    "value": "active"},
                                                {"label": "Wishlist",
                                                    "value": "wishlist"},
                                            ],
                                            value=["active"],
                                            className="layer-checklist layer-checklist--nested",
                                            inputClassName="layer-checklist__input",
                                            labelClassName="layer-checklist__label",
                                        )
                                    ],
                                    id="apres-status-wrap",
                                    className="nested-wrap",
                                ),
                            ]
                        ),

                        # -----------------------------
                        # ASP Group
                        # -----------------------------
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="asp-parent",
                                    options=[
                                        {"label": "ASP Moorings", "value": "asp"}],
                                    value=["asp"],
                                    className="layer-checklist",
                                    inputClassName="layer-checklist__input",
                                    labelClassName="layer-checklist__label",
                                ),
                                html.Div(
                                    [
                                        dcc.Checklist(
                                            id="asp-status",
                                            options=[
                                                {"label": "Planned 2027", "value": "planned"}],
                                            value=["planned"],
                                            className="layer-checklist layer-checklist--nested",
                                            inputClassName="layer-checklist__input",
                                            labelClassName="layer-checklist__label",
                                        )
                                    ],
                                    id="asp-status-wrap",
                                    className="nested-wrap",
                                ),
                            ]
                        ),

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
    ],
    className="app-root",
)

# -------------------------------------------------------------------
# Client-side callback: layer visibility + popups
# -------------------------------------------------------------------
app.clientside_callback(
    """
    function(apresParent, aspParent, apresStatusValues, aspStatusValues) {
        // ----------------------------
        // Layer visibility logic
        // ----------------------------
        const parentOnApres = apresParent && apresParent.includes("apres");
        const parentOnAsp = aspParent && aspParent.includes("asp");

        const apresStatuses = apresStatusValues || [];
        const aspStatuses = aspStatusValues || [];

        const showActive = parentOnApres && apresStatuses.includes("active");
        const showWishlist = parentOnApres && apresStatuses.includes("wishlist");
        const showAspPlanned = parentOnAsp && aspStatuses.includes("planned");

        if (window.setLayerVisibility) {
            window.setLayerVisibility("k872b_active", !!showActive);
            window.setLayerVisibility("k872b_wishlist", !!showWishlist);
            window.setLayerVisibility("asp_planned", !!showAspPlanned);
        }

        // ----------------------------
        // Popups: include Description for ASP Planned
        // ----------------------------
        if (window.olMap && window.popupOverlay && !window.olMap._popupListenerAdded) {
            window.olMap.on('singleclick', function(evt) {
                const feature = window.olMap.forEachFeatureAtPixel(evt.pixel, f => f);
                const popup = document.getElementById('ol-popup-content');

                if (feature && popup) {
                    let content = '';
                    const layerName = feature.get('layer_name');

                    if(layerName === 'asp_planned') {
                        content = '<div><strong>' + feature.get('name') + '</strong></div>' +
                                  '<div><strong>Status:</strong> Planned</div>' +
                                  '<div><strong>Description:</strong> ' + feature.get('description') + '</div>';
                    } else if(layerName.startsWith('k872b')) {
                        const status = layerName.includes('active') ? 'Active' : 'Wishlist';
                        content = '<div><strong>' + feature.get('name') + '</strong></div>' +
                                  '<div><strong>Status:</strong> ' + status + '</div>';
                    } else {
                        content = '<div><strong>' + feature.get('name') + '</strong></div>';
                    }

                    popup.innerHTML = content;
                    window.popupOverlay.setPosition(evt.coordinate);

                } else if (popup) {
                    window.popupOverlay.setPosition(undefined);
                    popup.innerHTML = '';
                }
            });

            // Flag to prevent multiple listeners
            window.olMap._popupListenerAdded = true;
        }

        return "layers-updated";
    }
    """,
    Output("js-sink", "children"),
    Input("apres-parent", "value"),
    Input("asp-parent", "value"),
    Input("apres-status", "value"),
    Input("asp-status", "value"),
)

# -------------------------------------------------------------------
# Toggle nested visibility
# -------------------------------------------------------------------


@app.callback(
    Output("apres-status", "disabled"),
    Output("apres-status-wrap", "style"),
    Output("asp-status", "disabled"),
    Output("asp-status-wrap", "style"),
    Input("apres-parent", "value"),
    Input("asp-parent", "value"),
)
def toggle_nested(apres_values, asp_values):
    show_apres = apres_values and "apres" in apres_values
    show_asp = asp_values and "asp" in asp_values
    return (
        not show_apres,
        {"display": "block"} if show_apres else {"display": "none"},
        not show_asp,
        {"display": "block"} if show_asp else {"display": "none"},
    )


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
