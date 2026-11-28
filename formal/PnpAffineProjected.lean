namespace PnpAffineProjected

-- Local semantic bridges only: finite matrix compilation, RUP and
-- Python implementation remain outside this formal scope.
theorem substitutionPreservesXor (x a y b : Bool)
    (hx : x = a) (hy : y = b) :
    Bool.xor x y = Bool.xor a b := by
  rw [hx, hy]

theorem projectedContradictionLifts {Original Projected : Type}
    (translate : Original → Projected)
    (refute : Projected → False) : Original → False :=
  fun witness => refute (translate witness)

theorem xorGateCharacterization (a b z : Bool) :
    z = Bool.xor a b ↔
    (a = true ∨ b = true ∨ z = false) ∧
    (a = true ∨ b = false ∨ z = true) ∧
    (a = false ∨ b = true ∨ z = true) ∧
    (a = false ∨ b = false ∨ z = false) := by
  cases a <;> cases b <;> cases z <;> decide

#print axioms substitutionPreservesXor
#print axioms projectedContradictionLifts
#print axioms xorGateCharacterization
end PnpAffineProjected
