/-! F034: decimal operand-width invariant and a binary addition primitive.
The five-gate-per-column model is an explicit Boolean circuit ledger,
not a compiler or whole-checker bit-cost refinement. -/
namespace ProctorDecimalBitWidth
open ProctorDataParser (digitLimit tokenize)
open ProctorWireRoundtrip (Word Wire)
open ProctorTerminalPolynomial (mul_mono)
open ProctorHallDeficiency (Literal)

def radix : Nat → Nat
  | 0 => 1
  | k+1 => 16*radix k

private theorem one_mul_local (k : Nat) : 1*k=k := by
  induction k with
  | zero => rfl
  | succ k ih => exact congrArg Nat.succ ih

private theorem radix_step (k : Nat) : radix k≤radix (k+1) := by
  change radix k≤16*radix k
  have h := mul_mono (by decide : 1≤16) (Nat.le_refl (radix k))
  rw [one_mul_local] at h
  exact h

theorem radix_mono (a b : Nat) (h : a≤b) : radix a≤radix b := by
  induction h with
  | refl => exact Nat.le_refl _
  | step _ ih => exact Nat.le_trans ih (radix_step _)

-- A valid next digit preserves v < 16^k, represented constructively
-- as v+1 <= radix k. This is a local transition theorem, regardless
-- of whether subsequent bytes are valid or rejected.
theorem digit_step (v k b : Nat) (hv : v+1≤radix k) (hi : b≤57) :
    (10*v+(b-48))+1≤radix (k+1) := by
  have hd : b-48≤9 := Nat.sub_le_sub_right hi 48
  calc
    (10*v+(b-48))+1 = 10*v+((b-48)+1) := Nat.add_assoc _ _ _
    _ ≤ 10*v+10 := Nat.add_le_add (Nat.le_refl _) (Nat.succ_le_succ hd)
    _ = 10*(v+1) := rfl
    _ ≤ 16*radix k := mul_mono (by decide : 10≤16) hv
    _ = radix (k+1) := rfl

def ceiling : Nat := radix digitLimit

theorem word_bound (v k : Nat) (ds : List Nat) (out : Nat)
    (h : Word v k ds out) (hv : v+1≤radix k) (hk : k≤digitLimit) :
    out+1≤ceiling := by
  revert hv hk
  induction h with
  | done v k _ =>
    intro hv hk
    exact Nat.le_trans hv (radix_mono k digitLimit hk)
  | @digit v k b out bs lo hi size nonzero sub ih =>
    intro hv _
    exact ih (digit_step v k b hv hi) size

theorem wire_bound (bytes ts : List Nat) (h : Wire bytes ts) :
    ∀ v ∈ ts, v+1≤ceiling := by
  induction h with
  | nil =>
    intro v hm
    cases hm
  | @cons ds bs v vs word tail ih =>
    intro x hm
    cases hm with
    | head => exact word_bound 0 0 ds v word (Nat.le_refl 1) (Nat.zero_le _)
    | tail _ hmem => exact ih x hmem

theorem token_width (bytes ts : List Nat) (h : tokenize bytes=some ts) :
    ∀ v ∈ ts, v+1≤ceiling :=
  wire_bound bytes ts (ProctorEnvelopeRoundtrip.tokenize_converse bytes ts h).right

-- Symbolic induction avoids reducing a 512-bit closed power in
-- a single elaborator decision. No recursion-limit change.
private theorem radix_pow (k : Nat) : radix k=2^(4*k) := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change 16*radix k=2^(4*k+4)
    calc
      16*radix k = 16*2^(4*k) := congrArg (fun v => 16*v) ih
      _ = 2^(4*k)*2^4 := Nat.mul_comm _ _
      _ = 2^(4*k+4) := (Nat.pow_add 2 (4*k) 4).symm

theorem ceiling_bits : ceiling=2^512 :=
  radix_pow digitLimit

theorem natural_width (w : List Nat) (v : Nat)
    (h : ProctorDimacsInput.naturalWord w=some v) : v+1≤ceiling := by
  unfold ProctorDimacsInput.naturalWord at h
  cases e : tokenize (w++[10]) with
  | none => rw [e] at h; cases h
  | some ts =>
    rw [e] at h
    cases ts with
    | nil => cases h
    | cons x xs =>
      cases xs with
      | nil =>
        have hv := token_width (w++[10]) [x] e x (List.Mem.head _)
        cases h
        exact hv
      | cons _ _ => cases h

theorem signed_width (w : List Nat) (l : Literal)
    (h : ProctorDimacsInput.signedWord w=some l) : l.1+1≤ceiling := by
  cases w with
  | nil => cases h
  | cons b ds =>
    change (if b=45 then
      (do let v ← ProctorDimacsInput.naturalWord ds
          if v=0 then none else some (v,false))
      else (do let v ← ProctorDimacsInput.naturalWord (b::ds)
               some (v,true)))=some l at h
    by_cases sign : b=45
    · rw [if_pos sign] at h
      cases e : ProctorDimacsInput.naturalWord ds with
      | none => rw [e] at h; cases h
      | some v =>
        rw [e] at h
        change (if v=0 then none else some (v,false))=some l at h
        by_cases z : v=0
        · rw [if_pos z] at h; cases h
        · rw [if_neg z] at h
          have hv := natural_width ds v e
          cases h
          exact hv
    · rw [if_neg sign] at h
      cases e : ProctorDimacsInput.naturalWord (b::ds) with
      | none => rw [e] at h; cases h
      | some v =>
        rw [e] at h
        have hv := natural_width (b::ds) v e
        cases h
        exact hv

