import pandas as pd
from pathlib import Path


class Demand:
    BASE_DIR = Path(__file__).resolve().parent

    demand_dict: dict[str, int] = {}
    year: int

    def __init__(self, year: int, airportdata: str):
        self.year = year
        filename = self.BASE_DIR / airportdata
        print(filename)
        airportdata = pd.read_excel(
            filename,
            skiprows=range(11),
            usecols="B:V",
            nrows=20,
            index_col=0,
        )

        headers = airportdata.columns.tolist()

        for i, city1 in enumerate(headers):
            for j, city2 in enumerate(headers):
                key = city1 + ":" + city2
                if i != 0 and j != 0:
                    self.demand_dict[key] = airportdata.iloc[i, j]

    def get_demand(self, city1: str, city2: str) -> int:
        key: str = city1 + ":" + city2
        return self.demand_dict[key]

    def get_year(self) -> int:
        return self.year
