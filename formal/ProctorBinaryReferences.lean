/-! F034 candidate: binary literal equality, membership, ordered row
equality and certificate reference validation. Conditional result
projection for representable Nat operands. Gate and lookup visit
coordinates are separate. Encoder and allocation costs excluded. -/
namespace ProctorBinaryReferences
open ProctorHallDeficiency
open ProctorCapacityReplay (test RefRow refCheck)
open ProctorExecutableReplay (contains lookup lookup_mem)
open ProctorCheckedBinaryScanner (cap)
open ProctorCheckerBinaryTests (checkedEq checked_eq_value checked_eq_bound)
open ProctorBinaryLookup (checkedLookup checked_formula_projection checked_bound)

def Fits (w : Nat) (c : Clause) : Prop :=
  ∀ l ∈ c, l.1<cap w

def literalMeter (w : Nat) (a b : Literal) : Bool × Nat :=
  let r := checkedEq w a.1 b.1
  match r.1 with
  | none => (false,r.2)
  | some e => (e && !(ProctorXorReplay.bx a.2 b.2),r.2+3)

def literalBudget (w : Nat) : Nat := ((5*w+5*w)+3)+3

theorem literal_value (w : Nat) (a b : Literal)
    (ha : a.1<cap w) (hb : b.1<cap w) :
    (literalMeter w a b).1=test (a=b) := by
  unfold literalMeter
  rw [checked_eq_value w a.1 b.1 ha hb]
  cases a with
  | mk x p =>
    cases b with
    | mk y q =>
      change (test (x=y) && !(ProctorXorReplay.bx p q))=test ((x,p)=(y,q))
      unfold test
      by_cases h : x=y
      · cases h
        cases p <;> cases q <;> rfl
      · have ne : (x,p)≠(y,q) := fun e => h (congrArg Prod.fst e)
        rw [if_neg h,if_neg ne]
        rfl

theorem literal_bound (w : Nat) (a b : Literal) :
    (literalMeter w a b).2≤literalBudget w := by
  unfold literalMeter
  cases e : (checkedEq w a.1 b.1).1 with
  | none => exact Nat.le_trans (checked_eq_bound w a.1 b.1) (Nat.le_add_right _ _)
  | some bval => exact Nat.add_le_add (checked_eq_bound w a.1 b.1) (Nat.le_refl 3)

def containsMeter (w : Nat) (l : Literal) : Clause → Bool × Nat
  | [] => (false,0)
  | a::as =>
    let e := literalMeter w l a
    if e.1 then (true,e.2)
    else let r := containsMeter w l as; (r.1,r.2+e.2)

theorem contains_value (w : Nat) (l : Literal) (c : Clause)
    (hl : l.1<cap w) (hc : Fits w c) :
    (containsMeter w l c).1=contains l c := by
  induction c with
  | nil => rfl
  | cons a as ih =>
    change (if (literalMeter w l a).1 then (true,(literalMeter w l a).2)
      else ((containsMeter w l as).1,(containsMeter w l as).2+(literalMeter w l a).2)).1=
      (if l=a then true else contains l as)
    rw [literal_value w l a hl (hc a (List.Mem.head _))]
    unfold test
    by_cases e : l=a
    · rw [if_pos e] <;> rfl
    · rw [if_neg e,if_neg e]
      exact ih (fun b h => hc b (List.Mem.tail _ h))

theorem contains_bound (w : Nat) (l : Literal) (c : Clause) :
    (containsMeter w l c).2≤literalBudget w*c.length := by
  induction c with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    change (if (literalMeter w l a).1 then (true,(literalMeter w l a).2)
      else ((containsMeter w l as).1,(containsMeter w l as).2+(literalMeter w l a).2)).2≤
      literalBudget w*as.length+literalBudget w
    cases e : (literalMeter w l a).1 with
    | true => exact Nat.le_trans (literal_bound w l a) (Nat.le_add_left _ _)
    | false => exact Nat.add_le_add ih (literal_bound w l a)

def rowMeter (w : Nat) : Clause → Clause → Bool × Nat
  | [],[] => (true,0)
  | [],_::_ => (false,0)
  | _::_,[] => (false,0)
  | a::as,b::bs =>
    let e := literalMeter w a b
    if e.1 then let r := rowMeter w as bs; (r.1,r.2+e.2)
    else (false,e.2)

