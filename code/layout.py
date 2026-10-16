"""Dash user interface. All selectors are in the left sidebar."""
import pandas as pd
from dash import dcc, html

import constants as cfg
import filters as flt


def dropdown(label, control_id, options, value=None, *, persist=False):
    return html.Div(className="filter-field", children=[
        html.Label(label, className="filter-label"),
        dcc.Dropdown(id=control_id, options=options, value=value,
                     clearable=False, className="sidebar-dropdown",
                     persistence=persist, persistence_type="local"),
    ])


def selection_group(label, control_id, options, value, *, multiple=False, show_actions=False):
    """Generate compact, accessible options from actual workbook values."""
    head = [html.Label(label, className="filter-label")]
    if show_actions:
        head.append(html.Div(className="selection-actions", children=[
            html.Button("All", id=f"{control_id}-all", n_clicks=0,
                        type="button", className="mini-action"),
            html.Button("Clear", id=f"{control_id}-clear", n_clicks=0,
                        type="button", className="mini-action"),
        ]))
    component = (dcc.Checklist if multiple else dcc.RadioItems)
    return html.Div(className="filter-field", children=[
        html.Div(head, className="filter-heading"),
        component(id=control_id, options=options, value=value,
                  className="chip-choice-group"),
    ])


def graph_panel(plot_type):
    """One panel per teammate function; no plot-side filters."""
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

    # First visit defaults to spot position. QA selection persists locally.
    qa_type = "spot_position"
    plot_type = "average"
    params = flt.parameter_options(df, qa_type, plot_type)
    param = params[0]["value"] if params else None

    ref_options = [{"label": "No reference", "value": "none"}]
    if sigma_ref_df is not None or direct_ref_df is not None:
        ref_options.insert(0, {"label": "TPS", "value": "TPS"})
    if (direct_ref_df is not None and
            (direct_ref_df["data_type"].astype(str).str.lower() == "baseline").any()):
        ref_options.insert(1 if ref_options[0]["value"] == "TPS" else 0,
                           {"label": "Baseline", "value": "baseline"})

    today = pd.Timestamp.today().normalize()
    earliest = pd.to_datetime(df["ADate"], errors="coerce").min()
    latest = pd.to_datetime(df["ADate"], errors="coerce").max()
    earliest = earliest.normalize() if pd.notna(earliest) else today - pd.DateOffset(years=5)
    latest = max(today, latest.normalize()) if pd.notna(latest) else today
    custom_start = max(earliest, today - pd.DateOffset(months=cfg.DEFAULT_MONTHS))

    sidebar = html.Aside(id="sidebar", style=cfg.SIDEBAR_STYLE_OPEN, children=[
        html.Button("◀", id="toggle-sidebar", n_clicks=0, title="Hide/show filters",
                    className="collapse-toggle", type="button"),
        html.Div(id="sidebar-content", children=[
            html.Div(className="sidebar-heading-row", children=[
                html.H2("Spot Grid QA", className="sidebar-title"),
                dcc.RadioItems(
                    id="theme-mode", options=[
                        {"label": "Light", "value": "light"},
                        {"label": "Dark", "value": "dark"},
                    ], value="light", persistence=True,
                    persistence_type="local", className="theme-mode-segments",
                ),
            ]),
            html.Div(className="filter-section", children=[
                dropdown("QA type", "qa-type-dropdown",
                         flt.choices(cfg.QA_TYPES, cfg.QA_TYPES), qa_type, persist=True),
                dropdown("Plot type", "plot-type-dropdown", flt.valid_plots(qa_type), plot_type),
                html.Div(id="parameter-group", children=[
                    dropdown("Parameter", "parameter-dropdown", params, param),
                ]),
            ]),
            html.Hr(className="sidebar-divider"),
            html.Div(className="filter-section", children=[
                html.Div(className="filter-field", children=[
                    html.Label("Gantry", className="filter-label"),
                    dcc.RadioItems(id="gantry-dropdown", options=flt.gantry_choices(gantries),
                                   value=gantry, className="gantry-segments"),
                ]),
                html.Div(className="filter-field", children=[
                    html.Label("Device", className="filter-label"),
                    dcc.RadioItems(id="device-dropdown", options=flt.device_choices(devices),
                                   value=device, className="device-segments"),
                ]),
                selection_group("Energies (MeV)", "energy-dropdown", flt.choices(energies),
                                energies, multiple=True, show_actions=True),
                html.Div(id="focus-ga-group", style=cfg.SIDEBAR_GROUP_HIDDEN, children=[
                    selection_group("Gantry angle (°)", "focus-ga-dropdown",
                                    flt.choices(angles), angle),
                ]),
                html.Div(id="multi-ga-group", children=[
                    selection_group("Gantry angles (°)", "gantry-angle-dropdown",
                                    flt.choices(angles), angles, multiple=True, show_actions=True),
                ]),
            ]),
            html.Hr(className="sidebar-divider"),
            html.Div(className="filter-section", children=[
                html.Div(className="filter-field", children=[
                    html.Label("Time period", className="filter-label"),
                    dcc.RadioItems(id="period-select", options=[
                        {"label": label, "value": value}
                        for value, label in cfg.DATE_PRESETS.items()
                    ], value=str(cfg.DEFAULT_MONTHS), className="period-segments"),
                ]),
                html.Div(id="custom-date-group", style=cfg.SIDEBAR_GROUP_HIDDEN,
                         className="filter-field", children=[
                    html.Label("Custom date range", className="filter-label"),
                    html.Div(className="date-range-field", children=[
                        html.Div(className="date-range-labels", children=[
                            html.Span("From"), html.Span("To"),
                        ]),
                        dcc.DatePickerRange(
                            id="custom-date-range",
                            start_date=custom_start.date(),
                            end_date=today.date(),
                            min_date_allowed=earliest.date(),
                            max_date_allowed=latest.date(),
                            initial_visible_month=custom_start.date(),
                            start_date_placeholder_text="DD MMM YYYY",
                            end_date_placeholder_text="DD MMM YYYY",
                            display_format="DD MMM YYYY",
                            month_format="MMMM YYYY",
                            first_day_of_week=1,
                            minimum_nights=0,
                            updatemode="bothdates",
                            number_of_months_shown=2,
                            with_portal=True,
                            clearable=False,
                            className="sidebar-date-range",
                        ),
                    ]),
                ]),
                html.Div(id="reference-group", style=cfg.SIDEBAR_GROUP_HIDDEN, children=[
                    dropdown("FWHM reference", "ref-source-dropdown", ref_options,
                             ref_options[0]["value"]),
                ]),
            ]),
        ]),
    ])

    main = html.Main(style=cfg.MAIN_STYLE, children=[
        html.Div(style={"width": "100%", "maxWidth": "1450px", "minWidth": "0"}, children=[
            graph_panel("average"), graph_panel("individual"),
            graph_panel("time"), graph_panel("matrix"),
        ]),
    ])
    return html.Div(id="app-shell", className="theme-light",
                    style=cfg.APP_STYLE_OPEN, children=[sidebar, main])
