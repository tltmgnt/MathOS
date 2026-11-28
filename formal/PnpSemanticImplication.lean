import Init

namespace PnpSemanticImplication

theorem resolve (x a b : Bool)
    (hp : (x || a) = true) (hn : ((!x) || b) = true) :
    (a || b) = true := by
  cases x <;> cases a <;> cases b <;>
    first | rfl | exact hp | exact hn

theorem liftPremise (c z : Bool)
    (h1 : (c || z) = true) (h2 : (c || !z) = true) : c = true := by
  cases c <;> cases z <;>
    first | rfl | exact h1 | exact h2

theorem consequencesPreserve {A : Type} (p q : A → Prop)
    (h : ∀ a, p a → q a) : (∃ a, p a) ↔ (∃ a, p a ∧ q a) := by
  constructor
  · intro hp
    rcases hp with ⟨a, ha⟩
    exact ⟨a, ha, h a ha⟩
  · intro hp
    rcases hp with ⟨a, ha, _⟩
    exact ⟨a, ha⟩

#print axioms PnpSemanticImplication.resolve
#print axioms PnpSemanticImplication.liftPremise
#print axioms PnpSemanticImplication.consequencesPreserve

end PnpSemanticImplication
