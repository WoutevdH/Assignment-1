import numpy as np
import Demand_manager
import Airport_manager
import Population_manager


def city_info_collector(city1, city2):
    airport_manager = Airport_manager.AirportManager(
        "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    )
    demand_manager = Demand_manager.DemandManager(
        "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    )

    population_data = Population_manager.Population_manager(
        "Problem 1 - Data/Problem 1 - Data/Pop.xlsx"
    )

    code_city1 = airport_manager.get_airport(city1).code
    code_city2 = airport_manager.get_airport(city2).code

    demand_ij = demand_manager.get_demand(2021, code_city1, code_city2)
    population_city1 = population_data.get_population_data(city1).pop2021
    population_city2 = population_data.get_population_data(city2).pop2021
    gdp_city1 = population_data.get_population_data(city1).gdp2021
    gdp_city2 = population_data.get_population_data(city2).gdp2021

    return f"The demand from {city1} to {city2} is {demand_ij}, the population of {code_city1} in 2021 is {population_city1} with a GDP of {gdp_city1}, and the population of {code_city2} in 2021 is {population_city2} with a GDP of {gdp_city2}."


print(city_info_collector("Paris", "Madeira"))
