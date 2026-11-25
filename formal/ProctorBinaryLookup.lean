/-! F034 candidate: replace Nat-index recursion with checked binary
decrement for ordered list lookup. A failed decrement at a nonempty
list selects the zero index. One list visit and the inspected
decrement bits per visited cell, including the successful target.
No encoding, allocation or total machine-cost claim. -/
namespace ProctorBinaryLookup
open ProctorDecimalBitWidth (bitsValue)
open ProctorCheckedDecrement (decMeter dec_sound dec_reject_iff dec_visit_bound)
open ProctorCheckedBinaryScanner (encode encode_complete encode_sound cap)
open ProctorCapacityReplay (getAt)
open ProctorTerminalPolynomial (mul_mono)

def lookupBits {α : Type} : List α → List Bool → Option α × Nat
  | [],_ => (none,0)
  | a::as,c =>
    let r := decMeter c
    match r.1 with
    | none => (some a,r.2+1)
    | some d =>
      let q := lookupBits as d
      (q.1,q.2+(r.2+1))

theorem lookup_projection {α : Type} (xs : List α) (c : List Bool) :
    (lookupBits xs c).1=getAt xs (bitsValue c) := by
  induction xs generalizing c with
  | nil => rfl
  | cons a as ih =>
    rw [lookupBits]
    cases e : (decMeter c).1 with
    | none =>
      have h := (dec_reject_iff c).mp e
      rw [h]
      rfl
    | some d =>
      change (lookupBits as d).1=getAt (a::as) (bitsValue c)
      rw [← (dec_sound c d e).right]
      exact ih d

theorem lookup_bound {α : Type} (xs : List α) (c : List Bool) :
    (lookupBits xs c).2≤(c.length+1)*xs.length := by
  induction xs generalizing c with
  | nil => exact Nat.le_refl 0
  | cons a as ih =>
    rw [lookupBits]
    cases e : (decMeter c).1 with
    | none =>
      change (decMeter c).2+1≤(c.length+1)*as.length+(c.length+1)
      exact Nat.le_trans (Nat.succ_le_succ (dec_visit_bound c)) (Nat.le_add_left _ _)
    | some d =>
      change (lookupBits as d).2+((decMeter c).2+1)≤
        (c.length+1)*as.length+(c.length+1)
      have h := ih d
      rw [(dec_sound c d e).left] at h
      exact Nat.add_le_add h (Nat.succ_le_succ (dec_visit_bound c))

theorem index_bound {α : Type} (xs : List α) (c : List Bool) :
    (lookupBits xs c).2≤(c.length+1)*(bitsValue c+1) := by
  induction xs generalizing c with
  | nil => exact Nat.zero_le _
  | cons a as ih =>
    rw [lookupBits]
    cases e : (decMeter c).1 with
    | none =>
      change (decMeter c).2+1≤(c.length+1)*bitsValue c+(c.length+1)
      exact Nat.le_trans (Nat.succ_le_succ (dec_visit_bound c)) (Nat.le_add_left _ _)
    | some d =>
      change (lookupBits as d).2+((decMeter c).2+1)≤
        (c.length+1)*bitsValue c+(c.length+1)
      have h := ih d
      have hd := dec_sound c d e
      rw [hd.left,hd.right] at h
      exact Nat.add_le_add h (Nat.succ_le_succ (dec_visit_bound c))

theorem formula_lookup_value (f : ProctorHallDeficiency.Formula) (i : Nat) :
    getAt f i=ProctorExecutableReplay.lookup f i := by
  induction f generalizing i with
  | nil => rfl
  | cons a as ih =>
    cases i with
    | zero => rfl
    | succ i => exact ih i

def checkedLookup {α : Type} (w : Nat) (xs : List α) (i : Nat) : Option α × Nat :=
  match encode w i with
  | none => (none,0)
  | some c => lookupBits xs c

theorem checked_projection {α : Type} (w : Nat) (xs : List α) (i : Nat)
    (h : i<cap w) :
    (checkedLookup w xs i).1=getAt xs i := by
  obtain ⟨c,e⟩ := encode_complete w i h
  unfold checkedLookup
  rw [e]
  exact (lookup_projection xs c).trans (congrArg (getAt xs) (encode_sound w i c e).right)

theorem checked_bound {α : Type} (w : Nat) (xs : List α) (i : Nat) :
    (checkedLookup w xs i).2≤(w+1)*xs.length := by
  unfold checkedLookup
  cases e : encode w i with
  | none => exact Nat.zero_le _
  | some c =>
    have h := lookup_bound xs c
    rw [(encode_sound w i c e).left] at h
    exact h

theorem checked_formula_projection (w : Nat) (f : ProctorHallDeficiency.Formula)
    (i : Nat) (h : i<cap w) :
    (checkedLookup w f i).1=ProctorExecutableReplay.lookup f i :=
  (checked_projection w f i h).trans (formula_lookup_value f i)

theorem checked_formula_bound (f : ProctorHallDeficiency.Formula) (i : Nat) :
    (checkedLookup 512 f i).2≤513*f.length :=
  checked_bound 512 f i

end ProctorBinaryLookup

#print axioms ProctorBinaryLookup.lookup_projection
#print axioms ProctorBinaryLookup.lookup_bound
#print axioms ProctorBinaryLookup.index_bound
#print axioms ProctorBinaryLookup.formula_lookup_value
#print axioms ProctorBinaryLookup.checked_projection
#print axioms ProctorBinaryLookup.checked_bound
#print axioms ProctorBinaryLookup.checked_formula_projection
#print axioms ProctorBinaryLookup.checked_formula_bound
