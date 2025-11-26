import pandas as pd
from pathlib import Path


class Population_data:
    def __init__(self, city, pop2021, pop2024, gdp2021, gdp2024):
        self.city: str = city
        self.pop2021: int = pop2021
        self.pop2024: int = pop2024
        self.gdp2021: float = gdp2021
        self.gdp2024: float = gdp2024


class Population_manager:
    BASE_DIR = Path(__file__).resolve().parent

    pop_dict = {}

    def __init__(self, filename_input: str):
        self.filename: str = filename_input

        filename = self.BASE_DIR / filename_input

        print(filename)

        popdata = pd.read_excel(
            filename, skiprows=[0, 1], usecols="A:C, F:G", index_col=0
        )

        for city_row, row in popdata.iterrows():
            # print(city_row)
            city: str = city_row
            pop2021 = (city_row, row.iloc[0])
            pop2024 = (city_row, row.iloc[1])
            gdp2021 = (city_row, row.iloc[2])
            gdp2024 = (city_row, row.iloc[3])

            pop_obj = Population_data(
                city, pop2021[1], pop2024[1], gdp2021[1], gdp2024[1]
            )

            self.pop_dict[city] = pop_obj

    def get_population_data(self, city: str) -> Population_data:
        return self.pop_dict.get(city)
