/-! F034: checked little-endian decrement with an explicit visited-bit
ledger. Each inspected input bit costs one, even on rejection. This
is not a Boolean gate or complete machine-cost model. -/
namespace ProctorCheckedDecrement
open ProctorDecimalBitWidth (bitsValue)
open ProctorCheckedBinaryScanner (zeroBits zero_complete)

def decMeter : List Bool → Option (List Bool) × Nat
  | [] => (none,0)
  | true::xs => (some (false::xs),1)
  | false::xs =>
    let r := decMeter xs
    ((match r.1 with
      | none => none
      | some ys => some (true::ys)), r.2+1)

theorem dec_sound (xs ys : List Bool) (h : (decMeter xs).1=some ys) :
    ys.length=xs.length ∧ bitsValue ys+1=bitsValue xs := by
  induction xs generalizing ys with
  | nil => cases h
  | cons b xs ih =>
    cases b with
    | true =>
      change some (false::xs)=some ys at h
      cases h
      refine ⟨rfl,?_⟩
      change (0+2*bitsValue xs)+1=1+2*bitsValue xs
      rw [Nat.zero_add,Nat.add_comm (2*bitsValue xs) 1]
    | false =>
      change (match (decMeter xs).1 with
        | none => none
        | some t => some (true::t))=some ys at h
      cases e : (decMeter xs).1 with
      | none => rw [e] at h; cases h
      | some t =>
        rw [e] at h
        cases h
        have ht := ih t e
        refine ⟨congrArg Nat.succ ht.left,?_⟩
        change (1+2*bitsValue t)+1=0+2*bitsValue xs
        calc
          (1+2*bitsValue t)+1 = (2*bitsValue t+1)+1 :=
            congrArg (fun n => n+1) (Nat.add_comm _ _)
          _ = 2*(bitsValue t+1) := rfl
          _ = 2*bitsValue xs := congrArg (fun n => 2*n) ht.right
          _ = 0+2*bitsValue xs := (Nat.zero_add _).symm

theorem dec_complete (xs : List Bool) (h : 0<bitsValue xs) :
    ∃ ys, (decMeter xs).1=some ys := by
  induction xs with
  | nil => cases h
  | cons b xs ih =>
    cases b with
    | true => exact ⟨false::xs,rfl⟩
    | false =>
      have ht : 0<bitsValue xs := by
        cases e : bitsValue xs with
        | zero =>
          change 0<0+2*bitsValue xs at h
          rw [e] at h
          cases h
        | succ n => exact Nat.succ_le_succ (Nat.zero_le n)
      obtain ⟨t,e⟩ := ih ht
      refine ⟨true::t,?_⟩
      change (match (decMeter xs).1 with
        | none => none
        | some u => some (true::u))=some (true::t)
      rw [e]

theorem dec_iff (xs : List Bool) :
    (∃ ys, (decMeter xs).1=some ys) ↔ 0<bitsValue xs := by
  constructor
  · intro h
    obtain ⟨ys,e⟩ := h
    have hs := dec_sound xs ys e
    rw [← hs.right]
    exact Nat.succ_le_succ (Nat.zero_le _)
  · exact dec_complete xs

theorem dec_reject_iff (xs : List Bool) :
    (decMeter xs).1=none ↔ bitsValue xs=0 := by
  constructor
  · intro h
    cases e : bitsValue xs with
    | zero => rfl
    | succ n =>
      have hp : 0<bitsValue xs := by
        rw [e]
        exact Nat.succ_le_succ (Nat.zero_le n)
      obtain ⟨ys,hy⟩ := dec_complete xs hp
      rw [h] at hy
      cases hy
  · intro h
    cases e : (decMeter xs).1 with
    | none => rfl
    | some ys =>
      have hs := (dec_sound xs ys e).right
      rw [h] at hs
      cases hs

theorem dec_visit_bound (xs : List Bool) : (decMeter xs).2≤xs.length := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons b xs ih =>
    cases b with
    | true => exact Nat.succ_le_succ (Nat.zero_le _)
    | false => exact Nat.succ_le_succ ih

theorem dec_zero_visits (xs : List Bool) (h : zeroBits xs=true) :
    (decMeter xs).2=xs.length := by
  induction xs with
  | nil => rfl
  | cons b xs ih =>
    cases b with
    | true => cases h
    | false =>
      change zeroBits xs=true at h
      exact congrArg Nat.succ (ih h)

theorem dec_zero_boundary (xs : List Bool) (h : bitsValue xs=0) :
    (decMeter xs).1=none ∧ (decMeter xs).2=xs.length :=
  ⟨(dec_reject_iff xs).mpr h,dec_zero_visits xs (zero_complete xs h)⟩

end ProctorCheckedDecrement

#print axioms ProctorCheckedDecrement.dec_sound
#print axioms ProctorCheckedDecrement.dec_complete
#print axioms ProctorCheckedDecrement.dec_iff
#print axioms ProctorCheckedDecrement.dec_reject_iff
#print axioms ProctorCheckedDecrement.dec_visit_bound
#print axioms ProctorCheckedDecrement.dec_zero_visits
#print axioms ProctorCheckedDecrement.dec_zero_boundary
