/-! F034 candidate: checked representation conversion and scanner refinement.
Unsigned little-endian words, no discarded nonzero high bits.
The scanner still uses Nat byte/counter operations and projects tokens to Nat.
No allocation, conversion or total machine-cost theorem. -/
namespace ProctorCheckedBinaryScanner
open ProctorDecimalBitWidth (bitVal bitsValue radix radix_mono ceiling ceiling_bits)
open ProctorBinaryPrimitives (decimalMeter decimal_value decimal_width_invariant)
open ProctorTerminalPolynomial (mul_mono)
open ProctorDataParser (digitLimit byteLimit)

def cap : Nat → Nat
  | 0 => 1
  | w+1 => 2*cap w

theorem cap_pow (w : Nat) : cap w=2^w := by
  induction w with
  | zero => rfl
  | succ w ih =>
    change 2*cap w=2^w*2
    rw [ih]
    exact Nat.mul_comm _ _

private theorem one_mul_local (n : Nat) : 1*n=n := by
  induction n with
  | zero => rfl
  | succ n ih => exact congrArg Nat.succ ih

private theorem twice_ge (n : Nat) : n≤2*n := by
  have h := mul_mono (by decide : 1≤2) (Nat.le_refl n)
  rw [one_mul_local] at h
  exact h

private theorem half_bound (t b w : Nat) (h : b+2*t<cap (w+1)) :
    t<cap w := by
  apply Nat.lt_of_not_ge
  intro ge
  have bad : cap (w+1)≤b+2*t := calc
    cap (w+1) = 2*cap w := rfl
    _ ≤ 2*t := mul_mono (Nat.le_refl 2) ge
    _ ≤ b+2*t := Nat.le_add_left _ _
  exact Nat.not_lt_of_ge bad h

theorem value_bound (xs : List Bool) : bitsValue xs<cap xs.length := by
  induction xs with
  | nil => exact Nat.le_refl 1
  | cons a xs ih =>
    change (bitVal a+2*bitsValue xs)+1≤2*cap xs.length
    have hb : bitVal a+1≤2 := by cases a <;> decide
    calc
      (bitVal a+2*bitsValue xs)+1 = (2*bitsValue xs+bitVal a)+1 :=
        congrArg (fun n => n+1) (Nat.add_comm _ _)
      _ = 2*bitsValue xs+(bitVal a+1) := Nat.add_assoc _ _ _
      _ ≤ 2*bitsValue xs+2 := Nat.add_le_add (Nat.le_refl _) hb
      _ = 2*(bitsValue xs+1) := rfl
      _ ≤ 2*cap xs.length := mul_mono (Nat.le_refl 2) ih

def zeroBits : List Bool → Bool
  | [] => true
  | false::xs => zeroBits xs
  | true::_ => false

theorem zero_sound (xs : List Bool) (h : zeroBits xs=true) :
    bitsValue xs=0 := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    cases a with
    | false =>
      change zeroBits xs=true at h
      change 0+2*bitsValue xs=0
      rw [ih h]
      rfl
    | true => cases h

theorem zero_complete (xs : List Bool) (h : bitsValue xs=0) :
    zeroBits xs=true := by
  induction xs with
  | nil => rfl
  | cons a xs ih =>
    cases a with
    | false =>
      change zeroBits xs=true
      apply ih
      have ht : bitsValue xs≤0 := calc
        bitsValue xs ≤ 2*bitsValue xs := twice_ge _
        _ ≤ 0+2*bitsValue xs := Nat.le_add_left _ _
        _ = 0 := h
      exact Nat.eq_zero_of_le_zero ht
    | true =>
      have bad : 1≤0 := calc
        1 ≤ 1+2*bitsValue xs := Nat.le_add_right _ _
        _ = 0 := h
      cases bad

def low : List Bool → Bool
  | [] => false
  | b::_ => b

def high : List Bool → List Bool
  | [] => []
  | _::xs => xs

private theorem split_value (xs : List Bool) :
    bitsValue xs=bitVal (low xs)+2*bitsValue (high xs) := by
  cases xs <;> rfl

