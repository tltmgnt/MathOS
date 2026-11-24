/-! F034: abstract list-cell/comparison meters. The value projections
refine the corresponding executable functions. Counts do not model
Nat bit complexity, allocator behavior, compiler or total runtime. -/
namespace ProctorCheckerCost
open ProctorHallDeficiency
open ProctorExecutableReplay (lookup contains shapeCheck)

def lookupMeter : Formula → Nat → Option Clause × Nat
  | [], _ => (none,0)
  | c::_, 0 => (some c,1)
  | _::cs, i+1 =>
    let r := lookupMeter cs i
    (r.1,r.2+1)

theorem lookup_value (f : Formula) (i : Nat) :
    (lookupMeter f i).1 = lookup f i := by
  induction f generalizing i with
  | nil => rfl
  | cons c cs ih =>
    cases i with
    | zero => rfl
    | succ i => exact ih i

theorem lookup_bound (f : Formula) (i : Nat) :
    (lookupMeter f i).2 ≤ f.length := by
  induction f generalizing i with
  | nil => exact Nat.le_refl 0
  | cons c cs ih =>
    cases i with
    | zero => exact Nat.succ_le_succ (Nat.zero_le cs.length)
    | succ i => exact Nat.succ_le_succ (ih i)

def containsMeter (l : Literal) : Clause → Bool × Nat
  | [] => (false,0)
  | a::as =>
    if l=a then (true,1)
    else
      let r := containsMeter l as
      (r.1,r.2+1)

theorem contains_value (l : Literal) (c : Clause) :
    (containsMeter l c).1 = contains l c := by
  induction c with
  | nil => rfl
  | cons a as ih =>
    change (if l=a then (true,1) else
      ((containsMeter l as).1,(containsMeter l as).2+1)).1 =
      (if l=a then true else contains l as)
    by_cases e : l=a
    · rw [if_pos e,if_pos e]
    · rw [if_neg e,if_neg e]
      exact ih

theorem contains_bound (l : Literal) (c : Clause) :
    (containsMeter l c).2 ≤ c.length := by
  induction c with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    change (if l=a then (true,1) else
      ((containsMeter l as).1,(containsMeter l as).2+1)).2 ≤ as.length+1
    by_cases e : l=a
    · rw [if_pos e]
      exact Nat.succ_le_succ (Nat.zero_le as.length)
    · rw [if_neg e]
      exact Nat.succ_le_succ ih

def shapeMeter (pivot : Literal) (tail : Clause) : Clause → Bool × Nat
  | [] => (true,0)
  | l::ls =>
    if l=pivot then
      let r := shapeMeter pivot tail ls
      (r.1,r.2+1)
    else
      let m := containsMeter l tail
      if m.1 then
        let r := shapeMeter pivot tail ls
        (r.1,r.2+(m.2+1))
      else (false,m.2+1)

theorem shape_value (pivot : Literal) (tail row : Clause) :
    (shapeMeter pivot tail row).1 = shapeCheck pivot tail row := by
  induction row with
  | nil => rfl
  | cons l ls ih =>
    change (if l=pivot then
      ((shapeMeter pivot tail ls).1,(shapeMeter pivot tail ls).2+1)
      else if (containsMeter l tail).1 then
        ((shapeMeter pivot tail ls).1,(shapeMeter pivot tail ls).2+((containsMeter l tail).2+1))
        else (false,(containsMeter l tail).2+1)).1 =
      (if l=pivot then shapeCheck pivot tail ls
        else if contains l tail then shapeCheck pivot tail ls else false)
    by_cases e : l=pivot
    · rw [if_pos e,if_pos e]
      exact ih
    · rw [if_neg e,if_neg e,contains_value]
      cases contains l tail with
      | false => rfl
      | true => exact ih

def shapeBudget (tail : Clause) : Clause → Nat
  | [] => 0
  | _::ls => shapeBudget tail ls + (tail.length+1)

theorem shape_bound (pivot : Literal) (tail row : Clause) :
    (shapeMeter pivot tail row).2 ≤ shapeBudget tail row := by
  induction row with
  | nil => exact Nat.le_refl 0
  | cons l ls ih =>
    change (if l=pivot then
      ((shapeMeter pivot tail ls).1,(shapeMeter pivot tail ls).2+1)
      else if (containsMeter l tail).1 then
        ((shapeMeter pivot tail ls).1,(shapeMeter pivot tail ls).2+((containsMeter l tail).2+1))
        else (false,(containsMeter l tail).2+1)).2 ≤
        shapeBudget tail ls + (tail.length+1)
    by_cases e : l=pivot
    · rw [if_pos e]
      exact Nat.add_le_add ih (Nat.succ_le_succ (Nat.zero_le tail.length))
    · rw [if_neg e]
      cases h : (containsMeter l tail).1 with
      | false =>
        rw [h]
        exact Nat.le_trans (Nat.succ_le_succ (contains_bound l tail))
          (Nat.le_add_left _ _)
      | true =>
        rw [h]
        exact Nat.add_le_add ih (Nat.succ_le_succ (contains_bound l tail))

end ProctorCheckerCost

#print axioms ProctorCheckerCost.lookup_value
#print axioms ProctorCheckerCost.lookup_bound
#print axioms ProctorCheckerCost.contains_value
#print axioms ProctorCheckerCost.contains_bound
#print axioms ProctorCheckerCost.shape_value
#print axioms ProctorCheckerCost.shape_bound
