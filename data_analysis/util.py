"""
Helper functions for data cleaning and visualization of HVAC data
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def timestamp_split(file_path):
    """
    Split timestamp columns into date and time columns

    Args:
        file_path (str): string representing the path to the csv file to be split

    Returns (pd.DataFrame) with new columns of "date" and "time" instead of the "timestamp"
    """
    df = pd.read_csv(file_path)
    df["datetime"] = df["timestamp"].str.split(" ").str[:2].agg(" ".join)
    df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d %H:%M:%S")
    df = df.drop(columns="timestamp")
    return df


def filter_setpoint(df):
    """
    Filter data so that only points where the data is in between the high and low thresholds is
    kept. This runs on the assumption that unoccupied rooms usually end up at one of the extremes

    Args:
        df (pandas.DataFrame): dataframe containing data to filter

    Returns (pd.DataFrame) with only rows that are "occupied"
    """
    top_threshold = max(df["RmTmpCspt"])
    bottom_threshold = min(df["RmTmpHpst"])
    df_filtered = df[df["RmTmpCspt"] < top_threshold]
    df_filtered = df_filtered[df["RmTmpHpst"] > bottom_threshold]
    return df_filtered


def graph_df(df, df_filtered):
    ax = sns.lineplot(data=df[:5000], x="datetime", y="RmTmp", color="black")
    sns.scatterplot(data=df_filtered, x="datetime", y="RmTmpCspt", color="blue")
    sns.scatterplot(data=df_filtered, x="datetime", y="RmTmpHpst", color="red")
    plt.show()
