import NaturalRightUnit

/-!
Independently authored reference-goal contract for Nat arithmetic.
The contract does not derive its theorem type from candidate source text.
-/
set_option warningAsError true

namespace MathOS.TECTX.Contracts

def natRightZeroReference : Prop := ∀ n : Nat, n + 0 = n

theorem nat_right_zero_matches_reference : natRightZeroReference :=
  MathOS.TECTX.Arguments.nat_add_right_zero

end MathOS.TECTX.Contracts

#print axioms MathOS.TECTX.Arguments.nat_add_right_zero
#print axioms MathOS.TECTX.Contracts.nat_right_zero_matches_reference
