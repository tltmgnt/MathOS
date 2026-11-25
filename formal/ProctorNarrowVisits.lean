/-! F034: selected structural visits for checked narrowing and
zero detection. One charge per inspected zero-test bit or requested
output position, including padding and rejection. No allocation,
Nat conversion, or full machine-cost claim. -/
namespace ProctorNarrowVisits
open ProctorCheckedBinaryScanner (zeroBits narrow low high encode encode_sound checkedDigit)
open ProctorBinaryPrimitives (decimalMeter decimal_bound compareMeter addMeter add_length)
open ProctorStructuralCounters (bumpBelow increment)
open ProctorScannerCounters (nextCount countLimit)

def zeroMeter : List Bool → Bool × Nat
  | [] => (true,0)
  | true::_ => (false,1)
  | false::xs => let r := zeroMeter xs; (r.1,r.2+1)

theorem zero_projection (xs : List Bool) : (zeroMeter xs).1=zeroBits xs := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    cases a with
    | true => rfl
    | false => exact ih

theorem zero_bound (xs : List Bool) : (zeroMeter xs).2≤xs.length := by
  induction xs with
  | nil => exact Nat.le_refl 0
  | cons a xs ih =>
    cases a with
    | true => exact Nat.succ_le_succ (Nat.zero_le _)
    | false => exact Nat.succ_le_succ ih

def narrowMeter : Nat → List Bool → Option (List Bool) × Nat
  | 0,xs =>
    let r := zeroMeter xs
    (if r.1 then some [] else none,r.2)
  | w+1,xs =>
    let r := narrowMeter w (high xs)
    (match r.1 with
      | none => none
      | some t => some (low xs::t),r.2+1)

theorem narrow_projection (w : Nat) (xs : List Bool) :
    (narrowMeter w xs).1=narrow w xs := by
  induction w generalizing xs with
  | zero =>
    change (if (zeroMeter xs).1 then some [] else none)=
      (if zeroBits xs then some [] else none)
    rw [zero_projection]
  | succ w ih =>
    change (match (narrowMeter w (high xs)).1 with
      | none => none
      | some t => some (low xs::t))=
      (match narrow w (high xs) with
      | none => none
      | some t => some (low xs::t))
    rw [ih]

private theorem shift (a b : Nat) : (a+1)+b=(a+b)+1 := by
  calc
    (a+1)+b = a+(1+b) := Nat.add_assoc _ _ _
    _ = a+(b+1) := congrArg (fun n => a+n) (Nat.add_comm _ _)
    _ = (a+b)+1 := (Nat.add_assoc _ _ _).symm

theorem narrow_bound (w extra : Nat) (xs : List Bool)
    (h : xs.length≤w+extra) : (narrowMeter w xs).2≤w+extra := by
  induction w generalizing xs with
  | zero => exact Nat.le_trans (zero_bound xs) h
  | succ w ih =>
    change (narrowMeter w (high xs)).2+1≤(w+1)+extra
    rw [shift]
    apply Nat.succ_le_succ
    apply ih
    cases xs with
    | nil => exact Nat.zero_le _
    | cons a xs =>
      change xs.length+1≤(w+1)+extra at h
      rw [shift] at h
      exact Nat.le_of_succ_le_succ h

theorem narrow_minimum (w : Nat) (xs : List Bool) :
    w≤(narrowMeter w xs).2 := by
  induction w generalizing xs with
  | zero => exact Nat.zero_le _
  | succ w ih => exact Nat.succ_le_succ (ih (high xs))

def digitNarrowMeter (v : List Bool) (b : Nat) : Option (List Bool) × Nat :=
  match encode 4 (b-48) with
  | none => (none,0)
  | some d => narrowMeter 512 (decimalMeter v d).1

theorem digit_projection (v : List Bool) (b : Nat) :
    (digitNarrowMeter v b).1=checkedDigit v b := by
  unfold digitNarrowMeter checkedDigit
  cases e : encode 4 (b-48) with
  | none => rfl
  | some d => exact narrow_projection 512 (decimalMeter v d).1

theorem digit_bound (v : List Bool) (b : Nat) (hv : v.length≤512) :
    (digitNarrowMeter v b).2≤517 := by
  unfold digitNarrowMeter
  cases e : encode 4 (b-48) with
  | none => exact Nat.zero_le _
  | some d =>
    have hd : d.length≤4 := by
      rw [(encode_sound 4 (b-48) d e).left]
      exact Nat.le_refl _
    exact narrow_bound 512 5 (decimalMeter v d).1
      (decimal_bound v d 512 hv hd).left

def countNarrowMeter (c : List Bool) : Option (List Bool) × Nat :=
  if (compareMeter c countLimit).1 then narrowMeter 8 (addMeter c [true]).1
  else (none,0)

theorem count_projection (c : List Bool) :
    (countNarrowMeter c).1=nextCount c := by
  unfold countNarrowMeter nextCount bumpBelow increment
  cases e : (compareMeter c countLimit).1 with
  | false => rfl
  | true => exact narrow_projection 8 (addMeter c [true]).1

theorem count_bound (c : List Bool) (hc : c.length≤8) :
    (countNarrowMeter c).2≤9 := by
  unfold countNarrowMeter
  cases e : (compareMeter c countLimit).1 with
  | false => exact Nat.zero_le _
  | true =>
    exact narrow_bound 8 1 (addMeter c [true]).1
      (add_length c [true] 8 hc (by decide))

end ProctorNarrowVisits

#print axioms ProctorNarrowVisits.zero_projection
#print axioms ProctorNarrowVisits.zero_bound
#print axioms ProctorNarrowVisits.narrow_projection
#print axioms ProctorNarrowVisits.narrow_bound
#print axioms ProctorNarrowVisits.narrow_minimum
#print axioms ProctorNarrowVisits.digit_projection
#print axioms ProctorNarrowVisits.digit_bound
#print axioms ProctorNarrowVisits.count_projection
#print axioms ProctorNarrowVisits.count_bound
