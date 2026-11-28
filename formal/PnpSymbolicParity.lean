import Init

namespace PnpSymbolicParity

theorem xorInvolution (a b : Bool) : ((a != b) != b) = a := by
  cases a <;> cases b <;> rfl

theorem omittedCheck {I A : Type} (test : I → A → Prop)
    (keep : I → Prop) (j : I) (a : A)
    (missing : ¬ keep j)
    (passes : ∀ i, i ≠ j → test i a)
    (fails : ¬ test j a) :
    (∀ i, keep i → test i a) ∧ ¬ (∀ i, test i a) := by
  constructor
  · intro i hi
    apply passes i
    intro eq
    exact missing (eq ▸ hi)
  · intro h
    exact fails (h j)

#print axioms PnpSymbolicParity.xorInvolution
#print axioms PnpSymbolicParity.omittedCheck

end PnpSymbolicParity
