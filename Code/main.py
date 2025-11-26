import Airport_manager
import Demand_manager
import Population_manager

def main():
    airport_manager = Airport_manager.AirportManager(
        "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    )
    demand_manager = Demand_manager.DemandManager(
        "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    )

    population_data = Population_manager.Population_manager(
        "Problem 1 - Data/Problem 1 - Data/Pop.xlsx"
    )

    barcelona_population = population_data.get_population_data("Barcelona")
    print(f"Barcelona population in 2024: {barcelona_population.pop2024}")

    london_airport = airport_manager.get_airport("London")
    print(london_airport)

    distance = airport_manager.get_distance_between_airports("London", "Paris")
    print(f"Distance between London and Paris: {distance} km")

    demand = demand_manager.get_demand(2021, "EHAM", "EPWA")
    print(f"Demand from EHAM to EPWA: {demand}")


if __name__ == "__main__":
    main()
