import unittest

from models.omega_welfare_solver import (
    evaluate_welfare,
    optimize_policies,
)


class TestOmegaWelfare(unittest.TestCase):

    def test_constant_welfare(self):
        result = evaluate_welfare(
            times=[0, 1, 2],
            utilities=[[10, 10, 10]],
            weights=[1],
            risks=[0, 0, 0],
            governance=[0, 0, 0],
            rho=0,
            risk_penalty=0,
            governance_penalty=0,
        )
        self.assertAlmostEqual(result, 20)

    def test_risk_penalty(self):
        result = evaluate_welfare(
            times=[0, 1],
            utilities=[[10, 10]],
            weights=[1],
            risks=[2, 2],
            governance=[0, 0],
            rho=0,
            risk_penalty=3,
            governance_penalty=0,
        )
        self.assertAlmostEqual(result, 4)

    def test_policy_optimization(self):
        policies = {
            "policy_A": {
                "utilities": [[10, 10]],
                "risks": [0, 0],
                "governance": [0, 0],
            },
            "policy_B": {
                "utilities": [[15, 15]],
                "risks": [0, 0],
                "governance": [0, 0],
            },
        }

        result = optimize_policies(
            policies,
            times=[0, 1],
            weights=[1],
            rho=0,
            risk_penalty=0,
            governance_penalty=0,
        )

        self.assertEqual(result["best_policy"], "policy_B")
        self.assertAlmostEqual(result["maximum_welfare"], 15)

    def test_invalid_time_order(self):
        with self.assertRaises(ValueError):
            evaluate_welfare(
                times=[1, 0],
                utilities=[[10, 10]],
                weights=[1],
                risks=[0, 0],
                governance=[0, 0],
                rho=0,
                risk_penalty=0,
                governance_penalty=0,
            )


if __name__ == "__main__":
    unittest.main()
