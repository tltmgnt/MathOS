"""Millennium Ω: bounded seven-track research orchestration and proof-state governance.

This package does not prove Millennium problems or bypass MathOS's canonical
proof obligations. All model outputs remain research-only.
"""

from .framework import (
    ENGINES,
    STAGES,
    AssuranceError,
    audit_packet,
    run_engine,
    run_framework,
)

__all__ = [
    "ENGINES", "STAGES", "AssuranceError",
    "audit_packet", "run_engine", "run_framework",
]
