import pandas as pd
import Airport
from Distance_calculator import calculate_distance
from pathlib import Path


class AirportManager:
    BASE_DIR = Path(__file__).resolve().parent

    airports_dict: dict[str, Airport.Airport] = {}

    def __init__(self, airportdata: str):
        filename = self.BASE_DIR / airportdata
        print(filename)
        airportdata = pd.read_excel(
            filename,
            skiprows=[0, 1, 2],
            usecols="C:V",
            nrows=5,
        )

        for col in airportdata.columns:

            city = col
            code = airportdata[col][0]
            lat = airportdata[col][1]
            lon = airportdata[col][2]
            runway_length = airportdata[col][3]
            available_slots = airportdata[col][4]

            airport_obj = Airport.Airport(
                city, code, lat, lon, runway_length, available_slots
            )
            self.airports_dict[city] = airport_obj

    def get_airport(self, city: str) -> Airport.Airport:
        return self.airports_dict.get(city)

    def get_distance_between_airports(self, city1: str, city2: str) -> float:
        airport1 = self.get_airport(city1)
        airport2 = self.get_airport(city2)
        if airport1 and airport2:

            distance = calculate_distance(
                airport1.lat,
                airport2.lat,
                airport1.lon,
                airport2.lon,
            )
            return distance
        else:
            raise ValueError("One or both airports not found.")