-- Pad short inputs; reject any nonzero bits beyond the requested width.
def narrow : Nat → List Bool → Option (List Bool)
  | 0,xs => if zeroBits xs then some [] else none
  | w+1,xs =>
    match narrow w (high xs) with
    | none => none
    | some t => some (low xs::t)

theorem narrow_sound (w : Nat) (xs ys : List Bool)
    (h : narrow w xs=some ys) : ys.length=w ∧ bitsValue ys=bitsValue xs := by
  induction w generalizing xs ys with
  | zero =>
    change (if zeroBits xs then some [] else none)=some ys at h
    cases e : zeroBits xs with
    | false => rw [e] at h; cases h
    | true =>
      rw [e] at h
      cases h
      exact ⟨rfl,(zero_sound xs e).symm⟩
  | succ w ih =>
    change (match narrow w (high xs) with
      | none => none
      | some t => some (low xs::t))=some ys at h
    cases e : narrow w (high xs) with
    | none => rw [e] at h; cases h
    | some t =>
      rw [e] at h
      cases h
      have ht := ih (high xs) t e
      constructor
      · exact congrArg Nat.succ ht.left
      · change bitVal (low xs)+2*bitsValue t=bitsValue xs
        rw [ht.right]
        exact (split_value xs).symm

theorem narrow_complete (w : Nat) (xs : List Bool)
    (h : bitsValue xs<cap w) : ∃ ys, narrow w xs=some ys := by
  induction w generalizing xs with
  | zero =>
    have hz : bitsValue xs=0 :=
      Nat.eq_zero_of_le_zero (Nat.le_of_succ_le_succ h)
    refine ⟨[],?_⟩
    change (if zeroBits xs then some [] else none)=some []
    rw [zero_complete xs hz]
  | succ w ih =>
    have ht : bitsValue (high xs)<cap w := by
      apply half_bound (bitsValue (high xs)) (bitVal (low xs)) w
      rw [← split_value xs]
      exact h
    obtain ⟨t,e⟩ := ih (high xs) ht
    refine ⟨low xs::t,?_⟩
    change (match narrow w (high xs) with
      | none => none
      | some u => some (low xs::u))=some (low xs::t)
    rw [e]

theorem narrow_iff (w : Nat) (xs : List Bool) :
    (∃ ys, narrow w xs=some ys) ↔ bitsValue xs<cap w := by
  constructor
  · intro h
    obtain ⟨ys,e⟩ := h
    have hs := narrow_sound w xs ys e
    have hb := value_bound ys
    rw [hs.left,hs.right] at hb
    exact hb
  · exact narrow_complete w xs

def smallBit : Nat → Bool
  | 0 => false
  | _+1 => true

private theorem small_bit_value (m : Nat) (h : m<2) :
    bitVal (smallBit m)=m := by
  cases m with
  | zero => rfl
  | succ m =>
    cases m with
    | zero => rfl
    | succ m =>
      exact False.elim (Nat.not_lt_of_ge
        (Nat.succ_le_succ (Nat.succ_le_succ (Nat.zero_le m))) h)

-- The Nat boundary conversion itself has no gate-cost claim.
-- At width zero reject a nonzero residual quotient.
def encode : Nat → Nat → Option (List Bool)
  | 0,n => if n=0 then some [] else none
  | w+1,n =>
    match encode w (n/2) with
    | none => none
    | some t => some (smallBit (n%2)::t)

theorem encode_sound (w n : Nat) (ys : List Bool)
    (h : encode w n=some ys) : ys.length=w ∧ bitsValue ys=n := by
  induction w generalizing n ys with
  | zero =>
    change (if n=0 then some [] else none)=some ys at h
    by_cases e : n=0
    · rw [if_pos e] at h
      cases h
      exact ⟨rfl,e.symm⟩
    · rw [if_neg e] at h
      cases h
  | succ w ih =>
    change (match encode w (n/2) with
      | none => none
      | some t => some (smallBit (n%2)::t))=some ys at h
    cases e : encode w (n/2) with
    | none => rw [e] at h; cases h
    | some t =>
      rw [e] at h
      cases h
      have ht := ih (n/2) t e
      constructor
      · exact congrArg Nat.succ ht.left
      · change bitVal (smallBit (n%2))+2*bitsValue t=n
        rw [ht.right,small_bit_value (n%2) (Nat.mod_lt n (by decide : 0<2))]
        exact Nat.mod_add_div n 2

