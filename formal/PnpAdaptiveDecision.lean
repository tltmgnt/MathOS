namespace PnpAdaptiveDecision

-- Abstract soundness of complete Boolean case splitting. This is not a
-- formalization of the Python certificate format or resource accounting.
theorem completeSplit (P : Bool → Prop)
    (hfalse : ¬ P false) (htrue : ¬ P true) (b : Bool) : ¬ P b := by
  cases b
  · exact hfalse
  · exact htrue

theorem conflictLeaf (satisfied : Prop) (conflict : ¬ satisfied) :
    ¬ satisfied := conflict

#print axioms completeSplit
#print axioms conflictLeaf
end PnpAdaptiveDecision
