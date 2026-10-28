"""HTTP integration tests for the Omega welfare API."""

import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from mathos.web import MathOSHandler


class TestOmegaWelfareAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), MathOSHandler)
        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()
        cls.base_url = (
            f"http://127.0.0.1:{cls.server.server_port}"
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def post_json(self, payload):
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + "/api/omega-welfare",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=5) as response:
                return (
                    response.status,
                    json.load(response),
                )
        except HTTPError as error:
            return (
                error.code,
                json.loads(error.read().decode("utf-8")),
            )

    def valid_payload(self):
        return {
            "times": [0, 1],
            "weights": [1],
            "rho": 0,
            "risk_penalty": 1,
            "governance_penalty": 1,
            "policies": {
                "Policy_A": {
                    "utilities": [[10, 10]],
                    "risks": [1, 1],
                    "governance": [1, 1],
                },
                "Policy_B": {
                    "utilities": [[6, 6]],
                    "risks": [1, 1],
                    "governance": [1, 1],
                },
            },
        }

    def test_valid_policy_request(self):
        status, result = self.post_json(
            self.valid_payload()
        )
        self.assertEqual(status, 200)
        self.assertIn("best_policy", result)
        self.assertIn("policy_scores", result)

    def test_expected_welfare_scores(self):
        status, result = self.post_json(
            self.valid_payload()
        )
        self.assertEqual(status, 200)

        scores = result["policy_scores"]
        self.assertAlmostEqual(scores["Policy_A"], 8)
        self.assertAlmostEqual(scores["Policy_B"], 4)

    def test_best_policy_selection(self):
        status, result = self.post_json(
            self.valid_payload()
        )
        self.assertEqual(status, 200)
        self.assertEqual(
            result["best_policy"],
            "Policy_A",
        )
        self.assertAlmostEqual(
            result["maximum_welfare"],
            8,
        )

    def test_rejects_empty_policies(self):
        payload = self.valid_payload()
        payload["policies"] = {}

        status, result = self.post_json(payload)
        self.assertEqual(status, 400)
        self.assertIn("error", result)

    def test_rejects_invalid_time_points(self):
        payload = self.valid_payload()
        payload["times"] = [1, 0]

        status, result = self.post_json(payload)
        self.assertEqual(status, 400)
        self.assertIn("error", result)

    def test_existing_homepage_still_works(self):
        with urlopen(
            self.base_url + "/",
            timeout=5,
        ) as response:
            page = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("MathOS", page)
            self.assertIn("Solve & Verify", page)


if __name__ == "__main__":
    unittest.main()
