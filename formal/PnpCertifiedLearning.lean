import Init

namespace PnpCertifiedLearning

theorem failedAssumption {f a : Prop} (h : ¬ (f ∧ a)) : f → ¬ a :=
  fun hf ha => h ⟨hf, ha⟩

theorem extendEquisat {f a : Prop} (h : ¬ (f ∧ a)) :
    f ↔ f ∧ ¬ a :=
  ⟨fun hf => ⟨hf, failedAssumption h hf⟩, fun hf => hf.1⟩

theorem twoAssumptions (a b : Bool) :
    (!(a && b)) = ((!a) || (!b)) := by
  cases a <;> cases b <;> rfl

#print axioms PnpCertifiedLearning.failedAssumption
#print axioms PnpCertifiedLearning.extendEquisat
#print axioms PnpCertifiedLearning.twoAssumptions

end PnpCertifiedLearning
