import Init

/-!
This file specifies the expected mathematical proposition independently of
the candidate theorem module. The checker generates the proof binding.
-/
set_option warningAsError true

namespace MathOS.TECTX.Contracts

def implicationChainReference : Prop :=
  ∀ (P Q R : Prop), (P → Q) → (Q → R) → P → R

end MathOS.TECTX.Contracts
