/-! F007: least-significant-first codec, counting parity, mask certificates. -/
namespace ProctorGF2

def encodeBits : List Bool → Nat
  | [] => 0
  | b::bs => 2 * encodeBits bs + b.toNat

theorem encode_head (b : Bool) (bs : List Bool) :
    (encodeBits (b::bs)).testBit 0 = b := by
  have h : b.toNat < 2^1 := by cases b <;> decide
  have e := Nat.testBit_mul_pow_two_add (encodeBits bs) h 0
  cases b <;> exact e

theorem encode_tail (b : Bool) (bs : List Bool) (k : Nat) :
    (encodeBits (b::bs)).testBit (k+1) = (encodeBits bs).testBit k := by
  have h : b.toNat < 2^1 := by cases b <;> decide
  have e := Nat.testBit_mul_pow_two_add (encodeBits bs) h (k+1)
  simpa [encodeBits] using e

theorem decode_tail (n : Nat) (b : Bool) (bs : List Bool) (k : Nat) :
    decodeAt n (encodeBits (b::bs)) (k+1) = decodeAt n (encodeBits bs) k := by
  induction n generalizing k with
  | zero => rfl
  | succ n ih =>
    exact (congrArg (fun v : Bool => v :: decodeAt n (encodeBits (b::bs)) (k+1+1))
      (encode_tail b bs k)).trans
      (congrArg (List.cons ((encodeBits bs).testBit k)) (ih (k+1)))

theorem decode_encode (bs : List Bool) : decode bs.length (encodeBits bs) = bs := by
  induction bs with
  | nil => rfl
  | cons b bs ih =>
    exact (congrArg (fun v : Bool => v :: decodeAt bs.length (encodeBits (b::bs)) 1)
      (encode_head b bs)).trans
      (congrArg (List.cons b) ((decode_tail bs.length b bs 0).trans ih))

theorem encode_decode_bit (n a k i : Nat) :
    (encodeBits (decodeAt n a k)).testBit i =
      (decide (i < n) && a.testBit (k+i)) := by
  induction n generalizing k i with
  | zero => simp [decodeAt,encodeBits]
  | succ n ih =>
    cases i with
    | zero => simpa [decodeAt] using encode_head (a.testBit k) (decodeAt n a (k+1))
    | succ i =>
      have e := encode_tail (a.testBit k) (decodeAt n a (k+1)) i
      have f := e.trans (ih (k+1) i)
      simpa [decodeAt, Nat.add_assoc, Nat.add_comm 1 i] using f

theorem encode_decode_mod (n a : Nat) :
    encodeBits (decode n a) = a % 2^n := by
  apply Nat.eq_of_testBit_eq
  intro i
  exact (encode_decode_bit n a 0 i).trans
    ((congrArg (fun j => decide (i < n) && a.testBit j) (Nat.zero_add i)).trans (Nat.testBit_mod_two_pow a n i).symm)

theorem encode_decode_exact (n a : Nat) (h : a < 2^n) :
    encodeBits (decode n a) = a :=
  (encode_decode_mod n a).trans (Nat.mod_eq_of_lt h)

theorem encode_bound (bs : List Bool) : encodeBits bs < 2^bs.length := by
  induction bs with
  | nil => decide
  | cons b bs ih =>
    cases b with
    | false =>
      change 2 * encodeBits bs + 0 < 2^(bs.length+1)
      rw [Nat.pow_succ]
      omega
    | true =>
      change 2 * encodeBits bs + 1 < 2^(bs.length+1)
      rw [Nat.pow_succ]
      omega

-- Count the set bits in exactly the declared window, then take oddness.
def countAt : Nat → Nat → Nat → Nat
  | 0, _, _ => 0
  | n+1, a, k => (a.testBit k).toNat + countAt n a (k+1)

def odd (n : Nat) : Bool := decide (n % 2 = 1)

theorem odd_add_bit (b : Bool) (c : Nat) :
    odd (b.toNat+c) = bx b (odd c) := by
  cases b with
  | false => simp [odd,bx,Bool.toNat]
  | true =>
    change decide ((1+c)%2=1) = !decide (c%2=1)
    by_cases h : c%2=1
    · have e : ¬ (1+c)%2=1 := by omega
      simp [h,e]
    · have e : (1+c)%2=1 := by omega
      simp [h,e]

theorem count_parity (n a k : Nat) :
    odd (countAt n a k) = parityAt n a k := by
  induction n generalizing k with
  | zero => rfl
  | succ n ih =>
    exact (odd_add_bit (a.testBit k) (countAt n a (k+1))).trans
      (congrArg (bx (a.testBit k)) (ih (k+1)))

theorem dot_count (n a b : Nat) :
    dot (decode n a) (decode n b) = odd (countAt n (a &&& b) 0) :=
  (decode_dot n a b 0).trans (count_parity n (a &&& b) 0).symm

-- Independent recursive popcount on the decoded vector.
def countOnes : List Bool → Nat
  | [] => 0
  | b::bs => b.toNat + countOnes bs

theorem count_decode (n a k : Nat) :
    countOnes (decodeAt n a k) = countAt n a k := by
  induction n generalizing k with
  | zero => rfl
  | succ n ih =>
    exact congrArg (fun z : Nat => (a.testBit k).toNat + z) (ih (k+1))

theorem count_extend (n a k : Nat) (h : a.testBit (k+n) = false) :
    countAt (n+1) a k = countAt n a k := by
  induction n generalizing k with
  | zero => exact congrArg Bool.toNat h
  | succ n ih =>
    exact congrArg (fun z : Nat => (a.testBit k).toNat + z)
      (ih (k+1) (by simpa [Nat.add_assoc,Nat.add_comm 1 n] using h))