theorem row_value (w : Nat) (a b : Clause) (ha : Fits w a) (hb : Fits w b) :
    (rowMeter w a b).1=test (a=b) := by
  induction a generalizing b with
  | nil => cases b <;> rfl
  | cons l ls ih =>
    cases b with
    | nil => rfl
    | cons m ms =>
      change (if (literalMeter w l m).1 then
        ((rowMeter w ls ms).1,(rowMeter w ls ms).2+(literalMeter w l m).2)
        else (false,(literalMeter w l m).2)).1=test (l::ls=m::ms)
      rw [literal_value w l m (ha l (List.Mem.head _)) (hb m (List.Mem.head _))]
      unfold test
      by_cases e : l=m
      · rw [if_pos e]
        cases e
        change (rowMeter w ls ms).1=test (l::ls=l::ms)
        rw [ih ms (fun b h => ha b (List.Mem.tail _ h)) (fun b h => hb b (List.Mem.tail _ h))]
        unfold test
        by_cases t : ls=ms
        · rw [if_pos t,if_pos (congrArg (List.cons l) t)]
        · have ne : l::ls≠l::ms := fun h => t (List.cons.inj h).2
          rw [if_neg t,if_neg ne]
      · rw [if_neg e]
        have ne : l::ls≠m::ms := fun h => e (List.cons.inj h).1
        rw [if_neg ne]
        rfl

theorem row_bound (w : Nat) (a b : Clause) :
    (rowMeter w a b).2≤literalBudget w*a.length := by
  induction a generalizing b with
  | nil => cases b <;> exact Nat.le_refl 0
  | cons l ls ih =>
    cases b with
    | nil => exact Nat.zero_le _
    | cons m ms =>
      change (if (literalMeter w l m).1 then
        ((rowMeter w ls ms).1,(rowMeter w ls ms).2+(literalMeter w l m).2)
        else (false,(literalMeter w l m).2)).2≤literalBudget w*ls.length+literalBudget w
      cases e : (literalMeter w l m).1 with
      | true => exact Nat.add_le_add (ih ms) (literal_bound w l m)
      | false => exact Nat.le_trans (literal_bound w l m) (Nat.le_add_left _ _)

-- Separate selected lookup visits and literal circuit gates.
def refMeter (w : Nat) (f : Formula) (r : RefRow) : Bool × Nat × Nat :=
  let a := checkedLookup w f r.index
  match a.1 with
  | none => (false,a.2,0)
  | some row => let b := rowMeter w row r.row; (b.1,a.2,b.2)

theorem ref_value (w : Nat) (f : Formula) (r : RefRow)
    (hi : r.index<cap w) (hf : ∀ c ∈ f, Fits w c) (hr : Fits w r.row) :
    (refMeter w f r).1=refCheck f r := by
  unfold refMeter refCheck
  rw [checked_formula_projection w f r.index hi]
  cases e : lookup f r.index with
  | none => rfl
  | some row => exact row_value w row r.row (hf row (lookup_mem f r.index row e)) hr

theorem ref_visits (w : Nat) (f : Formula) (r : RefRow) :
    (refMeter w f r).2.1≤(w+1)*f.length := by
  unfold refMeter
  cases (checkedLookup w f r.index).1 <;> exact checked_bound w f r.index

theorem ref_gates (w : Nat) (f : Formula) (r : RefRow) :
    (refMeter w f r).2.2≤literalBudget w*
      (match (checkedLookup w f r.index).1 with
      | none => 0
      | some c => c.length) := by
  unfold refMeter
  cases (checkedLookup w f r.index).1 with
  | none => exact Nat.le_refl 0
  | some row => exact row_bound w row r.row

end ProctorBinaryReferences

#print axioms ProctorBinaryReferences.literal_value
#print axioms ProctorBinaryReferences.literal_bound
#print axioms ProctorBinaryReferences.contains_value
#print axioms ProctorBinaryReferences.contains_bound
#print axioms ProctorBinaryReferences.row_value
#print axioms ProctorBinaryReferences.row_bound
#print axioms ProctorBinaryReferences.ref_value
#print axioms ProctorBinaryReferences.ref_visits
#print axioms ProctorBinaryReferences.ref_gates
