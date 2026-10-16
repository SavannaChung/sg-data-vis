"""Central configuration for the Spot Grid QA Dash application.

Styling belongs here. QA rules and data assumptions are also explicit here;
these must be checked/approved before clinical use.
"""
from pathlib import Path
from plotly.colors import qualitative

# Paths: Python scripts are assumed to live in <repository>/code/.
CODE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CODE_DIR.parent if CODE_DIR.name == "code" else CODE_DIR
DATA_DIR = PROJECT_ROOT / "data" / "xlsx_exported_from_access"
QA_DATA_PATH = DATA_DIR / "SpotPositionResults.xlsx"
REF_DATA_PATH = DATA_DIR / "ref" / "Ref_RS0_Dist0.xlsx"
BASELINE_REF_PATH = DATA_DIR / "ref" / "gantry_specific_baseline_2026_05_29.xlsx"

# Scientific/calculation settings inherited from supplied functions.
FWHM_FACTOR = 2.3548200450309493    # Gaussian sigma -> FWHM
DEFAULT_MONTHS = 12
FWHM_TOL_FRAC = 0.10
SPOT_POSITION_TOLERANCES = {"abs_xpos": 2.0, "abs_ypos": 2.0,
                            "rel_xpos": 1.0, "rel_ypos": 1.0}  # mm
TPS_REF_GANTRY = 1   # teammate's convention: G1, GA 90
TPS_REF_GA = 90
TPS_REF_SOURCE = f"G{TPS_REF_GANTRY}"

# Nominal spot positions in millimetres, not measured coordinates.
# XRV-4000: transcribed from pred_xrv4000 in the original QA notebook.
# XRV-3000: inferred as the shared central 3x3 grid (same spot names).
# Confirm nominal geometry against the device QA procedure before clinical use.
# Values are (X, Y); upper rows have negative Y in the notebook.
EXPECTED_SPOT_COORDS = {
    "XRV-3000": {
        "Top-Left": (-125, -125),
        "Top-Centre": (0, -125),
        "Top-Right": (125, -125),
        "Left": (-125, 0),
        "Centre": (0, 0),
        "Right": (125, 0),
        "Bottom-Left": (-125, 125),
        "Bottom-Centre": (0, 125),
        "Bottom-Right": (125, 125),
    },
    "XRV-4000": {
        "Top-Top-Left": (-125, -175),
        "Top-Top-Centre": (0, -175),
        "Top-Top-Right": (125, -175),
        "Top-Left": (-125, -125),
        "Top-Centre": (0, -125),
        "Top-Right": (125, -125),
        "Left": (-125, 0),
        "Centre": (0, 0),
        "Right": (125, 0),
        "Bottom-Left": (-125, 125),
        "Bottom-Centre": (0, 125),
        "Bottom-Right": (125, 125),
        "Bottom-Bottom-Left": (-125, 175),
        "Bottom-Bottom-Centre": (0, 175),
        "Bottom-Bottom-Right": (125, 175),
    },
}

QA_TYPES = {"spot_position": "Spot position", "fwhm": "FWHM (spot size)",
            "spot_symmetry": "Spot symmetry (gradient ratio)"}
PARAMETERS = {
    "spot_position": ["abs_xpos", "abs_ypos", "rel_xpos", "rel_ypos"],
    "fwhm": ["hor_fwhm", "vert_fwhm", "bltr_fwhm", "tlbr_fwhm", "ave_fwhm"],
    "spot_symmetry": ["gr_hor", "gr_vert", "gr_bltr", "gr_tlbr"],
}
PARAMETER_LABELS = {
    "abs_xpos": "Absolute X Position (mm)", "abs_ypos": "Absolute Y Position (mm)",
    "rel_xpos": "Relative X Position (mm)", "rel_ypos": "Relative Y Position (mm)",
    "hor_fwhm": "Horizontal FWHM (mm)", "vert_fwhm": "Vertical FWHM (mm)",
    "bltr_fwhm": "BLTR FWHM (mm)", "tlbr_fwhm": "TLBR FWHM (mm)",
    "ave_fwhm": "Average FWHM (mm)",
    "gr_hor": "Horizontal Gradient Ratio (RT/LT)",
    "gr_vert": "Vertical Gradient Ratio (RT/LT)",
    "gr_bltr": "BLTR Gradient Ratio (RT/LT)",
    "gr_tlbr": "TLBR Gradient Ratio (RT/LT)",
}
MATRIX_PARAMETERS = {
    "fwhm": {"hor": "Horizontal", "vert": "Vertical", "bltr": "BLTR",
             "tlbr": "TLBR", "ave": "Average"},
    "spot_symmetry": {"hor": "Horizontal", "vert": "Vertical", "bltr": "BLTR",
                      "tlbr": "TLBR"},
}
ORIENTATIONS = {"Horizontal": (1, 1), "Vertical": (1, 2), "BLTR": (2, 1), "TLBR": (2, 2)}
FWHM_ORIENTATIONS = {"Horizontal": "hor_fwhm", "Vertical": "vert_fwhm",
                     "BLTR": "bltr_fwhm", "TLBR": "tlbr_fwhm"}
