from pathlib import Path
import numpy as np
from data_loader import *
import pickle
from gurobipy import Model, Var, GRB, quicksum

# from data_loader import (
#     mix_flow_flights_loader,
#     mix_flow_itineraries_loader,
#     mix_flow_recapture_loader,
# )

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

(recapture_from, recapture_to, recapture_dict) = mix_flow_recapture_loader()
# print(recapture_from)

path_indexes_with_recapture = {
    (recapture_from[i], recapture_to[i]) for i in recapture_from.keys()
}

print(recapture_from)


# ter bepaling delta_p_l
itinerary_flights = {
    p: [itinerary_flight_1_dict[p], itinerary_flight_2_dict[p]] for p in itinerary
}
# delta_p_i = {}
delta = {}
for p in itinerary:
    for i in flight_numbers:
        # print(flight_numbers)
        delta[i, p] = 1 if i in itinerary_flights[p] else 0

# berekening Q_i dus vraag per vlucht
Q_i = {}
for i in flight_numbers:
    Q_i[i] = sum(delta[i, p] * itinerary_demand_dict[p] for p in itinerary)

# print(Q_i)


model = Model("PASSENGERMIXFLOW")

## Decision variables

# x_pr:
# t = model.addVars(
#     path_indexes_with_recapture,
#     vtype=GRB.INTEGER,
#     lb=0,
#     name="t"
# )
# print(t)
t = {}
for p in recapture_from:
    for r in recapture_to:
        t[p, r] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"t_{p}_{r}")
        t[r, p] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"t_{r}_{p}")

# Objective: maximize profit
objective = quicksum(
    (itinerary_price_dict[p] - recapture_dict[p, r] * itinerary_price_dict[r]) * t[p, r]
    for p in recapture_from
    for r in recapture_to
    if (p, r) in recapture_dict
)

model.setObjective(objective, GRB.MINIMIZE)

model.update()

## Constraints
##Constraint 1: Capacity constraints:
for i in flight_numbers:
    model.addConstr(
        quicksum(
            delta[i, p] * t[p, r]
            for p in recapture_from
            for r in recapture_to
            if (p, r) in recapture_dict
        )
        - quicksum(
            delta[i, p] * recapture_dict[p, r] * t[r, p]
            for r in recapture_to
            for p in recapture_from
            if (r, p) in recapture_dict
        )
        >= Q_i[i] - capacity_dict[i],
        name=f"spill_{i}",
    )

## Constraint 2: Number of passengers is lower than demand
for p in itinerary:
    # print(p)
    model.addConstr(
        quicksum(
            t[p, r]
            for p in recapture_from
            for r in recapture_to
            if (p, r) in recapture_dict
        )
        <= itinerary_demand_dict[p],
        name=f"demand_{p}",
    )


## Constraint 3: Non-negativity (already defined in variable creation)

# model.params.MIPGap = 0

# model.update()

# model.optimize()
# if model.Status == GRB.OPTIMAL:
#     print("\nOptimal t[p,r] values:")
#     for (p, r) in path_indexes_with_recapture:
#         val = t[p, r].X
#         if abs(val) > 1e-6:   # only show non-zero flows
#             print(f"t[{p},{r}] = {val}")
# else:
#     print("Model status:", model.Status)

# # print("Optimal objective value:", model.objVal)
# #print("Decision Variables:", model.getVars())
# model.write("gurobi_model2.lp")