-- Explicit Boolean full-adder circuit: two XOR, two AND, one OR.
def bitVal : Bool → Nat
  | false => 0
  | true => 1

def fullAdder (a b carry : Bool) : Bool × Bool :=
  let p := ProctorXorReplay.bx a b
  (ProctorXorReplay.bx p carry,(a && b) || (p && carry))

theorem full_adder_value (a b c : Bool) :
    bitVal (fullAdder a b c).1+2*bitVal (fullAdder a b c).2=
      bitVal a+bitVal b+bitVal c := by
  cases a <;> cases b <;> cases c <;> rfl

-- Little-endian columns. Each column contains the two input bits.
-- Return one extra final carry bit, so overflow is never discarded.
def bitsValue : List Bool → Nat
  | [] => 0
  | a::as => bitVal a+2*bitsValue as

def columnValue : List (Bool × Bool) → Nat
  | [] => 0
  | (a,b)::xs => (bitVal a+bitVal b)+2*columnValue xs

def rippleMeter : List (Bool × Bool) → Bool → List Bool × Nat
  | [],c => ([c],0)
  | (a,b)::xs,c =>
    let q := fullAdder a b c
    let r := rippleMeter xs q.2
    (q.1::r.1,r.2+5)

private theorem mul_add_local (n a b : Nat) : n*(a+b)=n*a+n*b := by
  induction b with
  | zero => rfl
  | succ b ih =>
    change n*(a+b)+n=n*a+(n*b+n)
    rw [ih]
    exact Nat.add_assoc _ _ _

theorem ripple_value (cols : List (Bool × Bool)) (c : Bool) :
    bitsValue (rippleMeter cols c).1=columnValue cols+bitVal c := by
  induction cols generalizing c with
  | nil =>
    change bitVal c+0=0+bitVal c
    exact (Nat.zero_add _).symm
  | cons ab xs ih =>
    cases ab with
    | mk a b =>
      let q := fullAdder a b c
      change bitVal q.1+2*bitsValue (rippleMeter xs q.2).1=
        (bitVal a+bitVal b)+2*columnValue xs+bitVal c
      rw [ih q.2,mul_add_local]
      calc
        bitVal q.1+(2*columnValue xs+2*bitVal q.2) =
          bitVal q.1+(2*bitVal q.2+2*columnValue xs) :=
            congrArg (fun v => bitVal q.1+v) (Nat.add_comm _ _)
        _ = (bitVal q.1+2*bitVal q.2)+2*columnValue xs := (Nat.add_assoc _ _ _).symm
        _ = (bitVal a+bitVal b+bitVal c)+2*columnValue xs :=
          congrArg (fun v => v+2*columnValue xs) (full_adder_value a b c)
        _ = (bitVal a+bitVal b)+(bitVal c+2*columnValue xs) := Nat.add_assoc _ _ _
        _ = (bitVal a+bitVal b)+(2*columnValue xs+bitVal c) :=
          congrArg (fun v => (bitVal a+bitVal b)+v) (Nat.add_comm _ _)
        _ = (bitVal a+bitVal b)+2*columnValue xs+bitVal c := (Nat.add_assoc _ _ _).symm

theorem ripple_length (cols : List (Bool × Bool)) (c : Bool) :
    (rippleMeter cols c).1.length=cols.length+1 := by
  induction cols generalizing c with
  | nil => rfl
  | cons ab xs ih =>
    cases ab with
    | mk a b =>
      change (rippleMeter xs (fullAdder a b c).2).1.length+1=(xs.length+1)+1
      exact congrArg Nat.succ (ih _)

theorem ripple_gates (cols : List (Bool × Bool)) (c : Bool) :
    (rippleMeter cols c).2=5*cols.length := by
  induction cols generalizing c with
  | nil => rfl
  | cons ab xs ih =>
    cases ab with
    | mk a b =>
      change (rippleMeter xs (fullAdder a b c).2).2+5=5*xs.length+5
      rw [ih]

theorem ripple_gate_bound (cols : List (Bool × Bool)) (c : Bool)
    (h : cols.length≤512) : (rippleMeter cols c).2≤2560 := by
  rw [ripple_gates]
  exact mul_mono (Nat.le_refl 5) h

end ProctorDecimalBitWidth

#print axioms ProctorDecimalBitWidth.radix_mono
#print axioms ProctorDecimalBitWidth.digit_step
#print axioms ProctorDecimalBitWidth.word_bound
#print axioms ProctorDecimalBitWidth.wire_bound
#print axioms ProctorDecimalBitWidth.token_width
#print axioms ProctorDecimalBitWidth.ceiling_bits
#print axioms ProctorDecimalBitWidth.natural_width
#print axioms ProctorDecimalBitWidth.signed_width
#print axioms ProctorDecimalBitWidth.full_adder_value
#print axioms ProctorDecimalBitWidth.ripple_value
#print axioms ProctorDecimalBitWidth.ripple_length
#print axioms ProctorDecimalBitWidth.ripple_gates
#print axioms ProctorDecimalBitWidth.ripple_gate_bound
