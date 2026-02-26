from dash import Dash, html, dcc, Input, Output

app = Dash(__name__)

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
                        html.Div("Science Events", className="sidebar__heading"),
                        dcc.Checklist(
                            id="layer-checklist",
                            options=[
                                {"label": "K872B – ApRES Sites", "value": "apres"}],
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
                html.Div(html.Div(id="ol-map", className="map"),
                         className="map-frame"),
            ],
            className="body-row",
        ),

        # Hidden sink to avoid circular Output=Input
        html.Div(id="js-sink", style={"display": "none"}),
    ],
    className="app-root",
)

# ✅ Client-side callback uses Output/Input from dash (NOT dcc)
#    Output goes to hidden 'js-sink' to avoid circular dependency.
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

if __name__ == "__main__":
    # If you keep seeing multiple "Dash is running..." lines, set debug=False or use_reloader=False
    app.run(debug=True)  # or: app.run(debug=True, use_reloader=False)
