## Group 2:
## Ivo Aben                 5099471
## Martijn Damman           5412633
## Wouter van der Hoorn     5370566

## This file calculates the yield for each OD pair based on the distance
from data_loader import *
import pickle
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

(
    cities,
    airport_code,
    airport_lat,
    airport_lon,
    airport_runway_length,
    airport_available_slots,
) = airportdata_loader()


def calculate_yield(distance_ij):
    yield_ij = (5.9 * distance_ij ** (-0.76)) + 0.043
    return yield_ij


def calculate_all_yields(cities, distance_dict):
    yield_dict = {}
    for i in cities:
        for j in cities:
            if i == j:
                yield_dict[(i, j)] = 0
            else:
                yield_dict[(i, j)] = calculate_yield(distance_dict[(i, j)])

    return yield_dict


## Load distance_dict from pickle file
with open(BASE_DIR / "Estimated Data/distance_dict.pkl", "rb") as file:
    distance_dict = pickle.load(file)

yield_dict = calculate_all_yields(cities, distance_dict)

## Save yield_dict as a pickle file
with open(BASE_DIR / "Estimated Data/yield_dict.pkl", "wb") as file:
    pickle.dump(yield_dict, file)
