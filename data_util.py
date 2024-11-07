"""
Helper functions for data cleaning and visualization of HVAC data
"""

import pandas as pd


def timestamp_split(file_path):
    """
    Split timestamp columns into date and time columns

    Args:
        file_path: string representing the path to the csv file to be split

    Returns a pandas dataframe with new columns of "date" and "time" instead of the "timestamp"
    """
    df = pd.read_csv(file_path)
    df[["date", "time"]] = df["timestamp"].str.split(" ", n=1, expand=True)
    df.drop(columns="timestamp")
    return df
