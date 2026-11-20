"""Bounded *numerical* demonstration of a constructive LF density lemma.

Mathematical target (proven in the accompanying analytic note):
finite complex/real spans of rational translates and rational dilates of
one even compactly supported C-infinity mollifier are dense in
D(R)=C_c^infinity(R) in its usual LF test-function topology.

This executable does not prove differentiability, LF convergence, or
the Weil-form hypotheses; it approximates ideal integrals with floating
point arithmetic. Reported analytical error bounds are CONDITIONAL on
caller-supplied supremum bounds and assume exact normalization/evaluation.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import json
import math
from pathlib import Path
from typing import Callable


def unnormalized_bump(x: float) -> float:
    """C-infinity even bump supported on [-1,1] (exact definition; FP evaluation)."""
    if not math.isfinite(x):
        raise ValueError("x must be finite")
    if abs(x) >= 1:
        return 0.0
    return math.exp(-1.0 / (1.0 - x*x))


@lru_cache(maxsize=1)
def _numerical_bump_mass() -> float:
    """Simpson approximation; NOT an interval-certified normalizing integral."""
    panels = 8192
    step = 2.0/panels
    total = math.fsum(
        (1 if i in (0, panels) else (4 if i % 2 else 2))
        * unnormalized_bump(-1.0 + i*step)
        for i in range(panels + 1)
    )
    return total*step/3.0


def numerical_mollifier(x: float, epsilon: Fraction) -> float:
    """Numerical evaluation of phi_epsilon; no rigorous roundoff claim."""
    eps = float(epsilon)
    if not 0 < eps <= 1 or not math.isfinite(x):
        raise ValueError("epsilon in (0,1] and finite x required")
    return unnormalized_bump(x/eps) / (eps*_numerical_bump_mass())


def scheduled_parameters(n: int) -> tuple[Fraction, Fraction]:
    """Theoretical diagonal sequence: epsilon=1/n, h=2^(-n^2)."""
    if type(n) is not int or not 2 <= n <= 64:
        raise ValueError("n must be an integer in [2,64]")
    return Fraction(1, n), Fraction(1, 2**(n*n))


def conditional_c0_error_bound(
    epsilon: Fraction, step: Fraction, sup_f: float, sup_fprime: float
) -> float:
    """Conditional exact-construction C0 bound given VALIDATED external M0/M1.

    ||S_(e,h)f-f||_infty <= e*M1 + h*(M1 + 3*M0/e),
    since integral |phi'| <= 3 for the normalized bump.
    This is NOT a certificate for the floating-point numerical evaluator.
    """
    e, h = float(epsilon), float(step)
    if not all(math.isfinite(t) for t in (e, h, sup_f, sup_fprime)):
        raise ValueError("finite bounds and parameters required")
    if not 0 < e <= 1 or h <= 0 or min(sup_f, sup_fprime) < 0:
        raise ValueError("positive scales and nonnegative upper bounds required")
    return e*sup_fprime + h*(sup_fprime + 3*sup_f/e)


@dataclass(frozen=True)
class DiscreteBumpSum:
    """A finite rational-center/radius bump sum with FLOATING coefficients.

    The mathematical support enclosure assumes f is supported in [-R,R].
    The program can sample but CANNOT validate that function-level property.
    """
    epsilon: Fraction
    step: Fraction
    support_radius: float
    sample_coefficients: tuple[tuple[int, float], ...]

    @property
    def support_enclosure(self) -> tuple[float, float]:
        bound = self.support_radius + float(self.epsilon)
        return -bound, bound

    def evaluate(self, x: float) -> float:
        if not math.isfinite(x):
            raise ValueError("evaluation point must be finite")
        return math.fsum(
            coefficient * numerical_mollifier(
                x - k*float(self.step), self.epsilon
            )
            for k, coefficient in self.sample_coefficients
        )


def build_approximation(
    f: Callable[[float], float], support_radius: float,
    epsilon: Fraction, step: Fraction, *, max_samples: int = 4097
) -> DiscreteBumpSum:
    """Approximate h * sum_k f(k*h) phi_epsilon(x-k*h).

    The caller ASSERTS support(f) subset [-support_radius,support_radius].
    Rational epsilon and step are required so the construction uses
    rational centers k*h and rational radius epsilon.
    """
    if not isinstance(epsilon, Fraction) or not isinstance(step, Fraction):
        raise ValueError("epsilon and step must be Fraction instances")
    if not math.isfinite(support_radius) or support_radius <= 0:
        raise ValueError("finite positive support radius required")
    if not 0 < epsilon <= 1 or step <= 0:
        raise ValueError("epsilon in (0,1] and positive step required")
    if type(max_samples) is not int or max_samples < 1:
        raise ValueError("positive integer max_samples required")
    radius = Fraction(str(support_radius))
    kmax = (radius.numerator*step.denominator
            + radius.denominator*step.numerator - 1) // (
                radius.denominator*step.numerator
            )
    if 2*kmax + 1 > max_samples:
        raise ValueError("sample budget exceeded; keep infinite sequence symbolic")
    samples: list[tuple[int, float]] = []
    h = float(step)
    for k in range(-kmax, kmax + 1):
        x = k*h
        if abs(x) > support_radius:
            continue
        val = float(f(x))
        if not math.isfinite(val):
            raise ValueError("f must be finite at sampled points")
        if val != 0.0:
            samples.append((k, h*val))
    return DiscreteBumpSum(
        epsilon, step, support_radius, tuple(samples)
    )


def demo() -> dict:
    """Bounded reproducible approximation only, not a mathematical certificate."""
    f = unnormalized_bump
    eps, step = Fraction(1, 5), Fraction(1, 80)
    approx = build_approximation(f, 1.0, eps, step)
    sites = (-1.25, -1.0, -0.5, 0.0, 0.5, 1.0, 1.25)
    return {
        "schema": "mathos.rh.lf_bump_core/1",
        "claim_scope": "FINITE_NUMERICAL_DEMONSTRATION_NOT_WEIL_DENSITY",
        "test_space": "D(R)=C_c^infinity(R), usual strict LF topology",
        "family": "finite real/complex linear combinations of normalized smooth-bump rational translates and rational dilates",
        "epsilon": str(eps),
        "rational_mesh": str(step),
        "terms": len(approx.sample_coefficients),
        "support_enclosure_conditional_on_input_support": list(approx.support_enclosure),
        "samples": [
            {"x":x, "f":f(x), "bump_sum":approx.evaluate(x)}
            for x in sites
        ],
        "conditional_exact_C0_bound_if_M0_le_1_M1_le_4": conditional_c0_error_bound(
            eps, step, 1.0, 4.0
        ),
        "external_supremum_assumptions_verified": False,
        "ideal_mollifier_normalization_rigorously_certified_by_code": False,
        "all_derivative_LF_convergence_checked_by_code": False,
        "RH_relevant_Weil_density_proved": False,
        "global_Weil_positivity_proved": False,
        "Riemann_hypothesis_proved": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(demo(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
