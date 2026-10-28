import html"""HTTP integration tests for the MathOS web interface."""

import http.client
import threading
import unittest
from http.server import HTTPServer
from urllib.parse import urlencode

from mathos.web import MathOSHandler


class TestMathOSHTTP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(
            ("127.0.0.1", 0),
            MathOSHandler,
        )

        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method, path="/", body=None, headers=None):
        connection = http.client.HTTPConnection(
            "127.0.0.1",
            self.server.server_port,
            timeout=5,
        )

        try:
            connection.request(
                method,
                path,
                body=body,
                headers=headers or {},
            )

            response = connection.getresponse()

            return (
                response.status,
                response.read().decode("utf-8"),
            )
        finally:
            connection.close()

    def test_homepage_loads(self):
        status, page = self.request("GET")

        self.assertEqual(status, 200)
        self.assertIn("<title>MathOS</title>", page)
        self.assertIn("Solve & Verify", page)

    def test_equation_solution(self):
        body = urlencode({
            "problem": "2x + 5 = 13",
        })

        status, page = self.request(
            "POST",
            body=body,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded",
            },
        )

        self.assertEqual(status, 200)
        self.assertIn('"answer": "4"', html.unescape(page))
        self.assertIn("Error: Unsupported equation", page)
        )

    def test_invalid_equation(self):
        body = urlencode({
            "problem": "x^2 = 4",
        })

        status, page = self.request(
            "POST",
            body=body,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded",
            },
        )

        self.assertEqual(status, 200)
        self.assertIn("Unsupported equation", page)

    def test_html_escaping(self):
        body = urlencode({
            "problem": "<script>alert(1)</script>",
        })

        status, page = self.request(
            "POST",
            body=body,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded",
            },
        )

        self.assertEqual(status, 200)
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)


if __name__ == "__main__":
    unittest.main()
