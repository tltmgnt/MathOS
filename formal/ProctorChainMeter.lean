/-! F034: eager abstract composition of lookup, shape and indexed
reference meters. Counts are for selected operations in the metered
algorithm, not wall time or the exact short-circuit execution trace. -/
namespace ProctorChainMeter
open ProctorHallDeficiency
open ProctorExecutableReplay (Step Batch lookup shapeCheck stepCheck batchCheck chainCheck tails)
open ProctorCheckerCost
open ProctorCapacityReplay (RefRow refCheck every test)

def both (a b : Bool × Nat) : Bool × Nat :=
  (a.1 && b.1,a.2+b.2)

def parentCheck (f : Formula) (i : Nat) (p : Literal) (t : Clause) : Bool :=
  match lookup f i with
  | none => false
  | some row => shapeCheck p t row

def parentMeter (f : Formula) (i : Nat) (p : Literal) (t : Clause) : Bool × Nat :=
  let a := lookupMeter f i
  match a.1 with
  | none => (false,a.2)
  | some row =>
    let b := shapeMeter p t row
    (b.1,a.2+b.2)

def parentBudget (f : Formula) (i : Nat) (t : Clause) : Nat :=
  f.length + (match lookup f i with
    | none => 0
    | some row => shapeBudget t row)

theorem parent_value (f : Formula) (i : Nat) (p : Literal) (t : Clause) :
    (parentMeter f i p t).1 = parentCheck f i p t := by
  unfold parentMeter parentCheck
  rw [lookup_value]
  cases lookup f i with
  | none => rfl
  | some row => exact shape_value p t row

theorem parent_bound (f : Formula) (i : Nat) (p : Literal) (t : Clause) :
    (parentMeter f i p t).2 ≤ parentBudget f i t := by
  unfold parentMeter parentBudget
  rw [lookup_value]
  cases lookup f i with
  | none => exact lookup_bound f i
  | some row => exact Nat.add_le_add (lookup_bound f i) (shape_bound p t row)

def stepMeter (f : Formula) (s : Step) : Bool × Nat :=
  both (parentMeter f s.left (s.pivot,true) s.tail)
       (parentMeter f s.right (s.pivot,false) s.tail)

def stepBudget (f : Formula) (s : Step) : Nat :=
  parentBudget f s.left s.tail + parentBudget f s.right s.tail

theorem step_value (f : Formula) (s : Step) :
    (stepMeter f s).1 = stepCheck f s := by
  unfold stepMeter both
  rw [parent_value,parent_value]
  unfold parentCheck stepCheck
  cases lookup f s.left with
  | none => rfl
  | some a =>
    cases lookup f s.right with
    | none => cases shapeCheck (s.pivot,true) s.tail a <;> rfl
    | some _ => rfl

theorem step_bound (f : Formula) (s : Step) :
    (stepMeter f s).2 ≤ stepBudget f s :=
  Nat.add_le_add (parent_bound f s.left (s.pivot,true) s.tail)
    (parent_bound f s.right (s.pivot,false) s.tail)

def batchMeter (f : Formula) : Batch → Bool × Nat
  | [] => (true,0)
  | s::ss => both (stepMeter f s) (batchMeter f ss)

def batchBudget (f : Formula) : Batch → Nat
  | [] => 0
  | s::ss => stepBudget f s + batchBudget f ss

theorem batch_value (f : Formula) (ss : Batch) :
    (batchMeter f ss).1 = batchCheck f ss := by
  induction ss with
  | nil => rfl
  | cons s ss ih =>
    change ((stepMeter f s).1 && (batchMeter f ss).1) =
      (stepCheck f s && batchCheck f ss)
    rw [step_value,ih]

theorem batch_bound (f : Formula) (ss : Batch) :
    (batchMeter f ss).2 ≤ batchBudget f ss := by
  induction ss with
  | nil => exact Nat.le_refl 0
  | cons s ss ih => exact Nat.add_le_add (step_bound f s) ih

def chainMeter (f : Formula) : List Batch → Bool × Nat
  | [] => (true,0)
  | ss::rest => both (batchMeter f ss) (chainMeter (tails ss) rest)

def chainBudget (f : Formula) : List Batch → Nat
  | [] => 0
  | ss::rest => batchBudget f ss + chainBudget (tails ss) rest

theorem chain_value (f : Formula) (bs : List Batch) :
    (chainMeter f bs).1 = chainCheck f bs := by
  induction bs generalizing f with
  | nil => rfl
  | cons ss rest ih =>
    change ((batchMeter f ss).1 && (chainMeter (tails ss) rest).1) =
      (batchCheck f ss && chainCheck (tails ss) rest)
    rw [batch_value,ih]

theorem chain_bound (f : Formula) (bs : List Batch) :
    (chainMeter f bs).2 ≤ chainBudget f bs := by
  induction bs generalizing f with
  | nil => exact Nat.le_refl 0
  | cons ss rest ih => exact Nat.add_le_add (batch_bound f ss) (ih (tails ss))

