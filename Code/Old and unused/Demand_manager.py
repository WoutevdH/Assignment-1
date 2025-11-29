import pandas as pd
from pathlib import Path
import Demand


class DemandManager:
    BASE_DIR = Path(__file__).resolve().parent

    demand_dict: dict[int, Demand.Demand] = {}

    def __init__(self, airportdata: str):
        self.demand_dict[2021] = Demand.Demand(2021, airportdata)

    def get_demand(self, year: int, city1: str, city2: str) -> int:
        demand = self.demand_dict.get(year)
        if demand:
            return demand.get_demand(city1, city2)
        else:
            raise ValueError(f"No demand data available for year {year}")

    def add_demand_matrix(self, year: int, matrix):
        self.demand_dict[year] = Demand.Demand(year, matrix)
