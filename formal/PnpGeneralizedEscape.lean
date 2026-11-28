import Init

/-! Logical ingredients only; no claim of verified Python execution. -/
namespace PnpGeneralizedEscape

theorem splitExhaustive (P : Bool → Prop) :
    (∃ b : Bool, P b) ↔ P false ∨ P true := by
  constructor
  · intro h
    cases h with
    | intro b hb =>
      cases b with
      | false => exact Or.inl hb
      | true => exact Or.inr hb
  · intro h
    cases h with
    | inl hf => exact ⟨false, hf⟩
    | inr ht => exact ⟨true, ht⟩

theorem independentConjunction {α β : Type} (P : α → Prop) (Q : β → Prop) :
    (∃ x : α, ∃ y : β, P x ∧ Q y) ↔ (∃ x, P x) ∧ (∃ y, Q y) := by
  constructor
  · intro h
    rcases h with ⟨x, y, hx, hy⟩
    exact ⟨⟨x, hx⟩, ⟨y, hy⟩⟩
  · intro h
    rcases h with ⟨⟨x, hx⟩, ⟨y, hy⟩⟩
    exact ⟨x, y, hx, hy⟩

theorem subformulaContradiction {α : Type} (P Q : α → Prop)
    (h : ∀ x, P x → Q x) (hQ : ¬ ∃ x, Q x) : ¬ ∃ x, P x := by
  intro hp
  rcases hp with ⟨x, hx⟩
  exact hQ ⟨x, h x hx⟩

#print axioms PnpGeneralizedEscape.splitExhaustive
#print axioms PnpGeneralizedEscape.independentConjunction
#print axioms PnpGeneralizedEscape.subformulaContradiction

end PnpGeneralizedEscape
