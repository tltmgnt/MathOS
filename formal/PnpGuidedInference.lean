import Init

namespace PnpGuidedInference

theorem addConsequence {A : Type} (f c : A → Prop)
    (h : ∀ a, f a → c a) : ∀ a, f a ↔ f a ∧ c a :=
  fun a => ⟨fun hf => ⟨hf, h a hf⟩, fun hc => hc.1⟩

theorem dropCovered {A : Type} (kept removed : A → Prop)
    (h : ∀ a, kept a → removed a) :
    ∀ a, (kept a ∧ removed a) ↔ kept a :=
  fun a => ⟨fun hf => hf.1, fun hk => ⟨hk, h a hk⟩⟩

theorem composeEquivalent {A : Type} (f g h : A → Prop)
    (fg : ∀ a, f a ↔ g a) (gh : ∀ a, g a ↔ h a) :
    ∀ a, f a ↔ h a :=
  fun a => Iff.trans (fg a) (gh a)

#print axioms PnpGuidedInference.addConsequence
#print axioms PnpGuidedInference.dropCovered
#print axioms PnpGuidedInference.composeEquivalent

end PnpGuidedInference
