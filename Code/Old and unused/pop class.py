##OUD martijn


import pandas as pd

popdata = pd.read_excel(
    "Code//Problem 1 - Data//Problem 1 - Data//pop.xlsx",
    skiprows=[1, 2],
    usecols="A:C, E:G",
)

print(popdata.head())


class Pop:
    def __init__(self, city, pop2021, pop2024, country, gdp2021, gdp2024):
        self.city: str = city
        self.pop2021: int = pop2021
        self.pop2024: int = pop2024
        self.country: str = country
        self.gdp2021: int = gdp2021
        self.gdp2024: int = gdp2024

        popgrowth_per_year = (pop2024 - pop2021) / 3
        self.pop2026 = pop2024 + 2 * popgrowth_per_year

        gdpgrowth_per_year = (gdp2024 - gdp2021) / 3
        self.gdp2026 = gdp2024 + 2 * gdpgrowth_per_year

    def __repr__(self):
        return f"Pop(city={self.city}, pop2021={self.pop2021}, pop2024={self.pop2024}, pop2026={self.pop2026}, country={self.country}, gdp2021={self.gdp2021}, gdp2024={self.gdp2024}, gdp2026={self.gdp2026})"


populations_list = []

# Loop over the *rows*, not columns
for idx, row in popdata.iterrows():
    city = row.iloc[0]  # first column = city name
    pop2021 = row.iloc[1]  # second column = population 2021
    pop2024 = row.iloc[2]  # third column = population 2024
    country = row.iloc[3]  # fourth column = country name
    gdp2021 = row.iloc[4]  # fifth column = GDP 2021
    gdp2024 = row.iloc[5]  # sixth column = GDP 2024

    pop_obj = Pop(city, pop2021, pop2024, country, gdp2021, gdp2024)
    populations_list.append(pop_obj)

print(populations_list)
