/-! F008: highest-bit elimination and back-substitution invariants. -/
namespace ProctorGF2

def Highest (a p : Nat) : Prop :=
  2^p ≤ a ∧ a < 2^(p+1)

theorem highest_bit (a p : Nat) (h : Highest a p) : a.testBit p = true := by
  cases e : a.testBit p with
  | true => rfl
  | false =>
    have bound : a < 2^p := Nat.lt_pow_two_of_testBit a (by
      intro i hi
      by_cases he : i = p
      · exact he.symm ▸ e
      · exact Nat.testBit_lt_two_pow (Nat.lt_of_lt_of_le h.right
          (Nat.pow_le_pow_of_le_right Nat.zero_lt_two (by omega))))
    exact False.elim (Nat.not_lt_of_ge h.left bound)

theorem highest_descent (a b p : Nat) (ha : Highest a p) (hb : Highest b p) :
    a ^^^ b < 2^p := by
  apply Nat.lt_pow_two_of_testBit
  intro i hi
  by_cases he : i = p
  · subst i
    rw [Nat.testBit_xor,highest_bit a p ha,highest_bit b p hb]
    rfl
  · have hle : p+1 ≤ i := by omega
    have ea : a.testBit i = false := Nat.testBit_lt_two_pow
      (Nat.lt_of_lt_of_le ha.right (Nat.pow_le_pow_of_le_right Nat.zero_lt_two hle))
    have eb : b.testBit i = false := Nat.testBit_lt_two_pow
      (Nat.lt_of_lt_of_le hb.right (Nat.pow_le_pow_of_le_right Nat.zero_lt_two hle))
    rw [Nat.testBit_xor,ea,eb]
    rfl

theorem pivot_strict_decrease (a b p : Nat) (ha : Highest a p) (hb : Highest b p) :
    a ^^^ b < a :=
  Nat.lt_of_lt_of_le (highest_descent a b p ha hb) ha.left

theorem next_pivot_lower (a b p q : Nat) (ha : Highest a p) (hb : Highest b p)
    (hq : Highest (a ^^^ b) q) : q < p := by
  apply Nat.lt_of_not_ge
  intro h
  have le := Nat.pow_le_pow_of_le_right Nat.zero_lt_two h
  exact Nat.not_lt_of_ge (Nat.le_trans le hq.left) (highest_descent a b p ha hb)

def maskAdd (p r : Nat × Bool) : Nat × Bool := (p.1 ^^^ r.1,bx p.2 r.2)

theorem decode_row_add (n : Nat) (p r : Nat × Bool) :
    maskRow n (maskAdd p r) = addRow (maskRow n p) (maskRow n r) := by
  exact congrArg (fun a => Row.mk a (bx p.2 r.2)) (decode_xor n p.1 r.1 0)

theorem mask_replace (n : Nat) (p r : Nat × Bool) (x : Nat) :
    (maskSat n p x ∧ maskSat n r x) ↔
    (maskSat n p x ∧ maskSat n (maskAdd p r) x) := by
  have ep := maskSat_iff n p x
  have er := maskSat_iff n r x
  have ea := maskSat_iff n (maskAdd p r) x
  have ec := decode_row_add n p r
  constructor
  · intro h
    have hs := add_sound (maskRow n p) (maskRow n r) (decode n x) (ep.mpr h.left) (er.mpr h.right)
    exact ⟨h.left,ea.mp (ec.symm ▸ hs)⟩
  · intro h
    have hs : Sat (addRow (maskRow n p) (maskRow n r)) (decode n x) :=
      ec ▸ ea.mpr h.right
    exact ⟨h.left,er.mp (add_reverse (maskRow n p) (maskRow n r) (decode n x) (ep.mpr h.left) hs)⟩

-- Provenance uses the same natural-number XOR as the Python proof mask.
def MaskProvenance (n : Nat) (orig : List (Nat × Bool)) (r : Nat × Bool) (w : Nat) : Prop :=
  (∀ x : List Bool, dot (decode n r.1) x = lhs (orig.map (maskRow n)) (decode orig.length w) x) ∧
  r.2 = rhs (orig.map (maskRow n)) (decode orig.length w)

