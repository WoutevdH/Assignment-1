from pathlib import Path
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

(recapture_from, recapture_to, recapture_dict) = mix_flow_recapture_loader()


## itenary_flights: dictionary mapping each path p to the list of flight legs in that path
itinerary_flights = {
    p: [itinerary_flight_1_dict[p], itinerary_flight_2_dict[p]] for p in itinerary
}

## Delta: 1 if flight leg i is in path p, 0 otherwise
delta = {}
for p in itinerary:
    for i in flight_numbers:
        delta[i, p] = 1 if i in itinerary_flights[p] else 0

# berekening Q_i dus vraag per vlucht
Q = {}
for i in flight_numbers:
    Q[i] = sum(delta[i, p] * itinerary_demand_dict[p] for p in itinerary)


model = Model("mix_flow_keypath")

## Decision variables
t = {}
for r in itinerary:
    for p in itinerary:
        t[r, p] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"t_{r}_{p}")

# Objective: minimize loss revenue for spillage
objective = quicksum(
    (itinerary_price_dict[p] - (recapture_dict[p, r] * itinerary_price_dict[r]))
    * t[p, r]
    for p in itinerary
    for r in itinerary
)

model.setObjective(objective, GRB.MINIMIZE)

model.update()

# ## Constraints
# ##Constraint 1: Capacity constraints:
for i in flight_numbers:
    model.addConstr(
        quicksum(delta[i, p] * t[p, r] for p in itinerary for r in itinerary)
        - quicksum(
            delta[i, p] * recapture_dict[r, p] * t[r, p]
            for r in itinerary
            for p in itinerary
        )
        >= Q[i] - capacity_dict[i],
        name=f"spill_{i}",
    )

# ## Constraint 2: Number of passengers is lower than demand
for p in itinerary:
    model.addConstr(
        quicksum(t[p, r] for r in itinerary) <= itinerary_demand_dict[p],
        name=f"demand_{p}",
    )


model.update()

model.optimize()

model.write("gurobi_model_question2b_keypath.lp")

if model.Status == GRB.OPTIMAL:
    print("\nOptimal t[p,r] values:")
    for p in itinerary:
        for r in itinerary:
            val = t[p, r].X
            if abs(val) > 1e-6:  # only show non-zero flows
                print(f"t[{p},{r}] = {val}")

    ## print number of nonzero t[p,r] values
    nonzero_count = sum(
        1 for p in itinerary for r in itinerary if abs(t[p, r].X) > 1e-6
    )
    print(f"Number of nonzero t[p,r] values: {nonzero_count}")

    ## number of passengers spilled to an path with a recapture rate of 0
    spilled_no_recapture = sum(
        t[p, r].X for p in itinerary for r in itinerary if recapture_dict[p, r] == 0
    )

    print(
        f"Number of passengers spilled to a path with a recapture rate of 0: {spilled_no_recapture}"
    )

    ## number of passengers spilled to an path with a recapture rate > 0
    spilled_with_recapture = sum(
        t[p, r].X for p in itinerary for r in itinerary if recapture_dict[p, r] > 0
    )
    print(
        f"Number of passengers spilled to a path with a recapture rate > 0: {spilled_with_recapture}"
    )

    print(f"\nOptimal objective value: {model.ObjVal}")
