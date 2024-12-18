import pandas as pd
import util
import os
from typing import List, Optional


def get_data(roomnumber: str) -> Optional[pd.DataFrame]:
    """
    Combine BAS and outdoor air databases.

    This function merges temperature data for a specific room with outdoor air statistics.

    Args:
        roomnumber (str): Id of room as given in combined_milas_hall folder (ex: A3-70)

    Returns:
        pd.DataFrame or None: Merged DataFrame containing BAS room data and outdoor air statistics,
                               or None if data cannot be loaded
    """
    try:
        bas_path = os.path.join("..", "data", "occupancy_data", f"Flo2.3-{roomnumber}.csv")
        oa_path = os.path.join("..", "data", "oa_data.csv")

        if not os.path.exists(bas_path):
            print(f"Error: BAS data file not found for room {roomnumber}")
            return None

        if not os.path.exists(oa_path):
            print(f"Error: Outdoor air data file not found")
            return None

        bas_df = util.timestamp_split(bas_path)
        oa_df = util.timestamp_split(oa_path)
        merged_df = pd.merge(bas_df, oa_df, on="datetime", how="left")
        return merged_df

    except Exception as e:
        print(f"Error processing data for room {roomnumber}: {e}")
        return None


def get_full_data_rooms() -> List[str]:
    """
    Retrieve a list of room identifiers from the occupancy data directory.

    Returns:
        List[str]: List of room identifiers found in the occupancy data directory

    Improvements:
    - Added error handling
    - More robust room identifier extraction
    - Used list comprehension with error checking
    - Added type hinting
    """
    try:
        occupancy_dir = os.path.join("..", "data", "occupancy_data")

        if not os.path.exists(occupancy_dir):
            print(f"Error: Occupancy data directory not found at {occupancy_dir}")
            return []

        df_list = [
            f[f.index("A") : f.index(".csv")]
            for f in os.listdir(occupancy_dir)
            if f.startswith("Flo2.3-") and f.endswith(".csv")
        ]

        return df_list

    except Exception as e:
        print(f"Error retrieving room data: {e}")
        return []


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
        except Exception as e:
            print(f"Error processing room {room}: {e}")

    return processed_rooms
