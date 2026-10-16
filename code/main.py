"""Dash entry point. Excel-export loading is temporary; database.py is deferred.

From the repository root run: python code/main.py
"""
import warnings
import pandas as pd
from dash import Dash

import constants as cfg
import layout as ui
from callbacks import register_callbacks


REQUIRED_BASE_COLUMNS = {"ADate", "MachineName", "Device", "Energy", "Gantry Angle", "Spot"}


def load_excel_data():
    if not cfg.QA_DATA_PATH.is_file():
        raise FileNotFoundError(f"Cannot find QA workbook: {cfg.QA_DATA_PATH}")
    df = pd.read_excel(cfg.QA_DATA_PATH)
    missing = REQUIRED_BASE_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"QA workbook is missing columns: {sorted(missing)}")

    df["ADate"] = pd.to_datetime(df["ADate"], errors="coerce")
    for col in ("MachineName", "Device", "Spot"):
        df[col] = df[col].astype("string").str.strip()
    for col in ("Energy", "Gantry Angle"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in set(cfg.PARAMETER_LABELS) | {"x-pos", "y-pos", "px_pos", "py_pos"} | {
        x for pair in cfg.GRADIENT_PAIRS.values() for x in pair
    }:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ref_RS0_Dist0.xlsx is the sigma-reference schema expected by the
    # team's matrix and 2x2 time-series functions.
    sigma_ref_df = pd.read_excel(cfg.REF_DATA_PATH) if cfg.REF_DATA_PATH.is_file() else None
    if sigma_ref_df is not None:
        required_ref = {"source", "gantry", "energy", "x_stddev", "y_stddev"}
        if not required_ref.issubset(sigma_ref_df.columns):
            warnings.warn("Sigma reference workbook schema not compatible with team functions; tolerance lines disabled")
            sigma_ref_df = None

    # Separate direct-FWHM reference schema used in the pasted notebook cells.
    direct_ref_df = (pd.read_excel(cfg.BASELINE_REF_PATH, sheet_name="summary", usecols="A:E")
                     if cfg.BASELINE_REF_PATH.is_file() else None)
    if direct_ref_df is not None:
        needed = {"data_type", "gantry", "gantry_angle", "energy", "fwhm"}
        if not needed.issubset(direct_ref_df.columns):
            warnings.warn("Baseline FWHM workbook schema not compatible; direct reference disabled")
            direct_ref_df = None
    return df, sigma_ref_df, direct_ref_df


def prepare_qa_data(df):
    """Prepare the three team-required measurement groups without fake data.

    Position data are only computed if real expected coordinates are provided
    in the workbook or in EXPECTED_SPOT_COORDS. A Centre offset must be matched
    within the same date, gantry, device, energy and gantry angle.
    """
    df = df.copy()
    fwhm_cols = list(cfg.FWHM_ORIENTATIONS.values())
    if all(c in df.columns for c in fwhm_cols):
        df["ave_fwhm"] = df[fwhm_cols].mean(axis=1)

    for ratio_col, (rt, lt) in cfg.GRADIENT_PAIRS.items():
        if rt in df.columns and lt in df.columns:
            df[ratio_col] = (df[rt] / df[lt]).replace([float("inf"), -float("inf")], float("nan"))

    if not {"abs_xpos", "abs_ypos"}.issubset(df.columns):
        if {"px_pos", "py_pos", "x-pos", "y-pos"}.issubset(df.columns):
            df["abs_xpos"] = df["x-pos"] - df["px_pos"]
            df["abs_ypos"] = df["y-pos"] - df["py_pos"]
        elif {"x-pos", "y-pos"}.issubset(df.columns):
            # Device-specific coordinates may be filled in constants.py.
            expected = {
                (dev, spot): xy
                for dev, mapping in cfg.EXPECTED_SPOT_COORDS.items()
                for spot, xy in mapping.items()
            }
            keys = list(zip(df["Device"], df["Spot"]))
            nominal = [expected.get(key, (float("nan"), float("nan"))) for key in keys]
            df["px_pos"] = [xy[0] for xy in nominal]
            df["py_pos"] = [xy[1] for xy in nominal]
            df["abs_xpos"] = df["x-pos"] - df["px_pos"]
            df["abs_ypos"] = df["y-pos"] - df["py_pos"]

    if {"abs_xpos", "abs_ypos"}.issubset(df.columns) and not {
        "rel_xpos", "rel_ypos"}.issubset(df.columns):
        grouping = ["ADate", "MachineName", "Device", "Energy", "Gantry Angle"]
        # Unlike the pasted notebook's Date/Energy-only map, this avoids mixing
        # Centre readings from different gantries/angles/devices.
        centre = (df.loc[df["Spot"] == "Centre", grouping + ["abs_xpos", "abs_ypos"]]
                    .groupby(grouping, as_index=False)[["abs_xpos", "abs_ypos"]].mean()
                    .rename(columns={"abs_xpos": "centre_abs_xpos", "abs_ypos": "centre_abs_ypos"}))
        df = df.merge(centre, on=grouping, how="left", validate="many_to_one")
        df["rel_xpos"] = df["abs_xpos"] - df["centre_abs_xpos"]
        df["rel_ypos"] = df["abs_ypos"] - df["centre_abs_ypos"]
    return df


def create_app():
    raw_df, sigma_ref_df, direct_ref_df = load_excel_data()
    qa_df = prepare_qa_data(raw_df)
    app = Dash(__name__)
    app.title = "Spot Grid QA"
    app.layout = ui.app_layout(qa_df, sigma_ref_df, direct_ref_df)
    register_callbacks(app, qa_df, sigma_ref_df, direct_ref_df)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, port=8050, use_reloader=False)
