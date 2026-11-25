/-! F034 candidate: checked unsigned structural counters.
Only comparison and addition Boolean gates are charged. Encoding,
narrowing, storage, routing, and all scanner/parser integration costs
remain outside this ledger. -/
namespace ProctorStructuralCounters
open ProctorDecimalBitWidth (bitsValue)
open ProctorBinaryPrimitives (compareMeter compare_value compare_gates addMeter add_value add_bound)
open ProctorCheckedBinaryScanner (cap encode encode_sound encode_complete narrow narrow_sound narrow_complete value_bound)
open ProctorDataParser (digitLimit listLimit byteLimit)

theorem digit_capacity : digitLimit<cap 8 := by decide
theorem list_capacity : listLimit<cap 17 := by decide
theorem byte_capacity : byteLimit<cap 20 := by decide

-- Explicit increment; retained carry is checked rather than discarded.
def increment (w : Nat) (x : List Bool) : Option (List Bool) :=
  narrow w (addMeter x [true]).1

theorem increment_sound (w : Nat) (x y : List Bool)
    (h : increment w x=some y) :
    y.length=w ∧ bitsValue y=bitsValue x+1 := by
  have hs := narrow_sound w (addMeter x [true]).1 y h
  refine ⟨hs.left,?_⟩
  rw [hs.right,add_value]
  rfl

theorem increment_complete (w : Nat) (x : List Bool)
    (h : bitsValue x+1<cap w) : ∃ y, increment w x=some y := by
  unfold increment
  apply narrow_complete
  rw [add_value]
  exact h

theorem increment_iff (w : Nat) (x : List Bool) :
    (∃ y, increment w x=some y) ↔ bitsValue x+1<cap w := by
  constructor
  · intro h
    obtain ⟨y,e⟩ := h
    have hs := increment_sound w x y e
    have hv := value_bound y
    rw [hs.left,hs.right] at hv
    exact hv
  · exact increment_complete w x

-- The bound word is supplied explicitly (e.g. an encoded static limit).
-- Reject at the inclusive limit and reject representational overflow.
def bumpBelow (w : Nat) (x limit : List Bool) : Option (List Bool) :=
  if (compareMeter x limit).1 then increment w x else none

theorem bump_sound (w : Nat) (x limit y : List Bool)
    (h : bumpBelow w x limit=some y) :
    y.length=w ∧ bitsValue y=bitsValue x+1 ∧ bitsValue y≤bitsValue limit := by
  unfold bumpBelow at h
  cases e : (compareMeter x limit).1 with
  | false => rw [e] at h; cases h
  | true =>
    rw [e] at h
    have hs := increment_sound w x y h
    have lt := (compare_value x limit).mp e
    refine ⟨hs.left,hs.right,?_⟩
    rw [hs.right]
    exact lt

theorem bump_complete (w : Nat) (x limit : List Bool)
    (hl : bitsValue limit<cap w) (h : bitsValue x<bitsValue limit) :
    ∃ y, bumpBelow w x limit=some y := by
  have he := (compare_value x limit).mpr h
  have fit : bitsValue x+1<cap w := Nat.lt_of_le_of_lt h hl
  obtain ⟨y,e⟩ := increment_complete w x fit
  refine ⟨y,?_⟩
  unfold bumpBelow
  rw [he] <;> exact e

theorem bump_iff (w : Nat) (x limit : List Bool)
    (hl : bitsValue limit<cap w) :
    (∃ y, bumpBelow w x limit=some y) ↔ bitsValue x<bitsValue limit := by
  constructor
  · intro h
    obtain ⟨y,e⟩ := h
    have hs := bump_sound w x limit y e
    have hb := hs.right.right
    rw [hs.right.left] at hb
    exact hb
  · exact bump_complete w x limit hl

-- Build a checked limit word at the boundary; its conversion is not
-- included in the circuit charges below.
def bumpNatLimit (w n : Nat) (x : List Bool) : Option (List Bool) :=
  match encode w n with
  | none => none
  | some limit => bumpBelow w x limit

theorem bump_nat_refines (w n : Nat) (x : List Bool)
    (hn : n<cap w) (hx : bitsValue x<n) :
    ∃ y, bumpNatLimit w n x=some y ∧
      y.length=w ∧ bitsValue y=bitsValue x+1 ∧ bitsValue y≤n := by
  obtain ⟨limit,e⟩ := encode_complete w n hn
  have hs := encode_sound w n limit e
  have hl : bitsValue limit<cap w := by
    rw [hs.right]
    exact hn
  have hlt : bitsValue x<bitsValue limit := by
    rw [hs.right]
    exact hx
  obtain ⟨y,ey⟩ := bump_complete w x limit hl hlt
  have hy := bump_sound w x limit y ey
  refine ⟨y,?_,hy.left,hy.right.left,?_⟩
  · unfold bumpNatLimit
    rw [e]
    change bumpBelow w x limit=some y
    exact ey
  · rw [← hs.right]
    exact hy.right.right

-- Gate ledger for one attempted guard and increment, charging both
-- circuits even when the guard rejects (an upper bound).
def bumpBudget (x limit : List Bool) : Nat :=
  (compareMeter x limit).2+(addMeter x [true]).2

theorem bump_gate_bound (w : Nat) (x limit : List Bool)
    (hw : 1≤w) (hx : x.length≤w) (hl : limit.length≤w) :
    bumpBudget x limit≤5*w+5*w := by
  unfold bumpBudget
  exact Nat.add_le_add (compare_gates x limit w hx hl)
    (add_bound x [true] w hx hw)

theorem digit_bump (x : List Bool) (h : bitsValue x<digitLimit) :
    ∃ y, bumpNatLimit 8 digitLimit x=some y ∧
      y.length=8 ∧ bitsValue y=bitsValue x+1 ∧ bitsValue y≤digitLimit :=
  bump_nat_refines 8 digitLimit x digit_capacity h

theorem list_bump (x : List Bool) (h : bitsValue x<listLimit) :
    ∃ y, bumpNatLimit 17 listLimit x=some y ∧
      y.length=17 ∧ bitsValue y=bitsValue x+1 ∧ bitsValue y≤listLimit :=
  bump_nat_refines 17 listLimit x list_capacity h

theorem byte_bump (x : List Bool) (h : bitsValue x<byteLimit) :
    ∃ y, bumpNatLimit 20 byteLimit x=some y ∧
      y.length=20 ∧ bitsValue y=bitsValue x+1 ∧ bitsValue y≤byteLimit :=
  bump_nat_refines 20 byteLimit x byte_capacity h

end ProctorStructuralCounters

#print axioms ProctorStructuralCounters.digit_capacity
#print axioms ProctorStructuralCounters.list_capacity
#print axioms ProctorStructuralCounters.byte_capacity
#print axioms ProctorStructuralCounters.increment_sound
#print axioms ProctorStructuralCounters.increment_complete
#print axioms ProctorStructuralCounters.increment_iff
#print axioms ProctorStructuralCounters.bump_sound
#print axioms ProctorStructuralCounters.bump_complete
#print axioms ProctorStructuralCounters.bump_iff
#print axioms ProctorStructuralCounters.bump_nat_refines
#print axioms ProctorStructuralCounters.bump_gate_bound
#print axioms ProctorStructuralCounters.digit_bump
#print axioms ProctorStructuralCounters.list_bump
#print axioms ProctorStructuralCounters.byte_bump
