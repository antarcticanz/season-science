from dash import Dash, html, dcc, Input, Output


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
                        dcc.Checklist(
                            id="layer-checklist",
                            options=[
                                {"label": "K872B – ApRES Sites", "value": "apres"}
                            ],
                            value=["apres"],  # default visible
                            className="layer-checklist",
                            inputClassName="layer-checklist__input",
                            labelClassName="layer-checklist__label",
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
    function(values) {
        const show = values && values.includes("apres");
        if (window.setLayerVisibility) {
            window.setLayerVisibility("apres", !!show);
        }
        return show ? "apres:on" : "apres:off";
    }
    """,
    Output("js-sink", "children"),
    Input("layer-checklist", "value"),
)


# -------------------------------------------------------------------
# Local development entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
