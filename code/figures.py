"""Team-supplied generalised plotting functions, wired for Dash.

Four function bodies correspond to the functions supplied by the user.
Data selection by gantry/device/energy/date was moved to filters.py.
Plot calculations and spot-specific rendering are retained from team code.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import constants as cfg


def blank_figure(message):
    fig = go.Figure()
    fig.update_layout(template=cfg.PLOT_TEMPLATE,
                      xaxis={"visible": False}, yaxis={"visible": False},
                      annotations=[dict(text=message.replace("\n", "<br>"), x=0.5, y=0.5,
                                        xref="paper", yref="paper", showarrow=False,
                                        font=dict(size=16))], height=cfg.PLOT_HEIGHT)
    return fig


# 1. Generalised averaged plot (from message)
def plot_ave_spot_position_by_en_ga(df, option, parameter, gantry, device, energy, n_months, tolerance):
    """Average each measurement date, energy and gantry angle; draw one figure."""
    # The selected energies and angles are already filtered by filters.py.
    if option not in ("spot_position", "fwhm", "spot_symmetry"):
        raise ValueError(f"Unknown QA option: {option}")
    if df.empty:
        return None

    # One result per date / energy / GA, rather than repeated .transform('mean') rows.
    selected_df = (df.groupby(["ADate", "Energy", "Gantry Angle"], as_index=False)[parameter]
                   .mean().rename(columns={parameter: f"avg_{parameter}"}))
    energies = sorted(selected_df["Energy"].dropna().unique().tolist())
    selected_df["Energy"] = selected_df["Energy"].astype(int).astype(str)
    selected_df["Gantry Angle"] = selected_df["Gantry Angle"].astype(str)
    energy_colours = cfg.colour_map(energies, cfg.ENERGY_COLOURS)

    fig = px.scatter(
        selected_df, x="ADate", y=f"avg_{parameter}",
        color="Energy", symbol="Gantry Angle",
        color_discrete_map={str(e): energy_colours[e] for e in energies},
        symbol_map={str(ga): symbol for ga, symbol in cfg.GANTRY_SYMBOLS.items()},
        title=f"{gantry} – {device} — Average {cfg.PARAMETER_LABELS[parameter]}",
        labels={"ADate": "Date", f"avg_{parameter}": f"Average {cfg.PARAMETER_LABELS[parameter]}",
                "Energy": "Energy (MeV)"},
        hover_data={"ADate": "|%Y-%m-%d"},
        height=cfg.PLOT_HEIGHT, opacity=cfg.MARKER_OPACITY,
    )

    for trace in fig.data:
        energy_text, angle_text = str(trace.name).split(", ", 1)
        trace.name = f"{energy_text} MeV | GA {angle_text}°"

    # Spot-position tolerance is independent of energy.
    if option == "spot_position" and tolerance is not None:
        for limit in (tolerance, -tolerance):
            fig.add_hline(y=limit, line_dash=cfg.TOLERANCE_DASH,
                          line_color=cfg.TOLERANCE_COLOR)

    # FWHM reference values depend on energy (and optionally gantry angle).
    # `tolerance` is the numeric reference, or {(energy, GA): reference}.
    elif option == "fwhm" and tolerance is not None:
        references = tolerance if isinstance(tolerance, dict) else {(e, None): tolerance for e in energies}
        drawn = set()
        for (e, ga), reference in references.items():
            if reference is None or (e, reference) in drawn:
                continue
            drawn.add((e, reference))
            colour = energy_colours.get(e, cfg.TOLERANCE_COLOR)
            for scale in (1 - cfg.FWHM_TOL_FRAC, 1 + cfg.FWHM_TOL_FRAC):
                fig.add_hline(y=reference * scale, line_dash=cfg.TOLERANCE_DASH,
                              line_color=colour)

    fig.update_traces(mode="markers+lines",
                      marker=dict(size=cfg.MARKER_SIZE,
                                  line=dict(width=cfg.MARKER_OUTLINE_WIDTH)),
                      line=dict(width=cfg.TRACE_LINE_WIDTH),
                      hovertemplate="Date: %{x|%Y-%m-%d}<br>"
                                    + f"{parameter}: %{{y:.3f}}<br>"
                                    + "Energy / GA: %{fullData.name}<extra></extra>")
    fig.update_layout(template=cfg.PLOT_TEMPLATE,
                      legend_title_text="Energy (MeV), GA (°)")
    return fig


# 2. Spot-position-indexed time-series (from attachment 2)
def plot_by_spot_position(df, option, parameter, gantry, device, energy, gantry_angle, n_months, tolerance):
    """Draw all selected energy/spot series on the same axes."""
    if option not in cfg.PARAMETERS or parameter not in cfg.PARAMETERS[option]:
        raise ValueError(f"Invalid parameter {parameter!r} for QA type {option!r}")
    if df.empty:
        return None

    # One colour per energy and one marker shape per physical spot.
    selected_df = df.copy()
    energies = sorted(selected_df["Energy"].dropna().unique().tolist())
    selected_df["Energy"] = selected_df["Energy"].astype(int).astype(str)
    energy_colours = cfg.colour_map(energies, cfg.ENERGY_COLOURS)
    spots = selected_df["Spot"].dropna().unique().tolist()

    fig = px.scatter(
        selected_df, x="ADate", y=parameter,
        color="Energy", symbol="Spot",
        color_discrete_map={str(e): energy_colours[e] for e in energies},
        symbol_map=cfg.symbol_map(spots, cfg.SPOT_SYMBOLS),
        title=f"{gantry} – {device} — GA {gantry_angle}° — {cfg.PARAMETER_LABELS[parameter]}",
        labels={"ADate": "Date", parameter: cfg.PARAMETER_LABELS[parameter],
                "Energy": "Energy (MeV)", "Spot": "Spot"},
        hover_data={"ADate": "|%Y-%m-%d"},
        height=cfg.PLOT_HEIGHT, opacity=cfg.MARKER_OPACITY,
    )

    for trace in fig.data:
        energy_text, spot_text = str(trace.name).split(", ", 1)
        trace.name = f"{energy_text} MeV | {spot_text}"

    if option == "spot_position" and tolerance is not None:
        for limit in (tolerance, -tolerance):
            fig.add_hline(y=limit, line_dash=cfg.TOLERANCE_DASH,
                          line_color=cfg.TOLERANCE_COLOR)
    elif option == "fwhm" and tolerance is not None:
        references = tolerance if isinstance(tolerance, dict) else {e: tolerance for e in energies}
        for e, reference in references.items():
            if reference is None:
                continue
            for scale in (1 - cfg.FWHM_TOL_FRAC, 1 + cfg.FWHM_TOL_FRAC):
                fig.add_hline(y=reference * scale, line_dash=cfg.TOLERANCE_DASH,
                              line_color=energy_colours.get(e, cfg.TOLERANCE_COLOR))

    fig.update_traces(mode="markers+lines",
                      marker=dict(size=cfg.MARKER_SIZE,
                                  line=dict(width=cfg.MARKER_OUTLINE_WIDTH)),
                      line=dict(width=cfg.TRACE_LINE_WIDTH),
                      hovertemplate="Date: %{x|%Y-%m-%d}<br>"
                                    + f"{parameter}: %{{y:.3f}}<br>"
                                    + "Energy, Spot: %{fullData.name}<extra></extra>")
    fig.update_layout(template=cfg.PLOT_TEMPLATE, legend_title_text="Energy (MeV), Spot")
    return fig


# 3. Four-orientation time-series (from attachment 1)
def plotly_spot_time_series(
    df,
    option,
    gantry,
    device,
    energy,
    gantry_angle,
    n_months=12,
    ref_df=None,
    ref_source="TPS",
    tol_frac=cfg.FWHM_TOL_FRAC
):
    """
    Plot spot time-series data as four orientation subplots.

    Parameters
    ----------
    df : DataFrame

    option : str
        "fwhm" | "spot_symmetry"

    gantry : str
        e.g. "Gantry 1", "Gantry 2"

    device : str
        e.g. "XRV-3000", "XRV-4000"

    energy : int or list[int] (selection already applied by filters.py)

    gantry_angle : int
        e.g. 0, 90, 180, 270

    n_months : int
        Number of months of data to display.

    ref_df : DataFrame or None
        Reference table used for FWHM tolerance.
        Expected columns:
        source, gantry, energy, x_stddev, y_stddev

    ref_source : str
        e.g. "TPS", "G1", "G2"

    tol_frac : float
        Fractional FWHM tolerance.
        e.g. 0.10 = ±10%

    Returns
    -------
    fig
        Plotly figure.
    """

    # Input df has already been filtered in filters.filter_qa_data().
    selected_df = df.copy()

    if selected_df.empty:
        print("No data after filtering.")
        return None

    # ------------------------------------------------------------------
    # Define data according to option
    # ------------------------------------------------------------------

    if option == "fwhm":

        plot_cols = cfg.FWHM_ORIENTATIONS

        y_axis_name = "FWHM (mm)"
        plot_title = "FWHM"

    elif option == "spot_symmetry":

        required_cols = [
            "hor_rt_gradient",
            "hor_lt_gradient",
            "vert_rt_gradient",
            "vert_lt_gradient",
            "bltr_rt_gradient",
            "bltr_lt_gradient",
            "tlbr_rt_gradient",
            "tlbr_lt_gradient"
        ]

        missing_cols = [
            col
            for col in required_cols
            if col not in selected_df.columns
        ]

        if missing_cols:
            raise ValueError(
                "Missing columns required for spot symmetry: "
                f"{missing_cols}"
            )

        # Gradient ratios used for spot symmetry
        selected_df["gr_hor"] = (
            selected_df["hor_rt_gradient"]
            / selected_df["hor_lt_gradient"]
        )

        selected_df["gr_vert"] = (
            selected_df["vert_rt_gradient"]
            / selected_df["vert_lt_gradient"]
        )

        selected_df["gr_bltr"] = (
            selected_df["bltr_rt_gradient"]
            / selected_df["bltr_lt_gradient"]
        )

        selected_df["gr_tlbr"] = (
            selected_df["tlbr_rt_gradient"]
            / selected_df["tlbr_lt_gradient"]
        )

        plot_cols = cfg.GR_ORIENTATIONS

        y_axis_name = "Gradient Ratio (RT/LT)"
        plot_title = "Spot Symmetry"

    else:
        raise ValueError(
            "option must be 'fwhm' or 'spot_symmetry'"
        )

    # ------------------------------------------------------------------
    # Check plotting columns exist
    # ------------------------------------------------------------------

    missing_plot_cols = [
        col
        for col in plot_cols.values()
        if col not in selected_df.columns
    ]

    if missing_plot_cols:
        raise ValueError(
            f"Missing plotting columns: {missing_plot_cols}"
        )

    # ------------------------------------------------------------------
    # Colours and symbols
    # ------------------------------------------------------------------

    spots = (
        selected_df["Spot"]
        .dropna()
        .unique()
        .tolist()
    )

    # Standard Plotly discrete colour palette
    spot_colours = cfg.colour_map(spots, cfg.SPOT_COLOURS)

    spot_symbols = cfg.symbol_map(spots, cfg.SPOT_SYMBOLS)

    # ------------------------------------------------------------------
    # Create 2 x 2 figure
    # ------------------------------------------------------------------

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=list(plot_cols.keys()),
        shared_xaxes=True,
        **cfg.TWO_BY_TWO_SPACING
    )

    subplot_positions = cfg.ORIENTATIONS

    # ------------------------------------------------------------------
    # Add data: all selected energies are already present in selected_df.
    # ------------------------------------------------------------------
    energies = sorted(selected_df["Energy"].dropna().unique().tolist())
    energy_colours = cfg.colour_map(energies, cfg.ENERGY_COLOURS)
    for orientation, parameter in plot_cols.items():
        row, col = subplot_positions[orientation]
        for energy_value in energies:
            colour = energy_colours[energy_value]
            for spot in spots:
                spot_df = selected_df[
                    (selected_df["Energy"] == energy_value) &
                    (selected_df["Spot"] == spot)
                ].sort_values("ADate")
                if spot_df.empty:
                    continue
                series_name = f"{energy_value} MeV | {spot}"
                fig.add_trace(
                    go.Scatter(
                        x=spot_df["ADate"], y=spot_df[parameter],
                        mode="markers+lines",
                        name=series_name, legendgroup=series_name,
                        showlegend=(orientation == "Horizontal"),
                        marker=dict(size=cfg.MARKER_SIZE, symbol=spot_symbols[spot],
                                    color=colour, opacity=cfg.MARKER_OPACITY,
                                    line=dict(width=cfg.MARKER_OUTLINE_WIDTH)),
                        line=dict(width=cfg.TRACE_LINE_WIDTH, color=colour),
                        hovertemplate=(
                            f"Energy: {energy_value} MeV<br>Spot: {spot}<br>"
                            "Date: %{x|%Y-%m-%d}<br>"
                            f"{orientation}: %{{y:.3f}}<extra></extra>"
                        ),
                    ), row=row, col=col,
                )

    # ------------------------------------------------------------------
    # FWHM reference / tolerance (one reference per selected energy)
    # ------------------------------------------------------------------
    if option == "fwhm" and ref_df is not None:
        ref_src = cfg.TPS_REF_SOURCE if str(ref_source).upper() == "TPS" else ref_source
        ref_ga = cfg.TPS_REF_GA if str(ref_source).upper() == "TPS" else gantry_angle
        for energy_value in energies:
            ref = ref_df[
                ref_df["source"].astype(str).str.strip().str.upper().eq(str(ref_src).upper()) &
                pd.to_numeric(ref_df["gantry"], errors="coerce").eq(ref_ga) &
                pd.to_numeric(ref_df["energy"], errors="coerce").eq(energy_value)
            ]
            if ref.empty:
                continue
            r = ref.iloc[0]
            hor_center = float(r["x_stddev"]) * cfg.FWHM_FACTOR
            vert_center = float(r["y_stddev"]) * cfg.FWHM_FACTOR
            diag_center = (hor_center + vert_center) / 2
            centres = {"Horizontal": hor_center, "Vertical": vert_center,
                       "BLTR": diag_center, "TLBR": diag_center}
            for orientation, center in centres.items():
                row, col = subplot_positions[orientation]
                for scale in (1 - tol_frac, 1 + tol_frac):
                    fig.add_hline(y=center * scale, line_dash=cfg.TOLERANCE_DASH,
                                  line_color=energy_colours[energy_value],
                                  line_width=cfg.TOLERANCE_WIDTH, row=row, col=col)

    # ------------------------------------------------------------------
    # Title
    # ------------------------------------------------------------------

    if option == "fwhm" and ref_df is not None:

        tolerance_text = (
            f"<br><sup>"
            f"Tolerance: {ref_source} FWHM "
            f"±{tol_frac:.0%}"
            f"</sup>"
        )

    else:
        tolerance_text = ""

    title = (
        f"{gantry} - {device} - "
        f"{', '.join(str(e) for e in energies)} MeV - GA {gantry_angle}°"
        f" - {plot_title}"
        f"{tolerance_text}"
    )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    fig.update_layout(
        title=title,
        height=cfg.TIME_SERIES_HEIGHT,
        template=cfg.PLOT_TEMPLATE,

        legend_title_text="Energy (MeV) | Spot",

        legend=cfg.PLOTLY_LEGEND,

        margin=cfg.TIME_SERIES_MARGIN
    )

    fig.update_xaxes(
        title_text="Date",
        showgrid=cfg.SHOW_GRID
    )

    fig.update_yaxes(
        title_text=y_axis_name,
        showgrid=cfg.SHOW_GRID
    )

    return fig



# 4. Physical spot matrix (from attachment 1)
def plotly_spot_matrix(
    df,
    option,
    parameter,
    gantry,
    device,
    energy=None,              # None / single value / list
    gantry_angle=None,        # None / single value / list
    n_months=12,
    ref_df=None,
    ref_source="TPS",
    tol_frac=cfg.FWHM_TOL_FRAC
):
    """
    Plot time-series data in the physical spot-position matrix.

    Parameters
    ----------
    df : DataFrame

    option : str
        "fwhm" | "spot_symmetry"

    parameter : str
        "hor" | "vert" | "bltr" | "tlbr"
        "ave" is also available for FWHM.

    gantry : str

    device : str
        "XRV-3000" | "XRV-4000"

    energy :
        None, single value, or list of values.

    gantry_angle :
        None, single value, or list of values.

    n_months : int

    ref_df : DataFrame or None

    ref_source : str

    tol_frac : float
        e.g. 0.10 = ±10%

    Returns
    -------
    fig
        Plotly figure.
    """

    # Input df has already been filtered in filters.filter_qa_data().
    selected_df = df.copy()

    if selected_df.empty:
        print("No data after filtering.")
        return None

    # Standardise spot labels
    selected_df["Spot"] = (
        selected_df["Spot"]
        .astype(str)
        .str.strip()
    )

    # ------------------------------------------------------------------
    # Define data according to option
    # ------------------------------------------------------------------

    if option == "fwhm":

        base_cols = list(cfg.FWHM_ORIENTATIONS.values())

        selected_df["ave_fwhm"] = (
            selected_df[base_cols]
            .mean(axis=1)
        )

        parameter_map = dict(zip(("hor", "vert", "bltr", "tlbr", "ave"),
                                 (*cfg.FWHM_ORIENTATIONS.values(), "ave_fwhm")))

        parameter_names = {
            "hor": "Horizontal FWHM (mm)",
            "vert": "Vertical FWHM (mm)",
            "bltr": "BLTR FWHM (mm)",
            "tlbr": "TLBR FWHM (mm)",
            "ave": "Average FWHM (mm)"
        }

    elif option == "spot_symmetry":

        required_cols = [
            "hor_rt_gradient",
            "hor_lt_gradient",
            "vert_rt_gradient",
            "vert_lt_gradient",
            "bltr_rt_gradient",
            "bltr_lt_gradient",
            "tlbr_rt_gradient",
            "tlbr_lt_gradient"
        ]

        missing_cols = [
            col
            for col in required_cols
            if col not in selected_df.columns
        ]

        if missing_cols:
            raise ValueError(
                "Missing columns required for spot symmetry: "
                f"{missing_cols}"
            )

        # Calculate gradient ratios
        selected_df["gr_hor"] = (
            selected_df["hor_rt_gradient"]
            / selected_df["hor_lt_gradient"]
        )

        selected_df["gr_vert"] = (
            selected_df["vert_rt_gradient"]
            / selected_df["vert_lt_gradient"]
        )

        selected_df["gr_bltr"] = (
            selected_df["bltr_rt_gradient"]
            / selected_df["bltr_lt_gradient"]
        )

        selected_df["gr_tlbr"] = (
            selected_df["tlbr_rt_gradient"]
            / selected_df["tlbr_lt_gradient"]
        )

        parameter_map = dict(zip(("hor", "vert", "bltr", "tlbr"),
                                 cfg.GR_ORIENTATIONS.values()))

        parameter_names = {
            "hor": "Horizontal Gradient Ratio (RT/LT)",
            "vert": "Vertical Gradient Ratio (RT/LT)",
            "bltr": "BLTR Gradient Ratio (RT/LT)",
            "tlbr": "TLBR Gradient Ratio (RT/LT)"
        }

    else:
        raise ValueError(
            "option must be 'fwhm' or 'spot_symmetry'"
        )

    # ------------------------------------------------------------------
    # Validate selected parameter
    # ------------------------------------------------------------------

    if parameter not in parameter_map:
        raise ValueError(
            f"For option='{option}', parameter must be one of "
            f"{list(parameter_map.keys())}"
        )

    plot_col = parameter_map[parameter]
    y_axis_name = parameter_names[parameter]

    # ------------------------------------------------------------------
    # Energy colours and GA symbols
    # ------------------------------------------------------------------

    energies = sorted(
        selected_df["Energy"]
        .dropna()
        .unique()
    )

    gantry_angles = sorted(
        selected_df["Gantry Angle"]
        .dropna()
        .unique()
    )

    energy_colors = cfg.colour_map(energies, cfg.ENERGY_COLOURS)

    ga_symbols = cfg.GANTRY_SYMBOLS

    # ------------------------------------------------------------------
    # Physical spot layout
    # ------------------------------------------------------------------

    spot_grid = cfg.SPOT_GRIDS.get(str(device).strip().upper())
    if spot_grid is None:
        raise ValueError(f"Unknown spot grid device: {device}")

    n_rows = len(spot_grid)
    n_cols = len(spot_grid[0])

    spot_order = [
        spot
        for row in spot_grid
        for spot in row
    ]

    spot_pos = {
        spot_grid[r][c]: (r + 1, c + 1)
        for r in range(n_rows)
        for c in range(n_cols)
    }

    # ------------------------------------------------------------------
    # Create subplot matrix
    # ------------------------------------------------------------------

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=spot_order,
        shared_xaxes=True,
        shared_yaxes=True,
        vertical_spacing=cfg.SUBPLOT_VERTICAL_SPACING[n_rows],
        horizontal_spacing=cfg.SUBPLOT_HORIZONTAL_SPACING
    )

    legend_done = set()

    x_min = selected_df["ADate"].min()
    x_max = selected_df["ADate"].max()

    # ------------------------------------------------------------------
    # Add traces
    # ------------------------------------------------------------------

    for e in energies:

        for ga in gantry_angles:

            sub = selected_df[
                (selected_df["Energy"] == e) &
                (selected_df["Gantry Angle"] == ga)
            ].copy()

            if sub.empty:
                continue

            color = energy_colors[e]
            symbol = ga_symbols.get(ga, cfg.UNKNOWN_GA_SYMBOL)

            combo_key = (e, ga)

            legend_group = f"E{e}_GA{ga}"
            legend_name = f"{e} | {ga}°"

            # ----------------------------------------------------------
            # Determine FWHM tolerance reference
            # ----------------------------------------------------------

            tol_center = None

            if option == "fwhm" and ref_df is not None:

                if str(ref_source).strip().upper() == "TPS":

                    ref_src = cfg.TPS_REF_SOURCE
                    ref_ga = cfg.TPS_REF_GA

                else:

                    ref_src = ref_source
                    ref_ga = ga

                ref = ref_df[
                    (
                        ref_df["source"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        ==
                        str(ref_src)
                        .strip()
                        .upper()
                    )
                    &
                    (
                        pd.to_numeric(
                            ref_df["gantry"],
                            errors="coerce"
                        )
                        == ref_ga
                    )
                    &
                    (
                        pd.to_numeric(
                            ref_df["energy"],
                            errors="coerce"
                        )
                        == e
                    )
                ]

                if not ref.empty:

                    r = ref.iloc[0]

                    x_sigma = float(r["x_stddev"])
                    y_sigma = float(r["y_stddev"])

                    hor_center = (
                        x_sigma
                        * cfg.FWHM_FACTOR
                    )

                    vert_center = (
                        y_sigma
                        * cfg.FWHM_FACTOR
                    )

                    ave_center = (
                        hor_center
                        + vert_center
                    ) / 2.0

                    if parameter == "hor":
                        tol_center = hor_center

                    elif parameter == "vert":
                        tol_center = vert_center

                    else:
                        tol_center = ave_center

            # ----------------------------------------------------------
            # Add each physical spot
            # ----------------------------------------------------------

            for spot in spot_order:

                row, col = spot_pos[spot]

                sub_spot = (
                    sub[sub["Spot"] == spot]
                    .sort_values("ADate")
                )

                # ------------------------------------------------------
                # FWHM tolerance lines
                # ------------------------------------------------------

                if tol_center is not None:

                    y_hi = (
                        tol_center
                        * (1 + tol_frac)
                    )

                    y_lo = (
                        tol_center
                        * (1 - tol_frac)
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=[x_min, x_max],
                            y=[y_hi, y_hi],
                            mode="lines",
                            line=dict(
                                color=color,
                                width=cfg.TRACE_LINE_WIDTH,
                                dash=cfg.TOLERANCE_DASH
                            ),
                            legendgroup=legend_group,
                            showlegend=False,
                            hoverinfo="skip"
                        ),
                        row=row,
                        col=col
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=[x_min, x_max],
                            y=[y_lo, y_lo],
                            mode="lines",
                            line=dict(
                                color=color,
                                width=cfg.TRACE_LINE_WIDTH,
                                dash=cfg.TOLERANCE_DASH
                            ),
                            legendgroup=legend_group,
                            showlegend=False,
                            hoverinfo="skip"
                        ),
                        row=row,
                        col=col
                    )

                if sub_spot.empty:
                    continue

                showlegend = (
                    combo_key not in legend_done
                )

                fig.add_trace(
                    go.Scatter(
                        x=sub_spot["ADate"],
                        y=sub_spot[plot_col],

                        mode="lines+markers",

                        name=legend_name,
                        legendgroup=legend_group,
                        showlegend=showlegend,

                        line=dict(
                            color=color,
                            width=cfg.TRACE_LINE_WIDTH
                        ),

                        marker=dict(
                            symbol=symbol,
                            size=cfg.MARKER_SIZE,
                            color=color,
                            opacity=cfg.MATRIX_MARKER_OPACITY,
                            line=dict(width=cfg.MARKER_OUTLINE_WIDTH)
                        ),

                        hovertemplate=(
                            f"Spot={spot}<br>"
                            f"Energy={e} MeV<br>"
                            f"GA={ga}°<br>"
                            "Date=%{x|%Y-%m-%d}<br>"
                            f"{y_axis_name}=%{{y:.3f}}"
                            "<extra></extra>"
                        )
                    ),
                    row=row,
                    col=col
                )


                legend_done.add(combo_key)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    fig.update_layout(

        height=cfg.MATRIX_HEIGHT[n_rows],

        autosize=True,

        margin=cfg.MATRIX_MARGIN,

        template=cfg.PLOT_TEMPLATE,

        title=dict(
            text=(
                f"{gantry} {device} — "
                f"{y_axis_name} "
                f"by spot location"
            ),
            x=0.02,
            y=0.98,
            xanchor="left"
        ),

        legend_title_text="Energy | GA",

        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
            groupclick="togglegroup",
            font=dict(size=cfg.LEGEND_FONT_SIZE)
        ),


    )

    # ------------------------------------------------------------------
    # Shared axes
    # ------------------------------------------------------------------

    fig.update_xaxes(
        showgrid=cfg.SHOW_GRID
    )

    fig.update_yaxes(
        showgrid=cfg.SHOW_GRID
    )

    # One shared y-axis label for the whole figure
    fig.add_annotation(
        text=y_axis_name,
        x=-0.045,
        y=0.5,
        xref="paper",
        yref="paper",
        textangle=-90,
        showarrow=False,
        font=dict(size=cfg.AXIS_LABEL_FONT_SIZE)
    )

    return fig
