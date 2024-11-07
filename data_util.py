"""
Helper functions for data cleaning and visualization of HVAC data
"""

import pandas as pd


def timestamp_split(file_path):
    """ """
    data = pd.read_csv(file_path)
