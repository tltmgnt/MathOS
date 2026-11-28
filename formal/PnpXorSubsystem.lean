namespace PnpXorSubsystem

-- Semantic local addition rule, not a formalization of finite
-- Gaussian elimination or the Python clause-source checker.
theorem xorRowAddition (a b c d : Bool)
    (h₁ : a = b) (h₂ : c = d) :
    Bool.xor a c = Bool.xor b d := by
  rw [h₁, h₂]

theorem zeroEqualsOneImpossible (h : false = true) : False := by
  cases h

#print axioms xorRowAddition
#print axioms zeroEqualsOneImpossible
end PnpXorSubsystem
