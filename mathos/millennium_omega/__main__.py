"""CLI for bounded Millennium Ω evidence generation (never proof promotion).

python -m mathos.millennium_omega --output artifacts/millennium-omega/report.json
python -m mathos.millennium_omega --engine riemann
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .framework import ENGINES, audit_packet, run_framework


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=["all", *ENGINES], default="all")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    packet = run_framework()
    audit_packet(packet)
    result = (
        packet if args.engine == "all" else
        next(e for e in packet["engines"] if e["engine"] == args.engine)
    )
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
