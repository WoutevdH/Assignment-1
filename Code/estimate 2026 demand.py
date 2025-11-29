##This file estimates the 2026 growth for gdp and population and then uses the gravity model to estimate 2026 demand


from data_loader_new import *
from Distance_calculator import calculate_distance
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


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


## Estimate population and gdp for 2026 based on linear growth from 2021 to 2024
def pop_gdp_2026estimator(
    cities, pop_2021_dict, pop_2024_dict, gdp_2021_dict, gdp_2024_dict
):
    pop_2026_dict = {}
    gdp_2026_dict = {}

    for i in cities:
        growth_pop_per_year = (pop_2024_dict[i] - pop_2021_dict[i]) / 3
        pop_2026_dict[i] = pop_2024_dict[i] + growth_pop_per_year * 2

        growth_gdp_per_year = (gdp_2024_dict[i] - gdp_2021_dict[i]) / 3
        gdp_2026_dict[i] = gdp_2024_dict[i] + growth_gdp_per_year * 2

    return pop_2026_dict, gdp_2026_dict


pop_2026_dict, gdp_2026_dict = pop_gdp_2026estimator(
    cities, pop_2021_dict, pop_2024_dict, gdp_2021_dict, gdp_2024_dict
)

# print(pop_2026_dict, gdp_2026_dict)


## Estimate 2026 demand using the gravity model parameters obtained earlier
def estimate_demand(
    cities,
    pop_year_dict,
    gdp_year_dict,
    airport_lat,
    airport_lon,
    f=1.42,
    k=9.724183066185807e-07,
    b1=0.5187262711183023,
    b2=0.5347745906777904,
    b3=1.0785119516638721,
):
    demand_year_dict = {}

    for i in cities:
        for j in cities:

            if i == j:
                demand_year_dict[(i, j)] = 0
            elif i != j:
                pop = pop_year_dict[i] * pop_year_dict[j]
                gdp = gdp_year_dict[i] * gdp_year_dict[j]
                distance_ij = calculate_distance(
                    airport_lat[i], airport_lat[j], airport_lon[i], airport_lon[j]
                )

                demand_ij = k * (((pop**b1) * (gdp**b2)) / ((f * distance_ij) ** b3))
                demand_year_dict[(i, j)] = demand_ij

    return demand_year_dict


demand_2026_dict = estimate_demand(
    cities, pop_2026_dict, gdp_2026_dict, airport_lat, airport_lon
)

demand_estimated_2021_dict = estimate_demand(
    cities, pop_2021_dict, gdp_2021_dict, airport_lat, airport_lon
)

print(
    demand_estimated_2021_dict["Paris", "London"], demand_2021_dict["Paris", "London"]
)

demand_2026_dataframe = pd.DataFrame(0.0, index=cities, columns=cities)

for (i, j), demand in demand_2026_dict.items():
    demand_2026_dataframe.loc[i, j] = demand

demand_2026_dataframe.to_excel(BASE_DIR / "Estimated Data/demand_2026_matrix.xlsx")

# print(pop_2026_dict["Paris"], gdp_2026_dict["Paris"])
# print(demand_2026_dict["Paris", "London"])
