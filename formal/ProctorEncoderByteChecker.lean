/-! F034 candidate: checked binary tokenizer, encoder-aware token
grammar and original typed checker selected resource composition.
Four scanner coordinates per input, and a grammar/checker selected
charge coordinate. No total machine cost assertion. -/
namespace ProctorEncoderByteChecker
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope boundCheck)
open ProctorParserMeterCompose (ParserMeter)
open ProctorEncoderGrammar (expectedMeter envelopeMeter expected_refines envelope_refines)
open ProctorEncoderIntegration (tokenizeEncode resource_bounds)
open ProctorBytePrepass (tokenize_refines)
open ProctorParserConsumption (wire_length byteCap byte_budget)
open ProctorEnvelopeRoundtrip (tokenize_converse)
open ProctorEncodedSize (globalUnit)
open ProctorTerminalPolynomial (mul_mono)

def finish {α : Type} : Option (α × List Nat) → Option α
  | none => none
  | some (a,[]) => some a
  | some (_, _::_) => none

-- Tokenizer result from the checked binary scanner. Grammar plus
-- final-consumption charge only; scanner coordinates remain separate.
private theorem scanner_projection (bytes : List Nat) :
    (tokenizeEncode bytes).1=ProctorDataParser.tokenize bytes :=
  (ProctorEncoderIntegration.tokenize_projection bytes).trans (tokenize_refines bytes)

def decodeMeter {α : Type} (p : ParserMeter α) (bytes : List Nat) :
    Option α × Nat :=
  match (tokenizeEncode bytes).1 with
  | none => (none,0)
  | some ts => let q := p ts; (finish q.1,q.2+1)

theorem decode_projection {α : Type} (p : ParserMeter α)
    (plain : ProctorDataParser.Parser α)
    (hp : ∀ ts, (p ts).1=plain ts) (bytes : List Nat) :
    (decodeMeter p bytes).1=ProctorDataParser.decode plain bytes := by
  change (match (tokenizeEncode bytes).1 with
    | none => (none,0)
    | some ts => (finish (p ts).1,(p ts).2+1)).1=_
  unfold ProctorDataParser.decode
  rw [scanner_projection]
  cases e : ProctorDataParser.tokenize bytes with
  | none => rfl
  | some ts =>
    change finish (p ts).1=(do
      let (a,rest) ← plain ts
      match rest with
      | [] => some a
      | _::_ => none)
    rw [hp ts]
    cases ep : plain ts with
    | none => rfl
    | some pair =>
      cases pair with
      | mk a rest => cases rest <;> rfl

def decodeBudget (bytes : List Nat) : Nat := 512*bytes.length+4

theorem decode_bound {α : Type} (p : ParserMeter α)
    (hp : ∀ ts, (p ts).2≤512*ts.length+3) (bytes : List Nat) :
    (decodeMeter p bytes).2≤decodeBudget bytes := by
  change (match (tokenizeEncode bytes).1 with
    | none => (none,0)
    | some ts => (finish (p ts).1,(p ts).2+1)).2≤_
  rw [scanner_projection]
  cases e : ProctorDataParser.tokenize bytes with
  | none => exact Nat.zero_le _
  | some ts =>
    have hl := wire_length bytes ts (tokenize_converse bytes ts e).right
    have hm : 512*ts.length≤512*bytes.length := mul_mono (Nat.le_refl 512) hl
    exact Nat.succ_le_succ (Nat.le_trans (hp ts)
      (Nat.add_le_add hm (Nat.le_refl 3)))

def expectedBytes := decodeMeter expectedMeter
def envelopeBytes := decodeMeter envelopeMeter

theorem expected_projection (bytes : List Nat) :
    (expectedBytes bytes).1=ProctorDataParser.decodeExpected bytes :=
  decode_projection _ _ expected_refines bytes

theorem envelope_projection (bytes : List Nat) :
    (envelopeBytes bytes).1=ProctorDataParser.decodeEnvelope bytes :=
  decode_projection _ _ envelope_refines bytes

theorem expected_bound (bytes : List Nat) :
    (expectedBytes bytes).2≤decodeBudget bytes :=
  decode_bound _ ProctorEncoderGrammar.expected_bound bytes

theorem envelope_bound (bytes : List Nat) :
    (envelopeBytes bytes).2≤decodeBudget bytes :=
  decode_bound _ ProctorEncoderGrammar.envelope_bound bytes

