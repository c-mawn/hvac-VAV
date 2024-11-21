import pandas as pd
import util


def get_data(roomnumber: str) -> pd.DataFrame:
    """
    Combine BAS and outdoor air databases into one.

    Args:
        roomnumber (str): Id of room as given in combined_milas_hall folder (ex: A3-70)

    Returns (pd.DataFrame) containing BAS data for room given merged with outside stats
    """
    bas_path = f"../data/combined_milas_hall/Flo2.3-{roomnumber}.csv"
    bas_df = util.timestamp_split(bas_path)

    oa_path = f"../data/oa_data.csv"
    oa_df = util.timestamp_split(oa_path)

    return bas_df.merge(oa_df, on="datetime", how="left")
