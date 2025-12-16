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


## Import aircraft data for different types of aircraft and return a dictionaries, index is number of aircraft
def aircraft_data_loader():
    filepath = BASE_DIR / "Problem 1 - Data/Problem 1 - Data/AircraftData.xlsx"
    aircraft_data = pd.read_excel(filepath, skiprows=[1, 2, 8], index_col=0)
    aircraft_types = list(aircraft_data.columns)

    ##Aircraft specs
    speed_dict = aircraft_data.loc["Speed [km/h]"].to_dict()
    seats_dict = aircraft_data.loc["Seats"].to_dict()
    TAT_dict = aircraft_data.loc["Average TAT [mins]"].to_dict()
    range_dict = aircraft_data.loc["Maximum range [km]"].to_dict()
    runway_req_dict = aircraft_data.loc["Runway required [m]"].to_dict()

    ##Aircraft operating costs
    weekly_lease_dict = aircraft_data.loc["Weekly lease cost [€]"].to_dict()
    fixed_cost_dict = aircraft_data.loc["Fixed operating cost C_X [€]"].to_dict()
    time_cost_param_dict = aircraft_data.loc["Time cost parameter C_T [€/hr]"].to_dict()
    fuel_cost_param_dict = aircraft_data.loc["Fuel cost parameter C_F"].to_dict()

    return (
        aircraft_types,
        speed_dict,
        seats_dict,
        TAT_dict,
        range_dict,
        runway_req_dict,
        weekly_lease_dict,
        fixed_cost_dict,
        time_cost_param_dict,
        fuel_cost_param_dict,
    )


#### Data for question 2 --------------------------------------------------------------


def mix_flow_flights_loader():  ##index is flight number
    filepath = BASE_DIR / "Problem 2 - Data/Problem 2 - Data/Group_2.xlsx"
    flights_data = pd.read_excel(filepath, sheet_name="Flights", index_col=0)
    flight_numbers = flights_data.index.tolist()
    origin_dict = flights_data["Origin"].to_dict()
    destination_dict = flights_data["Destination"].to_dict()
    departure_time_dict = flights_data["Departure"].to_dict()
    ready_time_dict = flights_data["Ready"].to_dict()
    capacity_dict = flights_data["Capacity"].to_dict()

    return (
        flight_numbers,
        origin_dict,
        destination_dict,
        departure_time_dict,
        ready_time_dict,
        capacity_dict,
    )


(
    flight_numbers,
    origin_dict,
    destination_dict,
    departure_time_dict,
    ready_time_dict,
    capacity_dict,
) = mix_flow_flights_loader()


def mix_flow_itineraries_loader():  ##index is itinerary number
    filepath = BASE_DIR / "Problem 2 - Data/Problem 2 - Data/Group_2.xlsx"
    itineraries_data = pd.read_excel(filepath, sheet_name="Itineraries", index_col=0)
    itinerary = itineraries_data.index.tolist()
    itinerary_origin_dict = itineraries_data["Origin"].to_dict()
    itinerary_destination_dict = itineraries_data["Destination"].to_dict()
    itinerary_flight_1_dict = itineraries_data["Flight 1"].to_dict()
    itinerary_flight_2_dict = itineraries_data["Flight 2"].to_dict()
    itinerary_price_dict = itineraries_data["Price [EUR]"].to_dict()
    itinerary_demand_dict = itineraries_data["Demand"].to_dict()

    return (
        itinerary,
        itinerary_origin_dict,
        itinerary_destination_dict,
        itinerary_flight_1_dict,
        itinerary_flight_2_dict,
        itinerary_price_dict,
        itinerary_demand_dict,
    )


(
    itinerary,
    itinerary_origin_dict,
    itinerary_destination_dict,
    itinerary_flight_1_dict,
    itinerary_flight_2_dict,
    itinerary_price_dict,
    itinerary_demand_dict,
) = mix_flow_itineraries_loader()


def mix_flow_recapture_loader():  ##Index with both 'from' and 'to' itenerary
    filepath = BASE_DIR / "Problem 2 - Data/Problem 2 - Data/Group_2.xlsx"
    recapture_data = pd.read_excel(filepath, sheet_name="Recapture")
    recapture_from = recapture_data["From Itinerary"].to_dict()
    recapture_to = recapture_data["To Itinerary"].to_dict()
    recapture_dict = {
        (row["From Itinerary"], row["To Itinerary"]): (row["Recapture Rate"])
        for _, row in recapture_data.iterrows()
    }

    ##return 0 if no recapture rate is defined
    for p in itinerary:
        for r in itinerary:
            if p == r:
                recapture_dict[p, r] = 1.0
            if (p, r) not in recapture_dict:
                recapture_dict[p, r] = 0

    return recapture_from, recapture_to, recapture_dict


