import Init

/-!
# Research attempt 005: a congruence fact for a synthetic Li-coefficient baseline.

Let q = (3+4i)/5. The Gaussian integer numerator (3+4i)^n
has imaginary coordinate congruent to 4 modulo 5 for ALL n >= 1.
In particular q^n != 1 for positive n, provided ordinary complex
arithmetic is interpreted as described in the accompanying paper.

This Lean file formalizes only the Gaussian-integer congruences.
It neither defines zeta/Li coefficients nor proves the Riemann hypothesis.
-/

namespace MathOS

/-- Real and imaginary integer coordinates of (3 + 4i)^n. -/
def liBaseNumerator : Nat → Int × Int
  | 0 => (1, 0)
  | n + 1 =>
    let p := liBaseNumerator n
    (3 * p.1 - 4 * p.2, 4 * p.1 + 3 * p.2)

/-- The Gaussian numerator is an idempotent fixed point modulo 5,
once at least one factor has been multiplied. -/
theorem liBaseNumerator_modFive (n : Nat) :
    (liBaseNumerator (n + 1)).1 % 5 = 3 ∧
    (liBaseNumerator (n + 1)).2 % 5 = 4 := by
  induction n with
  | zero =>
    decide
  | succ n ih =>
    change
      (3 * (liBaseNumerator (n + 1)).1 -
        4 * (liBaseNumerator (n + 1)).2) % 5 = 3 ∧
      (4 * (liBaseNumerator (n + 1)).1 +
        3 * (liBaseNumerator (n + 1)).2) % 5 = 4
    omega

/-- A nonzero imaginary numerator for EVERY positive exponent,
not merely a sweep up to a finite numerical cutoff. -/
theorem liBaseNumerator_imag_ne_zero (n : Nat) :
    (liBaseNumerator (n + 1)).2 ≠ 0 := by
  have h := (liBaseNumerator_modFive n).2
  intro hz
  rw [hz] at h
  omega

end MathOS

#print axioms MathOS.liBaseNumerator_modFive
#print axioms MathOS.liBaseNumerator_imag_ne_zero
