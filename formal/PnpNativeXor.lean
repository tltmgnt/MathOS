namespace PnpNativeXor

-- Local bridges only: not a formalization of the Gaussian search,
-- signed-clause extraction, RUP implementation, or full CDCL.
theorem parityExplanationSound (a b rhs : Bool)
    (h : Bool.xor a b = rhs)
    (wrong : Bool.xor false false ≠ rhs) :
    a = true ∨ b = true := by
  cases a with
  | false =>
    cases b with
    | false => exact False.elim (wrong h)
    | true => exact Or.inr rfl
  | true => exact Or.inl rfl

theorem xorCombination (a b c rhs₁ rhs₂ : Bool)
    (h₁ : Bool.xor a b = rhs₁)
    (h₂ : Bool.xor b c = rhs₂) :
    Bool.xor a c = Bool.xor rhs₁ rhs₂ := by
  subst rhs₁
  subst rhs₂
  cases a <;> cases b <;> cases c <;> rfl

theorem checkedAdditionPreservesRefutation (F C : Prop)
    (entails : F → C) (refute : F ∧ C → False) :
    F → False := fun h => refute ⟨h, entails h⟩

#print axioms parityExplanationSound
#print axioms xorCombination
#print axioms checkedAdditionPreservesRefutation
end PnpNativeXor
