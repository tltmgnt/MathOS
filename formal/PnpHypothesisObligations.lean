import Init

namespace PnpHypothesisObligations

theorem componentParityNotGlobal :
    (true != true) = false ∧ true = true ∧ true = true := by
  exact ⟨rfl, rfl, rfl⟩

theorem independentUnion {A B : Type} (p : A → Prop) (q : B → Prop) :
    (∃ a, p a) ∧ (∃ b, q b) ↔ ∃ ab : A × B, p ab.1 ∧ q ab.2 := by
  constructor
  · intro h
    rcases h with ⟨⟨a, ha⟩, ⟨b, hb⟩⟩
    exact ⟨(a,b), ha,hb⟩
  · intro h
    rcases h with ⟨ab, ha,hb⟩
    exact ⟨⟨ab.1,ha⟩,⟨ab.2,hb⟩⟩

theorem conditionalComposition (p q r : Prop) (hpq : p → q) (hqr : q → r) :
    p → r := fun h => hqr (hpq h)

#print axioms PnpHypothesisObligations.componentParityNotGlobal
#print axioms PnpHypothesisObligations.independentUnion
#print axioms PnpHypothesisObligations.conditionalComposition

end PnpHypothesisObligations
