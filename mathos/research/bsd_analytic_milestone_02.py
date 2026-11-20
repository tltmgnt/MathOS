"""BSD milestone 02: classical central-order lower-bound *logic* audit.

EXTERNAL THEOREM ASSUMED: Gross--Zagier--Kolyvagin says analytic
rank 0 or 1 implies the equal algebraic rank for E/Q.
Hence algebraic rank >=2 implies analytic rank >=2.

NO analytic L-values, analytic ranks, rational rank certificates,
or proof of BSD are computed by this Python module.
"""
from __future__ import annotations

import json
from mathos.research.bsd_rank_two_family import invariants, evalp, audit as family_audit


def analytic_order_floor(algebraic_rank_floor: int, root_number: int | None = None) -> int:
    """Logical floor implied by external rank-0/1 theorem + functional equation.

    A floor is a proved *conditional implication*, not a computed analytic rank.
    If algebraic rank >= 1, analytic rank cannot be zero; if algebraic rank
    >= 2, analytic rank cannot be zero or one.

    root_number=-1: analytic order must be odd;
    root_number=+1: analytic order must be even.
    """
    if type(algebraic_rank_floor) is not int or algebraic_rank_floor < 0:
        raise ValueError("algebraic rank lower bound must be a nonnegative exact integer")
    if root_number is not None and (
        type(root_number) is not int or root_number not in (-1, 1)
    ):
        raise ValueError("root number must be -1, +1 or unknown (None)")
    minimum = min(algebraic_rank_floor, 2)
    if root_number == -1 and minimum % 2 == 0:
        minimum += 1
    if root_number == 1 and minimum % 2 == 1:
        minimum += 1
    return minimum


def possible_under_external_low_rank_theorem(
    algebraic_rank: int, analytic_rank: int
) -> bool:
    """Truth-table abstraction of the *input* theorem, not a proof of it."""
    if any(type(x) is not int or x < 0 for x in (algebraic_rank, analytic_rank)):
        raise ValueError("nonnegative exact integer ranks required")
    return analytic_rank >= 2 or algebraic_rank == analytic_rank


def audit() -> dict:
    c4, delta = invariants()
    assert tuple(c4) == (112, 80, 16)
    assert tuple(delta) == (389, 696, 472, 144, 16)
    assert evalp(delta, 0) == 389 and evalp(delta, 2) == 5077
    parent = family_audit()
    assert parent["BSD_proved"] is False
    assert parent["novelty_established"] is False

    # Inspect the finite logical theorem consequence for hypothetical ranks.
    for floor in range(0, 10):
        for sign in (None, 1, -1):
            implied_floor = analytic_order_floor(floor, sign)
            valid = []
            for algebraic in range(floor, 20):
                for analytic in range(0, 20):
                    if not possible_under_external_low_rank_theorem(algebraic, analytic):
                        continue
                    if sign is not None and (-1 if analytic % 2 else 1) != sign:
                        continue
                    valid.append(analytic)
            assert valid, (floor, sign)
            assert min(valid) == implied_floor, (floor, sign, min(valid))
    assert analytic_order_floor(2) == 2
    assert analytic_order_floor(2, -1) == 3
    assert analytic_order_floor(2, 1) == 2
    assert analytic_order_floor(3) == 2  # Higher rank does NOT imply >=3 via GZK alone.
    assert analytic_order_floor(3, -1) == 3
    return {
        "milestone": "MATHOS-BSD-ANALYTIC-DOUBLE-ZEROS-02",
        "status": "CLASSICAL_COROLLARY_LOGIC_AUDIT",
        "symbolic_invariants_checked": True,
        "rank_two_sections_independent_proof_uses_external_LMFDB": True,
        "silverman_specialization_used_as_external_theorem": True,
        "GZK_low_analytic_rank_used_as_external_theorem": True,
        "cofinite_family_analytic_order_at_least_2_is_theorem_corollary": True,
        "explicit_specialization_exception_set_computed": False,
        "analytic_L_function_evaluated": False,
        "exact_analytic_rank_for_generic_fiber_computed": False,
        "rank_equality_for_infinite_family_proved": False,
        "mathematical_novelty_established": False,
        "BSD_proved": False,
    }


def main() -> None:
    print(json.dumps(audit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
