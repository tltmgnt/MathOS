import Init

/-! Local Boolean facts supporting signed renaming and implication certificates.
These are not a formal verification of the Python SCC or Horn algorithms. -/

namespace PnpHypothesisRules

theorem renameLiteral (x sign flip : Bool) :
    (x == sign) = ((x != flip) == (sign != flip)) := by
  cases x <;> cases sign <;> cases flip <;> decide

theorem implicationStep (a b : Bool) (h : (!a || b) = true)
    (ha : a = true) : b = true := by
  cases a <;> cases b <;> first | rfl | exact ha | exact h

theorem oppositeConflict (a : Bool) (ha : a = true)
    (hna : (!a) = true) : False := by
  cases a
  · nomatch ha
  · nomatch hna

#print axioms PnpHypothesisRules.renameLiteral
#print axioms PnpHypothesisRules.implicationStep
#print axioms PnpHypothesisRules.oppositeConflict

end PnpHypothesisRules
