# Airport

# import pandas as pd

# airportdata = pd.read_excel(
#     r"C:\wouter\2025-2026\Airline planning & optimisation\Assignment 1\Code\Problem 1 - Data\Problem 1 - Data\DemandGroup2.xlsx",
#     skiprows=[0, 1, 2],
#     usecols="C:V",
#     nrows=5,
# )


class Airport:
    def __init__(
        self,
        city,
        code,
        lat,
        lon,
        runway_length,
        available_slots,
    ):
        self.city: str = city
        self.code: str = code
        self.lat: float = lat
        self.lon: float = lon
        self.runway_length: int = runway_length
        self.available_slots: int = available_slots

    def __repr__(self):
        return f"Airport(city={self.city}, code={self.code}, lat={self.lat}, lon={self.lon}, runway_length={self.runway_length}, available_slots={self.available_slots})"


# airports_list = []

# for col in airportdata.columns:

#     city = col
#     code = airportdata[col][0]
#     lat = airportdata[col][1]
#     lon = airportdata[col][2]
#     runway_length = airportdata[col][3]
#     available_slots = airportdata[col][4]

#     airport_obj = Airport(city, code, lat, lon, runway_length, available_slots)
#     airports_list.append(airport_obj)
