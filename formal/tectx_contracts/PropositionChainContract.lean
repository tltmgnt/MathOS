import PropositionChain

/-!
Independently authored reference-goal contract.
Only the exact Lean expression is checked, not the meaning of English.
-/
set_option warningAsError true

namespace MathOS.TECTX.Contracts

/-- The separately written proposition that the candidate must inhabit. -/
def implicationChainReference : Prop :=
  ∀ (P Q R : Prop), (P → Q) → (Q → R) → P → R

/-- A Lean proof of the reference proposition must be supplied verbatim. -/
theorem implication_chain_matches_reference : implicationChainReference :=
  MathOS.TECTX.Arguments.implication_chain

end MathOS.TECTX.Contracts

#print axioms MathOS.TECTX.Arguments.implication_chain
#print axioms MathOS.TECTX.Contracts.implication_chain_matches_reference
