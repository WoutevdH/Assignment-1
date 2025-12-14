from data_loader import *
from gurobipy import Model, Var, GRB, quicksum
from collections import defaultdict
from keypath_model_functions import run_model, get_dual_values, pricing_problem

## === iterated column generation process === ##


#Set up variables to record progress over iterations
# Objective values per iteration
objective_values = []
number_of_columns = []


### First iteration
## Restricted columns to include: all (p, p) and (p, 1000)
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

## Iterative column generation loop
while True:
    
       
    iterations += 1
    print(f"This is iteration number {iterations}:")

    new_columns = list(slack_columns_to_add.keys())
    all_columns = all_columns + new_columns

    model = run_model(all_columns)
    duals_capacity_pi, duals_demand_sigma = get_dual_values(model)
    slack_columns, slack_columns_to_add = pricing_problem(
        duals_capacity_pi, duals_demand_sigma
    )

    if model.Status == GRB.OPTIMAL:
        print(f"\nOptimal objective value after adding columns: {model.ObjVal}")
        print(f"Number of columns in the model: {len(all_columns)}")

        objective_values.append(model.ObjVal)
        number_of_columns.append(len(all_columns))

        print("\nColumns with negative reduced cost to add:")
        for (p, r), slack in slack_columns_to_add.items():
            print(f"Column ({p}, {r}): slack = {slack}")

    if not slack_columns_to_add:
        print("No more columns to add. Terminating.")
        break

    if iterations == 10:
        print("Reached maximum number of iterations (10). Terminating.")
        break


print(objective_values)
print(number_of_columns)