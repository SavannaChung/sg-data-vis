import pandas as pd



import database as db
import figure as fg

database_path = r"O:\protons\Work in Progress\KC\Access\dose_lineariy_form\existing_db\_AssetsDatabase_be_current.accdb"

def main():

    df = db.fetch_db(DATABASE_DIR = database_path,table = "SpotPositionResults")

    # convert adate to datetime
    df['adate'] = pd.to_datetime(df['adate'])
    
    # Only keep useful columns
    sub_df = df[["adate",	"machinename", 	"energy", "device", "gantry angle", "spot", "x-pos", "y-pos"]].copy()

    # calculate abs shift
    pred_xrv4000 = {'Top-Top-Left': [-125, -175], 'Top-Top-Centre': [0, -175], 'Top-Top-Right': [125, -175], \
                'Top-Left': [-125, -125], 'Top-Centre':[0, -125], 'Top-Right':[125, -125], \
                'Left': [-125, 0], 'Centre':[0, 0], 'Right':[125, 0], \
                'Bottom-Left': [-125, 125], 'Bottom-Centre':[0, 125], 'Bottom-Right':[125, 125], \
                'Bottom-Bottom-Left': [-125, 175], 'Bottom-Bottom-Centre': [0, 175], 'Bottom-Bottom-Right': [125, 175]}

    sub_df['px_pos'] = sub_df['spot'].map(lambda s: pred_xrv4000[s][0] if s in pred_xrv4000 else None)
    sub_df['py_pos'] = sub_df['spot'].map(lambda s: pred_xrv4000[s][1] if s in pred_xrv4000 else None)

    sub_df['abs_xpos'] = sub_df["x-pos"] - sub_df["px_pos"]
    sub_df['abs_ypos'] = sub_df["y-pos"] - sub_df["py_pos"]


    # plot the abs shift as a function of time
    fig = fg.plotly_spot_position(sub_df, "abs_ypos", "Gantry 4", "XRV-4000", 70, 0, 24)


if __name__ == "__main__":
    main()