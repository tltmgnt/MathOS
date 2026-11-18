import Init

/-!
# Yang--Mills research attack 008: bounded Z2 strip checks

For a single square plaquette with Z2 link variables, the Wilson sign
is (-1)^(a XOR b XOR c XOR d). Flipping BOTH edges incident to a
vertex preserves the plaquette. Flipping ONE edge reverses its sign.
These are honest all-Boolean-case theorems about a FINITE Z2 toy model.

The sum/product recurrences below describe INDEPENDENT plaquette
parity weights; they are not a formal proof of the 2D lattice's
edge-to-plaquette fiber count (given in the accompanying note).

Z2 is finite abelian, not compact simple non-Abelian G.
No continuum QFT, Hilbert-space reconstruction, or physical gap is
constructed. No part of the Yang--Mills Millennium problem is solved.
-/

namespace MathOS

/-- Is the product of four link signs -1? -/
def ymPlaquetteOdd (a b c d : Bool) : Bool :=
  ((a.xor b).xor c).xor d

/-- An elementary lattice gauge transformation flips the two edges
incident to a given vertex, leaving the plaquette Wilson sign invariant. -/
theorem ymGaugeFlipAB (a b c d : Bool) :
    ymPlaquetteOdd (!a) (!b) c d = ymPlaquetteOdd a b c d := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

theorem ymGaugeFlipBC (a b c d : Bool) :
    ymPlaquetteOdd a (!b) (!c) d = ymPlaquetteOdd a b c d := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

theorem ymGaugeFlipCD (a b c d : Bool) :
    ymPlaquetteOdd a b (!c) (!d) = ymPlaquetteOdd a b c d := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

theorem ymGaugeFlipDA (a b c d : Bool) :
    ymPlaquetteOdd (!a) b c (!d) = ymPlaquetteOdd a b c d := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

/-- A single-link flip pairs positive and negative plaquette signs. -/
theorem ymSingleFlipChangesSign (a b c d : Bool) :
    ymPlaquetteOdd (!a) b c d = !(ymPlaquetteOdd a b c d) := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

/-- Encode the sign as an integer, without assuming a quantum Hilbert space. -/
def ymWilsonSign (a b c d : Bool) : Int :=
  if ymPlaquetteOdd a b c d then -1 else 1

theorem ymWilsonSignGaugeInvariantAB (a b c d : Bool) :
    ymWilsonSign (!a) (!b) c d = ymWilsonSign a b c d := by
  simp [ymWilsonSign, ymGaugeFlipAB]

theorem ymWilsonSignSingleFlip (a b c d : Bool) :
    ymWilsonSign (!a) b c d = -(ymWilsonSign a b c d) := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

/-- Abstract independent-plaquette unsigned polynomial:
each plaquette contributes t+1. Not a spectral gap or a 4D theory. -/
def ymIndependentWeight (t : Nat) : Nat → Nat
  | 0 => 1
  | n + 1 => ymIndependentWeight t n * (t + 1)

/-- Signed (Wilson-inserted) polynomial: each plaquette contributes t-1.
Natural subtraction is intended only for t >= 1. -/
def ymIndependentSignedWeight (t : Nat) : Nat → Nat
  | 0 => 1
  | n + 1 => ymIndependentSignedWeight t n * (t - 1)

theorem ymIndependentWeightClosed (t n : Nat) :
    ymIndependentWeight t n = (t + 1) ^ n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [ymIndependentWeight, ih, pow_succ]

theorem ymIndependentSignedWeightClosed (t n : Nat) :
    ymIndependentSignedWeight t n = (t - 1) ^ n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [ymIndependentSignedWeight, ih, pow_succ]

/-- For t=k^2+1 (k>=1), the normalized Wilson ratio is
k^2 / (k^2+2), with a strictly positive denominator difference.
The physical decay-rate scaling and logarithm estimate are justified
on paper, NOT in this Lean file. -/
theorem ymScalingNumerator (k : Nat) :
    (k * k + 1) - 1 = k * k := by
  omega

theorem ymScalingDenominator (k : Nat) :
    (k * k + 1) + 1 = k * k + 2 := by
  omega

theorem ymScalingStrictStep (k : Nat) :
    k * k < k * k + 2 := by
  omega

end MathOS

#print axioms MathOS.ymGaugeFlipAB
#print axioms MathOS.ymSingleFlipChangesSign
#print axioms MathOS.ymIndependentWeightClosed
#print axioms MathOS.ymIndependentSignedWeightClosed
