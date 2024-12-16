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
    try:
        df = pd.read_csv(file_path)
        df["datetime"] = df["timestamp"].str.split(" ").str[:2].agg(" ".join)
        df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d %H:%M:%S")
        df = df.drop(columns="timestamp")
        index = pd.DatetimeIndex(df["datetime"])
        df = df.iloc[index.indexer_between_time("09:00", "18:00")]
        return df
    
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing file: {e}")
        return pd.DataFrame()


def filter_setpoint(df):
    """
    Filter data so that only points where the data is in between the high and low thresholds is
    kept. This runs on the assumption that unoccupied rooms usually end up at one of the extremes

    Args:
        df (pd.DataFrame): dataframe containing data to filter

    Returns (pd.DataFrame) with only rows that are "occupied"
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
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
    final_data = []
    
    for group_key, group_df in df.groupby((df.index.to_series().diff() != 1).cumsum()):
        if (
            (group_df['RmTmp'] >= (group_df['RmTmpCspt'] + 3)).any() or 
            (group_df['RmTmp'] <= (group_df['RmTmpCspt'] - 3)).any()
        ):
            start_idx = group_df.index[0]
            try:
                this_data = df_full.loc[start_idx:start_idx+19]
            except KeyError:
                this_data = df_full.loc[start_idx:]
            
            final_data.append(this_data)
    
    return pd.concat(final_data) if final_data else pd.DataFrame()


def remove_asymptotes(df, df_full):
    """
    Clean data so when desired temperature asymptote is reached, remaining data is removed. This
    helps identify how long it takes for each instance of the room occupancy to heat up to the
    desired temperature.
    """
    final_data = []
    list_of_df = [d for _, d in df.groupby(df.index - np.arange(len(df)))]

    for new_df in list_of_df:
        this_occurrence = new_df.loc[new_df.index[0]]
        this_occurrence["TimeToStable"] = (
            new_df.iloc[-1].datetime - this_occurrence.datetime
        ).total_seconds() // 60
        if this_occurrence["TimeToStable"] > 300:
            continue
        final_data.append(this_occurrence)

    return pd.DataFrame(final_data)


def simplify_occurrences(df):
    """
    Summarize temperature occurrence data, filtering out long stabilization periods.

    Args:
        df (pd.DataFrame): Input DataFrame with temperature data

    Returns:
        pd.DataFrame: Summarized occurrences with stabilization time less than 300 minutes
    """
    final_data = []
    for group_key, group_df in df.groupby((df.index.to_series().diff() != 1).cumsum()):
        first_record = group_df.iloc[0]
        time_to_stable = (group_df.iloc[-1]['datetime'] - first_record['datetime']).total_seconds() / 60

        if 0 < time_to_stable <= 300:  # 5 hours max
            first_record['TimeToStable'] = time_to_stable
            final_data.append(first_record)
    
    return pd.DataFrame(final_data) if final_data else pd.DataFrame()


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
    """
    Create multiple line plots for temperature variations across different occurrences.

    Args:
        df (pd.DataFrame): Input temperature data
    """
    plt.figure(figsize=(15, 10))
    
    for i, (_, group_df) in enumerate(df.groupby((df.index.to_series().diff() != 1).cumsum()), 1):
        plt.subplot(3, 3, i)  # Adjust grid as needed
        
        # Ensure x-axis is consistent
        x = np.arange(len(group_df))
        
        plt.plot(x, group_df['RmTmp'], label='Room Temperature')
        plt.plot(x, group_df['RmTmpCspt'], color='black', label='Setpoint')
        plt.title(f"Occurrence {i}: {group_df.iloc[0]['datetime']}")
        plt.xlabel('Time')
        plt.ylabel('Temperature')
        plt.legend()
        plt.grid(True)
        
        if i >= 9:
            break
    
    plt.tight_layout()
    plt.show()


def scatter_temp_diff_vs_time_room(df):
    """
    Create a scatter plot of temperature difference vs stabilization time for a single room.

    Args:
        df (pd.DataFrame): Input temperature data
    """
    plt.scatter(df.TempDiff, df.TimeToStable)


def scatter_temp_diff_vs_time_all_room(df_list):
    """
    Create scatter plots of temperature difference vs stabilization time for multiple rooms.

    Args:
        df_list (list): List of DataFrames containing temperature data
    """
    for df in df_list:
        print(df)
        plt.scatter(df.TempDiff, df.TimeToStable)

    plt.show()
