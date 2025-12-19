## Group 2:
## Ivo Aben                 5099471
## Martijn Damman           5412633
## Wouter van der Hoorn     5370566

## This file contains the Gurobi model for question 2 of the assignment, implementing the normal mix flow model.


from pathlib import Path
import numpy as np
from data_loader import *
import pickle
from gurobipy import Model, Var, GRB, quicksum
import time

start_time = time.time()

BASE_DIR = Path(__file__).resolve().parent

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

## Set P_p set of itineraries r that can recapture passengers from itinerary p
itinerary_with_recapture = list(set([p for p in itinerary for r in itinerary if recapture_dict[p, r] != 0]))
## Same thing as above but in dictionary form


model = Model("normal_mix_flow")

## Decision variables
x = {}
for p in itinerary:
    for r in itinerary:
        x[p, r] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"x_{p}_{r}")

# Objective: maximum revenue for carrying all passengers
objective = quicksum(itinerary_price_dict[r] * x[p, r] 
       for p in itinerary 
       for r in itinerary)

model.setObjective(objective, GRB.MAXIMIZE)

model.update()

# ## Constraints
# ##Constraint 1: Capacity constraints:
for i in flight_numbers:
    model.addConstr(
        quicksum(delta[i, r] * x[p, r] for p in itinerary for r in itinerary) <= capacity_dict[i],
        name=f"capacity_{i}",
    )
        
# ## Constraint 2: Number of passengers is lower than demand
for p in itinerary:
    model.addConstr(
        quicksum((x[p, r] / recapture_dict[p, r]) for r in itinerary if recapture_dict[p, r] > 0) <= itinerary_demand_dict[p])
    
## Constraint 3: passengers can only be recaptured to itenaries that are allowed
for p in itinerary:
    for r in itinerary:
        if recapture_dict[p, r] == 0:
            model.addConstr(x[p, r] == 0, name=f"no_recapture_{p}_{r}")

model.update()

model.optimize()

model.write(str(BASE_DIR / "LP files/gurobi_model_question2_normal_mix_flow.lp"))

if model.Status == GRB.OPTIMAL:
    #print("\nOptimal x[p,r] values:")
    for p in itinerary:
        for r in itinerary:
            val = x[p, r].X
            if abs(val) > 1e-6:  # only show non-zero flows
                ...
                #print(f"x[{p},{r}] = {val}")

    ## print number of nonzero x[p,r] values
    nonzero_count = sum(
        1 for p in itinerary for r in itinerary if abs(x[p, r].X) > 1e-6
    )
    
    print(f'The optimal objective value is: {model.ObjVal}')

    print(f'Number of passengers not transported at all (spilled to fictious itinerary): {sum(itinerary_demand_dict[p] for p in itinerary) - sum(x[p, r].X for p in itinerary for r in itinerary if recapture_dict[p, r] > 0)}')

    print(f'Number of passengers spilled to real itineraries: {sum(x[p, r].X for p in itinerary for r in itinerary if recapture_dict[p, r] > 0 and p != r)}')

    print(f'Number of passengers transported on real itineraries: {sum(x[p, r].X for p in itinerary for r in itinerary if recapture_dict[p, r] > 0)}')

    print(f'Number of passengers travelling on preferred itineraries: {sum(x[p, p].X for p in itinerary)}')


end_time = time.time()
runtime = end_time - start_time

print(f"Runtime of the model: {runtime} seconds")

