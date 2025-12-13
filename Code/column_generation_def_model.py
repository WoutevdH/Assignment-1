from data_loader import *
from gurobipy import Model, Var, GRB, quicksum
from collections import defaultdict


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

## Fictitious itinerary index 1000
## Delta: 1 if flight leg i is in path p, 0 otherwise
## Set delta to 0 for fictitious itinerary 1000

delta = {}
for p in itinerary:
    for i in flight_numbers:
        delta[i, p] = 1 if i in itinerary_flights[p] else 0

for i in flight_numbers:
    delta[i, 1000] = 0


# berekening Q_i dus vraag per vlucht
Q = {}
for i in flight_numbers:
    Q[i] = sum(delta[i, p] * itinerary_demand_dict[p] for p in itinerary)

## Set recapture_dict[p, r] = 1.0 if p == r
for p in itinerary:
    for r in itinerary:
        if p == r:
            recapture_dict[p, r] = 1.0

for p in itinerary:
    recapture_dict[p, 1000] = 1.0

itinerary_price_dict[1000] = 0.0


def run_model(columns_included):

    model = Model("restricted_master_problem")

    t = {}
    for p, r in columns_included:
        t[p, r] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name=f"t_{p}_{r}")

    # objective:
    objective = quicksum(
        (itinerary_price_dict[p] - recapture_dict[p, r] * itinerary_price_dict[r])
        * t[p, r]
        for p, r in columns_included
    )

    model.setObjective(objective, GRB.MINIMIZE)

    ## Constraint 1: Capacity constraints:
    for i in flight_numbers:
        model.addConstr(
            quicksum(delta[i, p] * t[p, r] for p, r in columns_included)
            - quicksum(
                delta[i, p] * recapture_dict[r, p] * t[r, p]
                for r, p in columns_included
            )
            >= Q[i] - capacity_dict[i],
            name=f"capacity_{i}",
        )

    grouped_columns = defaultdict(list)
    for p, r in columns_included:
        grouped_columns[p].append(r)

    ## Constraint 2: Demand constraints
    for p, r_list in grouped_columns.items():
        model.addConstr(
            quicksum(t[p, r] for r in r_list) <= itinerary_demand_dict[p],
            name=f"demand_{p}",
        )

    # for p, r in columns_included:
    #     if r == 1000:
    #         continue
    #     model.addConstr(
    #         quicksum(t[p, r] for r in itinerary if (p, r) in columns_included)
    #         <= itinerary_demand_dict[p],
    #         name=f"demand_{p}",
    #     )

    model.optimize()

    return model


def get_dual_values(model):
    duals_capacity_pi = {}
    duals_demand_sigma = {}

    for constr in model.getConstrs():
        if constr.ConstrName.startswith("capacity_"):
            flight_i = constr.ConstrName.split("_")[1]
            duals_capacity_pi[flight_i] = constr.Pi
        elif constr.ConstrName.startswith("demand_"):
            path_p = int(constr.ConstrName.split("_")[1])
            duals_demand_sigma[path_p] = constr.Pi

    return duals_capacity_pi, duals_demand_sigma


def pricing_problem(duals_capacity_pi, duals_demand_sigma):
    slack_columns = {}
    slack_columns_to_add = {}

    for p in itinerary:
        for r in itinerary:
            if recapture_dict[p, r] > 0:
                reduced_cost = (
                    (
                        itinerary_price_dict[p]
                        - sum(
                            duals_capacity_pi[i] * delta[i, p] for i in flight_numbers
                        )
                    )
                    - (
                        recapture_dict[p, r]
                        * (
                            itinerary_price_dict[r]
                            - sum(
                                duals_capacity_pi[j] * delta[j, r]
                                for j in flight_numbers
                            )
                        )
                    )
                    - duals_demand_sigma[p]
                )
                if reduced_cost != 0:
                    slack_columns[p, r] = reduced_cost
                    if reduced_cost < -0.001:
                        slack_columns_to_add[p, r] = reduced_cost

    return slack_columns, slack_columns_to_add


### First iteration
## Restricted columns


start_columns = []
for p in itinerary:
    start_columns.append((p, p))
    start_columns.append((p, 1000))

model = run_model(start_columns)
duals_capacity_pi, duals_demand_sigma = get_dual_values(model)
slack_columns, slack_columns_to_add = pricing_problem(
    duals_capacity_pi, duals_demand_sigma
)




iterations = 0
all_columns = list(start_columns)

while True:
    iterations += 1
    print(f"Iteration {iterations}:")

    if iterations == 10:
        print("Reached maximum number of iterations (10). Terminating.")
        break

    if not slack_columns_to_add:
        print("No more columns to add. Terminating.")
        break

    new_columns = list(slack_columns_to_add.keys())
    all_columns = all_columns + new_columns

    model = run_model(all_columns)
    duals_capacity_pi, duals_demand_sigma = get_dual_values(model)
    slack_columns, slack_columns_to_add = pricing_problem(
        duals_capacity_pi, duals_demand_sigma
    )

    if model.Status == GRB.OPTIMAL:
        print(f"\nOptimal objective value after adding columns: {model.ObjVal}")

        print("\nColumns with negative reduced cost to add:")
        for (p, r), slack in slack_columns_to_add.items():
            print(f"Column ({p}, {r}): slack = {slack}")
