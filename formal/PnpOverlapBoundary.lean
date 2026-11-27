import Init

namespace PnpOverlapBoundary

def valid (u v : Bool) : Bool := (!v) || u

theorem gadget_forward (x b : Bool) : valid x (x && b) = true := by
  cases x <;> cases b <;> decide

theorem gadget_lift (u v : Bool) (h : valid u v = true) :
    (u && v) = v := by
  cases u <;> cases v <;> first | rfl | exact False.elim (Bool.noConfusion h)

def parity (a b c : Bool) : Bool := Bool.xor (Bool.xor a b) c

def selectorsOK (a b c s t w : Bool) : Bool :=
  valid a s && valid b t && valid c w && parity s t w

theorem selector_sound (a b c s t w : Bool)
    (h : selectorsOK a b c s t w = true) : (a || b || c) = true := by
  cases a <;> cases b <;> cases c <;> cases s <;> cases t <;> cases w <;>
    first | rfl | exact False.elim (Bool.noConfusion h)

def selectSecond (a b : Bool) := (!a) && b
def selectThird (a b c : Bool) := (!a) && (!b) && c

theorem selector_complete (a b c : Bool) (h : (a || b || c) = true) :
    selectorsOK a b c a (selectSecond a b) (selectThird a b c) = true := by
  cases a <;> cases b <;> cases c <;>
    first | rfl | exact False.elim (Bool.noConfusion h)

end PnpOverlapBoundary

#print axioms PnpOverlapBoundary.gadget_forward
#print axioms PnpOverlapBoundary.gadget_lift
#print axioms PnpOverlapBoundary.selector_sound
#print axioms PnpOverlapBoundary.selector_complete
