from dash import no_update
from dash import Dash, html, dcc, Input, Output, State


# -------------------------------------------------------------------
# Dash application setup
# -------------------------------------------------------------------
app = Dash(__name__)

# ✅ REQUIRED for gunicorn / PRAX deployment
server = app.server


# 3. Health Check Endpoint
# -----------------------
# Simple endpoint for container/orchestrator monitoring.

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

        # Body: sidebar + map
        html.Div(
            [
                # Sidebar

                html.Div(
                    [
                        html.Div("Science Events",
                                 className="sidebar__heading"),

                        # Parent toggle (layer visibility)
                        dcc.Checklist(
                            id="layer-checklist",
                            options=[
                                {"label": "K872B – ApRES Sites", "value": "apres"}],
                            value=["apres"],  # default visible
                            className="layer-checklist",
                            inputClassName="layer-checklist__input",
                            labelClassName="layer-checklist__label",
                        ),

                        # Nested categories (shown/usable only when parent is selected)
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="apres-status",
                                    options=[
                                        {"label": "Active", "value": "active"},
                                        {"label": "Wishlist", "value": "wishlist"},
                                    ],
                                    value=["active"],  # choose your default(s)
                                    className="layer-checklist layer-checklist--nested",
                                    inputClassName="layer-checklist__input",
                                    labelClassName="layer-checklist__label",
                                )
                            ],
                            id="apres-status-wrap",
                            className="nested-wrap",
                        ),

                        html.Hr(className="sidebar__hr"),
                    ],
                    className="sidebar",
                ),


                # Map container
                html.Div(
                    html.Div(id="ol-map", className="map"),
                    className="map-frame",
                ),
            ],
            className="body-row",
        ),

        # Hidden sink to avoid circular Output=Input
        html.Div(id="js-sink", style={"display": "none"}),
    ],
    className="app-root",
)


# -------------------------------------------------------------------
# Client-side callback for OpenLayers layer visibility
# -------------------------------------------------------------------
app.clientside_callback(
    """
    function(parentValues, statusValues) {
        const parentOn = parentValues && parentValues.includes("apres");
        const statuses = statusValues || [];

        const showActive = parentOn && statuses.includes("active");
        const showWishlist = parentOn && statuses.includes("wishlist");

        if (window.setLayerVisibility) {
            window.setLayerVisibility("k872b_active", !!showActive);
            window.setLayerVisibility("k872b_wishlist", !!showWishlist);
        }

        return "k872b:" + (showActive ? "active" : "") + "|" + (showWishlist ? "wishlist" : "");
    }
    """,
    Output("js-sink", "children"),
    Input("layer-checklist", "value"),
    Input("apres-status", "value"),
)


@app.callback(
    Output("apres-status", "disabled"),
    Output("apres-status-wrap", "style"),
    Output("apres-status", "value"),
    Input("layer-checklist", "value"),
    State("apres-status", "value"),
)
def toggle_nested(values, current_status):
    show = values and "apres" in values

    if show:
        # enable + show; keep current selections
        return False, {"display": "block"}, current_status

    # disable + hide; also clear selections (or keep them if you prefer)
    return True, {"display": "none"}, []

# -------------------------------------------------------------------
# Local development entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
