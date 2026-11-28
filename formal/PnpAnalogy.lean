import Init

namespace PnpAnalogy

theorem clauseSubset {L : Type} (small large holds : L → Prop)
    (sub : ∀ l, small l → large l) :
    (∃ l, small l ∧ holds l) → ∃ l, large l ∧ holds l := by
  intro h
  rcases h with ⟨l, hs, ht⟩
  exact ⟨l, sub l hs, ht⟩

theorem allPremises {A I : Type} (target : A → Prop) (premises : I → A → Prop)
    (witness : ∀ a i, target a → premises i a)
    (refute : ∀ a, ¬ (∀ i, premises i a)) :
    ∀ a, ¬ target a :=
  fun a h => refute a (fun i => witness a i h)

#print axioms PnpAnalogy.clauseSubset
#print axioms PnpAnalogy.allPremises

end PnpAnalogy
