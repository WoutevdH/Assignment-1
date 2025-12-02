from pathlib import Path
import numpy as np
from data_loader import *
import pickle
from gurobipy import Model, Var, GRB, quicksum

BASE_DIR = Path(__file__).resolve().parent

## This is importing the earlier calculated demand for 2026 without recalculating it
with open(BASE_DIR / "Estimated Data/demand_2026_dict.pkl", "rb") as file:
    demand_2026_dict = pickle.load(file)

## This is importang all the distances calculated earlier
with open(BASE_DIR / "Estimated Data/distance_dict.pkl", "rb") as file:
    distance_dict = pickle.load(file)

## This is importing all the yields calculated earlier
with open(BASE_DIR / "Estimated Data/yield_dict.pkl", "rb") as file:
    yield_dict = pickle.load(file)

## Importing airport data
## The index is the city names
(
    cities,
    airport_code,
    airport_lat,
    airport_lon,
    airport_runway_length,
    airport_available_slots,
) = airportdata_loader()

## Importing aircraft data
## The index is "Aircraft 1", "Aircraft 2", ...
(
    speed_dict,
    seats_dict,
    TAT_dict,
    range_dict,
    runway_req_dict,
    weekly_lease_dict,
    fixed_cost_dict,
    time_cost_param_dict,
    fuel_cost_param_dict,
) = aircraft_data_loader()

print(demand_2026_dict["London", "Madrid"], airport_code["Madrid"])  # Example usage
print(seats_dict["Aircraft 1"], speed_dict["Aircraft 1"])
print(yield_dict["Berlin", "Barcelona"])
