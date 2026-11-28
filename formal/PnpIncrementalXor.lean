namespace PnpIncrementalXor

-- Local semantic restriction and undo rules, not a formalization
-- of indexed mutable rows or the Python undo log.
theorem restrictTrue (a b : Bool) (h : Bool.xor a true = b) :
    a = Bool.xor b true := by
  subst b
  cases a <;> rfl

theorem restrictFalse (a b : Bool) (h : Bool.xor a false = b) :
    a = b := by
  subst b
  cases a <;> rfl

theorem undoXor (a b : Bool) : Bool.xor (Bool.xor a b) b = a := by
  cases a <;> cases b <;> rfl

#print axioms restrictTrue
#print axioms restrictFalse
#print axioms undoXor
end PnpIncrementalXor