GR_ORIENTATIONS = {"Horizontal": "gr_hor", "Vertical": "gr_vert",
                   "BLTR": "gr_bltr", "TLBR": "gr_tlbr"}
GRADIENT_PAIRS = {"gr_hor": ("hor_rt_gradient", "hor_lt_gradient"),
                  "gr_vert": ("vert_rt_gradient", "vert_lt_gradient"),
                  "gr_bltr": ("bltr_rt_gradient", "bltr_lt_gradient"),
                  "gr_tlbr": ("tlbr_rt_gradient", "tlbr_lt_gradient")}
SPOT_GRIDS = {
    "XRV-3000": [["Top-Left", "Top-Centre", "Top-Right"],
                 ["Left", "Centre", "Right"],
                 ["Bottom-Left", "Bottom-Centre", "Bottom-Right"]],
    "XRV-4000": [["Top-Top-Left", "Top-Top-Centre", "Top-Top-Right"],
                 ["Top-Left", "Top-Centre", "Top-Right"],
                 ["Left", "Centre", "Right"],
                 ["Bottom-Left", "Bottom-Centre", "Bottom-Right"],
                 ["Bottom-Bottom-Left", "Bottom-Bottom-Centre", "Bottom-Bottom-Right"]],
}

# Stable visual conventions across plots (change here, not in plotting functions).
PLOT_TEMPLATE = "plotly_white"
LEGEND_FONT_SIZE = 11
CONTROL_LABEL_FONT_SIZE = 12
AXIS_LABEL_FONT_SIZE = 14
DISCRETE_COLOURS = list(qualitative.Plotly)
ENERGY_COLOURS = {70: DISCRETE_COLOURS[0], 100: DISCRETE_COLOURS[1],
                  150: DISCRETE_COLOURS[2], 200: DISCRETE_COLOURS[3],
                  240: DISCRETE_COLOURS[4]}
GANTRY_ANGLE_COLOURS = {0: DISCRETE_COLOURS[0], 90: DISCRETE_COLOURS[1],
                        180: DISCRETE_COLOURS[2], 270: DISCRETE_COLOURS[3]}
UNKNOWN_GA_SYMBOL = "circle"
GANTRY_SYMBOLS = {0: "circle", 90: "square", 180: "diamond", 270: "x"}
SPOT_SYMBOL_CYCLE = ["circle", "square", "diamond", "cross", "x",
                     "triangle-up", "triangle-down", "triangle-left",
                     "triangle-right", "pentagon", "hexagon", "star"]
ALL_SPOTS = list(dict.fromkeys(s for grid in SPOT_GRIDS.values() for row in grid for s in row))
SPOT_COLOURS = {s: DISCRETE_COLOURS[i % len(DISCRETE_COLOURS)]
                for i, s in enumerate(ALL_SPOTS)}
SPOT_SYMBOLS = {s: SPOT_SYMBOL_CYCLE[i % len(SPOT_SYMBOL_CYCLE)]
                for i, s in enumerate(ALL_SPOTS)}
MARKER_SIZE = 12
MARKER_OPACITY = 0.8
MATRIX_MARKER_OPACITY = 0.65
MARKER_OUTLINE_WIDTH = 2
TRACE_LINE_WIDTH = 1
TOLERANCE_COLOR = "grey"
TOLERANCE_DASH = "dash"
TOLERANCE_WIDTH = 2
SHOW_GRID = True
PLOT_HEIGHT = 500
TIME_SERIES_HEIGHT = 700
MATRIX_HEIGHT = {3: 820, 5: 1080}
PLOTLY_LEGEND = dict(orientation="v", x=1.02, xanchor="left", y=1, yanchor="top")
MATRIX_MARGIN = dict(l=35, r=205, t=100, b=55)
TIME_SERIES_MARGIN = dict(l=70, r=180, t=100, b=60)
SUBPLOT_HORIZONTAL_SPACING = 0.025
SUBPLOT_VERTICAL_SPACING = {3: 0.06, 5: 0.04}
TWO_BY_TWO_SPACING = dict(horizontal_spacing=0.08, vertical_spacing=0.13)

