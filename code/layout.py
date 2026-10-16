"""Dash visual structure. All user controls live in the sticky left sidebar."""
from dash import dcc, html
import constants as cfg
import filters as flt


def dropdown(label, control_id, options, value=None, multi=False):
    return html.Div([
        html.Label(label, style=cfg.LABEL_STYLE),
        dcc.Dropdown(id=control_id, options=options, value=value, multi=multi,
                     clearable=False, style=cfg.DROPDOWN_STYLE),
    ])


def graph_panel(plot_type):
    """Charts are inserted by each plot callback; no plot-side filter controls."""
    return html.Div(id=f"{plot_type}-panel",
                    style=(cfg.GRAPH_PANEL_VISIBLE if plot_type == "average"
                           else cfg.GRAPH_PANEL_HIDDEN), children=[
        html.Div(style=cfg.PLOT_PANEL_STYLE, children=[
            dcc.Loading(type="circle", children=html.Div(id=f"{plot_type}-graphs")),
        ]),
    ])


def app_layout(df, sigma_ref_df, direct_ref_df):
    gantries = flt.existing_values(df, "MachineName")
    gantry = flt.select_preferred(gantries, preferred="Gantry 1")
    devices = flt.existing_values(df, "Device", gantry=gantry)
    device = flt.select_preferred(devices, preferred="XRV-3000")
    energies = flt.existing_values(df, "Energy", gantry=gantry, device=device)
    angles = flt.existing_values(df, "Gantry Angle", gantry=gantry,
                                 device=device, energies=energies)
    angle = flt.select_preferred(angles, preferred=0)
    params = flt.parameter_options(df, "fwhm", "average")

    ref_options = [{"label": "No reference", "value": "none"}]
    if sigma_ref_df is not None or direct_ref_df is not None:
        ref_options.insert(0, {"label": "TPS", "value": "TPS"})
    if (direct_ref_df is not None and
            (direct_ref_df["data_type"].astype(str).str.lower() == "baseline").any()):
        ref_options.insert(1 if ref_options[0]["value"] == "TPS" else 0,
                           {"label": "Baseline", "value": "baseline"})

    sidebar = html.Aside(id="sidebar", style=cfg.SIDEBAR_STYLE_OPEN, children=[
        html.Button("◀", id="toggle-sidebar", n_clicks=0, title="Hide/show filters",
                    style={"width": "34px", "height": "34px", "backgroundColor": "#0d131d",
                           "color": "#edf3fb", "border": "1px solid #34465f", "cursor": "pointer"}),
        html.Div(id="sidebar-content", children=[
            html.H2("Spot Grid QA", style={"fontSize": "17px", "margin": "8px 0 12px"}),
            dropdown("QA type", "qa-type-dropdown", flt.choices(cfg.QA_TYPES, cfg.QA_TYPES), "fwhm"),
            dropdown("Plot type", "plot-type-dropdown", flt.valid_plots("fwhm"), "average"),
            html.Div(id="parameter-group", children=[
                dropdown("Parameter", "parameter-dropdown", params,
                         "ave_fwhm" if "ave_fwhm" in [p["value"] for p in params]
                         else (params[0]["value"] if params else None))
            ]),
            html.Hr(style={"borderColor": "#26354b", "margin": "12px 0"}),
            dropdown("Gantry", "gantry-dropdown", flt.choices(gantries), gantry),
            dropdown("Device", "device-dropdown", flt.choices(devices), device),
            dropdown("Energies (MeV)", "energy-dropdown", flt.choices(energies), energies, multi=True),
            html.Div(id="focus-ga-group", children=[
                dropdown("Gantry angle (°)", "focus-ga-dropdown", flt.choices(angles), angle)
            ]),
            html.Div(id="multi-ga-group", style=cfg.SIDEBAR_GROUP_HIDDEN, children=[
                dropdown("Gantry angles (°)", "gantry-angle-dropdown",
                         flt.choices(angles), angles, multi=True),
            ]),
            html.Label("Months back", style=cfg.LABEL_STYLE),
            dcc.Input(id="months-input", type="number", value=cfg.DEFAULT_MONTHS,
                      min=1, max=60, step=1, style=cfg.INPUT_STYLE),
            html.Div(id="reference-group", children=[
                dropdown("FWHM reference", "ref-source-dropdown", ref_options, ref_options[0]["value"])
            ]),

        ]),
    ])

    # Plot type and all measurement filters are controlled from the sidebar.
    # Remove page heading and plot-panel headings to maximise plotting area.
    main = html.Main(style=cfg.MAIN_STYLE, children=[
        html.Div(style={"width": "100%", "maxWidth": "1450px", "minWidth": "0"}, children=[
            graph_panel("average"),
            graph_panel("individual"),
            graph_panel("time"),
            graph_panel("matrix"),
        ]),
    ])
    return html.Div(id="app-shell", style=cfg.APP_STYLE_OPEN, children=[sidebar, main])
