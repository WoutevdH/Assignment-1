##This file estimates the parameters for the gravity model based on 2021 data

import numpy as np
import pandas as pd
from data_loader_new import *
from Distance_calculator import calculate_distance


## Import airport data
(
    cities,
    airport_code,
    airport_lat,
    airport_lon,
    airport_runway_length,
    airport_available_slots,
) = airportdata_loader()

## Import demand data for 2021
demand_2021_dict = demand2021_loader()

## Import population and gdp data
pop_2021_dict, pop_2024_dict, gdp_2021_dict, gdp_2024_dict = population_data_loader()


def estimate_gravity_model(
    popdata, gdpdata, demand_data, airports_lat, airports_lon, f=1.42
):

    rows = []

    for (i, j), D_ij in demand_data.items():
        pop_i = popdata[i]
        pop_j = popdata[j]

        gdp_i = gdpdata[i]
        gdp_j = gdpdata[j]

        distance_ij = calculate_distance(
            airports_lat[i], airports_lat[j], airports_lon[i], airports_lon[j]
        )

        if i == j:
            continue  # Skip same city pairs

        if D_ij <= 0:
            continue  # Skip zero demand pairs to avoid log(0)

        rows.append(
            {
                "ln_D_ij": np.log(D_ij),
                "ln_pop": np.log(pop_i * pop_j),
                "ln_gdp": np.log(gdp_i * gdp_j),
                "ln_fd": np.log(f * distance_ij),
            }
        )

    gravity_df = pd.DataFrame(rows)

    # Design matrix X
    X = np.column_stack(
        [
            np.ones(len(gravity_df)),  # constant (a = ln k)
            gravity_df["ln_pop"].values,  # b1
            gravity_df["ln_gdp"].values,  # b2
            -gravity_df["ln_fd"].values,  # -b3
        ]
    )

    # Target vector y
    y = gravity_df["ln_D_ij"].values

    beta = np.linalg.lstsq(X, y, rcond=None)[0]

    k = np.exp(beta[0])
    b1 = beta[1]
    b2 = beta[2]
    b3 = beta[3]

    print(f"Estimated parameters:")
    print(f"k = {k}")
    print(f"b1 = {b1}")
    print(f"b2 = {b2}")
    print(f"b3 = {b3}")

    return k, b1, b2, b3


estimate_gravity_model(
    pop_2021_dict, gdp_2021_dict, demand_2021_dict, airport_lat, airport_lon
)