# Dash styling.
APP_STYLE_OPEN = dict(display="grid", gridTemplateColumns="260px minmax(0,1fr)",
                      height="100vh", maxHeight="100vh", width="100%",
                      minHeight="0", fontFamily="Arial,sans-serif", overflow="hidden")
APP_STYLE_COLLAPSED = dict(APP_STYLE_OPEN, gridTemplateColumns="50px minmax(0,1fr)")
# The sidebar and chart region scroll independently inside the fixed-height app shell.
# A sticky sidebar inside a document-length grid can finish above the page bottom.
SIDEBAR_STYLE_OPEN = dict(width="100%", minWidth="0", boxSizing="border-box",
                          padding="12px", backgroundColor="#111824", color="#edf3fb",
                          height="100vh", minHeight="0", overflowY="auto",
                          overscrollBehaviorY="contain", overflowX="hidden",
                          scrollbarWidth="thin", borderRight="1px solid #26354b")
SIDEBAR_STYLE_COLLAPSED = dict(SIDEBAR_STYLE_OPEN, padding="12px 7px", overflowY="hidden")
MAIN_STYLE = dict(padding="6px 10px", backgroundColor="#f7f9fc",
                  height="100vh", minHeight="0", minWidth="0", overflowY="auto",
                  overscrollBehaviorY="contain", overflowX="hidden", boxSizing="border-box")
LABEL_STYLE = dict(fontWeight="600", fontSize="12px", marginTop="9px",
                   marginBottom="4px", display="block")
DROPDOWN_STYLE = dict(width="100%", minWidth="0", fontSize="12px", color="#111")
INPUT_STYLE = dict(width="100%", boxSizing="border-box", padding="8px", borderRadius="8px",
                   border="1px solid #34465f", fontSize="12px")
PLOT_CARD_STYLE = dict(backgroundColor="white", border="1px solid #d8dee9",
                       borderRadius="12px", padding="6px", overflow="hidden",
                       minWidth="0", width="100%", maxWidth="1450px", boxSizing="border-box")
GRAPH_STYLE = dict(height="78vh", minHeight="580px", width="100%", minWidth="0")


def colour_map(values, mapping):
    """Use stable configured colours; allocate fallback colours for new categories."""
    found = dict(mapping)
    for value in sorted(values, key=str):
        if value not in found:
            found[value] = DISCRETE_COLOURS[len(found) % len(DISCRETE_COLOURS)]
    return {value: found[value] for value in values}


def symbol_map(values, mapping):
    found = dict(mapping)
    for value in sorted(values, key=str):
        if value not in found:
            found[value] = SPOT_SYMBOL_CYCLE[len(found) % len(SPOT_SYMBOL_CYCLE)]
    return {value: found[value] for value in values}

# Dashboard selector hierarchy: QA type -> supported plot types -> parameters.
# Actual available gantries/devices/energies/angles are read from the Excel data
# by filters.py, rather than being hardcoded here.
PLOT_TYPES = {
    "average": "Average by energy / GA",
    "individual": "Individual spots",
    "time": "4-orientation time series",
    "matrix": "Spot matrix",
}
SUPPORTED_PLOTS = {
    "spot_position": ("average", "individual"),
    "fwhm": ("average", "individual", "time", "matrix"),
    "spot_symmetry": ("average", "individual", "time", "matrix"),
}
PLOT_DESCRIPTIONS = {
    "average": "Averaged QA measurements by date and energy / gantry angle.",
    "individual": "Each physical spot shown across dates for a single energy and gantry angle.",
    "time": "Four FWHM / symmetry orientations for a single energy and gantry angle.",
    "matrix": "Physical spot-grid subplots, with selectable energies and gantry angles.",
}

# Graphs are standalone panels, not children of Dash tabs.
PLOT_PANEL_STYLE = dict(PLOT_CARD_STYLE, overflow="visible")
GRAPH_PANEL_HIDDEN = {"display": "none"}
GRAPH_PANEL_VISIBLE = {"display": "block"}
SIDEBAR_GROUP_VISIBLE = {"display": "block"}
SIDEBAR_GROUP_HIDDEN = {"display": "none"}
