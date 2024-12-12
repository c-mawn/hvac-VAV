import pandas as pd
import util
import os


def get_data(roomnumber: str) -> pd.DataFrame:
    """
    Combine BAS and outdoor air databases into one.

    Args:
        roomnumber (str): Id of room as given in combined_milas_hall folder (ex: A3-70)

    Returns (pd.DataFrame) containing BAS data for room given merged with outside stats
    """
    bas_path = f"../data/occupancy_data/Flo2.3-{roomnumber}.csv"
    bas_df = util.timestamp_split(bas_path)

    oa_path = f"../data/oa_data.csv"
    oa_df = util.timestamp_split(oa_path)

    return bas_df.merge(oa_df, on="datetime", how="left")


def get_full_data_rooms():
    df_list = []
    list_files = os.listdir("../data/occupancy_data")

    for f in list_files:
        this_room = f[f.index("A") : f.index(".csv")]
        df_list.append(this_room)
    return df_list
