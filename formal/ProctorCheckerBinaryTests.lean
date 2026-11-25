/-! F034 candidate: unsigned identifier range and equality tests
on arbitrary finite little-endian binary words. Use existing
verified borrow circuits with zero padding; no truncation.
Gate budgets exclude encoding, padding allocation and routing. -/
namespace ProctorCheckerBinaryTests
open ProctorDecimalBitWidth (bitsValue)
open ProctorBinaryPrimitives (compareMeter compare_value compare_gates)
open ProctorCapacityReplay (test)
open ProctorUnifiedReplay (validId)
open ProctorCheckedBinaryScanner (encode encode_sound encode_complete cap)

private theorem compare_test (a b : List Bool) :
    (compareMeter a b).1=test (bitsValue a<bitsValue b) := by
  unfold test
  by_cases h : bitsValue a<bitsValue b
  · rw [if_pos h]
    exact (compare_value a b).2 h
  · rw [if_neg h]
    cases e : (compareMeter a b).1 with
    | false => rfl
    | true => exact False.elim (h ((compare_value a b).1 e))

private theorem not_less_test (a b : Nat) :
    !(test (a<b))=test (b≤a) := by
  unfold test
  by_cases h : a<b
  · rw [if_pos h,if_neg (Nat.not_le_of_gt h)]
    rfl
  · rw [if_neg h,if_pos (Nat.le_of_not_gt h)]
    rfl

def eqMeter (a b : List Bool) : Bool × Nat :=
  let l := compareMeter a b
  let r := compareMeter b a
  (!l.1 && !r.1,l.2+r.2+3)

theorem eq_value (a b : List Bool) :
    (eqMeter a b).1=test (bitsValue a=bitsValue b) := by
  change (!(compareMeter a b).1 && !(compareMeter b a).1)=_
  rw [compare_test a b,compare_test b a,
    not_less_test (bitsValue a) (bitsValue b),
    not_less_test (bitsValue b) (bitsValue a)]
  unfold test
  by_cases h : bitsValue a=bitsValue b
  · rw [if_pos h,if_pos (Nat.le_of_eq h.symm),if_pos (Nat.le_of_eq h)]
    rfl
  · rw [if_neg h]
    by_cases le : bitsValue b≤bitsValue a
    · have ne : ¬ bitsValue a≤bitsValue b := fun e => h (Nat.le_antisymm e le)
      rw [if_pos le,if_neg ne]
      rfl
    · rw [if_neg le]
      rfl

theorem eq_gate_bound (a b : List Bool) (w : Nat)
    (ha : a.length≤w) (hb : b.length≤w) :
    (eqMeter a b).2≤(5*w+5*w)+3 :=
  Nat.add_le_add (Nat.add_le_add (compare_gates a b w ha hb)
    (compare_gates b a w hb ha)) (Nat.le_refl 3)

def idMeter (n v : List Bool) : Bool × Nat :=
  let positive := compareMeter [] v
  let above := compareMeter n v
  (positive.1 && !above.1,positive.2+above.2+2)

theorem id_value (n v : List Bool) :
    (idMeter n v).1=validId (bitsValue n) (bitsValue v) := by
  change ((compareMeter [] v).1 && !(compareMeter n v).1)=_
  rw [compare_test [] v,compare_test n v,not_less_test (bitsValue n) (bitsValue v)]
  rfl

theorem id_gate_bound (n v : List Bool) (w : Nat)
    (hn : n.length≤w) (hv : v.length≤w) :
    (idMeter n v).2≤(5*w+5*w)+2 :=
  Nat.add_le_add (Nat.add_le_add (compare_gates [] v w (Nat.zero_le _) hv)
    (compare_gates n v w hn hv)) (Nat.le_refl 2)

-- Nat adapters explicitly reject unrepresentable operands. Encoding
-- itself is outside this circuit gate ledger.
def checkedTest (w : Nat) (f : List Bool → List Bool → Bool × Nat)
    (a b : Nat) : Option Bool × Nat :=
  match encode w a,encode w b with
  | some x,some y => let r := f x y; (some r.1,r.2)
  | _,_ => (none,0)

theorem checked_projection (w : Nat)
    (f : List Bool → List Bool → Bool × Nat) (plain : Nat → Nat → Bool)
    (hf : ∀ x y, (f x y).1=plain (bitsValue x) (bitsValue y))
    (a b : Nat) (ha : a<cap w) (hb : b<cap w) :
    (checkedTest w f a b).1=some (plain a b) := by
  obtain ⟨x,ex⟩ := encode_complete w a ha
  obtain ⟨y,ey⟩ := encode_complete w b hb
  unfold checkedTest
  rw [ex,ey]
  change some (f x y).1=some (plain a b)
  rw [hf x y,(encode_sound w a x ex).right,(encode_sound w b y ey).right]

theorem checked_bound (w K : Nat)
    (f : List Bool → List Bool → Bool × Nat)
    (hf : ∀ x y, x.length≤w → y.length≤w → (f x y).2≤K)
    (a b : Nat) : (checkedTest w f a b).2≤K := by
  unfold checkedTest
  cases ex : encode w a with
  | none => exact Nat.zero_le _
  | some x =>
    cases ey : encode w b with
    | none => exact Nat.zero_le _
    | some y =>
      have hx : x.length≤w := by
        rw [(encode_sound w a x ex).left]
        exact Nat.le_refl _
      have hy : y.length≤w := by
        rw [(encode_sound w b y ey).left]
        exact Nat.le_refl _
      exact hf x y hx hy

def checkedEq (w : Nat) := checkedTest w eqMeter
def checkedId (w : Nat) := checkedTest w idMeter

theorem checked_eq_value (w a b : Nat) (ha : a<cap w) (hb : b<cap w) :
    (checkedEq w a b).1=some (test (a=b)) :=
  checked_projection w eqMeter (fun x y => test (x=y)) eq_value a b ha hb

theorem checked_id_value (w n v : Nat) (hn : n<cap w) (hv : v<cap w) :
    (checkedId w n v).1=some (validId n v) :=
  checked_projection w idMeter validId id_value n v hn hv

theorem checked_eq_bound (w a b : Nat) :
    (checkedEq w a b).2≤(5*w+5*w)+3 :=
  checked_bound w _ eqMeter (fun x y => eq_gate_bound x y w) a b

theorem checked_id_bound (w n v : Nat) :
    (checkedId w n v).2≤(5*w+5*w)+2 :=
  checked_bound w _ idMeter (fun x y => id_gate_bound x y w) n v

end ProctorCheckerBinaryTests

#print axioms ProctorCheckerBinaryTests.eq_value
#print axioms ProctorCheckerBinaryTests.eq_gate_bound
#print axioms ProctorCheckerBinaryTests.id_value
#print axioms ProctorCheckerBinaryTests.id_gate_bound
#print axioms ProctorCheckerBinaryTests.checked_projection
#print axioms ProctorCheckerBinaryTests.checked_bound
#print axioms ProctorCheckerBinaryTests.checked_eq_value
#print axioms ProctorCheckerBinaryTests.checked_id_value
#print axioms ProctorCheckerBinaryTests.checked_eq_bound
#print axioms ProctorCheckerBinaryTests.checked_id_bound