theorem encode_complete (w n : Nat) (h : n<cap w) :
    ∃ ys, encode w n=some ys := by
  induction w generalizing n with
  | zero =>
    have e : n=0 := Nat.eq_zero_of_le_zero (Nat.le_of_succ_le_succ h)
    refine ⟨[],?_⟩
    change (if n=0 then some [] else none)=some []
    rw [if_pos e]
  | succ w ih =>
    have ht : n/2<cap w := by
      apply half_bound (n/2) (n%2) w
      rw [Nat.mod_add_div]
      exact h
    obtain ⟨t,e⟩ := ih (n/2) ht
    refine ⟨smallBit (n%2)::t,?_⟩
    change (match encode w (n/2) with
      | none => none
      | some u => some (smallBit (n%2)::u))=some (smallBit (n%2)::t)
    rw [e]

theorem encode_iff (w n : Nat) :
    (∃ ys, encode w n=some ys) ↔ n<cap w := by
  constructor
  · intro h
    obtain ⟨ys,e⟩ := h
    have hs := encode_sound w n ys e
    have hb := value_bound ys
    rw [hs.left,hs.right] at hb
    exact hb
  · exact encode_complete w n

def checkedDigit (v : List Bool) (b : Nat) : Option (List Bool) :=
  match encode 4 (b-48) with
  | none => none
  | some d => narrow 512 (decimalMeter v d).1

-- Only the scanner's admissible transition is guaranteed to fit.
-- For arbitrary 512-bit inputs, the checked operation can reject.
set_option exponentiation.threshold 512 in
theorem checked_digit_refines (v : List Bool) (k b : Nat)
    (hv : bitsValue v+1≤radix k) (hk : k<digitLimit) (hb : b≤57) :
    ∃ out, checkedDigit v b=some out ∧ out.length=512 ∧
      bitsValue out=10*bitsValue v+(b-48) ∧ bitsValue out+1≤radix (k+1) := by
  have hd : b-48<cap 4 := Nat.lt_of_le_of_lt
    (Nat.sub_le_sub_right hb 48) (by decide)
  obtain ⟨d,e⟩ := encode_complete 4 (b-48) hd
  have hs := encode_sound 4 (b-48) d e
  have hr := decimal_width_invariant v d k b hv hs.right hb
  have hc : ceiling=cap 512 := ceiling_bits.trans (cap_pow 512).symm
  have hf : bitsValue (decimalMeter v d).1<cap 512 := calc
    bitsValue (decimalMeter v d).1 < radix (k+1) := hr
    _ ≤ ceiling := radix_mono (k+1) digitLimit hk
    _ = cap 512 := hc
  obtain ⟨out,eo⟩ := narrow_complete 512 (decimalMeter v d).1 hf
  have ho := narrow_sound 512 (decimalMeter v d).1 out eo
  refine ⟨out,?_,ho.left,?_,?_⟩
  · unfold checkedDigit
    rw [e,eo]
  · rw [ho.right,decimal_value,hs.right]
  · rw [ho.right]
    exact hr

def zeroWord : List Bool := List.replicate 512 false

private theorem zeros_value (w : Nat) :
    bitsValue (List.replicate w false)=0 := by
  induction w with
  | zero => rfl
  | succ w ih =>
    change 0+2*bitsValue (List.replicate w false)=0
    rw [ih]
    rfl

theorem zero_word_value : bitsValue zeroWord=0 := zeros_value 512

-- Byte and digit-count checks remain Nat operations, and emitted
-- tokens are decoded to Nat. The accumulator arithmetic is checked.
def scanBits : List Nat → List Bool → Nat → List Nat → Option (List Nat)
  | [],_,digits,acc => if digits=0 then some acc.reverse else none
  | b::bs,v,digits,acc =>
    if b=10 then
      if digits=0 then none else scanBits bs zeroWord 0 (bitsValue v::acc)
    else if 48≤b ∧ b≤57 then
      if digits≥digitLimit ∨ (digits>0 ∧ zeroBits v=true) then none
      else match checkedDigit v b with
        | none => none
        | some out => scanBits bs out (digits+1) acc
    else none

