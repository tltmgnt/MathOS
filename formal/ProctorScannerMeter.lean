/-! F034: executable selected charges for the decimal scanner.
One charge per visited byte or EOF test, one per length-pass cell,
one for the limit guard, and one per reversed token on success.
Not a bit-machine or actual runtime trace. -/
namespace ProctorScannerMeter
open ProctorDataParser

abbrev Meter := Option (List Nat) × Nat

def bump (m : Meter) : Meter := (m.1,m.2+1)

def scanMeter : List Nat → Nat → Nat → List Nat → Meter
  | [], _, digits, acc => (if digits=0 then some acc.reverse else none,1)
  | b::bs, v, digits, acc =>
    if b=10 then
      if digits=0 then (none,1) else bump (scanMeter bs 0 0 (v::acc))
    else if 48≤b ∧ b≤57 then
      if digits≥digitLimit ∨ (digits>0 ∧ v=0) then (none,1)
      else bump (scanMeter bs (10*v+(b-48)) (digits+1) acc)
    else (none,1)

theorem scan_value (bytes : List Nat) (v digits : Nat) (acc : List Nat) :
    (scanMeter bytes v digits acc).1=scan bytes v digits acc := by
  induction bytes generalizing v digits acc with
  | nil => rfl
  | cons b bs ih =>
    by_cases e : b=10
    · by_cases z : digits=0
      · simp only [scanMeter,scan,if_pos e,if_pos z]
      · simp only [scanMeter,scan,if_pos e,if_neg z,bump]
        exact ih 0 0 (v::acc)
    · by_cases d : 48≤b ∧ b≤57
      · by_cases bad : digits≥digitLimit ∨ (digits>0 ∧ v=0)
        · simp only [scanMeter,scan,if_neg e,if_pos d,if_pos bad]
        · simp only [scanMeter,scan,if_neg e,if_pos d,if_neg bad,bump]
          exact ih (10*v+(b-48)) (digits+1) acc
      · simp only [scanMeter,scan,if_neg e,if_neg d]

theorem scan_bound (bytes : List Nat) (v digits : Nat) (acc : List Nat) :
    (scanMeter bytes v digits acc).2≤bytes.length+1 := by
  induction bytes generalizing v digits acc with
  | nil => exact Nat.le_refl 1
  | cons b bs ih =>
    by_cases e : b=10
    · by_cases z : digits=0
      · simp only [scanMeter,if_pos e,if_pos z]
        exact Nat.succ_le_succ (Nat.zero_le _)
      · simp only [scanMeter,if_pos e,if_neg z,bump]
        exact Nat.succ_le_succ (ih 0 0 (v::acc))
    · by_cases d : 48≤b ∧ b≤57
      · by_cases bad : digits≥digitLimit ∨ (digits>0 ∧ v=0)
        · simp only [scanMeter,if_neg e,if_pos d,if_pos bad]
          exact Nat.succ_le_succ (Nat.zero_le _)
        · simp only [scanMeter,if_neg e,if_pos d,if_neg bad,bump]
          exact Nat.succ_le_succ (ih (10*v+(b-48)) (digits+1) acc)
      · simp only [scanMeter,if_neg e,if_neg d]
        exact Nat.succ_le_succ (Nat.zero_le _)

theorem scan_success_count (bytes : List Nat) (v digits : Nat)
    (acc out : List Nat) (h : scan bytes v digits acc=some out) :
    (scanMeter bytes v digits acc).2=bytes.length+1 := by
  induction bytes generalizing v digits acc with
  | nil => rfl
  | cons b bs ih =>
    by_cases e : b=10
    · by_cases z : digits=0
      · simp only [scan,if_pos e,if_pos z] at h
        cases h
      · simp only [scan,if_pos e,if_neg z] at h
        simp only [scanMeter,if_pos e,if_neg z,bump]
        exact congrArg Nat.succ (ih 0 0 (v::acc) h)
    · by_cases d : 48≤b ∧ b≤57
      · by_cases bad : digits≥digitLimit ∨ (digits>0 ∧ v=0)
        · simp only [scan,if_neg e,if_pos d,if_pos bad] at h
          cases h
        · simp only [scan,if_neg e,if_pos d,if_neg bad] at h
          simp only [scanMeter,if_neg e,if_pos d,if_neg bad,bump]
          exact congrArg Nat.succ (ih (10*v+(b-48)) (digits+1) acc h)
      · simp only [scan,if_neg e,if_neg d] at h
        cases h

def reverseCharge : Option (List Nat) → Nat
  | none => 0
  | some ts => ts.length

theorem reverse_bound (bytes : List Nat) :
    reverseCharge (tokenize bytes)≤bytes.length := by
  cases e : tokenize bytes with
  | none => exact Nat.zero_le _
  | some ts =>
    exact ProctorParserConsumption.wire_length bytes ts
      (ProctorEnvelopeRoundtrip.tokenize_converse bytes ts e).right

def tokenizeMeter (bytes : List Nat) : Meter :=
  if bytes.length≤byteLimit then
    let r := scanMeter bytes 0 0 []
    (r.1,(bytes.length+1)+r.2+reverseCharge r.1)
  else (none,bytes.length+1)

theorem tokenize_value (bytes : List Nat) :
    (tokenizeMeter bytes).1=tokenize bytes := by
  unfold tokenizeMeter tokenize
  by_cases h : bytes.length≤byteLimit
  · rw [if_pos h,if_pos h]
    exact scan_value bytes 0 0 []
  · rw [if_neg h,if_neg h]

def tokenBudget (bytes : List Nat) : Nat :=
  (bytes.length+1)+(bytes.length+1)+bytes.length

theorem tokenize_bound (bytes : List Nat) :
    (tokenizeMeter bytes).2≤tokenBudget bytes := by
  unfold tokenizeMeter tokenBudget
  by_cases h : bytes.length≤byteLimit
  · rw [if_pos h]
    change (bytes.length+1)+(scanMeter bytes 0 0 []).2+
      reverseCharge (scanMeter bytes 0 0 []).1≤
      (bytes.length+1)+(bytes.length+1)+bytes.length
    rw [scan_value]
    have ht : tokenize bytes=scan bytes 0 0 [] := by
      unfold tokenize
      rw [if_pos h]
    exact Nat.add_le_add
      (Nat.add_le_add (Nat.le_refl _) (scan_bound bytes 0 0 []))
      (by
        rw [← ht]
        exact reverse_bound bytes)
  · rw [if_neg h]
    exact Nat.le_trans (Nat.le_add_right _ _) (Nat.le_add_right _ _)

theorem tokenize_success_count (bytes ts : List Nat)
    (h : tokenize bytes=some ts) :
    (tokenizeMeter bytes).2=(bytes.length+1)+(bytes.length+1)+ts.length := by
  unfold tokenize at h
  unfold tokenizeMeter
  by_cases le : bytes.length≤byteLimit
  · rw [if_pos le] at h
    rw [if_pos le]
    change (bytes.length+1)+(scanMeter bytes 0 0 []).2+
      reverseCharge (scanMeter bytes 0 0 []).1=_
    rw [scan_value,h,scan_success_count bytes 0 0 [] ts h] <;> rfl
  · rw [if_neg le] at h
    cases h

end ProctorScannerMeter

#print axioms ProctorScannerMeter.scan_value
#print axioms ProctorScannerMeter.scan_bound
#print axioms ProctorScannerMeter.scan_success_count
#print axioms ProctorScannerMeter.reverse_bound
#print axioms ProctorScannerMeter.tokenize_value
#print axioms ProctorScannerMeter.tokenize_bound
#print axioms ProctorScannerMeter.tokenize_success_count
