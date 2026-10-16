from dash import Dash, Input, Output

import dash_layout as dsh
import figure as figs
import database as data_call

# =============
# Loading data
# =============
fwhm_df = data_call.load_fwhm_data()
ref_df = data_call.load_reference_data()

# =================
# dropdown options
# =================
machine_options = dsh.make_options(sorted(fwhm_df["MachineName"].dropna().unique()))
device_options = dsh.make_options(sorted(fwhm_df["Device"].dropna().unique()))
energy_options = dsh.make_options(sorted(fwhm_df["Energy"].dropna().unique()))
gantry_angle_options = dsh.make_options(sorted(fwhm_df["Gantry Angle"].dropna().unique()))

fwhm_options = [
    {"label": "Average FWHM", "value": "ave_fwhm"},
    {"label": "Horizontal FWHM", "value": "hor_fwhm"},
    {"label": "Vertical FWHM", "value": "vert_fwhm"},
    {"label": "BLTR diagonal FWHM", "value": "bltr_fwhm"},
    {"label": "TLBR diagonal FWHM", "value": "tlbr_fwhm"},
]

# =========
# Dash app
# =========

app = Dash(__name__)
server = app.server

app.layout = dsh.app_layout(fwhm_df,
                            machine_options, device_options, energy_options, gantry_angle_options, fwhm_options)

# ==========================
# Sidebar collapse callback
# ==========================

@app.callback(
    Output("app-shell", "style"),
    Output("sidebar", "style"),
    Output("sidebar-content", "style"),
    Output("toggle-sidebar", "children"),
    Input("toggle-sidebar", "n_clicks"),
)
def toggle_sidebar(n_clicks):
    """
    Collapse or expand the left filter panel.
    """

    collapsed = bool(n_clicks and n_clicks % 2 == 1)

    if collapsed:
        return (
            dsh.APP_STYLE_COLLAPSED,
            dsh.SIDEBAR_STYLE_COLLAPSED,
            {"display": "none"},
            "▶",
        )

    return (
        dsh.APP_STYLE_OPEN,
        dsh.SIDEBAR_STYLE_OPEN,
        {"display": "block"},
        "◀",
    )

# =====================
# Plot update callback
# =====================

@app.callback(
    Output("spot-size-graph", "figure"),
    Input("gantry-dropdown", "value"),
    Input("device-dropdown", "value"),
    Input("energy-dropdown", "value"),
    Input("gantry-angle-dropdown", "value"),
    Input("months-input", "value"),
    Input("fwhm-column-dropdown", "value"),
    Input("ref-source-dropdown", "value"),
)
def update_spot_size_plot(gantry, device, energy, gantry_angle, n_months, fwhm_col, ref_source):
    """
    Update the spot-size figure from the sidebar filters.
    """

    if not gantry or not device:
        return dsh.blank_figure("Select a gantry and device.")

    if not energy:
        return dsh.blank_figure("Select at least one energy.")

    if not gantry_angle:
        return dsh.blank_figure("Select at least one gantry angle.")

    if n_months is None:
        n_months = 12

    fig = figs.plotly_fwhm_spot_matrix(
        df=fwhm_df,
        gantry=gantry,
        device=device,
        energy=energy,
        gantry_angle=gantry_angle,
        n_months=int(n_months),
        fwhm_col=fwhm_col,
        ref_df=ref_df,
        ref_source=ref_source,
        show=False,
    )

    if fig is None:
        return dsh.blank_figure("No data after filtering.")

    # Keep sizing controlled by Dash rather than a fixed Plotly width.
    fig.update_layout(
        autosize=True,
        margin=dict(l=35, r=205, t=95, b=55),
    )

    return fig

# ========
# Run app
# ========

app.run(
    debug=False,
    port=8050,
    use_reloader=False,
)