theorem count_stable (n a extra : Nat) (h : a < 2^n) :
    countAt (n+extra) a 0 = countAt n a 0 := by
  induction extra with
  | zero => rfl
  | succ e ih =>
    have hle : n ≤ 0+(n+e) := by omega
    have hb : a.testBit (0+(n+e)) = false :=
      Nat.testBit_lt_two_pow (Nat.lt_of_lt_of_le h
        (Nat.pow_le_pow_of_le_right Nat.zero_lt_two hle))
    exact (count_extend (n+e) a 0 hb).trans ih

-- Transport original-row XOR selection to the exact projected affine system.
def xorMasks : List (Nat × Bool) → List Bool → Nat × Bool
  | [], _ => (0,false)
  | _::_, [] => (0,false)
  | _::rs,false::ws => xorMasks rs ws
  | r::rs,true::ws =>
    let s := xorMasks rs ws
    (r.1 ^^^ s.1,bx r.2 s.2)

theorem mask_lhs (n : Nat) (rs : List (Nat × Bool)) (w : List Bool) (x : List Bool) :
    dot (decode n (xorMasks rs w).1) x = lhs (rs.map (maskRow n)) w x := by
  have hz : ∀ k j, decodeAt k 0 j = zeros k := by
    intro k
    induction k with
    | zero => intro _; rfl
    | succ k ih =>
      intro j
      exact (congrArg (fun v : Bool => v :: decodeAt k 0 (j+1)) (Nat.zero_testBit j)).trans
        (congrArg (List.cons false) (ih (j+1)))
  have dz : ∀ k : Nat, ∀ ys : List Bool, dot (zeros k) ys = false := by
    intro k
    induction k with
    | zero => intro _; rfl
    | succ k ih =>
      intro ys
      cases ys with
      | nil => rfl
      | cons b bs => cases b <;> exact ih bs
  induction rs generalizing w with
  | nil => exact ((congrArg (fun a => dot a x) (hz n 0)).trans (dz n x)).trans (dot_nil w).symm
  | cons r rs ih =>
    cases w with
    | nil => exact (congrArg (fun a => dot a x) (hz n 0)).trans (dz n x)
    | cons b ws =>
      cases b with
      | false => exact ih ws
      | true =>
        exact (congrArg (fun a => dot a x) (decode_xor n r.1 (xorMasks rs ws).1 0)).trans
          ((dot_add (decode n r.1) (decode n (xorMasks rs ws).1) x).trans
            (congrArg (bx (dot (decode n r.1) x)) (ih ws)))

theorem mask_rhs (n : Nat) (rs : List (Nat × Bool)) (w : List Bool) :
    (xorMasks rs w).2 = rhs (rs.map (maskRow n)) w := by
  induction rs generalizing w with
  | nil => exact (dot_nil w).symm
  | cons r rs ih =>
    cases w with
    | nil => rfl
    | cons b ws =>
      cases b with
      | false => exact ih ws
      | true => exact congrArg (bx r.2) (ih ws)

theorem mask_certificate_sound (n : Nat) (rs : List (Nat × Bool)) (w : List Bool)
    (ha : (xorMasks rs w).1 % 2^n = 0)
    (hb : (xorMasks rs w).2 = true) :
    ¬ ∃ x : List Bool, x.length = n ∧ AllSat (rs.map (maskRow n)) x := by
  apply dual_sound n (rs.map (maskRow n)) w ((mask_rhs n rs w).symm.trans hb)
  intro x _
  have e : encodeBits (decode n (xorMasks rs w).1) = 0 :=
    (encode_decode_mod n (xorMasks rs w).1).trans ha
  have hlen : (decode n (xorMasks rs w).1).length = n := decode_length n (xorMasks rs w).1 0
  have hzero : decode n (xorMasks rs w).1 = decode n 0 := by
    have q := decode_encode (decode n (xorMasks rs w).1)
    rw [hlen,e] at q
    exact q.symm
  have hz : ∀ k j, decodeAt k 0 j = zeros k := by
    intro k
    induction k with
    | zero => intro _; rfl
    | succ k ih =>
      intro j
      exact (congrArg (fun v : Bool => v :: decodeAt k 0 (j+1)) (Nat.zero_testBit j)).trans
        (congrArg (List.cons false) (ih (j+1)))
  have dz : ∀ a : Nat, ∀ ys : List Bool, dot (zeros a) ys = false := by
    intro a
    induction a with
    | zero => intro _; rfl
    | succ a ih =>
      intro ys
      cases ys with
      | nil => rfl
      | cons b bs => cases b <;> exact ih bs
  exact (mask_lhs n rs w x).symm.trans
    ((congrArg (fun a => dot a x) (hzero.trans (hz n 0))).trans (dz n x))

end ProctorGF2
#print axioms ProctorGF2.decode_encode
#print axioms ProctorGF2.encode_decode_mod
#print axioms ProctorGF2.encode_decode_exact
#print axioms ProctorGF2.encode_bound
#print axioms ProctorGF2.count_parity
#print axioms ProctorGF2.dot_count
#print axioms ProctorGF2.count_decode
#print axioms ProctorGF2.count_stable
#print axioms ProctorGF2.mask_lhs
#print axioms ProctorGF2.mask_rhs
#print axioms ProctorGF2.mask_certificate_sound
