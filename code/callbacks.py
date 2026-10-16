"""One plot callback for each teammate function, plus sidebar UI callbacks."""
import re
import pandas as pd
from dash import Input, Output, State, ctx, dcc, html, no_update
import constants as cfg
import figures as figs
import filters as flt


def _numeric_ref(gantry, energy, ga, parameter, source, sigma_ref_df, direct_ref_df):
    """Resolve the correct direct-FWHM or sigma-derived reference value."""
    if source == "none" or energy is None:
        return None
    if direct_ref_df is not None:
        m = re.search(r"(\d+)$", str(gantry))
        if not m:
            return None
        ref_g = cfg.TPS_REF_GANTRY if source.upper() == "TPS" else int(m.group(1))
        ref_ga = cfg.TPS_REF_GA if source.upper() == "TPS" else ga
        subset = direct_ref_df[
            direct_ref_df["data_type"].astype(str).str.casefold().eq(source.casefold()) &
            pd.to_numeric(direct_ref_df["gantry"], errors="coerce").eq(ref_g) &
            pd.to_numeric(direct_ref_df["gantry_angle"], errors="coerce").eq(ref_ga) &
            pd.to_numeric(direct_ref_df["energy"], errors="coerce").eq(energy)
        ]
        if not subset.empty:
            return float(subset.iloc[0]["fwhm"])
    if source.upper() == "TPS" and sigma_ref_df is not None:
        subset = sigma_ref_df[
            sigma_ref_df["source"].astype(str).str.strip().str.upper().eq(cfg.TPS_REF_SOURCE) &
            pd.to_numeric(sigma_ref_df["gantry"], errors="coerce").eq(cfg.TPS_REF_GA) &
            pd.to_numeric(sigma_ref_df["energy"], errors="coerce").eq(energy)
        ]
        if not subset.empty:
            row = subset.iloc[0]
            hor = float(row["x_stddev"]) * cfg.FWHM_FACTOR
            vert = float(row["y_stddev"]) * cfg.FWHM_FACTOR
            return hor if parameter == "hor_fwhm" else (vert if parameter == "vert_fwhm"
                                                        else (hor + vert) / 2)
    return None


