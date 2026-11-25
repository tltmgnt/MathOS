/-! F034 candidate: integrate the checked boundary encoder's selected
event ledger at scanner digit attempts and a metered list header.
Nested parser encoder costs are not yet composed. Separate coordinates
remain abstract selected events, not machine instructions. -/
namespace ProctorEncoderIntegration
open ProctorBinaryScannerGates (meterCore core_projection)
open ProctorCheckedBinaryScanner (zeroWord checkedDigit zeroBits encode)
open ProctorScannerCounters (countZero nextCount scanCounted)
open ProctorDecimalBitWidth (bitsValue)
open ProctorBytePrepass (byteOK tokenizeBounded)
open ProctorEncodeVisits (encodeMeter encode_projection four_bound seventeen_bound)
open ProctorParserMeterCompose (ParserMeter listMeter wordRun)
open ProctorDataParser (listLimit)
open ProctorAmortizedParser (Amortized list_amortized all_bound)

def digitEvents (_v : List Bool) (b : Nat) : Nat := (encodeMeter 4 (b-48)).2
def noEvents (_c : List Bool) : Nat := 0

-- Reserve the encoder at every visited digit-classified byte,
-- even if a preceding scanner guard rejects.
theorem core_bound (reset cz : List Bool)
    (step : List Bool → Nat → Option (List Bool))
    (next : List Bool → Option (List Bool))
    (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (meterCore reset cz step next digitEvents noEvents bytes v c acc).2≤21*bytes.length := by
  induction bytes generalizing v c acc with
  | nil => exact Nat.le_refl 0
  | cons b bs ih =>
    rw [meterCore]
    by_cases lf : b=10
    · rw [if_pos lf]
      by_cases z : zeroBits c=true
      · rw [if_pos z]
        exact Nat.zero_le _
      · rw [if_neg z]
        exact Nat.le_trans (ih reset cz (bitsValue v::acc)) (Nat.le_add_right _ _)
    · rw [if_neg lf]
      by_cases digit : 48≤b ∧ b≤57
      · rw [if_pos digit]
        change (if zeroBits c≠true ∧ zeroBits v=true then (none,0)
          else match next c with
            | none => (none,0)
            | some d => match step v b with
              | none => (none,0)
              | some out => meterCore reset cz step next digitEvents noEvents bs out d acc).2+
          (encodeMeter 4 (b-48)).2≤21*bs.length+21
        apply Nat.add_le_add _ (four_bound (b-48))
        by_cases lead : zeroBits c≠true ∧ zeroBits v=true
        · rw [if_pos lead]
          exact Nat.zero_le _
        · rw [if_neg lead]
          cases en : next c with
          | none => exact Nat.zero_le _
          | some d =>
            change (match step v b with
              | none => (none,0)
              | some out => meterCore reset cz step next digitEvents noEvents bs out d acc).2≤_
            cases es : step v b with
            | none => exact Nat.zero_le _
            | some out => exact ih out d acc
      · rw [if_neg digit]
        exact Nat.zero_le _

def scanEncode := meterCore zeroWord countZero checkedDigit nextCount digitEvents noEvents

theorem scan_projection (bytes : List Nat) (v c : List Bool) (acc : List Nat) :
    (scanEncode bytes v c acc).1=scanCounted bytes v c acc :=
  core_projection zeroWord countZero checkedDigit nextCount digitEvents noEvents bytes v c acc

def tokenizeEncode (bytes : List Nat) : Option (List Nat) × Nat :=
  if byteOK bytes then scanEncode bytes zeroWord countZero [] else (none,0)

theorem tokenize_projection (bytes : List Nat) :
    (tokenizeEncode bytes).1=tokenizeBounded bytes := by
  unfold tokenizeEncode tokenizeBounded
  by_cases h : byteOK bytes=true
  · rw [if_pos h,if_pos h]
    exact scan_projection bytes zeroWord countZero []
  · rw [if_neg h,if_neg h]

theorem tokenize_bound (bytes : List Nat) :
    (tokenizeEncode bytes).2≤21*bytes.length := by
  unfold tokenizeEncode
  by_cases h : byteOK bytes=true
  · rw [if_pos h]
    exact core_bound zeroWord countZero checkedDigit nextCount bytes zeroWord countZero []
  · rw [if_neg h]
    exact Nat.zero_le _

def resources (bytes : List Nat) : Nat × Nat × Nat × Nat :=
  let r := ProctorScannerResourceCompose.resources bytes
  (r.1,r.2.1,r.2.2,(tokenizeEncode bytes).2)

theorem resource_bounds (bytes : List Nat) :
    (resources bytes).1≤5235*bytes.length ∧
    (resources bytes).2.1≤1046*bytes.length+8 ∧
    (resources bytes).2.2.1≤20*bytes.length ∧
    (resources bytes).2.2.2≤21*bytes.length := by
  have h := ProctorScannerResourceCompose.resource_bounds bytes
  exact ⟨h.1,h.2.1,h.2.2,tokenize_bound bytes⟩

-- Header encoder is entered only after the original list-limit guard.
def headerEvents : List Nat → Nat
  | [] => 0
  | k::_ => if k≤listLimit then (encodeMeter 17 k).2 else 0

theorem header_bound (ts : List Nat) : headerEvents ts≤307 := by
  cases ts with
  | nil => exact Nat.zero_le _
  | cons k rest =>
    change (if k≤listLimit then (encodeMeter 17 k).2 else 0)≤307
    by_cases h : k≤listLimit
    · rw [if_pos h]
      exact seventeen_bound k
    · rw [if_neg h]
      exact Nat.zero_le _

-- Actual header-meter substitution. The child parser is unchanged.
def listEncodeMeter {α : Type} (p : ParserMeter α) : ParserMeter (List α)
  | [] => (none,1)
  | k::ts =>
    if k≤listLimit then
      let e := encodeMeter 17 k
      match e.1 with
      | none => (none,1+e.2)
      | some c =>
        let r := wordRun p c ts
        (r.1,(r.2+1)+e.2)
    else (none,1)

theorem list_account {α : Type} (p : ParserMeter α) (ts : List Nat) :
    listEncodeMeter p ts=((listMeter p ts).1,(listMeter p ts).2+headerEvents ts) := by
  cases ts with
  | nil => rfl
  | cons k rest =>
    change (if k≤listLimit then
      match (encodeMeter 17 k).1 with
      | none => (none,1+(encodeMeter 17 k).2)
      | some c => ((wordRun p c rest).1,((wordRun p c rest).2+1)+(encodeMeter 17 k).2)
      else (none,1))=
      ((if k≤listLimit then
        match encode 17 k with
        | none => (none,1)
        | some c => ((wordRun p c rest).1,(wordRun p c rest).2+1)
        else (none,1)).1,
       (if k≤listLimit then
        match encode 17 k with
        | none => (none,1)
        | some c => ((wordRun p c rest).1,(wordRun p c rest).2+1)
        else (none,1)).2+
        (if k≤listLimit then (encodeMeter 17 k).2 else 0))
    by_cases h : k≤listLimit
    · simp only [if_pos h,encode_projection]
      cases e : encode 17 k <;> rfl
    · simp only [if_neg h]

theorem list_projection {α : Type} (p : ParserMeter α) (ts : List Nat) :
    (listEncodeMeter p ts).1=(listMeter p ts).1 := by
  rw [list_account]

theorem list_bound {α : Type} (p : ParserMeter α) (hp : Amortized p)
    (ts : List Nat) :
    (listEncodeMeter p ts).2≤(64*ts.length+3)+307 := by
  rw [list_account]
  exact Nat.add_le_add (all_bound _ (list_amortized p hp) ts) (header_bound ts)

end ProctorEncoderIntegration

#print axioms ProctorEncoderIntegration.core_bound
#print axioms ProctorEncoderIntegration.scan_projection
#print axioms ProctorEncoderIntegration.tokenize_projection
#print axioms ProctorEncoderIntegration.tokenize_bound
#print axioms ProctorEncoderIntegration.resource_bounds
#print axioms ProctorEncoderIntegration.header_bound
#print axioms ProctorEncoderIntegration.list_account
#print axioms ProctorEncoderIntegration.list_projection
#print axioms ProctorEncoderIntegration.list_bound
