"""
MathOS Command-Line Interface.

Run supported mathematical problems without
an API key or internet connection.
"""

import argparse
import json

from mathos.core import MathOS


def main():
    parser = argparse.ArgumentParser(
        description="MathOS mathematical reasoning interface"
    )

    parser.add_argument(
        "problem",
        help='Equation to solve, e.g. "2x + 5 = 13"',
    )

    parser.add_argument(
        "--domain",
        default="mathematics",
        choices=sorted(MathOS.SUPPORTED_DOMAINS),
        help="Problem domain",
    )

    args = parser.parse_args()

    # Offline mode supports deterministic mathematics only.
    if args.domain != "mathematics":
        parser.error(
            "Offline mode currently supports mathematics only. "
            "General AI reasoning requires a configured model."
        )

    system = MathOS()

    try:
        result = system.solve(
            args.problem,
            domain=args.domain,
        )
    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
