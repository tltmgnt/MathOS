/-! F034 candidate: compose the existing selected decimal scanner,
amortized token grammar, and typed checker meters. This uses the
original Nat scanner's verified abstract charges, NOT the binary
scanner's gate/visit costs. Both decoders are evaluated; the checker
is charged only when both decode successfully. -/
namespace ProctorByteCheckerLedger
open ProctorHallDeficiency
open ProctorUnifiedReplay (Envelope boundCheck)
open ProctorParserMeterCompose (ParserMeter)
open ProctorGrammarMeter (expectedMeter envelopeMeter expected_refines envelope_refines)
open ProctorScannerMeter (tokenizeMeter tokenize_value tokenize_bound tokenBudget)
open ProctorParserConsumption (wire_length byteCap byte_budget)
open ProctorEnvelopeRoundtrip (tokenize_converse)
open ProctorEncodedSize (globalUnit)
open ProctorTerminalPolynomial (mul_mono)

def finish {α : Type} : Option (α × List Nat) → Option α
  | none => none
  | some (a,[]) => some a
  | some (_, _::_) => none

def decodeMeter {α : Type} (p : ParserMeter α) (bytes : List Nat) :
    Option α × Nat :=
  let r := tokenizeMeter bytes
  match r.1 with
  | none => (none,r.2)
  | some ts =>
    let q := p ts
    (finish q.1,r.2+(q.2+1))

theorem decode_projection {α : Type} (p : ParserMeter α)
    (plain : ProctorDataParser.Parser α)
    (hp : ∀ ts, (p ts).1=plain ts) (bytes : List Nat) :
    (decodeMeter p bytes).1=ProctorDataParser.decode plain bytes := by
  change (match (tokenizeMeter bytes).1 with
    | none => (none,(tokenizeMeter bytes).2)
    | some ts => (finish (p ts).1,(tokenizeMeter bytes).2+((p ts).2+1))).1=_
  unfold ProctorDataParser.decode
  rw [tokenize_value]
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

def decodeBudget (bytes : List Nat) : Nat :=
  tokenBudget bytes+(64*bytes.length+4)

theorem decode_bound {α : Type} (p : ParserMeter α)
    (hp : ∀ ts, (p ts).2≤64*ts.length+3) (bytes : List Nat) :
    (decodeMeter p bytes).2≤decodeBudget bytes := by
  change (match (tokenizeMeter bytes).1 with
    | none => (none,(tokenizeMeter bytes).2)
    | some ts => (finish (p ts).1,(tokenizeMeter bytes).2+((p ts).2+1))).2≤_
  rw [tokenize_value]
  cases e : ProctorDataParser.tokenize bytes with
  | none =>
    exact Nat.le_trans (tokenize_bound bytes) (Nat.le_add_right _ _)
  | some ts =>
    have hl := wire_length bytes ts (tokenize_converse bytes ts e).right
    have hm : 64*ts.length≤64*bytes.length := mul_mono (Nat.le_refl 64) hl
    have hq : (p ts).2+1≤64*bytes.length+4 :=
      Nat.succ_le_succ (Nat.le_trans (hp ts)
        (Nat.add_le_add hm (Nat.le_refl 3)))
    exact Nat.add_le_add (tokenize_bound bytes) hq

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
  decode_bound _ ProctorAmortizedGrammar.expected_bound bytes

theorem envelope_bound (bytes : List Nat) :
    (envelopeBytes bytes).2≤decodeBudget bytes :=
  decode_bound _ ProctorAmortizedGrammar.envelope_bound bytes

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

end ProctorByteCheckerLedger

#print axioms ProctorByteCheckerLedger.decode_projection
#print axioms ProctorByteCheckerLedger.decode_bound
#print axioms ProctorByteCheckerLedger.expected_projection
#print axioms ProctorByteCheckerLedger.envelope_projection
#print axioms ProctorByteCheckerLedger.expected_bound
#print axioms ProctorByteCheckerLedger.envelope_bound
#print axioms ProctorByteCheckerLedger.check_projection
#print axioms ProctorByteCheckerLedger.check_bound
#print axioms ProctorByteCheckerLedger.check_sound
#print axioms ProctorByteCheckerLedger.check_fuel_free_agrees
