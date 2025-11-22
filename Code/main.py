import Airport_manager
import Airport
import Demand_manager


def main():
    airport_manager = Airport_manager.AirportManager(
        "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    )
    demand_manager = Demand_manager.DemandManager(
        "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx"
    )

    london_airport = airport_manager.get_airport("London")
    print(london_airport)

    distance = airport_manager.get_distance_between_airports("London", "Paris")
    print(f"Distance between London and Paris: {distance} km")

    demand = demand_manager.get_demand(2021, "EHAM", "EPWA")
    print(f"Demand from EHAM to EPWA: {demand}")


if __name__ == "__main__":
    main()
