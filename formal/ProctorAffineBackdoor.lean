/-! F027: local Boolean compression and a sufficient affine backdoor condition.
The finite truth-table lemmas do not certify the graph algorithm or general SAT time. -/
namespace ProctorAffineBackdoor

inductive Slot where
  | zero | one | free
deriving DecidableEq

inductive Residual where
  | satisfied | conflict | first | second | third | nonlinear
deriving DecidableEq

def literal (positive value : Bool) : Bool :=
  if positive then value else !value

def Slot.eval (s : Slot) (x : Bool) : Bool :=
  match s with
  | .zero => false
  | .one => true
  | .free => x

def Slot.isFree (s : Slot) : Bool :=
  match s with
  | .free => true
  | _ => false

def classify : Slot → Slot → Slot → Residual
  | .one, _, _ => .satisfied
  | _, .one, _ => .satisfied
  | _, _, .one => .satisfied
  | .zero, .zero, .zero => .conflict
  | .free, .zero, .zero => .first
  | .zero, .free, .zero => .second
  | .zero, .zero, .free => .third
  | _, _, _ => .nonlinear

def pairCovered (a b c : Slot) : Bool :=
  !(a.isFree && b.isFree) &&
  !(a.isFree && c.isFree) &&
  !(b.isFree && c.isFree)

def evalResidual (r : Residual) (a b c : Slot) (x y z : Bool) : Bool :=
  match r with
  | .satisfied => true
  | .conflict => false
  | .first => x
  | .second => y
  | .third => z
  | .nonlinear => a.eval x || b.eval y || c.eval z

theorem classify_correct (a b c : Slot) (x y z : Bool) :
    evalResidual (classify a b c) a b c x y z =
      (a.eval x || b.eval y || c.eval z) := by
  cases a <;> cases b <;> cases c <;>
    cases x <;> cases y <;> cases z <;> rfl

theorem covered_no_nonlinear (a b c : Slot) :
    pairCovered a b c = true → classify a b c ≠ .nonlinear := by
  cases a <;> cases b <;> cases c <;> decide

theorem duplicate_literal (a b : Bool) :
    (a || a || b) = (a || b) := by
  cases a <;> cases b <;> rfl

theorem tautology_literal (a b : Bool) :
    (a || !a || b) = true := by
  cases a <;> cases b <;> rfl

theorem literal_complement (p x : Bool) :
    literal (!p) x = !(literal p x) := by
  cases p <;> cases x <;> rfl

theorem incompatible_units (a b x : Bool)
    (ha : x = a) (hb : x = b) (h : a ≠ b) : False :=
  h (ha.symm.trans hb)

-- Two opposite unit constraints have no witness.
theorem opposite_units_unsat (p : Bool) :
    ¬ ∃ x : Bool, literal p x = true ∧ literal (!p) x = true := by
  intro h
  obtain ⟨x, ha, hb⟩ := h
  cases p <;> cases x <;> contradiction

end ProctorAffineBackdoor
#print axioms ProctorAffineBackdoor.classify_correct
#print axioms ProctorAffineBackdoor.covered_no_nonlinear
#print axioms ProctorAffineBackdoor.duplicate_literal
#print axioms ProctorAffineBackdoor.tautology_literal
#print axioms ProctorAffineBackdoor.literal_complement
#print axioms ProctorAffineBackdoor.incompatible_units
#print axioms ProctorAffineBackdoor.opposite_units_unsat