def checkMeter (a b : List Nat) : Bool × Nat :=
  let x := expectedBytes a
  let y := envelopeBytes b
  match x.1,y.1 with
  | some (n,f),some e =>
    let z := ProctorUnifiedMeter.boundMeter n f e
    (z.1,(x.2+y.2)+z.2)
  | _,_ => (false,x.2+y.2)

theorem check_projection (a b : List Nat) :
    (checkMeter a b).1=ProctorDataParser.checkBytes a b := by
  change (match (expectedBytes a).1,(envelopeBytes b).1 with
    | some (n,f),some e => ((ProctorUnifiedMeter.boundMeter n f e).1,
        ((expectedBytes a).2+(envelopeBytes b).2)+(ProctorUnifiedMeter.boundMeter n f e).2)
    | _,_ => (false,(expectedBytes a).2+(envelopeBytes b).2)).1=_
  unfold ProctorDataParser.checkBytes
  rw [expected_projection,envelope_projection]
  cases ea : ProctorDataParser.decodeExpected a with
  | none => rfl
  | some nf =>
    cases nf with
    | mk n f =>
      cases eb : ProctorDataParser.decodeEnvelope b with
      | none => rfl
      | some e => exact ProctorUnifiedMeter.bound_value n f e

def checkBudget (a b : List Nat) : Nat :=
  (decodeBudget a+decodeBudget b)+globalUnit (byteCap a b)

theorem check_bound (a b : List Nat) :
    (checkMeter a b).2≤checkBudget a b := by
  have hd := Nat.add_le_add (expected_bound a) (envelope_bound b)
  change (match (expectedBytes a).1,(envelopeBytes b).1 with
    | some (n,f),some e => ((ProctorUnifiedMeter.boundMeter n f e).1,
        ((expectedBytes a).2+(envelopeBytes b).2)+(ProctorUnifiedMeter.boundMeter n f e).2)
    | _,_ => (false,(expectedBytes a).2+(envelopeBytes b).2)).2≤_
  rw [expected_projection,envelope_projection]
  cases ea : ProctorDataParser.decodeExpected a with
  | none => exact Nat.le_trans hd (Nat.le_add_right _ _)
  | some nf =>
    cases nf with
    | mk n f =>
      cases eb : ProctorDataParser.decodeEnvelope b with
      | none => exact Nat.le_trans hd (Nat.le_add_right _ _)
      | some e => exact Nat.add_le_add hd (byte_budget a b n f e ea eb)

theorem check_sound (a b : List Nat) (h : (checkMeter a b).1=true) :
    ∃ n f, ProctorDataParser.decodeExpected a=some (n,f) ∧
      ¬ ∃ x : Assignment, FormulaSat f x := by
  rw [check_projection] at h
  exact ProctorDataParser.accepted_unsat a b h

theorem check_fuel_free_agrees (a b : List Nat) :
    (checkMeter a b).1=ProctorFuelFreeDecoder.checkBytes a b :=
  (check_projection a b).trans (ProctorFuelFreeDecoder.check_refines a b).symm

-- Four scanner coordinates on each input and one selected
-- grammar/checker coordinate for the pair. No common machine unit.
def scannerResources (bytes : List Nat) := ProctorEncoderIntegration.resources bytes

def resources (a b : List Nat) :=
  (scannerResources a,scannerResources b,(checkMeter a b).2)

def ScannerWithin (bytes : List Nat) (r : Nat × Nat × Nat × Nat) : Prop :=
  r.1≤5235*bytes.length ∧
  r.2.1≤1046*bytes.length+8 ∧
  r.2.2.1≤20*bytes.length ∧
  r.2.2.2≤21*bytes.length

theorem combined_bounds (a b : List Nat) :
    ScannerWithin a (resources a b).1 ∧
    ScannerWithin b (resources a b).2.1 ∧
    (resources a b).2.2≤checkBudget a b :=
  ⟨resource_bounds a,resource_bounds b,check_bound a b⟩

end ProctorEncoderByteChecker

#print axioms ProctorEncoderByteChecker.decode_projection
#print axioms ProctorEncoderByteChecker.decode_bound
#print axioms ProctorEncoderByteChecker.expected_projection
#print axioms ProctorEncoderByteChecker.envelope_projection
#print axioms ProctorEncoderByteChecker.expected_bound
#print axioms ProctorEncoderByteChecker.envelope_bound
#print axioms ProctorEncoderByteChecker.check_projection
#print axioms ProctorEncoderByteChecker.check_bound
#print axioms ProctorEncoderByteChecker.check_sound
#print axioms ProctorEncoderByteChecker.check_fuel_free_agrees
#print axioms ProctorEncoderByteChecker.combined_bounds
