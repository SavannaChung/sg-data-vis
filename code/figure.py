import plotly.express as px
import seaborn as sns
from matplotlib.colors import to_hex
import pandas as pd




def plotly_spot_position(df, pos, gantry, device, energy, gantry_angle, n_months):
    """ plot spot position time series data
        df = dataframe
        gantry = "Gantry 1", "Gantry 2", 
        pos = "abs_xpos",
        device = "XRV-3000", "XRV-4000"
        energy = int,
        gantry_angle = 0,90,180,270
        n_month = int

     """
    
     # only show data from last 12 months
    start_date = pd.Timestamp.today() - pd.DateOffset(months=n_months)

    selected_df = df[(df["machinename"]==gantry) & (df["device"] == device) & (df['adate'] >= start_date) & (df["energy"] == energy) &(df["gantry angle"] == gantry_angle)]

    # set colour
    palette = sns.color_palette("deep", n_colors=df['spot'].nunique())
    palette_hex = [to_hex(c) for c in palette]


    # Plot
    fig = px.scatter(
        selected_df,
        x='adate',
        y=pos,
        symbol='spot', 
        color='spot',        # hue
         color_discrete_sequence= px.colors.qualitative.T10,
        title=f'{gantry} - absolute shift- {pos}',
        labels={'x-pos': 'X Position', 'adate': 'Date'},
        height=500
    )

    # Add tolerance bands +/- 2
    fig.add_hline(y=2, line_dash="dash", line_color="grey", annotation_text="tolerance", annotation_position="top left")
    fig.add_hline(y=-2, line_dash="dash", line_color="grey")



    # Optional: connect points by spot for clarity
    fig.update_traces(mode='markers+lines',
                    marker=dict(size=12,               # larger size
                                line=dict(width=2)),     # outline width
                    line=dict(width=1                # thinner connecting lines
                    ))

    # Show plot
    fig.show()

    
    return 