theorem provenance_xor (n : Nat) (orig : List (Nat × Bool))
    (p r : Nat × Bool) (u v : Nat)
    (hp : MaskProvenance n orig p u) (hr : MaskProvenance n orig r v) :
    MaskProvenance n orig (maskAdd p r) (u ^^^ v) := by
  constructor
  · intro x
    let vals := (orig.map (maskRow n)).map (fun r : Row => dot r.coeff x)
    change dot (decode n (p.1 ^^^ r.1)) x = dot (decode orig.length (u ^^^ v)) vals
    have ep : dot (decode n p.1) x = dot (decode orig.length u) vals := hp.left x
    have er : dot (decode n r.1) x = dot (decode orig.length v) vals := hr.left x
    rw [show decode n (p.1 ^^^ r.1) = addVec (decode n p.1) (decode n r.1) from decode_xor n p.1 r.1 0,
        dot_add,ep,er,show decode orig.length (u ^^^ v) = addVec (decode orig.length u) (decode orig.length v) from decode_xor orig.length u v 0,dot_add]
  · let vals := (orig.map (maskRow n)).map Row.rhs
    change bx p.2 r.2 = dot (decode orig.length (u ^^^ v)) vals
    have ep : p.2 = dot (decode orig.length u) vals := hp.right
    have er : r.2 = dot (decode orig.length v) vals := hr.right
    rw [ep,er,show decode orig.length (u ^^^ v) = addVec (decode orig.length u) (decode orig.length v) from decode_xor orig.length u v 0,dot_add]

theorem zero_mask_dot (n : Nat) (x : List Bool) : dot (decode n 0) x = false := by
  have hz : ∀ k j, decodeAt k 0 j = zeros k := by
    intro k
    induction k with
    | zero => intro _; rfl
    | succ k ih =>
      intro j
      exact (congrArg (fun v => v :: decodeAt k 0 (j+1)) (Nat.zero_testBit j)).trans
        (congrArg (List.cons false) (ih (j+1)))
  rw [show decode n 0 = zeros n from hz n 0]
  induction n generalizing x with
  | zero => rfl
  | succ n ih =>
    cases x with
    | nil => rfl
    | cons b bs => cases b <;> exact ih bs

theorem provenance_refutes (n : Nat) (orig : List (Nat × Bool)) (w : Nat)
    (h : MaskProvenance n orig (0,true) w) :
    ¬ ∃ x : List Bool, x.length = n ∧ AllSat (orig.map (maskRow n)) x :=
  dual_sound n (orig.map (maskRow n)) (decode orig.length w) h.right.symm
    (fun x _ => (h.left x).symm.trans (zero_mask_dot n x))

-- Dot with a unit vector: precisely one selected coordinate.
theorem dot_commute (a b : List Bool) : dot a b = dot b a := by
  induction a generalizing b with
  | nil => exact (dot_nil b).symm
  | cons u us ih =>
    cases b with
    | nil => rfl
    | cons v vs =>
      cases u <;> cases v <;> exact congrArg (bx _) (ih vs)

theorem unit_dot_window (n a p k j : Nat) (h : j ≤ p) (hi : p-j < n) :
    dot (decodeAt n a k) (decodeAt n (2^p) j) = a.testBit (k+(p-j)) := by
  induction n generalizing k j with
  | zero => omega
  | succ n ih =>
    by_cases he : p = j
    · subst j
      have hz : ∀ m offset l, p < offset → dot (decodeAt m a l) (decodeAt m (2^p) offset) = false := by
        intro m
        induction m with
        | zero => intro _ _ _; rfl
        | succ m hm =>
          intro offset l ho
          change bx (a.testBit l && (2^p : Nat).testBit offset)
            (dot (decodeAt m a (l+1)) (decodeAt m (2^p) (offset+1))) = false
          rw [Nat.testBit_two_pow_of_ne (by omega : p ≠ offset),hm (offset+1) (l+1) (by omega)]
          cases a.testBit l <;> rfl
      have tail := hz n (p+1) (k+1) (by omega)
      change bx (a.testBit k && (2^p : Nat).testBit p)
        (dot (decodeAt n a (k+1)) (decodeAt n (2^p) (p+1))) = a.testBit (k+(p-p))
      rw [Nat.testBit_two_pow_self,tail,Nat.sub_self,Nat.add_zero]
      cases a.testBit k <;> rfl
    · have e : (2^p : Nat).testBit j = false := Nat.testBit_two_pow_of_ne he
      have tail := ih (k+1) (j+1) (by omega) (by omega)
      change bx (a.testBit k && (2^p : Nat).testBit j)
        (dot (decodeAt n a (k+1)) (decodeAt n (2^p) (j+1))) = _
      rw [e,tail]
      have eqk : k+1+(p-(j+1)) = k+(p-j) := by omega
      rw [eqk]
      cases a.testBit k <;> rfl

