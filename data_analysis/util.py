"""
Helper functions for data cleaning and visualization of HVAC data
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


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
        df (pd.DataFrame): dataframe containing data to filter

    Returns (pd.DataFrame) with only rows that are "occupied"
    """
    top_threshold = max(df["RmTmpCspt"])
    bottom_threshold = min(df["RmTmpHpst"])
    df_filtered = df[df["RmTmpCspt"] < top_threshold]
    df_filtered = df_filtered[df["RmTmpHpst"] > bottom_threshold]

    return df_filtered


def split_by_occupancy(df, df_full):
    """
    Split the data so only "occupied" rooms and the 20 time stamps after are included.

    Args:
        df (pd.DataFrame): dataframe containing filtered data
        df_full (pd.DataFrame): dataframe containing original data

    Returns (pd.DataFrame) with data segmented by occupancy
    """
    final_data = {}
    list_of_df = [d for _, d in df.groupby(df.index - np.arange(len(df)))]
    for new_df in list_of_df:
        if (new_df.head(1)["RmTmp"] >= (new_df.head(1)["RmTmpCspt"] + 3)).all() or (
            new_df.head(1)["RmTmp"] <= (new_df.head(1)["RmTmpCspt"] - 3)
        ).all():
            start_idx = new_df.index[0]
            this_data = df_full.loc[range(start_idx, start_idx + 20)]
            if final_data == {}:
                final_data = this_data.to_dict()
            else:
                for k, v in this_data.to_dict().items():
                    orig_dict = final_data[k]
                    orig_dict.update(v)
                    final_data[k] = orig_dict
    return pd.DataFrame(final_data)


def aggregate_by_occupancy(df, df_full):
    final_data = {}
    list_of_df = [d for _, d in df.groupby(df.index - np.arange(len(df)))]

    for new_df in list_of_df:
        start_idx = new_df.index[0]
        room_goal_temp = new_df.loc[start_idx]["RmTmpCspt"]

        this_data = df_full.loc[range(start_idx, start_idx + 30)]
        this_data["TempDiff"] = abs(this_data.RmTmp - room_goal_temp)

        end_idxes = this_data[this_data.TempDiff <= 2.5].index
        if len(end_idxes) == 0:
            continue
        end_idx = end_idxes[0]
        this_data = this_data.loc[range(start_idx, end_idx)]

        if final_data == {}:
            final_data = this_data.to_dict()
        else:
            for k, v in this_data.to_dict().items():
                orig_dict = final_data[k]
                orig_dict.update(v)
                final_data[k] = orig_dict
    return pd.DataFrame(final_data)


################### GRAPHING FUNCTIONS ##############################################################


def graph_df_temp(df, df_filtered):
    """
    Plot temperature and setpoints against time.

    Args:
        df (pd.DataFrame): dataframe containing raw data
        df_filtered (pd.DataFrame): dataframe containing filtered data
    """
    ax = sns.lineplot(data=df[:5000], x="datetime", y="RmTmp", color="black")
    sns.scatterplot(data=df_filtered, x="datetime", y="RmTmpCspt", color="blue")
    sns.scatterplot(data=df_filtered, x="datetime", y="RmTmpHpst", color="red")
    plt.show()


def graph_aggregated_temp(df):
    list_of_df = [d for _, d in df.groupby(df.index - np.arange(len(df)))]
    for new_df in list_of_df:
        start_idx = new_df.index[0]
        sns.lineplot(data=new_df, x=np.arange(20), y="RmTmp")
        sns.lineplot(data=new_df, x=np.arange(20), y="RmTmpCspt", color="black")
        plt.title(new_df.loc[start_idx, "datetime"])
        plt.show()