def _safe_months(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = cfg.DEFAULT_MONTHS
    return value if 1 <= value <= 60 else cfg.DEFAULT_MONTHS


def _date_kwargs(period, start_date, end_date):
    """Convert sidebar preset/custom selection into filter-only date arguments."""
    if period == "custom":
        return {"start_date": start_date or "invalid", "end_date": end_date or "invalid"}
    return {"months": _safe_months(period)}


def _keep_multi(available, current):
    """Keep user's deliberate Clear selection; remove now-unavailable values."""
    if current == []:
        return []
    if current is None:
        return available
    kept = [v for v in current if v in available]
    return kept if kept else available


def _graph_or_blank(fig):
    return fig if fig is not None else figs.blank_figure("No data for the selected filters.")


def _selected_energies(values):
    """Normalise Dash's multi-select output to a list."""
    if values is None:
        return []
    return list(values) if isinstance(values, (list, tuple, set)) else [values]


def _plot_component(fig, graph_id, theme="light"):
    """Graph height follows the Plotly figure; no large blank fixed-height graph."""
    fig = _graph_or_blank(fig)
    # Keep teammates' traces, layouts, heights and data intact: only change theme.
    mode = theme if theme in cfg.THEME_TEMPLATES else "light"
    palette = cfg.THEME_FIGURE_COLOURS[mode]
    fig.update_layout(template=cfg.THEME_TEMPLATES[mode],
                      paper_bgcolor=palette["paper"],
                      plot_bgcolor=palette["plot"],
                      font=dict(color=palette["text"]))
    height = fig.layout.height or cfg.PLOT_HEIGHT
    return dcc.Graph(id=graph_id, figure=fig,
                     config={"displaylogo": False, "responsive": True},
                     responsive=True,
                     style={"width": "100%", "minWidth": "0", "height": f"{height}px"})


def _blank_component(message, graph_id, theme="light"):
    return [_plot_component(figs.blank_figure(message), graph_id, theme)]


def register_callbacks(app, qa_df, sigma_ref_df, direct_ref_df):

    @app.callback(Output("app-shell", "className"), Input("theme-mode", "value"))
    def set_colour_theme(mode):
        return "theme-dark" if mode == "dark" else "theme-light"

    @app.callback(Output("app-shell", "style"), Output("sidebar", "style"),
                  Output("sidebar-content", "style"), Output("toggle-sidebar", "children"),
                  Input("toggle-sidebar", "n_clicks"))
    def toggle_sidebar(clicks):
        if clicks and clicks % 2:
            return cfg.APP_STYLE_COLLAPSED, cfg.SIDEBAR_STYLE_COLLAPSED, {"display": "none"}, "▶"
        return cfg.APP_STYLE_OPEN, cfg.SIDEBAR_STYLE_OPEN, {"display": "block"}, "◀"

    @app.callback(Output("custom-date-group", "style"),
                  Input("period-select", "value"))
    def toggle_custom_dates(period):
        return (cfg.SIDEBAR_GROUP_VISIBLE if period == "custom"
                else cfg.SIDEBAR_GROUP_HIDDEN)

    @app.callback(Output("plot-type-dropdown", "options"),
                  Output("plot-type-dropdown", "value"),
                  Input("qa-type-dropdown", "value"),
                  State("plot-type-dropdown", "value"))
    def update_plot_options(qa_type, current_plot):
        options = flt.valid_plots(qa_type)
        valid = [o["value"] for o in options]
        return options, flt.select_preferred(valid, current_plot, preferred="average")

    @app.callback(Output("parameter-dropdown", "options"),
                  Output("parameter-dropdown", "value"),
                  Output("parameter-group", "style"),
                  Output("focus-ga-group", "style"),
                  Output("multi-ga-group", "style"),
                  Output("reference-group", "style"),
                  Input("qa-type-dropdown", "value"),
                  Input("plot-type-dropdown", "value"),
                  Input("gantry-dropdown", "value"),
                  Input("device-dropdown", "value"),
                  State("parameter-dropdown", "value"))
    def update_plot_controls(qa_type, plot_type, gantry, device, current_param):
        options = flt.parameter_options(qa_df, qa_type, plot_type,
                                        gantry=gantry, device=device)
        valid = [o["value"] for o in options]
        default = "ave_fwhm" if qa_type == "fwhm" and plot_type == "average" else None
        value = flt.select_preferred(valid, current_param, preferred=default)
        # Every average or matrix view uses the sidebar's multi-angle selector.
        # Single-spot and 2x2 plots use one GA at a time.
        multi_ga = plot_type in ("average", "matrix")
        focus_ga = plot_type in ("individual", "time")
        return (options, value,
                cfg.SIDEBAR_GROUP_HIDDEN if plot_type == "time" else cfg.SIDEBAR_GROUP_VISIBLE,
                cfg.SIDEBAR_GROUP_VISIBLE if focus_ga else cfg.SIDEBAR_GROUP_HIDDEN,
                cfg.SIDEBAR_GROUP_VISIBLE if multi_ga else cfg.SIDEBAR_GROUP_HIDDEN,
                cfg.SIDEBAR_GROUP_VISIBLE if qa_type == "fwhm" else cfg.SIDEBAR_GROUP_HIDDEN)

    @app.callback(Output("device-dropdown", "options"),
                  Output("device-dropdown", "value"),
                  Input("gantry-dropdown", "value"),
                  State("device-dropdown", "value"))
    def update_device_choices(gantry, current_device):
        values = flt.existing_values(qa_df, "Device", gantry=gantry)
        return flt.device_choices(values), flt.select_preferred(values, current_device, preferred="XRV-3000")

    @app.callback(Output("energy-dropdown", "options"),
                  Output("energy-dropdown", "value"),
                  Input("gantry-dropdown", "value"), Input("device-dropdown", "value"),
                  Input("energy-dropdown-all", "n_clicks"),
                  Input("energy-dropdown-clear", "n_clicks"),
                  State("energy-dropdown", "value"))
    def update_energy_choices(gantry, device, all_clicks, clear_clicks, selected):
        available = flt.existing_values(qa_df, "Energy", gantry=gantry, device=device)
        if ctx.triggered_id == "energy-dropdown-all":
            chosen = available
        elif ctx.triggered_id == "energy-dropdown-clear":
            chosen = []
        else:
            chosen = _keep_multi(available, selected)
        return flt.choices(available), chosen

    @app.callback(Output("focus-ga-dropdown", "options"),
                  Output("focus-ga-dropdown", "value"),
                  Output("gantry-angle-dropdown", "options"),
                  Output("gantry-angle-dropdown", "value"),
                  Input("gantry-dropdown", "value"), Input("device-dropdown", "value"),
                  Input("energy-dropdown", "value"),
                  Input("gantry-angle-dropdown-all", "n_clicks"),
                  Input("gantry-angle-dropdown-clear", "n_clicks"),
                  State("focus-ga-dropdown", "value"),
                  State("gantry-angle-dropdown", "value"))
    def update_ga_choices(gantry, device, energies, all_clicks, clear_clicks,
                          current_focus, current_multi):
        # With no selected energy, still show available GA choices for recovery.
        available = flt.existing_values(qa_df, "Gantry Angle", gantry=gantry,
                                        device=device, energies=energies or None)
        if ctx.triggered_id == "gantry-angle-dropdown-all":
            multi = available
        elif ctx.triggered_id == "gantry-angle-dropdown-clear":
            multi = []
        else:
            multi = _keep_multi(available, current_multi)
        return (flt.choices(available), flt.select_preferred(available, current_focus, preferred=0),
                flt.choices(available), multi)

    @app.callback(Output("average-panel", "style"),
                  Output("individual-panel", "style"),
                  Output("time-panel", "style"),
                  Output("matrix-panel", "style"),
                  Input("plot-type-dropdown", "value"))
    def show_selected_graph(plot_type):
        return tuple(cfg.GRAPH_PANEL_VISIBLE if value == plot_type else cfg.GRAPH_PANEL_HIDDEN
                     for value in cfg.PLOT_TYPES)

    # Plot callback 1 -> collaborator's averaged function.
    @app.callback(Output("average-graphs", "children"),
                  Input("plot-type-dropdown", "value"), Input("qa-type-dropdown", "value"),
                  Input("parameter-dropdown", "value"), Input("gantry-dropdown", "value"),
                  Input("device-dropdown", "value"), Input("energy-dropdown", "value"),
                  Input("focus-ga-dropdown", "value"), Input("gantry-angle-dropdown", "value"),
                  Input("period-select", "value"),
                  Input("custom-date-range", "start_date"),
                  Input("custom-date-range", "end_date"), Input("ref-source-dropdown", "value"),
                  Input("theme-mode", "value"))
    def plot_average_callback(plot_type, option, parameter, gantry, device,
                              energies, ga, angles, period, date_start, date_end, source, theme):
        if plot_type != "average":
            return no_update
        if not flt.plot_is_available(qa_df, option, "average", parameter):
            return _blank_component("Selected average parameter is unavailable.", "average-empty", theme)
        selected = _selected_energies(energies)
        if not selected:
            return _blank_component("Select at least one energy.", "average-empty", theme)
        if not angles:
            return _blank_component("Select at least one gantry angle.", "average-empty", theme)
        filtered = flt.filter_qa_data(qa_df, gantry=gantry, device=device,
                                      energies=selected, gantry_angles=angles, **_date_kwargs(period, date_start, date_end))
        if filtered.empty:
            return _blank_component("No data for the selected filters.", "average-empty", theme)
        tolerance = (cfg.SPOT_POSITION_TOLERANCES.get(parameter)
                     if option == "spot_position" else None)
        if option == "fwhm" and source != "none":
            tolerance = {(e, angle): _numeric_ref(gantry, e, angle, parameter, source,
                                                  sigma_ref_df, direct_ref_df)
                         for e in selected for angle in angles}
        figure = figs.plot_ave_spot_position_by_en_ga(
            filtered, option, parameter, gantry, device, selected,
            _safe_months(period), tolerance)
        return [_plot_component(figure, "average-result", theme)]

    # Plot callback 2 -> collaborator's individual-spot function.
    @app.callback(Output("individual-graphs", "children"),
                  Input("plot-type-dropdown", "value"), Input("qa-type-dropdown", "value"),
                  Input("parameter-dropdown", "value"), Input("gantry-dropdown", "value"),
                  Input("device-dropdown", "value"), Input("energy-dropdown", "value"),
                  Input("focus-ga-dropdown", "value"), Input("period-select", "value"),
                  Input("custom-date-range", "start_date"),
                  Input("custom-date-range", "end_date"),
                  Input("ref-source-dropdown", "value"),
                  Input("theme-mode", "value"))
    def plot_individual_callback(plot_type, option, parameter, gantry, device,
                                 energies, ga, period, date_start, date_end, source, theme):
        if plot_type != "individual":
            return no_update
        if not flt.plot_is_available(qa_df, option, "individual", parameter):
            return _blank_component("Selected individual parameter is unavailable.", "individual-empty", theme)
        selected = _selected_energies(energies)
        if not selected:
            return _blank_component("Select at least one energy.", "individual-empty", theme)
        filtered = flt.filter_qa_data(qa_df, gantry=gantry, device=device,
                                      energies=selected, gantry_angles=ga, **_date_kwargs(period, date_start, date_end))
        if filtered.empty:
            return _blank_component("No data for the selected filters.", "individual-empty", theme)
        tolerance = (cfg.SPOT_POSITION_TOLERANCES.get(parameter)
                     if option == "spot_position" else None)
        if option == "fwhm" and source != "none":
            tolerance = {e: _numeric_ref(gantry, e, ga, parameter, source,
                                         sigma_ref_df, direct_ref_df) for e in selected}
        fig = figs.plot_by_spot_position(
            filtered, option, parameter, gantry, device, selected, ga,
            _safe_months(period), tolerance)
        return [_plot_component(fig, "individual-result", theme)]

    # Plot callback 3 -> collaborator's 2x2 time series.
    @app.callback(Output("time-graphs", "children"),
                  Input("plot-type-dropdown", "value"), Input("qa-type-dropdown", "value"),
                  Input("gantry-dropdown", "value"), Input("device-dropdown", "value"),
                  Input("energy-dropdown", "value"), Input("focus-ga-dropdown", "value"),
                  Input("period-select", "value"),
                  Input("custom-date-range", "start_date"),
                  Input("custom-date-range", "end_date"), Input("ref-source-dropdown", "value"),
                  Input("theme-mode", "value"))
    def plot_time_series_callback(plot_type, option, gantry, device, energies, ga, period, date_start, date_end, source, theme):
        if plot_type != "time":
            return no_update
        if not flt.plot_is_available(qa_df, option, "time", None):
            return _blank_component("This QA type or orientation data is unavailable for 2x2 plots.", "time-empty", theme)
        selected = _selected_energies(energies)
        if not selected:
            return _blank_component("Select at least one energy.", "time-empty", theme)
        filtered = flt.filter_qa_data(qa_df, gantry=gantry, device=device,
                                      energies=selected, gantry_angles=ga, **_date_kwargs(period, date_start, date_end))
        if filtered.empty:
            return _blank_component("No data for the selected filters.", "time-empty", theme)
        raw = {column for pair in cfg.GRADIENT_PAIRS.values() for column in pair}
        if option == "spot_symmetry" and not raw.issubset(filtered.columns):
            return _blank_component("Missing raw gradient columns.", "time-empty", theme)
        ref = sigma_ref_df if option == "fwhm" and source == "TPS" else None
        fig = figs.plotly_spot_time_series(
            filtered, option, gantry, device, selected, ga,
            n_months=_safe_months(period), ref_df=ref, ref_source="TPS",
            tol_frac=cfg.FWHM_TOL_FRAC)
        return [_plot_component(fig, "time-result", theme)]

    # Plot callback 4 -> collaborator's multi-energy spot matrix.
    @app.callback(Output("matrix-graphs", "children"),
                  Input("plot-type-dropdown", "value"), Input("qa-type-dropdown", "value"),
                  Input("parameter-dropdown", "value"), Input("gantry-dropdown", "value"),
                  Input("device-dropdown", "value"), Input("energy-dropdown", "value"),
                  Input("gantry-angle-dropdown", "value"), Input("period-select", "value"),
                  Input("custom-date-range", "start_date"),
                  Input("custom-date-range", "end_date"),
                  Input("ref-source-dropdown", "value"),
                  Input("theme-mode", "value"))
    def plot_matrix_callback(plot_type, option, parameter, gantry, device, energies, angles, period, date_start, date_end, source, theme):
        if plot_type != "matrix":
            return no_update
        if not flt.plot_is_available(qa_df, option, "matrix", parameter):
            return _blank_component("Selected matrix parameter is unavailable.", "matrix-empty", theme)
        if not energies or not angles:
            return _blank_component("Select at least one energy and gantry angle.", "matrix-empty", theme)
        filtered = flt.filter_qa_data(qa_df, gantry=gantry, device=device,
                                      energies=energies, gantry_angles=angles, **_date_kwargs(period, date_start, date_end))
        if filtered.empty:
            return _blank_component("No data for the selected filters.", "matrix-empty", theme)
        raw = {column for pair in cfg.GRADIENT_PAIRS.values() for column in pair}
        if option == "spot_symmetry" and not raw.issubset(filtered.columns):
            return _blank_component("Missing raw gradient columns.", "matrix-empty", theme)
        ref = sigma_ref_df if option == "fwhm" and source == "TPS" else None
        fig = figs.plotly_spot_matrix(
            filtered, option, parameter, gantry, device,
            energy=energies, gantry_angle=angles, n_months=_safe_months(period),
            ref_df=ref, ref_source="TPS", tol_frac=cfg.FWHM_TOL_FRAC)
        return [_plot_component(fig, "matrix-result", theme)]
