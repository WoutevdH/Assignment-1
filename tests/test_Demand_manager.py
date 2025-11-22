import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest
from Code.Demand import Demand


class TestDemand(unittest.TestCase):
    def test_get_demand(self):

        demand = Demand(2021, "Problem 1 - Data/Problem 1 - Data/DemandGroup2.xlsx")

        demand = demand.get_demand("EHAM", "EPWA")
        assert demand == 52


if __name__ == "__main__":
    unittest.main()
