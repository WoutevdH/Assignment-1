import numpy as np
from data_loader import *
import pickle
from gurobipy import Model, Var, GRB, quicksum


(
    flight_numbers,
    origin_dict,
    destination_dict,
    departure_time_dict,
    ready_time_dict,
    capacity_dict,
) = mix_flow_flights_loader()

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

path_indexes_with_recapture = {
    (recapture_from[i], recapture_to[i]) for i in recapture_from.keys()
}
print(path_indexes_with_recapture)

# ter bepaling delta_p_l
itinerary_flights = {
    p: [itinerary_flight_1_dict[p], itinerary_flight_2_dict[p]] for p in itinerary
}
# delta = {}
delta = {}
for r in itinerary:
    for i in flight_numbers:
        # print(flight_numbers)
        delta[i, r] = 1 if i in itinerary_flights[r] else 0

model = Model("PASSENGERMIXFLOW")

## Decision variables

# x_pr:
x = model.addVars(path_indexes_with_recapture, vtype=GRB.INTEGER, lb=0, name="x")


# Objective: maximize profit
objective = quicksum(
    (itinerary_price_dict[r] * x[p, r]) for (p, r) in path_indexes_with_recapture
)


model.setObjective(objective, GRB.MAXIMIZE)

model.update()

## Constraints
##Constraint 1: Capacity constraints:
for i in flight_numbers:
    model.addConstr(
        quicksum(delta[i, r] * (x[p, r]) for (p, r) in path_indexes_with_recapture)
        <= capacity_dict[i],
        name=f"capacity_{i}",
    )

## Constraint 2: Number of passengers is lower than demand
for p in itinerary:
    model.addConstr(
        quicksum(x[p, r] for (pp, r) in path_indexes_with_recapture if pp == p)
        <= itinerary_demand_dict[p],
        name=f"demand_{p}",
    )

## Constraint 3: Non-negativity (already defined in variable creation)

# model.params.MIPGap = 0

model.update()

model.optimize()
print("Optimal objective value:", model.objVal)
print("Decision Variables:", model.getVars())
model.write("full_passenger_mix_flow.lp")
