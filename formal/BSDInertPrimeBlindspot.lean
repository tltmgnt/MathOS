import Init

/-!
# BSD attack 007: a conditional quadratic-character cancellation and an exact point.

For E_d: y^2 = x^3 - d^2*x, the cubic is odd in x.
At good primes p = 3 (mod 4), the quadratic character satisfies
chi(-t)=-chi(t), and contributions at x and -x cancel.

Lean proves:
  * polynomial oddness over the integers;
  * cancellation under the EXPLICIT character-negation hypothesis;
  * exact coordinates of a rational point of E_5.

It does NOT construct a finite field, prove Euler's criterion, establish
Mordell-Weil rank, construct L(E,s), or prove BSD. The arithmetic and
prime-level consequences are explained in the companion research note.
-/

namespace MathOS

/-- The factored odd cubic x^3 - d^2 x, over integers. -/
def bsdTwistCubic (d x : Int) : Int := x * (x * x - d * d)

theorem bsdTwistCubic_odd (d x : Int) :
    bsdTwistCubic d (-x) = -(bsdTwistCubic d x) := by
  simp [bsdTwistCubic, mul_assoc]

/-- If an abstract character is odd, paired summands cancel.
The property of the Legendre character at p=3 mod 4 is an EXTERNAL
hypothesis, not inferred here from primality. -/
theorem bsdCharacter_pair_cancel
    (chi : Int → Int)
    (hneg : ∀ t : Int, chi (-t) = -(chi t))
    (d x : Int) :
    chi (bsdTwistCubic d x) +
      chi (bsdTwistCubic d (-x)) = 0 := by
  rw [bsdTwistCubic_odd, hneg]
  omega

/-- Short Weierstrass equation with coefficient -d^2. -/
def bsdTwistPointOnCurve (d x y : Rat) : Prop :=
  y * y = x * x * x - d * d * x

/-- Exact rational witness (25/4,75/8) for E_5: y^2=x^3-25x. -/
theorem bsdE5_rational_point :
    bsdTwistPointOnCurve 5 ((25 : Rat) / 4) ((75 : Rat) / 8) := by
  decide

/-- The rational y coordinate is visibly nonzero. -/
theorem bsdE5_y_nonzero : ((75 : Rat) / 8) ≠ 0 := by
  decide

/-- The x numerator is not divisible by its denominator.
The inference to non-torsion uses the EXTERNAL Nagell-Lutz theorem. -/
theorem bsdE5_x_numerator_mod_four : (25 : Nat) % 4 = 1 := by
  decide

end MathOS

#print axioms MathOS.bsdTwistCubic_odd
#print axioms MathOS.bsdCharacter_pair_cancel
#print axioms MathOS.bsdE5_rational_point
