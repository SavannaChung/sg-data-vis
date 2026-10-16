import pandas as pd
import plotly.graph_objects as go

from dash import dcc, html

# =============
# Dash helpers
# =============

def make_options(values):
    """
    Convert values into Dash dropdown options.
    """
    clean_values = []

    for value in values:
        if pd.isna(value):
            continue

        if hasattr(value, "item"):
            value = value.item()

        clean_values.append(value)

    return [{"label": str(v), "value": v} for v in clean_values]


def blank_figure(message):
    """
    Return an empty Plotly figure with a central message.
    """
    fig = go.Figure()

    fig.update_layout(
        template="plotly_white",
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 18},
            }
        ],
        height=700,
    )

    return fig


# ================
# Dash app layout
# ================

APP_STYLE_OPEN = {
    "display": "grid",
    "gridTemplateColumns": "280px minmax(0, 1fr)",
    "minHeight": "100vh",
    "fontFamily": "Arial, sans-serif",
    "overflowX": "hidden",
}

APP_STYLE_COLLAPSED = {
    "display": "grid",
    "gridTemplateColumns": "54px minmax(0, 1fr)",
    "minHeight": "100vh",
    "fontFamily": "Arial, sans-serif",
    "overflowX": "hidden",
}

SIDEBAR_STYLE_OPEN = {
    "width": "100%",
    "boxSizing": "border-box",
    "padding": "16px",
    "backgroundColor": "#111824",
    "color": "#edf3fb",
    "height": "100vh",
    "overflowY": "auto",
    "overflowX": "hidden",
    "borderRight": "1px solid #26354b",
}

SIDEBAR_STYLE_COLLAPSED = {
    "width": "100%",
    "boxSizing": "border-box",
    "padding": "10px 6px",
    "backgroundColor": "#111824",
    "color": "#edf3fb",
    "height": "100vh",
    "overflowY": "hidden",
    "overflowX": "hidden",
    "borderRight": "1px solid #26354b",
}

MAIN_STYLE = {
    "padding": "22px",
    "backgroundColor": "#f7f9fc",
    "minHeight": "100vh",
    "minWidth": "0",
    "overflowX": "hidden",
}

LABEL_STYLE = {
    "fontWeight": "600",
    "fontSize": "12px",
    "marginTop": "13px",
    "marginBottom": "6px",
    "display": "block",
}

DROPDOWN_STYLE = {
    "width": "100%",
    "minWidth": "0",
    "fontSize": "12px",
    "color": "#111",
}

INPUT_STYLE = {
    "width": "100%",
    "boxSizing": "border-box",
    "padding": "8px",
    "borderRadius": "8px",
    "border": "1px solid #34465f",
    "fontSize": "12px",
}

PLOT_CARD_STYLE = {
    "backgroundColor": "white",
    "border": "1px solid #d8dee9",
    "borderRadius": "12px",
    "padding": "14px",
    "overflow": "hidden",
    "minWidth": "0",
    "width": "100%",
    "maxWidth": "1450px",
    "boxSizing": "border-box",
}

