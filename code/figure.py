import pandas as pd
import seaborn as sns

from matplotlib.colors import to_hex

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================
# Plotting function
# ==================

FWHM_FACTOR = 2.3548200450309493

def get_hls_palette_hex(n_colors):
    """
    Return seaborn HLS colours as hex strings for Plotly.
    """
    return [to_hex(c) for c in sns.color_palette("hls", n_colors=n_colors)]


def plotly_fwhm_spot_matrix(df,
                            gantry, device, energy=None, gantry_angle=None, n_months=12, fwhm_col="hor_fwhm",
                            ref_df=None, ref_source="TPS", tol_frac=0.10, show=False):
    """
    Plot FWHM measurements by spot position.

    The output is a Plotly subplot matrix:
    - one subplot per spot location
    - colour represents energy
    - marker symbol represents gantry angle
    - optional dashed lines represent reference tolerance limits
    """

    start_date = pd.Timestamp.today() - pd.DateOffset(months=n_months)

    base_cols = ["hor_fwhm", "vert_fwhm", "bltr_fwhm", "tlbr_fwhm"]
    allowed_single = base_cols + ["ave_fwhm"]

    if fwhm_col not in allowed_single:
        raise ValueError(f"fwhm_col must be one of {allowed_single}")

    df = df.copy()
    df["ADate"] = pd.to_datetime(df["ADate"], errors="coerce")

    sel = df[
        (df["MachineName"] == gantry) &
        (df["Device"] == device) &
        (df["ADate"] >= start_date)
    ].copy()

    if energy is not None:
        if not isinstance(energy, (list, tuple, set)):
            energy = [energy]
        sel = sel[sel["Energy"].isin(energy)].copy()

    if gantry_angle is not None:
        if not isinstance(gantry_angle, (list, tuple, set)):
            gantry_angle = [gantry_angle]
        sel = sel[sel["Gantry Angle"].isin(gantry_angle)].copy()

    if sel.empty:
        return None

    sel["Spot"] = sel["Spot"].astype(str).str.strip()

    # Average measured FWHM across the four measured directions.
    sel["ave_fwhm"] = sel[base_cols].mean(axis=1)

    energies = sorted(sel["Energy"].dropna().unique())
    gantry_angles = sorted(sel["Gantry Angle"].dropna().unique())

    energy_colors = dict(zip(energies, get_hls_palette_hex(len(energies))))

    # The measurement uses these four gantry angles.
    ga_symbols = {
        0: "circle",
        90: "square",
        180: "diamond",
        270: "x",
    }

    # Define the spot layout for each device type.
    if str(device).strip().upper() == "XRV-3000":
        spot_grid = [
            ["Top-Left", "Top-Centre", "Top-Right"],
            ["Left", "Centre", "Right"],
            ["Bottom-Left", "Bottom-Centre", "Bottom-Right"],
        ]
    else:
        spot_grid = [
            ["Top-Top-Left", "Top-Top-Centre", "Top-Top-Right"],
            ["Top-Left", "Top-Centre", "Top-Right"],
            ["Left", "Centre", "Right"],
            ["Bottom-Left", "Bottom-Centre", "Bottom-Right"],
            ["Bottom-Bottom-Left", "Bottom-Bottom-Centre", "Bottom-Bottom-Right"],
        ]

    n_rows = len(spot_grid)
    n_cols = len(spot_grid[0])

    spot_order = [s for row in spot_grid for s in row]

    spot_pos = {
        spot_grid[r][c]: (r + 1, c + 1)
        for r in range(n_rows)
        for c in range(n_cols)
    }

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=spot_order,
        shared_xaxes=True,
        shared_yaxes=True,
        vertical_spacing=0.06 if n_rows == 3 else 0.04,
        horizontal_spacing=0.025,
    )

    legend_done = set()

    x_min = sel["ADate"].min()
    x_max = sel["ADate"].max()

    for e in energies:
        for ga in gantry_angles:
            sub = sel[
                (sel["Energy"] == e) &
                (sel["Gantry Angle"] == ga)
            ].copy()

            if sub.empty:
                continue

            color = energy_colors[e]
            symbol = ga_symbols[ga]
            combo_key = (e, ga)
            legend_group = f"E{e}_GA{ga}"
            legend_name = f"{e} | {ga}°"

            # Determine the reference FWHM value used for tolerance lines.
            tol_center = None

            if ref_df is not None:
                # TPS reference data are stored in ref_df as source G1 at GA 90.
                if str(ref_source).strip().upper() == "TPS":
                    ref_src = "G1"
                    ref_ga = 90
                else:
                    ref_src = ref_source
                    ref_ga = ga

                ref = ref_df[
                    (
                        ref_df["source"].astype(str).str.strip().str.upper()
                        == str(ref_src).strip().upper()
                    ) &
                    (
                        pd.to_numeric(ref_df["gantry"], errors="coerce")
                        == ref_ga
                    ) &
                    (
                        pd.to_numeric(ref_df["energy"], errors="coerce")
                        == e
                    )
                ]

                if not ref.empty:
                    r = ref.iloc[0]

                    x_sigma = float(r["x_stddev"])
                    y_sigma = float(r["y_stddev"])

                    hor_center = x_sigma * FWHM_FACTOR
                    vert_center = y_sigma * FWHM_FACTOR

                    # For diagonal and average FWHM, use the mean of horizontal and vertical reference FWHM.
                    ave_center = (hor_center + vert_center) / 2.0

                    if fwhm_col == "hor_fwhm":
                        tol_center = hor_center
                    elif fwhm_col == "vert_fwhm":
                        tol_center = vert_center
                    else:
                        tol_center = ave_center

            for spot in spot_order:
                row, col = spot_pos[spot]
                sub_spot = sub[sub["Spot"] == spot].sort_values("ADate")

                # Keep tolerance lines visible even if the spot has no measured data.
                if tol_center is not None:
                    y_hi = tol_center * (1 + tol_frac)
                    y_lo = tol_center * (1 - tol_frac)

                    fig.add_trace(
                        go.Scatter(
                            x=[x_min, x_max],
                            y=[y_hi, y_hi],
                            mode="lines",
                            line=dict(color=color, width=1, dash="dash"),
                            legendgroup=legend_group,
                            showlegend=False,
                            hoverinfo="skip",
                        ),
                        row=row,
                        col=col,
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=[x_min, x_max],
                            y=[y_lo, y_lo],
                            mode="lines",
                            line=dict(color=color, width=1, dash="dash"),
                            legendgroup=legend_group,
                            showlegend=False,
                            hoverinfo="skip",
                        ),
                        row=row,
                        col=col,
                    )

                if sub_spot.empty:
                    continue

                showlegend = combo_key not in legend_done

                fig.add_trace(
                    go.Scatter(
                        x=sub_spot["ADate"],
                        y=sub_spot[fwhm_col],
                        mode="lines+markers",
                        name=legend_name,
                        legendgroup=legend_group,
                        showlegend=showlegend,
                        line=dict(color=color, width=1),
                        marker=dict(
                            symbol=symbol,
                            size=12,
                            color=color,
                            opacity=0.65,
                            line=dict(width=2),
                        ),
                        hovertemplate=(
                            f"Spot={spot}<br>"
                            f"Energy={e} MeV<br>"
                            f"GA={ga}<br>"
                            "Date=%{x|%Y-%m-%d}<br>"
                            f"{fwhm_col}=%{{y:.2f}}<extra></extra>"
                        ),
                    ),
                    row=row,
                    col=col,
                )

                legend_done.add(combo_key)

    # No fixed width here. Dash controls the figure width through dcc.Graph.
    fig.update_layout(
        autosize=True,
        height=820 if n_rows == 3 else 1080,
        margin=dict(l=35, r=205, t=95, b=55),
        template="plotly_white",
        title=dict(
            text=f"{gantry} {device} — {fwhm_col} by spot location",
            x=0.02,
            y=0.98,
            xanchor="left",
        ),
        legend_title_text="Energy | GA",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.02,
            groupclick="togglegroup",
            font=dict(size=10),
        ),
    )

    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)

    if show:
        fig.show()

    return fig