theorem scan_refines (bytes : List Nat) (v : List Bool) (k : Nat)
    (acc : List Nat) (hv : bitsValue v+1≤radix k) :
    scanBits bytes v k acc=ProctorDataParser.scan bytes (bitsValue v) k acc := by
  induction bytes generalizing v k acc with
  | nil => rfl
  | cons b bs ih =>
    unfold scanBits ProctorDataParser.scan
    by_cases lf : b=10
    · rw [if_pos lf] <;> try rw [if_pos lf]
      by_cases z : k=0
      · rw [if_pos z] <;> try rw [if_pos z]
      · rw [if_neg z] <;> try rw [if_neg z]
        have hz : bitsValue zeroWord+1≤radix 0 := by
          rw [zero_word_value]
          exact Nat.le_refl 1
        have e := ih zeroWord 0 (bitsValue v::acc) hz
        rw [zero_word_value] at e
        exact e
    · rw [if_neg lf] <;> try rw [if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit] <;> try rw [if_pos digit]
        by_cases g : k≥digitLimit ∨ (k>0 ∧ bitsValue v=0)
        · have gb : k≥digitLimit ∨ (k>0 ∧ zeroBits v=true) :=
            g.elim Or.inl (fun h => Or.inr ⟨h.left,zero_complete v h.right⟩)
          rw [if_pos gb,if_pos g]
        · have gb : ¬ (k≥digitLimit ∨ (k>0 ∧ zeroBits v=true)) :=
            fun h => g (h.elim Or.inl (fun z => Or.inr ⟨z.left,zero_sound v z.right⟩))
          rw [if_neg gb,if_neg g]
          have hk : k<digitLimit := Nat.lt_of_not_ge (fun h => g (Or.inl h))
          obtain ⟨out,eo,_,ev,hi⟩ := checked_digit_refines v k b hv hk digit.right
          rw [eo]
          have e := ih out (k+1) acc hi
          rw [ev] at e
          exact e
      · rw [if_neg digit] <;> try rw [if_neg digit]

def tokenizeBits (bytes : List Nat) : Option (List Nat) :=
  if bytes.length≤byteLimit then scanBits bytes zeroWord 0 [] else none

theorem tokenize_refines (bytes : List Nat) :
    tokenizeBits bytes=ProctorDataParser.tokenize bytes := by
  unfold tokenizeBits ProctorDataParser.tokenize
  by_cases h : bytes.length≤byteLimit
  · rw [if_pos h] <;> try rw [if_pos h]
    have hz : bitsValue zeroWord+1≤radix 0 := by
      rw [zero_word_value]
      exact Nat.le_refl 1
    have e := scan_refines bytes zeroWord 0 [] hz
    rw [zero_word_value] at e
    exact e
  · rw [if_neg h] <;> try rw [if_neg h]

end ProctorCheckedBinaryScanner

#print axioms ProctorCheckedBinaryScanner.cap_pow
#print axioms ProctorCheckedBinaryScanner.value_bound
#print axioms ProctorCheckedBinaryScanner.zero_sound
#print axioms ProctorCheckedBinaryScanner.zero_complete
#print axioms ProctorCheckedBinaryScanner.narrow_sound
#print axioms ProctorCheckedBinaryScanner.narrow_complete
#print axioms ProctorCheckedBinaryScanner.narrow_iff
#print axioms ProctorCheckedBinaryScanner.encode_sound
#print axioms ProctorCheckedBinaryScanner.encode_complete
#print axioms ProctorCheckedBinaryScanner.encode_iff
#print axioms ProctorCheckedBinaryScanner.checked_digit_refines
#print axioms ProctorCheckedBinaryScanner.zero_word_value
#print axioms ProctorCheckedBinaryScanner.scan_refines
#print axioms ProctorCheckedBinaryScanner.tokenize_refines
