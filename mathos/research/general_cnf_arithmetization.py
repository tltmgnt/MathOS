"""Bounded independent regression for arbitrary signed-CNF arithmetic semantics.

This evaluates an arithmetic circuit for a GIVEN assignment. It does not
provide a polynomial-time search procedure for satisfying assignments,
establish either side of P versus NP, or demonstrate novelty.
All integers in the circuit are 0/1 at every completed gate.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN_FILE = ROOT / "formal" / "GeneralCNFArithmetization.lean"


def validate_cnf(formula, variable_count):
    if type(variable_count) is not int or variable_count < 0:
        raise ValueError("variable_count must be nonnegative int")
    if not isinstance(formula, (tuple, list)):
        raise ValueError("CNF must be a list or tuple of clauses")
    for clause in formula:
        if not isinstance(clause, (tuple, list)):
            raise ValueError("each clause must be list or tuple")
        for literal in clause:
            if type(literal) is not int or literal == 0 or abs(literal) > variable_count:
                raise ValueError("signed literal must be nonzero and within variable indices")


def validate_assignment(assignment, variable_count):
    if not isinstance(assignment, (tuple, list)) or len(assignment) != variable_count:
        raise ValueError("assignment must match the declared number of variables")
    if any(type(value) is not int or value not in (0, 1) for value in assignment):
        raise ValueError("assignment values must be exact integer 0 or 1")


def _literal_value(lit, assignment):
    value = assignment[abs(lit) - 1]
    return value if lit > 0 else 1 - value


def cnf_truth(formula, assignment):
    validate_assignment(assignment, len(assignment))
    validate_cnf(formula, len(assignment))
    return all(
        any(_literal_value(lit, assignment) == 1 for lit in clause)
        for clause in formula
    )


def cnf_arithmetic_circuit(formula, assignment):
    """Nested factored integer OR and AND, never expanded as a polynomial."""
    validate_assignment(assignment, len(assignment))
    validate_cnf(formula, len(assignment))
    result = 1
    for clause in formula:
        clause_value = 0
        for lit in clause:
            x = _literal_value(lit, assignment)
            clause_value = x + clause_value - x * clause_value
            if clause_value not in (0, 1):
                raise AssertionError("invalid Boolean-indicator gate")
        result *= clause_value
        if result not in (0, 1):
            raise AssertionError("invalid conjunction-indicator gate")
    return result


def arithmetic_gate_count(formula, variable_count):
    """Each factored literal uses one OR gate and each clause one AND gate."""
    validate_cnf(formula, variable_count)
    return sum(len(clause) + 1 for clause in formula)


def verify_bounded(max_variables=3, max_clauses=2, max_clause_length=2):
    """Exhaustive but finite check of all ordered signed CNFs in this box."""
    limits = (max_variables, max_clauses, max_clause_length)
    if any(type(x) is not int for x in limits) or not (
        0 <= max_variables <= 3 and
        0 <= max_clauses <= 2 and
        0 <= max_clause_length <= 2
    ):
        raise ValueError("finite verification limited to variables<=3, clauses<=2, length<=2")

    results = []
    for variable_count in range(max_variables + 1):
        literals = tuple(range(1, variable_count + 1)) + tuple(
            -i for i in range(1, variable_count + 1)
        )
        clause_choices = tuple(
            tuple(p)
            for length in range(max_clause_length + 1)
            for p in itertools.product(literals, repeat=length)
        )
        assignments = tuple(itertools.product((0, 1), repeat=variable_count))
        formulas_checked = 0
        evaluations = 0
        satisfiable_formulas = 0
        for number_clauses in range(max_clauses + 1):
            for formula in itertools.product(clause_choices, repeat=number_clauses):
                formulas_checked += 1
                sat_truth = False
                sat_arithmetic = False
                for assignment in assignments:
                    evaluations += 1
                    truth = cnf_truth(formula, assignment)
                    arithmetic = cnf_arithmetic_circuit(formula, assignment)
                    if arithmetic != int(truth):
                        raise AssertionError(
                            f"CNF indicator mismatch: formula={formula}, assignment={assignment}"
                        )
                    sat_truth |= truth
                    sat_arithmetic |= arithmetic == 1
                if sat_truth != sat_arithmetic:
                    raise AssertionError("existential SAT equivalence failed")
                satisfiable_formulas += int(sat_truth)
                if arithmetic_gate_count(formula, variable_count) != (
                    sum(len(c) for c in formula) + len(formula)
                ):
                    raise AssertionError("gate bound is incorrect")
        expected_formulas = sum(len(clause_choices)**k for k in range(max_clauses + 1))
        if formulas_checked != expected_formulas:
            raise AssertionError("formula coverage mismatch")
        if evaluations != formulas_checked * len(assignments):
            raise AssertionError("assignment coverage mismatch")
        results.append({
            "variables": variable_count,
            "clause_choices": len(clause_choices),
            "formulas_checked": formulas_checked,
            "assignment_evaluations": evaluations,
            "satisfiable_formulas": satisfiable_formulas,
        })
    return {
        "attempt": "MathOS-MILLENNIUM-004-GENERAL-CNF-ARITHMETIZATION",
        "status": "FINITE_REGRESSION_ONLY",
        "scope": "all finite signed CNF formulas covered by the configured tiny finite box",
        "formal_all_formula_theorem": "MathOS.cnfFormulaValue_indicator",
        "formal_existence_equivalence": "MathOS.cnfHasWitness_iff",
        "formal_linear_gate_bound": "MathOS.cnfTotalGates_eq",
        "lean_source_sha256": hashlib.sha256(LEAN_FILE.read_bytes()).hexdigest(),
        "limits": {
            "max_variables": max_variables,
            "max_clauses": max_clauses,
            "max_clause_length": max_clause_length,
        },
        "results": results,
        "total_formula_assignment_pairs": sum(r["assignment_evaluations"] for r in results),
        "arbitrary_sat_polynomial_time_algorithm": False,
        "establishes_p_equals_np": False,
        "establishes_p_not_equals_np": False,
        "mathematical_novelty_established": False,
        "external_independent_review_completed": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-variables", type=int, default=3)
    p.add_argument("--max-clauses", type=int, default=2)
    p.add_argument("--max-clause-length", type=int, default=2)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    report = verify_bounded(args.max_variables, args.max_clauses, args.max_clause_length)
    content = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
