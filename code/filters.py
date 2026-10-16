"""Selector dependencies and measurement filtering for Spot Grid QA.

Only this module restricts the input QA rows based on user selections.
Plotting functions receive an already-filtered DataFrame. Filtering rows
by physical Spot *within* a subplot remains part of rendering the figure.
"""
import pandas as pd
import constants as cfg


def choices(values, labels=None):
    """Convert actual workbook values into Dash dropdown options."""
    values = [v.item() if hasattr(v, "item") else v for v in values if pd.notna(v)]
    return [{"label": (labels.get(v, str(v)) if labels else str(v)), "value": v}
            for v in values]




def gantry_choices(gantries):
    """Short button labels from available gantries, without fixing their count."""
    return [{"label": f"G{str(g).rsplit(' ', 1)[-1]}" if str(g).startswith("Gantry ")
             else str(g), "value": g} for g in gantries]


def device_choices(devices):
    """Segment labels are derived from the workbook, not hardcoded device options."""
    return [{"label": (str(d).removeprefix("XRV-") if str(d).startswith("XRV-")
                       else str(d)), "value": d} for d in devices]


def valid_plots(qa_type):
    return choices(cfg.SUPPORTED_PLOTS.get(qa_type, ()), cfg.PLOT_TYPES)


def required_parameters(qa_type, plot_type):
    if qa_type not in cfg.SUPPORTED_PLOTS or plot_type not in cfg.SUPPORTED_PLOTS[qa_type]:
        return []
    if plot_type == "time":
        return []  # Four directions are drawn together, no separate parameter.
    if plot_type == "matrix":
        return list(cfg.MATRIX_PARAMETERS.get(qa_type, {}))
    return list(cfg.PARAMETERS.get(qa_type, ()))


def parameter_column(qa_type, plot_type, parameter):
    """Translate shortened matrix parameters to workbook column names."""
    if plot_type != "matrix":
        return parameter
    if qa_type == "fwhm":
        return "ave_fwhm" if parameter == "ave" else f"{parameter}_fwhm"
    if qa_type == "spot_symmetry":
        return f"gr_{parameter}"
    return None


def parameter_options(df, qa_type, plot_type, *, gantry=None, device=None):
    """Return only supported parameters with real non-null measurements."""
    relevant = df
    if gantry is not None:
        relevant = relevant.loc[relevant["MachineName"].eq(gantry)]
    if device is not None:
        relevant = relevant.loc[relevant["Device"].eq(device)]
    result = []
    for param in required_parameters(qa_type, plot_type):
        col = parameter_column(qa_type, plot_type, param)
        if col not in relevant or not relevant[col].notna().any():
            continue
        label = (cfg.MATRIX_PARAMETERS[qa_type][param] if plot_type == "matrix"
                 else cfg.PARAMETER_LABELS[param])
        result.append({"label": label, "value": param})
    return result


def plot_is_available(df, qa_type, plot_type, parameter):
    if plot_type not in cfg.SUPPORTED_PLOTS.get(qa_type, ()):
        return False
    if plot_type == "time":
        cols = (list(cfg.FWHM_ORIENTATIONS.values()) if qa_type == "fwhm" else
                list(cfg.GR_ORIENTATIONS.values()))
        return all(c in df and df[c].notna().any() for c in cols)
    return parameter in {o["value"] for o in parameter_options(df, qa_type, plot_type)}


def existing_values(df, column, gantry=None, device=None, energies=None):
    """Only offer values that actually exist for the upstream selections."""
    sel = df
    if gantry is not None:
        sel = sel.loc[sel["MachineName"].eq(gantry)]
    if device is not None:
        sel = sel.loc[sel["Device"].eq(device)]
    if energies is not None:
        if not isinstance(energies, (list, tuple, set)):
            energies = [energies]
        sel = sel.loc[sel["Energy"].isin(energies)]
    return sorted(sel[column].dropna().unique().tolist())


def select_preferred(values, current=None, preferred=None, multi=False):
    """Preserve valid selections; otherwise choose an actual available value."""
    if not values:
        return [] if multi else None
    if multi:
        if isinstance(current, (list, tuple, set)):
            matching = [v for v in current if v in values]
            if matching:
                return matching
        return values
    if current in values:
        return current
    if preferred in values:
        return preferred
    return values[0]


def filter_qa_data(df, *, gantry, device, months=None, energies=None,
                   gantry_angles=None, start_date=None, end_date=None):
    """Select real QA measurements, including an inclusive custom end date.

    Presets use the previous N calendar months; a custom range is inclusive of
    both days, including measurements with an afternoon/evening timestamp.
    No date filtering is performed later in the plotting functions.
    """
    if not gantry or not device:
        return df.iloc[0:0].copy()
    mask = df["MachineName"].eq(gantry) & df["Device"].eq(device)

    if start_date is not None or end_date is not None:
        start = pd.to_datetime(start_date, errors="coerce")
        end = pd.to_datetime(end_date, errors="coerce")
        if pd.isna(start) or pd.isna(end) or start > end:
            return df.iloc[0:0].copy()
        mask &= df["ADate"].ge(start) & df["ADate"].lt(end.normalize() + pd.Timedelta(days=1))
    else:
        try:
            months = int(months)
        except (TypeError, ValueError):
            months = cfg.DEFAULT_MONTHS
        if months < 1 or months > 60:
            months = cfg.DEFAULT_MONTHS
        start = pd.Timestamp.today() - pd.DateOffset(months=months)
        mask &= df["ADate"].ge(start)

    if energies is not None:
        energies = energies if isinstance(energies, (list, tuple, set)) else [energies]
        mask &= df["Energy"].isin(energies)
    if gantry_angles is not None:
        gantry_angles = (gantry_angles if isinstance(gantry_angles, (list, tuple, set))
                         else [gantry_angles])
        mask &= df["Gantry Angle"].isin(gantry_angles)
    return df.loc[mask].copy()
