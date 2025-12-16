##################################################################################################################
# THIS MODEL IS JUST THE FIRST ITERATION OF THE COLUMN GENERATION PROCEDURE


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


## start Restricted master problem
model = Model("mix_flow_keypath_restricted_master")

t = {}
for p in itinerary:
    t[p, len(itinerary)] = model.addVar(
        vtype=GRB.CONTINUOUS, lb=0, name=f"t_{p}_fictitious"
    )

# (recapture_dict[p, r] * itinerary_price_dict[r])

# Objective: minimize loss revenue for spillage
objective = quicksum(
    (itinerary_price_dict[p] - (0)) * t[p, len(itinerary)] for p in itinerary
)

model.setObjective(objective, GRB.MINIMIZE)

model.update()

# - quicksum(
#             delta[i, p] * recapture_dict[r, p] * t[r, p]
#             for r in itinerary
#             for p in itinerary

## Constraints
##Constraint 1: Capacity constraints:
spill_constrs = {}
for i in flight_numbers:
    spill_constrs[i] = model.addConstr(
        quicksum(delta[i, p] * t[p, len(itinerary)] for p in itinerary)
        >= Q[i] - capacity_dict[i],
        name=f"spill_{i}",
    )

# ## Constraint 2: Number of passengers is lower than demand
demand_constrs = {}
for p in itinerary:
    demand_constrs[p] = model.addConstr(
        t[p, len(itinerary)] <= itinerary_demand_dict[p],
        name=f"demand_{p}",
    )


## Constraint 3: Non-negativity (already defined in variable creation)

# model.params.MIPGap = 0

model.update()

model.optimize()

model.write("gurobi_model_keypath_RMP.lp")

if model.Status == GRB.OPTIMAL:
    print("\nOptimal t[p,fictitious] values:")
    for p in itinerary:
        val = t[p, len(itinerary)].X
        if abs(val) > 1e-6:  # only show non-zero flows
            print(f"t[{p},fictitious] = {val}")

    ## print number of nonzero t[p,fictitious] values
    nonzero_count = sum(1 for p in itinerary if abs(t[p, len(itinerary)].X) > 1e-6)
    print(f"Number of nonzero t[p,fictitious] values: {nonzero_count}")

    ## number of passengers spilled to an path with a recapture rate of 0
    spilled_no_recapture = sum(t[p, len(itinerary)].X for p in itinerary)

    print(
        f"Number of passengers spilled to a path with a recapture rate of 0: {spilled_no_recapture}"
    )

    print(f"\nOptimal objective value: {model.ObjVal}")

    ##dual variables
    ## pi: marginal value of addign one extra seat on flight i
    ## sigma: marginal value of transporting one extra passenger on itinerary p

    pi_dict = {}

    for i in flight_numbers:
        dual_val = spill_constrs[i].Pi
        # if abs(dual_val) > 1e-6:
        #     #print(f"Constraint spill_{i}: dual = {dual_val}")
        #     pi_dict[i] = dual_val
        pi_dict[i] = dual_val

    sigma_dict = {}

    print("\nDual variables for demand constraints:")
    for p in itinerary:
        dual_val = demand_constrs[p].Pi
        # if abs(dual_val) > 1e-6:
        #     #print(f"Constraint demand_{p}: dual = {dual_val}")
        sigma_dict[p] = dual_val

    # print(pi_dict)
    # print(sigma_dict)

c = {}
columns_to_add = []
for p in itinerary:
    for r in itinerary:
        if recapture_dict[p, r] > 0:
            c[p, r] = (
                itinerary_price_dict[p]
                - sum(pi_dict[i] * delta[i, p] for i in flight_numbers)
            ) - (
                recapture_dict[p, r]
                * (
                    itinerary_price_dict[r]
                    - sum(pi_dict[j] * delta[j, r] for j in flight_numbers)
                )) - sigma_dict[p]
            if c[p, r] != 0 and c[p, r] < 0:
                print(f"c[{p},{r}] = {c[p,r]}")
                columns_to_add.append((p, r))

print(columns_to_add)

## Second iteration: add columns with negative reduced cost
    



