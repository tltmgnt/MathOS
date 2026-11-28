import Init

namespace PnpComplexityBarriers

theorem transcriptAgreement {A : Type} (queried : A → Prop)
    (zero singleton : A → Bool) (hidden : A)
    (missing : ¬ queried hidden)
    (agreeElsewhere : ∀ a, a ≠ hidden → zero a = singleton a) :
    ∀ a, queried a → zero a = singleton a := by
  intro a ha
  apply agreeElsewhere
  intro h
  exact missing (h ▸ ha)

theorem decisionConflict (a b out : Bool) (ha : out = a) (hb : out = b)
    (different : a ≠ b) : False :=
  different (ha.symm.trans hb)

theorem singletonNonzero (a : Nat) (h : a = 1 ∨ a = 2) : a ≠ 0 := by
  intro hz
  rcases h with h1 | h2
  · rw [hz] at h1
    nomatch h1
  · rw [hz] at h2
    nomatch h2

#print axioms PnpComplexityBarriers.transcriptAgreement
#print axioms PnpComplexityBarriers.decisionConflict
#print axioms PnpComplexityBarriers.singletonNonzero

end PnpComplexityBarriers