def app_layout(df, gty_op, xrv_op, mev_op, ga_op, fwhm_op):
    return html.Div(
        id="app-shell",
        style=APP_STYLE_OPEN,
        children=[
            html.Aside(
                id="sidebar",
                style=SIDEBAR_STYLE_OPEN,
                children=[
                    html.Button(
                        "◀",
                        id="toggle-sidebar",
                        n_clicks=0,
                        title="Hide/show filters",
                        style={
                            "width": "34px",
                            "height": "34px",
                            "border": "1px solid #34465f",
                            "borderRadius": "9px",
                            "backgroundColor": "#0d131d",
                            "color": "#edf3fb",
                            "cursor": "pointer",
                            "fontSize": "15px",
                            "marginBottom": "12px",
                        },
                    ),

                    html.Div(
                        id="sidebar-content",
                        children=[
                            html.H2(
                                "Spot Position QA",
                                style={
                                    "marginTop": "0",
                                    "marginBottom": "4px",
                                    "fontSize": "20px",
                                },
                            ),
                            html.Div(
                                "MVP dashboard",
                                style={
                                    "color": "#9dadc2",
                                    "fontSize": "13px",
                                },
                            ),

                            html.Hr(
                                style={
                                    "borderColor": "#26354b",
                                    "margin": "18px 0",
                                }
                            ),

                            html.Div(
                                "Filters",
                                style={
                                    "fontSize": "12px",
                                    "textTransform": "uppercase",
                                    "color": "#9dadc2",
                                    "fontWeight": "700",
                                    "letterSpacing": "0.08em",
                                },
                            ),

                            html.Label("Gantry", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="gantry-dropdown",
                                options=gty_op,
                                value=(
                                    "Gantry 1"
                                    if "Gantry 1" in df["MachineName"].unique()
                                    else gty_op[0]["value"]
                                ),
                                clearable=False,
                                style=DROPDOWN_STYLE,
                            ),

                            html.Label("Device", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="device-dropdown",
                                options=xrv_op,
                                value=(
                                    "XRV-3000"
                                    if "XRV-3000" in df["Device"].unique()
                                    else xrv_op[0]["value"]
                                ),
                                clearable=False,
                                style=DROPDOWN_STYLE,
                            ),

                            html.Label("Energy", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="energy-dropdown",
                                options=mev_op,
                                value=[70, 100, 150, 200, 240],
                                multi=True,
                                clearable=False,
                                style=DROPDOWN_STYLE,
                            ),

                            html.Label("Gantry angle", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="gantry-angle-dropdown",
                                options=ga_op,
                                value=[0, 90, 180, 270],
                                multi=True,
                                clearable=False,
                                style=DROPDOWN_STYLE,
                            ),

                            html.Label("FWHM value", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="fwhm-column-dropdown",
                                options=fwhm_op,
                                value="ave_fwhm",
                                clearable=False,
                                style=DROPDOWN_STYLE,
                            ),

                            html.Label("Months back", style=LABEL_STYLE),
                            dcc.Input(
                                id="months-input",
                                type="number",
                                value=12,
                                min=1,
                                max=60,
                                step=1,
                                style=INPUT_STYLE,
                            ),

                            html.Label("Reference source", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="ref-source-dropdown",
                                options=[
                                    {"label": "TPS", "value": "TPS"},
                                ],
                                value="TPS",
                                clearable=False,
                                style=DROPDOWN_STYLE,
                            ),

                            html.Div(
                                "The graph updates automatically when a filter changes.",
                                style={
                                    "color": "#9dadc2",
                                    "fontSize": "12px",
                                    "marginTop": "16px",
                                    "lineHeight": "1.4",
                                },
                            ),
                        ],
                    ),
                ],
            ),

            html.Main(
                style=MAIN_STYLE,
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "alignItems": "baseline",
                            "marginBottom": "14px",
                            "maxWidth": "1450px",
                        },
                        children=[
                            html.Div(
                                children=[
                                    html.H1(
                                        "Spot size QA",
                                        style={
                                            "margin": "0",
                                            "fontSize": "28px",
                                        },
                                    ),
                                    html.Div(
                                        "FWHM by spot location, energy and gantry angle.",
                                        style={
                                            "color": "#5c6777",
                                            "fontSize": "14px",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),

                    dcc.Tabs(
                        id="right-tabs",
                        value="spot-size",
                        style={
                            "maxWidth": "1450px",
                        },
                        children=[
                            dcc.Tab(
                                label="Spot size",
                                value="spot-size",
                                children=[
                                    html.Div(
                                        style=PLOT_CARD_STYLE,
                                        children=[
                                            dcc.Loading(
                                                type="circle",
                                                children=dcc.Graph(
                                                    id="spot-size-graph",
                                                    config={
                                                        "displaylogo": False,
                                                        "responsive": True,
                                                    },
                                                    responsive=True,
                                                    style={
                                                        "height": "78vh",
                                                        "width": "100%",
                                                        "minWidth": "0",
                                                    },
                                                ),
                                            )
                                        ],
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
