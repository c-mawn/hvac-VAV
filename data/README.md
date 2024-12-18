### Data Files Overview
This document is meant to serve as a source of reference regarding the data present in this repo.

This data folder contains two main folders for data: `combined_milas_hall` and `occupancy_data`. `combined_milas_hall` contains BAS data for each room in the system for Milas hall, while `occupancy_data` contains BAS data for each room in the system that has a working occupancy sensor. It is import to note that there are a few rooms which have occupancy sensors installed but the resulting data is broken due to some error. Those rooms have been excluded from the analysis.

In addition to this, there are standalone csv files in this folder: `oa_data.csv`, `RoomStatsCopy.csv` <ADD OTHER ONES HERE>. `oa_data.csv` contains outside air information for every 15 minute interval from March 11, 2021 onwards. `RoomStatsCopy.csv` contains information regarding each of the rooms being analyzed, like room square feet, professor name, etc. This should be edited based on whatever new information is collected regarding any room.