theorem unit_dot (n a p : Nat) (h : p < n) :
    dot (decode n a) (decode n (2^p)) = a.testBit p := by
  simpa [decode,Nat.zero_add] using unit_dot_window n a p 0 0 (Nat.zero_le p) (by simpa using h)

theorem flip_coordinate (n a x p : Nat) (h : p < n) :
    dot (decode n a) (decode n (x ^^^ 2^p)) =
      bx (dot (decode n a) (decode n x)) (a.testBit p) := by
  rw [show decode n (x ^^^ 2^p) = addVec (decode n x) (decode n (2^p)) from decode_xor n x (2^p) 0]
  exact (dot_commute _ _).trans ((dot_add _ _ _).trans
    ((congrArg (fun v => bx v (dot (decode n (2^p)) (decode n a))) (dot_commute _ _)).trans
      (congrArg (bx (dot (decode n a) (decode n x))) ((dot_commute _ _).trans (unit_dot n a p h)))))

def backStep (n : Nat) (r : Nat × Bool) (x p : Nat) : Nat :=
  if eqBit (dot (decode n r.1) (decode n x)) r.2 then x else x ^^^ 2^p

theorem backstep_pivot (n : Nat) (r : Nat × Bool) (x p : Nat)
    (hp : Highest r.1 p) (hn : p < n) :
    Sat (maskRow n r) (decode n (backStep n r x p)) := by
  unfold backStep
  cases e : eqBit (dot (decode n r.1) (decode n x)) r.2 with
  | true =>
    simp only [e, if_true]
    exact (eqBit_iff _ _).mp e
  | false =>
    simp only [e, Bool.false_eq_true, if_false]
    change dot (decode n r.1) (decode n (x ^^^ 2^p)) = r.2
    rw [flip_coordinate n r.1 x p hn,highest_bit r.1 p hp]
    cases h : dot (decode n r.1) (decode n x) <;> cases hb : r.2 <;>
      simp_all [eqBit,bx]

theorem backstep_preserves_lower (n : Nat) (r q : Nat × Bool) (x p : Nat)
    (hq : q.1 < 2^p) (hn : p < n) :
    Sat (maskRow n q) (decode n (backStep n r x p)) ↔ Sat (maskRow n q) (decode n x) := by
  unfold backStep
  cases e : eqBit (dot (decode n r.1) (decode n x)) r.2 with
  | true => simp [e]
  | false =>
    simp only [e,Bool.false_eq_true,if_false]
    change (dot (decode n q.1) (decode n (x ^^^ 2^p)) = q.2) ↔ _
    rw [flip_coordinate n q.1 x p hn,Nat.testBit_lt_two_pow hq,bx_zero]
    exact Iff.rfl

-- For a fresh coordinate the Python OR and the mathematical XOR coincide.
theorem fresh_or_xor (x p : Nat) (h : x < 2^p) :
    x ||| 2^p = x ^^^ 2^p := by
  apply Nat.eq_of_testBit_eq
  intro i
  rw [Nat.testBit_or,Nat.testBit_xor]
  by_cases e : p = i
  · subst i
    rw [Nat.testBit_lt_two_pow h,Nat.testBit_two_pow_self]
    rfl
  · rw [Nat.testBit_two_pow_of_ne e]
    cases x.testBit i <;> rfl

end ProctorGF2
#print axioms ProctorGF2.highest_bit
#print axioms ProctorGF2.highest_descent
#print axioms ProctorGF2.pivot_strict_decrease
#print axioms ProctorGF2.next_pivot_lower
#print axioms ProctorGF2.mask_replace
#print axioms ProctorGF2.provenance_xor
#print axioms ProctorGF2.provenance_refutes
#print axioms ProctorGF2.unit_dot
#print axioms ProctorGF2.flip_coordinate
#print axioms ProctorGF2.backstep_pivot
#print axioms ProctorGF2.backstep_preserves_lower
#print axioms ProctorGF2.fresh_or_xor
