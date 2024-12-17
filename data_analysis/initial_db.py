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
            f[f.index("A"):f.index(".csv")]
            for f in os.listdir(occupancy_dir)
            if f.startswith("Flo2.3-") and f.endswith(".csv")
        ]

        return df_list

    except Exception as e:
        print(f"Error retrieving room data: {e}")
        return []
