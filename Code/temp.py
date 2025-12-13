## FF AAN HET PRUTSEN NIKS MEE DOEN


from data_loader import *
import numpy as np
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

valid_recapture = [
    (p, r)
    for p in itinerary
    for r in itinerary
    if (p == r) or (recapture_dict[p, r] > 0)
]

for p in itinerary:
    for r in itinerary:
        if p == r:
            recapture_dict[p, r] = 1.0

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

# itinerary_with_recapture = []
# for p in itinerary:
#     for r in itinerary:
#         if recapture_dict[p, r] == 0:
#             continue
#         else:
#             if p not in itinerary_with_recapture:
#                 itinerary_with_recapture.append(p)
#             break

model = Model("mix_flow_test")

## Decision variables
x = {}
for p, r in valid_recapture:
    x[p, r] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{p}_{r}")


# Objective: maximum revenue for carrying all passengers
objective = quicksum(itinerary_price_dict[r] * x[p, r] for p, r in valid_recapture)

model.setObjective(objective, GRB.MAXIMIZE)

# ## Constraint 1: Capacity constraints:
for i in flight_numbers:
    model.addConstr(quicksum(delta[i, r] * x[p, r] for p, r in valid_recapture) <= capacity_dict[i])

# ## Constraint 2: Number of passengers is lower than demand
for p in itinerary:
    model.addConstr(quicksum(x[p, r] / recapture_dict[p, r] for (pp, r) in valid_recapture if pp == p) <= itinerary_demand_dict[p])

model.update()

model.optimize()

if model.Status == GRB.OPTIMAL:
    print("\nOptimal x[p,r] values:")
    for p, r in valid_recapture:
        val = x[p, r].X
        if abs(val) > 1e-6:  # only show non-zero flows
            print(f"x[{p},{r}] = {val}")
    ## print number of nonzero x[p,r] values
    nonzero_count = sum(
        1 for p, r in valid_recapture if abs(x[p, r].X) > 1e-6
    )
    print(f"Number of nonzero x[p,r] values: {nonzero_count}")

    print(f"\nOptimal objective value: {model.ObjVal}")