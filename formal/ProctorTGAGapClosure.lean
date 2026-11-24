/-! TGA-PNP: semantic compatibility and parity-cycle obstruction.
These are local logical lemmas, not a formal Kruskal or complexity theorem. -/
namespace ProctorTGAGapClosure

def edge (odd a b : Bool) : Prop :=
  if odd then a ≠ b else a = b

theorem edge_has_left_support (odd a : Bool) :
    ∃ b : Bool, edge odd a b := by
  cases odd <;> cases a
  · exact ⟨false, rfl⟩
  · exact ⟨true, rfl⟩
  · exact ⟨true, by intro h; cases h⟩
  · exact ⟨false, by intro h; cases h⟩

theorem edge_has_right_support (odd b : Bool) :
    ∃ a : Bool, edge odd a b := by
  cases odd <;> cases b
  · exact ⟨false, rfl⟩
  · exact ⟨true, rfl⟩
  · exact ⟨true, by intro h; cases h⟩
  · exact ⟨false, by intro h; cases h⟩

theorem even_triangle_sat :
    ∃ a b c : Bool, edge false a b ∧ edge false b c ∧ edge false c a := by
  exact ⟨false, false, false, rfl, rfl, rfl⟩

theorem odd_triangle_unsat :
    ¬ ∃ a b c : Bool, edge false a b ∧ edge false b c ∧ edge true c a := by
  intro h
  obtain ⟨a, b, c, hab, hbc, hca⟩ := h
  exact hca (hbc.symm.trans hab.symm)

theorem agreement_path (a b c : Bool) (h₁ : a = b) (h₂ : b = c) :
    a = c := h₁.trans h₂

end ProctorTGAGapClosure

#print axioms ProctorTGAGapClosure.edge_has_left_support
#print axioms ProctorTGAGapClosure.edge_has_right_support
#print axioms ProctorTGAGapClosure.even_triangle_sat
#print axioms ProctorTGAGapClosure.odd_triangle_unsat
#print axioms ProctorTGAGapClosure.agreement_path
