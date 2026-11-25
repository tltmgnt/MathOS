/-! F034: end-to-end selected resource composition for raw file pairs.
Both decoders are evaluated once; typed verification is entered only
when both decode successfully. No claim of complete runtime. -/
namespace ProctorEndToEndMeter
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope boundCheck)
open ProctorDataParser (decodeExpected decodeEnvelope checkBytes expectedToken envelopeToken)
open ProctorDimacsInput (decodeDimacs checkDimacs)
open ProctorTypedParserMeter (expectedMeter envelopeMeter decodeBudget)
open ProctorEncodedSize (globalUnit)
open ProctorUnifiedMeter (boundMeter bound_value)

abbrev InputResult := Option (Nat × Formula) × Nat
abbrev ProofResult := Option Envelope × Nat

-- Eagerly charge both decoders, even when one fails.
def pairMeter (x : InputResult) (y : ProofResult) : Bool × Nat :=
  let base := x.2+y.2
  match x.1,y.1 with
  | some (n,f),some e =>
    let r := boundMeter n f e
    (r.1,base+r.2)
  | _,_ => (false,base)

theorem pair_value (x : InputResult) (y : ProofResult) :
    (pairMeter x y).1=(match x.1,y.1 with
      | some (n,f),some e => boundCheck n f e
      | _,_ => false) := by
  unfold pairMeter
  cases x.1 with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases y.1 with
      | none => rfl
      | some e => exact bound_value n f e

theorem pair_bound (x : InputResult) (y : ProofResult) (X Y V : Nat)
    (hx : x.2≤X) (hy : y.2≤Y)
    (hv : ∀ n f e, x.1=some (n,f) → y.1=some e →
      (boundMeter n f e).2≤V) :
    (pairMeter x y).2≤(X+Y)+V := by
  unfold pairMeter
  cases ex : x.1 with
  | none => exact Nat.le_trans (Nat.add_le_add hx hy) (Nat.le_add_right _ _)
  | some nf =>
    cases nf with
    | mk n f =>
      cases ey : y.1 with
      | none => exact Nat.le_trans (Nat.add_le_add hx hy) (Nat.le_add_right _ _)
      | some e => exact Nat.add_le_add (Nat.add_le_add hx hy) (hv n f e ex ey)

def expectedDecode (a : List Nat) : InputResult :=
  ProctorTypedParserMeter.decodeMeter expectedMeter a

def proofDecode (b : List Nat) : ProofResult :=
  ProctorTypedParserMeter.decodeMeter envelopeMeter b

theorem expected_value (a : List Nat) : (expectedDecode a).1=decodeExpected a :=
  ProctorTypedParserMeter.decode_value expectedMeter expectedToken
    ProctorTypedParserMeter.expected_value a

theorem envelope_value (b : List Nat) : (proofDecode b).1=decodeEnvelope b :=
  ProctorTypedParserMeter.decode_value envelopeMeter envelopeToken
    ProctorTypedParserMeter.envelope_value b

theorem expected_bound (a : List Nat) : (expectedDecode a).2≤decodeBudget a :=
  ProctorTypedParserMeter.decode_bound expectedMeter ProctorTypedParserMeter.expected_good a

theorem envelope_bound (b : List Nat) : (proofDecode b).2≤decodeBudget b :=
  ProctorTypedParserMeter.decode_bound envelopeMeter ProctorTypedParserMeter.envelope_good b

def customMeter (a b : List Nat) : Bool × Nat :=
  pairMeter (expectedDecode a) (proofDecode b)

def dimacsMeter (a b : List Nat) : Bool × Nat :=
  pairMeter (ProctorDimacsDecoderMeter.decodeMeter a) (proofDecode b)

def customBudget (a b : List Nat) : Nat :=
  (decodeBudget a+decodeBudget b)+globalUnit (ProctorParserConsumption.byteCap a b)

def dimacsBudget (a b : List Nat) : Nat :=
  (a.length*34+29+decodeBudget b)+globalUnit (ProctorDimacsSize.byteCap a b)

theorem custom_value (a b : List Nat) :
    (customMeter a b).1=checkBytes a b := by
  unfold customMeter checkBytes
  rw [pair_value,expected_value,envelope_value]

theorem dimacs_value (a b : List Nat) :
    (dimacsMeter a b).1=checkDimacs a b := by
  unfold dimacsMeter checkDimacs
  rw [pair_value,ProctorDimacsDecoderMeter.decode_value,envelope_value]

theorem custom_bound (a b : List Nat) :
    (customMeter a b).2≤customBudget a b := by
  unfold customMeter customBudget
  apply pair_bound _ _ _ _ _ (expected_bound a) (envelope_bound b)
  intro n f e ha hb
  rw [expected_value] at ha
  rw [envelope_value] at hb
  exact ProctorParserConsumption.byte_budget a b n f e ha hb

theorem dimacs_bound (a b : List Nat) :
    (dimacsMeter a b).2≤dimacsBudget a b := by
  unfold dimacsMeter dimacsBudget
  apply pair_bound _ _ _ _ _ (ProctorDimacsDecoderMeter.decode_linear a) (envelope_bound b)
  intro n f e ha hb
  rw [ProctorDimacsDecoderMeter.decode_value] at ha
  rw [envelope_value] at hb
  exact ProctorDimacsSize.byte_budget a b n f e ha hb

theorem custom_sound (a b : List Nat) (h : (customMeter a b).1=true) :
    (∃ n f, decodeExpected a=some (n,f) ∧ ¬ ∃ x : Assignment, FormulaSat f x) ∧
      (customMeter a b).2≤customBudget a b := by
  rw [custom_value] at h
  exact ⟨ProctorDataParser.accepted_unsat a b h,custom_bound a b⟩

theorem dimacs_sound (a b : List Nat) (h : (dimacsMeter a b).1=true) :
    (∃ n f, ProctorDimacsLexical.RawMeaning a n f ∧ ¬ ∃ x : Assignment, FormulaSat f x) ∧
      (dimacsMeter a b).2≤dimacsBudget a b := by
  rw [dimacs_value] at h
  exact ⟨ProctorDimacsLexical.raw_accepted_unsat a b h,dimacs_bound a b⟩

end ProctorEndToEndMeter

#print axioms ProctorEndToEndMeter.pair_value
#print axioms ProctorEndToEndMeter.pair_bound
#print axioms ProctorEndToEndMeter.expected_value
#print axioms ProctorEndToEndMeter.envelope_value
#print axioms ProctorEndToEndMeter.expected_bound
#print axioms ProctorEndToEndMeter.envelope_bound
#print axioms ProctorEndToEndMeter.custom_value
#print axioms ProctorEndToEndMeter.dimacs_value
#print axioms ProctorEndToEndMeter.custom_bound
#print axioms ProctorEndToEndMeter.dimacs_bound
#print axioms ProctorEndToEndMeter.custom_sound
#print axioms ProctorEndToEndMeter.dimacs_sound
