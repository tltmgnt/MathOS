/-! F034 candidate: bounded byte-length prepass with checked
binary remaining capacity. The executable guard is tail recursive.
A separate selected visit ledger counts inspected decrement bits,
including the first rejecting decrement. No whole-machine cost. -/
namespace ProctorBytePrepass
open ProctorDecimalBitWidth (bitsValue)
open ProctorCheckedDecrement (decMeter dec_sound dec_reject_iff dec_visit_bound)
open ProctorCheckedBinaryScanner (zeroWord)
open ProctorScannerCounters (scanCounted countZero tokenizeCounted)
open ProctorDataParser (byteLimit)

-- Static 20-bit little-endian representation of 1000000.
def byteWord : List Bool :=
  [false,false,false,false,false,false,true,false,false,true,
   false,false,false,false,true,false,true,true,true,true]

theorem byte_word_value : bitsValue byteWord=byteLimit := by decide
theorem byte_word_width : byteWord.length=20 := rfl

def lengthOK {α : Type} : List α → List Bool → Bool
  | [],_ => true
  | _::xs,c =>
    match (decMeter c).1 with
    | none => false
    | some d => lengthOK xs d

theorem length_iff {α : Type} (xs : List α) (c : List Bool) :
    lengthOK xs c=true ↔ xs.length≤bitsValue c := by
  induction xs generalizing c with
  | nil =>
    constructor
    · intro _
      exact Nat.zero_le _
    · intro _
      rfl
  | cons _a xs ih =>
    rw [lengthOK]
    cases e : (decMeter c).1 with
    | none =>
      rw [e]
      have hz := (dec_reject_iff c).mp e
      rw [hz]
      constructor
      · intro h
        cases h
      · intro h
        cases h
    | some d =>
      rw [e]
      have hd := (dec_sound c d e).right
      constructor
      · intro h
        have hl := (ih d).mp h
        rw [← hd]
        exact Nat.succ_le_succ hl
      · intro h
        rw [← hd] at h
        exact (ih d).mpr (Nat.le_of_succ_le_succ h)

theorem length_reject_iff {α : Type} (xs : List α) (c : List Bool) :
    lengthOK xs c=false ↔ bitsValue c<xs.length := by
  constructor
  · intro h
    apply Nat.lt_of_not_ge
    intro le
    have e := (length_iff xs c).mpr le
    rw [h] at e
    cases e
  · intro h
    cases e : lengthOK xs c with
    | false => rfl
    | true => exact False.elim (Nat.not_lt_of_ge ((length_iff xs c).mp e) h)

-- A specification of the visits made by the executable guard.
-- Not executed on the large controls; not a runtime accumulator.
def visits {α : Type} : List α → List Bool → Nat
  | [],_ => 0
  | _::xs,c =>
    let r := decMeter c
    r.2+(match r.1 with
      | none => 0
      | some d => visits xs d)

theorem visits_length_bound {α : Type} (xs : List α) (c : List Bool) :
    visits xs c≤c.length*xs.length := by
  induction xs generalizing c with
  | nil => exact Nat.le_refl 0
  | cons _a xs ih =>
    rw [visits]
    cases e : (decMeter c).1 with
    | none =>
      change (decMeter c).2+(match (decMeter c).1 with
        | none => 0
        | some d => visits xs d)≤c.length*(xs.length+1)
      rw [e]
      exact Nat.le_trans (dec_visit_bound c) (Nat.le_add_left _ _)
    | some d =>
      change (decMeter c).2+(match (decMeter c).1 with
        | none => 0
        | some z => visits xs z)≤c.length*(xs.length+1)
      rw [e]
      have h := ih d
      rw [(dec_sound c d e).left] at h
      calc
        (decMeter c).2+visits xs d ≤ c.length+c.length*xs.length :=
          Nat.add_le_add (dec_visit_bound c) h
        _ = c.length*(xs.length+1) := Nat.add_comm _ _

-- Oversize input stops at the first exhausted decrement. This
-- independent bound also applies when the original list is huge.
theorem visits_capacity_bound {α : Type} (xs : List α) (c : List Bool) :
    visits xs c≤c.length*(bitsValue c+1) := by
  induction xs generalizing c with
  | nil => exact Nat.zero_le _
  | cons _a xs ih =>
    rw [visits]
    cases e : (decMeter c).1 with
    | none =>
      change (decMeter c).2+(match (decMeter c).1 with
        | none => 0
        | some d => visits xs d)≤c.length*(bitsValue c+1)
      rw [e]
      exact Nat.le_trans (dec_visit_bound c) (Nat.le_add_left _ _)
    | some d =>
      change (decMeter c).2+(match (decMeter c).1 with
        | none => 0
        | some z => visits xs z)≤c.length*(bitsValue c+1)
      rw [e]
      have hs := dec_sound c d e
      have h := ih d
      rw [hs.left,hs.right] at h
      calc
        (decMeter c).2+visits xs d ≤ c.length+c.length*bitsValue c :=
          Nat.add_le_add (dec_visit_bound c) h
        _ = c.length*(bitsValue c+1) := Nat.add_comm _ _

def byteOK (bytes : List Nat) : Bool := lengthOK bytes byteWord

theorem byte_ok_iff (bytes : List Nat) :
    byteOK bytes=true ↔ bytes.length≤byteLimit := by
  unfold byteOK
  rw [← byte_word_value]
  exact length_iff bytes byteWord

theorem byte_visit_length_bound (bytes : List Nat) :
    visits bytes byteWord≤20*bytes.length := by
  have h := visits_length_bound bytes byteWord
  rw [byte_word_width] at h
  exact h

theorem byte_visit_capacity_bound (bytes : List Nat) :
    visits bytes byteWord≤20*(byteLimit+1) := by
  have h := visits_capacity_bound bytes byteWord
  rw [byte_word_width,byte_word_value] at h
  exact h

-- Compose with the independently verified binary digit scanner.
def tokenizeBounded (bytes : List Nat) : Option (List Nat) :=
  if byteOK bytes then scanCounted bytes zeroWord countZero [] else none

theorem counted_refines (bytes : List Nat) :
    tokenizeBounded bytes=tokenizeCounted bytes := by
  unfold tokenizeBounded tokenizeCounted
  by_cases h : bytes.length≤byteLimit
  · rw [if_pos ((byte_ok_iff bytes).mpr h),if_pos h]
  · have hb : ¬ byteOK bytes=true := fun e => h ((byte_ok_iff bytes).mp e)
    rw [if_neg hb,if_neg h]

theorem tokenize_refines (bytes : List Nat) :
    tokenizeBounded bytes=ProctorDataParser.tokenize bytes :=
  (counted_refines bytes).trans (ProctorScannerCounters.tokenize_refines bytes)

end ProctorBytePrepass

#print axioms ProctorBytePrepass.byte_word_value
#print axioms ProctorBytePrepass.byte_word_width
#print axioms ProctorBytePrepass.length_iff
#print axioms ProctorBytePrepass.length_reject_iff
#print axioms ProctorBytePrepass.visits_length_bound
#print axioms ProctorBytePrepass.visits_capacity_bound
#print axioms ProctorBytePrepass.byte_ok_iff
#print axioms ProctorBytePrepass.byte_visit_length_bound
#print axioms ProctorBytePrepass.byte_visit_capacity_bound
#print axioms ProctorBytePrepass.counted_refines
#print axioms ProctorBytePrepass.tokenize_refines
