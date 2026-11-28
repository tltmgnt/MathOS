import Init

/-! Local Boolean identities used in restricted CNF preprocessing.
These do not prove correctness of the Python implementation. -/
namespace PnpReductionRules

theorem resolutionLocal (a b : Bool) :
    (∃ x : Bool, ((x || a) && (!x || b)) = true) ↔ (a || b) = true := by
  constructor
  · intro h
    rcases h with ⟨x, hx⟩
    cases x <;> cases a <;> cases b <;> simp_all
  · intro h
    cases a <;> cases b
    · simp at h
    · exact ⟨true, by decide⟩
    · exact ⟨false, by decide⟩
    · exact ⟨true, by decide⟩

theorem purePositive (a : Bool) :
    ∃ x : Bool, (x || a) = true :=
  ⟨true, by decide⟩

theorem pureNegative (a : Bool) :
    ∃ x : Bool, (!x || a) = true :=
  ⟨false, by decide⟩

theorem subsumptionLocal (a b : Bool) :
    (a && (a || b)) = a := by
  cases a <;> cases b <;> decide

#print axioms PnpReductionRules.resolutionLocal
#print axioms PnpReductionRules.purePositive
#print axioms PnpReductionRules.pureNegative
#print axioms PnpReductionRules.subsumptionLocal

end PnpReductionRules
