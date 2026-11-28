namespace PnpHallCertificate

-- The local semantic bridge: incompatible choices cannot select the
-- same resource. This is conditional, not a formalization of the finite
-- pigeonhole cardinality theorem or Python's extraction/checker.
theorem exclusiveSelectionInjective {G R : Type} [DecidableEq G]
    (choose : G → R)
    (exclusive : ∀ a b, a ≠ b → choose a = choose b → False) :
    ∀ a b, choose a = choose b → a = b := by
  intro a b eq
  by_cases h : a = b
  · exact h
  · exact False.elim (exclusive a b h eq)

theorem deficientSelectionImpossible {G R : Type}
    (collision : ∀ choose : G → R, ∃ a b, a ≠ b ∧ choose a = choose b)
    (choose : G → R)
    (exclusive : ∀ a b, a ≠ b → choose a = choose b → False) :
    False := by
  obtain ⟨a, b, h, eq⟩ := collision choose
  exact exclusive a b h eq

#print axioms exclusiveSelectionInjective
#print axioms deficientSelectionImpossible
end PnpHallCertificate
