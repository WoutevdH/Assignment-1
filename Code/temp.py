## FF AAN HET PRUTSEN NIKS MEE DOEN


from data_loader import *
import numpy as np
import pickle
from gurobipy import Model, Var, GRB, quicksum


## index using flight number
(
    flight_numbers,
    origin_dict,
    destination_dict,
    departure_time_dict,
    ready_time_dict,
    capacity_dict,
) = mix_flow_flights_loader()


## index using itinerary number
(
    itinerary,
    itinerary_origin_dict,
    itinerary_destination_dict,
    itinerary_flight_1_dict,
    itinerary_flight_2_dict,
    itinerary_price_dict,
    itinerary_demand_dict,
) = mix_flow_itineraries_loader()

recapture_from, recapture_to, recapture_dict = mix_flow_recapture_loader()

## itenary_flights: dictionary mapping each path p to the list of flight legs in that path
itinerary_flights = {
    p: [itinerary_flight_1_dict[p], itinerary_flight_2_dict[p]] for p in itinerary
}

# print(itinerary_flights)

## Delta: 1 if flight leg i is in path p, 0 otherwise
delta = {}
for p in itinerary:
    for i in flight_numbers:
        if i in itinerary_flights[p]:
            delta[i, p] = 1
        else:
            delta[i, p] = 0

print(delta["CC1077", 2])
print(capacity_dict["CC1077"])
print(len(delta))

print(recapture_dict[8, 2])

model = Model("passenger_mix_flow")

## Decision variables

## x_pr: number of passengers on path p that will travel on itinerary r
x = {}
for p in itinerary:
    for r in itinerary:
        x[p, r] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{p}_{r}")

##print number of variables
print(len(x))
