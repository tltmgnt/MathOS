import Init

/-!
The independent Nat reference contains only the intended formal goal.
The checker—not this source—must bind the candidate theorem to it.
-/
set_option warningAsError true

namespace MathOS.TECTX.Contracts

def natRightZeroReference : Prop := ∀ n : Nat, n + 0 = n

end MathOS.TECTX.Contracts
