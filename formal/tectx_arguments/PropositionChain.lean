import Init

/-!
Proof-carrying mathematical argument about arbitrary propositions.
This is an actual theorem of Lean's Prop logic, NOT a claim about
external English prose or the correctness of TGA's authored edges.
-/
set_option warningAsError true

namespace MathOS.TECTX.Arguments

/-- From P→Q, Q→R and P, derive R, for arbitrary propositions. -/
theorem implication_chain (P Q R : Prop) :
    (P → Q) → (Q → R) → P → R := by
  intro hpq hqr hp
  exact hqr (hpq hp)

end MathOS.TECTX.Arguments
