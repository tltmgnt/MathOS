"""Automated tests for the MathOS web interface."""

import unittest
from io import BytesIO
from unittest.mock import patch

from mathos.web import MathOSHandler, PAGE


class TestMathOSWeb(unittest.TestCase):

    def test_page_has_title(self):
        self.assertIn("<title>MathOS</title>", PAGE)

    def test_page_has_equation_input(self):
        self.assertIn('name="problem"', PAGE)

    def test_page_has_submit_button(self):
        self.assertIn("Solve & Verify", PAGE)

    def test_page_has_result_placeholder(self):
        self.assertIn("{result}", PAGE)

    def test_page_rendering_preserves_css(self):
        rendered = PAGE.replace(
            "{result}",
            "Answer: 4",
        )

        self.assertIn("Answer: 4", rendered)
        self.assertIn("font-family:", rendered)

    def test_mathematical_engine_integration(self):
        from mathos.core import MathOS

        result = MathOS().solve(
            "2x + 5 = 13",
            domain="mathematics",
        )

        self.assertEqual(result.answer, "4")
        self.assertEqual(
            result.verification_status,
            "verified",
        )

    def test_invalid_equation_rejected(self):
        from mathos.core import MathOS

        with self.assertRaises(ValueError):
            MathOS().solve(
                "x^2 = 4",
                domain="mathematics",
            )


if __name__ == "__main__":
    unittest.main()
