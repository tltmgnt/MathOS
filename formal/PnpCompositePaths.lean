import Init

namespace PnpCompositePaths

theorem residualClause {A : Type} (holds : A → Prop) (c : List A)
    (removed : A → Prop)
    (sat : ∃ a, a ∈ c ∧ holds a)
    (falseRemoved : ∀ a, removed a → ¬ holds a) :
    ∃ a, a ∈ c ∧ holds a ∧ ¬ removed a := by
  obtain ⟨a, mem, yes⟩ := sat
  exact ⟨a, mem, yes, fun h => falseRemoved a h yes⟩

theorem prefixPreserves {V : Type} (original units residual : V → Prop)
    (unitSound : ∀ v, original v → units v)
    (reductionSound : ∀ v, original v → units v → residual v) :
    ∀ v, original v → units v ∧ residual v :=
  fun v h => ⟨unitSound v h, reductionSound v h (unitSound v h)⟩

theorem compositeRefutation {V : Type} (original units residual : V → Prop)
    (unitSound : ∀ v, original v → units v)
    (reductionSound : ∀ v, original v → units v → residual v)
    (tailSound : ∀ v, original v → units v → residual v → False) :
    ∀ v, ¬ original v :=
  fun v h => tailSound v h (unitSound v h) (reductionSound v h (unitSound v h))

#print axioms PnpCompositePaths.residualClause
#print axioms PnpCompositePaths.prefixPreserves
#print axioms PnpCompositePaths.compositeRefutation

end PnpCompositePaths