/-- One charge per compared literal pair and one final end-marker
comparison if no earlier mismatch. -/
def rowEqMeter : Clause → Clause → Bool × Nat
  | [], [] => (true,1)
  | [], _::_ => (false,1)
  | _::_, [] => (false,1)
  | a::as, b::bs =>
    if a=b then
      let r := rowEqMeter as bs
      (r.1,r.2+1)
    else (false,1)

theorem row_eq_value (a b : Clause) :
    (rowEqMeter a b).1 = test (a=b) := by
  induction a generalizing b with
  | nil =>
    cases b <;> rfl
  | cons l ls ih =>
    cases b with
    | nil => rfl
    | cons m ms =>
      change (if l=m then ((rowEqMeter ls ms).1,(rowEqMeter ls ms).2+1)
        else (false,1)).1 = test (l::ls=m::ms)
      by_cases e : l=m
      · rw [if_pos e]
        cases e
        change (rowEqMeter ls ms).1 = test (l::ls=l::ms)
        rw [ih ms]
        unfold test
        by_cases t : ls=ms
        · rw [if_pos t,if_pos (congrArg (List.cons l) t)]
        · have ne : l::ls ≠ l::ms := fun h => t (List.cons.inj h).2
          rw [if_neg t,if_neg ne]
      · rw [if_neg e]
        have ne : l::ls ≠ m::ms := fun h => e (List.cons.inj h).1
        unfold test
        rw [if_neg ne]

theorem row_eq_bound (a b : Clause) :
    (rowEqMeter a b).2 ≤ a.length+1 := by
  induction a generalizing b with
  | nil => cases b <;> exact Nat.le_refl 1
  | cons l ls ih =>
    cases b with
    | nil => exact Nat.succ_le_succ (Nat.zero_le (ls.length+1))
    | cons m ms =>
      change (if l=m then ((rowEqMeter ls ms).1,(rowEqMeter ls ms).2+1)
        else (false,1)).2 ≤ ls.length+1+1
      by_cases e : l=m
      · rw [if_pos e]
        exact Nat.succ_le_succ (ih ms)
      · rw [if_neg e]
        exact Nat.succ_le_succ (Nat.zero_le (ls.length+1))

def refMeter (f : Formula) (r : RefRow) : Bool × Nat :=
  let a := lookupMeter f r.index
  match a.1 with
  | none => (false,a.2)
  | some row =>
    let b := rowEqMeter row r.row
    (b.1,a.2+b.2)

def refBudget (f : Formula) (r : RefRow) : Nat :=
  f.length + (match lookup f r.index with
    | none => 0
    | some row => row.length+1)

theorem ref_value (f : Formula) (r : RefRow) :
    (refMeter f r).1 = refCheck f r := by
  unfold refMeter refCheck
  rw [lookup_value]
  cases lookup f r.index with
  | none => rfl
  | some row => exact row_eq_value row r.row

theorem ref_bound (f : Formula) (r : RefRow) :
    (refMeter f r).2 ≤ refBudget f r := by
  unfold refMeter refBudget
  rw [lookup_value]
  cases lookup f r.index with
  | none => exact lookup_bound f r.index
  | some row => exact Nat.add_le_add (lookup_bound f r.index) (row_eq_bound row r.row)

def refsMeter (f : Formula) : List RefRow → Bool × Nat
  | [] => (true,0)
  | r::rs => both (refMeter f r) (refsMeter f rs)

def refsBudget (f : Formula) : List RefRow → Nat
  | [] => 0
  | r::rs => refBudget f r + refsBudget f rs

theorem refs_value (f : Formula) (rs : List RefRow) :
    (refsMeter f rs).1 = every (refCheck f) rs := by
  induction rs with
  | nil => rfl
  | cons r rs ih =>
    change ((refMeter f r).1 && (refsMeter f rs).1) =
      (refCheck f r && every (refCheck f) rs)
    rw [ref_value,ih]

theorem refs_bound (f : Formula) (rs : List RefRow) :
    (refsMeter f rs).2 ≤ refsBudget f rs := by
  induction rs with
  | nil => exact Nat.le_refl 0
  | cons r rs ih => exact Nat.add_le_add (ref_bound f r) ih

end ProctorChainMeter

#print axioms ProctorChainMeter.parent_value
#print axioms ProctorChainMeter.parent_bound
#print axioms ProctorChainMeter.step_value
#print axioms ProctorChainMeter.step_bound
#print axioms ProctorChainMeter.batch_value
#print axioms ProctorChainMeter.batch_bound
#print axioms ProctorChainMeter.chain_value
#print axioms ProctorChainMeter.chain_bound
#print axioms ProctorChainMeter.row_eq_value
#print axioms ProctorChainMeter.row_eq_bound
#print axioms ProctorChainMeter.ref_value
#print axioms ProctorChainMeter.ref_bound
#print axioms ProctorChainMeter.refs_value
#print axioms ProctorChainMeter.refs_bound
