import Init

namespace PnpCrossModel

def xor (a b : Bool) : Bool := a != b

theorem cancelShared (a b c : Bool) :
    xor (xor a b) (xor b c) = xor a c := by
  cases a <;> cases b <;> cases c <;> rfl

theorem sameParityNoSingleFlip (a b c : Bool) :
    xor (xor a b) c ≠ xor (xor (!a) b) c := by
  cases a <;> cases b <;> cases c <;> decide

theorem inconsistentParity (lhs rhs : Bool)
    (h : lhs = rhs) (hl : lhs = false) (hr : rhs = true) : False := by
  rw [hl, hr] at h
  nomatch h

#print axioms PnpCrossModel.cancelShared
#print axioms PnpCrossModel.sameParityNoSingleFlip
#print axioms PnpCrossModel.inconsistentParity

end PnpCrossModel
