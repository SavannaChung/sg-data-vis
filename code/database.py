from pathlib import Path
import pandas as pd

# ===========
# Data paths
# ===========

PROJECT_ROOT = Path.cwd()

FWHM_DATA_PATH = PROJECT_ROOT / "data" / "xlsx_exported_from_access" / "SpotPositionResults.xlsx"

REF_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "xlsx_exported_from_access"
    / "ref"
    / "Ref_RS0_Dist0.xlsx"
)

# =============
# Data loading
# =============

def load_fwhm_data():
    """
    Use fwhm_df from the notebook if it already exists.
    Otherwise, load from the Excel file path above.
    """
    global fwhm_df

    try:
        fwhm_df
        df = fwhm_df.copy()
    except NameError:
        df = pd.read_excel(FWHM_DATA_PATH)

    df["ADate"] = pd.to_datetime(df["ADate"], errors="coerce")
    df["MachineName"] = df["MachineName"].astype(str).str.strip()
    df["Device"] = df["Device"].astype(str).str.strip()
    df["Energy"] = pd.to_numeric(df["Energy"], errors="coerce").astype("Int64")
    df["Gantry Angle"] = pd.to_numeric(df["Gantry Angle"], errors="coerce").astype("Int64")

    return df

def load_reference_data():
    """
    Use ref_df from the notebook if it already exists.
    Otherwise, load from REF_DATA_PATH if available.
    """
    global ref_df

    try:
        ref_df
        return ref_df.copy()
    except NameError:
        if REF_DATA_PATH.exists():
            return pd.read_excel(REF_DATA_PATH)
        return None
