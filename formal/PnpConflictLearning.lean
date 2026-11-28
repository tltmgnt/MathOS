namespace PnpConflictLearning

-- A local semantic resolution rule, not a formalization of the
-- watched-literal implementation, RUP checker or full CDCL algorithm.
theorem resolveSound (p A B : Prop)
    (left : p ∨ A) (right : ¬p ∨ B) : A ∨ B := by
  cases left with
  | inl hp =>
    cases right with
    | inl hn => exact False.elim (hn hp)
    | inr hb => exact Or.inr hb
  | inr ha => exact Or.inl ha

theorem contradictionDischargesAssumption (p : Prop)
    (conflict : p → False) : ¬p := conflict

#print axioms resolveSound
#print axioms contradictionDischargesAssumption
end PnpConflictLearning
