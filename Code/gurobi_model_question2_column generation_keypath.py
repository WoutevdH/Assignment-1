from data_loader import *
from gurobipy import Model, Var, GRB, quicksum
from collections import defaultdict
from keypath_model_functions import run_model, get_dual_values, pricing_problem
import time

## === iterated column generation process === ##
start_time = time.time()


# Set up variables to record progress over iterations
# Objective values per iteration
objective_values = []
number_of_columns = []


### First iteration
## Restricted columns to include: all (p, p) and (p, 1000)
start_columns = []
for p in itinerary:
    start_columns.append((p, p))
    start_columns.append((p, 1000))

iterations = 0
all_columns = list(start_columns)


## Iterative column generation loop
while True:

    print(f"This is iteration number {iterations}:")

    model, x = run_model(all_columns, gurobi_output=False)
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
        print("No more columns to add, final number of iterations:", iterations)
        print(f"Final objective value: {model.ObjVal}")
        print(f"Final decision variables:")
        for v in model.getVars():
            if v.X > 1e-6:
                print(f"{v.VarName}: {v.X}")

        # print non zero x[p,r] values
        print(f"\nFinal x[p,r] values:")
        for (p, r), val in x.items():
            if abs(val) > 1e-6:
                ...
                # print(f"x[{p},{r}] = {val}")

        print(
            f'Number of passengers spilled to fictitious itinerary: {sum(v.X for v in model.getVars() if "_1000" in v.VarName)}'
        )
        print(
            f'Number of spilled to on real itineraries: {sum(v.X for v in model.getVars() if "_1000" not in v.VarName)}'
        )
        print(
            f"Number transportred on to real itineraries: {sum(x[p,r] for (p,r) in x if r != 1000)}"
        )

        print(f'Number of passengers transported on preferred itineraries: {sum(x[p,r] for (p,r) in x if p == r and r != 1000)}')
        print(f"Sum of all passengers accounted for: {sum(x[p,r] for (p,r) in x)}")

        break

    if iterations == 10:
        print("Reached maximum number of iterations (10). Terminating.")
        break

    new_columns = list(slack_columns_to_add.keys())
    all_columns = all_columns + new_columns

    iterations += 1

end_time = time.time()
runtime = end_time - start_time

print(f'The objective values over iterations: {objective_values}')
print(f'Number of columns over iterations: {number_of_columns}')
print(f"\nTotal runtime: {runtime:.4f} seconds")
