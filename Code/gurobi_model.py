from pathlib import Path
import numpy as np
from data_loader import *
import pickle
from gurobipy import Model, Var, GRB, quicksum

BASE_DIR = Path(__file__).resolve().parent

## This is importing the earlier calculated demand for 2026 without recalculating it
with open(BASE_DIR / "Estimated Data/demand_2026_dict.pkl", "rb") as file:
    demand_2026_dict = pickle.load(file)

## This is importang all the distances calculated earlier
with open(BASE_DIR / "Estimated Data/distance_dict.pkl", "rb") as file:
    distance_dict = pickle.load(file)

## This is importing all the yields calculated earlier
with open(BASE_DIR / "Estimated Data/yield_dict.pkl", "rb") as file:
    yield_dict = pickle.load(file)

## Importing airport data
## The index is the city names
(
    cities,
    airport_code,
    airport_lat,
    airport_lon,
    airport_runway_length,
    airport_available_slots,
) = airportdata_loader()

## Importing aircraft data
## The index is "Aircraft 1", "Aircraft 2", ...
(
    aircraft_types,
    speed_dict,
    seats_dict,
    TAT_dict,
    range_dict,
    runway_req_dict,
    weekly_lease_dict,
    fixed_cost_dict,
    time_cost_param_dict,
    fuel_cost_param_dict,
) = aircraft_data_loader()

f = 1.42  # fuel cost

g = {city: (0 if city == "Paris" else 1) for city in cities}

LF = 0.75  # load factor

BT = 70  # operating hours per week per aircraft

model = Model("network_fleet_development")

## Decision variables

# x_ij: direct  flow of passengers from airport i to airport j
# w_ij: flow from airport i to airport j with transfer at the hub
x = {}
w = {}
for i in cities:
    for j in cities:
        x[i, j] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"x_{i}_{j}")
        w[i, j] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"w_{i}_{j}")


# z_ijk: number of flights from airport i to airport j using aircraft k
z = {}
for i in cities:
    for j in cities:
        for k in aircraft_types:
            z[i, j, k] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"z_{i}_{j}_{k}")


# AC_k: number of aircraft of type k to be leased
AC = {}
for k in aircraft_types:
    AC[k] = model.addVar(vtype=GRB.INTEGER, lb=0, name=f"AC_{k}")


# Objective: maximize profit
objective = (
    quicksum(
        (distance_dict[i, j] * yield_dict[i, j]) * (x[i, j] + w[i, j])
        for i in cities
        for j in cities
    )
    - quicksum(
        z[i, j, k]
        * 0.7
        * (
            fixed_cost_dict[k]
            + time_cost_param_dict[k] * (distance_dict[i, j] / speed_dict[k])
            + ((fuel_cost_param_dict[k] * f * distance_dict[i, j]) / 1.5)
        )
        for k in aircraft_types
        for i in cities
        for j in cities
    )
    - quicksum(weekly_lease_dict[k] * AC[k] for k in aircraft_types)
)


model.setObjective(objective, GRB.MAXIMIZE)

model.update()

## Constraints
# Constraint 1: Demand satisfaction
for i in cities:
    for j in cities:
        model.addConstr(
            x[i, j] + w[i, j] <= demand_2026_dict[i, j], name=f"demand_{i}_{j}"
        )

# Constraint 2: ensure w_ij is only nonzero if there is a transfer at the hub
for i in cities:
    for j in cities:
        model.addConstr(
            w[i, j] <= demand_2026_dict[i, j] * (g[i] * g[j]),
            name=f"hub_transfer_{i}_{j}",
        )

# Constraint 3: All flights go via the hub
for i in cities:
    for j in cities:
        for k in aircraft_types:
            model.addConstr(z[i, j, k] * g[i] * g[j] == 0, name=f"via_hub_{i}_{j}_{k}")

# Constraint 4: capacity check considering direct and transfer passengers
for i in cities:
    for j in cities:
        model.addConstr(
            x[i, j]
            + quicksum(w[i, m] * (1 - g[j]) for m in cities if m != i and m != j)
            + quicksum(w[m, j] * (1 - g[i]) for m in cities if m != i and m != j)
            <= quicksum(z[i, j, k] * seats_dict[k] * LF for k in aircraft_types),
            name=f"capacity_{i}_{j}",
        )

# Constraint 5: continuity constraint of aircrafts
for i in cities:
    for k in aircraft_types:
        model.addConstr(
            quicksum(z[i, j, k] for j in cities)
            == quicksum(z[j, i, k] for j in cities),
            name=f"aircraft_continuity_{i}_{k}",
        )

# Constraint 6: aircraft utilization constraint
for k in aircraft_types:
    model.addConstr(
        quicksum(
            ((distance_dict[i, j] / speed_dict[k]) + (TAT_dict[k] / 60)) * z[i, j, k]
            for i in cities
            for j in cities
        )
        <= BT * AC[k],
        name=f"aircraft_utilization_{k}",
    )

# Constraint 7: range constraint
for i in cities:
    for j in cities:
        if i != j:
            for k in aircraft_types:
                if distance_dict[i, j] <= range_dict[k]:
                    a = 10000  # big M
                else:
                    a = 0
                model.addConstr(z[i, j, k] <= a, name=f"range_{i}_{j}_{k}")


# # # Constraint 8: runway length constraint
for i in cities:
    for j in cities:
        if i != j:
            for k in aircraft_types:
                if (
                    runway_req_dict[k] <= airport_runway_length[i]
                    and runway_req_dict[k] <= airport_runway_length[j]
                ):
                    b = 10000  # big M
                else:
                    b = 0
                model.addConstr(z[i, j, k] <= b, name=f"runway_{i}_{j}_{k}")

# Constraint 9: slot constraint
for i in cities:
    if i == "Paris":
        continue
    model.addConstr(
        quicksum(z[i, j, k] for j in cities for k in aircraft_types)
        <= airport_available_slots[i],
        name=f"slot_constraint_{i}",
    )

model.params.MIPGap = 0.002


model.update()

model.optimize()


model.write("network_fleet_development.lp")

if model.status == GRB.OPTIMAL:
    print("Optimal objective value:", model.objVal)
    for v in model.getVars():
        if v.x > 0:
            print(f"{v.varName}: {v.x}")

    # --- Sum of all x[i,j] ---
    sum_x = sum(v.x for v in model.getVars() if v.varName.startswith("x_"))
    print("\nTotal direct passengers (sum of x):", sum_x)

    # --- Sum of all w[i,j] ---
    sum_w = sum(v.x for v in model.getVars() if v.varName.startswith("w_"))
    print("Total transfer passengers (sum of w):", sum_w)

    # --- Sum of all z[i,j,k] ---
    sum_z = sum(v.x for v in model.getVars() if v.varName.startswith("z_"))
    print("Total number of flights (sum of z):", sum_z)
