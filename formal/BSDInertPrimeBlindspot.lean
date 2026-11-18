import Init

/-!
# BSD attack 007: conditional quadratic-character cancellation and point coordinates.

For E_d: y^2 = x^3 - d^2*x, the cubic is odd in x. At good primes
p=3 (mod 4), the quadratic character has chi(-t)=-chi(t), so the terms
at x and -x cancel. Lean verifies the integer polynomial identity and
its consequence under the explicitly supplied character hypothesis.

The E5 rational point Q=(25/4,75/8) is checked by clearing denominators:
with x=a/b^2 and y=c/b^3, the Weierstrass identity becomes
c^2 = a^3-d^2*a*b^4, evaluated here at (d,a,b,c)=(5,25,2,75).

Lean does NOT construct finite fields, prove Euler's criterion,
derive elliptic-curve ranks, formalize Nagell-Lutz, or construct L(E,s).
-/

namespace MathOS

def bsdTwistCubic (d x : Int) : Int := x * (x * x - d * d)

theorem bsdTwistCubic_odd (d x : Int) :
    bsdTwistCubic d (-x) = -(bsdTwistCubic d x) := by
  simp [bsdTwistCubic]

/-- Conditional character cancellation, with the character law as hypothesis. -/
theorem bsdCharacter_pair_cancel
    (chi : Int → Int)
    (hneg : ∀ t : Int, chi (-t) = -(chi t))
    (d x : Int) :
    chi (bsdTwistCubic d x) +
      chi (bsdTwistCubic d (-x)) = 0 := by
  rw [bsdTwistCubic_odd, hneg]
  omega

/-- Cleared-denominator form of y^2=x^3-d^2x for
x=a/b^2 and y=c/b^3. The denominator must be NONZERO when this is
interpreted as a rational point; it is b=2 in the concrete witness. -/
def bsdClearedPointIdentity (d a b c : Int) : Prop :=
  c * c = a * a * a - d * d * a * (b * b * b * b)

theorem bsdE5_point_numerators :
    bsdClearedPointIdentity 5 25 2 75 := by
  decide

theorem bsdE5_denominator_nonzero : (2 : Int) ≠ 0 := by
  decide

theorem bsdE5_y_numerator_nonzero : (75 : Int) ≠ 0 := by
  decide

theorem bsdE5_x_numerator_mod_four : (25 : Nat) % 4 = 1 := by
  decide

end MathOS

#print axioms MathOS.bsdTwistCubic_odd
#print axioms MathOS.bsdCharacter_pair_cancel
#print axioms MathOS.bsdE5_point_numerators
