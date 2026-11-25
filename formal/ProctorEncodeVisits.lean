/-! F034: selected boundary encoder work. Count one Nat comparison
per level (including the residual zero test), one Nat subtraction on
the high branch, one abstract cap multiplication per recursive cap
level, and one append visit per existing output bit on success.
These are selected source-level events, not Nat bit costs. -/
namespace ProctorEncodeVisits
open ProctorCheckedBinaryScanner (cap encode encode_sound)

def chargeAppend (b : Bool) (localCost : Nat)
    (r : Option (List Bool) × Nat) : Option (List Bool) × Nat :=
  match r.1 with
  | none => (none,r.2+localCost)
  | some t => (some (t++[b]),(r.2+localCost)+t.length)

def encodeMeter : Nat → Nat → Option (List Bool) × Nat
  | 0,n => (if n=0 then some [] else none,1)
  | w+1,n =>
    if n<cap w then chargeAppend false (w+1) (encodeMeter w n)
    else chargeAppend true (w+2) (encodeMeter w (n-cap w))

private theorem append_projection (b : Bool) (k : Nat)
    (r : Option (List Bool) × Nat) :
    (chargeAppend b k r).1=(match r.1 with
      | none => none
      | some t => some (t++[b])) := by
  cases r with
  | mk out cost => cases out <;> rfl

theorem encode_projection (w n : Nat) : (encodeMeter w n).1=encode w n := by
  induction w generalizing n with
  | zero => rfl
  | succ w ih =>
    rw [encodeMeter,encode]
    by_cases h : n<cap w
    · rw [if_pos h,if_pos h,append_projection,ih]
    · rw [if_neg h,if_neg h,append_projection,ih]

-- Quadratic in requested width; deliberately independent of Nat
-- operand magnitude, because a Nat operation is one abstract event.
def budget : Nat → Nat
  | 0 => 1
  | w+1 => (budget w+(w+2))+w

private theorem append_bound (b : Bool) (k w C K : Nat)
    (r : Option (List Bool) × Nat)
    (hc : r.2≤C) (hk : k≤K)
    (hw : ∀ t, r.1=some t → t.length≤w) :
    (chargeAppend b k r).2≤(C+K)+w := by
  cases r with
  | mk out cost =>
    cases out with
    | none =>
      exact Nat.le_trans (Nat.add_le_add hc hk) (Nat.le_add_right _ _)
    | some t =>
      exact Nat.add_le_add (Nat.add_le_add hc hk) (hw t rfl)

theorem encode_bound (w n : Nat) : (encodeMeter w n).2≤budget w := by
  induction w generalizing n with
  | zero => exact Nat.le_refl 1
  | succ w ih =>
    rw [encodeMeter]
    by_cases h : n<cap w
    · rw [if_pos h]
      exact append_bound false (w+1) w (budget w) (w+2) (encodeMeter w n)
        (ih n) (Nat.le_succ _) (fun t e => by
          rw [encode_projection] at e
          rw [(encode_sound w n t e).left]
          exact Nat.le_refl _)
    · rw [if_neg h]
      exact append_bound true (w+2) w (budget w) (w+2)
        (encodeMeter w (n-cap w)) (ih _) (Nat.le_refl _) (fun t e => by
          rw [encode_projection] at e
          rw [(encode_sound w (n-cap w) t e).left]
          exact Nat.le_refl _)

theorem four_bound (n : Nat) : (encodeMeter 4 n).2≤21 :=
  encode_bound 4 n

theorem seventeen_bound (n : Nat) : (encodeMeter 17 n).2≤307 :=
  encode_bound 17 n

theorem encode_sound_meter (w n : Nat) (t : List Bool)
    (h : (encodeMeter w n).1=some t) :
    t.length=w ∧ ProctorDecimalBitWidth.bitsValue t=n := by
  rw [encode_projection] at h
  exact encode_sound w n t h

end ProctorEncodeVisits

#print axioms ProctorEncodeVisits.encode_projection
#print axioms ProctorEncodeVisits.encode_bound
#print axioms ProctorEncodeVisits.four_bound
#print axioms ProctorEncodeVisits.seventeen_bound
#print axioms ProctorEncodeVisits.encode_sound_meter
