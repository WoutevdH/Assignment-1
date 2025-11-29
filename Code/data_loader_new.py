##This file loads all data provided from the excel files


import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

##Everything is linked to the name of the cities, not the airport codes.


## Import all airport data and return multiple dictionaries
def airportdata_loader():
    filepath = BASE_DIR / "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    airport_data = pd.read_excel(
        filepath,
        skiprows=[0, 1, 2],
        usecols="B:V",
        nrows=5,
        index_col=0,
    )

    cities = list(airport_data)
    airport_code = airport_data.loc["ICAO Code"].to_dict()
    airport_lat = airport_data.loc["Latitude (deg)"].to_dict()
    airport_lon = airport_data.loc["Longitude (deg)"].to_dict()
    airport_runway_length = airport_data.loc["Runway (m)"].to_dict()
    airport_available_slots = airport_data.loc["Available slots"].to_dict()
    return (
        cities,
        airport_code,
        airport_lat,
        airport_lon,
        airport_runway_length,
        airport_available_slots,
    )


## Import demand data for 2021 and return a dictionary with (city_i, city_j): demand
def demand2021_loader():
    filepath = BASE_DIR / "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    demand_df = pd.read_excel(
        filepath,
        skiprows=range(11),
        usecols="B:V",
        index_col=0,
        nrows=20,
    )

    (
        cities,
        airport_code,
        airport_lat,
        airport_lon,
        airport_runway_length,
        airport_available_slots,
    ) = airportdata_loader()

    icao_to_city = {code: city for city, code in airport_code.items()}

    demand_city_df = demand_df.rename(index=icao_to_city, columns=icao_to_city)

    demand_2021_dict = {
        (i, j): demand_city_df.loc[i, j] for i in cities for j in cities
    }

    return demand_2021_dict


## Import population data and return four dictionaries with population and gdp
def population_data_loader():
    filepath = BASE_DIR / "Problem 1 - Data/Problem 1 - Data/pop.xlsx"
    population_data = pd.read_excel(
        filepath, skiprows=[0, 1], usecols="A:C, F:G", index_col=0
    )

    pop_2021_dict = population_data[2021].to_dict()
    pop_2024_dict = population_data[2024].to_dict()
    gdp_2021_dict = population_data["2021.1"].to_dict()
    gdp_2024_dict = population_data["2024.1"].to_dict()

    return pop_2021_dict, pop_2024_dict, gdp_2021_dict, gdp_2024_dict


(
    cities,
    airport_code,
    airport_lat,
    airport_lon,
    airport_runway_length,
    airport_available_slots,
) = airportdata_loader()

demand_2021_dict = demand2021_loader()

pop2021_dict, pop2024_dict, gdp2021_dict, gdp2024_dict = population_data_loader()

# print(f"This is an example of all data for city Barcelona: ")
# print(f"Airport code: {airport_code['Barcelona']}")
# print(f"Latitude: {airport_lat['Barcelona']}")
# print(f"Longitude: {airport_lon['Barcelona']}")
# print(f"Runway length: {airport_runway_length['Barcelona']}")
# print(f"Available slots: {airport_available_slots['Barcelona']}")
# print(f"Demand 2021: {demand_2021_dict[('Barcelona', 'Barcelona')]}")
# print(f"Population 2021: {pop2021_dict['Barcelona']}")
# print(f"Population 2024: {pop2024_dict['Barcelona']}")
# print(f"GDP 2021: {gdp2021_dict['Barcelona']}")
# print(f"GDP 2024: {gdp2024_dict['Barcelona']}")
