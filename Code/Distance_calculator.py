##Distance calculator

import numpy as np
import pandas as pd

# from gurobipy import Model, GRB, Var, quicksum


def calculate_distance(
    lat_i,
    lat_j,
    lon_i,
    lon_j,
    Re=6371,
):
    R = Re  # Radius of the Earth in kilometers
    lat_i_rad = np.radians(lat_i)
    lat_j_rad = np.radians(lat_j)
    delta_lat = np.radians(lat_j - lat_i)
    delta_lon = np.radians(lon_j - lon_i)

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat_i_rad) * np.cos(lat_j_rad) * np.sin(delta_lon / 2) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance
