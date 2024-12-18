"""
Helper functions for data cleaning and visualization of HVAC data
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from typing import List


def timestamp_split(file_path):
    """
    Split timestamp columns into date and time columns

    Args:
        file_path (str): string representing the path to the csv file to be split

    Returns (pd.DataFrame) with new columns of "date" and "time" instead of the "timestamp"
    """
    try:
        df = pd.read_csv(file_path)
        df["datetime"] = df["timestamp"].str.split(" ").str[:2].str.join(" ")
        df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d %H:%M:%S")
        df = df.drop(columns="timestamp")
        index = pd.DatetimeIndex(df["datetime"])
        df = df.iloc[index.indexer_between_time("08:00", "18:00")]
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
    df_filtered = df_filtered.loc[df["RmTmpHpst"] > bottom_threshold]
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
            if start_idx + 20 in df_full.index:
                this_data = df_full.loc[range(start_idx, start_idx + 20)]
            else:
                this_data = df_full.loc[start_idx:]
            if final_data == {}:
                final_data = this_data.to_dict()
            else:
                for k, v in this_data.to_dict().items():
                    orig_dict = final_data[k]
                    orig_dict.update(v)
                    final_data[k] = orig_dict
    return pd.DataFrame(final_data)


def remove_asymptotes(df, df_full):
    """
    Clean data so when desired temperature asymptote is reached, remaining data is removed. This
    helps identify how long it takes for each instance of the room occupancy to heat up to the
    desired temperature.
    """
    final_data = {}
    list_of_df = [d for _, d in df.groupby(df.index - np.arange(len(df)))]

    for new_df in list_of_df:
        start_idx = new_df.index[0]
        room_goal_temp = new_df.loc[start_idx]["RmTmpCspt"]

        if start_idx + 30 in df_full.index:
            this_data = df_full.loc[range(start_idx, start_idx + 30)]
        else:
            this_data = df_full.loc[start_idx:]
        this_data["TempDiff"] = abs(this_data.RmTmp - room_goal_temp)

        end_idxes = this_data[this_data.TempDiff <= 2.5].index
        if len(end_idxes) == 0:
            continue
        end_idx = end_idxes[0] + 1
        this_data = this_data.loc[range(start_idx, end_idx)]

        if final_data == {}:
            final_data = this_data.to_dict()
        else:
            for k, v in this_data.to_dict().items():
                orig_dict = final_data[k]
                orig_dict.update(v)
                final_data[k] = orig_dict
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


def combine_all_room_data(room_list: List[str], data_getter, room_stats_path):
    """
    Process room data through a series of filtering and aggregation steps.

    This utility function applies a standard data processing pipeline to a list of rooms:
    1. Load room statistics from CSV
    2. Retrieve full dataset for each room
    3. Merge room statistics with room data
    4. Filter by setpoint
    5. Split by occupancy
    6. Remove asymptotes
    7. Simplify occurrences

    Args:
        room_list (List[str]): List of room identifiers to process
        data_getter (callable): Function to retrieve data for a specific room
        room_stats_path (str, optional): Path to the room statistics CSV file

    Raises:
        ValueError: If data retrieval or processing fails for any room
    """
    try:
        room_stats_df = pd.read_csv(room_stats_path)
    except Exception as e:
        print(f"Error reading room statistics file: {e}")
        room_stats_df = pd.DataFrame()
    processed_rooms = []

    for room in room_list:
        try:
            # Retrieve room data
            full_df = data_getter(room)

            if full_df is None or full_df.empty:
                print(f"Skipping room {room}: No data available")
                continue

            # Find matching room statistics
            room_stats = room_stats_df[room_stats_df["idBAS"] == f"Flo2.3-{room}"]

            # If room stats exist, merge them with the room data
            if not room_stats.empty:
                full_df["idBAS"] = room_stats["idBAS"].values[0]
                full_df["prof"] = room_stats["prof"].values[0]
                full_df["unoccDamper"] = room_stats["unoccDamper"].values[0]
                full_df["unoccHeat"] = room_stats["unoccHeat"].values[0]
                full_df["unoccCool"] = room_stats["unoccCool"].values[0]
                full_df["roomSqFt"] = room_stats["roomSqFt"].values[0]

            full_df.to_csv("../data/aggregatedData.csv", index=False)

            filtered_df1 = filter_setpoint(full_df)
            if filtered_df1.empty:
                print(f"Skipping room {room}: No data after setpoint filtering")
                continue

            filtered_df = split_by_occupancy(filtered_df1, full_df)
            if filtered_df.empty:
                print(f"Skipping room {room}: No occupancy data found")
                continue

            agg_df = remove_asymptotes(filtered_df, full_df)
            if agg_df.empty:
                print(f"Skipping room {room}: No data after asymptote removal")
                continue

            final_df = simplify_occurrences(agg_df)
            if not final_df.empty:
                processed_rooms.append(final_df)

        except Exception as e:
            print(f"Error processing room {room}: {e}")

    return processed_rooms


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
    # Group by contiguous index segments
    grouped = df.groupby((df.index.to_series().diff() != 1).cumsum())

    # Filter groups with more than 1 data point
    valid_groups = [group_df for _, group_df in grouped if len(group_df) > 1]
    print(valid_groups)

    plt.figure(figsize=(15, 10))

    for i, group_df in enumerate(valid_groups, 1):
        plt.subplot(3, 3, i)

        # Ensure x-axis is consistent
        x = np.arange(len(group_df))
        print(f"Occurence: {i}, Date: {group_df.iloc[0]['datetime']}")
        print(f"{df.index.to_series()}")
        print(f"Diff: {df.index.to_series().diff()}")
        print(f"Temp: {group_df['RmTmp']}")
        print(f"Temp Setpoint: {group_df['RmTmpCspt']}")

        plt.plot(x, group_df["RmTmp"], label="Room Temperature")
        plt.plot(x, group_df["RmTmpCspt"], color="black", label="Setpoint")
        plt.title(f"Occurrence {i}: {group_df.iloc[0]['datetime']}")
        plt.xlabel("Time")
        plt.ylabel("Temperature")
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
